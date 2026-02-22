"""Fetches real-time carbon intensity data from public APIs.

Supported sources (in priority order):
  1. UK Carbon Intensity API  (free, no auth, UK-only)
     https://api.carbonintensity.org.uk/
  2. Electricity Maps API     (free tier, requires API key, global)
     https://api.electricitymap.org/
  3. Static fallback           (regional averages from IEA 2023 data)
"""

import time
import httpx

from app.config import settings

# ------------------------------------------------------------------ #
# Cache: carbon intensity doesn't change second-by-second.
# We cache for 30 minutes.
# ------------------------------------------------------------------ #

_cache: dict[str, tuple[float, float]] = {}  # key -> (value, timestamp)
_CACHE_TTL = 1800  # 30 minutes


def _get_cached(key: str) -> float | None:
    if key in _cache:
        value, ts = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return value
    return None


def _set_cached(key: str, value: float) -> None:
    _cache[key] = (value, time.time())


# ------------------------------------------------------------------ #
# IEA 2023 regional average emission factors (gCO2/kWh)
# Source: IEA Emission Factors 2023
# ------------------------------------------------------------------ #

REGIONAL_AVERAGES: dict[str, float] = {
    "GB": 207.0,
    "DE": 385.0,
    "FR": 56.0,
    "US": 388.0,
    "CN": 555.0,
    "IN": 632.0,
    "JP": 462.0,
    "AU": 540.0,
    "BR": 61.0,
    "CA": 120.0,
    "SE": 13.0,
    "NO": 8.0,
    "PL": 635.0,
    "NL": 328.0,
    "EU": 230.0,  # EU average
    "WORLD": 436.0,
}


async def get_carbon_intensity_gco2_kwh(location: str | None = None) -> float:
    """Return the current carbon intensity in gCO2/kWh.

    Tries live APIs first, falls back to static regional averages.
    """
    loc = (location or settings.CARBON_INTENSITY_LOCATION).upper()
    cache_key = f"ci_{loc}"

    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    # 1. Try UK Carbon Intensity API (free, no auth)
    if loc in ("GB", "UK"):
        value = await _fetch_uk_carbon_intensity()
        if value is not None:
            _set_cached(cache_key, value)
            return value

    # 2. Try Electricity Maps API (needs API key)
    if settings.ELECTRICITY_MAPS_API_KEY:
        value = await _fetch_electricity_maps(loc)
        if value is not None:
            _set_cached(cache_key, value)
            return value

    # 3. Static fallback
    value = REGIONAL_AVERAGES.get(loc, REGIONAL_AVERAGES["EU"])
    _set_cached(cache_key, value)
    return value


async def _fetch_uk_carbon_intensity() -> float | None:
    """Fetch current carbon intensity from api.carbonintensity.org.uk.

    Returns gCO2/kWh or None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.carbonintensity.org.uk/intensity"
            )
            resp.raise_for_status()
            data = resp.json()
            # Response: { "data": [{ "intensity": { "actual": 185, "forecast": 190, "index": "moderate" } }] }
            intensity = data["data"][0]["intensity"]
            # Prefer actual, fall back to forecast
            return float(intensity.get("actual") or intensity.get("forecast"))
    except Exception:
        return None


async def _fetch_electricity_maps(zone: str) -> float | None:
    """Fetch current carbon intensity from Electricity Maps API.

    Requires ELECTRICITY_MAPS_API_KEY in settings.
    Returns gCO2/kWh or None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.electricitymap.org/v3/carbon-intensity/latest",
                params={"zone": zone},
                headers={"auth-token": settings.ELECTRICITY_MAPS_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()
            return float(data["carbonIntensity"])
    except Exception:
        return None
