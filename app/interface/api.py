from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import google.generativeai as genai

from app.core.database import save_message, get_history
from app.services.llm_handler import stream_gemini, stream_ollama
from config.settings import get_config

router = APIRouter()
cfg = get_config()

# Konfigurera Gemini globalt för att kunna lista modeller
if cfg["GOOGLE_API_KEY"]:
    genai.configure(api_key=cfg["GOOGLE_API_KEY"])

# --- Request Model ---
class ChatRequest(BaseModel):
    model: str
    messages: List[dict]
    session_id: str = "default"

# --- Endpoints ---

@router.get("/api/models")
async def get_models():
    """Hämtar tillgängliga modeller dynamiskt."""
    models = []
    
    # 1. Hämta från Ollama
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{cfg['OLLAMA_URL']}/api/tags", timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get('models', []):
                    models.append({
                        "id": m['name'], 
                        "name": f"🏠 Ollama: {m['name']}"
                    })
    except Exception as e:
        print(f"Ollama connection failed: {e}")

    # 2. Hämta från Google Gemini
    if cfg["GOOGLE_API_KEY"]:
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Skapa ett snyggt namn
                    friendly = m.display_name if hasattr(m, "display_name") else m.name
                    models.append({"id": m.name, "name": f"☁️ {friendly}"})
        except Exception as e:
            print(f"Gemini API Error: {e}")
        
    return JSONResponse(content=models)

@router.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Chatt-endpoint med stöd för streaming och historik."""
    
    last_msg = req.messages[-1]
    user_text = last_msg.get("content", "")
    user_image = last_msg.get("image", None)
    
    # Spara användarens meddelande
    save_message(req.session_id, "user", user_text, user_image)
    
    history = get_history(req.session_id)
    
    # Välj generator baserat på modellnamn
    if "gemini" in req.model.lower() or "models/" in req.model.lower():
        generator = stream_gemini(req.model, history, user_text, user_image)
    else:
        generator = stream_ollama(req.model, history, user_text)

    # Strömma svaret och spara det
    async def response_wrapper():
        full_response = ""
        async for chunk in generator:
            full_response += chunk
            yield chunk
        
        if full_response:
            save_message(req.session_id, "assistant", full_response)

    return StreamingResponse(response_wrapper(), media_type="text/plain")