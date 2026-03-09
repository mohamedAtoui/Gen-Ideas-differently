"""TRIZ 40 Inventive Principles and Contradiction Matrix.

Pure deterministic data — no LLM involvement in principle selection.
"""

from __future__ import annotations

# The 40 Inventive Principles of TRIZ
INVENTIVE_PRINCIPLES: dict[int, dict] = {
    1: {
        "name": "Segmentation",
        "description": "Divide an object into independent parts; make it sectional; increase degree of fragmentation.",
        "examples": ["Modular furniture", "Sectioned containers", "Multi-blade razors"],
    },
    2: {
        "name": "Taking out / Extraction",
        "description": "Separate an interfering part or property from an object, or single out the only necessary part.",
        "examples": ["Noise-canceling headphones extract anti-noise", "Extract heat from a process"],
    },
    3: {
        "name": "Local quality",
        "description": "Change an object's structure from uniform to non-uniform; make each part function in conditions most suitable for its operation.",
        "examples": ["Pencil with eraser", "Bifocal lenses", "Multi-zone climate control"],
    },
    4: {
        "name": "Asymmetry",
        "description": "Change the shape of an object from symmetrical to asymmetrical.",
        "examples": ["Asymmetric tires for better grip", "Ergonomic handles"],
    },
    5: {
        "name": "Merging / Consolidation",
        "description": "Bring closer together identical or similar objects; assemble identical parts to perform parallel operations.",
        "examples": ["Multi-core processors", "Bundled cables", "Combine harvester"],
    },
    6: {
        "name": "Universality",
        "description": "Make a part or object perform multiple functions; eliminate the need for other parts.",
        "examples": ["Smartphone replaces camera, phone, GPS", "Swiss army knife"],
    },
    7: {
        "name": "Nested doll / Nesting",
        "description": "Place one object inside another; pass one through a cavity in another.",
        "examples": ["Telescopic antenna", "Stacking chairs", "Russian dolls"],
    },
    8: {
        "name": "Anti-weight / Counterweight",
        "description": "Compensate for the weight of an object by merging with other objects that provide lift.",
        "examples": ["Helium balloons on heavy equipment", "Counterweights in elevators"],
    },
    9: {
        "name": "Preliminary anti-action",
        "description": "If it will be necessary to do an action with both harmful and useful effects, this action should be replaced with anti-actions to control harmful effects.",
        "examples": ["Pre-stress concrete", "Vaccination (controlled exposure)"],
    },
    10: {
        "name": "Preliminary action",
        "description": "Perform the required change fully or partially in advance; pre-arrange objects for convenient operation.",
        "examples": ["Pre-pasted wallpaper", "Sterilized packaging", "Pre-compiled code"],
    },
    11: {
        "name": "Beforehand cushioning",
        "description": "Prepare emergency means beforehand to compensate for the relatively low reliability of an object.",
        "examples": ["Airbags", "Backup systems", "Checksums", "Circuit breakers"],
    },
    12: {
        "name": "Equipotentiality",
        "description": "Change the conditions of work so that an object need not be raised or lowered.",
        "examples": ["Lock gates equalize water levels", "Pressure equalization valves"],
    },
    13: {
        "name": "The other way round / Inversion",
        "description": "Invert the action; make movable parts fixed and fixed parts movable; turn the object upside down.",
        "examples": ["Treadmill (person stationary, ground moves)", "Rotary engine"],
    },
    14: {
        "name": "Spheroidality / Curvature",
        "description": "Use curves instead of straight lines; use spheres instead of cubes; use spiral or rotary motion.",
        "examples": ["Arched bridges", "Ball bearings", "Spiral conveyor"],
    },
    15: {
        "name": "Dynamics",
        "description": "Allow characteristics of an object or process to change to be optimal at each stage.",
        "examples": ["Adjustable steering wheel", "Dynamic pricing", "Adaptive algorithms"],
    },
    16: {
        "name": "Partial or excessive action",
        "description": "If 100% of an objective is hard to achieve, use slightly less or slightly more.",
        "examples": ["Overfill and remove excess (painting)", "Approximate solutions"],
    },
    17: {
        "name": "Another dimension",
        "description": "Move to multi-dimensional space; use multi-layered assemblies; tilt or re-orient the object.",
        "examples": ["Spiral staircase", "3D printing", "Multi-story parking"],
    },
    18: {
        "name": "Mechanical vibration",
        "description": "Cause an object to oscillate or vibrate; increase frequency; use resonance.",
        "examples": ["Ultrasonic cleaning", "Vibrating concrete pour", "Resonance imaging"],
    },
    19: {
        "name": "Periodic action",
        "description": "Replace continuous action with periodic or pulsed action; change periodicity; use pauses between impulses.",
        "examples": ["Pulsed laser vs continuous", "Interval training", "Batch processing"],
    },
    20: {
        "name": "Continuity of useful action",
        "description": "Carry on work continuously; eliminate all idle or intermittent actions.",
        "examples": ["Continuous casting", "Flywheel energy storage", "Pipeline processing"],
    },
    21: {
        "name": "Skipping / Rushing through",
        "description": "Conduct a process at high speed to avoid harmful side effects.",
        "examples": ["High-speed cutting reduces heat damage", "Flash pasteurization"],
    },
    22: {
        "name": "Blessing in disguise",
        "description": "Use harmful factors to achieve a positive effect; amplify a harmful factor to the point where it is no longer harmful.",
        "examples": ["Use waste heat for heating", "Controlled burns prevent wildfires"],
    },
    23: {
        "name": "Feedback",
        "description": "Introduce feedback to improve a process; if feedback exists, change its magnitude or influence.",
        "examples": ["Thermostat", "PID controllers", "A/B testing"],
    },
    24: {
        "name": "Intermediary / Mediator",
        "description": "Use an intermediary carrier article or process; merge one object temporarily with another.",
        "examples": ["Catalyst", "Adapter pattern", "Message broker"],
    },
    25: {
        "name": "Self-service",
        "description": "Make an object serve itself by performing auxiliary functions; use waste resources, energy, or substances.",
        "examples": ["Self-cleaning oven", "Self-healing materials", "Garbage collection"],
    },
    26: {
        "name": "Copying",
        "description": "Use simpler and inexpensive copies instead of unavailable, expensive, or fragile objects.",
        "examples": ["Virtual prototypes", "Simulations", "Digital twins"],
    },
    27: {
        "name": "Cheap short-living objects",
        "description": "Replace an expensive object with multiple inexpensive objects, compromising certain qualities.",
        "examples": ["Disposable diapers", "Containerized microservices", "A/B test variants"],
    },
    28: {
        "name": "Mechanics substitution",
        "description": "Replace a mechanical means with sensory means (optical, acoustic, taste or smell).",
        "examples": ["Electric field instead of mechanical barrier", "Optical sorting"],
    },
    29: {
        "name": "Pneumatics and hydraulics",
        "description": "Use gas and liquid parts of an object instead of solid parts.",
        "examples": ["Inflatable structures", "Hydraulic press", "Air cushion"],
    },
    30: {
        "name": "Flexible shells and thin films",
        "description": "Use flexible shells and thin films instead of three-dimensional structures.",
        "examples": ["Bubble wrap", "Thin-film solar cells", "Shrink wrap"],
    },
    31: {
        "name": "Porous materials",
        "description": "Make an object porous or add porous elements; fill pores with useful substance.",
        "examples": ["Sponge filters", "Aerogel insulation", "Porous bone implants"],
    },
    32: {
        "name": "Color changes",
        "description": "Change the color of an object or its external environment; change the transparency.",
        "examples": ["Photochromic lenses", "Thermochromic indicators", "Syntax highlighting"],
    },
    33: {
        "name": "Homogeneity",
        "description": "Make objects interacting with the main object of the same material or close to it.",
        "examples": ["Ice container for ice cream", "Edible packaging", "Same-language interfaces"],
    },
    34: {
        "name": "Discarding and recovering",
        "description": "Make portions of an object that have fulfilled their functions go away; restore consumable parts during operation.",
        "examples": ["Rocket staging", "Biodegradable packaging", "Memory deallocation"],
    },
    35: {
        "name": "Parameter changes",
        "description": "Change an object's physical state, concentration, density, flexibility, or temperature.",
        "examples": ["Freeze-drying", "Compressed gas storage", "Phase-change cooling"],
    },
    36: {
        "name": "Phase transitions",
        "description": "Use phenomena occurring during phase transitions (volume changes, heat loss/absorption).",
        "examples": ["Heat pipes use evaporation/condensation", "Water expansion when freezing"],
    },
    37: {
        "name": "Thermal expansion",
        "description": "Use thermal expansion or contraction; use multiple materials with different thermal expansion coefficients.",
        "examples": ["Bimetallic thermostat", "Shrink-fit assembly"],
    },
    38: {
        "name": "Strong oxidants / Accelerated oxidation",
        "description": "Replace common air with enriched air or oxygen; use ionized oxygen; use ozone.",
        "examples": ["Ozone water treatment", "Oxygen-enriched combustion", "Plasma cleaning"],
    },
    39: {
        "name": "Inert atmosphere",
        "description": "Replace a normal environment with an inert one; add neutral parts or inert additives.",
        "examples": ["Nitrogen-packed food", "Noble gas welding", "Sandboxed execution"],
    },
    40: {
        "name": "Composite materials",
        "description": "Change from uniform to composite (multiple) materials.",
        "examples": ["Carbon fiber reinforced plastic", "Reinforced concrete", "Hybrid architectures"],
    },
}


