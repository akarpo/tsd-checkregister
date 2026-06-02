"""Rebuild combined dataset after bundle-date fix.
- Load new pre2020_lines.pkl (with corrected meeting dates)
- Append Oct 2019 recovered rows (still needed because pypdf fallback was added mid-run)
- Append FY21+ all_lines.pkl
- Add Issue Date FY column
- Apply categorization + subject classification
- Save combined_lines.pkl, then defer to build_combined_wb.py for workbook"""
import sys, pickle
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from categorize_v2 import categorize
from subjects import classify_subject, classify_confidence
import _paths

BUILD = _paths.BUILD
pre = pickle.loads(_paths.PRE2020_PKL.read_bytes())
oct19 = pickle.loads(_paths.OCT2019_PKL.read_bytes())
post = pickle.loads(_paths.ALL_LINES_PKL.read_bytes())
print(f'Pre-2020 (re-extracted): {len(pre):,}', flush=True)
print(f'Oct 2019 recovered:      {len(oct19):,}', flush=True)
print(f'FY21-FY26 standalone:    {len(post):,}', flush=True)

# Pre-2020 doesn't have Category/Subject/Confidence yet
for r in pre:
    r.setdefault('Category', '')
    r.setdefault('Subject', '')
    r.setdefault('Confidence', '')

combined = pre + oct19 + post
print(f'Combined: {len(combined):,}', flush=True)

# Add Issue Date FY
def issue_fy(d):
    if not isinstance(d, datetime): return ''
    return f'FY{(d.year+1)%100:02d}' if d.month >= 7 else f'FY{d.year%100:02d}'

# Subject + confidence classification now live in subjects.py (committed lookup).

print('Re-applying categorization + subjects + Issue-Date FY...', flush=True)
for r in combined:
    r['Issue Date FY'] = issue_fy(r['Issue Date'])
    r['Category'] = categorize(r.get('Vendor Name',''), r.get('Fund',''),
                              r.get('Function Code',''), r.get('Account',''),
                              r.get('Budget Unit',''), r.get('Amount', 0))
    if r.get('Budget Unit','').startswith('101425221'):
        r['Subject'] = classify_subject(r.get('Vendor Name',''), r.get('Description',''))
        r['Confidence'] = classify_confidence(r.get('Vendor Name',''), r['Subject'])
    else:
        r['Subject'] = ''
        r['Confidence'] = ''

_paths.COMBINED_PKL.write_bytes(pickle.dumps(combined))
print(f'Saved combined_lines.pkl: {len(combined):,} rows', flush=True)

# FY breakdown
mfys = Counter(r['Fiscal Year'] for r in combined)
ifys = Counter(r['Issue Date FY'] for r in combined if r['Issue Date FY'])
print(f'\nMeeting-FY breakdown:')
for fy in sorted(mfys): print(f'  {fy}: {mfys[fy]:,}')
print(f'\nIssue-Date FY breakdown:')
for fy in sorted(ifys): print(f'  {fy}: {ifys[fy]:,}')
print(f'\nGrand total: ${sum(r["Amount"] for r in combined):,.2f}')
