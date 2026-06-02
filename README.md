# Troy SD Check Register Reconciliation · FY11-FY26

Interactive dashboard and master workbook reconciling Troy School District (MI) check-register expenditures from FY2011 (partial) through FY2026-to-date, sourced from BoardDocs Treasurer's Reports and embedded check-register sections in board-meeting packets.

## Deliverables (repo root)

| File | What it is |
|---|---|
| `index.html` | Interactive dashboard (static, all data inlined). Open in any browser. |
| `Troy_SD_Check_Register_FY11-FY26.xlsx` | Master workbook — 8 sheets including both Meeting-FY and Issue-Date-FY pivots. 224,267 line items. |
| `Missing_Months_FY11-FY26.xlsx` | Gap audit — months with no register data, summary by FY, and the BoardDocs API probe log. |

## Coverage

- **FY11-FY20**: 152,649 line items extracted from 85 embedded check registers in monthly board-meeting packet PDFs (FY11 partial — bundle starts Jan 2011; FY17/FY21/FY22/FY23/FY25 fully complete; others have 1-7 month gaps)
- **FY21-FY26**: 71,618 line items from 67 standalone "Check register by fund" PDFs (BoardDocs began separating May 2020)
- **Total**: 224,267 line items, $1,227,024,514.73 across 16 fiscal years
- **Two FY columns** in the workbook: `Fiscal Year` (FY of the approving meeting, legacy) and `Issue Date FY` (true transaction FY, recommended for analysis)

## Project layout

```
tsd-checkregister/                           ← repo root (deliverables only)
├── index.html                               ← dashboard (static, hand-edited, data inlined)
├── Troy_SD_Check_Register_FY11-FY26.xlsx    ← master workbook (224,267 line items)
├── Missing_Months_FY11-FY26.xlsx            ← gap audit + BoardDocs probe log
├── README.md                                ← this file
├── PROMPTS.md                               ← structured build-prompt scaffold
└── Working Folder/                          ← tooling, source data, prompt history
    ├── Prompts/                             ← per-prompt archive + running.md log
    └── Cache and Tools/
        ├── build/                           ← parser, categorizer, rebuild scripts (Python)
        ├── source_data/
        │   └── BoardDocs_PDFs/              ← 45 standalone register PDFs tracked in git (May 2022 → Feb 2026); rest gitignored
        └── project_docs/
            └── INDEX.md                     ← provenance, FY coverage, known gaps
```

**Source PDFs are large and mostly excluded from git** (see `.gitignore`). The master workbook was built from 152 source registers — 85 embedded board-meeting packets (FY11-FY20) and 67 standalone "Check register by fund" PDFs (FY21-FY26) — but the repo tracks only the **45 standalone register PDFs** spanning May 2022 → Feb 2026, under `source_data/BoardDocs_PDFs/`. The remaining standalone registers (FY21 through early FY22) and all pre-2020 embedded packets (`BoardDocs_PDFs_pre2020/`, ~640 MB) are **not in git history** and must be re-downloaded from BoardDocs for a full from-scratch rebuild. The published deliverables are complete and current regardless — they contain the fully processed data.

## Reproducibility

The original FY23-FY26 dashboard and workbook were built via the Claude.ai web interface; those prompts were not captured. The FY21-FY22 backfill (April 2026) and FY12-FY19 backfill (May 2026) were performed via Claude Code with full source under `Working Folder/Cache and Tools/build/`:

- `parser.py` — Pentamation check register PDF parser (regex-based, validated to within 0 rows / $0.00 against original FY23-FY26 totals: 47,917 rows / $417,275,260.96)
- `pre2020_extract.py` — embedded-register extractor for 2011-2019 board-meeting packets; handles em-dash normalization
- `categorize_v2.py` — line categorization (vendor lookup + Michigan PSAM function-code rules)
- `full_parse.py` — orchestrator: parses all PDFs, applies categorization, emits `all_lines.pkl`
- `build_combined_wb.py` — combines pre-2020 + post-2020, applies categorization + subject classification, builds the 7-sheet xlsx
- `rebuild_dashboard.py` — rebuilds the inlined JSON payload in `index.html`

To re-run end-to-end:
```bash
cd "Working Folder/Cache and Tools/build"
python full_parse.py            # parse standalone registers (67) → all_lines.pkl  (~7 min)
python pre2020_extract.py       # extract embedded registers (85) → pre2020_lines.pkl  (~30 min)
python build_combined_wb.py     # merge + classify + build xlsx
python rebuild_dashboard.py     # update index.html payload
```

> **Reproducibility caveat:** This four-step sequence is the core post-2020 flow and assumes the full source-PDF corpus is present in `source_data/` (most of it is **not** tracked in git — see the source-PDF note above). The committed FY11-FY26 workbook was built incrementally on top of this flow: the 8th sheet (`By Issue-Date FY x Fund`), the Oct 2019 / FY20-FY21 register recoveries, and the FY11-FY22 backfill were applied by additional one-off scripts in `build/` (e.g. `rebuild_with_issue_fy.py`, `rebuild_final.py`), not a single clean entry point. Reproducing the exact committed workbook from scratch would require re-tracing those steps.

See [`PROMPTS.md`](PROMPTS.md) for the prompt scaffold and [`Working Folder/Prompts/running.md`](Working%20Folder/Prompts/running.md) for the chronological prompt log.

## Source

All check registers were pulled from BoardDocs (https://go.boarddocs.com/mi/troysd/Board.nsf/Public). For FY21+, each was attached to the Treasurer's Report agenda item of the corresponding Regular Board of Education meeting. For FY12-FY19, the registers are embedded inside the larger meeting-packet PDFs (typically pages 30+ of a 100-250 page packet). Filenames are prefixed with the meeting date (`YYYY-MM-DD`) for sortability; the period each register actually covers is stated inside the PDF (typically meeting date minus ~2 months).

See `Working Folder/Cache and Tools/project_docs/INDEX.md` for fiscal-year coverage and known gaps.

## License

MIT — see [`LICENSE`](LICENSE).
