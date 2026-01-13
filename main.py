import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_config
from app.core.database import init_db
from app.interface.api import router as api_router

cfg = get_config()

app = FastAPI(title=cfg["APP_NAME"], version="2.1")

# Allow all CORS (Useful for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Lifecycle event: Run on server start."""
    init_db()

# Include API Routes
app.include_router(api_router)

# Mount Static Files (Web Interface)
# Ensure your 'public' folder is in the root directory
app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    print(f"--- Starting {cfg['APP_NAME']} ---")
    print(f"--- Listening on http://{cfg['HOST']}:{cfg['PORT']} ---")
    uvicorn.run(app, host=cfg["HOST"], port=cfg["PORT"])
