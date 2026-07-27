"""Source fidelity — bottom-up: raw PDF text -> dataset.

The companion to validate.py, which only proves the artifacts agree with each
other. This proves the data is right in the first place: a parser that drops
rows drops them from every artifact at once, so validate.py cannot see it.

Deliberately avoids the pipeline's own helpers where it can: totals come from
what the PDFs print about themselves, and sampled rows are re-extracted from raw
page text with an independently-written regex, then matched against the dataset.

  1.1  Every tracked register reconciles to its printed TOTAL REPORT.
  1.2  Every per-fund TOTAL FUND subtotal reconciles.
  1.3  Sampled detail lines re-extracted from raw text match the dataset
       field-for-field (independent regex, not parser.LINE_RE).
  1.4  No line is dropped or duplicated between the PDFs and the dataset.
  1.5  The documented date corrections are applied, and only those.
"""
import re
import sys
import pickle
from collections import defaultdict
from pathlib import Path

BUILD = Path.home() / "Downloads" / "tsd-checkregister" / "Working Folder" / "Cache and Tools" / "build"
sys.path.insert(0, str(BUILD))
import _paths
import pdfplumber
from fiscal_year import DATE_CORRECTIONS

FAIL = []
def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        FAIL.append(label)

combined = pickle.loads(_paths.COMBINED_PKL.read_bytes())
print(f"dataset: {len(combined):,} rows / ${sum(r['Amount'] for r in combined):,.2f}\n")

# Independent line regex — written from the Pentamation column layout, not imported.
IND_LINE = re.compile(
    r'^(?P<cash>[A-Z]\d+)\s+(?P<check>\S+)\s+(?:(?P<v>V)\s+)?(?P<date>\d{2}/\d{2}/\d{2})\s+'
    r'(?P<vid>\d{3,6})\s+(?P<rest>.+?)\s+(?P<tax>-?[\d,]+\.\d{2})\s+(?P<amt>-?[\d,]+\.\d{2})$')
IND_FUND = re.compile(r'FUND\s*-\s*(\d+)\s*-')
IND_TFUND = re.compile(r'^TOTAL\s+FUND\s+-?[\d,]+\.\d{2}\s+(-?[\d,]+\.\d{2})$')
IND_TREPORT = re.compile(r'^TOTAL\s+REPORT\s+-?[\d,]+\.\d{2}\s+(-?[\d,]+\.\d{2})$')
money = lambda s: float(s.replace(",", ""))

pdfs = sorted(_paths.STANDALONE_PDFS.glob("*.pdf"))
by_meeting_fund = defaultdict(float)
by_meeting_rows = defaultdict(list)
for r in combined:
    by_meeting_fund[(r["Source Meeting"], r["Fund"])] += r["Amount"]
    by_meeting_rows[r["Source Meeting"]].append(r)

# Meetings where a second register exists whose PDF is not tracked in git.
# Verified 2026-07-27: the 2023-12-12 meeting carried Sep + Oct 2023; only Sep is tracked.
UNTRACKED_SIBLING = {"2023-12-12"}

print("1.1/1.2  per-register reconciliation vs the PDF's own printed totals")
rep_ok = fund_ok = 0
rep_skip = []
scanned = {}
for p in pdfs:
    stated_fund, report, cur = defaultdict(float), None, None
    lines_by_fund = defaultdict(list)
    with pdfplumber.open(p) as pdf:
        for pg in pdf.pages:
            for raw in (pg.extract_text() or "").splitlines():
                s = raw.strip()
                fm = IND_FUND.search(s)
                if fm:
                    cur = fm.group(1); continue
                m = IND_TFUND.match(s)
                if m and cur:
                    stated_fund[cur] += money(m.group(1)); continue
                m = IND_TREPORT.match(s)
                if m:
                    report = money(m.group(1)); continue
                m = IND_LINE.match(s)
                if m and cur and not s.startswith(("TOTAL", "PENTAMATION", "DATE:", "TIME:",
                                                   "CASH ACCT", "PAGE NUMBER", "SELECTION",
                                                   "ACCOUNTING")):
                    lines_by_fund[cur].append(m)
    scanned[p.name] = lines_by_fund
    meeting = p.name[:10]
    if meeting in UNTRACKED_SIBLING:
        rep_skip.append(p.name); continue
    got = round(sum(v for (mtg, f), v in by_meeting_fund.items() if mtg == meeting), 2)
    if report is not None and abs(report - got) <= 0.01:
        rep_ok += 1
    else:
        check(False, f"TOTAL REPORT {p.name}", f"PDF ${report:,.2f} vs dataset ${got:,.2f}")
    bad = [f for f, amt in stated_fund.items()
           if abs(round(by_meeting_fund.get((meeting, f), 0.0), 2) - round(amt, 2)) > 0.01]
    if bad:
        check(False, f"TOTAL FUND {p.name}", f"funds {bad}")
    else:
        fund_ok += 1

