from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.performance import Performance
from app.models.player import Player
from app.schemas.performance import PerformanceCreate, PerformanceResponse, PerformanceUpdate

router = APIRouter()

@router.post("/", response_model=PerformanceResponse)
def create_performance(performance: PerformanceCreate, db: Session = Depends(get_db)):
    # Check if player exists
    player = db.query(Player).filter(Player.id == performance.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    db_performance = Performance(**performance.model_dump())
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance

@router.get("/", response_model=List[PerformanceResponse])
def get_performances(skip: int = 0, limit: int = 100, player_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Performance)
    if player_id:
        query = query.filter(Performance.player_id == player_id)
    return query.offset(skip).limit(limit).all()
