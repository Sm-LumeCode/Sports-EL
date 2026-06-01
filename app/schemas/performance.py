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

class PerformanceResponse(PerformanceBase):
    id: int
    player_id: int
    
    model_config = ConfigDict(from_attributes=True)
