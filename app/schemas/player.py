from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.performance import PerformanceResponse

class PlayerBase(BaseModel):
    name: str
    age: int
    sport: str
    position: str
    team: str

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sport: Optional[str] = None
    position: Optional[str] = None
    team: Optional[str] = None

class PlayerResponse(PlayerBase):
    id: int
    performances: List[PerformanceResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
