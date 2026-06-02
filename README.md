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

The original FY23-FY26 dashboard and workbook were built via the Claude.ai web interface (those prompts were not captured). The FY21-FY22 backfill (April 2026) and FY12-FY19 backfill (May 2026) were performed via Claude Code. The build pipeline lives under `Working Folder/Cache and Tools/build/` as a single, portable, self-contained flow — no machine-specific paths, no external lookup files — driven by `rebuild.py`:

| Stage | Script | Output |
|---|---|---|
| Parse standalone registers (FY21-FY26) | `full_parse.py` → `parser.py` | `all_lines.pkl` |
| Parse embedded packets (FY11-FY20) | `pre2020_extract.py` | `pre2020_lines.pkl` |
| Recover the Oct 2019 register (pypdf fallback) | `recover_oct2019.py` | `oct2019_recovered.pkl` |
| Merge + Issue-Date FY + categorize + classify | `rebuild_after_bundlefix.py` | `combined_lines.pkl` |
| Build the 8-sheet workbook | `rebuild_final.py` (`build_workbook`) | `Troy_SD_Check_Register_FY11-FY26.xlsx` |
| Build the dashboard payload | `rebuild_dashboard_full.py` (`write_dashboard`) | `index.html` |

Categorization (`categorize_v2.py`) and subject classification (`subjects.py`) read committed lookups in `build/lookups/` (`vendor_categories.json`, `vendor_subject.json`), regenerated from the deliverables by `build_lookups.py`. Superseded one-off scripts are kept in `build/archive/`.

```bash
cd "Working Folder/Cache and Tools/build"
python rebuild.py                  # full pipeline (needs source PDFs + pdfplumber/pypdf)
python rebuild.py --assemble-only  # rebuild workbook + dashboard from combined_lines.pkl
python validate.py                 # verify a rebuild reconciles to 224,267 lines / $1,227,024,514.73
```

**Caveats:**
- The **parse** stages need the full source-PDF corpus in `source_data/`, most of which is **not tracked in git** (see "Source PDFs" above). The **assemble** stages (workbook + dashboard) are fully reproducible and are validated against the committed totals by `validate.py`, which reconstructs the row set from the workbook itself — so no source PDFs are needed to verify them.
- The committed workbook and `index.html` are regenerated by this pipeline (`rebuild.py --assemble-only`, last run 2026-06-02) and verified consistent by `validate.py` — both reflect 224,267 lines / $1,227,024,514.73. Regenerating re-derives categories from the committed seed, which entailed a one-time ~0.56% category restatement vs the originally-published breakdown (grand total and per-FY totals unchanged); see `Working Folder/Cache and Tools/project_docs/INDEX.md`.
- The curriculum/PD spotlight in `index.html` (the hand-anchored `CURRICULUM_DATA` block) is regenerated separately and semi-manually via `split_curriculum_pd_v2.py` (run it, paste its JS arrays); `rebuild.py` does not touch it.
- `parser.py` was validated to within 0 rows / $0.00 against the original FY23-FY26 workbook (47,917 rows / $417,275,260.96).

See [`PROMPTS.md`](PROMPTS.md) for the prompt scaffold and [`Working Folder/Prompts/running.md`](Working%20Folder/Prompts/running.md) for the chronological prompt log.

## Source

All check registers were pulled from BoardDocs (https://go.boarddocs.com/mi/troysd/Board.nsf/Public). For FY21+, each was attached to the Treasurer's Report agenda item of the corresponding Regular Board of Education meeting. For FY12-FY19, the registers are embedded inside the larger meeting-packet PDFs (typically pages 30+ of a 100-250 page packet). Filenames are prefixed with the meeting date (`YYYY-MM-DD`) for sortability; the period each register actually covers is stated inside the PDF (typically meeting date minus ~2 months).

See `Working Folder/Cache and Tools/project_docs/INDEX.md` for fiscal-year coverage and known gaps.

## License

MIT — see [`LICENSE`](LICENSE).
