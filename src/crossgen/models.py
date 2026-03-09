"""Pydantic models for all pipeline stages."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Stage 1: Decompose ---

class Contradiction(BaseModel):
    improving: str = Field(description="Parameter being improved")
    worsening: str = Field(description="Parameter that degrades as a result")
    description: str = Field(description="Natural-language description of the trade-off")


class ProblemAnalysis(BaseModel):
    original_problem: str
    domain: str = Field(description="Home domain of the problem")
    primary_function: str = Field(description="Core function the solution must perform")
    sub_functions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    parameters: list[str] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    key_verbs: list[str] = Field(default_factory=list, description="Action verbs extracted from problem")
    elaborated_problem: str = Field(default="", description="Expanded description of the problem")
    operating_context: str = Field(default="", description="System/environment the problem operates in")
    current_state: str = Field(default="", description="How things work now")
    desired_outcome: str = Field(default="", description="What success looks like")
    analogical_hooks: list[str] = Field(default_factory=list, description="Aspects amenable to cross-domain metaphor")


# --- Stage 2: Abstract (4 lenses) ---

class SAPPhIREAbstraction(BaseModel):
    effect: str = Field(description="Underlying scientific effect/principle")
    phenomenon: str = Field(description="Observable phenomenon")
    action: str = Field(description="Action that causes the phenomenon")
    parts: list[str] = Field(default_factory=list, description="Physical/logical components involved")
    abstraction_level: str = Field(description="effect|phenomenon|action|parts")


class BiologizeLens(BaseModel):
    nature_questions: list[str] = Field(description="'How does nature...?' reframings")
    inversions: list[str] = Field(default_factory=list, description="Inverted framings")
    biological_strategies: list[str] = Field(default_factory=list)


class WordTreeExpansion(BaseModel):
    verb: str
    hypernyms: list[str] = Field(default_factory=list, description="More general terms")
    troponyms: list[str] = Field(default_factory=list, description="More specific manner-of terms")
    cross_domain_terms: list[str] = Field(default_factory=list, description="Terms that bridge domains")


class WordTreeLens(BaseModel):
    expansions: list[WordTreeExpansion] = Field(default_factory=list)


class TRIZLensResult(BaseModel):
    contradictions_mapped: list[dict] = Field(
        default_factory=list,
        description="Each contradiction mapped to TRIZ parameters"
    )
    principles_suggested: list[dict] = Field(
        default_factory=list,
        description="TRIZ principles from matrix lookup with descriptions"
    )


class AbstractionResult(BaseModel):
    sapphire: SAPPhIREAbstraction
    biologize: BiologizeLens
    wordtree: WordTreeLens
    triz: TRIZLensResult


# --- Stage 3: Expand ---

class CandidateDomain(BaseModel):
    domain: str
    rationale: str = Field(description="Why this domain is relevant")
    source_lens: str = Field(description="Which abstraction lens surfaced this domain")
    distance_from_home: str = Field(description="low|medium|high")


class ExpansionResult(BaseModel):
    candidate_domains: list[CandidateDomain] = Field(default_factory=list)
    excluded_home_domain: str = Field(description="The problem's home domain, explicitly excluded")


# --- Stage 4: Mine ---

class RelationalMapping(BaseModel):
    source_element: str = Field(description="Element in the source domain")
    target_element: str = Field(description="Corresponding element in the problem domain")
    relation_type: str = Field(description="Type of relational correspondence")


class StructuralAnalogy(BaseModel):
    source_domain: str
    mechanism: str = Field(description="Specific mechanism/phenomenon from the source domain")
    mappings: list[RelationalMapping] = Field(default_factory=list)
    where_it_breaks: str = Field(description="Where the analogy fails — honesty improves quality")
    abstraction_level: str = Field(description="SAPPhIRE level: effect|phenomenon|action|parts")
    systematicity_score: float = Field(ge=0, le=1, description="Higher = more relational correspondences")


class MiningResult(BaseModel):
    analogies: list[StructuralAnalogy] = Field(default_factory=list)


# --- Stage 5: Synthesize ---

class ResearchPointers(BaseModel):
    academic_searches: list[str] = Field(default_factory=list, description="Google Scholar queries")
    key_terms: list[str] = Field(default_factory=list, description="Technical terms to search in both domains")
    seminal_works: list[str] = Field(default_factory=list, description="Known relevant papers/books")


class SynthesizedSolution(BaseModel):
    source_domain: str
    source_mechanism: str
    concrete_approach: str = Field(description="How to apply this in the problem domain")
    candidate_inferences: list[str] = Field(
        default_factory=list,
        description="What the source predicts about the target that isn't obvious"
    )
    key_predictions: list[str] = Field(
        default_factory=list,
        description="Testable, falsifiable predictions from the analogy"
    )
    transfer_strength: str = Field(description="strong|moderate|weak")
    feasibility_notes: str = ""
    research_pointers: ResearchPointers | None = None


class SynthesisResult(BaseModel):
    solutions: list[SynthesizedSolution] = Field(default_factory=list)


# --- Stage 6: Evaluate ---

class ScoredSolution(BaseModel):
    solution: SynthesizedSolution
    analogy: StructuralAnalogy
    novelty: float = Field(ge=0, le=1)
    feasibility: float = Field(ge=0, le=1)
    structural_depth: float = Field(ge=0, le=1)
    actionability: float = Field(default=0.5, ge=0, le=1)
    combined_score: float = Field(ge=0, le=1)
    same_domain_penalty: bool = False
    reasoning: str = ""


class EvaluationResult(BaseModel):
    scored_solutions: list[ScoredSolution] = Field(default_factory=list)
    top_recommendation: str = ""


# --- Research Enrichment (deep mode) ---

class PaperReference(BaseModel):
    title: str = ""
    relevance: str = Field(default="", description="Why this paper is relevant to the analogy")
    url: str = ""


class AnalogyEnrichment(BaseModel):
    source_domain: str
    papers_found: list[PaperReference] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list, description="Key findings from research")
    quantitative_data: list[str] = Field(default_factory=list, description="Data points from source domain")


class EnrichmentResult(BaseModel):
    enrichments: list[AnalogyEnrichment] = Field(default_factory=list)


# --- Pipeline ---

class PipelineResult(BaseModel):
    problem: ProblemAnalysis
    abstractions: AbstractionResult
    expansion: ExpansionResult
    mining: MiningResult
    enrichment: EnrichmentResult | None = None
    synthesis: SynthesisResult
    evaluation: EvaluationResult
