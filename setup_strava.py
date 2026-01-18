import requests
from config.settings import get_config

"""
INSTRUKTIONER:
1. Gå till https://www.strava.com/settings/api och hämta ditt Client ID.
2. Ersätt DITT_CLIENT_ID i URL:en nedan och klistra in i din webbläsare:
   https://www.strava.com/oauth/authorize?client_id=DITT_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all

3. Godkänn appen. Du skickas till en sida som inte laddas (localhost). 
   Titta i webbläsarens adressfält och kopiera koden efter 'code=' (t.ex. abcdef12345).

4. Kör detta skript och klistra in koden när det efterfrågas.
"""

def get_initial_token(auth_code):
    cfg = get_config()
    url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': cfg['STRAVA_CLIENT_ID'],
        'client_secret': cfg['STRAVA_CLIENT_SECRET'],
        'code': auth_code,
        'grant_type': 'authorization_code'
    }
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        data = res.json()
        print(f"\nDitt Refresh Token är: {data['refresh_token']}")
        print("Spara detta i settings.py under STRAVA_REFRESH_TOKEN.")
    else:
        print(f"Fel vid hämtning av token: {res.text}")

if __name__ == "__main__":
    code = input("Klistra in 'code' från URL:en: ")
    get_initial_token(code)