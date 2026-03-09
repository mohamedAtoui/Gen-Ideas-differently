"""Tests for mapping analysis: systematicity computation and validation."""

from __future__ import annotations

from crossgen.mapping_analysis import compute_systematicity, validate_mappings
from crossgen.models import RelationalMapping, StructuralAnalogy


class TestComputeSystematicity:
    """Test systematicity computation on known graph structures."""

    def test_empty_mappings(self):
        assert compute_systematicity([]) == 0.0

    def test_single_mapping(self):
        mappings = [
            RelationalMapping(
                source_element="heart", target_element="pump", relation_type="causal"
            ),
        ]
        score = compute_systematicity(mappings)
        # Single mapping: connectivity=1.0 (trivial component), low quantity factor
        assert 0.0 < score < 1.0

    def test_connected_chain_scores_higher(self):
        """A connected chain (shared elements) should score higher than disconnected pairs."""
        # Connected: A→B, B→C (share element B)
        connected = [
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="A", target_element="Y", relation_type="process"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="functional"),
        ]
        # Disconnected: all different elements
        disconnected = [
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="structural"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="structural"),
        ]
        assert compute_systematicity(connected) > compute_systematicity(disconnected)

    def test_causal_relations_score_higher(self):
        """Causal/process relations should weight higher than structural."""
        causal = [
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="causal"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="process"),
        ]
        structural = [
            RelationalMapping(source_element="A", target_element="X", relation_type="structural"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="structural"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="structural"),
        ]
        assert compute_systematicity(causal) > compute_systematicity(structural)

    def test_more_connected_mappings_score_higher(self):
        """More connected mappings should increase score."""
        few_connected = [
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="A", target_element="Y", relation_type="process"),
        ]
        many_connected = [
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="A", target_element="Y", relation_type="process"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="Z", relation_type="functional"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="causal"),
        ]
        assert compute_systematicity(many_connected) > compute_systematicity(few_connected)

    def test_score_clamped_to_unit(self):
        """Score should always be in [0, 1]."""
        mappings = [
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="A", target_element="Y", relation_type="process"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="Z", relation_type="functional"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="causal"),
            RelationalMapping(source_element="C", target_element="W", relation_type="process"),
            RelationalMapping(source_element="D", target_element="W", relation_type="causal"),
        ]
        score = compute_systematicity(mappings)
        assert 0.0 <= score <= 1.0

    def test_ideal_mapping_scores_high(self):
        """7 causal mappings in a fully connected chain should score near 1.0."""
        # All share at least one element with another → fully connected
        mappings = [
            RelationalMapping(source_element="heart", target_element="pump", relation_type="causal"),
            RelationalMapping(source_element="heart", target_element="pressure", relation_type="process"),
            RelationalMapping(source_element="artery", target_element="pressure", relation_type="causal"),
            RelationalMapping(source_element="artery", target_element="pipe", relation_type="functional"),
            RelationalMapping(source_element="valve", target_element="pipe", relation_type="constraint"),
            RelationalMapping(source_element="valve", target_element="flow", relation_type="causal"),
            RelationalMapping(source_element="capillary", target_element="flow", relation_type="process"),
        ]
        score = compute_systematicity(mappings)
        assert score >= 0.7


class TestValidateMappings:
    """Test mapping validation against SMT constraints."""

    def _make_analogy(self, mappings: list[RelationalMapping]) -> StructuralAnalogy:
        return StructuralAnalogy(
            source_domain="test",
            mechanism="test mechanism",
            mappings=mappings,
            where_it_breaks="test",
            abstraction_level="effect",
            systematicity_score=0.5,
        )

    def test_no_mappings_flagged(self):
        analogy = self._make_analogy([])
        flags = validate_mappings(analogy)
        assert "no_mappings" in flags

    def test_too_few_mappings_flagged(self):
        analogy = self._make_analogy([
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="functional"),
        ])
        flags = validate_mappings(analogy)
        assert any("too_few_mappings" in f for f in flags)

    def test_one_to_one_violation_source(self):
        analogy = self._make_analogy([
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="A", target_element="Y", relation_type="functional"),
            RelationalMapping(source_element="B", target_element="Z", relation_type="structural"),
        ])
        flags = validate_mappings(analogy)
        assert any("one_to_one_violation_source" in f for f in flags)

    def test_one_to_one_violation_target(self):
        analogy = self._make_analogy([
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="X", relation_type="functional"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="structural"),
        ])
        flags = validate_mappings(analogy)
        assert any("one_to_one_violation_target" in f for f in flags)

    def test_low_relation_diversity(self):
        analogy = self._make_analogy([
            RelationalMapping(source_element="A", target_element="X", relation_type="structural"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="structural"),
            RelationalMapping(source_element="C", target_element="Z", relation_type="structural"),
        ])
        flags = validate_mappings(analogy)
        assert any("low_relation_diversity" in f for f in flags)

    def test_surface_matches_flagged(self):
        analogy = self._make_analogy([
            RelationalMapping(source_element="network", target_element="network", relation_type="structural"),
            RelationalMapping(source_element="A", target_element="X", relation_type="causal"),
            RelationalMapping(source_element="B", target_element="Y", relation_type="functional"),
        ])
        flags = validate_mappings(analogy)
        assert any("surface_matches" in f for f in flags)

    def test_good_mapping_no_flags(self):
        analogy = self._make_analogy([
            RelationalMapping(source_element="heart", target_element="pump", relation_type="causal"),
            RelationalMapping(source_element="artery", target_element="pipe", relation_type="structural"),
            RelationalMapping(source_element="valve", target_element="gate", relation_type="functional"),
        ])
        flags = validate_mappings(analogy)
        assert flags == []
