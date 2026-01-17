import sys
import os
import httpx

# Fixa sökvägar
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.settings import get_config
cfg = get_config()

# DITT ID
ENTITY_ID = "vacuum.roborock_s5_f528_robot_cleaner"

# VIKTIGT: Här testar vi kommandot som skickar hem den
url = f"{cfg['HA_BASE_URL'].rstrip('/')}/api/services/vacuum/return_to_base"
# OBS: Vissa dammsugare svarar bättre på "stop" först, men vi testar standarden.

headers = {
    "Authorization": f"Bearer {cfg['HA_TOKEN']}",
    "Content-Type": "application/json"
}

print(f"--- TESTAR ATT DOCKA (SKICKA HEM) {ENTITY_ID} ---")

try:
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json={"entity_id": ENTITY_ID}, timeout=10)
        print(f"Statuskod: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Kommando 'return_to_base' skickat! Kolla om dammsugaren vänder hemåt.")
        else:
            print(f"❌ Fel: {response.text}")

except Exception as e:
    print(f"❌ Nätverksfel: {e}")