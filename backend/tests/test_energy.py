import pytest
from app.analyzer.energy import estimate_energy
from app.models import DetectedPattern, PatternSeverity


def make_pattern(pattern_id, energy_cost=70.0, energy_saved=45.0):
    return DetectedPattern(
        pattern_id=pattern_id,
        name="Test Pattern",
        severity=PatternSeverity.HIGH,
        line_start=1,
        line_end=10,
        description="test",
        suggestion="test",
        estimated_energy_cost=energy_cost,
        estimated_energy_saved=energy_saved,
    )


def test_no_patterns_baseline():
    result = estimate_energy([])
    assert result["total_energy_score"] == 10.0
    assert result["estimated_kwh"] == 0.0
    assert result["estimated_co2_kg"] == 0.0


def test_single_sort_pattern():
    patterns = [make_pattern("inefficient_sort", 85.0, 60.0)]
    result = estimate_energy(patterns)
    assert result["total_energy_score"] > 10.0
    assert result["estimated_kwh"] > 0
    assert result["estimated_co2_kg"] > 0
    assert result["estimated_cost_eur"] > 0
    assert result["optimized_energy_score"] < result["total_energy_score"]


def test_multiple_patterns():
    patterns = [
        make_pattern("inefficient_sort", 85.0, 60.0),
        make_pattern("excessive_alloc", 75.0, 50.0),
    ]
    result = estimate_energy(patterns)
    assert result["total_energy_score"] > 50
    assert result["estimated_kwh"] > 0


def test_score_capped_at_100():
    patterns = [make_pattern("x", 95.0, 10.0) for _ in range(5)]
    result = estimate_energy(patterns)
    assert result["total_energy_score"] <= 100.0


def test_co2_and_cost_proportional():
    patterns = [make_pattern("inefficient_sort")]
    result = estimate_energy(patterns)
    # CO2 = kWh * 0.385, Cost = kWh * 0.25
    assert abs(result["estimated_co2_kg"] - result["estimated_kwh"] * 0.385) < 0.001
    assert abs(result["estimated_cost_eur"] - result["estimated_kwh"] * 0.25) < 0.001
