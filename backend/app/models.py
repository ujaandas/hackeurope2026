from pydantic import BaseModel, field_validator
from enum import Enum
from app.config import settings


class PatternSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DetectedPattern(BaseModel):
    pattern_id: str
    name: str
    severity: PatternSeverity
    line_start: int
    line_end: int
    description: str
    suggestion: str
    estimated_energy_cost: float
    estimated_energy_saved: float


class AnalyzeRequest(BaseModel):
    filename: str
    code: str
    language: str = "cpp"


class AnalyzeResponse(BaseModel):
    filename: str
    patterns: list[DetectedPattern]
    total_energy_score: float
    optimized_energy_score: float
    estimated_kwh: float
    estimated_co2_kg: float
    estimated_cost_eur: float
    carbon_intensity_gco2_kwh: float = 0.0


class OptimizeRequest(BaseModel):
    filename: str
    code: str
    patterns: list[DetectedPattern]
    language: str = "cpp"
    provider: str = ""

    @field_validator("provider", mode="before")
    @classmethod
    def default_provider(cls, v: str) -> str:
        return v or settings.AI_PROVIDER


class OptimizeResponse(BaseModel):
    filename: str
    original_code: str
    optimized_code: str
    changes_summary: str
    chain_of_thought: str
    energy_before: float
    energy_after: float
    savings_kwh: float
    savings_co2_kg: float
    savings_eur: float


class HookFileRequest(BaseModel):
    filename: str
    code: str


class HookRequest(BaseModel):
    files: list[HookFileRequest]
    provider: str = ""

    @field_validator("provider", mode="before")
    @classmethod
    def default_provider(cls, v: str) -> str:
        return v or settings.AI_PROVIDER


class HookFileResult(BaseModel):
    filename: str
    had_issues: bool
    optimized_code: str
    patterns_count: int
    savings_kwh: float
    savings_co2: float
    savings_eur: float
    chain_of_thought: str = ""


class HookResponse(BaseModel):
    results: list[HookFileResult]


class OptimizationRecord(BaseModel):
    id: int
    timestamp: str
    filename: str
    language: str
    patterns_found: int
    energy_before: float
    energy_after: float
    savings_kwh: float
    savings_co2_kg: float
    savings_eur: float
    original_code: str = ""
    optimized_code: str = ""
    chain_of_thought: str = ""


class DashboardData(BaseModel):
    total_optimizations: int
    total_kwh_saved: float
    total_co2_saved: float
    total_eur_saved: float
    sustainability_score: int
    history: list[OptimizationRecord]


class ROIRequest(BaseModel):
    kwh_price_eur: float = 0.25
    runs_per_day: int = 1000


class ROIResponse(BaseModel):
    annual_kwh_saved: float
    annual_co2_saved: float
    annual_eur_saved: float
