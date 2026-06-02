"""Pentamation check register PDF parser for Troy SD.

Output schema matches the existing 'All Lines' sheet:
  Source Meeting | Fiscal Year | Fund | Fund Name | Cash Acct | Check No | Voided
  Issue Date | Vendor ID | Vendor Name | Budget Unit | Function Code
  Account | Description | Sales Tax | Amount

Format observations (consistent FY20 through FY26):
  - Header includes "PENTAMATION ENTERPRISES,INC." and "CHECK REGISTER - BY FUND"
  - Each fund section starts with "FUND - <num> - <name>"
  - Column header: "CASH ACCT CHECK NO ISSUE DT VENDOR NAME BUDGET UNIT ACCNT ----DESCRIPTION---- SALES TAX AMOUNT"
  - Detail rows: cash_acct check_no [V] mm/dd/yy vendor_id vendor_name budget_unit account description sales_tax amount
  - "TOTAL CHECK"/"TOTAL FUND"/"TOTAL CASH"/grand totals are summary rows; skip
  - Vendor names truncated to 19 chars; descriptions truncated to 19-20 chars
  - Voided checks show 'V' between check_no and date; amount is negative
"""
from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
import pdfplumber

# Regex matches one detail line. The trick: vendor name is variable-width but
# always followed by budget_unit (digits / starts with L). We use a non-greedy
# vendor capture and require the budget unit to match a specific shape.
LINE_RE = re.compile(
    r'^(?P<cash>[A-Z]\d+)\s+'
    r'(?P<check>(?:[A-Z]\d+-\d+[A-Z]?|\d{2}-\d{3,5}|V\d{5,8}|\d{5,8}))\s+'
    r'(?:(?P<voided>V)\s+)?'
    r'(?P<date>\d{2}/\d{2}/\d{2})\s+'
    r'(?P<vendid>\d{3,6})\s+'
    r'(?P<vendor>.+?)\s+'
    r'(?P<bu>L\d+|\d{3,15})\s+'
    r'(?P<acct>[A-Z]?\d{4}|L\d+)\s+'
    r'(?P<desc>.*?)\s*'
    r'(?P<tax>-?[\d,]+\.\d{2})\s+'
    r'(?P<amt>-?[\d,]+\.\d{2})\s*$'
)
FUND_RE = re.compile(r'FUND\s*-\s*(?P<num>\d+)\s*-\s*(?P<name>[A-Z0-9 &/\-]+?)\s*$')

SKIP_PREFIXES = ('TOTAL', 'PENTAMATION', 'DATE:', 'TIME:', 'CASH ACCT', 'PAGE NUMBER',
                 'SELECTION CRITERIA', 'ACCOUNTING PERIOD')

def parse_amount(s):
    return float(s.replace(',', ''))

def parse_date(s):
    # mm/dd/yy → datetime; pivot at 2000 since registers go 2010s+
    mo, dd, yy = s.split('/')
    yr = 2000 + int(yy)
    return datetime(yr, int(mo), int(dd))

def fy_for(meeting_date_str: str) -> str:
    """Fiscal year of a board MEETING (TSD FY = Jul 1 - Jun 30, named by ending year).
    The meeting approves the prior month's register, so we use meeting date.
    Note: FY23 = Jul 1 2022 - Jun 30 2023. So a Jul 2022 meeting → FY23."""
    md = datetime.strptime(meeting_date_str, '%Y-%m-%d')
    if md.month >= 7:
        return f'FY{(md.year + 1) % 100:02d}'
    return f'FY{md.year % 100:02d}'

def parse_pdf(path: Path) -> list[dict]:
    parent = path.stem  # filename without extension
    # Filename pattern: YYYY-MM-DD_<rest>
    m = re.match(r'^(\d{4}-\d{2}-\d{2})_', parent)
    meeting_date = m.group(1) if m else ''
    fy = fy_for(meeting_date) if meeting_date else ''

    rows = []
    cur_fund = None
    cur_fund_name = None
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            text = pg.extract_text() or ''
            for line in text.splitlines():
                line = line.rstrip()
                if not line: continue
                # Fund section header
                fm = FUND_RE.search(line)
                if fm:
                    cur_fund = fm.group('num')
                    cur_fund_name = fm.group('name').strip()
                    continue
                # Skip non-detail lines
                if any(line.lstrip().startswith(p) for p in SKIP_PREFIXES):
                    continue
                # Try detail
                lm = LINE_RE.match(line)
                if not lm:
                    continue
                bu = lm.group('bu')
                # Function code = positions 7-9 of budget unit (3 digits) when BU is numeric
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
    return rows

if __name__ == '__main__':
    import sys, json
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _paths
    test = Path(sys.argv[1]) if len(sys.argv) > 1 else _paths.STANDALONE_PDFS / '2023-01-17_Check register by fund Nov 2022.pdf'
    rows = parse_pdf(test)
    print(f'Parsed: {len(rows)} rows')
    print(f'Total amount: ${sum(r["Amount"] for r in rows):,.2f}')
    print(f'Sample first: {rows[0] if rows else "—"}')
    print(f'Sample last:  {rows[-1] if rows else "—"}')
