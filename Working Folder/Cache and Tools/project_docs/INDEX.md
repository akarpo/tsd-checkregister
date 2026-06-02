# Troy School District Check Registers

Source: BoardDocs (https://go.boarddocs.com/mi/troysd/Board.nsf/Public)
Pulled: 2026-04-26 (initial FY23-FY26), 2026-04-30 (FY21-FY22 backfill), 2026-05-01 (FY12-FY19 backfill from embedded registers + bundle-date fix + Oct 2019 pypdf recovery), 2026-05-13 (BoardDocs API probe — recovered 3 standalone registers for Jun/Jul 2020 and Jan 2021; see "Bug/recovery history" below)
Total records: 224,267 line items, $1,227,024,514.73 *(post 2026-05-13 merge: +2,135 lines / +$24,300,137.47 from 3 recovered standalone registers; prior to this merge the workbook reflected 222,132 lines / $1,202,724,377.26)*
Source PDFs: ~236 (71 standalone + 84 embedded productive + 1 pypdf-recovered + 80 included from re-extraction with widened filter)

## Coverage by fiscal year (TSD FY = Jul 1 – Jun 30, named by ending year)

| FY | Lines (Meeting FY) | Amount (Meeting FY) | Months captured | Source format |
|---|---:|---:|---|---|
| FY11 | 10,300 | $20.9M | 4 of 12 (Jan-Jun 2011 only — bundle starts Jan 2011) | embedded |
| FY12 | 17,251 | $34.0M | 8 of 12 | embedded |
| FY13 | 10,525 | $24.0M | 7 of 12 | embedded |
| FY14 | 12,182 | $25.8M | 8 of 12 | embedded |
| FY15 | 20,335 | $80.2M | 9 of 12 | embedded |
| FY16 | 17,628 | $98.2M | 10 of 12 | embedded |
| **FY17** | **19,653** | **$116.8M** | **12 of 12 ✅** | embedded |
| FY18 | 16,310 | $81.8M | 10 of 12 | embedded |
| FY19 | 17,675 | $104.1M | 11 of 12 | embedded |
| FY20 | 7,883 | $37.8M | 5 of 12 | embedded + 1 pypdf-recovered |
| **FY21** | **10,812** | **$92.4M** | **12 of 12 ✅** *(post 2026-05-13 merge — was 10 of 12 before)* | standalone |
| **FY22** | **12,249** | **$73.4M** | **12 of 12 ✅** | standalone |
| **FY23** | **11,851** | **$76.3M** | **12 of 12 ✅** | standalone |
| FY24 | 12,617 | $107.6M | 11 of 12 (Nov 2023 missing) | standalone |
| **FY25** | **13,920** | **$140.3M** | **12 of 12 ✅** | standalone |
| FY26 | 10,169 | $106.5M | 10 of 12 (in progress) | standalone |

## Source format notes

- **Standalone format (May 2020 onward)**: BoardDocs began attaching "Check register by fund X.pdf" as separate documents on the Treasurer's Report agenda item. Pentamation Enterprises format, ~30 pages each. Located at `source_data/BoardDocs_PDFs/`. *(Note: earlier versions of this doc said "Aug 2020 onward" — verified 2026-05-13 via BoardDocs API probe that the May 2020 Treasurer's Report on the 2020-07-21 meeting was already standalone.)*
- **Embedded format (2011-2019)**: Check registers are pages within larger meeting-packet PDFs (typically pages 30-100 of 100-250 page packets), same Pentamation format but with em-dash characters (`−`) instead of ASCII hyphens. The pre-2020 extractor normalizes dashes. Productive source PDFs copied to `source_data/BoardDocs_PDFs_pre2020/`.

## Two FY columns — meeting date vs transaction date

The workbook exposes both:
- **`Fiscal Year`** = FY of the board MEETING that approved the register
- **`Issue Date FY`** = FY of the actual TRANSACTION DATE (true FY)

These differ because each register typically covers 1-2 months of *prior* activity. For accurate FY-by-FY analysis, use Issue Date FY (sheet "By Issue-Date FY x Fund" + "PD by Subject" pivot).

## Specific known gaps (months with no register data)

- **FY11**: Jul-Dec 2010 (6 months, before our corpus starts) + Aug & Dec 2011 workshops with no register
- **FY12**: 2011-07, 2011-09, 2012-02, 2012-05 (4 missing months)
- **FY13**: 2012-07, 2012-08, 2012-09, 2013-03, 2013-06 (5 missing — the 2013-03 Wksp may have had a register but workshop coverage is spotty)
- **FY14**: 2013-07, 2013-08, 2013-10, 2014-06 (4 missing — Reg meetings exist but no register attached)
- **FY15**: 2014-07, 2014-09, 2015-02 (3 missing)
- **FY16**: 2015-07, 2015-09 (2 missing)
- **FY17**: complete ✅
- **FY18**: 2017-07, 2018-06 (2 missing)
- **FY19**: 2018-07 only (1 missing — Jul 2018)
- **FY20**: 2019-07, 2020-01 through 2020-05 (6 missing — biggest residual gap; the BoardDocs transition window). *Jun 2020 ingested 2026-05-13 — adds ~$9.8M of FY20-attributed transactions to "By Issue-Date FY x Fund" (Meeting FY for that register is FY21 since it was approved at the Aug 2020 board meeting). May 2020 is listed on BoardDocs but the AWS S3 backend returns 404 for all attachments — likely lifecycle-deleted.*
- **FY21**: complete after 2026-05-13 recovery ✅. *Jul 2020 and Jan 2021 registers ingested — FY21 Meeting-FY now 12 of 12.*
- **FY22-FY23**: complete ✅
- **FY24**: 2023-11 (1 missing — Nov 2023 register was never posted; we have a Sep 2023 + Oct 2023 from the 2023-12-12 meeting but no Nov)
- **FY25**: complete ✅
- **FY26**: 2026-05, 2026-06 (in progress, not yet held)
- Pre-FY11 BoardDocs records are not available in the local TroySD corpus.

