import httpx
from app.ai.provider import (
    AIProvider,
    OptimizeResult,
    SYSTEM_PROMPT,
    build_optimization_prompt,
    parse_ai_response,
)
from app.models import DetectedPattern
from app.config import settings


class OllamaProvider(AIProvider):
    async def optimize_code(
        self, code: str, patterns: list[DetectedPattern], language: str
    ) -> OptimizeResult:
        prompt = build_optimization_prompt(code, patterns, language)
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.OLLAMA_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "system": SYSTEM_PROMPT,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                raw = response.json()["response"]
                return parse_ai_response(raw)
        except Exception as e:
            # Graceful degradation: return original code with error note
            return OptimizeResult(
                optimized_code=code,
                chain_of_thought=f"AI optimization failed: {str(e)}. Original code returned.",
                changes_summary="No changes - AI provider unavailable.",
            )
