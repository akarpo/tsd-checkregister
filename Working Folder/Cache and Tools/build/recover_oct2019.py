"""Recover the Oct 15, 2019 meeting register using pypdf as fallback parser."""
import sys, pickle, re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from parser import LINE_RE, FUND_RE, parse_amount, parse_date, fy_for, SKIP_PREFIXES
import _paths

from pypdf import PdfReader

ERRORED = _paths.EMBEDDED_PDFS / '2019-01-01_2019 Board Packets and Minutes' / '101519RegMtg.pdf'

DASH_TRANS = str.maketrans({'‐': '-', '‑': '-', '‒': '-', '–': '-',
                            '—': '-', '―': '-', '−': '-', '﹘': '-',
                            '﹣': '-', '－': '-'})

def parse_with_pypdf(pdf_path):
    """Parse register lines from PDF using pypdf instead of pdfplumber."""
    # Filename: 101519RegMtg.pdf → meeting date 2019-10-15
    fn = pdf_path.name
    m = re.match(r'^(\d{2})(\d{2})(\d{2})', fn)
    if m:
        mm, dd, yy = m.groups()
        meeting_date = f'20{yy}-{mm}-{dd}'
    else:
        meeting_date = ''
    fy = fy_for(meeting_date) if meeting_date else ''
    print(f'Meeting date: {meeting_date}, FY: {fy}')

    rows = []
    cur_fund = None
    cur_fund_name = None
    in_register = False
    reader = PdfReader(str(pdf_path))
    print(f'Pages: {len(reader.pages)}')

    for pg_idx, page in enumerate(reader.pages):
        text = (page.extract_text() or '').translate(DASH_TRANS)
        if 'PENTAMATION' in text and 'CHECK REGISTER' in text:
            in_register = True
        if not in_register:
            continue
        for line in text.splitlines():
            line = line.rstrip()
            if not line: continue
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
                'Category':       '',
                'Subject':        '',
                'Confidence':     '',
            })
    return rows

rows = parse_with_pypdf(ERRORED)
print(f'\nRecovered: {len(rows)} rows, ${sum(r["Amount"] for r in rows):,.2f}')

# Issue date range
dates = [r['Issue Date'] for r in rows]
if dates:
    print(f'Issue date range: {min(dates).date()} .. {max(dates).date()}')

# FY breakdown by issue date (since meeting fy=FY20)
from collections import Counter
def issue_fy(d):
    return f'FY{(d.year+1)%100:02d}' if d.month >= 7 else f'FY{d.year%100:02d}'
ifyr = Counter(issue_fy(r['Issue Date']) for r in rows)
print(f'Issue-Date FY: {dict(ifyr)}')

# Save
out = _paths.OCT2019_PKL
out.write_bytes(pickle.dumps(rows))
print(f'Saved: {out}')
