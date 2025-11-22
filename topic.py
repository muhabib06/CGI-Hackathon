# topic.py

import sys
import prompts # WICHTIG: Stellt sicher, dass Sie prompts importieren, um MATURITY_CHECK zu nutzen!

# System-Prompts für die Gesprächsführung
SYSTEM_REFINE = "Du bist ein erfahrener Requirements Engineer. Deine Aufgabe ist es, den Input des Users in eine präzise, technische Beschreibung für eine REST-API umzuwandeln. Liste die Kern-Ressourcen und wichtige Felder auf. Antworte direkt mit dem Scope."
SYSTEM_SENTIMENT = "Du bist eine Logik-Weiche. Analysiere den User-Input. Wenn der User zustimmt (ja, passt, ok, genau, gut, super), antworte nur mit 'YES'. Wenn der User Änderungen will oder 'nein' sagt, antworte nur mit 'NO'."

def get_final_topic(query_llm_func):
    """
    Führt einen Dialog mit dem User, um das Thema zu schärfen und die Plausibilität zu prüfen.
    """
    print("\n" + "="*50)
    print("💬 API KONFIGURATOR (Interview Modus)")
    print("="*50)
    
    current_description = input("\nBitte beschreibe kurz deine Idee (z.B. 'Verwaltung für Bibliothek'):\n> ")

    if not current_description:
        print("Beschreibung fehlt. Beende.")
        sys.exit(0)
        
    # --- NEUE PLAUSIBILITÄTS-SCHLEIFE ---
    while True:
        # A. Plausibilitätsprüfung
        print("\n🔎 Führe Plausibilitätsprüfung (Maturity Check) durch...")
        
        check_prompt = prompts.MATURITY_CHECK["user"].format(topic=current_description)
        check_result = query_llm_func(
            prompts.MATURITY_CHECK["system"], 
            check_prompt
        )
        
        check_result = check_result.strip().upper()

        if check_result.startswith('YES'):
            # 1. Fall: Input ist klar genug, breche die Plausibilitäts-Schleife ab
            print("✅ Plausibilitätsprüfung bestanden. Beginne mit der Verfeinerung.")
            break
        else:
            # 2. Fall: Input ist nicht ausreichend
            parts = check_result.split('NO', 1)
            reason = parts[1].strip() if len(parts) > 1 else "Die KI hat keine spezifische Begründung geliefert."
            
            print("\n❌ ANFORDERUNG NICHT EINDEUTIG GENUG.")
            print(f"**Begründung:** {reason}")
            
            # Neueingabe anfordern
            new_description = input("\nBitte verbessere deine Eingabe basierend auf der Begründung:\n> ")
            if not new_description:
                 print("Abbruch durch Benutzer.")
                 sys.exit(0)
                 
            current_description = new_description

    # --- ENDE PLAUSIBILITÄTS-SCHLEIFE ---
    
    # --- SCOPE VERFEINERUNGS-SCHLEIFE (Wie zuvor) ---
    while True:
        print("\n⏳ Ich analysiere und strukturiere deine Idee...")
        
        # A. Llama erstellt einen professionellen Vorschlag
        refined_text = query_llm_func(SYSTEM_REFINE, f"Input: {current_description}")
        
        print("\n" + "-"*40)
        print("📋 VORSCHLAG FÜR DEN SCOPE:")
        print("-"*40)
        print(refined_text)
        print("-"*40)

        # B. User Feedback einholen
        user_feedback = input("\nPasst das so? (Antworte mit 'Ja' oder nenne Änderungswünsche):\n> ")

        # C. Prüfen: Ist das ein JA oder ein NEIN?
        sentiment = query_llm_func(SYSTEM_SENTIMENT, f"User Input: {user_feedback}")

        if "YES" in sentiment.upper():
            print("\n✅ Perfekt! Scope ist bestätigt.")
            return refined_text
        else:
            print("\n🔄 Verstanden. Ich arbeite deine Wünsche ein...")
            current_description = f"Bisheriger Entwurf: {refined_text}. Neuer Änderungswunsch: {user_feedback}"