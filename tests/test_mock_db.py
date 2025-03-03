"""
Created on 2025.03.02

@Title: OroraTech Wildfire Tech Challenge - mockDB
@author: jseelig

This script contains tests fcts for mockDB
"""

from fcts.mock_db import get_hotspot, add_hotspot, delete_hotspot, get_next_hotspot_id
from shapely.geometry import Point
from datetime import datetime


def test_add_and_get_hotspot():
    id_ = get_next_hotspot_id()
    add_hotspot(id_, 10.0, 20.0, "2025-03-02 12:00:00", "2025-03-02 14:00:00")

    hotspot = get_hotspot(id_)
    assert hotspot is not None
    assert hotspot.latitude == 10.0
    assert hotspot.longitude == 20.0
    assert hotspot.timestamp_start == datetime(2025, 3, 2, 12, 0, 0)
    assert hotspot.timestamp_end == datetime(2025, 3, 2, 14, 0, 0)
    assert isinstance(hotspot.geom, Point)


def test_delete_hotspot():
    id_ = get_next_hotspot_id()
    add_hotspot(id_, 30.0, 40.0, "2025-03-02 10:00:00", "2025-03-02 12:00:00")

    assert get_hotspot(id_) is not None
    assert delete_hotspot(id_) is True
    assert get_hotspot(id_) is None
