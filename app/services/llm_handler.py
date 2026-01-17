import google.generativeai as genai
import httpx
import json
import asyncio
from config.settings import get_config
# [VIKTIGT 1] Importera control_light här:
from app.tools import get_calendar_events, get_sensor_data, control_vacuum, get_ha_state, control_light
from app.core.prompts import SYSTEM_PROMPT 

cfg = get_config()

if cfg["GOOGLE_API_KEY"]:
    genai.configure(api_key=cfg["GOOGLE_API_KEY"])

# [VIKTIGT 2] Lägg till control_light i listan här!
# Det är denna rad som ger AI:n "tillåtelse" att styra lampor.
daa_tools = [get_calendar_events, get_sensor_data, control_vacuum, get_ha_state, control_light]

async def stream_gemini(model_id, history, new_message, image_data=None):
    try:
        model = genai.GenerativeModel(
            model_id, 
            tools=daa_tools, 
            system_instruction=SYSTEM_PROMPT
        )
        
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        # enable_automatic_function_calling=True gör att den kör control_light själv
        chat = model.start_chat(history=chat_history, enable_automatic_function_calling=True)
        
        parts = [new_message]
        if image_data:
            parts.append({"mime_type": "image/jpeg", "data": image_data})

        response = await chat.send_message_async(parts)
        
        if response.text:
            yield response.text

    except Exception as e:
        if "finish_reason" in str(e):
             yield "Säkerhetsfilter stoppade svaret."
        else:
             yield f"⚠️ Gemini Error: {str(e)}"

async def stream_ollama(model_id, history, new_message):
    url = f"{cfg['OLLAMA_URL']}/api/chat"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": new_message}]
    
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", url, json={"model": model_id, "messages": messages}, timeout=60.0) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data: yield data["message"].get("content", "")
                        except: continue
        except Exception as e:
            yield f"⚠️ Ollama Error: {e}"