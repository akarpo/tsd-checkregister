"""Split K-5 ELA, K-5 Math, 6-12 Math spend into Curriculum (materials) vs PD by Issue FY.

Methodology:
- PD = lines whose Budget Unit starts with '101425221' (function 221 = Improvement of Instruction)
        OR known PD vendors (TCRWP, AVMR/Math Recovery, IM/Illustrative Math PD providers, etc.)
- Curriculum = everything else (textbook/materials buys, instructional supplies, etc.)

Reproduces the same totals as the existing CURRICULUM_DATA hard-coded in index.html so the split sums match the bar.
"""
import pickle
from pathlib import Path
from collections import defaultdict

combined = pickle.loads(Path('combined_lines.pkl').read_bytes())
print(f'Loaded: {len(combined):,} rows')

# --- swimlane membership rules (must reproduce the existing CURRICULUM_DATA totals) ---

def matches_any(s, *kws):
    s = (s or '').upper()
    return any(k in s for k in kws)

def k5_ela(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    bu = r.get('Budget Unit') or ''
    # Vendor signals
    if matches_any(v, 'HARCOURT', 'HOUGHTON MIFFLIN', 'HMH PUBLISH'):
        if matches_any(d, 'JOURNEYS','READ','WRITE','LITERACY','SPELLING','PHONICS','ELA','LANG ARTS','LANGUAGE ARTS','LEVELED','LEXIA','GRAMMAR'):
            return True
    if matches_any(v, 'HEINEMANN', 'TEACHERS COLLEGE', 'READING AND WRI', 'READING WRITING PRO', 'THE READING AND WRI', 'FOUNTAS', 'CALKINS'):
        return True
    if matches_any(v, 'SCHOLASTIC') and matches_any(d, 'BOOK','READ','LITERACY','LEVELED','LIBRARY'):
        return True
    if matches_any(v, 'LEARNING A-Z', 'RAZ', 'LEXIA', 'LITERACY FOOTPRINTS'):
        return True
    if matches_any(v, 'BENCHMARK ED', 'WILSON LANGUAGE', 'READING RECOVERY'):
        return True
    return False

def k5_math(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    if matches_any(v, 'HARCOURT', 'HOUGHTON MIFFLIN', 'HMH PUBLISH'):
        if matches_any(d, 'MATH','EXPRESS','GO MATH'):
            return True
    if matches_any(v, 'MATH LEARNING CENTER', 'BRIDGES', 'AVMR', 'MATH RECOVERY', 'US MATH RECOVERY', 'ORIGO'):
        return True
    if matches_any(v, 'EUREKA', 'GREAT MINDS') and matches_any(d, 'MATH','ELEM'):
        return True
    if matches_any(v, 'PEARSON') and matches_any(d, 'MATH'):
        # only if elementary signal in description
        if matches_any(d, 'ELEM','GRADE','K-','PRIMARY'):
            return True
    return False

def m612_math(r):
    v = (r.get('Vendor Name') or '').upper()
    d = (r.get('Description') or '').upper()
    if matches_any(v, 'BIG IDEAS', 'LARSON TEXT', 'CENGAGE') and matches_any(d, 'MATH','ALGEBRA','GEOMETRY'):
        return True
    if matches_any(v, 'KENDALL HUNT', 'ILLUSTRATIVE MATH', 'IM CERTIFIED'):
        return True
    if matches_any(v, 'MCGRAW', 'PEARSON') and matches_any(d, 'ALGEBRA','GEOMETRY','PRECALC','TRIG','CALCULUS','HS MATH'):
        return True
    if matches_any(v, 'HOUGHTON MIFFLIN', 'HMH PUBLISH') and matches_any(d, 'ALGEBRA','GEOMETRY','HS MATH','SECONDARY'):
        return True
    if matches_any(d, 'BIG IDEAS') and matches_any(d, 'MATH','ALGEBRA','GEOMETRY'):
        return True
    return False

def is_pd(r):
    bu = r.get('Budget Unit') or ''
    if bu.startswith('101425221'):
        return True
    fc = (r.get('Function Code') or '').strip()
    if fc == '221':
        return True
    v = (r.get('Vendor Name') or '').upper()
    # Vendor-based PD (PD-only vendors regardless of budget unit)
    if matches_any(v, 'TEACHERS COLLEGE', 'READING AND WRI', 'READING WRITING PRO', 'THE READING AND WRI'):
        return True
    if matches_any(v, 'AVMR', 'MATH RECOVERY', 'US MATH RECOVERY'):
        return True
    return False

FY_LIST = ['FY11','FY12','FY13','FY14','FY15','FY16','FY17','FY18','FY19','FY20',
           'FY21','FY22','FY23','FY24','FY25','FY26']

def compute(membership_fn, label):
    cur = defaultdict(float)
    pd  = defaultdict(float)
    for r in combined:
        if not membership_fn(r):
            continue
        fy = r.get('Issue Date FY') or ''
        if fy not in FY_LIST:
            continue
        if is_pd(r):
            pd[fy] += r['Amount']
        else:
            cur[fy] += r['Amount']
    print(f'\n{label}:')
    print(f'  {"FY":<6}{"Curriculum":>14}{"PD":>14}{"Total":>14}')
    for fy in FY_LIST:
        print(f'  {fy:<6}{cur[fy]:>14,.0f}{pd[fy]:>14,.0f}{cur[fy]+pd[fy]:>14,.0f}')
    print(f'  {"TOT":<6}{sum(cur.values()):>14,.0f}{sum(pd.values()):>14,.0f}{sum(cur.values())+sum(pd.values()):>14,.0f}')
    return cur, pd

ela_cur, ela_pd = compute(k5_ela, 'K-5 ELA')
k5m_cur, k5m_pd = compute(k5_math, 'K-5 Math')
m612_cur, m612_pd = compute(m612_math, '6-12 Math')

# Emit JS arrays that match index.html FY ordering
print('\n\n=== JS arrays for index.html ===')
def js(arr_dict):
    return '[' + ','.join(f'{int(round(arr_dict[fy]))}' for fy in FY_LIST) + ']'

print(f"'K-5 ELA cur':    {js(ela_cur)},")
print(f"'K-5 ELA pd':     {js(ela_pd)},")
print(f"'K-5 Math cur':   {js(k5m_cur)},")
print(f"'K-5 Math pd':    {js(k5m_pd)},")
print(f"'6-12 Math cur':  {js(m612_cur)},")
print(f"'6-12 Math pd':   {js(m612_pd)},")

# Compare totals against the hard-coded values in index.html
EXPECTED = {
    'K-5 ELA':   [1097,19130,923530,10721,11895,52419,247434,311897,494802,99189,218878,186538,305069,291826,289380,282867],
    'K-5 Math':  [2350,10176,12421,696718,12933,16361,22262,94,1385,197908,308055,319786,553956,567481,423042,319524],
    '6-12 Math': [0,267168,11000,276001,192651,39584,14040,0,0,3719,97560,1500,99903,215087,211095,256268],
}

print('\n=== Reconciliation vs hard-coded totals ===')
for label, exp, got_cur, got_pd in [
    ('K-5 ELA', EXPECTED['K-5 ELA'], ela_cur, ela_pd),
    ('K-5 Math', EXPECTED['K-5 Math'], k5m_cur, k5m_pd),
    ('6-12 Math', EXPECTED['6-12 Math'], m612_cur, m612_pd),
]:
    print(f'\n{label}:')
    for i, fy in enumerate(FY_LIST):
        got = got_cur[fy] + got_pd[fy]
        diff = got - exp[i]
        marker = '   ' if abs(diff) < 1 else ' ***'
        print(f'  {fy}  expected={exp[i]:>10,}  got={int(round(got)):>10,}  diff={int(round(diff)):>10,}{marker}')
