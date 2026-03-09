"""Stage 4: Mine — Structural analogy mapping per domain (parallel)."""

from __future__ import annotations

import asyncio
import json

from ..llm.client import call_claude_json
from ..llm.prompts import MINE_PROMPT
from ..models import (
    AbstractionResult,
    CandidateDomain,
    MiningResult,
    ProblemAnalysis,
    StructuralAnalogy,
)


async def _mine_domain(
    domain: CandidateDomain,
    analysis: ProblemAnalysis,
    abstractions: AbstractionResult | None,
    model: str | None,
) -> StructuralAnalogy | None:
    """Mine a single domain for structural analogies."""
    contradictions_text = json.dumps(
        [c.model_dump() for c in analysis.contradictions]
    ) if analysis.contradictions else "None identified"

    # Gather richer context from abstractions
    sapphire_effect = ""
    nature_questions = "None available"
    if abstractions:
        sapphire_effect = abstractions.sapphire.effect
        nature_questions = json.dumps(abstractions.biologize.nature_questions[:4])

    prompt = MINE_PROMPT.format(
        source_domain=domain.domain,
        primary_function=analysis.primary_function,
        sub_functions=", ".join(analysis.sub_functions),
        constraints=", ".join(analysis.constraints),
        contradictions=contradictions_text,
        parameters=", ".join(analysis.parameters),
        rationale=domain.rationale,
        sapphire_effect=sapphire_effect,
        nature_questions=nature_questions,
        analogical_hooks=json.dumps(analysis.analogical_hooks) if analysis.analogical_hooks else "None identified",
    )

    kwargs = {}
    if model:
        kwargs["model"] = model

    try:
        data = await call_claude_json(
            prompt,
            system_prompt="You are an analogical reasoning expert. Respond only with valid JSON.",
            **kwargs,
        )
        return StructuralAnalogy(**data)
    except Exception:
        return None


async def mine(
    analysis: ProblemAnalysis,
    candidate_domains: list[CandidateDomain],
    *,
    abstractions: AbstractionResult | None = None,
    model: str | None = None,
) -> MiningResult:
    """Mine all candidate domains in parallel for structural analogies."""
    tasks = [_mine_domain(d, analysis, abstractions, model) for d in candidate_domains]
    results = await asyncio.gather(*tasks)

    analogies = [r for r in results if r is not None]
    return MiningResult(analogies=analogies)
