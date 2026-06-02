"""Categorization rules — function-code first, fund-only as fallback."""
from __future__ import annotations

def categorize(fund, func, account, bu, amt, vendor=''):
    fund = (fund or '').strip()
    func = (func or '').strip()
    account = (account or '').strip()
    bu = (bu or '').strip()

    f3 = func[:3] if len(func) >= 3 else func
    f2 = func[:2] if len(func) >= 2 else func

    is_sub = account in ('1240', '1241')

    if f3 == '111' or (len(func)==3 and func.startswith('11') and func[2] in '23456789'):
        if is_sub: return 'Instruction — Substitute Teachers (General Classes)'
        return 'Instruction — Basic Programs (Elementary/Secondary)'
    if f3 in ('112', '113'):
        if is_sub: return 'Instruction — Substitute Teachers (General Classes)'
        return 'Instruction — Basic Programs (Elementary/Secondary)'
    if f3 == '122':
        if is_sub: return 'Instruction — Substitute Teachers (Special Education)'
        return 'Instruction — Special Education'
    if f3 == '125':
        if is_sub: return 'Instruction — Substitute Teachers (Special Education)'
        return 'Instruction — Compensatory Education'
    if f2 == '13': return 'Instruction — Adult / Continuing Ed'
    if f2 == '14': return 'Instruction — Vocational / CTE'

    if f2 == '21': return 'Support — Pupil Services (Counsel/Health/Psych)'
    if f2 == '22': return 'Support — Instructional Staff (PD/Curriculum)'
    if f2 == '23': return 'Support — General Administration'
    if f2 == '24': return 'Support — School Administration'
    if f3 == '252': return 'Support — Business Services'
    if f2 == '25': return 'Support — Central Services / Personnel'
    if f2 == '26': return 'Support — Operations & Maintenance'
    if f2 == '27': return 'Support — Transportation'
    if f2 in ('28', '29'): return 'Support — Other'

    if f2 == '33': return 'Community — Athletics & Activities'
    if f2 in ('32', '34', '35', '39', '41'): return 'Community — Other Services'

    if f2 in ('45', '46'): return 'Capital Outlay — Land/Buildings'
    if f2 == '51': return 'Debt Service'

    if account.startswith('L'):
        return 'Payroll Deductions / Garnishments'

    if fund and fund.startswith('4') and len(fund) == 3:
        return 'Capital Outlay — Land/Buildings'
    if fund and fund.startswith('3') and len(fund) == 3:
        return 'Debt Service'

    if fund == '520': return 'Food Service Fund — Untyped'
    if fund in ('700', '701', '750'): return 'Student Activity Fund — Untyped'

    if bu and len(bu) <= 4:
        return 'Payroll Batch (Function not coded)'
    if amt < 0 and not func:
        return 'Refunds / Credits'

    return 'Untyped (function code blank or 000)'

if __name__ == '__main__':
    import openpyxl, json
    from pathlib import Path
    from collections import defaultdict
    wb = openpyxl.load_workbook(r'C:\Dev\CheckRegister\Troy_SD_Check_Register_FY23-FY26.xlsx', read_only=True, data_only=True)
    payload = json.loads(Path(r'C:\Users\Alex\AppData\Local\Temp\dashboard_payload.json').read_text(encoding='utf-8'))
    expected = {c: d['total'] for c, d in payload['all']['categories'].items()}
    actual = defaultdict(float)
    for r in wb['All Lines'].iter_rows(values_only=True):
        if r[0] == 'Source Meeting': continue
        cat = categorize(str(r[2] or ''), str(r[11] or ''), str(r[12] or ''),
                         str(r[10] or ''), r[15] or 0)
        actual[cat] += r[15] or 0
    print(f'{"Category":<55} {"Expected":>16} {"Actual":>16} {"Diff":>14} {"Pct":>7}')
    matched = 0
    total = sum(expected.values())
    for cat in sorted(expected, key=lambda c: -expected[c]):
        exp = expected[cat]; act = actual.get(cat, 0); diff = act - exp
        pct = (diff / exp * 100) if exp else 0
        ok = 'OK' if abs(diff) < 5000 else '  '
        print(f'{ok} {cat:<53} {exp:>16,.0f} {act:>16,.0f} {diff:>+14,.0f} {pct:>+6.1f}%')
        if abs(diff) < 5000: matched += exp
    extra = set(actual) - set(expected)
    if extra:
        print('Extras:', extra)
    print(f'\nGrand: ${sum(actual.values()):,.2f} (vs ${total:,.2f}, diff ${sum(actual.values())-total:+,.2f})')
    print(f'Match within $5K: {matched/total*100:.1f}%')
