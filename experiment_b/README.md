# Experiment B — Expert-Validity Study of the SWRL Orchestration Rules

This directory holds the instrument for the expert-validity study. The
theory-alignment audit in `scripts/experiment_b.py` is author-internal; the
validity study itself must be completed by real human experts. This README
defines the protocol.

## What is being rated

Each of the 24 orchestration rules maps a discourse pattern to a virtual-agent
response, e.g. `FailureReporting in Implementation -> MetacognitiveChallenger`.
The claim to validate is: **this trigger choice is pedagogically appropriate**
(i.e., a competent PBL facilitator would agree that the discourse pattern
should prompt that agent's kind of scaffolding).

## Rating scale (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Highly appropriate — theory-consistent and pedagogically sound |
| 4 | Appropriate, with minor reservations |
| 3 | Uncertain — reasonable in some contexts, questionable in others |
| 2 | Inappropriate — the agent's scaffolding kind does not fit the discourse |
| 1 | Clearly inappropriate — theory-conflicting or pedagogically counterproductive |

## Procedure

1. Recruit 3-5 raters: PBL teachers and/or learning-science researchers who
   have not been involved in designing the ontology.
2. Give each rater `judgment_cards.csv` and the scale above. Raters work
   independently (no cross-consultation) — this is the independence that
   breaks the circularity.
3. Collect the filled files into one TSV with one column per rater.
4. Run the reliability statistics:

   ```
   /opt/anaconda3/bin/python scripts/compute_expert_reliability.py <ratings.tsv>
   ```

## Statistics reported

- **Kendall's W** — overall inter-rater agreement (0-1).
- **Fleiss' kappa** — agreement after binarizing at >= 4 ("appropriate").
- **Per-rule mean / std** — std >= 1.0 flags a *contested* rule (experts
  disagree about that trigger).

## Interpretation for the paper

- High W / kappa (> 0.5) and high mean: the trigger choice has expert consensus.
- Low mean (< 3): experts judge the trigger inappropriate — the rule should be
  revised or removed.
- High std: a contested rule — the trigger is context-dependent; either refine
  the antecedent or split the rule.

## Ethics

Raters review the ontology's rule set only; no student-identifiable data is
shared. Raters are free to decline without consequence.
