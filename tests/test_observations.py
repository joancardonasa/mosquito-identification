import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from app.main import api
from app.utils import PhotoSaveError
from app.database import get_db

client = TestClient(api)

def create_mock_file(filename="test.jpg"):
    return ("photo", (filename, io.BytesIO(b"fake image"), "image/jpeg"))

class TestObservationsValidation:
    def test_missing_photo_validation(self):
        response = client.post("/observations/", data={"latitude": 45.0, "longitude": 45.0})
        assert response.status_code == 422 # No photo found!!!

    def test_invalid_timestamp(self):
        data = {
            "latitude": 0.0,
            "longitude": 0.0,
            "timestamp": "sdfdsfsdfwe44r23"
        }
        files = [create_mock_file()]
        response = client.post("/observations/", data=data, files=files)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid timestamp"

    def test_invalid_latitude(self):
        data = {
            "latitude": 999.0,
            "longitude": 0.0,
            "timestamp": "2000-01-01T12:00:00"
        }
        files = [create_mock_file()]
        response = client.post("/observations/", data=data, files=files)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid latitude"

    def test_invalid_longitude(self):
        data = {
            "latitude": 0.0,
            "longitude": 999.0,
            "timestamp": "2000-01-01T12:00:00"
        }
        files = [create_mock_file()]
        response = client.post("/observations/", data=data, files=files)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid longitude"

    def test_photo_save_failure_returns_500(self):
        data = {
            "latitude": 40.0,
            "longitude": 2.0,
            "timestamp": "2000-01-01T12:00:00"
        }
        files = [create_mock_file()]
        with patch("app.main.store_photo", side_effect=PhotoSaveError("Simulated failure")):
            response = client.post("/observations/", data=data, files=files)
            assert response.status_code == 500
            assert response.json()["detail"] == "Internal error while storing photo"

    def test_create_observation(self):
        data = {
            "latitude": 40.0,
            "longitude": 2.0,
            "timestamp": "2000-01-01T12:00:00"
        }
        files = [create_mock_file()]

        mock_db = MagicMock()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        api.dependency_overrides[get_db] = lambda: mock_db

        with patch("app.main.store_photo", return_value="photro/path.jpg"):
            response = client.post("/observations/", data=data, files=files)

        assert response.status_code == 200
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        json_resp = response.json()
        assert json_resp["message"] == "Observation saved"

        api.dependency_overrides.clear()
