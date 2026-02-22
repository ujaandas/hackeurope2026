from google import genai
from google.genai import types
from app.ai.provider import (
    AIProvider,
    OptimizeResult,
    SYSTEM_PROMPT,
    build_optimization_prompt,
    parse_ai_response,
)
from app.models import DetectedPattern
from app.config import settings


class GeminiProvider(AIProvider):
    async def optimize_code(
        self, code: str, patterns: list[DetectedPattern], language: str
    ) -> OptimizeResult:
        prompt = build_optimization_prompt(code, patterns, language)
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=8192,
                    temperature=0.7,
                ),
                contents=prompt,
            )

            raw = response.text
            return parse_ai_response(raw)

        except Exception as e:
            return OptimizeResult(
                optimized_code=code,
                chain_of_thought=f"Gemini optimization failed: {str(e)}. Original code returned.",
                changes_summary="No changes - AI provider unavailable.",
            )
