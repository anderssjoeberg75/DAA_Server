import google.generativeai as genai
import httpx
import json
import asyncio
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from config.settings import get_config

# Importera alla verktyg centralt från app.tools
from app.tools import (
    get_calendar_events, 
    get_sensor_data, 
    control_vacuum, 
    get_ha_state, 
    control_light,
    get_weather
)
from app.core.prompts import get_system_prompt

cfg = get_config()

# --- INITIALISERING ---
if cfg.get("GOOGLE_API_KEY"):
    genai.configure(api_key=cfg["GOOGLE_API_KEY"])

# Samla verktyg för AI-modeller
daa_tools = [
    get_calendar_events, 
    get_sensor_data, 
    control_vacuum, 
    get_ha_state, 
    control_light,
    get_weather
]

# --- 1. GOOGLE GEMINI ---
async def stream_gemini(model_id, history, new_message, image_data=None):
    try:
        model = genai.GenerativeModel(
            model_name=model_id, 
            tools=daa_tools, 
            system_instruction=get_system_prompt()
        )
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=chat_history, enable_automatic_function_calling=True)
        parts = [new_message]
        if image_data:
            parts.append({"mime_type": "image/jpeg", "data": image_data})

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: chat.send_message(parts))
        if response.text:
            yield response.text
    except Exception as e:
        yield f"⚠️ Gemini Error: {str(e)}"

# --- 2. OPENAI KOMPATIBEL (OpenAI, Groq, DeepSeek) ---
async def stream_openai_compatible(api_key, base_url, model_id, history, new_message):
    try:
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        messages = [{"role": "system", "content": get_system_prompt()}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": new_message})

        stream = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"⚠️ Provider Error ({model_id}): {str(e)}"

# --- 3. ANTHROPIC ---
async def stream_anthropic(api_key, model_id, history, new_message):
    try:
        client = AsyncAnthropic(api_key=api_key)
        messages = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": new_message})

        async with client.messages.stream(
            max_tokens=2048,
            system=get_system_prompt(),
            messages=messages,
            model=model_id,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except Exception as e:
        yield f"⚠️ Claude Error: {str(e)}"

# --- 4. OLLAMA ---
async def stream_ollama(model_id, history, new_message):
    url = f"{cfg['OLLAMA_URL']}/api/chat"
    messages = [{"role": "system", "content": get_system_prompt()}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": new_message})
    
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", url, json={"model": model_id, "messages": messages}, timeout=60.0) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data:
                            yield data["message"].get("content", "")
        except Exception as e:
            yield f"⚠️ Ollama Error: {e}"