"""Regression guards for public interpretation of historical registry figures.

No test treats the unreproduced historical E156 aggregates as validated data.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("page", [
    "index.html", "dashboard.html", "e156-submission/index.html",
])
def test_prominent_historical_uncertainty_notice_on_public_pages(page):
    html = (ROOT / page).read_text(encoding="utf-8")
    assert html.count('class="methodology-notice"') == 1
    assert "not independently reproduced" in html.lower()
    assert "not an ACT/FDAAA" in html
    assert "results posting" in html.lower()
    assert "submission" in html.lower()
    assert "external publication" in html.lower() or "external journal publication" in html.lower()
    assert html.index('class="methodology-notice"') < html.index('class="hero"') if page in ("index.html", "dashboard.html") else html.index('class="methodology-notice"') < html.index('class="body-section"')


@pytest.mark.parametrize("document", [
    "E156-PROTOCOL.md", "e156-submission/paper.md",
    "e156-submission/protocol.md",
])
def test_scientific_validity_documented_in_historical_text(document):
    text = (ROOT / document).read_text(encoding="utf-8")
    assert "not been independently reproduced" in text
    assert "not a statutory ACT/FDAAA" in text
    assert "FULL REGISTRY RUN" not in text


@pytest.mark.parametrize("document", [
    "e156-submission/config.json", "e156-submission/paper.json",
])
def test_json_historical_validation_not_misrepresented(document):
    data = json.loads((ROOT / document).read_text(encoding="utf-8"))
    assert "not independently reproduced" in data["notes"]["validation"]
    assert "descriptive, not statutory" in data["notes"]["reproducibility"]
    assert "FULL REGISTRY RUN" not in data["notes"]["validation"]
