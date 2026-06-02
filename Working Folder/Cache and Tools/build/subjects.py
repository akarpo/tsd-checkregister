"""Curriculum / PD subject classification for budget-unit 101425221 lines.

Vendor-first lookup (build/lookups/vendor_subject.json, committed) with a
description-keyword fallback. Confidence mirrors the merge-stage logic that
produced the committed workbook (rebuild_after_bundlefix.py):

    high = vendor matched the lookup (by 15-char prefix)
    med  = no vendor match but a description keyword assigned a subject
    low  = no signal ('Not Directly Attributable')

This replaces the three near-identical copies that were inlined in
full_parse.py / rebuild_after_bundlefix.py / rebuild_with_issue_fy.py.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _paths

VENDOR_SUBJECT = json.loads(_paths.VENDOR_SUBJECT.read_text(encoding="utf-8"))

_KEYWORDS = (
    (("READING", "WRITING", "LITERACY", "CALKINS", "F&P", "FOUNTAS"), "ELA"),
    (("MATH", "AVMR", "MRSP", "BRIDGES", "ALGEBRA", "GEOMETRY"), "Math"),
    (("SCIENCE",), "Science"),
    (("SOCIAL",), "Social Studies"),
)


def classify_subject(vendor, desc):
    """Return the PD subject for a (vendor, description) pair."""
    if not vendor:
        return "Not Directly Attributable"
    for v_key, subj in VENDOR_SUBJECT.items():
        if vendor.startswith(v_key[:15]):
            return subj
    d = (desc or "").upper()
    for keys, subj in _KEYWORDS:
        if any(k in d for k in keys):
            return subj
    return "Not Directly Attributable"


def classify_confidence(vendor, subj):
    """Confidence label for a subject assignment (see module docstring)."""
    if vendor and any(vendor.startswith(v[:15]) for v in VENDOR_SUBJECT):
        return "high"
    if subj != "Not Directly Attributable":
        return "med"
    return "low"
