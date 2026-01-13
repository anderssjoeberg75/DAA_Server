from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx

from app.core.database import save_message, get_history
from app.services.llm_handler import stream_gemini, stream_ollama
from config.settings import get_config

router = APIRouter()
cfg = get_config()

# --- Request Model ---
class ChatRequest(BaseModel):
    model: str
    messages: List[dict] # Expected: [{"role": "user", "content": "...", "image": "..."}]
    session_id: str = "default"

# --- Endpoints ---

@router.get("/api/models")
async def get_models():
    """Returns available models from Ollama and Gemini."""
    models = []
    
    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{cfg['OLLAMA_URL']}/api/tags", timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get('models', []):
                    models.append({"id": m['name'], "name": f"🏠 Ollama: {m['name']}"})
    except:
        pass 

    # Check Gemini
    if cfg["GOOGLE_API_KEY"]:
        models.append({"id": "gemini-1.5-flash", "name": "☁️ Gemini 1.5 Flash"})
        models.append({"id": "gemini-1.5-pro", "name": "☁️ Gemini 1.5 Pro"})
        
    return JSONResponse(content=models)

@router.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Main chat endpoint handling history, vision, and streaming."""
    
    # Extract latest user input
    last_msg_obj = req.messages[-1]
    user_text = last_msg_obj.get("content", "")
    user_image = last_msg_obj.get("image", None) # Base64 string
    
    # Save to DB
    save_message(req.session_id, "user", user_text, user_image)
    
    # Load Context
    history = get_history(req.session_id)
    
    # Select Generator
    if "gemini" in req.model.lower():
        generator = stream_gemini(req.model, history, user_text, user_image)
    else:
        generator = stream_ollama(req.model, history, user_text)

    # Stream Response Wrapper (Saves AI response at the end)
    async def response_wrapper():
        full_response = ""
        async for chunk in generator:
            full_response += chunk
            yield chunk
        
        if full_response:
            save_message(req.session_id, "assistant", full_response)

    return StreamingResponse(response_wrapper(), media_type="text/plain")
