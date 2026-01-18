import os

"""
==============================================================================
FILE: config/settings.py
PROJECT: DAA Digital Advanced Assistant
==============================================================================
"""

# ==============================================================================
# GENERAL APPLICATION SETTINGS
# ==============================================================================
APP_NAME = "DAA Digital Advanced Assistant"
VERSION = "1.0 (Dynamic & HA)"
DEBUG_MODE = True

# ==============================================================================
# SERVER CONFIGURATION
# ==============================================================================
HOST = "0.0.0.0"
PORT = 3500

# ==============================================================================
# FILE PATHS
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(LOG_PATH, "daa_memory.db")


# ==============================================================================
# MEMORY SETTINGS (NYTT!)
# ==============================================================================

# Hur många meddelanden AI:n ska "komma ihåg" i en session.
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", 600))

# ==============================================================================
# API KEYS & CREDENTIALS
# ==============================================================================
# Hämta nyckel här: https://aistudio.google.com/
GOOGLE_API_KEY = ""
OPENAI_API_KEY = ""
ANTHROPIC_API_KEY = ""
GROQ_API_KEY = ""
DEEPSEEK_API_KEY = ""

# Filen ska ligga i 'config'-mappen
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "config", "service_account.json")

# ==============================================================================
# LOCAL AI (OLLAMA)
# ==============================================================================
OLLAMA_URL = "http://127.0.0.1:11434"
# Fallback om vi inte kan hämta listan
OLLAMA_DEFAULT_MODEL = "llama3"

# ==============================================================================
# HOME ASSISTANT (Styrning)
# ==============================================================================
HA_BASE_URL = "" # Din HA IP
HA_TOKEN = ""

# ==============================================================================
# ZIGBEE2MQTT (Sensorer)
# ==============================================================================
MQTT_BROKER_IP = ""
MQTT_PORT = 1883
MQTT_TOPIC_BASE = "zigbee2mqtt"

# ==============================================================================
# LOCATION SETTINGS (För Väder & Astro)
# ==============================================================================
LATITUDE = float(os.getenv("LATITUDE", xx.xxxx))
LONGITUDE = float(os.getenv("LONGITUDE", xx.xxxx))

# ==============================================================================
# GARMIN SETTINGS
# ==============================================================================
# GARMIN CONFIGURATION
GARMIN_EMAIL = ""
GARMIN_PASSWORD = ""

# ==============================================================================
# EXPORT
# ==============================================================================
def get_config():
    return {
        "APP_NAME": APP_NAME,
        "LATITUDE": LATITUDE,
        "LONGITUDE": LONGITUDE,
        "VERSION": VERSION,
        "DEBUG_MODE": DEBUG_MODE,
        "HOST": HOST,
        "PORT": PORT,
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "GROQ_API_KEY": GROQ_API_KEY,
        "DEEPSEEK_API_KEY": DEEPSEEK_API_KEY,
        "SERVICE_ACCOUNT_FILE": SERVICE_ACCOUNT_FILE,
        "OLLAMA_URL": OLLAMA_URL,
        "OLLAMA_DEFAULT_MODEL": OLLAMA_DEFAULT_MODEL,
        "HA_BASE_URL": HA_BASE_URL,
        "HA_TOKEN": HA_TOKEN,
        "MQTT_BROKER_IP": MQTT_BROKER_IP,
        "MQTT_PORT": MQTT_PORT,
        "MQTT_TOPIC_BASE": MQTT_TOPIC_BASE,
        "BASE_DIR": BASE_DIR,
        "LOG_DIR": LOG_PATH,
        "DB_PATH": DB_PATH
    }
