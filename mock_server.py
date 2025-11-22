
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

# --- 1. Pydantic Model (Schema: Project) ---
class Project(BaseModel):
    id: int | None = None # ID ist optional beim Erstellen
    key: str
    name: str

# --- 2. In-Memory Datenbank (Mit generierten Testdaten) ---
IN_MEMORY_DB: Dict[int, Project] = {}
NEXT_ID = 5

# Daten aus Testdaten laden und validieren (mit Pydantic)
INITIAL_DATA = {1: {'id': 1, 'key': 'PRO-1', 'name': 'Project 1', 'fields': {'summary': 'Summary of issue 1', 'description': 'Description of issue 1', 'status': 'Open', 'assignee': 'John Doe', 'issuetype': 'Bug', 'project': 'PRO-1'}}, 2: {'id': 2, 'key': 'PRO-2', 'name': 'Project 2', 'fields': {'summary': 'Summary of issue 2', 'description': 'Description of issue 2', 'status': 'Open', 'assignee': 'Jane Doe', 'issuetype': 'Feature', 'project': 'PRO-2'}}, 4: {'id': 4, 'key': 'PRO-4', 'name': 'Project 4', 'fields': {'summary': 'Summary of issue 4', 'description': 'Description of issue 4', 'status': 'Open', 'assignee': 'Jane Doe', 'issuetype': 'Feature', 'project': 'PRO-4'}}}

for id_key, item_data in INITIAL_DATA.items():
    try:
        IN_MEMORY_DB[id_key] = Project(**item_data)
    except Exception as e:
        print(f"WARNUNG: Testdaten ID {id_key} konnte nicht geladen werden ({e})")


# --- 3. Security Dependency (Adressiert die GAP-Analyse) ---
# NOTE: Nur für POST, PUT, DELETE benötigt. GET ist öffentlich.
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != "MOCK_TOKEN_123":
        # Demonstriert die von der KI erkannte GAP 'Authentifizierung'
        raise HTTPException(status_code=401, detail="Invalid API Key. Authorization required.")
    return True

# --- 4. FastAPI App ---
app = FastAPI(
    title="Issue Tracking API",
    description="Mock Server basierend auf generierter OpenAPI Spec (inkl. Security Mock).",
    version="1.0.0"
)

# --- 5. CRUD Endpunkte (/projects) ---

# POST / (CREATE) - Gesichert
@app.post("/projects", status_code=201, response_model=Project, dependencies=[Depends(verify_api_key)])
async def create_project(item: Project):
    global NEXT_ID
    
    if item.id is not None:
        raise HTTPException(status_code=400, detail="ID must not be provided on creation.")
        
    item.id = NEXT_ID
    NEXT_ID += 1
    
    IN_MEMORY_DB[item.id] = item
    return item

# GET / (READ ALL) - Öffentlich
@app.get("/projects", response_model=List[Project])
async def get_all_projects():
    return list(IN_MEMORY_DB.values())

# GET /<built-in function id> (READ ONE) - Öffentlich
@app.get("/projects/{id}", response_model=Project)
async def get_one_project(id: int):
    if id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    return IN_MEMORY_DB[id]

# PUT /<built-in function id> (UPDATE) - Gesichert
@app.put("/projects/{id}", response_model=Project, dependencies=[Depends(verify_api_key)])
async def update_project(id: int, item: Project):
    if id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if item.id is not None and item.id != id:
        raise HTTPException(status_code=400, detail="ID in body must match ID in path")
        
    item.id = id 
    IN_MEMORY_DB[id] = item
    return item

# DELETE /<built-in function id> (DELETE) - Gesichert
@app.delete("/projects/{id}", status_code=204, dependencies=[Depends(verify_api_key)])
async def delete_project(id: int):
    if id not in IN_MEMORY_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del IN_MEMORY_DB[id]
    return

# --- Server Start ---
if __name__ == "__main__":
    print(f"🚀 Mock Server gestartet auf http://127.0.0.1:8000")
    print(f"🔗 Dokumentation (Swagger UI) verfügbar unter http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