# 39 TRIZ Engineering Parameters (used in the contradiction matrix)
TRIZ_PARAMETERS: dict[int, str] = {
    1: "Weight of moving object",
    2: "Weight of stationary object",
    3: "Length of moving object",
    4: "Length of stationary object",
    5: "Area of moving object",
    6: "Area of stationary object",
    7: "Volume of moving object",
    8: "Volume of stationary object",
    9: "Speed",
    10: "Force (intensity)",
    11: "Stress or pressure",
    12: "Shape",
    13: "Stability of the object's composition",
    14: "Strength",
    15: "Duration of action by a moving object",
    16: "Duration of action by a stationary object",
    17: "Temperature",
    18: "Illumination intensity",
    19: "Use of energy by moving object",
    20: "Use of energy by stationary object",
    21: "Power",
    22: "Loss of energy",
    23: "Loss of substance",
    24: "Loss of information",
    25: "Loss of time",
    26: "Quantity of substance/matter",
    27: "Reliability",
    28: "Measurement accuracy",
    29: "Manufacturing precision",
    30: "Object-affected harmful factors",
    31: "Object-generated harmful factors",
    32: "Ease of manufacture",
    33: "Ease of operation",
    34: "Ease of repair",
    35: "Adaptability or versatility",
    36: "Device complexity",
    37: "Difficulty of detecting and measuring",
    38: "Extent of automation",
    39: "Productivity",
}


