"""
Created on 2025.03.02

@Title: OroraTech Wildfire Tech Challenge - Test API
@author: jseelig

This script contains tests fcts for api
"""

import pytest
from fastapi.testclient import TestClient
from api.api import app
import fcts.mock_db as mock_db
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def setup_mock_db():
    """Set up a mock database before each test."""
    mock_db.data = {
        1: {
            "id": 1,
            "latitude": 52.52,
            "longitude": 13.405,
            "timestamp_start": "2025-02-27T12:00:00",
            "timestamp_end": "2025-02-27T14:00:00",
            "geom": {"type": "Point", "coordinates": [13.405, 52.52]},
        }
    }
    yield
    mock_db.data.clear()


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "In Root"}


def test_get_hotspots_no_params():
    """Test /hotspots without parameters should return 400."""
    response = client.get("/hotspots")
    assert response.status_code == 400


def test_get_hotspots_with_bounding_box(setup_mock_db):
    """Test /hotspots with bounding box parameters."""
    response = client.get(
        "/hotspots",
        params={"min_lat": 52.0, "max_lat": 53.0, "min_lon": 13.0, "max_lon": 14.0},
    )
    assert response.status_code == 200
    assert "features" in response.json()


def test_get_hotspot_by_id_valid(setup_mock_db):
    """Test /hotspots/{id} with a valid ID."""
    response = client.get("/hotspots/1")
    assert response.status_code == 200
    assert response.json()["geometry"]["type"] == "Point"


def test_get_hotspot_by_id_invalid():
    """Test /hotspots/{id} with an invalid ID."""
    response = client.get("/hotspots/999")
    assert response.status_code == 404


def test_add_new_hotspot():
    """Test adding a new hotspot."""
    response = client.post(
        "/hotspots/add",
        params={
            "latitude": 50.0,
            "longitude": 10.0,
            "timestamp_start": datetime(2023, 11, 16, 19, 13, 14, 364950).isoformat(),
            "timestamp_end": datetime(2023, 11, 20, 19, 13, 14, 364950).isoformat()
        },
    )
    assert response.status_code == 200
    assert "Hotspot with ID" in response.json()["message"]


def test_delete_hotspot(setup_mock_db):
    """Test deleting a hotspot."""
    response = client.delete("/hotspots/remove", params={"id": 1})
    assert response.status_code == 200
    assert "Hotspot with ID 1 deleted successfully" in response.json()["message"]
