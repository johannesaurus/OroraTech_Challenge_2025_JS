"""
Created on 2025.03.02

@Title: OroraTech Wildfire Tech Challenge - models
@author: jseelig

This script contains models for typed entry
"""

from pydantic import BaseModel
from datetime import datetime


class HotspotEntry(BaseModel):
    """Single Hotspot Class"""

    id: int
    latitude: float
    longitude: float
    timestamp_start: datetime
    timestamp_end: datetime
    # geom: Union[Point, dict]

    class Config:
        arbitrary_types_allowed = True