# Contradiction Matrix: maps (improving_param, worsening_param) -> list of principle numbers.
# This is a subset of the full 39x39 matrix covering the most commonly used entries.
# Format: {(improving, worsening): [principle_numbers]}
CONTRADICTION_MATRIX: dict[tuple[int, int], list[int]] = {
    # Speed vs Weight
    (9, 1): [2, 28, 13, 38],
    (9, 2): [13, 14, 8],
    # Speed vs Force
    (9, 10): [13, 28, 15, 19],
    # Speed vs Reliability
    (9, 27): [11, 35, 27, 28],
    # Speed vs Complexity
    (9, 36): [13, 35, 1],
    # Speed vs Productivity
    (9, 39): [28, 35, 13, 18],
    # Force vs Weight
    (10, 1): [8, 1, 37, 18],
    (10, 2): [13, 28, 15, 12],
    # Force vs Speed
    (10, 9): [13, 28, 15, 19],
    # Force vs Stability
    (10, 13): [35, 10, 36],
    # Strength vs Weight
    (14, 1): [1, 8, 40, 15],
    (14, 2): [40, 26, 27, 1],
    # Strength vs Ease of manufacture
    (14, 32): [1, 35, 11, 10],
    # Reliability vs Complexity
    (27, 36): [13, 35, 1],
    # Reliability vs Speed
    (27, 9): [11, 35, 27, 28],
    # Reliability vs Loss of time
    (27, 25): [10, 30, 4],
    # Productivity vs Reliability
    (39, 27): [35, 28, 2, 24],
    # Productivity vs Complexity
    (39, 36): [35, 28, 2, 24],
    # Productivity vs Loss of energy
    (39, 22): [28, 10, 29, 35],
    # Productivity vs Speed
    (39, 9): [28, 35, 13, 18],
    # Ease of operation vs Complexity
    (33, 36): [27, 22, 13, 24],
    # Ease of operation vs Reliability
    (33, 27): [25, 2, 13, 15],
    # Adaptability vs Complexity
    (35, 36): [15, 29, 37, 28],
    # Adaptability vs Reliability
    (35, 27): [35, 1, 13, 11],
    # Adaptability vs Ease of manufacture
    (35, 32): [1, 15, 29, 4],
    # Loss of information vs Speed
    (24, 9): [10, 24, 35],
    # Loss of information vs Complexity
    (24, 36): [24, 26, 28, 32],
    # Loss of information vs Reliability
    (24, 27): [10, 28, 23],
    # Loss of time vs Reliability
    (25, 27): [10, 30, 4],
    # Loss of time vs Complexity
    (25, 36): [35, 28, 34, 4],
    # Loss of time vs Productivity
    (25, 39): [10, 37, 36, 5],
    # Loss of energy vs Speed
    (22, 9): [19, 38, 7],
    # Loss of energy vs Productivity
    (22, 39): [28, 10, 29, 35],
    # Complexity vs Reliability
    (36, 27): [26, 24, 32, 28],
    # Complexity vs Adaptability
    (36, 35): [15, 29, 37, 28],
    # Complexity vs Ease of operation
    (36, 33): [27, 22, 13, 24],
    # Ease of manufacture vs Strength
    (32, 14): [1, 35, 11, 10],
    # Ease of manufacture vs Reliability
    (32, 27): [11, 13, 1],
    # Ease of manufacture vs Complexity
    (32, 36): [26, 24, 32, 28],
    # Measurement accuracy vs Speed
    (28, 9): [28, 32, 13, 6],
    # Measurement accuracy vs Complexity
    (28, 36): [26, 24, 32, 28],
    # Automation vs Complexity
    (38, 36): [15, 24, 10],
    # Automation vs Reliability
    (38, 27): [5, 12, 35, 26],
    # Automation vs Productivity
    (38, 39): [5, 12, 35, 26],
    # Harmful factors vs Reliability
    (30, 27): [22, 21, 27, 39],
    (31, 27): [19, 22, 31, 2],
    # Object stability vs Adaptability
    (13, 35): [35, 15, 34, 18],
    # Shape vs Ease of manufacture
    (12, 32): [14, 4, 15, 22],
    # Area vs Weight
    (5, 1): [29, 30, 14, 5],
    (6, 2): [40, 29, 14, 5],
    # Volume vs Weight
    (7, 1): [2, 26, 29, 40],
    (8, 2): [35, 10, 19, 14],
    # Temperature vs Reliability
    (17, 27): [21, 36, 29, 31],
    # Power vs Loss of energy
    (21, 22): [19, 38, 7],
    # Power vs Reliability
    (21, 27): [2, 35, 22],
}


