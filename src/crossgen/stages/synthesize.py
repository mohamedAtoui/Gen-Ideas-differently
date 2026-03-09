"""Stage 5: Synthesize — Generate concrete solutions from analogies (parallel)."""

from __future__ import annotations

import asyncio

from ..llm.client import call_claude_json
from ..llm.prompts import SYNTHESIZE_PROMPT
from ..models import (
    AnalogyEnrichment,
    EnrichmentResult,
    ProblemAnalysis,
    ResearchPointers,
    StructuralAnalogy,
    SynthesisResult,
    SynthesizedSolution,
)


async def _synthesize_analogy(
    analogy: StructuralAnalogy,
    analysis: ProblemAnalysis,
    enrichment: AnalogyEnrichment | None,
    model: str | None,
) -> SynthesizedSolution | None:
    """Synthesize a solution from a single analogy."""
    mappings_text = "\n".join(
        f"  {m.source_element} → {m.target_element} ({m.relation_type})"
        for m in analogy.mappings
    )

    # Build enrichment context if available
    enrichment_context = ""
    if enrichment and (enrichment.papers_found or enrichment.key_findings):
        parts = ["RESEARCH FINDINGS (from deep search):"]
        if enrichment.papers_found:
            parts.append("Papers found:")
            for p in enrichment.papers_found:
                parts.append(f"  - {p.title}: {p.relevance}")
        if enrichment.key_findings:
            parts.append("Key findings:")
            for f in enrichment.key_findings:
                parts.append(f"  - {f}")
        if enrichment.quantitative_data:
            parts.append("Quantitative data:")
            for d in enrichment.quantitative_data:
                parts.append(f"  - {d}")
        enrichment_context = "\n".join(parts)

    prompt = SYNTHESIZE_PROMPT.format(
        original_problem=analysis.elaborated_problem or analysis.original_problem,
        source_domain=analogy.source_domain,
        mechanism=analogy.mechanism,
        mappings_text=mappings_text,
        where_it_breaks=analogy.where_it_breaks,
        enrichment_context=enrichment_context,
    )

    kwargs = {}
    if model:
        kwargs["model"] = model

    try:
        data = await call_claude_json(
            prompt,
            system_prompt="You are an innovation engineer. Respond only with valid JSON.",
            **kwargs,
        )
        # Parse research_pointers if present
        rp_data = data.pop("research_pointers", None)
        if rp_data and isinstance(rp_data, dict):
            data["research_pointers"] = ResearchPointers(**rp_data)
        return SynthesizedSolution(**data)
    except Exception:
        return None


async def synthesize(
    analogies: list[StructuralAnalogy],
    analysis: ProblemAnalysis,
    *,
    enrichment: EnrichmentResult | None = None,
    model: str | None = None,
) -> SynthesisResult:
    """Synthesize concrete solutions from all analogies in parallel."""
    # Build enrichment lookup by source domain
    enrichment_map: dict[str, AnalogyEnrichment] = {}
    if enrichment:
        for e in enrichment.enrichments:
            enrichment_map[e.source_domain] = e

    tasks = [
        _synthesize_analogy(a, analysis, enrichment_map.get(a.source_domain), model)
        for a in analogies
    ]
    results = await asyncio.gather(*tasks)

    solutions = [r for r in results if r is not None]
    return SynthesisResult(solutions=solutions)
