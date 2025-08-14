# app/routers/beds.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.bed import BedOut
from app.services.beds import list_beds, create_bed, update_bed, delete_bed
from app.services.beds import get_bed_by_id  # ✅ add

router = APIRouter(prefix="/plots/{plot_id}/beds", tags=["beds"])

class BedCreate(BaseModel):
  name: str
  coordinates: list[list[list[float]]]

class BedUpdate(BaseModel):
  name: Optional[str] = None
  coordinates: Optional[list[list[list[float]]]] = None

@router.get("", response_model=List[BedOut])
async def get_beds(plot_id: str):
  return await list_beds(plot_id)

# ✅ NEW: get a single bed
@router.get("/{bed_id}", response_model=BedOut)
async def get_bed(plot_id: str, bed_id: str):
  return await get_bed_by_id(plot_id, bed_id)

@router.post("", response_model=BedOut, status_code=201)
async def post_bed(plot_id: str, body: BedCreate):
  return await create_bed(plot_id, body.name, body.coordinates)

@router.patch("/{bed_id}", response_model=BedOut)
async def patch_bed(plot_id: str, bed_id: str, body: BedUpdate):
  return await update_bed(plot_id, bed_id, body.name, body.coordinates)

@router.delete("/{bed_id}", status_code=204)
async def del_bed(plot_id: str, bed_id: str):
  await delete_bed(plot_id, bed_id)
  return {}
