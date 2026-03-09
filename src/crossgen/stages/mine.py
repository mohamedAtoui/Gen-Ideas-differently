"""Stage 4: Mine — Structural analogy mapping per domain (parallel).

Implements MAC/FAC-inspired two-phase mining:
  Phase 1 (Retrieve): Cheap LLM call to list 3-5 candidate mechanisms.
  Phase 2 (Map): Full structural mapping on top 2 candidates.

After each analogy is created, mapping validation and computed systematicity
are applied to override LLM self-assessment (Gentner's SMT constraints).
"""

from __future__ import annotations

import asyncio
import json
import logging

from ..llm.client import call_claude_json
from ..llm.prompts import MINE_PROMPT, MINE_RETRIEVE_PROMPT
from ..mapping_analysis import compute_systematicity, validate_mappings
from ..models import (
    AbstractionResult,
    CandidateDomain,
    CandidateMechanism,
    MiningResult,
    ProblemAnalysis,
    StructuralAnalogy,
)

logger = logging.getLogger(__name__)

# Critical validation flags that warrant a retry of the mapping call.
_CRITICAL_FLAGS = {"no_mappings", "too_few_mappings"}


def _has_critical_flags(flags: list[str]) -> bool:
    """Return True if any flag starts with a critical flag prefix."""
    for flag in flags:
        prefix = flag.split(":")[0].strip()
        if prefix in _CRITICAL_FLAGS:
            return True
    return False


def _build_common_context(
    domain: CandidateDomain,
    analysis: ProblemAnalysis,
    abstractions: AbstractionResult | None,
) -> dict[str, str]:
    """Build the common context dict shared by retrieve and map prompts."""
    contradictions_text = json.dumps(
        [c.model_dump() for c in analysis.contradictions]
    ) if analysis.contradictions else "None identified"

    sapphire_effect = ""
    nature_questions = "None available"
    if abstractions:
        sapphire_effect = abstractions.sapphire.effect
        nature_questions = json.dumps(abstractions.biologize.nature_questions[:4])

    behavior_chain_text = " → ".join(analysis.behavior_chain) if analysis.behavior_chain else "Not available"

    return {
        "source_domain": domain.domain,
        "primary_function": analysis.primary_function,
        "sub_functions": ", ".join(analysis.sub_functions),
        "constraints": ", ".join(analysis.constraints),
        "contradictions": contradictions_text,
        "parameters": ", ".join(analysis.parameters),
        "rationale": domain.rationale,
        "sapphire_effect": sapphire_effect,
        "nature_questions": nature_questions,
        "analogical_hooks": json.dumps(analysis.analogical_hooks) if analysis.analogical_hooks else "None identified",
        "behavior_chain": behavior_chain_text,
    }


async def _retrieve_mechanisms(
    context: dict[str, str],
    model: str | None,
) -> list[CandidateMechanism]:
    """Phase 1 (Retrieve): Cheap LLM call to list 3-5 candidate mechanisms."""
    prompt = MINE_RETRIEVE_PROMPT.format(**context)

    kwargs: dict = {}
    if model:
        kwargs["model"] = model

    try:
        data = await call_claude_json(
            prompt,
            system_prompt="You are an analogical reasoning expert. Respond only with valid JSON.",
            max_retries=1,
            **kwargs,
        )
        # data should be a list of dicts
        if isinstance(data, list):
            return [CandidateMechanism(**item) for item in data]
        # If the LLM wraps it in an object, try common keys
        if isinstance(data, dict):
            for key in ("mechanisms", "candidates", "results"):
                if key in data and isinstance(data[key], list):
                    return [CandidateMechanism(**item) for item in data[key]]
        logger.warning("Retrieve phase returned unexpected format: %s", type(data))
        return []
    except Exception:
        logger.warning("Retrieve phase failed for domain %s", context["source_domain"], exc_info=True)
        return []


