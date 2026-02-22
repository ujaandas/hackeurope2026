"""Energy estimation with live carbon intensity data.

kWh estimates are derived from published measurements:
  - Typical server CPU (Intel Xeon / AMD EPYC): ~100-200W TDP
  - We use 150W as reference, which is the midpoint for cloud instances.
  - Time estimates per pattern come from algorithmic analysis and published
    benchmarks (see references in PATTERN_ENERGY_PROFILES).

CO2 intensity is fetched live from:
  1. UK Carbon Intensity API  (free, no auth)
  2. Electricity Maps API     (global, needs key)
  3. IEA 2023 regional averages (offline fallback)
"""

from app.models import DetectedPattern
from app.config import settings
from app.analyzer.carbon_intensity import get_carbon_intensity_gco2_kwh

# Reference hardware power consumption
_CPU_TDP_WATTS = 150.0     # Typical cloud instance CPU power draw
_NIC_ACTIVE_WATTS = 10.0   # Network interface active power
_DRAM_WATTS = 5.0          # Per-channel DRAM power

# ------------------------------------------------------------------ #
# Energy profiles per pattern type.
#
# Each profile specifies:
#   cpu_seconds_per_run  : estimated additional CPU time per execution
#   nic_seconds_per_run  : estimated NIC active time per execution
#   memory_overhead_mb   : additional working-set pressure (MB)
#
# Savings factor (0.0-1.0): fraction of waste eliminated by fix.
# ------------------------------------------------------------------ #

PATTERN_ENERGY_PROFILES: dict[str, dict] = {
    # O(n^2) sort vs O(n log n): for n=10000, bubble ~50M ops vs introsort ~130K ops
    # At ~1 ns/op: 50ms vs 0.13ms -> ~50ms excess CPU time per call
    # Ref: Knuth TAOCP Vol 3; empirical measurements on Xeon E5-2690
    "inefficient_sort": {
        "cpu_seconds_per_run": 0.050,
        "nic_seconds_per_run": 0.0,
        "memory_overhead_mb": 0.0,
        "savings_factor": 0.95,
    },
    # Heap allocation in loop: malloc ~100ns per call, if 1000 iterations
    # that's 0.1ms CPU + memory pressure causing cache misses (~2x slowdown)
    # Ref: glibc malloc benchmarks, Chandler Carruth CppCon 2014
    "excessive_alloc": {
        "cpu_seconds_per_run": 0.005,
        "nic_seconds_per_run": 0.0,
        "memory_overhead_mb": 50.0,
        "savings_factor": 0.80,
    },
    # Memory leak: progressive working set growth -> swap pressure
    # Long-running process: ~10MB/hour leak -> after 8h, ~80MB swap I/O
    "memory_leak": {
        "cpu_seconds_per_run": 0.002,
        "nic_seconds_per_run": 0.0,
        "memory_overhead_mb": 80.0,
        "savings_factor": 0.90,
    },
    # Network call in loop: each HTTP request ~50ms latency + NIC wake
    # 100 iterations: 5s network wait + NIC active power
    # Ref: Huang et al., "A Close Examination of Performance and Power
    # Characteristics of 4G LTE Networks" (MobiCom 2012) - adapted for wired
    "network_waste": {
        "cpu_seconds_per_run": 0.010,
        "nic_seconds_per_run": 5.0,
        "memory_overhead_mb": 10.0,
        "savings_factor": 0.85,
    },
    # Polling: sleep(5) + HTTP check -> CPU wakes every 5s, NIC active
    # Over 1 hour: 720 wake-ups, 720 HTTP requests
    # vs event-driven: CPU sleeps, NIC interrupt on data arrival
    "polling_pattern": {
        "cpu_seconds_per_run": 0.200,
        "nic_seconds_per_run": 3.600,
        "memory_overhead_mb": 5.0,
        "savings_factor": 0.90,
    },
    # Duplicate network call: redundant HTTP round-trip (~100ms + data transfer)
    "duplicate_network_call": {
        "cpu_seconds_per_run": 0.005,
        "nic_seconds_per_run": 0.100,
        "memory_overhead_mb": 2.0,
        "savings_factor": 0.95,
    },
}

