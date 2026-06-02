"""Build the dashboard payload from combined FY11-FY26 data and inline it into index.html.

Exposes ``build_payload(combined)`` (pure: rows -> payload dict) and
``write_dashboard(payload, html_path)`` (inlines the payload + refreshes the
header text) so the orchestrator and validator can reuse them. Run directly to
(re)write the committed index.html from build/combined_lines.pkl.
"""
import sys
import pickle
import json
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _paths

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
    s = s.lower().replace('—','-').replace('/','-').replace('(','').replace(')','')
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
        cat = r.get('Category','') or 'Untyped (function code blank or 000)'
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
    sub_count = defaultdict(int)
    for r in pd_lines:
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


def build_payload(combined):
    """Pure: combined rows -> dashboard payload dict (matches the committed schema)."""
    fys = sorted({r['Fiscal Year'] for r in combined})
    operating = [r for r in combined if not (r['Fund'].startswith('3') or r['Fund'].startswith('4'))]
    bond = [r for r in combined if (r['Fund'].startswith('3') or r['Fund'].startswith('4'))]
    payload = {
        'fy': fys,
        'all': build_section(combined, fys),
        'operating': build_section(operating, fys),
        'bond': build_section(bond, fys),
        'meta': {
            'totalLines': len(combined),
            'fyRange': f'{fys[0]}-{fys[-1]}',
            'sourceCount': len({r['Source Meeting'] for r in combined}),
        },
    }
    payload['all']['subjects'] = build_subjects(combined, fys)
    return payload


def write_dashboard(payload, html_path):
    """Inline `payload` into the index.html data-payload script and refresh header text."""
    html_path = Path(html_path)
    new_payload = json.dumps(payload, separators=(',', ':'))
    fys = payload['fy']
    html = html_path.read_text(encoding='utf-8')
    html = re.sub(
        r'(<script id="data-payload"[^>]*>).*?(</script>)',
        lambda m: m.group(1) + new_payload + m.group(2),
        html, count=1, flags=re.DOTALL
    )
    fy_range = f'FY{fys[0][2:]}-{fys[-1]}'
    html = re.sub(r'FY\d\d-FY\d\d', fy_range, html)
    def fmt_m(n): return f'${n/1_000_000:.0f}M'
    total = payload['all']['grandTotal']
    op_total = payload['operating']['grandTotal']
    bond_total = payload['bond']['grandTotal']
    html = re.sub(
        r'\d+,?\d* line items, \$\d+M total — split into operating \(\$\d+M\) and bond/capital \(\$\d+M\) views\.',
        f'{payload["all"]["lineCount"]:,} line items, {fmt_m(total)} total — split into operating ({fmt_m(op_total)}) and bond/capital ({fmt_m(bond_total)}) views.',
        html
    )
    html = re.sub(r'\d+ monthly check register PDFs', f'{payload["meta"]["sourceCount"]} monthly check register PDFs', html)
    html_path.write_text(html, encoding='utf-8')
    return html_path


if __name__ == '__main__':
    combined = pickle.loads(_paths.COMBINED_PKL.read_bytes())
    print(f'Loaded: {len(combined):,} rows', flush=True)
    payload = build_payload(combined)
    print(f'Grand total: ${payload["all"]["grandTotal"]:,.2f}  lines: {payload["meta"]["totalLines"]:,}  '
          f'sources: {payload["meta"]["sourceCount"]}', flush=True)
    path = write_dashboard(payload, _paths.DASHBOARD)
    print(f'Updated {path} ({Path(path).stat().st_size:,} bytes)', flush=True)
