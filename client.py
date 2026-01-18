"""
client.py
---------
Dynamic Terminal Client for DAA Server.
"""

import requests
import sys
import os
import uuid
import argparse

# --- CONFIGURATION ---
DEFAULT_SERVER_URL = "http://127.0.0.1:3500"

# --- COLORS ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_server_config():
    parser = argparse.ArgumentParser(description="DAA Terminal Client")
    parser.add_argument("--url", type=str, default=DEFAULT_SERVER_URL, help="URL to DAA Server")
    args = parser.parse_args()
    return args.url

def fetch_available_models(server_url):
    print(f"{Colors.CYAN}Connecting to {server_url}...{Colors.ENDC}")
    try:
        response = requests.get(f"{server_url}/api/models", timeout=5)
        if response.status_code == 200:
            json_resp = response.json()
            # FIX: Hantera både {"data": [...]} och ren lista [...]
            if isinstance(json_resp, dict) and "data" in json_resp:
                return json_resp["data"]
            elif isinstance(json_resp, list):
                return json_resp
        return []
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}Error: Could not connect to server.{Colors.ENDC}")
        return []

def select_model(models):
    if not models:
        print(f"{Colors.YELLOW}No models found via API. Using fallback ID.{Colors.ENDC}")
        return "gemini-1.5-flash"

    # Default logic: Gemini 2.5 > Flash > First available
    default_index = 0
    for idx, m in enumerate(models):
        if not isinstance(m, dict): continue # Safety check
        name_lower = m.get('id', '').lower()
        if "2.5" in name_lower and "flash" in name_lower:
            default_index = idx
            break
        elif "flash" in name_lower:
            default_index = idx

    print(f"\n{Colors.HEADER}--- AVAILABLE MODELS ---{Colors.ENDC}")
    
    for idx, m in enumerate(models):
        if not isinstance(m, dict): continue
        if idx == default_index:
            print(f"{Colors.GREEN}* {idx + 1}. {m.get('name', 'Unknown')} (Default){Colors.ENDC}")
        else:
            print(f"  {idx + 1}. {m.get('name', 'Unknown')}")

    print(f"{Colors.CYAN}------------------------{Colors.ENDC}")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}Select model (Enter for default): {Colors.ENDC}")
            if not user_input.strip():
                selected = models[default_index]['id']
                print(f"{Colors.CYAN}Selected: {selected}{Colors.ENDC}")
                return selected
            
            idx = int(user_input) - 1
            if 0 <= idx < len(models):
                return models[idx]['id']
        except ValueError: pass
        print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")

def print_stream(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def chat_loop():
    server_url = get_server_config()
    models = fetch_available_models(server_url)
    model_id = select_model(models)
    session_id = str(uuid.uuid4())
    
    print(f"\n{Colors.CYAN}--- SESSION STARTED ---{Colors.ENDC}")

    while True:
        try:
            user_input = input(f"{Colors.GREEN}You: {Colors.ENDC}")
            if user_input.lower() in ["exit", "quit"]: break
            
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": user_input}],
                "session_id": session_id
            }

            print(f"{Colors.BLUE}DAA: {Colors.ENDC}", end="")
            
            # Simple sync request (streaming is handled by server accumulating response for now)
            r = requests.post(f"{server_url}/api/chat", json=payload)
            if r.status_code == 200:
                print(r.text)
            else:
                print(f"{Colors.FAIL}Error: {r.status_code}{Colors.ENDC}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")

if __name__ == "__main__":
    if os.name == 'nt': os.system('color')
    chat_loop()