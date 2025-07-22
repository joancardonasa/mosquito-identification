import logging
import os
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, null

from app.utils import store_photo, PhotoSaveError
from app.database import SessionLocal, get_db
from app.models import Observation, IdentificationTask
from app.schemas import ObservationResponse
from app.tasks import classify_observation_ai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

API_NAME = "Mosquito Observation API"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

api = FastAPI(title=API_NAME, version="1.0.0")

@api.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": f"{API_NAME} is running"}


@api.post("/observations/")
async def create_observation(
    latitude: float = Form(0.0),
    longitude: float = Form(0.0),
    timestamp: str = Form("2000-01-01T12:00:00"),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Should never happen, as photo is required, but for failsafe
    if not photo:
        raise HTTPException(status_code=422, detail="Photo is required")

    photo_extension = os.path.splitext(photo.filename)[1].lower()
    if photo_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension: {photo_extension}. The provided file must be: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    if not -90 <= latitude <= 90:
        raise HTTPException(400, "Invalid latitude")
    if not -180 <= longitude <= 180:
        raise HTTPException(400, "Invalid longitude")

    try:
        parsed_timestamp = datetime.fromisoformat(timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp")

    try:
        file_path = store_photo(photo)
    except PhotoSaveError:
        raise HTTPException(status_code=500, detail="Internal error while storing photo")

    # Write to DB
    observation = Observation(
        latitude=latitude,
        longitude=longitude,
        timestamp=parsed_timestamp,
        photo_path=file_path
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)

    classify_observation_ai.delay(observation.id)
    # total = db.query(Observation).count()
    # print(f"Total observations in DB: {total}")

    return {
        "message": "Observation saved",
        "photo_location": file_path
    }

@api.get("/observations/", response_model=List[ObservationResponse])
def list_observations(species: Optional[str] = None, db: Session = Depends(get_db)):
    query = (
        db.query(
            Observation.id,
            Observation.latitude,
            Observation.longitude,
            Observation.timestamp,
            Observation.photo_path,
            IdentificationTask.annotations,
            IdentificationTask.ai_classification,
            IdentificationTask.expert_classification,
        )
        .outerjoin(IdentificationTask, IdentificationTask.observation_id == Observation.id)
    )

    ### Explanation:
    # We prioritize expert classifications, but will show AI classifications
    # With more time, this system could be improved to filter
    # by only AI classifications, expert ones, to be able to see
    # how the AI is performing, and other management tasks
    if species:
        query = query.filter(
            or_(
                IdentificationTask.expert_classification == species,
                and_(
                    IdentificationTask.expert_classification == None,
                    IdentificationTask.ai_classification == species
                )
            )
        )

    results = query.all()
    observations = []
    for row in results:
        observations.append(
            ObservationResponse(
                id=row.id,
                latitude=row.latitude,
                longitude=row.longitude,
                timestamp=row.timestamp,
                photo_path=row.photo_path,
                annotations=row.annotations,
                ai_classification=row.ai_classification,
                expert_classification=row.expert_classification,
            )
        )

    return observations

@api.get("/observations/{observation_id}", response_model=ObservationResponse)
def get_observation(observation_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(
            Observation.id,
            Observation.latitude,
            Observation.longitude,
            Observation.timestamp,
            Observation.photo_path,
            IdentificationTask.annotations,
            IdentificationTask.ai_classification,
            IdentificationTask.expert_classification,
        )
        .outerjoin(IdentificationTask, IdentificationTask.observation_id == Observation.id)
        .filter(Observation.id == observation_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Observation not found")

    return ObservationResponse(
        id=result.id,
        latitude=result.latitude,
        longitude=result.longitude,
        timestamp=result.timestamp,
        photo_path=result.photo_path,
        annotations=result.annotations,
        ai_classification=result.ai_classification,
        expert_classification=result.expert_classification,
    )
