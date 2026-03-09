"""Mapping analysis: systematicity computation and mapping validation.

Implements Gentner's Structure-Mapping Theory constraints as computable metrics
rather than relying on LLM self-assessment.

Literature:
- Gentner (1983) — systematicity principle
- Forbus, Gentner, Law (1995) — MAC/FAC model
"""

from __future__ import annotations

from collections import defaultdict

from .models import RelationalMapping, StructuralAnalogy


# Relation types ordered by structural importance (causal/process > structural > other)
_RELATION_WEIGHTS: dict[str, float] = {
    "causal": 1.0,
    "process": 0.9,
    "functional": 0.7,
    "constraint": 0.6,
    "structural": 0.5,
}

_DEFAULT_RELATION_WEIGHT = 0.3


def compute_systematicity(mappings: list[RelationalMapping]) -> float:
    """Compute systematicity score from mapping graph structure.

    Systematicity = (largest connected component / total nodes) × relation-type weighting.

    Nodes are element pairs (source, target). Two nodes share an edge if they
    have a common element, forming a causal/relational chain.

    Returns a float in [0, 1].
    """
    if not mappings:
        return 0.0

    # Build adjacency graph: nodes are mapping indices
    n = len(mappings)
    adj: dict[int, set[int]] = defaultdict(set)

    # Two mappings are connected if they share a source or target element
    # (indicating a chain of relations through shared entities)
    for i in range(n):
        for j in range(i + 1, n):
            mi, mj = mappings[i], mappings[j]
            if (
                mi.source_element.lower() == mj.source_element.lower()
                or mi.target_element.lower() == mj.target_element.lower()
                or mi.source_element.lower() == mj.target_element.lower()
                or mi.target_element.lower() == mj.source_element.lower()
            ):
                adj[i].add(j)
                adj[j].add(i)

    # Find largest connected component via BFS
    visited: set[int] = set()
    largest_component = 0

    for start in range(n):
        if start in visited:
            continue
        component: set[int] = set()
        queue = [start]
        while queue:
            node = queue.pop()
            if node in component:
                continue
            component.add(node)
            visited.add(node)
            queue.extend(adj[node] - component)
        largest_component = max(largest_component, len(component))

    # Connectivity ratio
    connectivity = largest_component / n if n > 0 else 0.0

    # Relation-type weighting: average weight of all mappings
    total_weight = sum(
        _RELATION_WEIGHTS.get(m.relation_type.lower(), _DEFAULT_RELATION_WEIGHT)
        for m in mappings
    )
    avg_weight = total_weight / n

    # Final score: connectivity × relation quality, clamped to [0, 1]
    score = connectivity * avg_weight

    # Bonus for having more mappings (diminishing returns, caps at ~7)
    quantity_factor = min(1.0, n / 7.0)
    score = score * 0.7 + quantity_factor * 0.3

    return round(min(1.0, max(0.0, score)), 3)


def validate_mappings(analogy: StructuralAnalogy) -> list[str]:
    """Validate mappings against Structure-Mapping Theory constraints.

    Returns a list of quality flag strings (empty = all good).

    Checks:
    (a) One-to-one constraint: each source/target element appears at most once
    (b) Minimum mapping count (at least 3)
    (c) Relation type diversity (at least 2 different relation_types)
    (d) Surface match detection: flag lexically-identical source/target pairs
    """
    flags: list[str] = []
    mappings = analogy.mappings

    if not mappings:
        flags.append("no_mappings")
        return flags

    # (a) One-to-one constraint
    source_elements = [m.source_element.lower().strip() for m in mappings]
    target_elements = [m.target_element.lower().strip() for m in mappings]

    source_dupes = [e for e in set(source_elements) if source_elements.count(e) > 1]
    target_dupes = [e for e in set(target_elements) if target_elements.count(e) > 1]

    if source_dupes:
        flags.append(f"one_to_one_violation_source: {', '.join(source_dupes)}")
    if target_dupes:
        flags.append(f"one_to_one_violation_target: {', '.join(target_dupes)}")

    # (b) Minimum mapping count
    if len(mappings) < 3:
        flags.append(f"too_few_mappings: {len(mappings)} (minimum 3)")

    # (c) Relation type diversity
    relation_types = {m.relation_type.lower().strip() for m in mappings}
    if len(relation_types) < 2:
        flags.append(f"low_relation_diversity: only '{next(iter(relation_types))}'")

    # (d) Surface match detection (lexically identical pairs)
    surface_matches = []
    for m in mappings:
        src = m.source_element.lower().strip()
        tgt = m.target_element.lower().strip()
        if src == tgt:
            surface_matches.append(src)
    if surface_matches:
        flags.append(f"surface_matches: {', '.join(surface_matches)}")

    return flags