# Generalized parameter keywords to help map natural-language contradictions to TRIZ parameters
PARAMETER_KEYWORDS: dict[int, list[str]] = {
    1: ["weight", "mass", "heavy", "light", "moving"],
    2: ["weight", "mass", "heavy", "light", "stationary", "static"],
    5: ["area", "surface", "footprint", "moving"],
    6: ["area", "surface", "footprint", "stationary"],
    7: ["volume", "size", "space", "capacity", "moving", "memory", "RAM", "VRAM", "buffer", "cache size"],
    8: ["volume", "size", "space", "capacity", "stationary", "storage", "disk", "footprint", "memory footprint"],
    9: ["speed", "velocity", "fast", "slow", "latency", "throughput", "rate", "bandwidth",
        "response time", "execution time", "compute time", "inference", "tokens per second"],
    10: ["force", "intensity", "power", "strength", "pressure"],
    11: ["stress", "pressure", "tension", "load"],
    12: ["shape", "form", "structure", "geometry", "topology"],
    13: ["stability", "consistency", "robustness", "steady"],
    14: ["strength", "durability", "resilience", "hardness"],
    17: ["temperature", "heat", "thermal", "cooling", "warming"],
    19: ["energy", "power consumption", "resource use", "moving"],
    20: ["energy", "power consumption", "resource use", "stationary"],
    21: ["power", "wattage", "output", "performance"],
    22: ["energy loss", "waste", "dissipation", "leakage", "overhead",
         "compute waste", "redundant computation", "wasted cycles"],
    23: ["substance loss", "material loss", "data loss"],
    24: ["information loss", "data loss", "signal loss", "accuracy loss", "precision loss", "fidelity",
         "quality loss", "accuracy degradation", "approximation error", "quantization error"],
    25: ["time loss", "delay", "latency", "waiting", "downtime", "time waste",
         "recomputation", "compute cost", "wall time"],
    26: ["quantity", "amount", "count", "number"],
    27: ["reliability", "uptime", "availability", "fault tolerance", "consistency", "correctness"],
    28: ["accuracy", "precision", "measurement", "resolution"],
    29: ["manufacturing precision", "build quality", "tolerance"],
    30: ["harmful factors", "external harm", "vulnerability", "susceptibility"],
    31: ["harmful side effects", "pollution", "noise", "interference"],
    32: ["ease of manufacture", "manufacturability", "ease of implementation", "simplicity of creation"],
    33: ["ease of operation", "usability", "user experience", "convenience", "ergonomics"],
    34: ["ease of repair", "maintainability", "serviceability", "debuggability"],
    35: ["adaptability", "versatility", "flexibility", "configurability", "extensibility"],
    36: ["complexity", "complication", "difficulty", "intricacy",
         "implementation complexity", "algorithmic complexity"],
    37: ["detectability", "measurability", "observability", "monitorability"],
    38: ["automation", "autonomy", "self-regulation"],
    39: ["productivity", "efficiency", "throughput", "output", "performance", "capacity",
         "utilization", "ops per second", "FLOPS"],
}


