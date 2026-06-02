"""Central, portable path resolution for the Troy SD check-register pipeline.

Every path below derives from the location of THIS file, so the project is
fully portable: clone the repo anywhere and the build scripts find their
inputs and outputs without edits. This replaces the machine-specific
``C:\\Dev\\CheckRegister`` / ``C:\\Dev\\TroySD`` / ``%TEMP%`` paths that the
original one-off scripts hardcoded.

Directory layout (relative to this file):

    <repo root>/
    ├── index.html                                 <- DASHBOARD
    ├── Troy_SD_Check_Register_FY11-FY26.xlsx       <- WORKBOOK
    └── Working Folder/Cache and Tools/
        ├── source_data/
        │   ├── BoardDocs_PDFs/                     <- STANDALONE_PDFS (FY21-FY26)
        │   └── BoardDocs_PDFs_pre2020/             <- EMBEDDED_PDFS  (FY11-FY20)
        └── build/                                  <- BUILD (this dir)
            └── lookups/                            <- committed vendor lookups
"""
from pathlib import Path

# build/ -> "Cache and Tools"/ -> "Working Folder"/ -> <repo root>
BUILD = Path(__file__).resolve().parent
CACHE_AND_TOOLS = BUILD.parent
WORKING_FOLDER = CACHE_AND_TOOLS.parent
REPO_ROOT = WORKING_FOLDER.parent

# --- Source PDFs (large; mostly gitignored — see repo README "Source PDFs") ---
SOURCE_DATA = CACHE_AND_TOOLS / "source_data"
STANDALONE_PDFS = SOURCE_DATA / "BoardDocs_PDFs"          # FY21-FY26 standalone registers
EMBEDDED_PDFS = SOURCE_DATA / "BoardDocs_PDFs_pre2020"    # FY11-FY20 board-meeting packets

# --- Committed lookup data (re-derived from the deliverables; see build_lookups.py) ---
LOOKUPS = BUILD / "lookups"
VENDOR_CATEGORIES = LOOKUPS / "vendor_categories.json"    # {vendor: {category: total}}
VENDOR_SUBJECT = LOOKUPS / "vendor_subject.json"          # {vendor: subject} for Curriculum_PD

# --- Intermediate artifacts (gitignored — regenerable from source) ---
ALL_LINES_PKL = BUILD / "all_lines.pkl"        # standalone parse output
PRE2020_PKL = BUILD / "pre2020_lines.pkl"      # embedded parse output
OCT2019_PKL = BUILD / "oct2019_recovered.pkl"  # pypdf-recovered Oct 2019 register
COMBINED_PKL = BUILD / "combined_lines.pkl"    # merged + classified (assemble-stage input)

# --- Deliverables (repo root) ---
WORKBOOK = REPO_ROOT / "Troy_SD_Check_Register_FY11-FY26.xlsx"
DASHBOARD = REPO_ROOT / "index.html"
