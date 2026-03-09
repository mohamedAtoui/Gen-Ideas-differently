"""All prompt templates for the CrossGen pipeline.

Centralized prompt management — every LLM call uses a template from here.
"""

from __future__ import annotations

# --- Stage 1: Decompose ---

DECOMPOSE_PROMPT = """\
You are a systems analyst specializing in functional decomposition.

Analyze the following problem and extract its structural components.

PROBLEM: {problem}

First, ELABORATE the problem — expand the terse statement into a rich description. Then decompose.

Respond with ONLY valid JSON (no markdown, no explanation) in this exact format:
{{
  "original_problem": "<the problem as stated>",
  "elaborated_problem": "<2-3 sentence expansion: what is the real challenge here, what makes it hard, what are the key tensions>",
  "domain": "<the primary domain this problem belongs to, e.g. 'computer science', 'mechanical engineering'>",
  "operating_context": "<what system/environment does this operate in>",
  "current_state": "<how things work now — the baseline>",
  "desired_outcome": "<what success looks like>",
  "primary_function": "<the core function the solution must perform, stated in domain-neutral terms>",
  "sub_functions": ["<supporting functions needed>"],
  "constraints": ["<limitations, requirements, boundary conditions>"],
  "parameters": ["<key parameters that can be tuned>"],
  "contradictions": [
    {{
      "improving": "<parameter being improved — use physical/engineering terms>",
      "worsening": "<parameter that degrades — use physical/engineering terms>",
      "description": "<natural language description of the trade-off>"
    }}
  ],
  "key_verbs": ["<action verbs extracted from the problem description>"],
  "analogical_hooks": ["<2-3 aspects of this problem most amenable to cross-domain metaphor>"]
}}

IMPORTANT:
- State functions in domain-neutral terms (e.g., "selectively retain under capacity constraint" not "implement LRU cache")
- Identify at least 3 contradictions (trade-offs) — these are critical for cross-domain transfer
- For contradiction parameters, use PHYSICAL/ENGINEERING vocabulary that maps to general concepts:
  Use terms like: speed, capacity, volume, memory, throughput, latency, accuracy, precision,
  reliability, complexity, energy, overhead, adaptability, productivity, information loss,
  time loss, stability, ease of operation, ease of repair, flexibility
  NOT domain-specific jargon (e.g., use "capacity" not "KV-cache size", "speed" not "attention latency")
- Extract 3-5 key action verbs that capture what the system does
- "analogical_hooks" should identify what aspects of this problem have interesting parallels in other fields
  (e.g., "the trade-off between storing everything and forgetting" is a hook that connects to neuroscience, ecology, library science)
"""

# --- Stage 2: Abstract (4 lenses) ---

SAPPHIRE_PROMPT = """\
You are a scientist applying the SAPPhIRE abstraction framework.

Given this problem analysis, identify the underlying scientific principles at play.

PROBLEM: {primary_function}
ELABORATED CONTEXT: {elaborated_problem}
SUB-FUNCTIONS: {sub_functions}
CONSTRAINTS: {constraints}

SAPPhIRE hierarchy (from most abstract to most concrete):
- Effect: The underlying scientific principle (e.g., thermodynamic equilibrium, natural selection, wave interference)
- Phenomenon: The observable behavior that results from the effect
- Action: The action/process that causes the phenomenon
- Parts: The physical or logical components involved

Respond with ONLY valid JSON:
{{
  "effect": "<the deepest scientific principle — this is where the most novel cross-domain connections live>",
  "phenomenon": "<the observable behavior>",
  "action": "<the action that produces the phenomenon>",
  "parts": ["<components involved>"],
  "abstraction_level": "effect"
}}

IMPORTANT:
- Go DEEP to the scientific principle level. "Caching" → "selective retention under resource constraint" → "thermodynamic free energy minimization"
- The Effect should be expressible in domain-neutral scientific language
- Think about what PHYSICAL or MATHEMATICAL principle underlies the problem
- Consider principles from: thermodynamics, information theory, evolutionary biology, control theory, statistical mechanics
"""

