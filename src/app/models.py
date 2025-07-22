from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    photo_path = Column(String, nullable=False)

    ai_classification = Column(Text, nullable=True)
    expert_classification = Column(Text, nullable=True)
    annotations = Column(Text, nullable=True)
