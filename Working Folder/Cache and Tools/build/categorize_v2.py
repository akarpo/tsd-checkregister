"""Categorization v2 — vendor lookup with fund/function disambiguation for multi-cat vendors.

The vendor->category seed lives in build/lookups/vendor_categories.json (committed,
re-derived from the dashboard payload by build_lookups.py). Vendors not in the seed
fall through to pure rule-based categorization (_default_categorize)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _paths

# {vendor: {category: total}} — vendor-first categorization seed.
VENDOR_CATS = json.loads(_paths.VENDOR_CATEGORIES.read_text(encoding="utf-8"))


def categorize(vendor, fund, func, account, bu, amt):
    fund = (fund or '').strip()
    func = (func or '').strip()
    account = (account or '').strip()
    bu = (bu or '').strip()
    cats = VENDOR_CATS.get(vendor or '')
    if not cats:
        return _default_categorize(fund, func, account, bu, amt)
    if len(cats) == 1:
        return list(cats.keys())[0]

    # Multi-category vendor — disambiguate via signature
    f2 = func[:2] if len(func) >= 2 else func
    f3 = func[:3] if len(func) >= 3 else func

    def maybe(name):
        return name if name in cats else None

    # Substitute teacher payroll (account L4026) — categorize by fund
    if account == 'L4026':
        if fund == '101':
            return maybe('Instruction — Substitute Teachers (General Classes)') or _max(cats)
        if fund == '122':
            return maybe('Instruction — Substitute Teachers (Special Education)') or _max(cats)
        if fund == '531':
            return maybe('Community — Childcare / Latchkey') or _max(cats)
        if fund == '530':
            return maybe('Instruction — Adult / Continuing Ed') or _max(cats)
        if fund == '120':
            return maybe('Instruction — Compensatory Education') or _max(cats)

    # Function-code first
    if f3 in ('111','112','113','114','115','116','117','118','119'):
        return maybe('Instruction — Basic Programs (Elementary/Secondary)') or _max(cats)
    if f3 == '122':
        return maybe('Instruction — Special Education') or _max(cats)
    if f3 == '125':
        return maybe('Instruction — Compensatory Education') or _max(cats)
    if f2 == '13':
        return maybe('Instruction — Adult / Continuing Ed') or _max(cats)
    if f2 == '14':
        return maybe('Instruction — Vocational / CTE') or _max(cats)
    if f2 == '21':
        return maybe('Support — Pupil Services (Counsel/Health/Psych)') or _max(cats)
    if f2 == '22':
        return maybe('Support — Instructional Staff (PD/Curriculum)') or _max(cats)
    if f2 == '23':
        return maybe('Support — General Administration') or _max(cats)
    if f2 == '24':
        return maybe('Support — School Administration') or _max(cats)
    if f3 == '252':
        return maybe('Support — Business Services') or _max(cats)
    if f2 == '25':
        return maybe('Support — Central Services / Personnel') or _max(cats)
    if f2 == '26':
        return maybe('Support — Operations & Maintenance') or _max(cats)
    if f2 == '27':
        return maybe('Support — Transportation') or _max(cats)
    if f2 in ('28', '29'):
        return maybe('Support — Other') or _max(cats)
    if f2 == '33':
        return maybe('Community — Athletics & Activities') or _max(cats)
    if f2 in ('32', '34', '35', '39', '41'):
        return maybe('Community — Other Services') or _max(cats)
    if f2 in ('45', '46'):
        return maybe('Capital Outlay — Land/Buildings') or _max(cats)
    if f2 == '51':
        return maybe('Debt Service') or _max(cats)

    # No function code or unrecognized — use fund signal
    if not func or func == '000':
        if account.startswith('L'):
            return maybe('Payroll Deductions / Garnishments') or maybe('Untyped (function code blank or 000)') or _max(cats)
        if maybe('Untyped (function code blank or 000)'):
            return 'Untyped (function code blank or 000)'
    if fund == '520':
        return maybe('Food Service Fund — Untyped') or maybe('Food Service — Lunch Account Refunds') or _max(cats)
    if fund == '531':
        return maybe('Community — Childcare / Latchkey') or _max(cats)
    if fund == '529':
        return maybe('Instruction — Vocational / CTE') or _max(cats)
    if fund == '530':
        return maybe('Instruction — Adult / Continuing Ed') or _max(cats)
    if fund in ('700', '701', '750'):
        return maybe('Student Activity Fund — Untyped') or _max(cats)
    if fund.startswith('4') and len(fund) == 3:
        return maybe('Capital Outlay — Land/Buildings') or _max(cats)
    if fund.startswith('3') and len(fund) == 3:
        return maybe('Debt Service') or _max(cats)
    return _max(cats)


def _max(cats):
    return max(cats.keys(), key=lambda k: cats[k])


def _default_categorize(fund, func, account, bu, amt):
    """For vendors not seen in FY23-FY26 payload — apply pure rule-based categorization."""
    f2 = func[:2] if len(func) >= 2 else func
    f3 = func[:3] if len(func) >= 3 else func
    sub_acct = account in ('1240', '1241')
    if f3 in ('111','112','113','114','115','116','117','118','119'):
        return 'Instruction — Substitute Teachers (General Classes)' if sub_acct else 'Instruction — Basic Programs (Elementary/Secondary)'
    if f3 == '122':
        return 'Instruction — Substitute Teachers (Special Education)' if sub_acct else 'Instruction — Special Education'
    if f3 == '125':
        return 'Instruction — Substitute Teachers (Special Education)' if sub_acct else 'Instruction — Compensatory Education'
    if f2 == '13': return 'Instruction — Adult / Continuing Ed'
    if f2 == '14': return 'Instruction — Vocational / CTE'
    if f2 == '21': return 'Support — Pupil Services (Counsel/Health/Psych)'
    if f2 == '22': return 'Support — Instructional Staff (PD/Curriculum)'
    if f2 == '23': return 'Support — General Administration'
    if f2 == '24': return 'Support — School Administration'
    if f3 == '252': return 'Support — Business Services'
    if f2 == '25': return 'Support — Central Services / Personnel'
    if f2 == '26': return 'Support — Operations & Maintenance'
    if f2 == '27': return 'Support — Transportation'
    if f2 in ('28', '29'): return 'Support — Other'
    if f2 == '33': return 'Community — Athletics & Activities'
    if f2 in ('32', '34', '35', '39', '41'): return 'Community — Other Services'
    if f2 in ('45', '46'): return 'Capital Outlay — Land/Buildings'
    if f2 == '51': return 'Debt Service'
    if account.startswith('L'): return 'Payroll Deductions / Garnishments'
    if fund.startswith('4') and len(fund) == 3: return 'Capital Outlay — Land/Buildings'
    if fund.startswith('3') and len(fund) == 3: return 'Debt Service'
    if fund == '520': return 'Food Service Fund — Untyped'
    if fund in ('700','701','750'): return 'Student Activity Fund — Untyped'
    if fund == '529': return 'Instruction — Vocational / CTE'
    if fund == '530': return 'Instruction — Adult / Continuing Ed'
    if fund == '531': return 'Community — Childcare / Latchkey'
    if bu and len(bu) <= 4: return 'Payroll Batch (Function not coded)'
    if amt < 0 and not func: return 'Refunds / Credits'
    return 'Untyped (function code blank or 000)'


if __name__ == "__main__":
    # Smoke test: re-categorize the committed workbook and print category totals.
    # Full reconciliation lives in validate.py.
    import openpyxl
    from collections import defaultdict
    wb = openpyxl.load_workbook(_paths.WORKBOOK, read_only=True, data_only=True)
    actual = defaultdict(float)
    for r in wb["All Lines"].iter_rows(values_only=True):
        if r[0] == "Source Meeting":
            continue
        # All Lines schema: [3]=Fund [10]=Vendor Name [11]=Budget Unit [12]=Function Code [13]=Account [16]=Amount
        cat = categorize(r[10] or "", str(r[3] or ""), str(r[12] or ""),
                         str(r[13] or ""), str(r[11] or ""), r[16] or 0)
        actual[cat] += r[16] or 0
    wb.close()
    print(f"{len(VENDOR_CATS):,} vendors in seed; {len(actual)} categories assigned")
    for cat in sorted(actual, key=lambda c: -actual[c]):
        print(f"  {cat:<55} ${actual[cat]:>14,.2f}")
    print(f"  {'GRAND TOTAL':<55} ${sum(actual.values()):>14,.2f}")
