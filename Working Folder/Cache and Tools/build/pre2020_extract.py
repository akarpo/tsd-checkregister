"""Extract embedded check registers from 2011-2019 meeting-packet PDFs under source_data/BoardDocs_PDFs_pre2020/.

Strategy:
- Scan every page of every meeting PDF
- Find pages where 'PENTAMATION' or 'CHECK REGISTER' marker appears
- Run the same parser logic, with em-dash → hyphen normalization (older PDFs use Unicode dashes)
- Use the meeting date (from folder name or filename) for source-meeting attribution

Outputs:
  build/pre2020_lines.pkl     — list of dicts (same schema as all_lines.pkl)
  build/pre2020_summary.txt   — per-file stats
"""
from __future__ import annotations
import sys, re, pickle, time
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from parser import LINE_RE, FUND_RE, parse_amount, parse_date, fy_for, SKIP_PREFIXES
import _paths
import pdfplumber

TROYSD = _paths.EMBEDDED_PDFS
BUILD = _paths.BUILD
OUT_PKL = _paths.PRE2020_PKL
SUMMARY = BUILD / 'pre2020_summary.txt'

DASH_TRANS = str.maketrans({'‐': '-', '‑': '-', '‒': '-', '–': '-',
                            '—': '-', '―': '-', '−': '-', '﹘': '-',
                            '﹣': '-', '－': '-'})
DATE_FN_RE = re.compile(r'^(\d{6})(.*Mtg\.pdf|.*Special\.pdf|.*RegMtg\.pdf|.*WkspMtg.*\.pdf|.*SpMtg.*\.pdf)$', re.I)
DATE_FOLDER_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})_')

def extract_meeting_date(pdf_path: Path) -> str:
    """Return meeting date YYYY-MM-DD given a PDF path.

    Priority:
    1. For BUNDLE folders ("Board Packets and Minutes"), use FILENAME date
       since the folder represents a year, not a single meeting.
    2. Per-meeting folder prefix YYYY-MM-DD_...
    3. Filename prefix MMDDYY fallback.
    """
    parent = pdf_path.parent.name
    is_bundle = 'Board Packets and Minutes' in parent
    fn = pdf_path.name

    if not is_bundle:
        m = DATE_FOLDER_RE.match(parent)
        if m:
            return m.group(1)

    # Filename like 040913Mtg.pdf or 011811Org_RegMtg.pdf
    m = re.match(r'^(\d{2})(\d{2})(\d{2})', fn)
    if m:
        mm, dd, yy = m.groups()
        yr = 2000 + int(yy)
        try:
            return datetime(yr, int(mm), int(dd)).strftime('%Y-%m-%d')
        except ValueError:
            return ''

    # Last resort: folder date (only used if filename has no date prefix)
    m = DATE_FOLDER_RE.match(parent)
    if m:
        return m.group(1)
    return ''

def _iter_page_texts(pdf_path: Path):
    """Yield (page_number, text) tuples. Try pdfplumber first; fall back to pypdf if it fails."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    yield i + 1, page.extract_text() or ''
                except Exception:
                    yield i + 1, ''
    except Exception:
        # pdfplumber failed entirely — try pypdf fallback
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(pdf_path))
            for i, page in enumerate(reader.pages):
                try:
                    yield i + 1, page.extract_text() or ''
                except Exception:
                    yield i + 1, ''
        except Exception as e:
            raise RuntimeError(f'both pdfplumber and pypdf failed: {e}')

def parse_pdf_for_register(pdf_path: Path):
    """Parse all pages, but only emit rows when we're inside a CHECK REGISTER section.
    Uses pdfplumber by default with pypdf fallback for PDFs that pdfplumber can't open."""
    meeting_date = extract_meeting_date(pdf_path)
    fy = fy_for(meeting_date) if meeting_date else ''

    rows = []
    cur_fund = None
    cur_fund_name = None
    in_register = False
    try:
        for _pg, text in _iter_page_texts(pdf_path):
            text = text.translate(DASH_TRANS)
            if 'PENTAMATION' in text and 'CHECK REGISTER' in text:
                in_register = True
            if not in_register:
                continue
            for line in text.splitlines():
                line = line.rstrip()
                if not line:
                    continue
                fm = FUND_RE.search(line)
                if fm:
                    cur_fund = fm.group('num')
                    cur_fund_name = fm.group('name').strip()
                    continue
                if any(line.lstrip().startswith(p) for p in SKIP_PREFIXES):
                    continue
                lm = LINE_RE.match(line)
                if not lm:
                    continue
                bu = lm.group('bu')
                func = bu[6:9] if bu.isdigit() and len(bu) >= 9 else ''
                rows.append({
                    'Source Meeting': meeting_date,
                    'Fiscal Year':    fy,
                    'Fund':           cur_fund or '',
                    'Fund Name':      cur_fund_name or '',
                    'Cash Acct':      lm.group('cash'),
                    'Check No':       lm.group('check'),
                    'Voided':         lm.group('voided') or '',
                    'Issue Date':     parse_date(lm.group('date')),
                    'Vendor ID':      lm.group('vendid'),
                    'Vendor Name':    lm.group('vendor').strip(),
                    'Budget Unit':    bu,
                    'Function Code':  func,
                    'Account':        lm.group('acct'),
                    'Description':    lm.group('desc').strip(),
                    'Sales Tax':      parse_amount(lm.group('tax')),
                    'Amount':         parse_amount(lm.group('amt')),
                })
    except Exception as e:
        return [], f'ERROR: {e}'
    return rows, ''

