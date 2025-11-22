# Das hier ist für die OpenAPI Definition und GAP-Analyse
SPEC_GENERATION = {
    "system": "You are a Senior API Architect. Output only the requested formats separated by a delimiter.",
    "user": """
Create a comprehensive OpenAPI 3.0 JSON definition for a CRUD REST API for the following use case:
"{topic}"

Your task:
1. Analyze the use case and determine appropriate data fields (properties) and data types automatically.
2. Define standard CRUD endpoints (POST, GET, PUT, DELETE).
3. Ensure the JSON is valid.

Structure your response exactly as follows:
<<<JSON_START>>>
[Insert raw OpenAPI JSON here]
<<<SPLIT_MARKER>>>
[Insert concise GAP analysis regarding enterprise readiness here]
"""
}

# Das hier ist für die Plausibilitätsprüfung
MATURITY_CHECK = {
    "system": "Du bist ein erfahrener, hilfsbereiter API-Architekt, der die Qualität von Anforderungen prüft. Bewerte den folgenden Anwendungsfall für eine REST-API.",
    "user": """
Bewerte den folgenden API-Anwendungsfall: '{topic}'

Antworte:
1. Wenn der Anwendungsfall **zu unklar** ist und **keine klaren Hauptentitäten** (z.B. 'Mitarbeiter', 'Urlaubsantrag') oder **grundlegenden Funktionen** (CRUD) ableitbar sind: 
    Antworte NUR mit 'NO' gefolgt von einer KURZEN LISTE (maximal 3 Stichpunkte), die genau erklärt, was fehlt und wie der User es verbessern soll (z.B. 'Es fehlen die zentralen Datenobjekte').
2. Wenn mindestens eine **klare Hauptentität** und eine **CRUD-Funktion** (Erstellen, Abrufen, Aktualisieren, Löschen) implizit oder explizit erkennbar ist: 
    Antworte NUR mit 'YES'.

Zweck ist es, **nur offensichtlich unsinnige oder leere Eingaben** abzulehnen.
"""
}

# Das hier ist für die Testdaten
TEST_DATA_GENERATION = {
    "system": "You are a QA Engineer. Output only raw JSON.",
    "user": """
Based on the following API specification, generate a JSON array containing 5 test objects for the creation endpoint (POST).

Scenarios to generate:
1. Positive: All possible fields filled with valid data.
2. Positive: Only required fields filled with valid data.
3. Negative: A required field is missing (choose one automatically).
4. Negative: Logical error (e.g. numeric value out of realistic range or past date where future is needed).
5. Negative: Invalid data type (e.g. string instead of integer).

Context (The API Definition):
{spec_content}

Output ONLY the valid JSON array. No markdown.
"""
}