import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.interface.api import router as api_router
from app.interface.web_ui import router as ui_router
from app.core.database import init_db  # <--- Importera denna

app = FastAPI(title="DAA HTTP Server")

# Kör databas-initiering vid start
@app.on_event("startup")
async def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ui_router)
app.include_router(api_router)

if __name__ == "__main__":
    print("--- STARTAR DAA (HTTP) PÅ PORT 3500 ---")
    uvicorn.run(app, host="0.0.0.0", port=3500)