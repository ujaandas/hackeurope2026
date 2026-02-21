from app.models import DetectedPattern
from app.config import settings

# Energy weights per pattern type
PATTERN_ENERGY_WEIGHTS = {
    "inefficient_sort": {
        "cpu_cycles_factor": 85,
        "memory_pressure": 10,
        "kwh_per_1k_runs": 0.0015,
    },
    "excessive_alloc": {
        "cpu_cycles_factor": 60,
        "memory_pressure": 80,
        "kwh_per_1k_runs": 0.0008,
    },
    "memory_leak": {
        "cpu_cycles_factor": 30,
        "memory_pressure": 70,
        "kwh_per_1k_runs": 0.0005,
    },
}

# Default for unknown patterns
DEFAULT_WEIGHT = {
    "cpu_cycles_factor": 40,
    "memory_pressure": 40,
    "kwh_per_1k_runs": 0.0006,
}


def estimate_energy(patterns: list[DetectedPattern]) -> dict:
    if not patterns:
        return {
            "total_energy_score": 10.0,
            "optimized_energy_score": 10.0,
            "estimated_kwh": 0.0,
            "estimated_co2_kg": 0.0,
            "estimated_cost_eur": 0.0,
        }

    total_kwh_per_1k = 0.0
    total_energy_cost = 0.0
    total_energy_saved = 0.0

    for p in patterns:
        weight = PATTERN_ENERGY_WEIGHTS.get(p.pattern_id, DEFAULT_WEIGHT)
        total_kwh_per_1k += weight["kwh_per_1k_runs"]
        total_energy_cost += p.estimated_energy_cost
        total_energy_saved += p.estimated_energy_saved

    # Scale to annual estimate (runs_per_day * 365 days)
    annual_kwh = total_kwh_per_1k * settings.ASSUMED_RUNS_PER_DAY * 365
    annual_co2 = annual_kwh * settings.CO2_PER_KWH
    annual_eur = annual_kwh * settings.COST_PER_KWH

    energy_score = min(100.0, 10.0 + total_energy_cost)
    optimized_score = max(10.0, energy_score - total_energy_saved)

    return {
        "total_energy_score": round(energy_score, 1),
        "optimized_energy_score": round(optimized_score, 1),
        "estimated_kwh": round(annual_kwh, 4),
        "estimated_co2_kg": round(annual_co2, 4),
        "estimated_cost_eur": round(annual_eur, 4),
    }