BIOLOGIZE_PROMPT = """\
You are a biomimicry expert. Your task is to "biologize" a technical problem — reframe it as questions nature has already solved.

PROBLEM: {primary_function}
ELABORATED CONTEXT: {elaborated_problem}
CONSTRAINTS: {constraints}
KEY VERBS: {key_verbs}

Generate multiple "How does nature...?" questions AND their inversions.

Respond with ONLY valid JSON:
{{
  "nature_questions": [
    "How does nature <reframing 1>?",
    "How does nature <reframing 2>?",
    "How does nature <reframing 3>?",
    "How does nature <reframing 4>?",
    "How does nature <reframing 5>?",
    "How does nature <reframing 6>?"
  ],
  "inversions": [
    "How does nature AVOID <inverse problem>?",
    "How does nature BENEFIT FROM <the constraint itself>?",
    "How does nature TURN <the limitation> INTO an advantage?"
  ],
  "biological_strategies": [
    "<known biological strategy 1 that addresses this — be specific, name the organism and mechanism>",
    "<known biological strategy 2>",
    "<known biological strategy 3>",
    "<known biological strategy 4>"
  ]
}}

IMPORTANT:
- Generate at least 6 nature questions with DIFFERENT framings — vary the level of abstraction
- Include at least 3 inversions (sometimes the inverse is more productive)
- For biological_strategies, cite REAL biological mechanisms with specific organisms (not made up)
- Think beyond obvious parallels — consider organisms in extreme environments, symbiotic relationships, developmental biology
"""

WORDTREE_PROMPT = """\
You are a computational linguist specializing in semantic relationships.

For each key verb, expand it into a WordTree of hypernyms (more general) and troponyms (more specific manner-of).
The goal is to find cross-domain search terms — words that mean similar things but are used in different fields.

KEY VERBS: {key_verbs}
HOME DOMAIN: {domain}

Respond with ONLY valid JSON:
{{
  "expansions": [
    {{
      "verb": "<original verb>",
      "hypernyms": ["<more general terms — e.g., 'filter' → 'select', 'discriminate', 'sort'>"],
      "troponyms": ["<more specific terms — e.g., 'filter' → 'sieve', 'screen', 'distill', 'curate'>"],
      "cross_domain_terms": ["<terms that bridge to other domains — e.g., 'filter' connects fluid dynamics, signal processing, social curation>"]
    }}
  ]
}}

IMPORTANT:
- For each verb, aim for 3-5 hypernyms, 3-5 troponyms, and 3-5 cross-domain terms
- Cross-domain terms should explicitly suggest domains OUTSIDE {domain}
- Think about how the same action is described in biology, physics, economics, art, cooking, military, etc.
"""

# --- Stage 3: Expand ---

EXPAND_PROMPT = """\
You are a cross-domain innovation researcher. Your task is to identify promising candidate domains for analogical transfer.

PROBLEM DOMAIN: {home_domain}
PRIMARY FUNCTION: {primary_function}
ANALOGICAL HOOKS: {analogical_hooks}
SAPPHIRE EFFECT: {sapphire_effect}
SAPPHIRE PHENOMENON: {sapphire_phenomenon}
NATURE QUESTIONS: {nature_questions}
CROSS-DOMAIN TERMS: {cross_domain_terms}
TRIZ PRINCIPLES: {triz_principles}
UNIVERSAL PRINCIPLES MATCHES: {universal_principles}

DOMAIN CATALOG (for inspiration — you may go beyond this list):
{domain_catalog}

Identify 6-8 candidate domains that might contain useful analogies for solving this problem.

Respond with ONLY valid JSON:
{{
  "candidate_domains": [
    {{
      "domain": "<specific domain name>",
      "rationale": "<why this domain is relevant — which abstraction lens connected it AND what specific mechanism you have in mind>",
      "source_lens": "<sapphire|biologize|wordtree|triz|universal_principles>",
      "distance_from_home": "<low|medium|high>"
    }}
  ],
  "excluded_home_domain": "{home_domain}"
}}

CRITICAL RULES:
- NEVER include "{home_domain}" or closely adjacent fields as a candidate
- Prefer HIGH distance domains — that's where novel ideas come from
- Include at least 2 domains from biology/ecology (mycology, immunology, marine biology, entomology...)
- Include at least 1 domain from arts/humanities (music theory, choreography, linguistics...)
- Include at least 1 domain from earth/physical sciences
- Each domain should connect to a DIFFERENT aspect of the problem
- Cite which lens (sapphire/biologize/wordtree/triz/universal) surfaced each domain
- In the rationale, hint at the SPECIFIC mechanism you think will be useful (not just "this domain is relevant")
"""

# --- Stage 4: Mine ---

