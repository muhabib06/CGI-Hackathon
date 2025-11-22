# mock_server_builder.py

import json
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any, Optional
import sys
from termcolor import colored
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_mock_server(spec_filename: str = "openapi_definition.json", data_filename: str = "testdata.json"):
    """
    Liess die OpenAPI Spezifikation und die Testdaten ein, um ein
    lauffähiges FastAPI Mock-Server Skript zu generieren.
    """
    print("\n--- 4. MOCK SERVER BUILDER GESTARTET ---")
    
    try:
        # 1. Daten einlesen
        with open(spec_filename, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        with open(data_filename, 'r', encoding='utf-8') as f:
            test_data_raw = json.load(f)
            
    except FileNotFoundError as e:
        print(colored(f"❌ FEHLER: Datei nicht gefunden: {e}. Führen Sie zuerst main.py aus.", 'red'))
        sys.exit(1)
    except json.JSONDecodeError:
        print(colored(f"❌ FEHLER: Konnte JSON aus '{spec_filename}' oder '{data_filename}' nicht dekodieren.", 'red'))
        sys.exit(1)

    # 2. Ressourcenpfad und Schema-Name bestimmen
    try:
        resource_path_plural = next(iter(spec['paths'])).split('/{')[0] 
        resource_name_plural = resource_path_plural.split('/')[-1]
        
        if resource_name_plural.endswith('s'):
            resource_name_singular = resource_name_plural[:-1]
        else:
            resource_name_singular = resource_name_plural
            
        post_ref = spec['paths'][resource_path_plural]['post']['requestBody']['content']['application/json']['schema']['$ref']
        schema_name = post_ref.split('/')[-1] 
    except Exception as e:
        print(colored(f"❌ FEHLER beim Parsen der OpenAPI Spec: {e}", 'red'))
        sys.exit(1)

    # 3. Das Pydantic-Model bestimmen
    schema_definition = spec['components']['schemas'][schema_name]
    model_fields = []
    
    for prop_name, prop_def in schema_definition['properties'].items():
        py_type = 'str' 
        
        if prop_def['type'] == 'integer':
            py_type = 'int'
        elif prop_def['type'] == 'number':
            py_type = 'float'
        elif prop_def['type'] == 'boolean':
            py_type = 'bool'
            
        is_required = prop_name in schema_definition.get('required', [])
        
        # Erstelle die Pydantic-Felder
        if not is_required and prop_name != 'id':
             model_fields.append(f"    {prop_name}: {py_type} | None = None")
        elif prop_name == 'id':
             model_fields.append(f"    {prop_name}: int | None = None # ID ist optional beim Erstellen")
        else:
            model_fields.append(f"    {prop_name}: {py_type}")

    pydantic_model_code = "\n".join(model_fields)
    
    # 4. Mock-Datenbank vorbereiten
    mock_data = {}
    valid_test_items = [item for item in test_data_raw if isinstance(item, dict) and item.get('id') is not None and isinstance(item.get('id'), int)]
    
    next_id = 1
    if valid_test_items:
        next_id = max(item.get('id', 0) for item in valid_test_items) + 1
        mock_data = {item['id']: item for item in valid_test_items}
    
    
    # 5. FastAPI Mock Server Code generieren
    mock_server_code = f"""
# mock_server.py
#
# DIESER CODE WURDE AUTOMATISCH VON mock_server_builder.py GENERIERT
# BASIEREND AUF openapi_definition.json
#
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any, Optional
import sys
import os

# --- 1. Pydantic Model (Schema: {schema_name}) ---
class {schema_name}(BaseModel):
{pydantic_model_code}

# --- 2. In-Memory Datenbank (Mit generierten Testdaten) ---
IN_MEMORY_DB: Dict[int, {schema_name}] = {{}}
NEXT_ID = {next_id}

# Daten aus Testdaten laden und validieren (mit Pydantic)
INITIAL_DATA = {mock_data}

for id_key, item_data in INITIAL_DATA.items():
    try:
        IN_MEMORY_DB[id_key] = {schema_name}(**item_data)
    except Exception as e:
        print(f"WARNUNG: Testdaten ID {{id_key}} konnte nicht geladen werden ({{e}})")


# --- 3. Security Dependency (Adressiert die GAP-Analyse) ---
# NOTE: Nur für POST, PUT, DELETE benötigt. GET ist öffentlich.
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != "MOCK_TOKEN_123":
        # Demonstriert die von der KI erkannte GAP 'Authentifizierung'
        raise HTTPException(status_code=401, detail="Invalid API Key. Authorization required.")
    return True

# --- 4. FastAPI App ---
app = FastAPI(
    title="{spec['info']['title']}",
    description="Mock Server basierend auf generierter OpenAPI Spec (inkl. Security Mock).",
    version="{spec['info']['version']}"
)

# --- 5. CRUD Endpunkte ({resource_path_plural}) ---

# POST / (CREATE) - Gesichert
@app.post("{resource_path_plural}", status_code=201, response_model={schema_name}, dependencies=[Depends(verify_api_key)])
async def create_{resource_name_singular}(item: {schema_name}):
    global NEXT_ID
    
    if item.id is not None:
        raise HTTPException(status_code=400, detail="ID must not be provided on creation.")
        
    item.id = NEXT_ID
    NEXT_ID += 1
    
    IN_MEMORY_DB[item.id] = item
    return item

# GET / (READ ALL) - Öffentlich
@app.get("{resource_path_plural}", response_model=List[{schema_name}])
async def get_all_{resource_name_plural}():
    return list(IN_MEMORY_DB.values())

# GET /{id} (READ ONE) - Öffentlich
@app.get("{resource_path_plural}/{{id}}", response_model={schema_name})
async def get_one_{resource_name_singular}(id: int):
    if id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="{schema_name} not found")
    return IN_MEMORY_DB[id]

# PUT /{id} (UPDATE) - Gesichert
@app.put("{resource_path_plural}/{{id}}", response_model={schema_name}, dependencies=[Depends(verify_api_key)])
async def update_{resource_name_singular}(id: int, item: {schema_name}):
    if id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="{schema_name} not found")
        
    if item.id is not None and item.id != id:
        raise HTTPException(status_code=400, detail="ID in body must match ID in path")
        
    item.id = id 
    IN_MEMORY_DB[id] = item
    return item

# DELETE /{id} (DELETE) - Gesichert
@app.delete("{resource_path_plural}/{{id}}", status_code=204, dependencies=[Depends(verify_api_key)])
async def delete_{resource_name_singular}(id: int):
    if id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="{schema_name} not found")
    
    del IN_MEMORY_DB[id]
    return

# --- Server Start ---
if __name__ == "__main__":
    print(f"🚀 Mock Server gestartet auf http://127.0.0.1:8000")
    print(f"🔗 Dokumentation (Swagger UI) verfügbar unter http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

    # 6. Datei schreiben
    server_filename = "mock_server.py"
    with open(server_filename, 'w', encoding='utf-8') as f:
        f.write(mock_server_code)
        
    print(colored(f"✅ Mock Server erfolgreich in '{server_filename}' generiert.", 'green'))
    print(colored("\nNächster Schritt: Führen Sie 'python generate_tests.py' aus.", 'cyan'))


if __name__ == "__main__":
    create_mock_server()