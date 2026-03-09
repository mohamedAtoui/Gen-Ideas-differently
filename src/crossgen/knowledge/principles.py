"""Universal cross-domain principles.

These are recurring patterns observed across many fields — physics, biology,
computer science, economics, ecology, etc. Used in Stage 3 (Expand) to suggest
less-obvious candidate domains.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UniversalPrinciple:
    name: str
    description: str
    domains: list[str]  # domains where this principle appears
    keywords: list[str]  # search terms for matching


UNIVERSAL_PRINCIPLES: list[UniversalPrinciple] = [
    UniversalPrinciple(
        name="Feedback loops",
        description="Output of a system is fed back as input, creating self-regulation (negative) or amplification (positive).",
        domains=["control theory", "biology", "economics", "ecology", "neuroscience", "climate science"],
        keywords=["feedback", "regulation", "homeostasis", "amplification", "damping", "control"],
    ),
    UniversalPrinciple(
        name="Phase transitions",
        description="Abrupt qualitative change when a quantitative parameter crosses a threshold.",
        domains=["physics", "chemistry", "social dynamics", "ecology", "materials science", "network theory"],
        keywords=["phase", "transition", "threshold", "critical point", "tipping point", "emergence"],
    ),
    UniversalPrinciple(
        name="Gradient descent",
        description="Moving toward a local optimum by following the steepest direction of improvement.",
        domains=["mathematics", "machine learning", "evolution", "economics", "fluid dynamics", "neuroscience"],
        keywords=["gradient", "optimization", "descent", "hill climbing", "local minimum", "convergence"],
    ),
    UniversalPrinciple(
        name="Hierarchical organization",
        description="Systems organized in nested levels where each level has emergent properties.",
        domains=["biology", "military", "computer science", "linguistics", "urban planning", "ecology"],
        keywords=["hierarchy", "nested", "levels", "emergence", "organization", "tree"],
    ),
    UniversalPrinciple(
        name="Redundancy",
        description="Duplicate components ensure function continues despite failure.",
        domains=["engineering", "biology", "genetics", "aerospace", "networking", "immunology"],
        keywords=["redundancy", "backup", "fault tolerance", "replication", "spare", "failover"],
    ),
    UniversalPrinciple(
        name="Modularity",
        description="System composed of independent, interchangeable units with defined interfaces.",
        domains=["software engineering", "biology", "manufacturing", "architecture", "ecology", "genetics"],
        keywords=["modular", "module", "component", "interface", "plug-in", "interchangeable"],
    ),
    UniversalPrinciple(
        name="Competitive exclusion",
        description="Two species/entities competing for the same niche cannot coexist indefinitely.",
        domains=["ecology", "economics", "technology markets", "evolutionary biology", "immunology"],
        keywords=["competition", "niche", "exclusion", "winner-take-all", "displacement", "dominance"],
    ),
    UniversalPrinciple(
        name="Diffusion",
        description="Substances, information, or innovations spread from high to low concentration.",
        domains=["physics", "chemistry", "sociology", "epidemiology", "marketing", "urban planning"],
        keywords=["diffusion", "spread", "propagation", "gradient", "concentration", "dissemination"],
    ),
    UniversalPrinciple(
        name="Resonance",
        description="Small periodic input at the right frequency produces large response.",
        domains=["physics", "music", "electronics", "structural engineering", "social movements", "marketing"],
        keywords=["resonance", "frequency", "oscillation", "amplification", "tuning", "vibration"],
    ),
    UniversalPrinciple(
        name="Symbiosis",
        description="Two different entities cooperate for mutual benefit.",
        domains=["biology", "economics", "technology", "ecology", "mycology", "business"],
        keywords=["symbiosis", "mutualism", "cooperation", "partnership", "co-evolution"],
    ),
    UniversalPrinciple(
        name="Homeostasis",
        description="System maintains internal stability through self-regulation despite external changes.",
        domains=["biology", "control theory", "economics", "ecology", "medicine", "climate science"],
        keywords=["homeostasis", "equilibrium", "balance", "stability", "regulation", "set point"],
    ),
    UniversalPrinciple(
        name="Catalysis",
        description="A third party lowers the barrier for a reaction/process without being consumed.",
        domains=["chemistry", "biology", "economics", "social dynamics", "entrepreneurship", "enzyme science"],
        keywords=["catalyst", "catalysis", "enzyme", "activation energy", "facilitator", "enabler"],
    ),
    UniversalPrinciple(
        name="Network effects",
        description="Value of a network grows super-linearly with the number of participants.",
        domains=["economics", "technology", "epidemiology", "social networks", "telecommunications", "ecology"],
        keywords=["network effect", "Metcalfe", "scale", "connectivity", "viral", "contagion"],
    ),
    UniversalPrinciple(
        name="Entropy and disorder",
        description="Systems tend toward maximum disorder unless energy is applied to maintain order.",
        domains=["thermodynamics", "information theory", "sociology", "ecology", "cosmology", "software engineering"],
        keywords=["entropy", "disorder", "decay", "degradation", "maintenance", "order"],
    ),
    UniversalPrinciple(
        name="Parallel processing",
        description="Performing multiple operations simultaneously to increase throughput.",
        domains=["computer science", "neuroscience", "manufacturing", "biology", "economics", "logistics"],
        keywords=["parallel", "concurrent", "simultaneous", "distributed", "throughput"],
    ),
    UniversalPrinciple(
        name="Caching / Memoization",
        description="Store results of expensive operations for future reuse.",
        domains=["computer science", "neuroscience", "ecology", "economics", "logistics"],
        keywords=["cache", "memoize", "store", "remember", "pre-compute", "buffer"],
    ),
    UniversalPrinciple(
        name="Quorum sensing",
        description="Individual agents change behavior when group density crosses a threshold.",
        domains=["microbiology", "social dynamics", "swarm intelligence", "economics", "political science"],
        keywords=["quorum", "threshold", "collective", "swarm", "consensus", "critical mass"],
    ),
    UniversalPrinciple(
        name="Selective permeability",
        description="A barrier allows some things through while blocking others.",
        domains=["biology", "chemistry", "computer security", "immigration", "filtration", "architecture"],
        keywords=["filter", "permeability", "membrane", "selective", "barrier", "gateway", "firewall"],
    ),
    UniversalPrinciple(
        name="Adaptation through variation and selection",
        description="Generate diverse variants, test against environment, keep what works.",
        domains=["evolution", "machine learning", "entrepreneurship", "immunology", "materials science"],
        keywords=["evolution", "selection", "variation", "mutation", "fitness", "adaptation", "genetic"],
    ),
    UniversalPrinciple(
        name="Signal amplification cascade",
        description="Small initial signal triggers a chain of amplifying reactions.",
        domains=["biochemistry", "electronics", "neuroscience", "social media", "immunology", "nuclear physics"],
        keywords=["cascade", "amplification", "signal", "chain reaction", "domino", "avalanche"],
    ),
    UniversalPrinciple(
        name="Load balancing",
        description="Distribute work across multiple agents to prevent overload of any single one.",
        domains=["computer science", "logistics", "biology", "urban planning", "electrical engineering"],
        keywords=["load balance", "distribute", "spread", "equalize", "share", "distribute"],
    ),
    UniversalPrinciple(
        name="Annealing / Simulated cooling",
        description="Start with high randomness, gradually reduce to settle into optimal configuration.",
        domains=["metallurgy", "optimization", "machine learning", "molecular biology", "urban planning"],
        keywords=["annealing", "cooling", "temperature", "randomness", "exploration", "exploitation"],
    ),
    UniversalPrinciple(
        name="Immune response pattern",
        description="Detect-identify-remember-respond pattern for handling threats.",
        domains=["immunology", "computer security", "fraud detection", "ecology", "military"],
        keywords=["immune", "detection", "antibody", "memory", "response", "defense", "antigen"],
    ),
    UniversalPrinciple(
        name="Scaffolding and dissolution",
        description="Temporary structure supports growth, then is removed when no longer needed.",
        domains=["construction", "education", "embryology", "software development", "mycology"],
        keywords=["scaffold", "temporary", "support", "bootstrap", "staging", "dissolve"],
    ),
    UniversalPrinciple(
        name="Predator-prey dynamics",
        description="Oscillating populations where increase in one drives increase/decrease in another.",
        domains=["ecology", "economics", "cybersecurity", "epidemiology", "game theory"],
        keywords=["predator", "prey", "oscillation", "Lotka-Volterra", "arms race", "co-evolution"],
    ),
    UniversalPrinciple(
        name="Self-organization",
        description="Order emerges from local interactions without central control.",
        domains=["physics", "biology", "sociology", "urban planning", "swarm intelligence", "chemistry"],
        keywords=["self-organization", "emergent", "bottom-up", "decentralized", "spontaneous order"],
    ),
    UniversalPrinciple(
        name="Hysteresis",
        description="System state depends on history, not just current input. Path-dependent behavior.",
        domains=["physics", "materials science", "economics", "ecology", "psychology", "political science"],
        keywords=["hysteresis", "path dependence", "history", "memory", "irreversible", "lag"],
    ),
    UniversalPrinciple(
        name="Compartmentalization",
        description="Isolate different processes/substances in separate spaces to prevent interference.",
        domains=["biology", "chemistry", "software engineering", "architecture", "nuclear engineering", "security"],
        keywords=["compartment", "isolate", "separate", "contain", "sandbox", "encapsulate"],
    ),
    UniversalPrinciple(
        name="Tensegrity",
        description="Structural integrity from balance of tension and compression, not rigid connections.",
        domains=["architecture", "biology", "materials science", "robotics", "art"],
        keywords=["tensegrity", "tension", "compression", "balance", "structural", "integrity"],
    ),
    UniversalPrinciple(
        name="Mycelial networks",
        description="Underground resource-sharing networks that connect and support diverse organisms.",
        domains=["mycology", "ecology", "computer networking", "economics", "neuroscience"],
        keywords=["mycelium", "network", "underground", "nutrient", "sharing", "wood wide web"],
    ),
    UniversalPrinciple(
        name="Stigmergy",
        description="Indirect coordination through environmental modifications (ant pheromone trails).",
        domains=["entomology", "urban planning", "software engineering", "robotics", "social systems"],
        keywords=["stigmergy", "pheromone", "trail", "indirect", "coordination", "environment"],
    ),
    UniversalPrinciple(
        name="Hydraulic amplification",
        description="Force multiplied through fluid pressure in confined spaces (Pascal's principle).",
        domains=["physics", "engineering", "biology", "geology", "medicine"],
        keywords=["hydraulic", "pressure", "amplify", "fluid", "Pascal", "force multiplication"],
    ),
    UniversalPrinciple(
        name="Ecological succession",
        description="Predictable sequence of community changes where each stage creates conditions for the next.",
        domains=["ecology", "urban development", "technology adoption", "organizational growth", "soil science"],
        keywords=["succession", "pioneer", "climax", "colonization", "maturation", "stages"],
    ),
    UniversalPrinciple(
        name="Allosteric regulation",
        description="Binding at one site changes behavior at a distant site.",
        domains=["biochemistry", "economics", "organizational behavior", "network theory"],
        keywords=["allosteric", "remote control", "indirect regulation", "conformational change"],
    ),
    UniversalPrinciple(
        name="Capillary action",
        description="Liquid spontaneously moves through narrow spaces against gravity via surface tension.",
        domains=["physics", "botany", "materials science", "microfluidics", "construction"],
        keywords=["capillary", "wicking", "surface tension", "spontaneous", "narrow"],
    ),
    UniversalPrinciple(
        name="Metamorphosis",
        description="Radical structural transformation between life stages optimized for different functions.",
        domains=["biology", "software migration", "organizational change", "materials science"],
        keywords=["metamorphosis", "transformation", "larva", "restructure", "radical change"],
    ),
    UniversalPrinciple(
        name="Quenching",
        description="Rapid state change locks in a non-equilibrium configuration with desired properties.",
        domains=["metallurgy", "chemistry", "glass-making", "machine learning", "photography"],
        keywords=["quench", "rapid", "freeze", "lock in", "non-equilibrium", "temper"],
    ),
    UniversalPrinciple(
        name="Trophic cascades",
        description="Changes at the top of a hierarchy propagate dramatic effects downward through all levels.",
        domains=["ecology", "economics", "organizational behavior", "supply chains"],
        keywords=["trophic", "cascade", "top-down", "apex", "ripple effect", "indirect effects"],
    ),
    UniversalPrinciple(
        name="Chirality / Handedness",
        description="Mirror-image forms of the same structure have dramatically different properties.",
        domains=["chemistry", "biology", "physics", "manufacturing", "cryptography"],
        keywords=["chirality", "mirror", "enantiomer", "handedness", "asymmetry", "orientation"],
    ),
    UniversalPrinciple(
        name="Dormancy",
        description="Suspend activity during unfavorable conditions, resume when conditions improve.",
        domains=["biology", "ecology", "software engineering", "economics", "military strategy"],
        keywords=["dormancy", "hibernation", "suspend", "latent", "sleep", "quiescent", "idle"],
    ),
]


def search_principles(query: str) -> list[UniversalPrinciple]:
    """Search universal principles by keyword match."""
    query_lower = query.lower()
    results = []
    for p in UNIVERSAL_PRINCIPLES:
        if (
            query_lower in p.name.lower()
            or query_lower in p.description.lower()
            or any(query_lower in k for k in p.keywords)
            or any(query_lower in d for d in p.domains)
        ):
            results.append(p)
    return results


def get_domains_for_principle(principle_name: str) -> list[str]:
    """Get all domains associated with a named principle."""
    for p in UNIVERSAL_PRINCIPLES:
        if p.name.lower() == principle_name.lower():
            return p.domains
    return []
