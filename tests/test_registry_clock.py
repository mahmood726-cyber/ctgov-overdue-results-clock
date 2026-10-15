import gzip
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
from src.registry_clock import anniversary, classify, exact_day

ROOT = Path(__file__).resolve().parents[1]


def trial(*, nct="NCT00000001", pcd="2023-02-01", pcd_type="ACTUAL",
          posted=False, post_date=None, status="COMPLETED", kind="INTERVENTIONAL"):
    dates = {"primaryCompletionDateStruct": {"date": pcd, "type": pcd_type},
             "overallStatus": status}
    if post_date is not None:
        dates["resultsFirstPostDateStruct"] = {"date": post_date}
    return {"protocolSection": {
        "identificationModule": {"nctId": nct},
        "statusModule": dates,
        "designModule": {"studyType": kind},
        "sponsorCollaboratorsModule": {"leadSponsor": {"class": "INDUSTRY"}},
    }, "hasResults": posted}


def test_older_no_post_is_not_legal_violation():
    r = classify(trial(), date(2026, 3, 29))
    assert r["eligible_older_closed_interventional"]
    assert r["days_beyond_two_year_marker_without_post"] == 421
    assert r["no_posted_results_after_two_years"] is True
    assert r["act_applicability"] == r["statutory_overdue_status"] == "UNDETERMINED"


def test_calendar_anniversary_leap_day():
    assert anniversary(date(2024, 2, 29)) == date(2026, 3, 1)
    assert anniversary(date(2023, 3, 1), 1) == date(2024, 3, 1)
    assert exact_day("2020-02") is None
    assert exact_day("2020-02-30") is None


@pytest.mark.parametrize("kind,status", [
    ("OBSERVATIONAL", "COMPLETED"), ("INTERVENTIONAL", "RECRUITING"),
])
def test_outside_closed_interventional_cohort(kind, status):
    r = classify(trial(kind=kind, status=status), date(2026, 3, 29))
    assert not r["eligible_older_closed_interventional"]
    assert r["no_posted_results_after_two_years"] is None


@pytest.mark.parametrize("pcd,pcd_type", [
    ("2023-02", "ACTUAL"), ("2023-02-01", "ESTIMATED"), ("bad", "ACTUAL"),
])
def test_do_not_impute_primary_completion(pcd, pcd_type):
    r = classify(trial(pcd=pcd, pcd_type=pcd_type), date(2026, 3, 29))
    assert r["registry_posting_state"] == "UNKNOWN_ACTUAL_DAY_PRECISE_PCD"
    assert r["no_posted_results_after_two_years"] is None


def test_posted_before_and_after_two_year_marker():
    ontime = classify(trial(posted=True, post_date="2024-08-01"), date(2026, 3, 29))
    late = classify(trial(posted=True, post_date="2025-06-01"), date(2026, 3, 29))
    assert ontime["posted_within_two_calendar_years"] is True
    assert late["posted_within_two_calendar_years"] is False
    assert late["no_posted_results_after_two_years"] is False
    assert late["statutory_overdue_status"] == "UNDETERMINED"


def test_posted_without_date_not_timeliness():
    r = classify(trial(posted=True), date(2026, 3, 29))
    assert r["registry_posting_state"] == "RESULTS_POSTED_DATE_MISSING"
    assert r["posted_within_two_calendar_years"] is None
    assert r["no_posted_results_after_two_years"] is False


@pytest.mark.parametrize("post_date,posted", [
    ("2026-04-01", True), ("2025-03-01", False),
])
def test_conflicting_posting_fields_not_assessable(post_date, posted):
    r = classify(trial(posted=posted, post_date=post_date), date(2026, 3, 29))
    assert r["registry_posting_state"] == "INCONSISTENT_POSTING_FIELDS"
    assert r["no_posted_results_after_two_years"] is None


def test_negative_first_post_lag_quarantined():
    r = classify(trial(posted=True, post_date="2022-12-31"), date(2026, 3, 29))
    assert r["dated_posting_lag_days"] is None
    assert r["posted_within_two_calendar_years"] is None
    assert "first_post_date_before_actual_primary_completion" in r["data_quality_issues"]


def test_missing_hasresults_unknown_not_false():
    example = trial()
    example.pop("hasResults")
    r = classify(example, date(2026, 3, 29))
    assert r["registry_posting_state"] == "UNKNOWN_POSTING_STATUS"
    assert r["no_posted_results_after_two_years"] is None


def test_cli_gzip_manifest_integrity(tmp_path):
    original = tmp_path / "source.jsonl.gz"
    with gzip.open(original, "wt") as f:
        f.write(json.dumps(trial()) + "\n")
    target = tmp_path / "clock.jsonl"
    run = subprocess.run([sys.executable, str(ROOT / "src/registry_clock.py"),
        "--input", str(original), "--snapshot-date", "2026-03-29",
        "--output", str(target)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    summary = json.loads((tmp_path / "clock.jsonl.metadata.json").read_text())
    assert summary["record_count"] == 1
    assert summary["source_input_sha256"] == hashlib.sha256(original.read_bytes()).hexdigest()
    assert summary["derived_output_sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
    assert summary["legal_results_overdue"] == "UNDETERMINED"


def test_cli_duplicate_refuses_partial_output(tmp_path):
    original = tmp_path / "source.jsonl"
    original.write_text((json.dumps(trial()) + "\n") * 2)
    target = tmp_path / "clock.jsonl"
    run = subprocess.run([sys.executable, str(ROOT / "src/registry_clock.py"),
        "--input", str(original), "--snapshot-date", "2026-03-29",
        "--output", str(target)], capture_output=True, text=True)
    assert run.returncode != 0
    assert "Duplicate" in run.stderr
    assert not target.exists()
    assert not (tmp_path / "clock.jsonl.partial").exists()
