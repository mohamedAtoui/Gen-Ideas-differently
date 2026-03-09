"""Stage 2: Abstract — 4 parallel abstraction lenses."""

from __future__ import annotations

import asyncio
import json

from ..knowledge.triz import INVENTIVE_PRINCIPLES, find_parameter, lookup_principles
from ..llm.client import call_claude_json
from ..llm.prompts import BIOLOGIZE_PROMPT, SAPPHIRE_PROMPT, WORDTREE_PROMPT, TRIZ_FALLBACK_PROMPT
from ..models import (
    AbstractionResult,
    BiologizeLens,
    ProblemAnalysis,
    SAPPhIREAbstraction,
    TRIZLensResult,
    WordTreeLens,
)


async def _sapphire_lens(analysis: ProblemAnalysis, model: str | None) -> SAPPhIREAbstraction:
    prompt = SAPPHIRE_PROMPT.format(
        primary_function=analysis.primary_function,
        elaborated_problem=analysis.elaborated_problem or analysis.original_problem,
        sub_functions=", ".join(analysis.sub_functions),
        constraints=", ".join(analysis.constraints),
    )
    kwargs = {}
    if model:
        kwargs["model"] = model
    data = await call_claude_json(
        prompt,
        system_prompt="You are a scientist. Respond only with valid JSON.",
        **kwargs,
    )
    return SAPPhIREAbstraction(**data)


async def _biologize_lens(analysis: ProblemAnalysis, model: str | None) -> BiologizeLens:
    prompt = BIOLOGIZE_PROMPT.format(
        primary_function=analysis.primary_function,
        elaborated_problem=analysis.elaborated_problem or analysis.original_problem,
        constraints=", ".join(analysis.constraints),
        key_verbs=", ".join(analysis.key_verbs),
    )
    kwargs = {}
    if model:
        kwargs["model"] = model
    data = await call_claude_json(
        prompt,
        system_prompt="You are a biomimicry expert. Respond only with valid JSON.",
        **kwargs,
    )
    return BiologizeLens(**data)


async def _wordtree_lens(analysis: ProblemAnalysis, model: str | None) -> WordTreeLens:
    prompt = WORDTREE_PROMPT.format(
        key_verbs=", ".join(analysis.key_verbs),
        domain=analysis.domain,
    )
    kwargs = {}
    if model:
        kwargs["model"] = model
    data = await call_claude_json(
        prompt,
        system_prompt="You are a computational linguist. Respond only with valid JSON.",
        **kwargs,
    )
    return WordTreeLens(**data)


async def _triz_lens(analysis: ProblemAnalysis, model: str | None) -> TRIZLensResult:
    """TRIZ matrix lookup with LLM fallback when deterministic lookup finds nothing."""
    contradictions_mapped = []
    all_principles: dict[int, dict] = {}

    for contradiction in analysis.contradictions:
        improving_matches = find_parameter(contradiction.improving)
        worsening_matches = find_parameter(contradiction.worsening)

        mapping = {
            "contradiction": contradiction.description,
            "improving_param": contradiction.improving,
            "worsening_param": contradiction.worsening,
            "triz_improving": [(p[0], p[1]) for p in improving_matches[:3]],
            "triz_worsening": [(p[0], p[1]) for p in worsening_matches[:3]],
            "principles_found": [],
        }

        # Try all combinations of matched parameters
        for imp_id, _ in improving_matches[:3]:
            for wor_id, _ in worsening_matches[:3]:
                principles = lookup_principles(imp_id, wor_id)
                if principles:
                    mapping["principles_found"].extend(
                        [{"from": (imp_id, wor_id), "principles": [p["number"] for p in principles]}]
                    )
                    for p in principles:
                        all_principles[p["number"]] = p

        contradictions_mapped.append(mapping)

    # LLM fallback if no principles found deterministically
    if not all_principles and analysis.contradictions:
        try:
            contradictions_text = "\n".join(
                f"- Improving '{c.improving}' worsens '{c.worsening}': {c.description}"
                for c in analysis.contradictions
            )
            principles_list = "\n".join(
                f"  {num}. {p['name']}: {p['description']}"
                for num, p in sorted(INVENTIVE_PRINCIPLES.items())
            )
            prompt = TRIZ_FALLBACK_PROMPT.format(
                contradictions=contradictions_text,
                principles_list=principles_list,
            )
            kwargs = {}
            if model:
                kwargs["model"] = model
            data = await call_claude_json(
                prompt,
                system_prompt="You are a TRIZ expert. Respond only with valid JSON.",
                **kwargs,
            )
            for p_info in data.get("principles", []):
                num = p_info.get("number")
                if num and num in INVENTIVE_PRINCIPLES:
                    all_principles[num] = {"number": num, **INVENTIVE_PRINCIPLES[num]}
        except Exception:
            pass  # Fallback failed, proceed with empty principles

    return TRIZLensResult(
        contradictions_mapped=contradictions_mapped,
        principles_suggested=list(all_principles.values()),
    )


async def abstract(analysis: ProblemAnalysis, *, model: str | None = None) -> AbstractionResult:
    """Run all 4 abstraction lenses in parallel.

    All 4 lenses run as concurrent async calls (TRIZ now includes LLM fallback).
    """
    sapphire, biologize, wordtree, triz_result = await asyncio.gather(
        _sapphire_lens(analysis, model),
        _biologize_lens(analysis, model),
        _wordtree_lens(analysis, model),
        _triz_lens(analysis, model),
    )

    return AbstractionResult(
        sapphire=sapphire,
        biologize=biologize,
        wordtree=wordtree,
        triz=triz_result,
    )
