from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
