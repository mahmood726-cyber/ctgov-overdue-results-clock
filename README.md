# CT.gov Overdue Results Clock

**Methodological correction (15 October 2026):** The historical March 29, 2026 dashboard described 249,507 older closed interventional trials and reported “overdue debt” beyond two years. Those figures are retained for historical context but **have not been independently reproduced from a dated source dataset in this repository**. Do not interpret the two-year marker as an individual statutory reporting deadline, an FDAAA/Final Rule legal violation, or proof that results were never published elsewhere.

ClinicalTrials.gov first public results *posting* is different from results *submission*, and study-level reporting obligations depend on ACT status, trial era, product, exemptions, certifications, delays, waivers and extensions. See [42 CFR 11.22](https://www.law.cornell.edu/cfr/text/42/11.22), [11.42](https://www.law.cornell.edu/cfr/text/42/11.42), [11.44](https://www.law.cornell.edu/cfr/text/42/11.44).

## Reproducible descriptive registry clock

Run the new research-only `src/registry_clock.py` against genuine **frozen API v2** individual study objects, one JSON record per line (optional gzip):

```bash
python src/registry_clock.py --input ctgov-snapshot.jsonl.gz \
    --snapshot-date 2026-03-29 --output clock.jsonl
```

The snapshot date is **asserted by the user and cannot be authenticated by this script**. Do not pass live records with a historical date and infer an earlier registry state. The script detects duplicates, invalid or estimated primary completion dates, inconsistent posting indicators, future posting dates and undated results. It computes a **descriptive two-calendar-year marker** for closed interventional studies, never an individual legal due date. Output consists of per-NCT JSONL and a JSON metadata file with SHA-256 digests, status counts and denominators. ACT applicability, legal overdue and external publication remain explicitly `UNDETERMINED`.

The historical 249,507-study analysis needs its exact cohort data and original code to become reproducible. Descriptive posted-only lag medians condition on trials with posted results and must not be interpreted as unbiased survival estimates across differently censored cohorts. Run tests with `python -m pip install pytest && python -m pytest -q tests`.
