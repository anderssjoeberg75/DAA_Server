import requests
from datetime import datetime, timedelta
from config.settings import get_config
from .formatter import format_temp_for_speech

"""
==============================================================================
FILE: app/tools/weather_core.py
PROJECT: DAA Digital Advanced Assistant
DESCRIPTION: Väderverktyg med förbättrad sökning efter veckoprognos.
==============================================================================
"""

cfg = get_config()

def get_weather():
    """
    Hämtar väderprognos från SMHI och returnerar text optimerad för TTS.
    Täcker nuvarande väder, imorgon och kommande dagar.
    """
    lat = cfg.get("LATITUDE")
    lon = cfg.get("LONGITUDE")

    if lat is None or lon is None:
        return "Systemfel: Koordinater saknas i settings punkt py."

    # SMHI API (pmp3g v2)
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{round(float(lon), 4)}/lat/{round(float(lat), 4)}/data.json"
    
    headers = {"User-Agent": "DAA-Digital-Advanced-Assistant/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Kunde inte nå vädertjänsten just nu."

        data = response.json()
        series = data.get("timeSeries", [])
        if not series:
            return "Ingen väderdata tillgänglig för din position."

        # Säkrare helper för parametrar
        def find_p(p_list, name):
            for p in p_list:
                if p["name"] == name: return p["values"][0]
            return None

        # Mappning av vädersymboler till naturligt talspråk
        wm = {
            1: "klart", 2: "mestadels klart", 3: "varierande molnighet", 4: "halvklart", 
            5: "molnigt", 6: "mulet", 7: "dimma", 8: "lätta regnskurar", 9: "regnskurar", 
            10: "kraftiga regnskurar", 18: "lätt regn", 19: "regn", 20: "kraftigt regn",
            25: "lätt snöfall", 26: "snöfall", 27: "kraftigt snöfall"
        }

        # --- 1. JUST NU ---
        now = series[0]
        curr_temp = find_p(now["parameters"], "t")
        curr_cond = wm.get(find_p(now["parameters"], "Wsymb2"), "växlande molnighet")
        report = f"Vädret just nu är {curr_cond} och det är {format_temp_for_speech(curr_temp)}.\n"

        # --- 2. VECKOPROGNOSTISERING ---
        # Vi skapar en ordlista för att spara en prognos per dag
        daily_forecasts = {}
        
        # Vi tittar på alla tidspunkter i serien
        for entry in series:
            valid_time = datetime.strptime(entry["validTime"], "%Y-%m-%dT%H:%M:%SZ")
            date_key = valid_time.strftime("%Y-%m-%d")
            
            # Vi hoppar över idag
            if date_key == datetime.now().strftime("%Y-%m-%d"):
                continue
                
            # Vi försöker hitta en tidpunkt så nära lunch (kl 12:00) som möjligt för varje dag
            # Om vi inte hittat något för denna dag än, eller om denna tidpunkt är närmare kl 12
            current_hour = valid_time.hour
            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = entry
            else:
                existing_time = datetime.strptime(daily_forecasts[date_key]["validTime"], "%Y-%m-%dT%H:%M:%SZ")
                if abs(current_hour - 12) < abs(existing_time.hour - 12):
                    daily_forecasts[date_key] = entry

        # Sortera dagarna och bygg rapporten
        sorted_days = sorted(daily_forecasts.keys())
        day_map = {
            "Mon": "måndag", "Tue": "tisdag", "Wed": "onsdag", 
            "Thu": "torsdag", "Fri": "fredag", "Sat": "lördag", "Sun": "söndag"
        }

        if sorted_days:
            report += "Här är prognosen för veckan: "
            forecast_parts = []
            
            # Ta med max 5 dagar framåt för att hålla det kort
            for d_key in sorted_days[:5]:
                f_entry = daily_forecasts[d_key]
                temp = find_p(f_entry["parameters"], "t")
                day_name_en = datetime.strptime(d_key, "%Y-%m-%d").strftime("%a")
                day_name_se = day_map.get(day_name_en, day_name_en)
                
                forecast_parts.append(f"på {day_name_se} blir det {format_temp_for_speech(temp)}")
            
            report += ", ".join(forecast_parts) + "."
        else:
            report += "Jag kunde tyvärr inte hitta några detaljer för resten av veckan."

        return report

    except Exception as e:
        return f"Ett tekniskt fel uppstod vid väderhämtning: {str(e)}"