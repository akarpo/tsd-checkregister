# Working Folder

Source data and project documentation for the Check Register Reconciliation project. The user-facing artifacts (`index.html`, `Troy_SD_Check_Register_FY11-FY26.xlsx`, `Missing_Months_FY11-FY26.xlsx`) live at the **repo root**, not here.

## Layout

```
tsd-checkregister/                           (git repo root — single source of truth for deliverables)
├── index.html                               ← dashboard (static, hand-edited)
├── Troy_SD_Check_Register_FY11-FY26.xlsx    ← master workbook
├── Missing_Months_FY11-FY26.xlsx            ← gap audit + BoardDocs probe log
├── README.md
├── PROMPTS.md                               ← structured build-prompt scaffold (reproducibility)
└── Working Folder/                          ← THIS FOLDER
    ├── README.md                            ← this file
    ├── Prompts/
    │   ├── running.md                       ← chronological one-line prompt log
    │   ├── TEMPLATE/                        ← shape of each timestamped prompt entry
    │   └── <YYYY-MM-DD_HH-MM-SS>/           ← one folder per logged prompt
    └── Cache and Tools/
        ├── build/                           ← the pipeline (rebuild.py orchestrator, validate.py, lookups/)
        ├── source_data/
        │   └── BoardDocs_PDFs/              ← 48 standalone register PDFs tracked in git (May 2022 → May 2026); most source PDFs gitignored
        └── project_docs/
            └── INDEX.md                     ← source notes, FY coverage, known gaps
```

## Fiscal year

One `Fiscal Year` column, derived from each line item's **issue date** on the
Michigan Jul 1 – Jun 30 boundary. `Source Meeting` is provenance only. The rule
and the source-date repairs live in `Cache and Tools/build/fiscal_year.py`; see
the root [`README.md`](../README.md#fiscal-year-attribution) for why the earlier
meeting-keyed column was retired (2026-07-27).

## Status

The original FY23-FY26 dashboard and workbook were built through the Claude.ai web interface; those prompts were not captured. The FY21-FY22 backfill (April 2026), FY12-FY19 backfill (May 2026), and the Mar-May 2026 ingest + single-fiscal-year refactor (July 2026) were done through Claude Code, which now provides a consolidated, portable build pipeline under `Cache and Tools/build/`: a single `rebuild.py` orchestrator (parse → merge → build workbook + dashboard), fiscal-year attribution in `fiscal_year.py`, committed vendor lookups in `build/lookups/`, a `validate.py` consistency check, and superseded one-offs in `build/archive/`. See the root [`README.md`](../README.md#reproducibility) for the stages, the `--assemble-only` path, and caveats.

Note that `validate.py` proves self-consistency only. Fidelity to source is checked separately by reconciling each register against the `TOTAL REPORT` total the PDF prints for itself — see the root README caveats.

A prompt-history scaffold lives under `Prompts/` and at the root in [`PROMPTS.md`](../PROMPTS.md). Any future revision (FY refresh, dashboard change, pipeline work) should be run through Claude Code with the prompt logged in both places, so the project stays reproducible going forward. If the original Claude.ai conversations are recovered, backfill them into the same structure.

Note: most source PDFs are excluded from git (see the root README "Source PDFs" note); the workbook and dashboard are committed as complete, current artifacts.
