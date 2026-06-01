from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.api import players, performances
from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the Sports Team Selection and Performance Analytics System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(performances.router, prefix="/performances", tags=["performances"])

# Serve frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
