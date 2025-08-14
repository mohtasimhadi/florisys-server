# app/routers/rover.py
from fastapi import APIRouter

router = APIRouter(prefix="/plots/{plot_id}/beds/{bed_id}", tags=["rover"])

@router.post("/collect-rover-data")
async def collect_rover_data(plot_id: str, bed_id: str):
    # TODO: integrate with your rover pipeline/controller
    return {"ok": True, "message": f"Rover data collection queued for plot={plot_id}, bed={bed_id}"}
