"""Curriculum / PD swimlane analysis — derived entirely from the dataset.

Supersedes the semi-manual split_curriculum_pd_v2.py flow, which applied a
computed PD percentage to a hard-coded per-FY total for three of the four
swimlanes. Those anchors came from the original FY23-FY26 build and were never
refreshed, so by 2026-07 they disagreed with the data by tens of thousands of
dollars per lane and did not move when new registers were ingested. Every figure
here now comes from the rows.

The swimlane membership filters and the PD test are carried over verbatim — they
are tuned heuristics over truncated vendor names and descriptions, and remain the
analytical judgement in this module. What changed is that the totals they produce
are used directly instead of being scaled onto fixed anchors.

`build_curriculum(rows, fys)` returns everything the dashboard needs: per-lane
curriculum/PD arrays, period totals, and the derived facts the narrative quotes.
"""
from collections import defaultdict

# --- swimlane filters + PD test (verbatim from split_curriculum_pd_v2.py) ---
def has(s, *kws):
    s = (s or '').upper()
    return any(k in s for k in kws)

# --- swimlane filters; use shorter prefixes since vendor names are truncated to 19 chars ---
def k5_ela(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    bu = r.get('Budget Unit') or ''
    if has(v, 'HEINEMANN', 'TEACHERS COLLEGE', 'READING AND WRI', 'READING WRITING',
           'THE READING AND', 'FOUNTAS', 'CALKINS', 'READING RECOVERY',
           'WILSON LANGUAGE', 'BENCHMARK ED', 'LEARNING A-Z', 'LEXIA', 'LITERACY FOOTPRINT',
           'HANDWRITING WITH', 'PROLITERACY'):
        return True
    if has(v, 'HARCOURT','HOUGHTON MIFFLIN','HMH'):
        if has(d, 'JOURNEYS','READ','WRITE','LITERACY','SPELLING','PHONICS','ELA',
               'LANG ARTS','LANGUAGE ARTS','LEVELED','GRAMMAR','VOCAB','READING'):
            return True
    if has(v, 'SCHOLASTIC') and has(d, 'BOOK','READ','LITERACY','LEVELED','LIBRARY'):
        return True
    if bu.startswith('101425221') and r.get('Subject') == 'ELA':
        return True
    return False

def k5_math(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    bu = r.get('Budget Unit') or ''
    # Short prefixes for 19-char truncation
    if has(v, 'MATH LEARNING','THE MATH LEARNING','BRIDGES','AVMR','MATH RECOVERY',
           'US MATH RECOVERY','U S MATH RECOVERY','ORIGO'):
        return True
    if has(d, 'BRIDGES'):  # Bridges materials regardless of vendor
        return True
    if has(v, 'HARCOURT','HOUGHTON MIFFLIN','HMH'):
        if has(d, 'MATH','EXPRESS','GO MATH','MATH EXPRESS','GOMATH'):
            return True
    if has(v, 'EUREKA','GREAT MINDS') and has(d, 'MATH','ELEM'):
        return True
    if bu.startswith('101425221') and r.get('Subject') == 'Math':
        return True
    return False

def m612_ela(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    fc = (r.get('Function Code') or '').strip()
    bu = r.get('Budget Unit') or ''
    secondary = fc in ('112','113') or (fc.startswith('11') and fc != '111')
    # Definite 6-12 ELA vendors
    if has(v,'NOREDIN','NO RED INK','COMMONLIT','ACTIVELY LEARN','TURNITIN','VOCABULARY.COM',
           'NORTON','BEDFORD ST','BEDFORD/ST','MACMILLAN LEARNING','PERFECTION LEARNING',
           'MCDOUGAL','HOLT RINEHART','PRESTWICK HOUSE','EMC PARADIGM','EMC/PARADIGM',
           'E M C /PARADIGM','GOODHEART-WILLCOX','JUNIOR LIBRARY GUIL','GREENWOOD PUBLISH'):
        return True
    # Major publishers — only if secondary fc + ELA description signal
    if has(v,'HOUGHTON MIFFLIN','HMH','MCGRAW','PEARSON','CENGAGE','MACMILLAN HOLDINGS',
           'MACMILLAN/MCGRAW'):
        if has(d,'ENGLISH','LITERATURE','GRAMMAR','RHETORIC','COMPOSITION','NOVEL','POETRY',
               'SHAKESPEARE','LANGUAGE ARTS','LANG ARTS','ELA','ANTHOL') and secondary:
            return True
    # Secondary fc + clear ELA-content description (regardless of vendor)
    if secondary and has(d,'NOVEL','SHAKESPEARE','POETRY','ANTHOL','LITERATURE','ENGLISH',
                         'GRAMMAR','COMPOSITION','RHETORIC'):
        return True
    return False

# Ron Larson authors the Big Ideas secondary-math texts, but "Larson" is also a
# Troy school building. A bare description match on LARSON swept in $8.4M of
# construction, utilities and transport for Larson School (Barton Malow, DTE,
# Nagle Paving, TMP Architecture...), which the retired hard-coded anchors hid.
# The token only counts when the vendor is actually a textbook publisher.
MATH_PUBLISHERS = ('HOUGHTON MIFFLIN', 'HMH', 'MCGRAW', 'CENGAGE', 'BIG IDEAS',
                   'KENDALL HUNT', 'PEARSON', 'LARSON TEXT', 'FOLLETT')


def m612_math(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    bu = r.get('Budget Unit') or ''
    if has(v, 'BIG IDEAS','LARSON TEXT'):
        return True
    if has(d, 'BIG IDEAS','ILLUSTRATIVE MATH','IM CERTIFIED'):
        return True
    if has(d, 'LARSON') and has(v, *MATH_PUBLISHERS):
        return True
    # Illustrative Math ships through Imagine Learning / Kendall Hunt. Match the
    # IM product lines specifically — the same vendor also sells Edgenuity
    # licences and Imagine Language & Literacy, which are not secondary math.
    if has(d, 'IMAGINE IM','IM MATHEMATICS','IM ALGEBRA','IM GEOMETRY','PD ILLUSTRATIVE'):
        return True
    if has(v, 'CENGAGE') and has(d, 'MATH','ALGEBRA','GEOMETRY','BIG IDEAS','LARSON'):
        return True
    if has(v, 'KENDALL HUNT'):
        return True
    if has(v, 'MCGRAW','PEARSON','HOUGHTON MIFFLIN','HMH') and \
       has(d, 'ALGEBRA','GEOMETRY','PRECALC','TRIG','CALCULUS','HS MATH','SECONDARY'):
        return True
    # 6-12 Math PD lines via BU 101-425-221 don't typically classify as 'Math' subject;
    # accept any function 221 spend explicitly tagged with secondary-math description
    if bu.startswith('101425221') and has(d, 'ALGEBRA','GEOMETRY','HS MATH','SECONDARY'):
        return True
    return False

def is_pd(r):
    bu = r.get('Budget Unit') or ''
    if bu.startswith('101425221'):
        return True
    if (r.get('Function Code') or '').strip() == '221':
        return True
    v = (r.get('Vendor Name') or '').upper()
    if has(v, 'TEACHERS COLLEGE','READING AND WRI','READING WRITING PRO','THE READING AND WRI'):
        return True
    if has(v, 'AVMR','MATH RECOVERY','US MATH RECOVERY','U S MATH RECOVERY'):
        return True
    return False


# Lane order is the display order. The blurb is editorial (what the money bought);
# every number beside it is derived.
LANES = [
    ('K-5 ELA',   k5_ela,    'HMH Journeys \u2192 TCRWP / Heinemann'),
    ('K-5 Math',  k5_math,   'Math Expressions \u2192 Bridges + AVMR'),
    ('6-12 ELA',  m612_ela,  'Turnitin / CommonLit / EMC'),
    ('6-12 Math', m612_math, 'Big Ideas \u2192 Illustrative Math'),
]

# Analytical windows. The spans are a judgement about adoption cycles; the totals
# for each span are computed, never written down.
PERIODS = [
    ('Cycle 1',      'FY12', 'FY15'),
    ('Steady-state', 'FY16', 'FY19'),
    ('Cycle 2',      'FY20', 'FY26'),
]

# Board actions and external events — genuinely hand-authored annotations.
NOTABLE = {
    'FY13': 'HMH Journeys K-5 ELA adoption (May 2012)',
    'FY14': 'HMH Math Expressions K-5 + Big Ideas 6-12 (May 2013)',
    'FY15': 'Math rollout completing',
    'FY17': 'TCRWP PD ramping',
    'FY19': 'TCRWP peak',
    'FY20': 'AVMR / Math Recovery first appears',
    'FY23': 'Bridges + Illustrative Math adoption (Mar/May 2023)',
    'FY24': 'K-5 Math materials buy year',
    'FY25': 'TCRWP Writing Units new edition (May 2025)',
}
ADOPTION_YEARS = ['FY13', 'FY14', 'FY23', 'FY24']


SECONDARY_WORDS = ('GEOMETRY', 'ALGEBRA', 'PRECALC', 'TRIG', 'CALCULUS', 'HS MATH',
                   'HIGH SCHOOL', 'SECONDARY', 'SHAKESPEARE', 'RHETORIC')
ELEMENTARY_WORDS = ('GRADE K', 'KINDER', 'ELEM', 'K-5', 'PRIMARY')


def assign_lane(r):
    """The single swimlane a row belongs to, or None.

    Subject is never ambiguous — no row matches both an ELA and a Math filter.
    Grade band can be: 60 rows match both bands of one subject, nearly all of
    them function-code 221 (improvement of instruction), which is grade-neutral.
    Left unresolved they would be counted twice and inflate the combined total,
    so resolve by the strongest available signal: an explicit secondary/
    elementary function code first, then wording in the description
    ("GEOMETRY COHORT" is secondary PD, "GRADE K" books are elementary),
    defaulting to elementary, where the bulk of the district's PD sits.
    """
    k5e, k5m = k5_ela(r), k5_math(r)
    s_e, s_m = m612_ela(r), m612_math(r)
    if not (k5e or k5m or s_e or s_m):
        return None

    elem, sec = ('K-5 ELA', '6-12 ELA') if (k5e or s_e) else ('K-5 Math', '6-12 Math')
    in_elem, in_sec = (k5e, s_e) if (k5e or s_e) else (k5m, s_m)
    if in_elem and not in_sec:
        return elem
    if in_sec and not in_elem:
        return sec

    fc = (r.get('Function Code') or '').strip()
    d = (r.get('Description') or '').upper()
    if fc in ('112', '113'):
        return sec
    if fc == '111':
        return elem
    if has(d, *SECONDARY_WORDS):
        return sec
    if has(d, *ELEMENTARY_WORDS):
        return elem
    return elem


def _split_by_fy(rows, lane_name, fys):
    """(curriculum, pd) totals per FY for one swimlane — straight from the rows."""
    cur = {fy: 0.0 for fy in fys}
    pd = {fy: 0.0 for fy in fys}
    for r in rows:
        fy = r.get('Fiscal Year', '')
        if fy not in cur or assign_lane(r) != lane_name:
            continue
        if is_pd(r):
            pd[fy] += r['Amount']
        else:
            cur[fy] += r['Amount']
    return cur, pd


def _window(fys, lo, hi):
    return [fy for fy in fys if lo <= fy <= hi] if lo in fys else []


def build_curriculum(rows, fys):
    """Everything the curriculum spotlight renders, derived from `rows`."""
    lanes = {}
    for name, _member, blurb in LANES:
        cur, pd = _split_by_fy(rows, name, fys)
        cur_a = [round(cur[fy]) for fy in fys]
        pd_a = [round(pd[fy]) for fy in fys]
        total = sum(cur_a) + sum(pd_a)
        lanes[name] = {
            'cur': cur_a,
            'pd': pd_a,
            'total': total,
            'pdPct': round(sum(pd_a) / total * 100) if total else 0,
            'blurb': blurb,
        }

    idx = {fy: i for i, fy in enumerate(fys)}
    lane_names = [n for n, _f, _b in LANES]

    def lane_window_total(name, span):
        L = lanes[name]
        return sum(L['cur'][idx[fy]] + L['pd'][idx[fy]] for fy in span)

    periods = []
    for label, lo, hi in PERIODS:
        span = _window(fys, lo, hi)
        by_lane = {n: lane_window_total(n, span) for n in lane_names}
        periods.append({
            'label': label,
            'span': f'{lo}-{hi}',
            'byLane': by_lane,
            'combined': sum(by_lane.values()),
        })

    combined_total = sum(L['total'] for L in lanes.values())

    def per_fy(name):
        L = lanes[name]
        return {fy: L['cur'][idx[fy]] + L['pd'][idx[fy]] for fy in fys}

    def best_run(name, span, length=2):
        """Highest-spending consecutive run of `length` FYs within `span`."""
        vals = per_fy(name)
        best = None
        for i in range(len(span) - length + 1):
            run = span[i:i + length]
            tot = sum(vals[fy] for fy in run)
            if best is None or tot > best[1]:
                best = (run, tot)
        return {'span': f'{best[0][0]}-{best[0][-1]}', 'amount': best[1]} if best else None

    def peak_year(name, span):
        vals = per_fy(name)
        fy = max(span, key=lambda f: vals[f])
        return {'fy': fy, 'amount': vals[fy]}

    def lowest_run(name, span, length=2):
        vals = per_fy(name)
        best = None
        for i in range(len(span) - length + 1):
            run = span[i:i + length]
            tot = sum(vals[fy] for fy in run)
            if best is None or tot < best[1]:
                best = (run, tot)
        return {'span': f'{best[0][0]}-{best[0][-1]}',
                'values': [vals[fy] for fy in best[0]]} if best else None

    c1_span = _window(fys, *PERIODS[0][1:])
    ss_span = _window(fys, *PERIODS[1][1:])
    c2_span = _window(fys, *PERIODS[2][1:])
    p = {x['label']: x for x in periods}

    ss_ela = [per_fy('K-5 ELA')[fy] for fy in ss_span]
    facts = {
        'cycleRatio': round(p['Cycle 2']['combined'] / p['Cycle 1']['combined'], 1)
                      if p['Cycle 1']['combined'] else 0,
        'cycle1': {n: peak_year(n, c1_span) for n in lane_names},
        'cycle2': {n: best_run(n, c2_span) for n in lane_names},
        'cycle1ELA612Total': p['Cycle 1']['byLane']['6-12 ELA'],
        'cycle2ELA612Total': p['Cycle 2']['byLane']['6-12 ELA'],
        'k5MathCycle1': p['Cycle 1']['byLane']['K-5 Math'],
        'k5MathCycle2': p['Cycle 2']['byLane']['K-5 Math'],
        'k5ELASteadyRange': [min(ss_ela), max(ss_ela)] if ss_ela else [0, 0],
        'ela612Peak': best_run('6-12 ELA', fys),
        'k5MathTrough': lowest_run('K-5 Math', ss_span),
        'k5ELACycle2Yearly': round(p['Cycle 2']['byLane']['K-5 ELA'] / len(c2_span))
                             if c2_span else 0,
        'ela612Cycle2Yearly': round(p['Cycle 2']['byLane']['6-12 ELA'] / len(c2_span))
                              if c2_span else 0,
        'first612MathYear': next(
            ({'fy': fy, 'amount': per_fy('6-12 Math')[fy]}
             for fy in fys if per_fy('6-12 Math')[fy] > 0), None),
        'nearZeroFloor': 100,
    }

    return {
        'fys': list(fys),
        'laneOrder': lane_names,
        'lanes': lanes,
        'periods': periods,
        'combined': combined_total,
        'notable': NOTABLE,
        'adoption': ADOPTION_YEARS,
        'facts': facts,
    }