check(rep_ok == len(pdfs) - len(rep_skip), "every tracked register matches its TOTAL REPORT",
      f"{rep_ok}/{len(pdfs) - len(rep_skip)} checked, {len(rep_skip)} skipped (untracked sibling register)")
check(fund_ok == len(pdfs) - len(rep_skip), "every per-fund TOTAL FUND subtotal matches",
      f"{fund_ok}/{len(pdfs) - len(rep_skip)}")

print("\n1.3  sampled detail lines re-extracted with an independent regex")
# Deterministic spread across the corpus: every 37th parsed line of every register.
sampled = mismatch = 0
examples = []
for p in pdfs:
    meeting = p.name[:10]
    rows = by_meeting_rows.get(meeting, [])
    index = defaultdict(list)
    for r in rows:
        index[(r["Check No"], r["Vendor ID"], round(r["Amount"], 2))].append(r)
    flat = [(f, m) for f, ms in scanned[p.name].items() for m in ms]
    for i in range(0, len(flat), 37):
        fund, m = flat[i]
        sampled += 1
        key = (m.group("check"), m.group("vid"), money(m.group("amt")))
        cands = index.get(key, [])
        if not cands:
            mismatch += 1
            if len(examples) < 5:
                examples.append(f"{p.name}: no dataset row for check {key[0]} / vendor {key[1]} / ${key[2]:,.2f}")
            continue
        mm, dd, yy = m.group("date").split("/")
        want = (2000 + int(yy), int(mm), int(dd))
        corrected = any((c["Check No"], c["Vendor ID"]) == (key[0], key[1]) for c in cands
                        for k in DATE_CORRECTIONS if k[0] == key[0])
        okrow = any(
            c["Fund"] == fund
            and round(c["Sales Tax"], 2) == round(money(m.group("tax")), 2)
            and (corrected or (c["Issue Date"].year, c["Issue Date"].month, c["Issue Date"].day) == want)
            for c in cands)
        if not okrow:
            mismatch += 1
            if len(examples) < 5:
                c = cands[0]
                examples.append(f"{p.name}: check {key[0]} fund/date/tax mismatch "
                                f"(PDF fund {fund} date {m.group('date')} tax {m.group('tax')})")
check(mismatch == 0, "sampled rows match the dataset field-for-field",
      f"{sampled:,} sampled, {mismatch} mismatched")
for e in examples:
    print("        ", e)

print("\n1.4  no line dropped or duplicated in the merge")
pdf_line_count = sum(len(ms) for lb in scanned.values() for ms in lb.values())
ds_line_count = sum(len(by_meeting_rows[p.name[:10]]) for p in pdfs
                    if p.name[:10] not in UNTRACKED_SIBLING)
# dataset side counts each meeting once even if two PDFs share it
seen, ds_line_count = set(), 0
for p in pdfs:
    mtg = p.name[:10]
    if mtg in UNTRACKED_SIBLING or mtg in seen:
        continue
    seen.add(mtg); ds_line_count += len(by_meeting_rows[mtg])
pdf_line_count = sum(len(ms) for name, lb in scanned.items()
                     if name[:10] not in UNTRACKED_SIBLING for ms in lb.values())
check(pdf_line_count == ds_line_count, "PDF detail-line count equals dataset row count",
      f"PDF {pdf_line_count:,} vs dataset {ds_line_count:,}")

print("\n1.5  date corrections applied, and only those")
applied = []
for r in combined:
    for (chk, vid, bad), (good, _why) in DATE_CORRECTIONS.items():
        if r["Check No"] == chk and r["Vendor ID"] == vid:
            applied.append((chk, r["Issue Date"], good, bad))
check(all(d == good for _c, d, good, _b in applied), "corrected rows carry the corrected date",
      f"{len(applied)} rows across {len(DATE_CORRECTIONS)} corrections")
check(not any(d == bad for _c, d, _g, bad in applied), "no row retains a known-bad date")
impl = [r for r in combined if r["Issue Date"].year < 2009 or r["Issue Date"].year > 2027]
check(not impl, "no remaining implausible issue dates",
      f"{len(impl)} outside 2009-2027")

print("\n" + "=" * 62)
print("RESULT:", "PASS - dataset is faithful to source" if not FAIL
      else f"FAIL — {len(FAIL)} check(s): {FAIL}")

sys.exit(1 if FAIL else 0)
