"""
app/tools/ha_core.py
--------------------
Hanterar kommunikation med Home Assistant API.
Nu med stöd för LAMPOR, Dammsugare och Sensorer.
"""
import httpx
from config.settings import get_config

cfg = get_config()

HEADERS = {
    "Authorization": f"Bearer {cfg['HA_TOKEN']}", 
    "Content-Type": "application/json"
}

def get_ha_state(entity_id: str):
    """Läser status från en sensor/enhet."""
    base_url = cfg['HA_BASE_URL'].rstrip('/')
    url = f"{base_url}/api/states/{entity_id}"
    
    with httpx.Client() as client:
        try:
            resp = client.get(url, headers=HEADERS, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                state = data.get("state")
                unit = data.get("attributes", {}).get("unit_of_measurement", "")
                friendly = data.get("attributes", {}).get("friendly_name", entity_id)
                return f"{friendly}: {state} {unit}"
            return f"Fel: {resp.status_code}"
        except Exception as e:
            return f"HA Error: {e}"

def control_light(entity_id: str, action: str):
    """
    Tänder eller släcker en lampa.
    Args:
        entity_id: T.ex. 'light.kontoret'
        action: 'on' (tänd) eller 'off' (släck)
    """
    base_url = cfg['HA_BASE_URL'].rstrip('/')
    
    # Avgör om det är en lampa eller switch baserat på namnet, eller tvinga 'light'
    domain = entity_id.split(".")[0] # Tar 'light' från 'light.kontoret'
    
    # Mappa 'on'/'off' till rätt tjänst i HA
    if action.lower() in ["on", "tänd", "starta", "true"]:
        service = "turn_on"
    else:
        service = "turn_off"

    url = f"{base_url}/api/services/{domain}/{service}"
    
    with httpx.Client() as client:
        try:
            resp = client.post(url, headers=HEADERS, json={"entity_id": entity_id}, timeout=5.0)
            if resp.status_code == 200:
                return f"OK. {action} utfört på {entity_id}."
            return f"Fel vid styrning av lampa: {resp.text}"
        except Exception as e:
            return f"Kunde inte nå HA: {e}"

def control_vacuum(entity_id: str, action: str):
    """Styr dammsugaren."""
    base_url = cfg['HA_BASE_URL'].rstrip('/')
    if "." not in entity_id: entity_id = f"vacuum.{entity_id}"
    
    action_map = {"start": "start", "stop": "stop", "dock": "return_to_base"}
    service = action_map.get(action.lower(), "start")
    url = f"{base_url}/api/services/vacuum/{service}"
    
    with httpx.Client() as client:
        try:
            client.post(url, headers=HEADERS, json={"entity_id": entity_id}, timeout=5.0)
            return f"Dammsugare {action} skickat."
        except Exception as e:
            return f"Fel: {e}"