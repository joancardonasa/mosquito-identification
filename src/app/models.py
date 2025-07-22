from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    photo_path = Column(String, nullable=False)

    identification_task = relationship("IdentificationTask", back_populates="observation", uselist=False)

class IdentificationTask(Base):
    __tablename__ = "identification_tasks"

    id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(Integer, ForeignKey("observations.id"), unique=True)
    ai_classification = Column(Text, nullable=True)
    expert_classification = Column(Text, nullable=True)
    annotations = Column(Text, nullable=True)

    observation = relationship("Observation", back_populates="identification_task")
