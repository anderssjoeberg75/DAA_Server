import os
import datetime
from garminconnect import Garmin
from config.settings import GARMIN_EMAIL, GARMIN_PASSWORD, BASE_DIR

class GarminCoach:
    def __init__(self):
        self.client = None
        # Peka på mappen med tokens
        self.token_dir = os.path.join(BASE_DIR, "config", "garmin_tokens")
        self._login()

    def _login(self):
        """Loggar in och säkerställer att vi har ett Display Name."""
        try:
            self.client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)

            # 1. Försök ladda sparad session
            if os.path.exists(self.token_dir):
                print(">> [Garmin] Laddar sparade tokens...")
                try:
                    self.client.garth.load(self.token_dir)
                    
                    # VIKTIGT: Vi måste anropa login() även om vi laddat tokens.
                    # Detta verifierar tokens mot Garmin OCH hämtar ditt 'display_name'.
                    # Utan detta blir namnet 'None' och anropen misslyckas.
                    self.client.login()
                    
                    print(f">> [Garmin] Inloggad via session som: {self.client.display_name}")
                    return
                except Exception as e:
                    print(f">> [Garmin] Kunde inte återanvända tokens: {e}")

            # 2. Fallback: Full inloggning (om tokens saknades eller var ogiltiga)
            print(">> [Garmin] Loggar in med lösenord...")
            self.client.login()
            
            # Spara tokens automatiskt
            if not os.path.exists(self.token_dir):
                os.makedirs(self.token_dir)
            self.client.garth.dump(self.token_dir)
            print(f">> [Garmin] Nya tokens sparade. Inloggad som: {self.client.display_name}")
                
        except Exception as e:
            print(f">> [Garmin] Inloggningsfel: {e}")
            self.client = None

    def get_health_report(self):
        if not self.client:
            self._login()
            if not self.client: return None

        try:
            # Hämtar dagens datum
            today = datetime.date.today().isoformat()
            
            # Hämta grunddata (Steps, HR etc)
            # Här kommer det fungera nu eftersom self.client.display_name är satt
            stats = self.client.get_user_summary(today)
            
            # Fallback till igår om ingen data finns än (t.ex. tidigt på morgonen)
            if not stats or stats.get('totalSteps') == 0:
                yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
                stats = self.client.get_user_summary(yesterday)
                today = f"{yesterday} (Igår)"

            data = {
                "datum": today,
                "steg": stats.get("totalSteps", 0),
                "vilopuls": stats.get("restingHeartRate", "Ingen data"),
                "stress_snitt": stats.get("averageStressLevel", "Ingen data"),
                "sömn_timmar": round(stats.get("sleepingSeconds", 0) / 3600, 1)
            }
            
            # Försök hämta Body Battery om det finns
            if 'bodyBattery' in stats:
                 data['body_battery'] = stats['bodyBattery']

            return data

        except Exception as e:
            print(f">> [Garmin] Fetch Error: {e}")
            return None