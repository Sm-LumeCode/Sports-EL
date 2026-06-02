from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.performance import Performance
from app.models.player import Player
from app.schemas.performance import PerformanceCreate


def create_performance(db: Session, perf_data: PerformanceCreate) -> Performance:
    """Create a performance record. Raises ValueError if player not found."""
    player = db.query(Player).filter(Player.id == perf_data.player_id).first()
    if not player:
        raise ValueError(f"Player with id {perf_data.player_id} not found")

    db_performance = Performance(**perf_data.model_dump())
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance


def get_performances(
    db: Session, skip: int = 0, limit: int = 100, player_id: Optional[int] = None
) -> List[Performance]:
    """Retrieve performance records, optionally filtered by player_id."""
    query = db.query(Performance)
    if player_id is not None:
        query = query.filter(Performance.player_id == player_id)
    return query.offset(skip).limit(limit).all()
