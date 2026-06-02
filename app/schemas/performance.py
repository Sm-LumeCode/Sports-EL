from pydantic import BaseModel, ConfigDict
from typing import Optional

class PerformanceBase(BaseModel):
    matches_played: int = 0
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    accuracy: float = 0.0
    efficiency: float = 0.0
    win_contribution: float = 0.0

    # Fitness
    fitness_score: float = 0.0
    stamina: float = 0.0
    speed: float = 0.0
    training_attendance: float = 0.0

    # Fatigue
    fatigue_index: float = 0.0
    recovery_score: float = 0.0
    workload_score: float = 0.0

    # Injury
    current_injury_status: float = 0.0
    injury_history: float = 0.0
    days_since_last_injury: float = 0.0

    # Performance history
    last_3_score: float = 0.0
    last_5_score: float = 0.0
    consistency: float = 0.0

    # Team requirement
    role_match: float = 0.0
    team_balance_need: float = 0.0
    versatility: float = 0.0

class PerformanceCreate(PerformanceBase):
    player_id: int

class PerformanceUpdate(BaseModel):
    matches_played: Optional[int] = None
    minutes_played: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    accuracy: Optional[float] = None
    efficiency: Optional[float] = None
    win_contribution: Optional[float] = None
    fitness_score: Optional[float] = None
    stamina: Optional[float] = None
    speed: Optional[float] = None
    training_attendance: Optional[float] = None
    fatigue_index: Optional[float] = None
    recovery_score: Optional[float] = None
    workload_score: Optional[float] = None
    current_injury_status: Optional[float] = None
    injury_history: Optional[float] = None
    days_since_last_injury: Optional[float] = None
    last_3_score: Optional[float] = None
    last_5_score: Optional[float] = None
    consistency: Optional[float] = None
    role_match: Optional[float] = None
    team_balance_need: Optional[float] = None
    versatility: Optional[float] = None

class PerformanceResponse(PerformanceBase):
    id: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)
