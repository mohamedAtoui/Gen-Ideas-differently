"""Stage 1: Decompose — Extract functions, constraints, contradictions."""

from __future__ import annotations

from ..llm.client import call_claude_json
from ..llm.prompts import DECOMPOSE_PROMPT
from ..models import ProblemAnalysis


async def decompose(problem: str, *, model: str | None = None) -> ProblemAnalysis:
    """Decompose a problem into functions, constraints, and contradictions.

    Enhanced to produce elaborated problem descriptions and TRIZ-friendly
    contradiction terms for better downstream results.
    """
    prompt = DECOMPOSE_PROMPT.format(problem=problem)
    kwargs = {}
    if model:
        kwargs["model"] = model

    data = await call_claude_json(
        prompt,
        system_prompt="You are a systems analyst specializing in functional decomposition and cross-domain innovation. Respond only with valid JSON.",
        **kwargs,
    )
    return ProblemAnalysis(**data)
