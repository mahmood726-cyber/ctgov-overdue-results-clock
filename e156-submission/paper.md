Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

CT.gov Overdue Results Clock

What does reporting debt look like once missing results are converted into time since due rather than a single binary flag? We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot. We summarized current result-posting status, shares reported within 12, 24, 36, and 60 months, reporting-lag distributions for reported studies, and overdue years beyond the two-year mark for unresolved studies. Pre-FDAAA cohorts remain the deepest debt pool: 87.7 percent unresolved, median reported lag 2,247 days, and mean unresolved debt 18.6 years beyond the two-year mark. By sponsor class, OTHER_GOV is worst on unresolved older studies at 95.7 percent, while industry still combines a 58.1 percent unresolved rate with 9.35 mean overdue years beyond the two-year mark. The clock therefore separates ancient unresolved stock from newer cohorts that are still drifting into silence. These timing summaries use current registry status and do not infer when unpublished external papers may have appeared yet.

**Scientific validity notice (15 October 2026):** The reported 29 March 2026 249,507-study aggregates have **not been independently reproduced**. This repository lacks the exact dated input snapshot and original aggregation code. The two-year no-posting marker is descriptive, **not a statutory ACT/FDAAA results-reporting deadline**; results posting is not results submission, and absence of posted results is not proof of legal noncompliance or absence of an external publication. The separate `src/registry_clock.py` per-NCT descriptive research utility does not recalculate these historical figures.

Outside Notes

Type: methods
Primary estimand: Unresolved share and overdue years beyond the two-year mark among eligible older CT.gov studies
App: CT.gov Overdue Results Clock dashboard
Data: 249,507 eligible older closed interventional studies with current reporting status and results-posting lag fields
Code: https://github.com/mahmood726-cyber/ctgov-overdue-results-clock
Version: 1.0.0
Validation: historical analysis NOT independently reproduced; source and aggregation missing

References

1. ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.
2. DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.
3. Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.
