#!/usr/bin/env python3
"""Research-only results-posting clock for a *frozen* ClinicalTrials.gov v2 JSONL snapshot.

A two-year no-posting window is descriptive, not a legal deadline. Posted results
are not synonymous with results submission or external publication.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

CLOSED = {"COMPLETED", "TERMINATED"}


def exact_day(raw):
    if not isinstance(raw, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw) is None:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def anniversary(start, years=2):
    """Calendar anniversary; Feb 29 -> Mar 1 in non-leap anniversary years."""
    try:
        return start.replace(year=start.year + years)
    except ValueError:
        return date(start.year + years, 3, 1)


def lookup(record, *keys):
    for k in keys:
        if not isinstance(record, dict):
            return None
        record = record.get(k)
    return record


def classify(study, snapshot_date):
    """Classify registry visibility only; never ACT applicability or violations."""
    nct = lookup(study, "protocolSection", "identificationModule", "nctId")
    if not isinstance(nct, str) or re.fullmatch(r"NCT[0-9]{8}", nct) is None:
        raise ValueError("Missing or invalid NCT ID")
    status = lookup(study, "protocolSection", "statusModule") or {}
    design = lookup(study, "protocolSection", "designModule") or {}
    raw_pcd = (status.get("primaryCompletionDateStruct") or {})
    raw_post = (status.get("resultsFirstPostDateStruct") or {})
    pcd = exact_day(raw_pcd.get("date")) if raw_pcd.get("type") == "ACTUAL" else None
    post = exact_day(raw_post.get("date"))
    present = study.get("hasResults")
    if type(present) is not bool:
        present = None
    study_type = design.get("studyType")
    state_status = status.get("overallStatus")
    aged = pcd is not None and pcd <= snapshot_date and snapshot_date >= anniversary(pcd)
    in_cohort = study_type == "INTERVENTIONAL" and state_status in CLOSED
    older = bool(in_cohort and aged)
    issue = []
    if not in_cohort:
        state = "OUTSIDE_CLOSED_INTERVENTIONAL_COHORT"
    elif pcd is None:
        state = "UNKNOWN_ACTUAL_DAY_PRECISE_PCD"
    elif pcd > snapshot_date:
        state = "INCONSISTENT_FUTURE_ACTUAL_PCD"
    elif present is None:
        state = "UNKNOWN_POSTING_STATUS"
    elif raw_post.get("date") and post is None:
        state = "UNKNOWN_POSTING_DATE_PRECISION"
    elif post and (post > snapshot_date or not present):
        state = "INCONSISTENT_POSTING_FIELDS"
    elif present and post is None:
        state = "RESULTS_POSTED_DATE_MISSING"
    elif present:
        state = "RESULTS_POSTED_DATED"
    else:
        state = "NO_POSTED_RESULTS"

    posting_lag = None
    by_two_years = None
    if state == "RESULTS_POSTED_DATED":
        posting_lag = (post - pcd).days
        if posting_lag < 0:
            issue.append("first_post_date_before_actual_primary_completion")
            posting_lag = None
        else:
            by_two_years = post <= anniversary(pcd)
    if state in {"UNKNOWN_POSTING_DATE_PRECISION", "INCONSISTENT_POSTING_FIELDS"}:
        issue.append("posted_results_fields_need_record_level_review")
    if state == "RESULTS_POSTED_DATE_MISSING":
        issue.append("reported_results_present_but_first_post_date_unknown")

    older_without_post = older and state == "NO_POSTED_RESULTS"
    older_known_posting = older and state in {"NO_POSTED_RESULTS", "RESULTS_POSTED_DATED", "RESULTS_POSTED_DATE_MISSING"}
    # Neither the two-year screen nor the statutory applicability can establish legal overdue status.
    return {
        "nctId": nct,
        "source_snapshot_date_user_asserted": snapshot_date.isoformat(),
        "study_type": study_type,
        "overall_status": state_status,
        "lead_sponsor_class": lookup(study, "protocolSection", "sponsorCollaboratorsModule", "leadSponsor", "class"),
        "source_pcd": raw_pcd.get("date"),
        "source_pcd_type": raw_pcd.get("type"),
        "source_first_post_date": raw_post.get("date"),
        "hasResults": present,
        "registry_posting_state": state,
        "eligible_older_closed_interventional": older,
        "dated_posting_lag_days": posting_lag,
        "posted_within_two_calendar_years": by_two_years,
        "no_posted_results_after_two_years": older_without_post if older_known_posting else None,
        "days_beyond_two_year_marker_without_post": (
            (snapshot_date - anniversary(pcd)).days if older_without_post else None
        ),
        "data_quality_issues": issue,
        "act_applicability": "UNDETERMINED",
        "statutory_overdue_status": "UNDETERMINED",
        "external_publication_status": "UNDETERMINED",
    }


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def study_rows(path):
    with (gzip.open if path.suffix == ".gz" else open)(path, "rt", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError("Invalid JSONL line " + str(number)) from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Frozen API v2 study .jsonl[.gz]")
    parser.add_argument("--snapshot-date", required=True, help="Original frozen-source date, YYYY-MM-DD")
    parser.add_argument("--output", type=Path, required=True, help="Per-NCT classified JSONL")
    args = parser.parse_args()
    when = exact_day(args.snapshot_date)
    if when is None:
        parser.error("Use day-precise YYYY-MM-DD for --snapshot-date")
    metadata = args.output.with_suffix(args.output.suffix + ".metadata.json")
    temporary = args.output.with_suffix(args.output.suffix + ".partial")
    if args.input.resolve() in {args.output.resolve(), metadata.resolve(), temporary.resolve()}:
        parser.error("Source and destination paths must be different")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    seen, states, older_states = set(), Counter(), Counter()
    # The output must attest to the bytes actually classified, not a later
    # revision of a source file changed during this potentially long run.
    source_sha256_before = digest(args.input)
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            for trial in study_rows(args.input):
                row = classify(trial, when)
                if row["nctId"] in seen:
                    raise ValueError("Duplicate source NCT ID: " + row["nctId"])
                seen.add(row["nctId"])
                states[row["registry_posting_state"]] += 1
                if row["eligible_older_closed_interventional"]:
                    older_states[row["registry_posting_state"]] += 1
                handle.write(json.dumps(row, sort_keys=True) + "\n")
        if not seen:
            raise ValueError("Refusing to publish an empty source dataset")
        if digest(args.input) != source_sha256_before:
            raise ValueError("Source input changed during classification; refusing mismatched provenance")
        temporary.replace(args.output)
    finally:
        temporary.unlink(missing_ok=True)
    provenance = {
        "source_snapshot_date_user_asserted": when.isoformat(),
        "source_input_sha256": source_sha256_before,
        "derived_output_sha256": digest(args.output),
        "record_count": len(seen),
        "states_all": dict(sorted(states.items())),
        "states_older_closed_interventional": dict(sorted(older_states.items())),
        "older_cohort_denominator": sum(older_states.values()),
        "legal_results_overdue": "UNDETERMINED",
        "historical_249507_record_estimates_reproduced": False,
        "limitations": [
            "Snapshot provenance/date is asserted, not verified by this script.",
            "Cannot recover a past registry state from current records.",
            "Two calendar years is a descriptive threshold, not a statutory due date.",
            "First results posting is not results submission or external publication.",
            "ACT status, responsible parties, certifications, delays and waivers require adjudication.",
            "Posted-only lag summaries are conditioned on having posted results.",
        ],
    }
    metadata.write_text(json.dumps(provenance, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("Classified " + str(len(seen)) + " records; legal status remains UNDETERMINED.")


if __name__ == "__main__":
    main()
