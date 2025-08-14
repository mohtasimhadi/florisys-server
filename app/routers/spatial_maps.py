# app/routers/spatial_maps.py
from fastapi import APIRouter, UploadFile, File, Form, Request
from typing import List, Optional
from app.services.spatial_maps import add_spatial_map, list_spatial_maps, delete_spatial_map
from app.services.plots import file_url  # reuse your URL builder
from app.models.spatial_map import SpatialMapOut

router = APIRouter(prefix="/plots/{plot_id}/beds/{bed_id}/spatial-maps", tags=["spatial-maps"])

@router.post("", response_model=SpatialMapOut)
async def post_spatial_map(plot_id: str, bed_id: str, request: Request, file: UploadFile = File(...), date: Optional[str] = Form(None)):
    item = await add_spatial_map(plot_id, bed_id, file, date)
    return SpatialMapOut(
        id=item["id"],
        fileName=item["fileName"],
        url=file_url(request, item["filename"]),
        bytes=item["bytes"],
        contentType=item["contentType"],
        date=item["date"],
        createdAt=item["createdAt"],
    )

@router.get("", response_model=List[SpatialMapOut])
async def get_spatial_maps(plot_id: str, bed_id: str, request: Request):
    maps = await list_spatial_maps(plot_id, bed_id)
    return [
        SpatialMapOut(
            id=m["id"],
            fileName=m["fileName"],
            url=file_url(request, m["filename"]),
            bytes=m["bytes"],
            contentType=m["contentType"],
            date=m["date"],
            createdAt=m["createdAt"],
        )
        for m in maps
    ]

@router.delete("/{map_id}", status_code=204)
async def del_spatial_map(plot_id: str, bed_id: str, map_id: str):
    await delete_spatial_map(plot_id, bed_id, map_id)
    return {}
