from fastapi import APIRouter
from pydantic import BaseModel
import google.generativeai as genai
import requests
import json
import time
from typing import List, Optional

# --- HÄR KOPPLAR VI IHOP MED DIN SETTINGS.PY ---
try:
    from config.settings import (
        GOOGLE_API_KEY, 
        OPENAI_API_KEY, 
        OLLAMA_URL, 
        GARMIN_EMAIL, 
        GARMIN_PASSWORD
    )
except ImportError:
    print(">> VARNING: Kunde inte importera från config.settings")
    GOOGLE_API_KEY = None
    OPENAI_API_KEY = None
    OLLAMA_URL = "http://127.0.0.1:11434"
    GARMIN_EMAIL = None
    GARMIN_PASSWORD = None

from app.tools.garmin_core import GarminCoach

router = APIRouter()

# --- KONFIGURATION AV AI-TJÄNSTER ---
has_google = False
if GOOGLE_API_KEY and len(str(GOOGLE_API_KEY)) > 10:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        has_google = True
        print(">> Google API konfigurerat.")
    except Exception as e:
        print(f">> Google API Error: {e}")
else:
    print(">> VARNING: Ingen giltig Google API-nyckel hittades.")

# --- INITIERA VERKTYG (GARMIN) ---
garmin_tool = None
if GARMIN_EMAIL and GARMIN_PASSWORD:
    try:
        garmin_tool = GarminCoach()
        print(">> Garmin-verktyg initierat.")
    except Exception as e:
        print(f">> Kunde inte starta Garmin: {e}")

last_garmin_fetch = 0
cached_garmin_data = None

# --- DATAMODELLER ---
class Message(BaseModel):
    role: str
    content: str
    image: Optional[str] = None

class ChatRequest(BaseModel):
    model: str = "gemini-1.5-flash"
    messages: List[Message]
    session_id: Optional[str] = None

# --- HÄMTA MODELLER ---
@router.get("/api/models")
async def get_models():
    models = []
    
    # 1. Google Gemini
    if has_google:
        print(">> Hämtar Google-modeller från API...")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    clean_id = m.name.replace("models/", "")
                    d_name = getattr(m, "display_name", getattr(m, "displayName", clean_id))
                    models.append({
                        "id": clean_id, 
                        "name": f"Google: {d_name} ({clean_id})"
                    })
        except Exception as e:
            print(f">> Fel vid listning av Google-modeller: {e}")
            models.append({"id": "gemini-1.5-flash", "name": "Google: Gemini 1.5 Flash (Fallback)"})
    
    # 2. OpenAI
    if OPENAI_API_KEY:
        print(">> Hämtar OpenAI-modeller från API...")
        try:
            h = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            r = requests.get("https://api.openai.com/v1/models", headers=h, timeout=5)
            if r.status_code == 200:
                data = r.json().get('data', [])
                data.sort(key=lambda x: x.get('created', 0), reverse=True)
                for m in data:
                    mid = m['id']
                    if "gpt" in mid or "o1" in mid:
                        models.append({"id": mid, "name": f"OpenAI: {mid}"})
        except Exception as e:
            print(f">> OpenAI Error: {e}")

    # 3. Ollama
    print(">> Hämtar Ollama-modeller...")
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            for m in r.json().get('models', []):
                models.append({"id": m['name'], "name": f"Ollama: {m['name']}"})
    except Exception as e:
        print(f">> Kunde inte nå Ollama: {e}")

    if not models:
        models.append({"id": "error", "name": "Inga modeller hittades (Kolla loggen)"})

    return {"object": "list", "data": models}

# --- CHATT-LOGIK ---
@router.post("/chat")
@router.post("/api/chat")
async def chat(request: ChatRequest):
    global last_garmin_fetch, cached_garmin_data
    
    user_msg = request.messages[-1].content
    model_id = request.model.lower()
    
    system_prompt = "Du är DAA, en smart assistent. Svara på svenska."

    # --- GARMIN-DATA ---
    triggers = ["puls", "sömn", "träning", "stress", "garmin", "mår jag", "status"]
    if garmin_tool and any(t in user_msg.lower() for t in triggers):
        now = time.time()
        if (now - last_garmin_fetch > 900) or not cached_garmin_data:
            print(">> Hämtar Garmin-data...")
            try:
                report = garmin_tool.get_health_report()
                if report:
                    cached_garmin_data = report
                    last_garmin_fetch = now
            except Exception as e:
                print(f">> Garmin Fetch Error: {e}")
        
        if cached_garmin_data:
            d = cached_garmin_data
            
            data_block = (
                f"Sömn: {d.get('sömn_timmar')}h\n"
                f"Vilopuls: {d.get('vilopuls')} bpm\n"
                f"Stress: {d.get('stress_snitt')}/100\n"
                f"Steg: {d.get('steg')}"
            )

            # NY PROMPT: Långt svar, ren text, tydliga radbrytningar
            system_prompt += (
                f"\n\n[HÄLSODATA FRÅN GARMIN]\n"
                f"{data_block}\n\n"
                "INSTRUKTION FÖR RAPPORTEN:\n"
                "Du ska agera som en professionell hälsocoach. Ge en utförlig, djupgående och omtänksam analys.\n"
                "VIKTIGT OM FORMATERING:\n"
                "1. Använd INTE Markdown-rubriker (###) eller fetstil (**text**). Skriv bara ren text.\n"
                "2. Använd punktlistor (*) för mätvärdena så att de hamnar på nya rader.\n"
                "3. Använd dubbla radbrytningar mellan stycken för att skapa luft i texten.\n\n"
                "Följ denna struktur:\n"
                "DAGENS STATUS\n"
                "* (Lista värdena med emojis, en per rad)\n\n"
                "ANALYS\n"
                "(Skriv en lång och detaljerad analys i flera stycken om hur värdena hänger ihop. Förklara varför sömnen är viktig om den är låg.)\n\n"
                "RÅD\n"
                "1. (Konkret råd 1)\n"
                "2. (Konkret råd 2)\n"
                "3. (Konkret råd 3)"
            )

    # --- ROUTING ---
    if "gemini" in model_id:
        try:
            msgs = [{"role": "user", "parts": [system_prompt]}]
            for m in request.messages:
                role = "user" if m.role == "user" else "model"
                msgs.append({"role": role, "parts": [m.content]})
            gmodel = genai.GenerativeModel(model_id)
            return gmodel.generate_content(msgs).text
        except Exception as e:
            return f"Gemini Error: {e}"

    elif "gpt" in model_id or "o1" in model_id:
        try:
            payload = {
                "model": model_id,
                "messages": [{"role": "system", "content": system_prompt}] + 
                            [{"role": m.role, "content": m.content} for m in request.messages]
            }
            h = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=h)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            else:
                return f"OpenAI Error {r.status_code}: {r.text}"
        except Exception as e:
            return f"OpenAI Connection Error: {e}"

    else:
        try:
            payload = {
                "model": model_id,
                "messages": [{"role": "system", "content": system_prompt}] + 
                            [{"role": m.role, "content": m.content} for m in request.messages],
                "stream": False
            }
            r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
            if r.status_code == 200:
                return r.json().get("message", {}).get("content", "")
            else:
                return f"Ollama Error: {r.text}"
        except Exception as e:
            return f"Ollama Connection Failed: {e}"