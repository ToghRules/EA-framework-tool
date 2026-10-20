"""
Data module: EA Framework scores and evaluation criteria definitions.

Scores are based on comparative literature review:
  - Lankhorst (2017) — ArchiMate modelling language
  - Kotusev (2019)   — TOGAF practical evaluation
  - Zachman (1987), Simon et al. (2015) — Zachman ontology & auditability
  - Zhou et al. (2020), Hinkelmann et al. (2016) — tool support gaps
  - ResearchGate (2025): Comparative Analysis of EA Frameworks (TOGAF, Zachman, FEAF)

Scale: 1–10 per criterion.
"""


EA_FRAMEWORKS = {
    "TOGAF": {
        
        "governance":        9,
        "traceability":      6,
        "usability":         6,
        "tool_support":      9,
        "flexibility":       8,
        "completeness":      9,
        "implementation":    9,
        "community":         10,
    },
    "ArchiMate": {
        "governance":        5,
        "traceability":      10,
        "usability":         8,
        "tool_support":      8,
        "flexibility":       8,
        "completeness":      7,
        "implementation":    6,
        "community":         7,
    },
    "Zachman": {
        "governance":        6,
        "traceability":      9,
        "usability":         4,
        "tool_support":      4,
        "flexibility":       5,
        "completeness":      10,
        "implementation":    2,
        "community":         5,
    },
}

DEFAULT_CRITERIA = {
    "governance": {
        "label": "Governance",
        "description": "Extent to which the framework supports organizational governance structures, policies, and compliance mechanisms.",
        "default_weight": 8,
    },
    "traceability": {
        "label": "Traceability",
        "description": "Ability to trace relationships between business, application, and technology layers across the architecture.",
        "default_weight": 7,
    },
    "usability": {
        "label": "Usability",
        "description": "Ease of adoption and use for architects and stakeholders with varying levels of expertise.",
        "default_weight": 6,
    },
    "tool_support": {
        "label": "Tool Support",
        "description": "Availability and maturity of software tools that support the framework (modeling tools, repositories, etc.).",
        "default_weight": 7,
    },
    "flexibility": {
        "label": "Flexibility",
        "description": "Degree to which the framework can be tailored to different organizational sizes, sectors, and contexts.",
        "default_weight": 6,
    },
    "completeness": {
        "label": "Completeness",
        "description": "Coverage of enterprise architecture domains: business, data, application, and technology.",
        "default_weight": 8,
    },
    "implementation": {
        "label": "Implementation Guidance",
        "description": "Quality and depth of guidance provided for practical framework implementation.",
        "default_weight": 5,
    },
    "community": {
        "label": "Community & Adoption",
        "description": "Size and activity of the practitioner community, certification programs, and industry adoption.",
        "default_weight": 5,
    },
}
