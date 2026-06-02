from pydantic import BaseModel, ConfigDict, field_validator
from typing import Dict, List, Optional


class SelectionRequest(BaseModel):
    """Request body for team selection."""
    sport: str
    team_size: int
    position_limits: Dict[str, int]
    weights: Optional[Dict[str, float]] = None
    use_ml: bool = False

    @field_validator("team_size")
    @classmethod
    def team_size_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("team_size must be at least 1")
        return v

    @field_validator("position_limits")
    @classmethod
    def position_limits_positive(cls, v: Dict[str, int]) -> Dict[str, int]:
        for pos, count in v.items():
            if count < 0:
                raise ValueError(f"Position limit for '{pos}' cannot be negative")
        return v


class SelectedPlayer(BaseModel):
    """A player selected for the team."""
    player_id: int
    name: str
    position: str
    team: str
    score: float
    goals: int
    assists: int
    efficiency: float


class SelectionResponse(BaseModel):
    """Response for team selection."""
    sport: str
    team_size: int
    players_selected: int
    scoring_method: str
    weights_used: Dict[str, float]
    team: List[SelectedPlayer]
