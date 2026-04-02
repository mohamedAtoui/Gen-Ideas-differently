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
    preferred_categories: list[str] | None = None,
) -> ExpansionResult:
    """Identify 6-8 candidate domains using all abstraction lens outputs.

    Parameters
    ----------
    preferred_categories:
        If provided, bias domain expansion toward these categories
        (e.g. ``["physics", "engineering", "math"]``).  Overrides the
        default requirement for biology/arts/earth science diversity.
    """

    # Collect cross-domain terms from WordTree
    cross_domain_terms = []
    for exp in abstractions.wordtree.expansions:
        cross_domain_terms.extend(exp.cross_domain_terms)

    # Collect nature questions from Biologize (if available)
    nature_questions = abstractions.biologize.nature_questions if abstractions.biologize else []

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

    # Build domain diversity rules based on preferences
    if preferred_categories:
        cats = ", ".join(preferred_categories)
        diversity_rules = (
            f"- STRONGLY PREFER domains from these categories: {cats}. "
            f"At least 5 of the 8 candidates should come from these categories.\n"
            f"- You MAY include 1-2 domains from other categories if they offer genuinely strong structural analogies.\n"
            f"- Do NOT force biology/ecology domains unless they are clearly the best fit."
        )
    else:
        diversity_rules = (
            "- Include at least 2 domains from biology/ecology (mycology, immunology, marine biology, entomology...)\n"
            "- Include at least 1 domain from arts/humanities (music theory, choreography, linguistics...)\n"
            "- Include at least 1 domain from earth/physical sciences"
        )

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
        diversity_rules=diversity_rules,
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
