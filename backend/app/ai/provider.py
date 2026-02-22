import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.models import DetectedPattern


@dataclass
class OptimizeResult:
    optimized_code: str
    chain_of_thought: str
    changes_summary: str


SYSTEM_PROMPT = """You are a Green Code Optimizer specializing in energy-efficient programming.
Your task is to refactor code to reduce energy consumption while maintaining correctness.

Rules:
1. Only modify code related to the detected energy anti-patterns
2. Maintain the same function signatures and external behavior
3. Explain your reasoning step by step (chain of thought)
4. Return the COMPLETE optimized file, not just snippets
5. Use modern C++ best practices (STL algorithms, smart pointers, etc.)"""


def build_optimization_prompt(
    code: str, patterns: list[DetectedPattern], language: str
) -> str:
    pattern_descriptions = "\n".join(
        f"- Line {p.line_start}-{p.line_end}: {p.name} -- {p.description}"
        for p in patterns
    )
    return f"""Analyze and optimize this {language} code for energy efficiency.

DETECTED ANTI-PATTERNS:
{pattern_descriptions}

ORIGINAL CODE:
```{language}
{code}
```

Provide your response in this EXACT format:

CHAIN OF THOUGHT:
[Your step-by-step reasoning about each optimization]

CHANGES SUMMARY:
[Brief bullet list of what you changed and why]

OPTIMIZED CODE:
```{language}
[Complete optimized code here]
```"""


def parse_ai_response(raw: str) -> OptimizeResult:
    chain_of_thought = ""
    changes_summary = ""
    optimized_code = ""

    # Extract chain of thought
    cot_match = re.search(
        r"CHAIN OF THOUGHT:\s*\n(.*?)(?=CHANGES SUMMARY:|OPTIMIZED CODE:|$)",
        raw,
        re.DOTALL,
    )
    if cot_match:
        chain_of_thought = cot_match.group(1).strip()

    # Extract changes summary
    cs_match = re.search(
        r"CHANGES SUMMARY:\s*\n(.*?)(?=OPTIMIZED CODE:|$)",
        raw,
        re.DOTALL,
    )
    if cs_match:
        changes_summary = cs_match.group(1).strip()

    # Extract optimized code from code block
    code_match = re.search(r"```\w*\n(.*?)```", raw, re.DOTALL)
    if code_match:
        optimized_code = code_match.group(1).strip()
    elif "OPTIMIZED CODE:" in raw:
        # Fallback: take everything after OPTIMIZED CODE:
        optimized_code = raw.split("OPTIMIZED CODE:")[-1].strip()

    # If parsing completely failed, return raw as code
    if not optimized_code:
        optimized_code = raw

    return OptimizeResult(
        optimized_code=optimized_code,
        chain_of_thought=chain_of_thought or "AI reasoning not available.",
        changes_summary=changes_summary or "Changes applied.",
    )


class AIProvider(ABC):
    @abstractmethod
    async def optimize_code(
        self, code: str, patterns: list[DetectedPattern], language: str
    ) -> OptimizeResult:
        pass


def get_provider(name: str) -> AIProvider:
    if name == "ollama":
        from app.ai.ollama_provider import OllamaProvider

        return OllamaProvider()
    elif name == "claude":
        from app.ai.claude_provider import ClaudeProvider

        return ClaudeProvider()
    elif name == "gemini":
        from app.ai.gemini_provider import GeminiProvider

        return GeminiProvider()
    raise ValueError(f"Unknown AI provider: {name}")