def lookup_principles(improving_param: int, worsening_param: int) -> list[dict]:
    """Look up inventive principles from the contradiction matrix.

    Returns list of principle dicts with number, name, description, examples.
    Returns empty list if the combination is not in the matrix.
    """
    principle_nums = CONTRADICTION_MATRIX.get((improving_param, worsening_param), [])
    results = []
    for num in principle_nums:
        if num in INVENTIVE_PRINCIPLES:
            results.append({"number": num, **INVENTIVE_PRINCIPLES[num]})
    return results


def find_parameter(keyword: str) -> list[tuple[int, str]]:
    """Find TRIZ parameters matching a keyword.

    Uses 3-tier matching:
    1. TRIZ keyword is a substring of the input (e.g., "capacity" matches "memory capacity")
    2. Input is a substring of a TRIZ keyword (original behavior, for single-word inputs)
    3. Word-level: any word in the input matches any TRIZ keyword or vice versa

    Returns list of (parameter_number, parameter_name) tuples.
    """
    keyword_lower = keyword.lower()
    keyword_words = keyword_lower.split()
    matches = []
    for param_id, keywords in PARAMETER_KEYWORDS.items():
        if any(
            kw in keyword_lower  # TRIZ keyword is substring of input
            or keyword_lower in kw  # input is substring of TRIZ keyword
            or any(w in kw or kw in w for w in keyword_words)  # word-level
            for kw in keywords
        ):
            matches.append((param_id, TRIZ_PARAMETERS[param_id]))
    return matches


def get_principle(number: int) -> dict | None:
    """Get a single inventive principle by number."""
    p = INVENTIVE_PRINCIPLES.get(number)
    if p:
        return {"number": number, **p}
    return None
