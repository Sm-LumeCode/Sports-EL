from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    sport = Column(String, index=True, nullable=False)
    position = Column(String, index=True, nullable=False)
    team = Column(String, index=True, nullable=False)

    performances = relationship("Performance", back_populates="player")
