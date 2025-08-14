# app/services/spatial_maps.py
from uuid import uuid4
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from app.db.mongo import get_db
from app.core.config import settings

_ALLOWED_PLY = {".ply"}

async def _enforce_size(file: UploadFile, max_bytes: int) -> None:
    # mirror plots._enforce_size behavior
    pos = 0
    chunk = await file.read(1024 * 1024)
    while chunk:
        pos += len(chunk)
        if pos > max_bytes:
            await file.close()
            raise HTTPException(status_code=413, detail="File too large")
        chunk = await file.read(1024 * 1024)
    await file.seek(0)

def _ensure_ply(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_PLY:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only .ply allowed")
    return ext

async def add_spatial_map(plot_id: str, bed_id: str, file: UploadFile, date_iso: Optional[str]) -> dict:
    db = get_db()
    # ensure plot/bed exist
    found = await db.plots.find_one({"id": plot_id, "beds.id": bed_id}, {"_id": 0, "beds.$": 1})
    if not found or not found.get("beds"):
        raise HTTPException(status_code=404, detail="Plot/bed not found")

    _ensure_ply(file.filename or "file.ply")

    # enforce size like TIF uploads
    max_bytes = settings.max_upload_mb * 1024 * 1024
    await _enforce_size(file, max_bytes)

    file_id = uuid4().hex
    filename = f"{file_id}.ply"
    dst = Path(settings.files_dir) / filename
    dst.parent.mkdir(parents=True, exist_ok=True)

    # write to disk
    with dst.open("wb") as out:
        # copyfileobj on underlying file is okay here
        import shutil
        shutil.copyfileobj(file.file, out)

    when: Optional[datetime] = None
    if date_iso:
        try:
            when = datetime.fromisoformat(date_iso)
        except Exception:
            when = None
    if when is None:
        when = datetime.utcnow()

    item = {
        "id": file_id,
        "filename": filename,                 # stored name
        "fileName": file.filename or filename, # original display name
        "bytes": dst.stat().st_size,
        "contentType": file.content_type or "application/octet-stream",
        "date": when,
        "createdAt": datetime.utcnow(),
    }

    # push as newest first
    res = await db.plots.update_one(
        {"id": plot_id, "beds.id": bed_id},
        {"$push": {"beds.$.spatialMaps": {"$each": [item], "$position": 0}}}
    )
    if res.matched_count == 0:
        # Cleanup file if DB op failed weirdly
        try:
            dst.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=404, detail="Plot/bed not found")

    return item

async def list_spatial_maps(plot_id: str, bed_id: str) -> List[dict]:
    db = get_db()
    d = await db.plots.find_one({"id": plot_id, "beds.id": bed_id}, {"_id": 0, "beds.$": 1})
    if not d or not d.get("beds"):
        raise HTTPException(status_code=404, detail="Plot/bed not found")
    maps = d["beds"][0].get("spatialMaps", [])
    # Already stored newest first, but ensure:
    maps.sort(key=lambda x: x.get("date") or x.get("createdAt"), reverse=True)
    return maps

async def delete_spatial_map(plot_id: str, bed_id: str, map_id: str) -> None:
    from app.utils.files import delete_file
    db = get_db()
    # find the filename first
    d = await db.plots.find_one({"id": plot_id, "beds.id": bed_id}, {"_id": 0, "beds.$": 1})
    if not d or not d.get("beds"):
        raise HTTPException(status_code=404, detail="Plot/bed not found")
    target = next((m for m in d["beds"][0].get("spatialMaps", []) if m.get("id") == map_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Spatial map not found")

    res = await db.plots.update_one(
        {"id": plot_id, "beds.id": bed_id},
        {"$pull": {"beds.$.spatialMaps": {"id": map_id}}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plot/bed not found")

    # best-effort file delete
    delete_file(settings.files_dir, target["filename"])
