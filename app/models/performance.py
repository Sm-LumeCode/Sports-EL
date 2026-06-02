from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    
    matches_played = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    efficiency = Column(Float, default=0.0)
    win_contribution = Column(Float, default=0.0)

    # Advanced Metrics (Fitness, Fatigue, Injury, etc.)
    fitness_score = Column(Float, default=0.0)
    stamina = Column(Float, default=0.0)
    speed = Column(Float, default=0.0)
    training_attendance = Column(Float, default=0.0)

    fatigue_index = Column(Float, default=0.0)
    recovery_score = Column(Float, default=0.0)
    workload_score = Column(Float, default=0.0)

    current_injury_status = Column(Float, default=0.0)
    injury_history = Column(Float, default=0.0)
    days_since_last_injury = Column(Float, default=0.0)

    last_3_score = Column(Float, default=0.0)
    last_5_score = Column(Float, default=0.0)
    consistency = Column(Float, default=0.0)

    role_match = Column(Float, default=0.0)
    team_balance_need = Column(Float, default=0.0)
    versatility = Column(Float, default=0.0)

    player = relationship("Player", back_populates="performances")
