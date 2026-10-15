Mahmood Ahmad
Tahir Heart Institute
author@example.com

Protocol: CT.gov Overdue Results Clock

**Scientific validity notice (15 October 2026):** The reported 29 March 2026 249,507-study aggregates have **not been independently reproduced**. This repository lacks the exact dated input snapshot and original aggregation code. The two-year no-posting marker is descriptive, **not a statutory ACT/FDAAA results-reporting deadline**; results posting is not results submission, and absence of posted results is not proof of legal noncompliance or absence of an external publication. The separate `src/registry_clock.py` per-NCT descriptive research utility does not recalculate these historical figures.

This protocol converts missing-results status into a reporting clock for eligible older closed interventional ClinicalTrials.gov studies. Primary outputs compare current unresolved shares, shares reported within 12, 24, 36, and 60 months, lag distributions for reported studies, and overdue years beyond the two-year mark for unresolved studies. The aim is to separate very old unresolved debt from newer cohorts that are only beginning to drift into silence. Because timing is based on registry dates and current status, these outputs describe registry-visible age of debt rather than external-publication timing.

Outside Notes

Type: protocol
Primary estimand: Unresolved share and overdue years beyond the two-year mark among eligible older CT.gov studies
App: CT.gov Overdue Results Clock dashboard
Code: https://github.com/mahmood726-cyber/ctgov-overdue-results-clock
Date: 2026-03-29
Validation: historical analysis NOT independently reproduced; source and aggregation missing

References

1. ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.
2. DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.
3. Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.

AI Disclosure

This work represents a compiler-generated evidence micro-publication built from structured registry data and deterministic summary code. AI was used as a constrained coding and drafting assistant for interface generation, packaging, and prose refinement, not as an autonomous author. The analytical choices, interpretation, and final outputs were reviewed by the author, who takes responsibility for the content.
