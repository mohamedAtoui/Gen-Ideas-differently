"""Stage 6: Evaluate — Score and rank solutions."""

from __future__ import annotations

import asyncio
import json

from ..knowledge.domains import DOMAIN_CATALOG
from ..llm.client import call_claude_json
from ..llm.prompts import EVALUATE_PROMPT
from ..mapping_analysis import compute_systematicity
from ..models import (
    EvaluationResult,
    ProblemAnalysis,
    ScoredSolution,
    StructuralAnalogy,
    SynthesizedSolution,
)

# Build domain-to-category mapping from the canonical DOMAIN_CATALOG
_DOMAIN_CATEGORIES: dict[str, str] = {
    d.name.lower(): d.category.lower() for d in DOMAIN_CATALOG
}

# Adjacent category pairs — domains in adjacent categories are closer
# than truly distant ones, but farther than same-category.
_ADJACENT_CATEGORIES: set[frozenset[str]] = {
    frozenset({"biology", "applied"}),
    frozenset({"biology", "earth"}),
    frozenset({"physics", "engineering"}),
    frozenset({"physics", "math"}),
    frozenset({"math", "engineering"}),
    frozenset({"social", "applied"}),
    frozenset({"social", "arts"}),
    frozenset({"earth", "physics"}),
    frozenset({"applied", "engineering"}),
    frozenset({"arts", "math"}),
}


def _domain_distance(home: str, source: str) -> float:
    """Estimate domain distance (0-1).

    Returns:
        0.0 — identical domains
        0.3 — same category
        0.5 — adjacent categories
        0.8 — distant categories
    """
    home_lower = home.lower().strip()
    source_lower = source.lower().strip()
    if home_lower == source_lower:
        return 0.0
    home_cat = _DOMAIN_CATEGORIES.get(home_lower, home_lower)
    source_cat = _DOMAIN_CATEGORIES.get(source_lower, source_lower)
    if home_cat == source_cat:
        return 0.3
    if frozenset({home_cat, source_cat}) in _ADJACENT_CATEGORIES:
        return 0.5
    return 0.8


def _abstraction_bonus(level: str) -> float:
    """Higher abstraction = more novelty potential."""
    return {"effect": 0.2, "phenomenon": 0.15, "action": 0.1, "parts": 0.0}.get(level, 0.1)


async def _evaluate_solution(
    solution: SynthesizedSolution,
    analogy: StructuralAnalogy,
    analysis: ProblemAnalysis,
    model: str | None,
) -> ScoredSolution:
    """Evaluate a single solution."""
    prompt = EVALUATE_PROMPT.format(
        original_problem=analysis.elaborated_problem or analysis.original_problem,
        home_domain=analysis.domain,
        source_domain=solution.source_domain,
        concrete_approach=solution.concrete_approach,
        candidate_inferences=json.dumps(solution.candidate_inferences),
        key_predictions=json.dumps(solution.key_predictions),
        mapping_count=len(analogy.mappings),
        abstraction_level=analogy.abstraction_level,
        transfer_strength=solution.transfer_strength,
        where_it_breaks=analogy.where_it_breaks,
    )

    kwargs = {}
    if model:
        kwargs["model"] = model

    try:
        data = await call_claude_json(
            prompt,
            system_prompt="You are an innovation evaluator. Respond only with valid JSON.",
            **kwargs,
        )
        novelty = float(data.get("novelty", 0.5))
        feasibility = float(data.get("feasibility", 0.5))
        structural_depth = float(data.get("structural_depth", 0.5))
        actionability = float(data.get("actionability", 0.5))
        reasoning = data.get("reasoning", "")
    except Exception:
        # Fallback to heuristic scoring
        dist = _domain_distance(analysis.domain, solution.source_domain)
        novelty = min(1.0, dist + _abstraction_bonus(analogy.abstraction_level))
        feasibility = {"strong": 0.8, "moderate": 0.5, "weak": 0.3}.get(solution.transfer_strength, 0.5)
        structural_depth = compute_systematicity(analogy.mappings)
        actionability = 0.5
        reasoning = "Scored via heuristic fallback"

    # Same-domain penalty — exact match only to avoid false positives
    same_domain = analysis.domain.lower().strip() == solution.source_domain.lower().strip()
    combined = 0.30 * novelty + 0.25 * feasibility + 0.25 * structural_depth + 0.20 * actionability
    if same_domain:
        combined *= 0.5

    return ScoredSolution(
        solution=solution,
        analogy=analogy,
        novelty=round(novelty, 2),
        feasibility=round(feasibility, 2),
        structural_depth=round(structural_depth, 2),
        actionability=round(actionability, 2),
        combined_score=round(combined, 2),
        same_domain_penalty=same_domain,
        reasoning=reasoning,
    )


async def evaluate(
    solutions: list[SynthesizedSolution],
    analogies: list[StructuralAnalogy],
    analysis: ProblemAnalysis,
    *,
    model: str | None = None,
) -> EvaluationResult:
    """Evaluate and rank all solutions."""
    # Pair solutions with their analogies by source domain
    analogy_map = {a.source_domain: a for a in analogies}

    tasks = []
    for solution in solutions:
        analogy = analogy_map.get(solution.source_domain)
        if not analogy and analogies:
            analogy = analogies[0]  # fallback
        if analogy:
            tasks.append(_evaluate_solution(solution, analogy, analysis, model))

    scored = await asyncio.gather(*tasks)
    scored_sorted = sorted(scored, key=lambda s: s.combined_score, reverse=True)

    top_rec = ""
    if scored_sorted:
        top = scored_sorted[0]
        top_rec = (
            f"Top recommendation: {top.solution.source_domain} → {top.solution.source_mechanism} "
            f"(score: {top.combined_score})"
        )

    return EvaluationResult(
        scored_solutions=list(scored_sorted),
        top_recommendation=top_rec,
    )
