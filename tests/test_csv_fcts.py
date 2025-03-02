import pytest
import os
from fcts.csv_fcts import read_csv_files, write_mockdb_to_mastercsv, read_mastercsv_to_dict
from models.models_response import FeatGeometry

@pytest.fixture
def sample_data():
    return {
        1: {
            "id": 1,
            "latitude": 12.34,
            "longitude": 56.78,
            "timestamp_start": "2025-03-02T12:00:00Z",
            "timestamp_end": "2025-03-02T14:00:00Z",
            "geom": FeatGeometry(type="Point", coordinates=[56.78, 12.34]),
        }
    }

def test_write_and_read_mockdb(sample_data, tmp_path):
    mock_csv = tmp_path / "mock_master.csv"
    os.environ["MASTER_CSV"] = str(mock_csv)  # Override settings for testing

    write_mockdb_to_mastercsv(sample_data)
    loaded_data = read_mastercsv_to_dict()

    assert len(loaded_data) == 1
    assert loaded_data[1]["latitude"] == 12.34
    assert loaded_data[1]["longitude"] == 56.78
    assert loaded_data[1]["geom"].coordinates == [56.78, 12.34]
