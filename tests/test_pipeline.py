"""Tests for the pipeline orchestrator."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from crossgen.models import (
    ProblemAnalysis,
    AbstractionResult,
    SAPPhIREAbstraction,
    BiologizeLens,
    WordTreeLens,
    TRIZLensResult,
    ExpansionResult,
    CandidateDomain,
    MiningResult,
    StructuralAnalogy,
    RelationalMapping,
    SynthesisResult,
    SynthesizedSolution,
    EvaluationResult,
    ScoredSolution,
)


def _mock_analysis():
    return ProblemAnalysis(
        original_problem="test problem",
        domain="computer science",
        primary_function="process data efficiently",
        sub_functions=["store", "retrieve"],
        constraints=["memory limited"],
        parameters=["cache size"],
        contradictions=[],
        key_verbs=["process", "store"],
    )


def _mock_abstractions():
    return AbstractionResult(
        sapphire=SAPPhIREAbstraction(
            effect="thermodynamic equilibrium",
            phenomenon="selective retention",
            action="eviction under pressure",
            parts=["cache", "memory"],
            abstraction_level="effect",
        ),
        biologize=BiologizeLens(
            nature_questions=["How does nature manage limited resources?"],
            inversions=["How does nature benefit from forgetting?"],
            biological_strategies=["synaptic pruning"],
        ),
        wordtree=WordTreeLens(expansions=[]),
        triz=TRIZLensResult(contradictions_mapped=[], principles_suggested=[]),
    )


def _mock_expansion():
    return ExpansionResult(
        candidate_domains=[
            CandidateDomain(
                domain="ecology",
                rationale="Resource management",
                source_lens="biologize",
                distance_from_home="high",
            ),
        ],
        excluded_home_domain="computer science",
    )


def _mock_analogy():
    return StructuralAnalogy(
        source_domain="ecology",
        mechanism="ecological succession",
        mappings=[
            RelationalMapping(
                source_element="pioneer species",
                target_element="initial cache entries",
                relation_type="functional",
            ),
        ],
        where_it_breaks="ecosystems operate on longer timescales",
        abstraction_level="phenomenon",
        systematicity_score=0.7,
    )


def _mock_solution():
    return SynthesizedSolution(
        source_domain="ecology",
        source_mechanism="ecological succession",
        concrete_approach="Implement staged cache where entries mature through phases",
        candidate_inferences=["Expect a climax state with stable composition"],
        transfer_strength="moderate",
        feasibility_notes="Interesting but needs validation",
    )


@pytest.mark.asyncio
async def test_pipeline_runs_all_stages():
    """Test that the pipeline calls all 6 stages in order."""
    with (
        patch("crossgen.pipeline.decompose", new_callable=AsyncMock) as mock_decompose,
        patch("crossgen.pipeline.abstract", new_callable=AsyncMock) as mock_abstract,
        patch("crossgen.pipeline.expand", new_callable=AsyncMock) as mock_expand,
        patch("crossgen.pipeline.mine", new_callable=AsyncMock) as mock_mine,
        patch("crossgen.pipeline.synthesize", new_callable=AsyncMock) as mock_synthesize,
        patch("crossgen.pipeline.evaluate", new_callable=AsyncMock) as mock_evaluate,
    ):
        analysis = _mock_analysis()
        abstractions = _mock_abstractions()
        expansion = _mock_expansion()
        mining = MiningResult(analogies=[_mock_analogy()])
        synthesis = SynthesisResult(solutions=[_mock_solution()])
        evaluation = EvaluationResult(
            scored_solutions=[
                ScoredSolution(
                    solution=_mock_solution(),
                    analogy=_mock_analogy(),
                    novelty=0.8,
                    feasibility=0.6,
                    structural_depth=0.7,
                    combined_score=0.71,
                    reasoning="test",
                )
            ],
            top_recommendation="ecology",
        )

        mock_decompose.return_value = analysis
        mock_abstract.return_value = abstractions
        mock_expand.return_value = expansion
        mock_mine.return_value = mining
        mock_synthesize.return_value = synthesis
        mock_evaluate.return_value = evaluation

        from crossgen.pipeline import run_pipeline
        result = await run_pipeline("test problem")

        assert result.problem == analysis
        assert result.abstractions == abstractions
        assert result.expansion == expansion
        assert result.mining == mining
        assert result.synthesis == synthesis
        assert result.evaluation == evaluation

        mock_decompose.assert_called_once()
        mock_abstract.assert_called_once()
        mock_expand.assert_called_once()
        mock_mine.assert_called_once()
        mock_synthesize.assert_called_once()
        mock_evaluate.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_streaming_yields_updates():
    """Test that streaming pipeline yields stage updates."""
    with (
        patch("crossgen.pipeline.decompose", new_callable=AsyncMock) as mock_decompose,
        patch("crossgen.pipeline.abstract", new_callable=AsyncMock) as mock_abstract,
        patch("crossgen.pipeline.expand", new_callable=AsyncMock) as mock_expand,
        patch("crossgen.pipeline.mine", new_callable=AsyncMock) as mock_mine,
        patch("crossgen.pipeline.synthesize", new_callable=AsyncMock) as mock_synthesize,
        patch("crossgen.pipeline.evaluate", new_callable=AsyncMock) as mock_evaluate,
    ):
        mock_decompose.return_value = _mock_analysis()
        mock_abstract.return_value = _mock_abstractions()
        mock_expand.return_value = _mock_expansion()
        mock_mine.return_value = MiningResult(analogies=[_mock_analogy()])
        mock_synthesize.return_value = SynthesisResult(solutions=[_mock_solution()])
        mock_evaluate.return_value = EvaluationResult(
            scored_solutions=[],
            top_recommendation="none",
        )

        from crossgen.pipeline import run_pipeline_streaming

        updates = []
        async for update in run_pipeline_streaming("test"):
            updates.append(update)

        # Should have running + done for each of 6 stages + complete
        assert len(updates) == 13  # 6 running + 6 done + 1 complete
        assert updates[-1]["stage"] == "complete"
