import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_config
from app.core.database import init_db
from app.interface.api import router as api_router

cfg = get_config()
app = FastAPI(title=cfg["APP_NAME"], version=cfg["VERSION"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router)

if __name__ == "__main__":
    print(f"--- Starting {cfg['APP_NAME']} on port {cfg['PORT']} ---")
    uvicorn.run(app, host=cfg["HOST"], port=cfg["PORT"])