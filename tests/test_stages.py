"""Tests for individual pipeline stages."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from crossgen.models import (
    ProblemAnalysis,
    Contradiction,
)
from crossgen.knowledge.triz import (
    lookup_principles,
    find_parameter,
    get_principle,
    INVENTIVE_PRINCIPLES,
    TRIZ_PARAMETERS,
)
from crossgen.knowledge.principles import (
    search_principles,
    UNIVERSAL_PRINCIPLES,
)
from crossgen.stages.abstract import _triz_lens


class TestTRIZLookup:
    """Test TRIZ deterministic matrix lookup (no LLM)."""

    def test_lookup_known_combination(self):
        """Speed vs Weight should return known principles."""
        results = lookup_principles(9, 1)
        assert len(results) > 0
        numbers = [r["number"] for r in results]
        assert 2 in numbers  # Extraction
        assert 28 in numbers  # Mechanics substitution

    def test_lookup_unknown_combination(self):
        """Unknown combination should return empty."""
        results = lookup_principles(99, 99)
        assert results == []

    def test_find_parameter_speed(self):
        matches = find_parameter("speed")
        assert any(p[0] == 9 for p in matches)

    def test_find_parameter_reliability(self):
        matches = find_parameter("reliability")
        assert any(p[0] == 27 for p in matches)

    def test_get_principle(self):
        p = get_principle(1)
        assert p is not None
        assert p["name"] == "Segmentation"

    def test_get_principle_invalid(self):
        assert get_principle(999) is None

    def test_all_40_principles_exist(self):
        assert len(INVENTIVE_PRINCIPLES) == 40
        for i in range(1, 41):
            assert i in INVENTIVE_PRINCIPLES

    def test_all_39_parameters_exist(self):
        assert len(TRIZ_PARAMETERS) == 39


class TestUniversalPrinciples:
    def test_search_feedback(self):
        results = search_principles("feedback")
        assert any(p.name == "Feedback loops" for p in results)

    def test_search_by_domain(self):
        results = search_principles("mycology")
        assert len(results) > 0

    def test_minimum_count(self):
        assert len(UNIVERSAL_PRINCIPLES) >= 30


class TestTRIZLens:
    """Test the TRIZ lens (Stage 2) — deterministic, no LLM."""

    def test_triz_lens_with_contradictions(self):
        analysis = ProblemAnalysis(
            original_problem="test",
            domain="computer science",
            primary_function="process fast",
            contradictions=[
                Contradiction(
                    improving="speed",
                    worsening="reliability",
                    description="Going faster reduces reliability",
                ),
            ],
            key_verbs=["process"],
        )
        result = _triz_lens(analysis)
        assert len(result.contradictions_mapped) == 1
        # Should find principles for speed vs reliability
        assert len(result.principles_suggested) > 0

    def test_triz_lens_no_contradictions(self):
        analysis = ProblemAnalysis(
            original_problem="test",
            domain="test",
            primary_function="test",
            contradictions=[],
            key_verbs=[],
        )
        result = _triz_lens(analysis)
        assert result.contradictions_mapped == []
        assert result.principles_suggested == []


class TestDecompose:
    @pytest.mark.asyncio
    async def test_decompose_calls_llm(self):
        mock_response = {
            "original_problem": "test problem",
            "domain": "computer science",
            "primary_function": "process data",
            "sub_functions": ["store"],
            "constraints": ["memory"],
            "parameters": ["size"],
            "contradictions": [],
            "key_verbs": ["process"],
        }
        with patch(
            "crossgen.stages.decompose.call_claude_json",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            from crossgen.stages.decompose import decompose
            result = await decompose("test problem")
            assert result.domain == "computer science"
            assert result.primary_function == "process data"


class TestAbstract:
    @pytest.mark.asyncio
    async def test_abstract_runs_4_lenses(self):
        analysis = ProblemAnalysis(
            original_problem="test",
            domain="CS",
            primary_function="cache data",
            sub_functions=["evict"],
            constraints=["memory limited"],
            contradictions=[
                Contradiction(
                    improving="speed",
                    worsening="reliability",
                    description="Faster caching is less reliable",
                ),
            ],
            key_verbs=["cache", "evict", "store"],
        )

        sapphire_resp = {
            "effect": "thermodynamic equilibrium",
            "phenomenon": "selective retention",
            "action": "eviction",
            "parts": ["cache", "memory"],
            "abstraction_level": "effect",
        }
        biologize_resp = {
            "nature_questions": ["How does nature manage limited memory?"],
            "inversions": ["How does nature benefit from forgetting?"],
            "biological_strategies": ["synaptic pruning"],
        }
        wordtree_resp = {
            "expansions": [
                {
                    "verb": "cache",
                    "hypernyms": ["store", "retain"],
                    "troponyms": ["buffer", "memoize"],
                    "cross_domain_terms": ["squirrel hoarding", "reservoir"],
                }
            ]
        }

        with patch(
            "crossgen.stages.abstract.call_claude_json",
            new_callable=AsyncMock,
            side_effect=[sapphire_resp, biologize_resp, wordtree_resp],
        ):
            from crossgen.stages.abstract import abstract
            result = await abstract(analysis)

            assert result.sapphire.effect == "thermodynamic equilibrium"
            assert len(result.biologize.nature_questions) > 0
            assert len(result.wordtree.expansions) > 0
            # TRIZ is deterministic — should have found principles
            assert len(result.triz.contradictions_mapped) == 1
