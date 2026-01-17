import datetime
import logging
import time
from garminconnect import Garmin

# HÄR ÄR ÄNDRINGEN: Vi importerar från config-mappen i roten
from config.settings import GARMIN_EMAIL, GARMIN_PASSWORD

# Konfigurera loggning
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GarminCore")

class GarminCoach:
    def __init__(self):
        self.email = GARMIN_EMAIL
        self.password = GARMIN_PASSWORD
        self.client = None
        self.last_login = 0

    def connect(self):
        """Loggar in på Garmin Connect."""
        try:
            # Enkel inloggning
            self.client = Garmin(self.email, self.password)
            self.client.login()
            self.last_login = time.time()
            logger.info("Garmin: Inloggning lyckades.")
            return True
        except Exception as e:
            logger.error(f"Garmin Login Error: {e}")
            return False

    def get_health_report(self):
        """Hämtar dagens hälsodata och analyserar den."""
        # Återanslut om vi tappat klienten
        if not self.client:
            if not self.connect():
                return None

        today = datetime.date.today()
        
        try:
            # Hämta statistik
            stats = self.client.get_user_summary(today.isoformat())
            sleep = self.client.get_sleep_data(today.isoformat())
            
            # Försök hämta aktiviteter (kan kasta fel om inga finns)
            try:
                activities = self.client.get_activities(0, 1)
            except:
                activities = []

            # Skapa grundrapport
            report = {
                "datum": str(today),
                "vilopuls": stats.get('restingHeartRate', 'Okänd'),
                "steg": stats.get('totalSteps', 0),
                "stress_snitt": stats.get('averageStressLevel', 'Okänd'),
                "body_battery": stats.get('bodyBatteryLargestDrain', 'Okänd'),
                "sömn_timmar": 0.0,
                "senaste_träning": "Ingen aktivitet registrerad nyligen."
            }

            # Beräkna sömn
            if sleep and 'dailySleepDTO' in sleep:
                sleep_sec = sleep['dailySleepDTO'].get('sleepTimeSeconds', 0)
                report["sömn_timmar"] = round(sleep_sec / 3600, 1)

            # Analysera senaste aktivitet
            if activities:
                last = activities[0]
                act_date = last['startTimeLocal'].split(" ")[0]
                type_act = last.get('activityType', {}).get('typeKey', 'Träning')
                dist = round(last.get('distance', 0) / 1000, 2)
                tid = round(last.get('duration', 0) / 60, 0)
                
                tidstext = "idag" if act_date == str(today) else f"den {act_date}"
                report["senaste_träning"] = f"{type_act} ({dist} km på {tid} min) {tidstext}."

            return report

        except Exception as e:
            logger.error(f"Fel vid hämtning av data: {e}")
            # Försök logga in igen nästa gång om sessionen dött
            self.client = None 
            return None