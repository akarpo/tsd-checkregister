"""rebuild.py — single entry point for the Troy SD check-register pipeline.

Canonical end-to-end flow:

    parse standalone PDFs   (full_parse.py)              -> all_lines.pkl
    parse embedded packets  (pre2020_extract.py)         -> pre2020_lines.pkl
    recover Oct 2019        (recover_oct2019.py)          -> oct2019_recovered.pkl
    merge + classify        (rebuild_after_bundlefix.py)  -> combined_lines.pkl
    build workbook          (rebuild_final.build_workbook)        -> Troy_SD_Check_Register_FY11-FY26.xlsx
    build dashboard         (rebuild_dashboard_full.write_dashboard) -> index.html

The parse stages need pdfplumber/pypdf and the full source-PDF corpus (most of
which is NOT tracked in git — see the repo README "Source PDFs"). When you only
have combined_lines.pkl, or want to re-emit the deliverables after a data fix,
use --assemble-only to skip parsing and rebuild the workbook + dashboard.

Usage:
    python rebuild.py                  # full pipeline (needs source PDFs + pdfplumber)
    python rebuild.py --assemble-only  # rebuild workbook + dashboard from combined_lines.pkl
    python validate.py                 # verify a rebuild reconciles to the committed totals
"""
import argparse
import pickle
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _paths
from rebuild_final import build_workbook
from rebuild_dashboard_full import build_payload, write_dashboard

PARSE_STAGES = [
    ("parse standalone PDFs", "full_parse.py", _paths.ALL_LINES_PKL),
    ("parse embedded packets", "pre2020_extract.py", _paths.PRE2020_PKL),
    ("recover Oct 2019 register", "recover_oct2019.py", _paths.OCT2019_PKL),
    ("merge + classify", "rebuild_after_bundlefix.py", _paths.COMBINED_PKL),
]


def run_script(script):
    print(f"    $ python {script}", flush=True)
    res = subprocess.run([sys.executable, str(_paths.BUILD / script)], cwd=str(_paths.BUILD))
    if res.returncode != 0:
        raise SystemExit(f"stage failed: {script} (exit {res.returncode})")


def assemble():
    if not _paths.COMBINED_PKL.exists():
        raise SystemExit(
            f"missing {_paths.COMBINED_PKL.name}. Run the parse+merge stages first "
            f"(omit --assemble-only); that requires the source PDFs under source_data/."
        )
    combined = pickle.loads(_paths.COMBINED_PKL.read_bytes())
    print(f"[assemble] {len(combined):,} rows", flush=True)
    _, n, amt = build_workbook(combined, _paths.WORKBOOK)
    print(f"    workbook  -> {_paths.WORKBOOK.name}  ({n:,} rows / ${amt:,.2f})", flush=True)
    payload = build_payload(combined)
    write_dashboard(payload, _paths.DASHBOARD)
    print(f"    dashboard -> {_paths.DASHBOARD.name}  ({payload['meta']['totalLines']:,} lines / "
          f"{payload['meta']['sourceCount']} source registers)", flush=True)


def main():
    ap = argparse.ArgumentParser(description="Rebuild the Troy SD check-register deliverables.")
    ap.add_argument("--assemble-only", "--skip-parse", action="store_true", dest="assemble_only",
                    help="skip parse+merge; rebuild workbook + dashboard from combined_lines.pkl")
    args = ap.parse_args()

    t0 = time.time()
    if args.assemble_only:
        print("[assemble-only] skipping parse + merge stages\n", flush=True)
    else:
        for i, (label, script, _out) in enumerate(PARSE_STAGES, 1):
            print(f"[{i}/{len(PARSE_STAGES)}] {label}", flush=True)
            run_script(script)
        print()
    assemble()
    print(f"\nDone in {time.time() - t0:.0f}s.", flush=True)


if __name__ == "__main__":
    main()
