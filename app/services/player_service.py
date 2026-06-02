from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerUpdate


def create_player(db: Session, player_data: PlayerCreate) -> Player:
    """Create a new player record."""
    db_player = Player(**player_data.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def get_players(db: Session, skip: int = 0, limit: int = 100) -> List[Player]:
    """Retrieve a paginated list of players."""
    return db.query(Player).offset(skip).limit(limit).all()


def get_player(db: Session, player_id: int) -> Optional[Player]:
    """Retrieve a single player by ID, or None if not found."""
    return db.query(Player).filter(Player.id == player_id).first()


def update_player(db: Session, player_id: int, player_update: PlayerUpdate) -> Optional[Player]:
    """Update an existing player. Returns None if player not found."""
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        return None

    update_data = player_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_player, key, value)

    db.commit()
    db.refresh(db_player)
    return db_player


def delete_player(db: Session, player_id: int) -> bool:
    """Delete a player. Returns True if deleted, False if not found."""
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        return False

    db.delete(db_player)
    db.commit()
    return True
