import google.generativeai as genai
import httpx
import json
from config.settings import get_config

cfg = get_config()

# Configure Gemini
if cfg["GOOGLE_API_KEY"]:
    genai.configure(api_key=cfg["GOOGLE_API_KEY"])

async def stream_gemini(model_id, history, new_message, image_data=None):
    """Streams response from Gemini Cloud with vision support."""
    try:
        model = genai.GenerativeModel(model_id)
        
        # Format history for Gemini
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            parts = [msg["content"]]
            chat_history.append({"role": role, "parts": parts})

        chat = model.start_chat(history=chat_history)
        
        # Prepare current message
        current_parts = [new_message]
        if image_data:
            current_parts.append({
                "mime_type": "image/jpeg",
                "data": image_data
            })

        # Send and stream
        response = await chat.send_message_async(current_parts, stream=True)
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"⚠️ Gemini Error: {str(e)}"

async def stream_ollama(model_id, history, new_message):
    """Streams response from local Ollama instance."""
    url = f"{cfg['OLLAMA_URL']}/api/chat"
    
    # Format history for Ollama
    messages = history + [{"role": "user", "content": new_message}]
    
    payload = {
        "model": model_id,
        "messages": messages,
        "stream": True
    }

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except:
                            continue
        except Exception as e:
            yield f"⚠️ Ollama Error: {str(e)}"
