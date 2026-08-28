# iSTEM-PBL Ontology

Public release for the paper *"iSTEM-PBL Ontology: Semantic Infrastructure
for Hybrid Intelligence, Cognitive Tracing, and Process-Oriented Assessment
in Project-Based Learning"* (IEEE Transactions on Learning Technologies,
submission).

## Contents

- `ontologies/` — the five-module OWL 2 DL ontology (Turtle)
- `vignette/` — the synthetic Team Alpha vignette ABox (no real classroom data)
- `queries/` — the five SPARQL competency questions
- `scripts/` — the ontology build-and-validation toolchain (`tbox.py`,
  `build_all.py`, `build_swrl.py`, `build_vignette.py`, `build_sparql.py`,
  `validate.py`)
- `experiment_b/` — blank expert-rating instruments (Experiment B2 and B2-R)

## Build

```bash
python scripts/build_all.py        # TBox build + Pellet consistency + export
python scripts/build_vignette.py   # synthetic vignette ABox
python scripts/build_swrl.py       # SWRL rules + Pellet inference  (needs Java)
python scripts/build_sparql.py     # competency-question verification
```

## Data availability (two tiers)

**Open (this repository):** everything listed above.

**On request:** the pseudonymized classroom observation dataset, the raw
expert and coder responses (all rating rounds), the blind-coding (IRR)
instruments (which embed the original observation labels), and the analysis
scripts that consume them (`validate_empirical.py`, `validate_analytics.py`,
`validate_swrl_coverage.py`, `gen_mapping_appendix.py`,
`analyze_expert_responses.py`, `compute_expert_reliability.py`,
`experiment_b.py`, `followup_studies.py`). Because the records concern
minors, these files are not publicly downloadable; contact the
corresponding author (**chens016@shnu.edu.cn**) to request them for
research verification, subject to a commitment not to attempt
re-identification.

## License

[Choose and state licenses, e.g., code under MIT, ontology under CC BY 4.0.]

## Citation

[Add the paper reference and the Zenodo DOI after the first archived release.]
