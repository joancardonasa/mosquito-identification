import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from app.utils import store_photo, PhotoSaveError

from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models import Observation

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
        photo_path=file_path,
        annotations=None,
        ai_classification=None,
        expert_classification=None
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)

    total = db.query(Observation).count()
    print(f"Total observations in DB: {total}")

    return {
        "message": "Observation saved",
        "photo_location": file_path
    }

