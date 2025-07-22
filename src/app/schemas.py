from pydantic import BaseModel
from datetime import datetime

class ObservationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    timestamp: datetime
    photo_path: str
    annotations: str | None = None
    ai_classification: str | None = None
    expert_classification: str | None = None

    class Config:
        orm_mode = True
