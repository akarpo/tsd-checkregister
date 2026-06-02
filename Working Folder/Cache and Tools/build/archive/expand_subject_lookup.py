"""Expand vendor → subject lookup with pre-2020 vendors I've identified by inspection.

Source of identifications: manual review of FY12-FY19 'Not Directly Attributable' PD lines
in Curriculum_PD (budget unit 101425221), grouped by vendor and inspected by description.
"""
import pickle
from pathlib import Path

# Load existing lookup (FY23-FY26 vendor → subject)
existing = pickle.loads(Path(r'C:\Users\Alex\AppData\Local\Temp\vendor_subject.pkl').read_bytes())
print(f'Existing FY23-FY26 lookup: {len(existing)} vendors')

# Expanded mappings — pre-2020 vendor name → subject (uses 19-char prefix matching)
EXPANDED = {
    # ELA / Literacy
    'GREENWOOD PUBLISHIN': 'ELA',          # Fountas & Pinnell publisher
    'THE READING AND WRI': 'ELA',          # Reading Recovery Homegrown / TCRWP
    'NATALIE HAEZEBROUCK': 'ELA',          # Teachers College / book club reimbursement
    'MI READING ASSOC (M': 'ELA',          # Michigan Reading Association
    'LAMINACK LESTER':    'ELA',           # Lester Laminack — literacy author/PD
    'OAKLAND UNIVERSITY':  'ELA',          # AP Lang & Comp Summer Institute (English)

    # Science
    'BATTLE CREEK PUBLIC': 'Science',      # Physical Sci / Earth Science textbook codes
    'NATL SCIENCE TEACHE': 'Science',      # NSTA Summer Institute
    'CREAN JASON J':       'Science',      # NGSS Implementation

    # Health / Safety (CPR / First Aid / PE)
    'C P R PLUS':         'Health / Safety',
    'BEAUMONT HOSPITAL-T': 'Health / Safety',
    'WILLIAM BEAUMONT HO': 'Health / Safety',
    'BAINES BRYAN':       'Health / Safety',
    'BAINES BRIAN K':     'Health / Safety',
    'ASHOK HOLDINGS INC': 'Health / Safety',  # PE PD
    'BALAMUCKI SUSAN M':  'Health / Safety',  # PE PD presenter

    # Leadership / Coaching
    'THE DANIELSON GROUP': 'Leadership / Coaching',
    'MI INST FOR EDUCATI': 'Leadership / Coaching',  # Galileo Leadership Retreat
    'RITCHHART RONALD E':  'Leadership / Coaching',  # Ron Ritchhart (Making Thinking Visible)
    'MIRAKOVITS KATHY J':  'Leadership / Coaching',  # Boogren/Fakhouri workshops
    'ALL MI COUNSELORS F': 'Leadership / Coaching',  # Counselors conference

    # Equity / Culturally Responsive
    'R & J CONSULTING GR': 'Equity / Culturally Responsive',  # Diversity consulting
    'METZGER KURT ROBERT': 'Equity / Culturally Responsive',  # Diversity council honorarium

    # Whole Child / SEL (Early Childhood)
    'PARSONS STEPHANIE':   'Whole Child / SEL',  # MTSS / PreK Summer Institute
    'HUMPHREY JENNIFER':   'Whole Child / SEL',  # MTSS / PreK Summer Institute
    'OAKLAND SCHOOLS':     'Whole Child / SEL',  # HighScope (PreK curriculum) / MICLASS

    # Maker / Innovation (tech-focused PD)
    'JR ABUD GARY G':      'Maker / Innovation',  # BYOD presenter
    'TODD CINDY':          'Maker / Innovation',  # Design Thinking presentation
    'APPLE COMPUTER INC':  'Maker / Innovation',  # iPads/MacBooks for curriculum

    # Arts (Visual/Performing)
    'NOTEFLIGHT LLC':      'Arts (Visual/Performing)',  # Music notation software K12/Fine Art

    # World Languages
    'TYLER HANCSAK':       'World Languages',  # AP French reimbursement
    'OAKLAND UNIVERSITY/': 'World Languages',  # Spanish instructor (the / suffix variant)
    'COLLEGE BOARD MWRO':  'World Languages',  # AP Spanish (mostly)

    # Assessment / Data
    'CALE ELLEN':          'Assessment / Data',  # AGP Testing
    'METRO DETROIT BUREA': 'Assessment / Data',  # SAT prep

    # Materials / Logistics (printing, supplies, hardware not curriculum-specific)
    'KONICA MINOLTA BUSI': 'Materials / Logistics',
    'AN CLAWSON - TROY C': 'Materials / Logistics',
    'IMPRESSION CENTER':   'Materials / Logistics',
    'STAPLES ADVANTAGE':   'Materials / Logistics',
    'METROPOLITAN PUBLIS': 'Materials / Logistics',
    'UNITED PARCEL SERVI': 'Materials / Logistics',
    'K R COMPANY LLC':     'Materials / Logistics',
    'V S C INC':           'Materials / Logistics',
    'HEWLETT PACKARD CO':  'Materials / Logistics',
    'C D W GOVERNMENT IN': 'Materials / Logistics',
    'NETECH CORP':         'Materials / Logistics',
    'DELL MARKETING LP':   'Materials / Logistics',
    'PRESIDIO HOLDINGS I': 'Materials / Logistics',
    'MICRO CENTER SALES':  'Materials / Logistics',
    'INACOMP TECHNICAL S': 'Materials / Logistics',
    'MARY KELSEY WITT':    'Materials / Logistics',  # mileage reimbursement
    'HALL RHODA':          'Materials / Logistics',  # T&L petty cash
    'ANDREA MCCUNE':       'Materials / Logistics',  # mileage reimbursement
    'GINGER PETTY':        'Materials / Logistics',  # PD-related petty
    'HAVEN':               'Materials / Logistics',  # presenter/materials (generic)
}

# Merge — expanded entries WIN over existing if keys collide (they shouldn't here)
combined = dict(existing)
combined.update(EXPANDED)
print(f'Expanded lookup: {len(combined)} vendors (+{len(combined) - len(existing)} new)')

Path(r'C:\Users\Alex\AppData\Local\Temp\vendor_subject.pkl').write_bytes(pickle.dumps(combined))
print('Saved updated lookup to vendor_subject.pkl')
