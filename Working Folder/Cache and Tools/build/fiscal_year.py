"""Fiscal-year attribution for Troy SD check-register lines.

Michigan school districts run a July 1 - June 30 fiscal year (MCL 388.1701 et
seq.), named by the ending year: FY26 = 2025-07-01 through 2026-06-30. Every
line item is attributed to the FY containing its ISSUE DATE — the date the
disbursement was actually made.

This replaces the earlier dual-column scheme (a "Fiscal Year" keyed to the board
meeting that approved the register, plus an "Issue Date FY" keyed to the
transaction). Meeting date is a workflow artifact: a register is approved one to
two months after the activity it covers, so a meeting-keyed FY systematically
shifts spend into the following year and, at the July boundary, into the
following FY entirely. `Source Meeting` is retained on every row as provenance,
but it no longer drives attribution.

DATE_CORRECTIONS fixes issue dates that are wrong *in the source PDFs* — the
district's Pentamation output prints them incorrectly, so a re-parse would
reintroduce them. Each entry records what the source says, what it should be,
and why.
"""
from datetime import datetime

# (Check No, Vendor ID, source date) -> (corrected date, rationale)
#
# Verified 2026-07-27 against the source registers re-pulled from BoardDocs;
# the bad dates are printed as-is in the PDFs, so this is a source-data defect,
# not a parse error. Both checks carry a "W22-" warrant prefix (FY22), and both
# corrections land in FY22, matching the register each appears in.
DATE_CORRECTIONS = {
    ('W22-042', '28283', datetime(2061, 9, 9)): (
        datetime(2021, 9, 9),
        'Sep 2021 register (approved 2021-11-16); day/month 09/09 intact, year 61 -> 21',
    ),
    ('W22-120', '10967', datetime(2031, 1, 1)): (
        datetime(2022, 1, 1),
        'Jan 2022 register (approved 2022-03-15); description "DEC 21 CLAIMS", year 31 -> 22',
    ),
}


def fiscal_year(issue_date):
    """FY label for an issue date, on the Michigan Jul 1 - Jun 30 boundary."""
    if not isinstance(issue_date, datetime):
        return ''
    if issue_date.month >= 7:
        return f'FY{(issue_date.year + 1) % 100:02d}'
    return f'FY{issue_date.year % 100:02d}'


def apply_corrections(rows):
    """Repair known-bad source issue dates in place; return the count applied."""
    applied = 0
    for r in rows:
        key = (r.get('Check No'), r.get('Vendor ID'), r.get('Issue Date'))
        fix = DATE_CORRECTIONS.get(key)
        if fix:
            r['Issue Date'] = fix[0]
            applied += 1
    return applied


def assign_fiscal_years(rows):
    """Apply date corrections, then set Fiscal Year from the issue date."""
    applied = apply_corrections(rows)
    for r in rows:
        r['Fiscal Year'] = fiscal_year(r.get('Issue Date'))
    return applied
