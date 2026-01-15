import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

"""
==============================================================================
FILE: config/settings.py
PROJECT: DAA Digital Advanced Assistant
==============================================================================

DESCRIPTION:
    Central configuration file. Contains API keys, server settings, and paths.
    Now includes MQTT configuration for Home Automation.
"""

# ==============================================================================
# 1. GENERAL APPLICATION SETTINGS
# ==============================================================================

APP_NAME = "DAA Digital Advanced Assistant"
VERSION = "2.2 (Server Intelligence)"
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# ==============================================================================
# 2. SERVER CONFIGURATION
# ==============================================================================

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 3500))

# ==============================================================================
# 3. API KEYS & CREDENTIALS
# ==============================================================================

# Google Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Service Account for Google Calendar
# Ensure this file is present in your root directory
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")

# ==============================================================================
# 4. EXTERNAL SERVICES (LOCAL AI)
# ==============================================================================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_DEFAULT_MODEL = "llama3"

# ==============================================================================
# 5. MQTT / IOT CONFIGURATION (ZIGBEE2MQTT)
# ==============================================================================

# IP address of your MQTT Broker (e.g., Home Assistant or Mosquitto)
MQTT_BROKER_IP = os.getenv("MQTT_BROKER_IP", "192.168.107.6") 
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_BASE = "zigbee2mqtt"

# ==============================================================================
# 6. FILE PATHS & DIRECTORIES
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(LOG_PATH, "daa_memory.db")

# ==============================================================================
# 7. CONFIGURATION EXPORT
# ==============================================================================

def get_config():
    """
    Returns the configuration as a dictionary.
    """
    return {
        "APP_NAME": APP_NAME,
        "VERSION": VERSION,
        "DEBUG_MODE": DEBUG_MODE,
        "HOST": HOST,
        "PORT": PORT,
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "SERVICE_ACCOUNT_FILE": SERVICE_ACCOUNT_FILE,
        "OLLAMA_URL": OLLAMA_URL,
        "OLLAMA_DEFAULT_MODEL": OLLAMA_DEFAULT_MODEL,
        "MQTT_BROKER_IP": MQTT_BROKER_IP,
        "MQTT_PORT": MQTT_PORT,
        "MQTT_TOPIC_BASE": MQTT_TOPIC_BASE,
        "BASE_DIR": BASE_DIR,
        "LOG_DIR": LOG_PATH,
        "DB_PATH": DB_PATH
    }
