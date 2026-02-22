from anthropic import AsyncAnthropic
from app.ai.provider import (
    AIProvider, OptimizeResult, SYSTEM_PROMPT,
    build_optimization_prompt, parse_ai_response,
)
from app.models import DetectedPattern
from app.config import settings


class ClaudeProvider(AIProvider):
    async def optimize_code(
        self, code: str, patterns: list[DetectedPattern], language: str
    ) -> OptimizeResult:
        prompt = build_optimization_prompt(code, patterns, language)
        try:
            client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = await client.messages.create(
                model="claude-sonnet-4-6-20250220",
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
            return parse_ai_response(raw)
        except Exception as e:
            return OptimizeResult(
                optimized_code=code,
                chain_of_thought=f"AI optimization failed: {str(e)}. Original code returned.",
                changes_summary="No changes - AI provider unavailable.",
            )
