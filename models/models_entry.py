"""
Created on 02.03.2025

@Title: OroraTech Wildfire Tech Challenge - models
@author: jseelig

This script contains models for typed entry
"""

from pydantic import BaseModel
from typing import Union
from shapely.geometry import Point
from datetime import datetime


class HotspotEntry(BaseModel):
    """Single Hotspot Class"""

    id: int
    latitude: float
    longitude: float
    timestamp_start: datetime
    timestamp_end: datetime
    geom: Union[Point, dict]

    class Config:
        arbitrary_types_allowed = True
