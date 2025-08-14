# app/services/beds.py
from uuid import uuid4
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from app.db.mongo import get_db
from app.models.bed import BedInDB

def _close_ring(coords: list[list[float]]) -> list[list[float]]:
    if not coords: return coords
    if coords[0] != coords[-1]:
        return coords + [coords[0]]
    return coords

def _validate_polygon(poly: list[list[list[float]]]) -> list[list[list[float]]]:
    if not poly or not poly[0] or len(poly[0]) < 4:
        raise HTTPException(status_code=422, detail="Polygon requires at least 4 points")
    poly[0] = _close_ring(poly[0])
    return poly

async def list_beds(plot_id: str) -> List[dict]:
    db = get_db()
    p = await db.plots.find_one({"id": plot_id}, {"_id": 0, "beds": 1})
    return p.get("beds", []) if p else []

async def create_bed(plot_id: str, name: str, coordinates: list[list[list[float]]]) -> dict:
    db = get_db()
    poly = _validate_polygon(coordinates)
    bed = BedInDB(id=uuid4().hex, name=name, coordinates=poly).model_dump()
    res = await db.plots.update_one({"id": plot_id}, {"$push": {"beds": bed}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plot not found")
    return bed

async def update_bed(plot_id: str, bed_id: str, name: Optional[str], coordinates: Optional[list[list[list[float]]]]) -> dict:
    db = get_db()
    if coordinates is not None:
        coordinates = _validate_polygon(coordinates)
    update = {"beds.$.updatedAt": datetime.utcnow()}
    if name is not None: update["beds.$.name"] = name
    if coordinates is not None: update["beds.$.coordinates"] = coordinates

    res = await db.plots.update_one({"id": plot_id, "beds.id": bed_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Bed not found")
    p = await db.plots.find_one({"id": plot_id}, {"_id": 0, "beds": 1})
    bed = next((b for b in p.get("beds", []) if b["id"] == bed_id), None)
    return bed

async def delete_bed(plot_id: str, bed_id: str) -> None:
    db = get_db()
    res = await db.plots.update_one({"id": plot_id}, {"$pull": {"beds": {"id": bed_id}}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plot not found")