async def _map_mechanism(
    mechanism: CandidateMechanism,
    context: dict[str, str],
    model: str | None,
    validation_errors: list[str] | None = None,
) -> StructuralAnalogy | None:
    """Phase 2 (Map): Full structural mapping for a single mechanism.

    Uses the existing MINE_PROMPT, adding the specific mechanism hint and
    behavior_chain to the context.
    """
    # Build the MINE_PROMPT with the mechanism hint injected into the rationale
    enriched_rationale = (
        f"{context['rationale']}\n"
        f"SPECIFIC MECHANISM TO MAP: {mechanism.mechanism} — {mechanism.rationale}"
    )

    prompt = MINE_PROMPT.format(
        source_domain=context["source_domain"],
        primary_function=context["primary_function"],
        sub_functions=context["sub_functions"],
        constraints=context["constraints"],
        contradictions=context["contradictions"],
        parameters=context["parameters"],
        rationale=enriched_rationale,
        sapphire_effect=context["sapphire_effect"],
        nature_questions=context["nature_questions"],
        analogical_hooks=context["analogical_hooks"],
        behavior_chain=context["behavior_chain"],
    )

    kwargs: dict = {}
    if model:
        kwargs["model"] = model
    if validation_errors:
        kwargs["validation_errors"] = validation_errors

    try:
        data = await call_claude_json(
            prompt,
            system_prompt="You are an analogical reasoning expert. Respond only with valid JSON.",
            **kwargs,
        )
        return StructuralAnalogy(**data)
    except Exception:
        logger.warning(
            "Map phase failed for mechanism '%s' in domain %s",
            mechanism.mechanism,
            context["source_domain"],
            exc_info=True,
        )
        return None


def _post_process_analogy(analogy: StructuralAnalogy) -> StructuralAnalogy:
    """Apply computed systematicity and mapping validation to an analogy."""
    # Computed systematicity overrides LLM self-reported score
    analogy.systematicity_score = compute_systematicity(analogy.mappings)

    # Mapping validation
    flags = validate_mappings(analogy)
    analogy.quality_flags = flags

    return analogy


async def _mine_domain(
    domain: CandidateDomain,
    analysis: ProblemAnalysis,
    abstractions: AbstractionResult | None,
    model: str | None,
) -> list[StructuralAnalogy]:
    """Mine a single domain for structural analogies (MAC/FAC two-phase).

    Returns up to 2 analogies per domain.
    """
    context = _build_common_context(domain, analysis, abstractions)

    # --- Phase 1: Retrieve candidate mechanisms ---
    candidates = await _retrieve_mechanisms(context, model)

    if not candidates:
        logger.info("No candidate mechanisms found for domain %s", domain.domain)
        return []

    # Pick top 2 by relevance_score
    candidates_sorted = sorted(candidates, key=lambda c: c.relevance_score, reverse=True)
    top_candidates = candidates_sorted[:2]

    # --- Phase 2: Map top candidates in parallel ---
    map_tasks = [_map_mechanism(mech, context, model) for mech in top_candidates]
    raw_analogies = await asyncio.gather(*map_tasks)

    # Post-process and validate each analogy
    analogies: list[StructuralAnalogy] = []
    for i, analogy in enumerate(raw_analogies):
        if analogy is None:
            continue

        analogy = _post_process_analogy(analogy)

        # Retry with validation feedback if critical issues found
        if _has_critical_flags(analogy.quality_flags):
            logger.info(
                "Critical validation flags for domain %s mechanism '%s': %s — retrying",
                domain.domain,
                top_candidates[i].mechanism,
                analogy.quality_flags,
            )
            retried = await _map_mechanism(
                top_candidates[i],
                context,
                model,
                validation_errors=analogy.quality_flags,
            )
            if retried is not None:
                retried = _post_process_analogy(retried)
                analogy = retried

        analogies.append(analogy)

    return analogies


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

    # Flatten: each domain can produce up to 2 analogies
    analogies = [a for domain_analogies in results for a in domain_analogies]
    return MiningResult(analogies=analogies)
