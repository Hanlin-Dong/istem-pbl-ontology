# Experiment B2-R — Re-rating of the revised orchestration rules

Six rules are re-rated with the SAME 1-5 scale and procedure as Experiment B2
(see README.md in this directory): the four rules retargeted after the first
rating round (R6, R12, R15b, R21) and the two audit-flagged rules retained
unchanged (R13, R22). Raters must not be told which rules changed.

## Procedure
1. Send `rerating_cards.csv` to the same three experts (or, if unavailable,
   three new qualified raters). Do not reveal which rules were retargeted.
2. Each rater fills `rating_1_to_5` (1-5, scale below) and an optional
   `comment`, independently, and returns the file renamed to
   `rerating_response_<n>.csv` (any delimiter; the parser auto-detects).
3. Run:  /opt/anaconda3/bin/python scripts/followup_studies.py analyze-rerating

## Scale (identical to Experiment B2)
5 highly appropriate — theory-consistent and pedagogically sound
4 appropriate, with minor reservations
3 uncertain — reasonable in some contexts, questionable in others
2 inappropriate — the agent's scaffolding kind does not fit the discourse
1 clearly inappropriate — theory-conflicting or pedagogically counterproductive
