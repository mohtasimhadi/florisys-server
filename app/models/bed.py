# app/models/bed.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# GeoJSON-like Polygon: coordinates[ring][vertex][lon/lat]
class BedBase(BaseModel):
    name: str
    coordinates: List[List[List[float]]]

class BedInDB(BedBase):
    id: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class BedOut(BedInDB):
    pass
