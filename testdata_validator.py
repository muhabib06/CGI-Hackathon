# testdata_validator.py

import json
import sys
import os
import requests
from termcolor import colored 
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- Konfiguration ---
IONOS_TOKEN = os.getenv("IONOS_API_TOKEN")
API_URL = "https://openai.inference.de-txl.ionos.com/v1/chat/completions"
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

TEST_VALIDATION_PROMPT = {
    "system": "Du bist ein erfahrener QA-Analyst. Deine Aufgabe ist es, die Vollständigkeit einer Reihe von Testfällen basierend auf den Anforderungen zu prüfen. Antworte immer kurz und präzise.",
    "user": """
Ich habe 5 Testfälle für eine POST-Operation generiert. Die Anforderungen waren:
1. Positive: Alle möglichen Felder gefüllt.
2. Positive: Nur erforderliche Felder gefüllt.
3. Negative: Ein erforderliches Feld fehlt.
4. Negative: Logischer Fehler (z.B. ungültiger Datumsbereich).
5. Negative: Ungültiger Datentyp (z.B. String statt Integer).

Hier sind die generierten Testfälle (JSON):
{test_data_content}

Prüfe, ob diese 5 Szenarien in der Liste abgedeckt sind.
Antworte NUR mit einer nummerierten Liste:
- Falls ein Szenario fehlt oder nicht erkennbar ist: Nenne das Szenario und erkläre KURZ warum (max. 1 Satz).
- Falls alle Szenarien erfüllt sind: Antworte NUR mit 'ALLE FÜNF SZENARIEN SIND ERFÜLLT.'
"""
}

def query_llm(system_prompt: str, user_prompt: str) -> str:
    """Hilfsfunktion: Sendet Anfragen an die KI."""
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
        print(colored(f"❌ API Request Failed (Test Validator): {e}", 'red'))
        sys.exit(1)


def validate_test_data(data_filename: str = "testdata.json"):
    """Prüft die Testdaten mithilfe des LLM."""
    print("\n--- 3. TESTFALL-VALIDATOR GESTARTET ---")

    if not IONOS_TOKEN:
        print(colored("❌ FEHLER: IONOS_API_TOKEN fehlt. Kann Validierung nicht durchführen.", 'red'))
        return

    try:
        with open(data_filename, 'r', encoding='utf-8') as f:
            test_data_raw = json.load(f)
    except FileNotFoundError:
        print(colored(f"❌ FEHLER: Datei '{data_filename}' nicht gefunden. Führen Sie zuerst main.py aus.", 'red'))
        return
    except json.JSONDecodeError:
        print(colored(f"❌ FEHLER: Konnte JSON aus '{data_filename}' nicht dekodieren.", 'red'))
        return

    test_data_content = json.dumps(test_data_raw, indent=2)

    print("🔎 Sende Testfälle zur Validierung an LLM...")
    
    formatted_prompt = TEST_VALIDATION_PROMPT["user"].format(test_data_content=test_data_content)
    
    validation_result = query_llm(
        TEST_VALIDATION_PROMPT["system"],
        formatted_prompt
    )
    
    validation_result = validation_result.strip()

    print("\n--- ERGEBNIS DER TESTFALL-VALIDIERUNG ---")
    
    if "ALLE FÜNF SZENARIEN SIND ERFÜLLT" in validation_result.upper():
        print(colored("✅ Die KI bestätigt: Alle 5 geforderten Test-Szenarien sind vorhanden.", 'green'))
    else:
        print(colored("⚠️ WARNUNG: Die KI hat Mängel in den generierten Testfällen festgestellt:", 'yellow'))
        print(validation_result)

    print("------------------------------------------")


if __name__ == "__main__":
    validate_test_data()