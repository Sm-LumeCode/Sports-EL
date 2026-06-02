from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.schemas.performance import PerformanceCreate, PerformanceResponse
from app.services import performance_service
from app.deps import get_current_active_user
from app.models.player import Player

router = APIRouter()

@router.post("/", response_model=PerformanceResponse, status_code=status.HTTP_201_CREATED)
def create_performance(performance: PerformanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    player = db.query(Player).filter(Player.id == performance.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return performance_service.create_performance(db, performance)

@router.get("/", response_model=List[PerformanceResponse])
def get_performances(skip: int = 0, limit: int = 100, player_id: int = None, db: Session = Depends(get_db)):
    return performance_service.get_performances(db, skip, limit, player_id)