DEFAULT_PROFILE = {
    "cpu_seconds_per_run": 0.010,
    "nic_seconds_per_run": 0.0,
    "memory_overhead_mb": 10.0,
    "savings_factor": 0.50,
}


def _kwh_per_run(profile: dict) -> float:
    """Calculate energy per single execution in kWh from a profile."""
    cpu_joules = profile["cpu_seconds_per_run"] * _CPU_TDP_WATTS
    nic_joules = profile["nic_seconds_per_run"] * _NIC_ACTIVE_WATTS
    # DRAM overhead: assume 1 channel per 8GB, proportional to overhead
    mem_channels = max(1.0, profile["memory_overhead_mb"] / 8192.0)
    mem_joules = profile["cpu_seconds_per_run"] * _DRAM_WATTS * mem_channels

    total_joules = cpu_joules + nic_joules + mem_joules
    return total_joules / 3_600_000  # J -> kWh


def estimate_energy(patterns: list[DetectedPattern]) -> dict:
    """Estimate energy impact using pattern profiles and static CO2 factor.

    For the synchronous codepath (used by existing callers).
    Uses the hardcoded CO2_PER_KWH fallback from settings.
    """
    return _compute_energy(patterns, settings.CO2_PER_KWH * 1000)


async def estimate_energy_live(
    patterns: list[DetectedPattern], location: str | None = None
) -> dict:
    """Estimate energy impact using live carbon intensity data.

    Fetches real-time gCO2/kWh from Carbon Intensity APIs.
    """
    carbon_intensity = await get_carbon_intensity_gco2_kwh(location)
    return _compute_energy(patterns, carbon_intensity)


def _compute_energy(
    patterns: list[DetectedPattern], carbon_intensity_gco2_kwh: float
) -> dict:
    if not patterns:
        return {
            "total_energy_score": 10.0,
            "optimized_energy_score": 10.0,
            "estimated_kwh": 0.0,
            "estimated_co2_kg": 0.0,
            "estimated_cost_eur": 0.0,
            "carbon_intensity_gco2_kwh": round(carbon_intensity_gco2_kwh, 1),
        }

    total_kwh_per_run = 0.0
    total_savings_kwh_per_run = 0.0

    for p in patterns:
        profile = PATTERN_ENERGY_PROFILES.get(p.pattern_id, DEFAULT_PROFILE)
        kwh = _kwh_per_run(profile)
        total_kwh_per_run += kwh
        total_savings_kwh_per_run += kwh * profile["savings_factor"]

    runs_per_year = settings.ASSUMED_RUNS_PER_DAY * 365
    annual_kwh = total_kwh_per_run * runs_per_year
    annual_savings_kwh = total_savings_kwh_per_run * runs_per_year

    # CO2: convert gCO2/kWh to kgCO2/kWh then multiply
    co2_kg_per_kwh = carbon_intensity_gco2_kwh / 1000.0
    annual_co2 = annual_kwh * co2_kg_per_kwh
    annual_eur = annual_kwh * settings.COST_PER_KWH

    # Energy score: 10 (perfect) to 100 (worst)
    # Scale: each mWh of annual waste adds ~1 point (capped at 100)
    energy_score = min(100.0, 10.0 + annual_kwh * 1000)
    optimized_score = max(10.0, energy_score - annual_savings_kwh * 1000)

    return {
        "total_energy_score": round(energy_score, 1),
        "optimized_energy_score": round(optimized_score, 1),
        "estimated_kwh": round(annual_kwh, 4),
        "estimated_co2_kg": round(annual_co2, 4),
        "estimated_cost_eur": round(annual_eur, 4),
        "carbon_intensity_gco2_kwh": round(carbon_intensity_gco2_kwh, 1),
    }
