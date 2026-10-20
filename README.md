# EA Framework Decision-Support System
**Master's Thesis Prototype** — Interactive decision-support tool for comparing Enterprise Architecture frameworks using the Weighted Sum Model (WSM).

## Frameworks Covered
- **TOGAF** — The Open Group Architecture Framework
- **ArchiMate** — EA modelling language (The Open Group)
- **Zachman** — Zachman Framework for Enterprise Architecture

## Evaluation Criteria
| Criterion | Description |
|---|---|
| Governance | Support for governance structures and compliance |
| Traceability | Cross-layer relationship tracing |
| Usability | Ease of adoption and use |
| Tool Support | Available tooling ecosystem |
| Flexibility | Adaptability to org context |
| Completeness | EA domain coverage |
| Implementation Guidance | Practical guidance quality |
| Community & Adoption | Industry uptake and community |

## Decision Algorithm
**Weighted Sum Model (WSM)**:

```
S(Ai) = Σⱼ [ wⱼ_norm × rᵢⱼ ] × 10
```

Where `wⱼ_norm` is the user-defined normalized weight and `rᵢⱼ` is the raw score (1–10) for framework `i` on criterion `j`. Final scores are on a 0–100 scale.

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the app
streamlit run app.py
```

The app opens at `http://localhost:8501`

## Features
- ✅ Framework selection (toggle on/off)
- ✅ Interactive weight sliders per criterion
- ✅ Real-time WSM score recalculation
- ✅ Bar chart rankings
- ✅ Radar chart (multi-criteria overview)
- ✅ Stacked bar (criteria contribution breakdown)
- ✅ Score matrix table
- ✅ What-if scenario saving and comparison
- ✅ Winner recommendation with top strengths

## Project Structure
```
ea_decision_support/
├── app.py           # Streamlit UI (Presentation Layer)
├── evaluation.py    # WSM engine (Application Layer)
├── data.py          # Framework scores & criteria (Data Layer)
├── requirements.txt
└── README.md
```

## Architecture Layers (from thesis)
| Layer | File | Responsibilities |
|---|---|---|
| Presentation | `app.py` | UI, interaction, visualization |
| Application | `evaluation.py` | WSM engine, ranking, scenario analysis |
| Data | `data.py` | Framework scores, criteria definitions |
