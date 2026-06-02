"""Parse all PDFs in source_data, apply categorization + subject classification,
emit a clean dataset matching the original All Lines schema (plus a Category column).

Outputs:
  build/all_lines.pkl  — list of dicts, one per line
  build/parse_summary.txt — per-file parse stats
"""
from __future__ import annotations
import sys, pickle, json, time
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))
from parser import parse_pdf
from categorize_v2 import categorize, VENDOR_CATS
from subjects import classify_subject, classify_confidence
import _paths

PDFS_DIR = _paths.STANDALONE_PDFS
OUT_PKL = _paths.ALL_LINES_PKL
SUMMARY = _paths.BUILD / 'parse_summary.txt'

def main():
    pdfs = sorted(PDFS_DIR.glob('*.pdf'))
    print(f'Found {len(pdfs)} PDFs', flush=True)
    all_lines = []
    summary = []
    t0 = time.time()
    for i, pdf in enumerate(pdfs, 1):
        try:
            rows = parse_pdf(pdf)
        except Exception as e:
            print(f'  [{i}/{len(pdfs)}] ERROR {pdf.name}: {e}', flush=True)
            summary.append((pdf.name, 0, 0.0, str(e)))
            continue
        # Add Category column
        for r in rows:
            r['Category'] = categorize(r.get('Vendor Name',''), r.get('Fund',''),
                                       r.get('Function Code',''), r.get('Account',''),
                                       r.get('Budget Unit',''), r.get('Amount', 0))
            r['Subject'] = ''
            r['Confidence'] = ''
            if r.get('Budget Unit','').startswith('101425221'):
                r['Subject'] = classify_subject(r.get('Vendor Name',''), r.get('Description',''))
                r['Confidence'] = classify_confidence(r.get('Vendor Name',''), r['Subject'])
        all_lines.extend(rows)
        tot = sum(r['Amount'] for r in rows)
        summary.append((pdf.name, len(rows), tot, ''))
        if i % 10 == 0:
            print(f'  [{i}/{len(pdfs)}] cumulative {len(all_lines):,} lines in {time.time()-t0:.0f}s', flush=True)
    print(f'\nTotal: {len(all_lines):,} lines, ${sum(r["Amount"] for r in all_lines):,.2f} in {time.time()-t0:.0f}s', flush=True)

    # FY breakdown
    fy_count = Counter()
    fy_amt = defaultdict(float)
    for r in all_lines:
        fy_count[r['Fiscal Year']] += 1
        fy_amt[r['Fiscal Year']] += r['Amount']
    print(f'\n{"FY":<6} {"Lines":>8} {"Amount":>16}')
    for fy in sorted(fy_count):
        print(f'{fy:<6} {fy_count[fy]:>8} ${fy_amt[fy]:>15,.2f}')

    OUT_PKL.write_bytes(pickle.dumps(all_lines))
    SUMMARY.write_text('\n'.join(f'{n}\t{c}\t{t:.2f}\t{e}' for n, c, t, e in summary), encoding='utf-8')
    print(f'\nSaved {OUT_PKL}, {SUMMARY}', flush=True)

if __name__ == '__main__':
    main()
