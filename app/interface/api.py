from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import time
from typing import List, Optional

# Vi importerar inställningar och verktyg
from app.tools.garmin_core import GarminCoach
from config.settings import GARMIN_EMAIL, GARMIN_PASSWORD

# Om du har din API-nyckel i settings.py, importera den här.
# Annars, lägg in den direkt nedan som sträng.
# from config.settings import GEMINI_API_KEY 
API_KEY = "DIN_GEMINI_API_KEY_HÄR"  # <--- SE TILL ATT DENNA ÄR RÄTT!

router = APIRouter()

# --- KONFIGURERA GEMINI ---
genai.configure(api_key=API_KEY)

# --- DATAMODELLER ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "gemini-1.5-flash"
    messages: List[Message]
    session_id: Optional[str] = None

# --- INITIERA VERKTYG ---
garmin_tool = GarminCoach()
last_garmin_fetch = 0
cached_garmin_data = None

# --- NY ENDPOINT: LISTA MODELLER (Löser 404-felet) ---
@router.get("/api/models")
async def get_models():
    """Berättar för agenten vilka modeller som finns."""
    return {
        "object": "list",
        "data": [
            {
                "id": "gemini-1.5-flash",
                "object": "model",
                "created": 1686935002,
                "owned_by": "google"
            }
        ]
    }

# --- CHAT ENDPOINT ---
# Vi lägger till både /chat och /api/chat för säkerhets skull
@router.post("/chat")
@router.post("/api/chat")
async def chat(request: ChatRequest):
    global last_garmin_fetch, cached_garmin_data
    
    user_input = request.messages[-1].content.lower()
    
    # 1. Definiera system-prompten
    system_context = (
        "Du är DAA (Digital Advanced Assistant). Du är smart, hjälpsam och koncis. "
        "Svara alltid på svenska."
    )

    # 2. Kolla om vi behöver Garmin-data
    trigger_words = ["träning", "hälsa", "sömn", "puls", "springa", "mår jag", "garmin", "tips", "trött", "pigg", "status"]
    should_fetch_health = any(word in user_input for word in trigger_words)

    if should_fetch_health:
        print(">> Trigger upptäckt: Försöker hämta hälsodata...")
        
        # Caching: Hämta max var 15:e minut
        now = time.time()
        if (now - last_garmin_fetch > 900) or (cached_garmin_data is None):
            data = garmin_tool.get_health_report()
            if data:
                cached_garmin_data = data
                last_garmin_fetch = now
                print(">> Garmin-data hämtad.")
            else:
                print(">> Kunde inte hämta Garmin-data.")
        
        # Lägg till datan i system-prompten
        if cached_garmin_data:
            stats = cached_garmin_data
            health_prompt = (
                f"\n\n[HÄLSODATA FRÅN GARMIN - {stats['datum']}]:\n"
                f"- Sömn: {stats['sömn_timmar']} timmar.\n"
                f"- Vilopuls: {stats['vilopuls']} bpm.\n"
                f"- Stressnivå (snitt): {stats['stress_snitt']}.\n"
                f"- Steg idag: {stats['steg']}.\n"
                f"- Senaste aktivitet: {stats['senaste_träning']}.\n"
                f"Analysera datan. Ge korta, konkreta råd baserat på dagsformen."
            )
            system_context += health_prompt

    # 3. Bygg meddelandelistan till Gemini
    gemini_messages = [{"role": "user", "parts": [system_context]}]
    
    for m in request.messages:
        role = "user" if m.role == "user" else "model"
        gemini_messages.append({"role": role, "parts": [m.content]})

    # 4. Anropa Gemini
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(gemini_messages)
        return response.text

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Jag har lite problem med anslutningen till hjärnan just nu."