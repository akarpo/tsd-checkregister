"""Fiscal-year coverage — which transaction months actually carry disbursements.

Replaces a hand-maintained table in index.html. That table was keyed to board
meetings rather than transaction months and had to be re-typed by hand whenever
registers were ingested, so it drifted from the data more than once.

A month counts as covered when it holds at least `FLOOR` line items. Below that
it is not a disbursement run, just stray adjustments swept in by an adjacent
register — FY20's Nov 2019 (15 lines) and Jan 2020 (7 lines) are the clearest
examples, against a normal month of 700-1,800.

Note this reads better than a register-availability count, and legitimately so:
a register covers one to two months of prior activity, so an unposted register
usually leaves no hole. FY24 is the clearest case — the Nov 2023 register was
never posted, yet every FY24 transaction month is covered.
"""
from collections import defaultdict

FLOOR = 100
MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Why a year is short — editorial context the row counts cannot express.
# Every figure beside these is still derived; only the explanation is authored.
WHY = {
    'FY11': 'the corpus begins with Nov 2010 activity, so the year opens mid-stream — treat it as a partial-year stub',
    'FY13': 'the K-5 ELA adoption year, so that spike may be understated',
    'FY18': 'mid-TCRWP era, so the PD line may be understated',
    'FY20': 'the BoardDocs transition window, which leaves COVID-era spend largely invisible',
}


def fy_months(fy):
    """The 12 (year, month) pairs of a Jul 1 - Jun 30 fiscal year, in order."""
    end = 2000 + int(fy[2:])
    return [(end - 1, m) for m in range(7, 13)] + [(end, m) for m in range(1, 7)]


def _label(pairs):
    """Compress consecutive months into ranges: 'Nov 2019 - Apr 2020'."""
    if not pairs:
        return ''
    runs, run = [], [pairs[0]]
    for prev, cur in zip(pairs, pairs[1:]):
        step = (cur[0] - prev[0]) * 12 + (cur[1] - prev[1])
        if step == 1:
            run.append(cur)
        else:
            runs.append(run); run = [cur]
    runs.append(run)
    out = []
    for run in runs:
        first, last = run[0], run[-1]
        if len(run) == 1:
            out.append(f'{MONTH_ABBR[first[1] - 1]} {first[0]}')
        else:
            out.append(f'{MONTH_ABBR[first[1] - 1]} {first[0]} - '
                       f'{MONTH_ABBR[last[1] - 1]} {last[0]}')
    return ', '.join(out)


def build_coverage(rows, fys, floor=FLOOR):
    """Per-FY coverage, ordered as `fys`, plus the years worth calling out."""
    counts = defaultdict(int)
    for r in rows:
        d = r.get('Issue Date')
        if hasattr(d, 'year'):
            counts[(d.year, d.month)] += 1

    years = []
    for fy in fys:
        months = fy_months(fy)
        gaps = [m for m in months if counts.get(m, 0) < floor]
        thin = [m for m in gaps if counts.get(m, 0) > 0]
        years.append({
            'fy': fy,
            'covered': 12 - len(gaps),
            'missing': _label(gaps),
            'gapCount': len(gaps),
            'thinCount': len(thin),
            'complete': not gaps,
            'why': WHY.get(fy, ''),
        })

    worst = sorted((y for y in years if y['gapCount']),
                   key=lambda y: -y['gapCount'])
    return {
        'floor': floor,
        'years': years,
        'complete': [y['fy'] for y in years if y['complete']],
        'callout': [y['fy'] for y in worst[:4]],
    }
