"""Stage 3: Expand — Identify candidate domains for analogical transfer."""

from __future__ import annotations

import json

from ..knowledge.domains import get_all_domain_names
from ..knowledge.principles import search_principles
from ..llm.client import call_claude_json
from ..llm.prompts import EXPAND_PROMPT
from ..models import AbstractionResult, ExpansionResult, ProblemAnalysis


async def expand(
    analysis: ProblemAnalysis,
    abstractions: AbstractionResult,
    *,
    model: str | None = None,
) -> ExpansionResult:
    """Identify 6-8 candidate domains using all abstraction lens outputs."""

    # Collect cross-domain terms from WordTree
    cross_domain_terms = []
    for exp in abstractions.wordtree.expansions:
        cross_domain_terms.extend(exp.cross_domain_terms)

    # Collect nature questions from Biologize
    nature_questions = abstractions.biologize.nature_questions

    # Collect TRIZ principles
    triz_principles = [
        f"{p.get('number', '?')}: {p.get('name', '?')} — {p.get('description', '?')}"
        for p in abstractions.triz.principles_suggested
    ]

    # Search universal principles for matches
    search_terms = [analysis.primary_function] + analysis.key_verbs
    matched_principles = set()
    for term in search_terms:
        for p in search_principles(term):
            matched_principles.add(f"{p.name}: {p.description} (domains: {', '.join(p.domains)})")

    # Get curated domain catalog (excluding home domain)
    domain_catalog = get_all_domain_names(exclude=analysis.domain)

    prompt = EXPAND_PROMPT.format(
        home_domain=analysis.domain,
        primary_function=analysis.primary_function,
        analogical_hooks=json.dumps(analysis.analogical_hooks) if analysis.analogical_hooks else "None identified",
        sapphire_effect=abstractions.sapphire.effect,
        sapphire_phenomenon=abstractions.sapphire.phenomenon,
        nature_questions=json.dumps(nature_questions),
        cross_domain_terms=json.dumps(cross_domain_terms),
        triz_principles=json.dumps(triz_principles) if triz_principles else "None found",
        universal_principles=json.dumps(list(matched_principles)) if matched_principles else "None matched",
        domain_catalog=", ".join(domain_catalog),
    )

    kwargs = {}
    if model:
        kwargs["model"] = model

    data = await call_claude_json(
        prompt,
        system_prompt="You are a cross-domain innovation researcher. Respond only with valid JSON.",
        **kwargs,
    )
    return ExpansionResult(**data)
