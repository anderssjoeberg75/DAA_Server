"""
client.py
---------
Dynamic Terminal Client for DAA Server.
Updates:
- Colorized Interface (Cyan/Green theme).
- Auto-selects 'Gemini 2.5 Flash' as default if available.
"""

import requests
import sys
import os
import uuid
import argparse

# --- CONFIGURATION ---
DEFAULT_SERVER_URL = "http://127.0.0.1:3500"

# --- COLORS (ANSI ESCAPE CODES) ---
class Colors:
    HEADER = '\033[95m'      # Pink/Purple
    BLUE = '\033[94m'        # Blue
    CYAN = '\033[96m'        # Cyan (System messages)
    GREEN = '\033[92m'       # Green (Success/Input)
    YELLOW = '\033[93m'      # Yellow (Warnings/Highlights)
    FAIL = '\033[91m'        # Red
    ENDC = '\033[0m'         # Reset
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_server_config():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(description="DAA Terminal Client")
    parser.add_argument("--url", type=str, default=DEFAULT_SERVER_URL, help="URL to DAA Server")
    args = parser.parse_args()
    return args.url

def fetch_available_models(server_url):
    """Fetches models from /api/models."""
    print(f"{Colors.CYAN}Connecting to {server_url}...{Colors.ENDC}")
    try:
        response = requests.get(f"{server_url}/api/models", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}Error: Could not connect to server.{Colors.ENDC}")
        return []

def select_model(models):
    """
    Displays a menu and selects a model.
    Prioritizes 'Gemini 2.5 Flash' as the default.
    """
    if not models:
        print(f"{Colors.YELLOW}No models found. Using fallback ID.{Colors.ENDC}")
        return "gemini-1.5-flash"

    # --- LOGIC: FIND PREFERRED DEFAULT (Gemini 2.5 Flash) ---
    default_index = 0
    for idx, m in enumerate(models):
        name_lower = m['id'].lower()
        # Look for 2.5 AND flash. If not found, fallback to just flash.
        if "2.5" in name_lower and "flash" in name_lower:
            default_index = idx
            break
        elif "flash" in name_lower and "2.5" not in name_lower:
            # Secondary preference if 2.5 doesn't exist yet
            default_index = idx

    print(f"\n{Colors.HEADER}--- AVAILABLE MODELS ---{Colors.ENDC}")
    
    for idx, m in enumerate(models):
        # Color the output
        if idx == default_index:
            # Highlight the default option in Green
            prefix = f"{Colors.GREEN}* {idx + 1}.{Colors.ENDC}"
            suffix = f"{Colors.GREEN}(Default){Colors.ENDC}"
            name_display = f"{Colors.BOLD}{m['name']}{Colors.ENDC}"
        else:
            prefix = f"  {idx + 1}."
            suffix = ""
            name_display = m['name']
            
        print(f"{prefix} {name_display} {suffix}")

    print(f"{Colors.CYAN}------------------------{Colors.ENDC}")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}Select model (Enter for default): {Colors.ENDC}")
            
            # If user presses Enter, use the calculated default (Gemini 2.5 Flash)
            if not user_input.strip():
                selected = models[default_index]['id']
                print(f"{Colors.CYAN}Selected default: {Colors.BOLD}{selected}{Colors.ENDC}")
                return selected
            
            # Parse number
            idx = int(user_input) - 1
            if 0 <= idx < len(models):
                return models[idx]['id']
                
        except ValueError:
            pass
        print(f"{Colors.FAIL}Invalid selection. Try again.{Colors.ENDC}")

def handle_pc_commands(full_response):
    """Parses hidden system tags."""
    if "[DO:SYS|lock]" in full_response:
        print(f"\n{Colors.YELLOW}🔒 [CLIENT] Locking workstation...{Colors.ENDC}")
        if os.name == 'nt': os.system("rundll32.exe user32.dll,LockWorkStation")
    
    elif "[DO:SYS|calc]" in full_response:
        print(f"\n{Colors.YELLOW}🧮 [CLIENT] Opening calculator...{Colors.ENDC}")
        if os.name == 'nt': os.system("calc")
            
    elif "[DO:SYS|minimize]" in full_response:
        print(f"\n{Colors.YELLOW}🖥️ [CLIENT] Minimizing windows...{Colors.ENDC}")
        try:
            import pyautogui
            pyautogui.hotkey('win', 'd')
        except: pass

    elif "[DO:BROWSER|" in full_response:
        try:
            start = full_response.find("[DO:BROWSER|") + 12
            end = full_response.find("]", start)
            url = full_response[start:end]
            print(f"\n{Colors.YELLOW}🌐 [CLIENT] Opening: {url}{Colors.ENDC}")
            import webbrowser
            webbrowser.open(url)
        except: pass

def print_stream(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def chat_loop():
    server_url = get_server_config()
    models = fetch_available_models(server_url)
    
    # Select model (Auto-defaults to 2.5 Flash if available)
    model_id = select_model(models)
    
    # Generate Session ID
    session_id = str(uuid.uuid4())
    print(f"\n{Colors.CYAN}--- SESSION STARTED ({session_id[:8]}) ---{Colors.ENDC}")
    print(f"{Colors.CYAN}Type 'exit' to quit.{Colors.ENDC}\n")

    while True:
        try:
            # Input in Green
            user_input = input(f"{Colors.GREEN}You: {Colors.ENDC}")
            if user_input.lower() in ["exit", "quit"]: break
            
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": user_input}],
                "session_id": session_id
            }

            print(f"{Colors.BLUE}DAA: {Colors.ENDC}", end="")
            
            full_response = ""
            with requests.post(f"{server_url}/api/chat", json=payload, stream=True) as r:
                if r.status_code != 200:
                    print(f"{Colors.FAIL}Error: {r.status_code}{Colors.ENDC}")
                    continue

                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        text = chunk.decode("utf-8")
                        full_response += text
                        print_stream(text)
            
            print() 
            handle_pc_commands(full_response)
            
        except requests.exceptions.ConnectionError:
            print(f"\n{Colors.FAIL}Lost connection.{Colors.ENDC}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    # Windows terminal color fix
    if os.name == 'nt':
        os.system('color')
    chat_loop()