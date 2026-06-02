from pydantic import BaseModel
from typing import List, Optional


class PlayerMetrics(BaseModel):
    """Computed metrics for a single player."""
    player_id: int
    name: str
    sport: str
    position: str
    goals_per_90: float
    assists_per_90: float
    avg_efficiency: float
    total_goal_contributions: int
    minutes_per_match: float
    avg_accuracy: float
    avg_win_contribution: float


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard."""
    rank: int
    player_id: int
    name: str
    sport: str
    position: str
    value: float


class LeaderboardResponse(BaseModel):
    """Response for the leaderboard endpoint."""
    metric: str
    sport: Optional[str] = None
    entries: List[LeaderboardEntry]
