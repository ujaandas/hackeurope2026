from fastapi import APIRouter
from app.models import DashboardData, ROIRequest, ROIResponse
from app.db.database import get_dashboard_data
from app.config import settings

router = APIRouter()


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard():
    data = await get_dashboard_data()
    return DashboardData(**data)


@router.post("/roi", response_model=ROIResponse)
async def calculate_roi(req: ROIRequest):
    data = await get_dashboard_data()

    # Scale savings based on custom parameters vs defaults
    kwh_ratio = req.kwh_price_eur / settings.COST_PER_KWH
    runs_ratio = req.runs_per_day / settings.ASSUMED_RUNS_PER_DAY

    annual_kwh = data["total_kwh_saved"] * runs_ratio
    annual_co2 = annual_kwh * settings.CO2_PER_KWH
    annual_eur = annual_kwh * req.kwh_price_eur

    return ROIResponse(
        annual_kwh_saved=round(annual_kwh, 4),
        annual_co2_saved=round(annual_co2, 4),
        annual_eur_saved=round(annual_eur, 4),
    )
