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


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of how a player's overall score was computed."""
    fitness_category: float
    fatigue_category: float
    injury_category: float
    performance_category: float
    team_requirement_category: float
    overall_score: float
    selection_reason: str


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
    score_breakdown: Optional[ScoreBreakdown] = None


class SelectionResponse(BaseModel):
    """Response for team selection."""
    sport: str
    team_size: int
    players_selected: int
    scoring_method: str
    weights_used: Dict[str, float]
    team: List[SelectedPlayer]


class SubstitutionRequest(BaseModel):
    """Request to find the best substitute for a player."""
    sport: str
    current_team_ids: List[int]
    player_to_replace_id: int
    allow_versatile: bool = True


class SubstitutionCandidate(BaseModel):
    """A candidate substitute player."""
    player_id: int
    name: str
    position: str
    team: str
    score: float
    score_breakdown: ScoreBreakdown
    improvement_over_replaced: float


class SubstitutionResponse(BaseModel):
    """Response showing the replaced player and recommended substitute."""
    replaced_player_id: int
    replaced_player_name: str
    replaced_player_score: float
    replaced_player_breakdown: ScoreBreakdown
    substitute: SubstitutionCandidate
    reason: str

