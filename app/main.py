from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import players, performances
from app.core.config import settings

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sports Analytics System API"}
