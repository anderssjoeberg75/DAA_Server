import os

"""
==============================================================================
FILE: config/settings.py
PROJECT: DAA Digital Advanced Assistant
==============================================================================

DESCRIPTION:
    Central configuration file. Contains API keys, server settings, and paths.
    
    SECURITY NOTE: 
    Do not upload this file to GitHub if it contains real API keys.
    Ensure 'config/settings.py' is in your .gitignore file.
"""

# ==============================================================================
# 1. GENERAL APPLICATION SETTINGS
# ==============================================================================

APP_NAME = "DAA Digital Advanced Assistant"
VERSION = "2.0 (Python Core)"
DEBUG_MODE = True  # Useful for seeing errors during development

# ==============================================================================
# 2. SERVER CONFIGURATION
# ==============================================================================

HOST = "0.0.0.0"
# We use 3500 to match your old Node.js setup
PORT = 3500 

# ==============================================================================
# 3. API KEYS & CREDENTIALS
# ==============================================================================

# Google API Key:
# Insert your real Google Cloud/Gemini API key here.
GOOGLE_API_KEY = "DIN_GOOGLE_API_KEY_HÄR" 

# ==============================================================================
# 4. EXTERNAL SERVICES (LOCAL AI)
# ==============================================================================

# Configuration for Ollama (Local LLM)
OLLAMA_URL = "http://127.0.0.1:11434"
# You can define a default model here if you want (e.g., "llama3" or "mistral")
OLLAMA_DEFAULT_MODEL = "llama3"

# ==============================================================================
# 5. FILE PATHS & DIRECTORIES
# ==============================================================================

# Base Directory:
# Calculates the absolute path to the project root (DAA-Digital-Advanced-Assistant/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Log Directory:
LOG_DIR_NAME = "logs"
LOG_FILENAME = "daa_memory.db" # Or daa.log, depending on usage

# Full Paths:
# We construct full paths using os.path.join for cross-platform compatibility
LOG_PATH = os.path.join(BASE_DIR, LOG_DIR_NAME)
DB_PATH = os.path.join(LOG_PATH, LOG_FILENAME)

# Note: We do not create directories here. 
# The directory creation is handled in app/utils/logger.py or main.py.

# ==============================================================================
# 6. CONFIGURATION EXPORT
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
        "OLLAMA_URL": OLLAMA_URL,
        "OLLAMA_DEFAULT_MODEL": OLLAMA_DEFAULT_MODEL,
        "BASE_DIR": BASE_DIR,
        "LOG_DIR": LOG_PATH,
        "DB_PATH": DB_PATH
    }
