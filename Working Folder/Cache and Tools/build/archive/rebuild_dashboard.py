"""Rebuild the index.html dashboard payload from parsed all_lines.pkl.

The original dashboard payload (extracted to dashboard_payload.json) defines the schema:
{
  "fy": ["FY23","FY24","FY25","FY26"],
  "all": {
    "totals": {fy: amt},
    "grandTotal": ...,
    "lineCount": ...,
    "categories": {
      cat: {
        "slug": "...",
        "total": ...,
        "instructional": bool,
        "byYear": {fy: amt},
        "countByYear": {fy: count},
        "vendorsByYear": {fy: [{"v": ..., "t": ..., "n": ..., "i": [{"d": ..., "a": ..., "c": ...}, ...]}]}
      }
    },
    "subjects": {... PD subject breakdown ...}
  },
  "operating": {... same shape, fund != 423/498 ...},
  "bond": {... same shape, fund 423/498 only ...},
  "meta": {...}
}
"""
from __future__ import annotations
import pickle, json, re
from pathlib import Path
from collections import defaultdict, Counter

BUILD = Path(__file__).parent
ALL_LINES = pickle.loads((BUILD / 'all_lines.pkl').read_bytes())

# Derive instructional flag from category names
INSTRUCTIONAL = {
    'Instruction — Substitute Teachers (General Classes)',
    'Support — Instructional Staff (PD/Curriculum)',
    'Instruction — Basic Programs (Elementary/Secondary)',
    'Instruction — Substitute Teachers (Special Education)',
    'Instruction — Compensatory Education',
    'Instruction — Special Education',
    'Instruction — Vocational / CTE',
}

def slug(s):
    s = s.lower().replace('—', '-').replace('/', '-').replace('(', '').replace(')', '')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

def build_section(lines, fy_list):
    totals = {fy: 0.0 for fy in fy_list}
    line_count = 0
    cats = defaultdict(lambda: {
        'byYear': defaultdict(float),
        'countByYear': defaultdict(int),
        'vendorsByYear': defaultdict(lambda: defaultdict(lambda: {'t': 0.0, 'n': 0, 'descs': defaultdict(lambda: [0.0, 0])})),
    })
    for r in lines:
        fy = r['Fiscal Year']
        if fy not in totals: continue
        cat = r.get('Category', 'Untyped (function code blank or 000)')
        amt = r['Amount']
        totals[fy] += amt
        line_count += 1
        cats[cat]['byYear'][fy] += amt
        cats[cat]['countByYear'][fy] += 1
        v = r['Vendor Name'] or '?'
        d = (r['Description'] or '').strip()
        vrec = cats[cat]['vendorsByYear'][fy][v]
        vrec['t'] += amt
        vrec['n'] += 1
        vrec['descs'][d][0] += amt
        vrec['descs'][d][1] += 1
    grand = sum(totals.values())
    out_cats = {}
    for cat, info in cats.items():
        # Top 20 vendors per FY, top 20 descriptions per vendor
        vbyy = {}
        for fy, vendors in info['vendorsByYear'].items():
            sorted_vs = sorted(vendors.items(), key=lambda x: -x[1]['t'])[:25]
            vbyy[fy] = []
            for vname, vdata in sorted_vs:
                top_descs = sorted(vdata['descs'].items(), key=lambda x: -x[1][0])[:20]
                vbyy[fy].append({
                    'v': vname, 't': round(vdata['t'], 2), 'n': vdata['n'],
                    'i': [{'d': d, 'a': round(a, 2), 'c': c} for d, (a, c) in top_descs]
                })
        out_cats[cat] = {
            'slug': slug(cat),
            'total': round(sum(info['byYear'].values()), 2),
            'instructional': cat in INSTRUCTIONAL,
            'byYear': {fy: round(v, 2) for fy, v in info['byYear'].items()},
            'countByYear': dict(info['countByYear']),
            'vendorsByYear': vbyy,
        }
    return {
        'totals': {fy: round(v, 2) for fy, v in totals.items()},
        'grandTotal': round(grand, 2),
        'lineCount': line_count,
        'categories': out_cats,
    }

def build_subjects(lines, fy_list):
    pd_lines = [r for r in lines if r['Budget Unit'].startswith('101425221')]
    sub_agg = defaultdict(lambda: {fy: 0.0 for fy in fy_list})
    sub_count = Counter()
    for r in pd_lines:
        if r['Fiscal Year'] not in sub_agg[next(iter(sub_agg.keys()))] if sub_agg else True:
            pass
        s = r.get('Subject') or 'Not Directly Attributable'
        sub_agg[s][r['Fiscal Year']] += r['Amount']
        sub_count[s] += 1
    out = {}
    for s, byfy in sub_agg.items():
        out[s] = {
            'lines': sub_count[s],
            'byYear': {fy: round(v, 2) for fy, v in byfy.items()},
            'total': round(sum(byfy.values()), 2),
        }
    return out

def main():
    fys = sorted({r['Fiscal Year'] for r in ALL_LINES})
    print(f'FYs: {fys}', flush=True)

    # Bond/capital = debt service funds (3xx, 312-323) + capital projects (4xx) + sinking (498)
    operating = [r for r in ALL_LINES if not (r['Fund'].startswith('3') or r['Fund'].startswith('4'))]
    bond = [r for r in ALL_LINES if (r['Fund'].startswith('3') or r['Fund'].startswith('4'))]
    print(f'Operating: {len(operating):,} lines  Bond: {len(bond):,} lines', flush=True)

    payload = {
        'fy': fys,
        'all': build_section(ALL_LINES, fys),
        'operating': build_section(operating, fys),
        'bond': build_section(bond, fys),
        'meta': {
            'sourceCount': 0,  # set below
            'totalLines': len(ALL_LINES),
            'fyRange': f'{fys[0]}-{fys[-1]}',
        },
    }
    payload['all']['subjects'] = build_subjects(ALL_LINES, fys)

    # Source PDF count
    pdfs_dir = Path(r'C:\Dev\CheckRegister\Working Folder\Cache and Tools\source_data\BoardDocs_PDFs')
    payload['meta']['sourceCount'] = len(list(pdfs_dir.glob('*.pdf')))

    print(f'Grand total: ${payload["all"]["grandTotal"]:,.2f}', flush=True)
    print(f'Line count:  {payload["all"]["lineCount"]:,}', flush=True)
    print(f'Categories:  {len(payload["all"]["categories"])}', flush=True)

    out_json = BUILD / 'payload.json'
    out_json.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
    print(f'Saved {out_json} ({out_json.stat().st_size:,} bytes)', flush=True)

    # Update index.html
    html_path = Path(r'C:\Dev\CheckRegister\index.html')
    html = html_path.read_text(encoding='utf-8')
    new_payload = json.dumps(payload, separators=(',', ':'))
    html2 = re.sub(
        r'(<script id="data-payload"[^>]*>).*?(</script>)',
        lambda m: m.group(1) + new_payload + m.group(2),
        html, count=1, flags=re.DOTALL
    )
    # Update title to reflect new FY range
    fy_range = f'FY{fys[0][2:]}-{fys[-1]}'
    html2 = re.sub(r'FY23-FY26', fy_range, html2)
    html2 = re.sub(r'(\d+,?\d*) line items across (\d+) monthly registers',
                   f'{payload["all"]["lineCount"]:,} line items across {payload["meta"]["sourceCount"]} monthly registers',
                   html2)
    html_path.write_text(html2, encoding='utf-8')
    print(f'Updated {html_path}', flush=True)
    print(f'Size: {html_path.stat().st_size:,} bytes', flush=True)

if __name__ == '__main__':
    main()
