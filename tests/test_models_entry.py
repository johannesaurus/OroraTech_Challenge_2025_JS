import pytest
from datetime import datetime
from models.models_entry import HotspotEntry

def test_hotspot_entry():
    hotspot = HotspotEntry(
        id=1,
        latitude=34.5,
        longitude=-117.3,
        timestamp_start=datetime(2025, 3, 3, 12, 34, 56),
        timestamp_end=datetime(2025, 3, 3, 14, 34, 56),
    )
    
    assert hotspot.id == 1
    assert hotspot.latitude == 34.5
    assert hotspot.longitude == -117.3
    assert hotspot.timestamp_start == datetime(2025, 3, 3, 12, 34, 56)
    assert hotspot.timestamp_end == datetime(2025, 3, 3, 14, 34, 56)

def test_hotspot_entry_invalid():
    with pytest.raises(ValueError):
        HotspotEntry(
            id=2,
            latitude="invalid",  # Should raise an error
            longitude=-118.2,
            timestamp_start=datetime(2025, 3, 3, 12, 34, 56),
            timestamp_end=datetime(2025, 3, 3, 14, 34, 56),
        )