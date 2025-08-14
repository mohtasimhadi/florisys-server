# app/routers/plots.py
from fastapi import APIRouter, File, UploadFile, Request, Response, status
from typing import List
from app.models.plot import PlotOut
from app.services.plots import list_plots, create_plot, delete_plot

router = APIRouter(prefix="/plots", tags=["plots"])

@router.get("", response_model=List[PlotOut])
async def get_plots(request: Request):
    return await list_plots(request)

@router.post("", response_model=PlotOut, status_code=status.HTTP_201_CREATED)
async def post_plot(request: Request, file: UploadFile = File(...)):
    return await create_plot(file, request)

@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_plot(plot_id: str):
    await delete_plot(plot_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
