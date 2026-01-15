import google.generativeai as genai
import httpx
import json
from config.settings import get_config

# Import tools
from app.tools.gcal_core import create_calendar_event
from app.tools.z2m_core import get_sensor_data

cfg = get_config()

# Configure Gemini
if cfg["GOOGLE_API_KEY"]:
    genai.configure(api_key=cfg["GOOGLE_API_KEY"])

# List of tools available to Gemini
# The model will automatically decide when to call these functions.
daa_tools = [create_calendar_event, get_sensor_data]

async def stream_gemini(model_id, history, new_message, image_data=None):
    """
    Streams response from Gemini Cloud with vision support and Function Calling.
    
    Args:
        model_id (str): The name of the Gemini model (e.g., 'gemini-1.5-flash').
        history (list): List of previous messages.
        new_message (str): The user's current input.
        image_data (str, optional): Base64 encoded image data.
    """
    try:
        # Initialize the model with the toolset
        model = genai.GenerativeModel(model_id, tools=daa_tools)
        
        # Format history for Gemini API
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            parts = [msg["content"]]
            chat_history.append({"role": role, "parts": parts})

        # Start chat with automatic function calling enabled
        # This allows Python to execute the requested function and return the result to Gemini
        chat = model.start_chat(
            history=chat_history,
            enable_automatic_function_calling=True
        )
        
        # Prepare current message parts
        current_parts = [new_message]
        if image_data:
            current_parts.append({
                "mime_type": "image/jpeg",
                "data": image_data
            })

        # Send message and stream the response
        response = await chat.send_message_async(current_parts, stream=True)
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"⚠️ Gemini Error: {str(e)}"

async def stream_ollama(model_id, history, new_message):
    """Streams response from local Ollama instance (No tools supported yet)."""
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