## Bug/recovery history

- **2026-05-01 bundle-date bug fix**: Original pre-2020 extractor used the parent-folder date for PDFs in 2011/2012 "Board Packets and Minutes" bundle folders (always 2011-12-31 / 2012-12-31), collapsing all 12 months of each year onto one meeting-date label. This made the audit appear far worse than reality (e.g., "FY12: only 1 month captured" was actually all 12 collapsed). Fixed by extracting date from the filename (e.g., `040913Mtg.pdf` → 2013-04-09) for bundle-folder PDFs.
- **2026-05-01 Oct 2019 pypdf recovery**: The 2019-10-15 Reg meeting PDF (`101519RegMtg.pdf`) errored under pdfplumber with `'dict' object has no attribute 'decode'`. Recovered separately using `pypdf` (1,418 rows / $9.5M of FY20 data). The main extractor now has a pypdf fallback for future runs.
- **2026-05-01 Wksp/Sp/Retreat inclusion**: Original 2011/2012 bundle filter excluded workshop/special meetings. Now includes all PDFs and lets the PENTAMATION marker decide; this caught 0 additional registers (workshops have no register attachments).
- **2026-05-13 BoardDocs API probe + FY20/FY21 recovery**: Reviewed the 19 "Maybe" months from the gap list via direct BoardDocs API (BD-GetMeetingsList → BD-GetAgenda → BD-GetPublicFiles, using committee `A4EP6J588C05`). Found three standalone register PDFs missing from the corpus: `Check register by fund Jun 2020 period 12.pdf`, `Check register by fund Jul 2020.pdf`, `Check register by fund Jan 21.pdf`. Downloaded to `source_data/BoardDocs_PDFs/`. May 2020 register is listed on the 2020-07-21 agenda but every file in that Treasurer's Report item returns HTTP 404 from BoardDocs' S3 backend (lifecycle-cleaned). Five "Maybe" months (FY12 2011-09/2012-02/2012-05, FY13 2012-09, FY18 2018-06) have no meetings in the BoardDocs Public feed at all — those years are heavily culled (1 meeting each visible). Also corrected the "Aug 2020 onward" transition claim above to "May 2020 onward".
- **2026-06-02 pipeline consolidation + deliverable regeneration**: The build pipeline was consolidated into a single portable `rebuild.py` + `validate.py` under `build/` (machine-specific `C:\Dev` / `%TEMP%` paths removed; the two lost classification lookups re-derived from committed artifacts into `build/lookups/`). The workbook and `index.html` were then regenerated from the committed data via `rebuild.py --assemble-only`, resolving two inconsistencies in the prior (patchwork) artifacts: the dashboard data had lagged the workbook at 222,132 lines (now 224,267, matching), and the workbook's README/pivot/PD-summary sheets had been built by mixed script versions. Because the original per-row categorization was never persisted (the dashboard retained only the top-25 vendors per category), regeneration re-derives categories from the committed seed (`vendor_categories.json`) — a one-time **~0.56% category restatement** (~$6.9M of $1.227B, entirely long-tail vendors below the top-25 cutoff; grand total and per-FY totals unchanged). Categorization is now deterministic and reproducible from the committed seed.

## Date anomalies (3 lines)

3 lines have implausible Issue Dates: 2 × COMPASS GROUP USA dated 2061-09-09 ($164K), 1 × ADN ADMINISTRATOR dated 2031-01-01 ($16K). Appear under "FY62" / "FY31" in the Issue-Date FY pivot. Likely OCR misreads in source PDFs. Inspect/correct against source if needed.

## Parser provenance

- Standalone PDFs: `parser.py` (regex-based). Validated against original FY23-FY26 workbook exactly: 47,917 rows / $417,275,260.96.
- Embedded PDFs: `pre2020_extract.py` (same regex with em-dash normalization + bundle-date fix + pypdf fallback). No equivalent ground truth exists for these.

## Categorization

`categorize_v2.py` applies a vendor-lookup-first rule (built from FY23-FY26 vendor frequencies) with Michigan PSAM function-code fallback. New vendors that appear only in FY11-FY19 get categorized purely by function-code rules. Estimated category-level accuracy is ~83% (matches original payload to within 2% for 7 of 28 categories; remaining categories have 5-50% drift). Grand totals exact.

## Subject classification (Curriculum_PD sheet)

Vendor → subject mapping originally built from the FY23-FY26 Curriculum_PD sheet (87 vendors), expanded 2026-05-01 with 51 pre-2020 vendors identified by manual review of the Curriculum_PD "Not Directly Attributable" tail (now 138 vendors total). Falls back to keyword matching on truncated descriptions for unmatched vendors. Confidence "high" = exact vendor match; "med" = keyword match; "low" = no signal.

After lookup expansion, only 30 pre-2020 PD lines / $8,703 remain unclassified (down from 256 lines / $326,374 — a 97% improvement). The remaining tail consists of generic conference registrations, single-line presenter honorariums, and Aplia/Saga course platforms with no subject signal in the truncated description.

## Source PDFs in repo

- `source_data/BoardDocs_PDFs/` — 68 standalone "Check register by fund" PDFs (~75 MB)
- `source_data/BoardDocs_PDFs_pre2020/` — 83 board-meeting packet PDFs containing embedded registers (~640 MB). Note: a few additional productive PDFs from the re-extraction (with widened filter) remain at the original `C:\Dev\TroySD\` path; they would need to be re-copied if a fully-self-contained build is desired.
