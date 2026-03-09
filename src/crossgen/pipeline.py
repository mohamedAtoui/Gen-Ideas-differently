"""Async 6-stage pipeline orchestrator."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from .models import (
    AbstractionResult,
    EvaluationResult,
    ExpansionResult,
    MiningResult,
    PipelineResult,
    ProblemAnalysis,
    SynthesisResult,
)
from .stages.abstract import abstract
from .stages.decompose import decompose
from .stages.evaluate import evaluate
from .stages.expand import expand
from .stages.mine import mine
from .stages.synthesize import synthesize


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
    await notify("mine", 4, {"status": "done", "data": mining_result.model_dump()})

    # Stage 5: Synthesize (parallel per analogy)
    await notify("synthesize", 5, {"status": "running"})
    synthesis = await synthesize(mining_result.analogies, analysis, model=model)
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
    )


async def run_pipeline_streaming(
    problem: str,
    *,
    model: str | None = None,
) -> AsyncGenerator[dict, None]:
    """Run the pipeline and yield stage updates as dicts for SSE streaming."""
    results: dict[str, Any] = {}

    stages = [
        ("decompose", 1),
        ("abstract", 2),
        ("expand", 3),
        ("mine", 4),
        ("synthesize", 5),
        ("evaluate", 6),
    ]

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
    results["mining"] = mining_result
    yield {"stage": "mine", "number": 4, "status": "done", "data": mining_result.model_dump()}

    # Stage 5
    yield {"stage": "synthesize", "number": 5, "status": "running"}
    synthesis_result = await synthesize(mining_result.analogies, analysis, model=model)
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
        ).model_dump(),
    }
