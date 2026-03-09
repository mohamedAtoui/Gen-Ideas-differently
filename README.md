# CrossGen: Cross-Domain Idea Generator

Give it a problem. It finds solutions from unrelated fields — not by keyword matching, but by mapping the *structure* of how things work across domains. A 6-stage pipeline that treats analogy as a rigorous transfer mechanism, not a creativity gimmick.

## The Pipeline

| # | Stage | What happens |
|---|-------|-------------|
| 1 | **Decompose** | Extracts functions, constraints, and contradictions from your problem |
| 2 | **Abstract** | 4 parallel lenses reframe it: SAPPhIRE, Biologize, WordTree, TRIZ |
| 3 | **Expand** | Identifies 6–8 high-distance candidate domains for analogical transfer |
| 4 | **Mine** | Finds structural analogies in each domain (relations, not surface features) |
| 5 | **Synthesize** | Converts analogies into concrete solutions with testable predictions |
| 6 | **Evaluate** | Scores on novelty, feasibility, structural depth, and actionability |

## What Makes It Interesting

- **4 parallel abstraction lenses** — SAPPhIRE (scientific principles), Biologize (biomimicry), WordTree (semantic expansion), and TRIZ (contradiction resolution) all run concurrently in Stage 2
- **Gentner's Structure-Mapping Theory enforced** — the Mining stage maps *relational* correspondences, not surface similarities. One-to-one mappings, systematic chains of relations, causal/functional/structural/constraint/process types
- **Hybrid deterministic + LLM** — TRIZ contradiction matrix and 40 inventive principles are looked up, not hallucinated. The LLM handles what it's good at: reasoning over structure
- **40 universal cross-domain principles + 42 curated domains** — feedback loops, phase transitions, self-organization, catalysis... each tagged with the domains where they appear
- **Mandatory "where it breaks" honesty** — every analogy must state where it fails. The prompt requires at least 3 specific weak spots. Solutions must address them
- **Testable predictions** — Stage 5 outputs Gentner's "candidate inferences": falsifiable predictions that emerge from the structural mapping, not just inspiration

## Quick Start

```bash
# Install
uv sync

# Solve a problem (CLI)
crossgen solve "How can we reduce hospital readmission rates?"

# JSON output
crossgen solve "How can we reduce hospital readmission rates?" --json

# Browse principles
crossgen principles list
crossgen principles search "feedback"

# Web UI with live streaming
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

## Tech Stack

Python 3.11+ · FastAPI · Typer · Rich · Pydantic v2 · SSE streaming via sse-starlette · LLM calls through Claude
