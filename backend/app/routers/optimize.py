from fastapi import APIRouter
from app.models import (
    OptimizeRequest, OptimizeResponse,
    HookRequest, HookResponse, HookFileResult,
)
from app.ai.provider import get_provider
from app.analyzer.engine import AnalysisEngine
from app.analyzer.energy import estimate_energy
from app.analyzer.patterns.sorting import SortingPatternDetector
from app.analyzer.patterns.memory import MemoryPatternDetector
from app.db.database import save_optimization

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_code(req: OptimizeRequest):
    provider = get_provider(req.provider)
    result = await provider.optimize_code(req.code, req.patterns, req.language)

    energy_before = estimate_energy(req.patterns)
    # After optimization, assume patterns are resolved
    energy_after = estimate_energy([])

    savings_kwh = energy_before["estimated_kwh"] - energy_after["estimated_kwh"]
    savings_co2 = energy_before["estimated_co2_kg"] - energy_after["estimated_co2_kg"]
    savings_eur = energy_before["estimated_cost_eur"] - energy_after["estimated_cost_eur"]

    # Save to database
    await save_optimization(
        filename=req.filename,
        language=req.language,
        patterns_found=len(req.patterns),
        pattern_details=[p.model_dump() for p in req.patterns],
        energy_before=energy_before["total_energy_score"],
        energy_after=energy_after["total_energy_score"],
        savings_kwh=savings_kwh,
        savings_co2_kg=savings_co2,
        savings_eur=savings_eur,
        original_code=req.code,
        optimized_code=result.optimized_code,
        chain_of_thought=result.chain_of_thought,
        ai_provider=req.provider,
    )

    return OptimizeResponse(
        filename=req.filename,
        original_code=req.code,
        optimized_code=result.optimized_code,
        changes_summary=result.changes_summary,
        chain_of_thought=result.chain_of_thought,
        energy_before=energy_before["total_energy_score"],
        energy_after=energy_after["total_energy_score"],
        savings_kwh=savings_kwh,
        savings_co2_kg=savings_co2,
        savings_eur=savings_eur,
    )


@router.post("/hook", response_model=HookResponse)
async def hook_endpoint(req: HookRequest):
    # Create a fresh engine for hook processing
    engine = AnalysisEngine()
    engine.register(SortingPatternDetector())
    engine.register(MemoryPatternDetector())

    results = []
    for file in req.files:
        language = "cpp" if file.filename.endswith((".cpp", ".hpp", ".cc", ".h")) else "python"
        patterns = engine.analyze(file.code, language)

        if not patterns:
            results.append(HookFileResult(
                filename=file.filename,
                had_issues=False,
                optimized_code=file.code,
                patterns_count=0,
                savings_kwh=0.0,
                savings_co2=0.0,
                savings_eur=0.0,
            ))
            continue

        # Optimize with AI
        provider = get_provider(req.provider)
        ai_result = await provider.optimize_code(file.code, patterns, language)

        energy_before = estimate_energy(patterns)
        energy_after = estimate_energy([])
        savings_kwh = energy_before["estimated_kwh"] - energy_after["estimated_kwh"]
        savings_co2 = energy_before["estimated_co2_kg"] - energy_after["estimated_co2_kg"]
        savings_eur = energy_before["estimated_cost_eur"] - energy_after["estimated_cost_eur"]

        # Save to DB
        await save_optimization(
            filename=file.filename,
            language=language,
            patterns_found=len(patterns),
            pattern_details=[p.model_dump() for p in patterns],
            energy_before=energy_before["total_energy_score"],
            energy_after=energy_after["total_energy_score"],
            savings_kwh=savings_kwh,
            savings_co2_kg=savings_co2,
            savings_eur=savings_eur,
            original_code=file.code,
            optimized_code=ai_result.optimized_code,
            chain_of_thought=ai_result.chain_of_thought,
            ai_provider=req.provider,
        )

        results.append(HookFileResult(
            filename=file.filename,
            had_issues=True,
            optimized_code=ai_result.optimized_code,
            patterns_count=len(patterns),
            savings_kwh=savings_kwh,
            savings_co2=savings_co2,
            savings_eur=savings_eur,
            chain_of_thought=ai_result.chain_of_thought,
        ))

    return HookResponse(results=results)
