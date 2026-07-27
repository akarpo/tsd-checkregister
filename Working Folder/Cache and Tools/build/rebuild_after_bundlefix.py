"""Rebuild combined dataset after bundle-date fix.
- Load new pre2020_lines.pkl (with corrected meeting dates)
- Append Oct 2019 recovered rows (still needed because pypdf fallback was added mid-run)
- Append FY21+ all_lines.pkl
- Repair known-bad source issue dates, then attribute each line to the FY
  containing its issue date (Jul 1 - Jun 30) — see fiscal_year.py
- Apply categorization + subject classification
- Save combined_lines.pkl, then defer to build_combined_wb.py for workbook"""
import sys, pickle
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from categorize_v2 import categorize
from subjects import classify_subject, classify_confidence
from fiscal_year import assign_fiscal_years
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

# Subject + confidence classification now live in subjects.py (committed lookup).

corrected = assign_fiscal_years(combined)
print(f'Repaired {corrected} known-bad source issue date(s); '
      'Fiscal Year attributed from issue date (Jul 1 - Jun 30)', flush=True)

print('Re-applying categorization + subjects...', flush=True)
for r in combined:
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
fys = Counter(r['Fiscal Year'] for r in combined)
print(f'\nFiscal-year breakdown (by issue date):')
for fy in sorted(fys): print(f'  {fy}: {fys[fy]:,}')
print(f'\nGrand total: ${sum(r["Amount"] for r in combined):,.2f}')
