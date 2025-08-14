# app/models/spatial_map.py
from pydantic import BaseModel, Field
from datetime import datetime

class SpatialMapInDB(BaseModel):
    id: str
    filename: str            # stored in settings.files_dir (e.g. "<uuid>.ply")
    fileName: str            # original file name for display
    bytes: int
    contentType: str
    date: datetime           # measurement/upload date (ISO)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class SpatialMapOut(BaseModel):
    id: str
    fileName: str
    url: str
    bytes: int
    contentType: str
    date: datetime
    createdAt: datetime
