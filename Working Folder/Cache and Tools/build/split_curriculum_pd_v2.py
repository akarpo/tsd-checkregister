"""Compute curriculum/PD split by FY for each swimlane, anchored to existing totals.

Approach:
- Use a broad vendor filter that captures the right line population per swimlane
- Classify each captured line as PD (function 221 / PD-only vendor) or Curriculum (everything else)
- Compute the PD % per FY per swimlane
- Apply that PD % to the EXISTING (load-bearing) hard-coded total for each FY
- Result: curriculum + PD = original total exactly

For FY/swimlane combos where my filter captured zero lines but the original total > 0
(parser/filter coverage mismatch), assume 100% curriculum (consistent with the description
'curriculum spend' for those years where PD wasn't isolated separately).
"""
import sys
import pickle
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _paths

combined = pickle.loads(_paths.COMBINED_PKL.read_bytes())
print(f'Loaded: {len(combined):,} rows')

EXISTING = {
    'K-5 ELA':   [1097,19130,923530,10721,11895,52419,247434,311897,494802,99189,218878,186538,305069,291826,289380,282867],
    'K-5 Math':  [2350,10176,12421,696718,12933,16361,22262,94,1385,197908,308055,319786,553956,567481,423042,319524],
    '6-12 Math': [0,267168,11000,276001,192651,39584,14040,0,0,3719,97560,1500,99903,215087,211095,256268],
    # 6-12 ELA: NEW — totals computed from filter; cur+pd will reconcile to these by construction
    '6-12 ELA':  None,
}
FYS = ['FY11','FY12','FY13','FY14','FY15','FY16','FY17','FY18','FY19','FY20',
       'FY21','FY22','FY23','FY24','FY25','FY26']

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

def m612_math(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    bu = r.get('Budget Unit') or ''
    if has(v, 'BIG IDEAS','LARSON TEXT'):
        return True
    if has(d, 'BIG IDEAS','LARSON','ILLUSTRATIVE MATH','IM CERTIFIED'):
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

def compute_ratios(membership_fn, label):
    cur = defaultdict(float); pd = defaultdict(float)
    for r in combined:
        if not membership_fn(r): continue
        fy = r.get('Issue Date FY','')
        if fy not in FYS: continue
        if is_pd(r): pd[fy] += r['Amount']
        else: cur[fy] += r['Amount']
    pd_pct = {}
    for fy in FYS:
        tot = cur[fy] + pd[fy]
        pd_pct[fy] = (pd[fy] / tot) if tot > 0 else 0.0
    return pd_pct

ela_pct = compute_ratios(k5_ela, 'K-5 ELA')
k5m_pct = compute_ratios(k5_math, 'K-5 Math')
m612_pct = compute_ratios(m612_math, '6-12 Math')

# 6-12 ELA: compute totals AND splits directly from filter (no anchored EXISTING totals)
def compute_direct(membership_fn, label):
    cur = defaultdict(float); pd = defaultdict(float)
    for r in combined:
        if not membership_fn(r): continue
        fy = r.get('Issue Date FY','')
        if fy not in FYS: continue
        if is_pd(r): pd[fy] += r['Amount']
        else: cur[fy] += r['Amount']
    return cur, pd

ela612_cur_d, ela612_pd_d = compute_direct(m612_ela, '6-12 ELA')
EXISTING['6-12 ELA'] = [int(round(ela612_cur_d[fy] + ela612_pd_d[fy])) for fy in FYS]

# Apply percentages to existing totals
def split(label, totals, pct_map):
    cur = []; pd = []
    for i, fy in enumerate(FYS):
        t = totals[i]
        p = pct_map[fy]
        pd_v = round(t * p)
        cur_v = t - pd_v
        cur.append(cur_v); pd.append(pd_v)
    return cur, pd

ela_cur, ela_pd = split('K-5 ELA', EXISTING['K-5 ELA'], ela_pct)
k5m_cur, k5m_pd = split('K-5 Math', EXISTING['K-5 Math'], k5m_pct)
m612_cur, m612_pd = split('6-12 Math', EXISTING['6-12 Math'], m612_pct)
ela612_cur = [int(round(ela612_cur_d[fy])) for fy in FYS]
ela612_pd  = [int(round(ela612_pd_d[fy])) for fy in FYS]
ela612_pct = {fy: (ela612_pd_d[fy] / (ela612_cur_d[fy]+ela612_pd_d[fy])) if (ela612_cur_d[fy]+ela612_pd_d[fy])>0 else 0.0 for fy in FYS}

print('\nSplit summary (anchored to existing totals):')
for label, cur, pd, totals, pct in [
    ('K-5 ELA',  ela_cur,  ela_pd,  EXISTING['K-5 ELA'],   ela_pct),
    ('K-5 Math', k5m_cur,  k5m_pd,  EXISTING['K-5 Math'],  k5m_pct),
    ('6-12 Math',m612_cur, m612_pd, EXISTING['6-12 Math'], m612_pct),
    ('6-12 ELA', ela612_cur, ela612_pd, EXISTING['6-12 ELA'], ela612_pct),
]:
    print(f'\n{label}:')
    print(f'  {"FY":<6}{"Curriculum":>13}{"PD":>13}{"Total":>13}{"PD%":>8}')
    for i, fy in enumerate(FYS):
        print(f'  {fy:<6}{cur[i]:>13,}{pd[i]:>13,}{totals[i]:>13,}{int(pct[fy]*100):>7}%')
    print(f'  TOT   {sum(cur):>13,}{sum(pd):>13,}{sum(totals):>13,}')

print('\n\n=== JS arrays for index.html (curriculum + PD) ===')
def js(arr):
    return '[' + ','.join(str(int(x)) for x in arr) + ']'
print(f"      'K-5 ELA cur':    {js(ela_cur)},")
print(f"      'K-5 ELA pd':     {js(ela_pd)},")
print(f"      'K-5 Math cur':   {js(k5m_cur)},")
print(f"      'K-5 Math pd':    {js(k5m_pd)},")
print(f"      '6-12 Math cur':  {js(m612_cur)},")
print(f"      '6-12 Math pd':   {js(m612_pd)},")
print(f"      '6-12 ELA cur':   {js(ela612_cur)},")
print(f"      '6-12 ELA pd':    {js(ela612_pd)},")
