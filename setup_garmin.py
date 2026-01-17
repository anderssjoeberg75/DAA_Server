"""
setup_garmin.py
Kör detta skript EN gång manuellt för att logga in på Garmin och spara inloggningen.
Version: 2.0 (Anpassad för nya garminconnect med Garth)
"""
import os
from garminconnect import Garmin
from config.settings import GARMIN_EMAIL, GARMIN_PASSWORD, BASE_DIR

# Vi sparar i en mapp istället för en fil nu (krav från nya biblioteket)
TOKEN_DIR = os.path.join(BASE_DIR, "config", "garmin_tokens")

def init_garmin():
    print(f"--- GARMIN SETUP ---")
    print(f"Försöker logga in som: {GARMIN_EMAIL}")
    
    try:
        # 1. Initiera klienten
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        
        # 2. Logga in (kan be om 2FA-kod i terminalen)
        client.login()
        print("Inloggning lyckades!")
        
        # 3. Skapa mappen om den inte finns
        if not os.path.exists(TOKEN_DIR):
            os.makedirs(TOKEN_DIR)
            print(f"Skapade mapp: {TOKEN_DIR}")
        
        # 4. Spara tokens (Garth-format)
        print(f"Sparar tokens till mappen: {TOKEN_DIR}")
        client.garth.dump(TOKEN_DIR)
            
        print("KLART! Nu kan DAA-servern använda denna mapp.")
        
    except Exception as e:
        print(f"\n[FEL] Kunde inte logga in: {e}")
        print("Tips: Kontrollera lösenord och 2FA-kod.")

if __name__ == "__main__":
    init_garmin()