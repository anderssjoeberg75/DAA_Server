
import asyncio
import httpx
import sys

# Mock server URL (assuming user will start it or I can start it)
URL = "http://127.0.0.1:3500/api/chat"

async def test_streaming():
    print(f"Connecting to {URL}...")
    payload = {
        "model": "gemini-1.5-flash", # or whatever fallback
        "messages": [{"role": "user", "content": "Hej, funkar streaming?"}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", URL, json=payload, timeout=10) as response:
                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    return
                print("Connected! Receiving stream:")
                async for chunk in response.aiter_text():
                    print(chunk, end="", flush=True)
                print("\nStream finished.")
    except Exception as e:
        print(f"Connection failed (Server might not be running): {e}")

if __name__ == "__main__":
    asyncio.run(test_streaming())
