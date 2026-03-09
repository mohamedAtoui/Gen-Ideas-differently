"""Tests for scoring and evaluation logic."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from crossgen.models import (
    ProblemAnalysis,
    StructuralAnalogy,
    RelationalMapping,
    SynthesizedSolution,
    ScoredSolution,
)
from crossgen.stages.evaluate import (
    _domain_distance,
    _abstraction_bonus,
    evaluate,
)


class TestDomainDistance:
    def test_same_domain(self):
        assert _domain_distance("computer science", "computer science") == 0.0

    def test_same_category(self):
        # Both in "biology" category (from DOMAIN_CATALOG)
        d = _domain_distance("immunology", "mycology")
        assert d == 0.3

    def test_different_category(self):
        d = _domain_distance("computer science", "ecology")
        assert d == 0.8

    def test_case_insensitive(self):
        assert _domain_distance("Computer Science", "computer science") == 0.0


class TestAbstractionBonus:
    def test_effect_highest(self):
        assert _abstraction_bonus("effect") == 0.2

    def test_parts_lowest(self):
        assert _abstraction_bonus("parts") == 0.0

    def test_unknown_gets_default(self):
        assert _abstraction_bonus("unknown") == 0.1


class TestEvaluation:
    @pytest.mark.asyncio
    async def test_same_domain_penalty(self):
        """Solutions from the same domain should be penalized."""
        analysis = ProblemAnalysis(
            original_problem="test",
            domain="computer science",
            primary_function="test",
            key_verbs=[],
        )
        analogy = StructuralAnalogy(
            source_domain="computer science",
            mechanism="some CS mechanism",
            mappings=[
                RelationalMapping(
                    source_element="a",
                    target_element="b",
                    relation_type="functional",
                ),
            ],
            where_it_breaks="trivial",
            abstraction_level="parts",
            systematicity_score=0.5,
        )
        solution = SynthesizedSolution(
            source_domain="computer science",
            source_mechanism="some CS mechanism",
            concrete_approach="do the obvious thing",
            candidate_inferences=["nothing surprising"],
            transfer_strength="strong",
        )

        # Use heuristic fallback by making LLM call fail
        with patch(
            "crossgen.stages.evaluate.call_claude_json",
            new_callable=AsyncMock,
            side_effect=Exception("LLM unavailable"),
        ):
            result = await evaluate([solution], [analogy], analysis)
            assert len(result.scored_solutions) == 1
            assert result.scored_solutions[0].same_domain_penalty is True

    @pytest.mark.asyncio
    async def test_scoring_formula(self):
        """Test the combined score formula: 0.30*novelty + 0.25*feasibility + 0.25*depth + 0.20*actionability."""
        analysis = ProblemAnalysis(
            original_problem="test",
            domain="computer science",
            primary_function="test",
            key_verbs=[],
        )
        analogy = StructuralAnalogy(
            source_domain="ecology",
            mechanism="ecological succession",
            mappings=[
                RelationalMapping(
                    source_element="a", target_element="b", relation_type="functional",
                ),
            ],
            where_it_breaks="timescales differ",
            abstraction_level="effect",
            systematicity_score=0.8,
        )
        solution = SynthesizedSolution(
            source_domain="ecology",
            source_mechanism="ecological succession",
            concrete_approach="staged processing",
            candidate_inferences=["climax state"],
            transfer_strength="moderate",
        )

        with patch(
            "crossgen.stages.evaluate.call_claude_json",
            new_callable=AsyncMock,
            return_value={
                "novelty": 0.8,
                "feasibility": 0.6,
                "structural_depth": 0.7,
                "actionability": 0.5,
                "reasoning": "good cross-domain transfer",
            },
        ):
            result = await evaluate([solution], [analogy], analysis)
            scored = result.scored_solutions[0]
            expected = round(0.30 * 0.8 + 0.25 * 0.6 + 0.25 * 0.7 + 0.20 * 0.5, 2)
            assert scored.combined_score == expected
            assert scored.same_domain_penalty is False

    @pytest.mark.asyncio
    async def test_solutions_ranked_by_score(self):
        """Higher-scored solutions should come first."""
        analysis = ProblemAnalysis(
            original_problem="test",
            domain="CS",
            primary_function="test",
            key_verbs=[],
        )

        def make_pair(domain, novelty):
            analogy = StructuralAnalogy(
                source_domain=domain,
                mechanism=f"{domain} mechanism",
                mappings=[
                    RelationalMapping(source_element="a", target_element="b", relation_type="functional"),
                ],
                where_it_breaks="somewhere",
                abstraction_level="effect",
                systematicity_score=0.7,
            )
            solution = SynthesizedSolution(
                source_domain=domain,
                source_mechanism=f"{domain} mechanism",
                concrete_approach="approach",
                candidate_inferences=["inference"],
                transfer_strength="moderate",
            )
            return analogy, solution

        a1, s1 = make_pair("ecology", 0.9)
        a2, s2 = make_pair("music theory", 0.5)

        # Return different novelty scores for different domains
        async def mock_llm(*args, **kwargs):
            prompt = args[0]
            if "ecology" in prompt:
                return {"novelty": 0.9, "feasibility": 0.7, "structural_depth": 0.8, "reasoning": "great"}
            return {"novelty": 0.5, "feasibility": 0.5, "structural_depth": 0.5, "reasoning": "ok"}

        with patch(
            "crossgen.stages.evaluate.call_claude_json",
            new_callable=AsyncMock,
            side_effect=mock_llm,
        ):
            result = await evaluate([s1, s2], [a1, a2], analysis)
            assert len(result.scored_solutions) == 2
            assert result.scored_solutions[0].combined_score >= result.scored_solutions[1].combined_score
