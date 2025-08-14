from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

class PlotInDB(BaseModel):
    id: str = Field(..., description="Public ID")
    name: str
    filename: str
    createdAt: datetime

class PlotOut(BaseModel):
    id: str
    name: str
    url: HttpUrl
    createdAt: Optional[datetime] = None
