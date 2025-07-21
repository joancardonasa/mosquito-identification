import shutil
import os
from fastapi import UploadFile
from uuid import uuid4

PHOTO_DIR = "/app/data/photos"

# Later on we might want to store photos in Azure Data Lake/AWS S3..., so we 
# provide an agnostic interface that just tells us where the photo ends up`
# and how it's called
def store_photo(photo: UploadFile) -> str:
    try:
        unique_filename = f"{uuid4()}.jpg"
        file_path = os.path.join(PHOTO_DIR, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        return file_path
    except Exception as e:
        raise PhotoSaveError(f"Failed to store photo: {str(e)}") from e

class PhotoSaveError(Exception):
    pass
