import requests
from config.settings import get_config

"""
SETUP WITHINGS
1. Skapa app på https://developer.withings.com/dashboard/
2. Sätt Redirect URI till: http://localhost
3. Kopiera Client ID och Secret till settings.py
4. Klistra in denna URL i din webbläsare (ersätt DITT_CLIENT_ID):
   https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=DITT_CLIENT_ID&state=daa_setup&scope=user.metrics,user.activity,user.info&redirect_uri=http://localhost
5. Godkänn och kopiera 'code' från URL:en du skickas till (allt efter code=)
6. Kör detta skript.
"""

def get_initial_token(auth_code):
    cfg = get_config()
    url = "https://wbsapi.withings.net/v2/oauth2"
    payload = {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': cfg['WITHINGS_CLIENT_ID'],
        'client_secret': cfg['WITHINGS_CLIENT_SECRET'],
        'code': auth_code,
        'redirect_uri': 'http://localhost'
    }
    
    res = requests.post(url, data=payload)
    data = res.json()
    
    if data.get('status') == 0:
        print(f"\nSUCCÉ! Ditt Refresh Token är:\n{data['body']['refresh_token']}")
        print("\nKlistra in detta i config/settings.py under WITHINGS_REFRESH_TOKEN")
    else:
        print(f"Fel: {data}")

if __name__ == "__main__":
    code = input("Klistra in 'code' från webbläsaren: ")
    get_initial_token(code)
