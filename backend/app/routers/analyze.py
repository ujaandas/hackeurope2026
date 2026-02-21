from fastapi import APIRouter, Request
from app.models import AnalyzeRequest, AnalyzeResponse
from app.analyzer.energy import estimate_energy

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(req: AnalyzeRequest, request: Request):
    engine = request.app.state.engine
    patterns = engine.analyze(req.code, req.language)
    energy = estimate_energy(patterns)

    return AnalyzeResponse(
        filename=req.filename,
        patterns=patterns,
        total_energy_score=energy["total_energy_score"],
        optimized_energy_score=energy["optimized_energy_score"],
        estimated_kwh=energy["estimated_kwh"],
        estimated_co2_kg=energy["estimated_co2_kg"],
        estimated_cost_eur=energy["estimated_cost_eur"],
    )
