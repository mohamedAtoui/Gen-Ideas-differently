"""Domain catalog for cross-domain exploration.

Provides a curated set of domains spanning diverse fields,
used in Stage 3 to suggest less-obvious candidate domains.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Domain:
    name: str
    category: str
    keywords: list[str]
    description: str


DOMAIN_CATALOG: list[Domain] = [
    # Biological Sciences
    Domain("immunology", "biology", ["immune", "antibody", "antigen", "defense", "pathogen"], "Study of immune systems and defense mechanisms"),
    Domain("mycology", "biology", ["fungus", "mycelium", "spore", "decomposition", "network"], "Study of fungi, their networks and lifecycle"),
    Domain("neuroscience", "biology", ["neuron", "brain", "synapse", "plasticity", "cognition"], "Study of nervous systems and brain function"),
    Domain("ecology", "biology", ["ecosystem", "population", "niche", "succession", "food web"], "Study of organism-environment interactions"),
    Domain("evolutionary biology", "biology", ["evolution", "selection", "adaptation", "fitness", "mutation"], "Study of how species change over time"),
    Domain("marine biology", "biology", ["ocean", "coral", "deep sea", "bioluminescence", "pressure"], "Study of ocean life and ecosystems"),
    Domain("entomology", "biology", ["insect", "colony", "swarm", "metamorphosis", "pheromone"], "Study of insects and their behaviors"),
    Domain("botany", "biology", ["plant", "photosynthesis", "root", "growth", "pollination"], "Study of plants and their processes"),
    Domain("microbiology", "biology", ["bacteria", "microbe", "biofilm", "quorum", "culture"], "Study of microscopic organisms"),

    # Physical Sciences
    Domain("fluid dynamics", "physics", ["flow", "turbulence", "viscosity", "pressure", "stream"], "Study of fluid motion and behavior"),
    Domain("thermodynamics", "physics", ["heat", "entropy", "energy", "equilibrium", "cycle"], "Study of heat, energy, and work"),
    Domain("materials science", "physics", ["material", "alloy", "composite", "crystal", "polymer"], "Study of material properties and design"),
    Domain("optics", "physics", ["light", "lens", "refraction", "diffraction", "spectrum"], "Study of light behavior and applications"),
    Domain("acoustics", "physics", ["sound", "wave", "resonance", "vibration", "frequency"], "Study of sound and mechanical waves"),
    Domain("quantum mechanics", "physics", ["quantum", "superposition", "entanglement", "wave function", "uncertainty"], "Study of subatomic particle behavior"),

    # Engineering
    Domain("civil engineering", "engineering", ["structure", "bridge", "foundation", "load", "construction"], "Design and construction of infrastructure"),
    Domain("aerospace engineering", "engineering", ["flight", "aerodynamics", "propulsion", "orbit", "payload"], "Design of aircraft and spacecraft"),
    Domain("chemical engineering", "engineering", ["reactor", "process", "separation", "catalyst", "yield"], "Chemical process design and optimization"),
    Domain("electrical engineering", "engineering", ["circuit", "signal", "amplifier", "filter", "impedance"], "Design of electrical systems"),

    # Social Sciences
    Domain("urban planning", "social", ["city", "zoning", "transit", "density", "infrastructure"], "Design and organization of urban spaces"),
    Domain("economics", "social", ["market", "supply", "demand", "incentive", "equilibrium"], "Study of resource allocation and exchange"),
    Domain("organizational behavior", "social", ["team", "leadership", "culture", "motivation", "hierarchy"], "Study of how organizations function"),
    Domain("epidemiology", "social", ["spread", "contagion", "outbreak", "vaccination", "herd immunity"], "Study of disease spread and control"),
    Domain("political science", "social", ["governance", "policy", "power", "democracy", "institution"], "Study of political systems and power"),

    # Earth Sciences
    Domain("geology", "earth", ["rock", "tectonic", "erosion", "sediment", "mineral"], "Study of Earth's structure and processes"),
    Domain("meteorology", "earth", ["weather", "atmosphere", "pressure", "front", "precipitation"], "Study of weather and atmospheric phenomena"),
    Domain("oceanography", "earth", ["current", "tide", "salinity", "depth", "circulation"], "Study of ocean systems and processes"),
    Domain("soil science", "earth", ["soil", "nutrient", "decomposition", "layer", "fertility"], "Study of soil formation and properties"),

    # Applied Fields
    Domain("logistics", "applied", ["supply chain", "routing", "warehouse", "delivery", "inventory"], "Management of goods flow and distribution"),
    Domain("architecture", "applied", ["building", "space", "design", "ventilation", "load"], "Design of buildings and spaces"),
    Domain("agriculture", "applied", ["crop", "irrigation", "soil", "harvest", "rotation"], "Science and practice of farming"),
    Domain("medicine", "applied", ["diagnosis", "treatment", "surgery", "drug", "therapy"], "Practice of healing and healthcare"),
    Domain("culinary arts", "applied", ["cooking", "fermentation", "emulsion", "reduction", "seasoning"], "Science and art of food preparation"),
    Domain("textile science", "applied", ["fiber", "weave", "dyeing", "tension", "fabric"], "Study of fibers, yarns, and fabrics"),

    # Information & Mathematical Sciences
    Domain("information theory", "math", ["entropy", "channel", "encoding", "compression", "noise"], "Mathematical study of information"),
    Domain("graph theory", "math", ["network", "node", "edge", "path", "connectivity"], "Mathematical study of networks"),
    Domain("game theory", "math", ["strategy", "payoff", "equilibrium", "cooperation", "defection"], "Mathematical study of strategic interaction"),
    Domain("cryptography", "math", ["encryption", "key", "hash", "cipher", "protocol"], "Science of secure communication"),
    Domain("signal processing", "math", ["filter", "transform", "frequency", "noise", "spectrum"], "Analysis and manipulation of signals"),

    # Arts & Humanities
    Domain("music theory", "arts", ["harmony", "rhythm", "melody", "counterpoint", "resonance"], "Study of musical structure and principles"),
    Domain("linguistics", "arts", ["language", "grammar", "syntax", "semantics", "morphology"], "Study of language structure"),
    Domain("choreography", "arts", ["movement", "sequence", "coordination", "rhythm", "spatial"], "Art of designing movement sequences"),
]


def search_domains(query: str, exclude: str | None = None) -> list[Domain]:
    """Search domains by keyword, optionally excluding a specific domain."""
    query_lower = query.lower()
    results = []
    for d in DOMAIN_CATALOG:
        if exclude and d.name.lower() == exclude.lower():
            continue
        if (
            query_lower in d.name.lower()
            or query_lower in d.category.lower()
            or query_lower in d.description.lower()
            or any(query_lower in k for k in d.keywords)
        ):
            results.append(d)
    return results


def get_all_domain_names(exclude: str | None = None) -> list[str]:
    """Get all domain names, optionally excluding one."""
    return [d.name for d in DOMAIN_CATALOG if not (exclude and d.name.lower() == exclude.lower())]
