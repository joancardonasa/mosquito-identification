import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

API_NAME = "Mosquito Observation API"
logger = logging.getLogger(__name__)

app = FastAPI(title=API_NAME, version="1.0.0")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": f"{API_NAME} is running"}