MINE_PROMPT = """\
You are an analogical reasoning expert trained in Gentner's Structure-Mapping Theory.

Find a specific mechanism in the SOURCE DOMAIN that maps structurally to the TARGET PROBLEM.

SOURCE DOMAIN: {source_domain}
TARGET PROBLEM: {primary_function}
TARGET SUB-FUNCTIONS: {sub_functions}
TARGET CONSTRAINTS: {constraints}
TARGET CONTRADICTIONS: {contradictions}
TARGET PARAMETERS: {parameters}
CONNECTION RATIONALE: {rationale}

ADDITIONAL CONTEXT (use to find deeper mappings):
UNDERLYING SCIENTIFIC PRINCIPLE: {sapphire_effect}
NATURE REFRAMINGS: {nature_questions}
ANALOGICAL HOOKS: {analogical_hooks}

Respond with ONLY valid JSON:
{{
  "source_domain": "{source_domain}",
  "mechanism": "<a SPECIFIC mechanism/phenomenon in {source_domain} — not a vague concept, a real thing>",
  "mappings": [
    {{
      "source_element": "<element in {source_domain}>",
      "target_element": "<corresponding element in the problem domain>",
      "relation_type": "<causal|functional|structural|constraint|process>"
    }}
  ],
  "where_it_breaks": "<honestly state where the analogy fails or is weak — list multiple points>",
  "abstraction_level": "<effect|phenomenon|action|parts>",
  "systematicity_score": <0.0-1.0, higher = more relational correspondences>
}}

CRITICAL RULES (Gentner's Structure-Mapping):
1. Map RELATIONS, not surface features. "Both involve networks" is BANNED. Map HOW the network functions.
2. Prefer systematic mappings — connected chains of relations, not isolated matches.
3. Each mapping must be a one-to-one correspondence between specific elements.
4. The mechanism must be REAL and SPECIFIC — cite actual phenomena, not abstractions.
5. "where_it_breaks" is REQUIRED and must be honest — list at least 3 specific weak spots.
6. Aim for 5-7 relational mappings minimum.
7. Use the ANALOGICAL HOOKS and SCIENTIFIC PRINCIPLE to find deeper structural parallels.
"""

# --- Stage 5: Synthesize ---

SYNTHESIZE_PROMPT = """\
You are an innovation engineer specializing in cross-domain technology transfer.

Translate this cross-domain analogy into a concrete solution approach for the original problem.

ORIGINAL PROBLEM: {original_problem}
SOURCE DOMAIN: {source_domain}
SOURCE MECHANISM: {mechanism}
STRUCTURAL MAPPINGS:
{mappings_text}
WHERE ANALOGY BREAKS: {where_it_breaks}
{enrichment_context}

Respond with ONLY valid JSON:
{{
  "source_domain": "{source_domain}",
  "source_mechanism": "<the mechanism being transferred>",
  "concrete_approach": "<HOW to implement this — provide NUMBERED STEPS (Step 1, Step 2, etc.) that are specific and actionable. Address the weak spots from WHERE ANALOGY BREAKS — explain how your design works around them.>",
  "candidate_inferences": [
    "<What does the source domain PREDICT about the target that isn't obvious?>",
    "<What secondary effects should we expect based on the source?>",
    "<What failure modes does the source domain warn about?>"
  ],
  "key_predictions": [
    "<A TESTABLE, FALSIFIABLE prediction derived from the analogy — something you could measure or experiment on>",
    "<Another testable prediction — these are the most valuable outputs of the entire process>"
  ],
  "transfer_strength": "<strong|moderate|weak>",
  "feasibility_notes": "<honest assessment of practical feasibility>",
  "research_pointers": {{
    "academic_searches": [
      "<Google Scholar search query to find papers about the source-domain mechanism>",
      "<Google Scholar search query to find papers applying similar ideas to the target domain>",
      "<A more specific/niche search query that could uncover non-obvious connections>"
    ],
    "key_terms": ["<technical term 1 to search in both domains>", "<technical term 2>", "<technical term 3>"],
    "seminal_works": ["<specific paper/book title that is relevant, if you know one>"]
  }}
}}

IMPORTANT:
- "concrete_approach" must be SPECIFIC and ACTIONABLE with numbered steps, not vague inspiration
- Explicitly address how you work around the analogy's weak spots (WHERE ANALOGY BREAKS)
- "candidate_inferences" are non-obvious predictions from the source domain (Gentner's "candidate inference")
- "key_predictions" must be TESTABLE and FALSIFIABLE — something an engineer could validate
- "research_pointers" helps the user find academic literature to validate and deepen the approach
  - academic_searches should be actual search queries that would work on Google Scholar
  - seminal_works should only include papers/books you are confident actually exist
- Be honest about transfer_strength — "weak" is valid and useful output
"""

