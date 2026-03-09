"""Async 6-stage pipeline orchestrator with quality gates and diagnostics."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

from .models import (
    AbstractionResult,
    CandidateDomain,
    EvaluationResult,
    ExpansionResult,
    MiningResult,
    PipelineResult,
    ProblemAnalysis,
    StructuralAnalogy,
    SynthesisResult,
)
from .stages.abstract import abstract
from .stages.decompose import decompose
from .stages.evaluate import evaluate
from .stages.expand import expand
from .stages.mine import mine, _mine_domain
from .stages.synthesize import synthesize

logger = logging.getLogger(__name__)


class PipelineStageError(Exception):
    """Raised when a pipeline stage fails a quality gate."""

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(f"[{stage}] {message}")


# ---------------------------------------------------------------------------
# Quality-gate helpers
# ---------------------------------------------------------------------------

async def _mine_quality_gate(
    mining_result: MiningResult,
    analysis: ProblemAnalysis,
    candidate_domains: list[CandidateDomain],
    abstractions: AbstractionResult | None,
    model: str | None,
    diagnostics: dict,
) -> MiningResult:
    """Check that mining produced >= 2 analogies; retry failed domains once."""
    # Determine which domains succeeded by matching source_domain names
    succeeded_domains = {a.source_domain for a in mining_result.analogies}
    failed_domains = [
        d for d in candidate_domains if d.domain not in succeeded_domains
    ]

    diagnostics["mine_failed_domains"] = [d.domain for d in failed_domains]
    diagnostics["mine_retried_domains"] = []
    diagnostics["mine_retry_results"] = {}

    if len(mining_result.analogies) >= 2:
        logger.info(
            "Mine quality gate passed: %d analogies from %d domains",
            len(mining_result.analogies),
            len(candidate_domains),
        )
        return mining_result

    # Not enough analogies — retry failed domains once
    if failed_domains:
        logger.warning(
            "Mine quality gate: only %d analogies (need >= 2). "
            "Retrying %d failed domains: %s",
            len(mining_result.analogies),
            len(failed_domains),
            [d.domain for d in failed_domains],
        )
        diagnostics["mine_retried_domains"] = [d.domain for d in failed_domains]

        retry_tasks = [
            _mine_domain(d, analysis, abstractions, model) for d in failed_domains
        ]
        retry_results = await asyncio.gather(*retry_tasks)

        for domain, result in zip(failed_domains, retry_results):
            if result:
                mining_result.analogies.extend(result)
                diagnostics["mine_retry_results"][domain.domain] = "success"
                logger.info("Retry succeeded for domain: %s", domain.domain)
            else:
                diagnostics["mine_retry_results"][domain.domain] = "failed"
                logger.warning("Retry also failed for domain: %s", domain.domain)

    # Final check after retry
    if len(mining_result.analogies) < 2:
        warning = (
            f"Mine quality gate: only {len(mining_result.analogies)} analogies "
            f"after retry (need >= 2)"
        )
        logger.warning(warning)
        diagnostics.setdefault("quality_warnings", []).append(warning)

    return mining_result


def _synthesize_quality_gate(
    synthesis: SynthesisResult,
    diagnostics: dict,
) -> None:
    """Check that synthesis produced >= 1 solution; log warning if not."""
    if len(synthesis.solutions) >= 1:
        logger.info(
            "Synthesize quality gate passed: %d solutions",
            len(synthesis.solutions),
        )
        return

    warning = "Synthesize quality gate: 0 solutions produced"
    logger.warning(warning)
    diagnostics.setdefault("quality_warnings", []).append(warning)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

async def run_pipeline(
    problem: str,
    *,
    model: str | None = None,
    on_stage: Any | None = None,
) -> PipelineResult:
    """Run the full 6-stage CrossGen pipeline.

    Args:
        problem: The problem statement to solve.
        model: LLM model override.
        on_stage: Optional async callback(stage_name, stage_number, data) for progress.
    """
    diagnostics: dict[str, Any] = {
        "mine_failed_domains": [],
        "mine_retried_domains": [],
        "mine_retry_results": {},
        "quality_warnings": [],
    }

    async def notify(stage: str, number: int, data: Any = None) -> None:
        if on_stage:
            if asyncio.iscoroutinefunction(on_stage):
                await on_stage(stage, number, data)
            else:
                on_stage(stage, number, data)

    # Stage 1: Decompose
    await notify("decompose", 1, {"status": "running"})
    analysis = await decompose(problem, model=model)
    await notify("decompose", 1, {"status": "done", "data": analysis.model_dump()})

    # Stage 2: Abstract (4 parallel lenses)
    await notify("abstract", 2, {"status": "running"})
    abstractions = await abstract(analysis, model=model)
    await notify("abstract", 2, {"status": "done", "data": abstractions.model_dump()})

    # Stage 3: Expand
    await notify("expand", 3, {"status": "running"})
    expansion = await expand(analysis, abstractions, model=model)
    await notify("expand", 3, {"status": "done", "data": expansion.model_dump()})

    # Stage 4: Mine (parallel per domain)
    await notify("mine", 4, {"status": "running"})
    mining_result = await mine(analysis, expansion.candidate_domains, model=model)

    # Quality gate: require >= 2 analogies, retry failed domains once
    mining_result = await _mine_quality_gate(
        mining_result, analysis, expansion.candidate_domains, abstractions, model,
        diagnostics,
    )
    await notify("mine", 4, {"status": "done", "data": mining_result.model_dump()})

    # Stage 5: Synthesize (parallel per analogy)
    await notify("synthesize", 5, {"status": "running"})
    synthesis = await synthesize(mining_result.analogies, analysis, model=model)

    # Quality gate: require >= 1 solution
    _synthesize_quality_gate(synthesis, diagnostics)
    await notify("synthesize", 5, {"status": "done", "data": synthesis.model_dump()})

    # Stage 6: Evaluate
    await notify("evaluate", 6, {"status": "running"})
    evaluation = await evaluate(
        synthesis.solutions, mining_result.analogies, analysis, model=model,
    )
    await notify("evaluate", 6, {"status": "done", "data": evaluation.model_dump()})

    return PipelineResult(
        problem=analysis,
        abstractions=abstractions,
        expansion=expansion,
        mining=mining_result,
        synthesis=synthesis,
        evaluation=evaluation,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# Streaming pipeline
# ---------------------------------------------------------------------------

async def run_pipeline_streaming(
    problem: str,
    *,
    model: str | None = None,
) -> AsyncGenerator[dict, None]:
    """Run the pipeline and yield stage updates as dicts for SSE streaming."""
    results: dict[str, Any] = {}
    diagnostics: dict[str, Any] = {
        "mine_failed_domains": [],
        "mine_retried_domains": [],
        "mine_retry_results": {},
        "quality_warnings": [],
    }

    # Stage 1
    yield {"stage": "decompose", "number": 1, "status": "running"}
    analysis = await decompose(problem, model=model)
    results["analysis"] = analysis
    yield {"stage": "decompose", "number": 1, "status": "done", "data": analysis.model_dump()}

    # Stage 2
    yield {"stage": "abstract", "number": 2, "status": "running"}
    abstractions = await abstract(analysis, model=model)
    results["abstractions"] = abstractions
    yield {"stage": "abstract", "number": 2, "status": "done", "data": abstractions.model_dump()}

    # Stage 3
    yield {"stage": "expand", "number": 3, "status": "running"}
    expansion = await expand(analysis, abstractions, model=model)
    results["expansion"] = expansion
    yield {"stage": "expand", "number": 3, "status": "done", "data": expansion.model_dump()}

    # Stage 4
    yield {"stage": "mine", "number": 4, "status": "running"}
    mining_result = await mine(analysis, expansion.candidate_domains, model=model)

    # Quality gate: require >= 2 analogies, retry failed domains once
    mining_result = await _mine_quality_gate(
        mining_result, analysis, expansion.candidate_domains, abstractions, model,
        diagnostics,
    )
    results["mining"] = mining_result
    yield {"stage": "mine", "number": 4, "status": "done", "data": mining_result.model_dump()}

    # Stage 5
    yield {"stage": "synthesize", "number": 5, "status": "running"}
    synthesis_result = await synthesize(mining_result.analogies, analysis, model=model)

    # Quality gate: require >= 1 solution
    _synthesize_quality_gate(synthesis_result, diagnostics)
    results["synthesis"] = synthesis_result
    yield {"stage": "synthesize", "number": 5, "status": "done", "data": synthesis_result.model_dump()}

    # Stage 6
    yield {"stage": "evaluate", "number": 6, "status": "running"}
    evaluation = await evaluate(
        synthesis_result.solutions, mining_result.analogies, analysis, model=model,
    )
    results["evaluation"] = evaluation
    yield {"stage": "evaluate", "number": 6, "status": "done", "data": evaluation.model_dump()}

    # Final result
    yield {
        "stage": "complete",
        "number": 7,
        "status": "done",
        "data": PipelineResult(
            problem=results["analysis"],
            abstractions=results["abstractions"],
            expansion=results["expansion"],
            mining=results["mining"],
            synthesis=results["synthesis"],
            evaluation=results["evaluation"],
            diagnostics=diagnostics,
        ).model_dump(),
    }
