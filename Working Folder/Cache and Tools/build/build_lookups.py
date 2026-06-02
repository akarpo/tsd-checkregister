"""Re-derive the two classification lookups from the committed deliverables.

The original pipeline read these from machine-local ``%TEMP%`` files
(``vendor_subject.pkl`` and ``dashboard_payload.json``) that no longer exist.
Both are fully recoverable from artifacts that ARE committed, so this script
regenerates them and writes them into ``build/lookups/`` as JSON, making the
pipeline self-contained:

  * ``vendor_categories.json`` -- {vendor: {category: total}}, extracted from
    the inlined ``<script id="data-payload">`` in ``index.html``. Seeds the
    vendor-first categorization in ``categorize_v2.py``.

  * ``vendor_subject.json`` -- {vendor: subject}, reconstructed from the
    high-confidence rows of the workbook's ``Curriculum_PD`` sheet (those are
    exact vendor matches) merged with the hand-identified pre-2020 vendors
    (the ``EXPANDED`` table below, lifted verbatim from the now-archived
    ``expand_subject_lookup.py`` so the knowledge stays in the live pipeline).

Run after any change that legitimately alters categories/subjects; commit the
resulting JSON. Idempotent.
"""
from __future__ import annotations
import json
import re
from collections import defaultdict

import openpyxl

import _paths

# Pre-2020 vendor -> subject identifications (manual review of FY12-FY19
# 'Not Directly Attributable' Curriculum_PD lines). 19-char prefix matching.
EXPANDED = {
    # ELA / Literacy
    "GREENWOOD PUBLISHIN": "ELA",
    "THE READING AND WRI": "ELA",
    "NATALIE HAEZEBROUCK": "ELA",
    "MI READING ASSOC (M": "ELA",
    "LAMINACK LESTER": "ELA",
    "OAKLAND UNIVERSITY": "ELA",
    # Science
    "BATTLE CREEK PUBLIC": "Science",
    "NATL SCIENCE TEACHE": "Science",
    "CREAN JASON J": "Science",
    # Health / Safety (CPR / First Aid / PE)
    "C P R PLUS": "Health / Safety",
    "BEAUMONT HOSPITAL-T": "Health / Safety",
    "WILLIAM BEAUMONT HO": "Health / Safety",
    "BAINES BRYAN": "Health / Safety",
    "BAINES BRIAN K": "Health / Safety",
    "ASHOK HOLDINGS INC": "Health / Safety",
    "BALAMUCKI SUSAN M": "Health / Safety",
    # Leadership / Coaching
    "THE DANIELSON GROUP": "Leadership / Coaching",
    "MI INST FOR EDUCATI": "Leadership / Coaching",
    "RITCHHART RONALD E": "Leadership / Coaching",
    "MIRAKOVITS KATHY J": "Leadership / Coaching",
    "ALL MI COUNSELORS F": "Leadership / Coaching",
    # Equity / Culturally Responsive
    "R & J CONSULTING GR": "Equity / Culturally Responsive",
    "METZGER KURT ROBERT": "Equity / Culturally Responsive",
    # Whole Child / SEL (Early Childhood)
    "PARSONS STEPHANIE": "Whole Child / SEL",
    "HUMPHREY JENNIFER": "Whole Child / SEL",
    "OAKLAND SCHOOLS": "Whole Child / SEL",
    # Maker / Innovation (tech-focused PD)
    "JR ABUD GARY G": "Maker / Innovation",
    "TODD CINDY": "Maker / Innovation",
    "APPLE COMPUTER INC": "Maker / Innovation",
    # Arts (Visual/Performing)
    "NOTEFLIGHT LLC": "Arts (Visual/Performing)",
    # World Languages
    "TYLER HANCSAK": "World Languages",
    "OAKLAND UNIVERSITY/": "World Languages",
    "COLLEGE BOARD MWRO": "World Languages",
    # Assessment / Data
    "CALE ELLEN": "Assessment / Data",
    "METRO DETROIT BUREA": "Assessment / Data",
    # Materials / Logistics
    "KONICA MINOLTA BUSI": "Materials / Logistics",
    "AN CLAWSON - TROY C": "Materials / Logistics",
    "IMPRESSION CENTER": "Materials / Logistics",
    "STAPLES ADVANTAGE": "Materials / Logistics",
    "METROPOLITAN PUBLIS": "Materials / Logistics",
    "UNITED PARCEL SERVI": "Materials / Logistics",
    "K R COMPANY LLC": "Materials / Logistics",
    "V S C INC": "Materials / Logistics",
    "HEWLETT PACKARD CO": "Materials / Logistics",
    "C D W GOVERNMENT IN": "Materials / Logistics",
    "NETECH CORP": "Materials / Logistics",
    "DELL MARKETING LP": "Materials / Logistics",
    "PRESIDIO HOLDINGS I": "Materials / Logistics",
    "MICRO CENTER SALES": "Materials / Logistics",
    "INACOMP TECHNICAL S": "Materials / Logistics",
    "MARY KELSEY WITT": "Materials / Logistics",
    "HALL RHODA": "Materials / Logistics",
    "ANDREA MCCUNE": "Materials / Logistics",
    "GINGER PETTY": "Materials / Logistics",
    "HAVEN": "Materials / Logistics",
}


def build_vendor_categories() -> dict:
    """Extract {vendor: {category: total}} from the inlined dashboard payload."""
    html = _paths.DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'<script id="data-payload"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        raise SystemExit("Could not find <script id=\"data-payload\"> in index.html")
    payload = json.loads(m.group(1))
    cats = defaultdict(lambda: defaultdict(float))
    for cat, data in payload["all"]["categories"].items():
        for _fy, vlist in data.get("vendorsByYear", {}).items():
            for v in vlist:
                cats[v["v"]][cat] += v["t"]
    return {v: {c: round(t, 2) for c, t in sorted(d.items())} for v, d in cats.items()}


def build_vendor_subject() -> dict:
    """Reconstruct {vendor: subject} from Curriculum_PD high-confidence rows + EXPANDED."""
    wb = openpyxl.load_workbook(_paths.WORKBOOK, read_only=True)
    ws = wb["Curriculum_PD"]
    high = {}
    seen_header = False
    for row in ws.iter_rows(values_only=True):
        if not seen_header:
            if row and row[0] == "Source Meeting":
                seen_header = True
            continue
        vendor, subject, confidence = row[5], row[9], row[10]
        if confidence == "high" and vendor and subject:
            high[vendor] = subject
    wb.close()
    # EXPANDED wins on collision (matches the original expand_subject_lookup.py intent).
    merged = dict(high)
    merged.update(EXPANDED)
    return merged, len(high)


def _dump(obj: dict, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=1)
        f.write("\n")


def main() -> None:
    cats = build_vendor_categories()
    _dump(cats, _paths.VENDOR_CATEGORIES)
    multi = sum(1 for d in cats.values() if len(d) > 1)
    print(f"vendor_categories.json: {len(cats):,} vendors ({multi} multi-category) "
          f"-> {_paths.VENDOR_CATEGORIES.relative_to(_paths.REPO_ROOT)}")

    subj, n_high = build_vendor_subject()
    _dump(subj, _paths.VENDOR_SUBJECT)
    print(f"vendor_subject.json:    {len(subj)} vendors "
          f"({n_high} from Curriculum_PD high-confidence + {len(EXPANDED)} hand-identified) "
          f"-> {_paths.VENDOR_SUBJECT.relative_to(_paths.REPO_ROOT)}")


if __name__ == "__main__":
    main()
