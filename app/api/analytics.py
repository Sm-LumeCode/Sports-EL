from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.analytics import PlayerMetrics, LeaderboardResponse, LeaderboardEntry
from app.services.analytics_service import get_player_metrics, get_leaderboard, VALID_METRICS

router = APIRouter()


@router.get("/players/{player_id}/metrics", response_model=PlayerMetrics, tags=["players"])
def player_metrics(player_id: int, db: Session = Depends(get_db)):
    """Get computed performance metrics for a specific player."""
    metrics = get_player_metrics(db, player_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return metrics


@router.get("/analytics/leaderboard", response_model=LeaderboardResponse, tags=["analytics"])
def leaderboard(
    metric: str = Query(..., description=f"Metric to rank by. Valid: goals, assists, efficiency, win_contribution, accuracy, minutes_played, goals_per_90, assists_per_90"),
    sport: Optional[str] = Query(None, description="Filter by sport"),
    top_n: int = Query(10, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Get the leaderboard ranked by a specific metric."""
    try:
        entries = get_leaderboard(db, metric=metric, sport=sport, top_n=top_n)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return LeaderboardResponse(
        metric=metric,
        sport=sport,
        entries=[LeaderboardEntry(**entry) for entry in entries],
    )