# --- Stage 6: Evaluate ---

EVALUATE_PROMPT = """\
You are a cross-domain innovation evaluator.

Score this solution on four dimensions. Be calibrated and honest.

ORIGINAL PROBLEM: {original_problem}
HOME DOMAIN: {home_domain}
SOURCE DOMAIN: {source_domain}
SOLUTION APPROACH: {concrete_approach}
CANDIDATE INFERENCES: {candidate_inferences}
KEY PREDICTIONS: {key_predictions}
STRUCTURAL MAPPINGS COUNT: {mapping_count}
ABSTRACTION LEVEL: {abstraction_level}
TRANSFER STRENGTH: {transfer_strength}
WHERE ANALOGY BREAKS: {where_it_breaks}

Respond with ONLY valid JSON:
{{
  "novelty": <0.0-1.0>,
  "feasibility": <0.0-1.0>,
  "structural_depth": <0.0-1.0>,
  "actionability": <0.0-1.0>,
  "reasoning": "<brief justification for scores>"
}}

SCORING GUIDE:
- NOVELTY (0-1): How surprising/non-obvious is this? Domain distance matters.
  - 0.0-0.3: Obvious connection, same general field
  - 0.3-0.6: Interesting cross-field connection
  - 0.6-0.8: Surprising, distant domain connection
  - 0.8-1.0: Genuinely novel, paradigm-shifting
- FEASIBILITY (0-1): How practically implementable is this?
  - 0.0-0.3: Interesting metaphor but impractical
  - 0.3-0.6: Requires significant adaptation but possible
  - 0.6-0.8: Clearly transferable with moderate effort
  - 0.8-1.0: Ready to implement
- STRUCTURAL DEPTH (0-1): Quality of the relational mapping
  - 0.0-0.3: Surface-level analogy, few correspondences
  - 0.3-0.6: Some relational mappings, partial systematicity
  - 0.6-0.8: Strong systematic mapping, 4+ correspondences
  - 0.8-1.0: Deep systematic mapping with predictive power
- ACTIONABILITY (0-1): How concrete and directly implementable is the solution?
  - 0.0-0.3: Vague inspiration, unclear next steps
  - 0.3-0.6: General direction clear, significant design work needed
  - 0.6-0.8: Concrete steps outlined, could prototype
  - 0.8-1.0: Ready to implement with clear action plan
"""

# --- Stage 4.5: Research Enrichment (deep mode) ---

RESEARCH_PROMPT = """\
You are a research assistant. Search for academic papers and quantitative data to validate and enrich this cross-domain analogy.

SOURCE DOMAIN: {source_domain}
SOURCE MECHANISM: {mechanism}
TARGET PROBLEM: {original_problem}
STRUCTURAL MAPPINGS:
{mappings_text}

Your task:
1. Search for academic papers about the source mechanism in {source_domain}
2. Search for existing work applying similar cross-domain transfer to the target problem
3. Find quantitative data from the source domain that could calibrate the transfer

Respond with ONLY valid JSON:
{{
  "source_domain": "{source_domain}",
  "papers_found": [
    {{
      "title": "<paper title>",
      "relevance": "<why this paper matters for the analogy>",
      "url": "<URL if found>"
    }}
  ],
  "key_findings": [
    "<key finding 1 from research that validates or challenges the analogy>",
    "<key finding 2>"
  ],
  "quantitative_data": [
    "<specific quantitative data point from the source domain that could inform the target design>"
  ]
}}

IMPORTANT:
- Only cite papers and data you actually find through search — do not fabricate references
- Focus on papers that validate the MECHANISM, not just the domain
- Quantitative data should be specific numbers, rates, or measurements from the source domain
"""

# --- TRIZ LLM Fallback ---

TRIZ_FALLBACK_PROMPT = """\
You are a TRIZ (Theory of Inventive Problem Solving) expert.

Given these contradictions from a problem, identify the most relevant TRIZ inventive principles.

CONTRADICTIONS:
{contradictions}

AVAILABLE TRIZ PRINCIPLES:
{principles_list}

Select 3-5 principles that are MOST relevant to resolving these contradictions.
Explain briefly why each principle applies.

Respond with ONLY valid JSON:
{{
  "principles": [
    {{
      "number": <principle number>,
      "name": "<principle name>",
      "relevance": "<why this principle helps resolve the contradiction>"
    }}
  ]
}}
"""
