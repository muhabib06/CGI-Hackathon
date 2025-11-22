# main.py

import os
import json
import requests
import sys
import prompts
import topic
import testdata_validator # <--- WICHTIG: Import des Validators
from termcolor import colored

# --- Konfiguration ---
IONOS_TOKEN = os.getenv("IONOS_API_TOKEN")

if not IONOS_TOKEN:
    print(colored("❌ FEHLER: IONOS_API_TOKEN fehlt! Bitte setzen Sie die Umgebungsvariable.", 'red'))
    sys.exit(1)

API_URL = "https://openai.inference.de-txl.ionos.com/v1/chat/completions"
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

def query_llm(system_prompt: str, user_prompt: str) -> str:
    """Hilfsfunktion: Sendet Anfragen an die KI."""
    print(f"--- Sende Anfrage an KI ({MODEL}) ---")
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {IONOS_TOKEN}"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 4096,
                "temperature": 0.0
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(colored(f"API Request Failed: {e}", 'red'))
        sys.exit(1)

def main():
    
    # =========================================================
    # SCHRITT 1: Das Interview (Interaktiver Teil)
    # =========================================================
    final_scope = topic.get_final_topic(query_llm)
    
    
    # =========================================================
    # SCHRITT 2: Die Generierung (Automatischer Teil)
    # =========================================================
    print("\n" + "="*50)
    print("🚀 STARTE AUTOMATISCHE GENERIERUNG...")
    print("="*50)

    # A) OpenAPI und GAP-Analyse erstellen
    print("\n1️⃣ Erstelle OpenAPI Definition & GAP-Analyse...")
    
    formatted_spec_prompt = prompts.SPEC_GENERATION["user"].format(topic=final_scope)
    
    raw_output = query_llm(
        prompts.SPEC_GENERATION["system"], 
        formatted_spec_prompt
    )

    spec_content = "" 

    try:
        # Parsen der Ausgabe (JSON und GAP-Analyse)
        parts = raw_output.split("<<<SPLIT_MARKER>>>")
        
        # JSON säubern und speichern
        spec_content_raw = parts[0].replace("<<<JSON_START>>>", "").replace("```json", "").replace("```", "").strip()
        gap_analysis = parts[1].strip()

        # Dateien speichern
        with open("openapi_definition.json", "w", encoding="utf-8") as f:
            json.dump(json.loads(spec_content_raw), f, indent=2) 
            
        with open("gap_analysis.txt", "w", encoding="utf-8") as f:
            f.write(gap_analysis)
        
        print(colored("    ✅ 'openapi_definition.json' gespeichert.", 'green'))
        print(colored("    ✅ 'gap_analysis.txt' gespeichert.", 'green'))
        
        spec_content = spec_content_raw 
        
    except (IndexError, json.JSONDecodeError):
        print(colored("❌ FEHLER: Die KI hat die Struktur nicht eingehalten oder JSON ist ungültig.", 'red'))
        sys.exit(1)

    # B) Testdaten erstellen
    print("\n2️⃣ Erstelle Testdaten basierend auf der API...")
    
    formatted_test_prompt = prompts.TEST_DATA_GENERATION["user"].format(spec_content=spec_content)
    
    json_output = query_llm(
        prompts.TEST_DATA_GENERATION["system"], 
        formatted_test_prompt
    )
    
    try:
        clean_json = json_output.replace("```json", "").replace("```", "").strip()
        test_data = json.loads(clean_json)
        
        with open("testdata.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=2)
            
        print(colored(f"    ✅ {len(test_data)} Testfälle in 'testdata.json' gespeichert.", 'green'))
        
    except json.JSONDecodeError:
        print(colored("❌ FEHLER: Konnte Testdaten nicht als JSON parsen.", 'red'))
        sys.exit(1)

    print("\n" + "="*50)
    print("🎉 FERTIG! Generierung abgeschlossen.")
    print("=====================================")

if __name__ == "__main__":
    main()
    # =========================================================
    # SCHRITT 3: Testfall-Validierung (Automatischer Aufruf)
    # =========================================================
    testdata_validator.validate_test_data() 
    
    print(colored("\nNächster Schritt: Führen Sie 'python mock_server_builder.py' aus.", 'cyan'))