def main():
    # Collect all candidate PDFs in TroySD that contain meeting packets (not the
    # already-separate FY20+ check-register files).
    candidates = []
    for p in sorted(TROYSD.iterdir()):
        if not p.is_dir():
            continue
        # Skip 2020+ since we already have those as standalone PDFs
        if p.name.startswith(('2020-', '2021-', '2022-', '2023-', '2024-', '2025-', '2026-')):
            continue
        # Bundle folders (2011, 2012) contain many MtgPdfs
        if 'Board Packets and Minutes' in p.name:
            # Include ALL PDFs — some Workshop/Special meetings DID have registers attached.
            # The PENTAMATION marker filter inside parse_pdf_for_register decides what to use.
            for f in p.glob('*.pdf'):
                candidates.append(f)
        else:
            # Per-meeting folder for 2013-2019: should contain one MtgPdf
            for f in p.glob('*.pdf'):
                candidates.append(f)
    print(f'Candidate PDFs: {len(candidates)}', flush=True)

    all_rows = []
    summary = []
    t0 = time.time()
    for i, f in enumerate(candidates, 1):
        rows, err = parse_pdf_for_register(f)
        if err:
            summary.append((str(f.relative_to(TROYSD)), 0, 0.0, err))
            if i % 20 == 0:
                print(f'  [{i}/{len(candidates)}] {f.name[:40]} {err[:40]}', flush=True)
            continue
        all_rows.extend(rows)
        summary.append((str(f.relative_to(TROYSD)), len(rows), sum(r['Amount'] for r in rows), ''))
        if i % 20 == 0:
            elapsed = time.time() - t0
            print(f'  [{i}/{len(candidates)}] cumulative {len(all_rows):,} rows in {elapsed:.0f}s', flush=True)

    print(f'\nTotal: {len(all_rows):,} rows  ${sum(r["Amount"] for r in all_rows):,.2f}  in {time.time()-t0:.0f}s', flush=True)

    # FY breakdown
    fy_count = Counter()
    fy_amt = defaultdict(float)
    for r in all_rows:
        fy_count[r['Fiscal Year']] += 1
        fy_amt[r['Fiscal Year']] += r['Amount']
    print(f'\n{"FY":<8} {"Lines":>8} {"Amount":>16}')
    for fy in sorted(fy_count):
        print(f'{fy:<8} {fy_count[fy]:>8} ${fy_amt[fy]:>15,.2f}')

    # Per-file summary, top files with rows or errors
    OUT_PKL.write_bytes(pickle.dumps(all_rows))
    SUMMARY.write_text('\n'.join(
        f'{n}\t{c}\t{t:.2f}\t{e}' for n, c, t, e in summary), encoding='utf-8')
    print(f'\nSaved {OUT_PKL}', flush=True)
    print(f'Saved {SUMMARY}', flush=True)

    # Files with zero rows (probably workshop/special-meeting PDFs without registers)
    zero = [s for s in summary if s[1] == 0 and not s[3]]
    print(f'\nFiles with 0 rows (likely no register): {len(zero)}', flush=True)
    print(f'Files with errors: {sum(1 for s in summary if s[3])}', flush=True)

if __name__ == '__main__':
    main()
