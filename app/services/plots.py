from datetime import datetime
from fastapi import UploadFile
from fastapi import HTTPException, status
from app.core.config import settings
from app.db.mongo import get_db
from app.utils.files import save_upload, delete_file
from app.models.plot import PlotInDB
from typing import List, Optional
from starlette.requests import Request

def file_url(request: Request, filename: str) -> str:
    if settings.backend_public_url:
        base = str(settings.backend_public_url).rstrip("/")
        return f"{base}/files/{filename}"
    base = str(request.base_url).rstrip("/")
    return f"{base}/files/{filename}"

async def list_plots(request) -> List[dict]:
    db = get_db()
    items = []
    cursor = db.plots.find({}, {"_id": 0})
    async for doc in cursor:
        items.append({
            "id": doc["id"],
            "name": doc["name"],
            "url": file_url(request, doc["filename"]),
            "createdAt": doc.get("createdAt")
        })
    return items

async def create_plot(file: UploadFile, request) -> dict:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    await _enforce_size(file, max_bytes)
    try:
        plot_id, filename, name = save_upload(settings.files_dir, file)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only .tif/.tiff allowed")
    db = get_db()
    doc = PlotInDB(id=plot_id, name=name, filename=filename, createdAt=datetime.utcnow()).model_dump()
    await db.plots.insert_one(doc)
    return {"id": doc["id"], "name": doc["name"], "url": file_url(request, doc["filename"]), "createdAt": doc["createdAt"]}

async def delete_plot(plot_id: str) -> None:
    db = get_db()
    found = await db.plots.find_one({"id": plot_id})
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await db.plots.delete_one({"id": plot_id})
    delete_file(settings.files_dir, found["filename"])

async def init_indexes() -> None:
    db = get_db()
    await db.plots.create_index("id", unique=True)
    await db.plots.create_index([("createdAt", -1)])

async def _enforce_size(file: UploadFile, max_bytes: int) -> None:
    pos = 0
    chunk = await file.read(1024 * 1024)
    while chunk:
        pos += len(chunk)
        if pos > max_bytes:
            await file.close()
            raise HTTPException(status_code=413, detail="File too large")
        chunk = await file.read(1024 * 1024)
    await file.seek(0)
