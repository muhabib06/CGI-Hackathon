🚀 API Mock Server Generator (KI-gestützt)

Dieses Projekt demonstriert einen automatisierten Workflow zur Erstellung eines funktionsfähigen API-Mock-Servers (mit FastAPI) und der zugehörigen Pytest-Testfälle, basierend auf einer einzigen textuellen Anforderung (dem "Topic"). Die gesamte Generierung von OpenAPI-Spezifikation, Testdaten, Mock-Server-Code und Test-Code wird durch einen LLM-Agenten gesteuert.

🛠️ Komponenten des Systems

Das System besteht aus mehreren aufeinander aufbauenden Python-Skripten, die den gesamten Generierungs- und Validierungsprozess steuern:

Datei

Rolle

Beschreibung

main.py

HAUPT-CONTROLLER

Startet den gesamten Workflow. Steuert den Dialog (topic.py), veranlasst die KI-Generierung (OpenAPI, Testdaten) und ruft die Code-Generatoren auf.

topic.py

REQUIREMENTS-ENGINEER

Führt einen interaktiven Dialog mit dem Benutzer, um das API-Thema zu schärfen und auf Plausibilität zu prüfen, bevor die Generierung beginnt.

prompts.py

PROMPT-BIBLIOTHEK

Enthält alle System- und User-Prompts, die für die Kommunikation mit dem LLM (Generierung von Spec, Testdaten, Validierung) verwendet werden.

testdata_validator.py

VALIDATOR

Prüft die generierten Testdaten (testdata.json) erneut durch einen LLM, um die Einhaltung der 5 geforderten Negativ-/Positiv-Szenarien sicherzustellen.

mock_server_builder.py

SERVER-GENERATOR

Liest die finale openapi_definition.json und testdata.json ein und generiert daraus das lauffähige FastAPI-Mock-Server-Skript (mock_server.py).

generate_tests.py

TEST-GENERATOR

Liest testdata.json und generiert daraus die Pytest-Integrationstests (test_mock_api.py) für die CRUD-Operationen.

mock_server.py

GENERIERTER SERVER

Der fertige FastAPI-Mock-Server-Code.

test_mock_api.py

GENERIERTE TESTS

Die Pytest-Tests, um den mock_server.py zu überprüfen.

openapi_definition.json

GENERIERTE SPEZIFIKATION

Die finale OpenAPI 3.0 (oder 3.1) Spezifikation.

testdata.json

GENERIERTE DATEN

Testdatensatz für den Mock-Server und die Tests.

⚙️ Voraussetzungen

Um das Projekt ausführen zu können, müssen folgende Voraussetzungen erfüllt sein:

Python 3.x

Abhängigkeiten: Alle benötigten Python-Pakete (z.B. fastapi, uvicorn, requests, pytest, pydantic, termcolor) müssen installiert sein.

pip install fastapi uvicorn requests pytest pydantic termcolor


API-Token: Sie benötigen einen API-Token für den LLM-Service (im Code als IONOS_API_TOKEN referenziert). Dieser muss als Umgebungsvariable gesetzt werden:

export IONOS_API_TOKEN="<Ihr-Token-hier>"


🚀 Workflow (Schritt-für-Schritt)

Phase 1: Generierung und Validierung

Start des Workflows:
Führen Sie das Hauptskript aus. Dies startet den interaktiven Modus.

python main.py


Interaktive Themenklärung:
Das Skript fragt nach Ihrer API-Idee und führt Sie durch eine Schleife zur Schärfung des Scopes, unterstützt durch den REQUIREMENTS-ENGINEER (topic.py).

LLM-Generierung:
Das LLM generiert die openapi_definition.json und die testdata.json.

Validierung:
Die generierten Testdaten werden automatisch durch den VALIDATOR (testdata_validator.py) validiert, um die Qualität des generierten Inhalts sicherzustellen.

Code-Generierung:
Anschließend werden der Mock-Server (mock_server.py) und die Testdatei (test_mock_api.py) generiert.

Phase 2: Test und Nutzung

Mock-Server starten:
Führen Sie den generierten Mock-Server aus.

python mock_server.py


Der Server ist nun unter http://127.0.0.1:8000 verfügbar. Die Swagger UI-Dokumentation finden Sie unter http://127.0.0.1:8000/docs.

Tests ausführen:
Öffnen Sie ein zweites Terminalfenster und führen Sie die generierten Pytest-Tests aus. Diese Tests kommunizieren direkt mit dem laufenden Mock-Server und prüfen die gesamte CRUD-Funktionalität.

pytest test_mock_api.py


Analyse-Modus (Optional):
Wenn Sie eine bereits vorhandene OpenAPI-Spezifikation (z.B. jira_like_openapi.json) verwenden möchten, starten Sie das Skript im Analyse-Modus, um neue Testdaten, den Mock-Server und die Tests zu generieren:

python main.py --analyze jira_like_openapi.json
