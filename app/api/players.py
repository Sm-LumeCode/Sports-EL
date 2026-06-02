from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.schemas.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.services import player_service
from app.deps import get_current_active_user

router = APIRouter()

@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(player: PlayerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return player_service.create_player(db, player)

@router.get("/", response_model=List[PlayerResponse])
def get_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return player_service.get_players(db, skip, limit)

@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = player_service.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, player_update: PlayerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    player = player_service.update_player(db, player_id, player_update)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.delete("/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    success = player_service.delete_player(db, player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully"}
