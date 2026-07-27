# Troy School District Check Registers

Source: BoardDocs (https://go.boarddocs.com/mi/troysd/Board.nsf/Public)
Pulled: 2026-04-26 (initial FY23-FY26), 2026-04-30 (FY21-FY22 backfill), 2026-05-01 (FY12-FY19 backfill from embedded registers + bundle-date fix + Oct 2019 pypdf recovery), 2026-05-13 (BoardDocs API probe — recovered 3 standalone registers for Jun/Jul 2020 and Jan 2021), 2026-07-27 (Mar/Apr/May 2026 registers + single-FY refactor; see "Bug/recovery history" below)
Total records: 227,066 line items, $1,277,793,488.14 *(post 2026-07-27 merge: +2,799 lines / +$50,768,973.41 from the Mar/Apr/May 2026 registers; prior to this merge the workbook reflected 224,267 lines / $1,227,024,514.73)*
Source PDFs: ~239 (74 standalone + 84 embedded productive + 1 pypdf-recovered + 80 included from re-extraction with widened filter)

## Coverage by fiscal year (Michigan FY = Jul 1 – Jun 30, named by ending year)

Every line item is attributed to the FY containing its **issue date**. A month
counts as covered when it holds 100+ line items; below that it is only stray
adjustments carried in by an adjacent register, not a real disbursement run.

Note that coverage reads better here than under the retired meeting-keyed
scheme, and legitimately so: a register covers 1-2 months of prior activity, so
an unposted register does not necessarily leave a hole — adjacent registers
usually carry those dates. FY24's missing Nov 2023 register is the clearest
case: no transaction-month gap results from it.

| FY | Lines | Amount | Months covered | Source format |
|---|---:|---:|---|---|
| FY11 | 12,066 | $24.3M | 8 of 12 (Jul-Oct 2010 absent — corpus starts Nov 2010) | embedded |
| **FY12** | **17,360** | **$34.2M** | **12 of 12 ✅** | embedded |
| FY13 | 13,183 | $30.1M | 10 of 12 (Apr, May 2013) | embedded |
| FY14 | 14,817 | $32.7M | 11 of 12 (Sep 2013) | embedded |
| FY15 | 18,050 | $77.5M | 11 of 12 (Dec 2014) | embedded |
| **FY16** | **19,257** | **$107.6M** | **12 of 12 ✅** | embedded |
| **FY17** | **18,065** | **$109.4M** | **12 of 12 ✅** | embedded |
| FY18 | 16,094 | $86.2M | 10 of 12 (Apr, May 2018) | embedded |
| FY19 | 17,374 | $95.0M | 11 of 12 (May 2019) | embedded |
| FY20 | 8,243 | $47.6M | 6 of 12 (Nov 2019 - Apr 2020) | embedded + 1 pypdf-recovered |
| FY21 | 11,019 | $85.5M | 11 of 12 (Nov 2020) | standalone |
| **FY22** | **12,459** | **$76.4M** | **12 of 12 ✅** | standalone |
| **FY23** | **12,124** | **$78.1M** | **12 of 12 ✅** | standalone |
| **FY24** | **12,274** | **$106.7M** | **12 of 12 ✅** | standalone |
| **FY25** | **14,048** | **$144.4M** | **12 of 12 ✅** | standalone |
| FY26 | 10,633 | $142.1M | 11 of 12 (Jun 2026 register not yet approved) | standalone |

## Two different "gap" measures — don't conflate them

- **This document's coverage table** counts *transaction* months with no
  substantive activity. It is the one that matters for FY-by-FY analysis.
- **`Missing_Months_FY11-FY26.xlsx`** (repo root) counts months whose *register*
  is unavailable on BoardDocs — a source-availability audit, with the per-month
  reason and the API probe log.

They diverge because a register covers 1-2 months of prior activity, so an
unposted register usually leaves no hole: adjacent registers carry those dates.
FY24 is the clearest case — the Nov 2023 register was never posted, yet FY24
has full transaction coverage. The gap audit is currently 40 months / 37
unrecovered; the coverage table shows 7 complete fiscal years.

## Source format notes

- **Standalone format (May 2020 onward)**: BoardDocs began attaching "Check register by fund X.pdf" as separate documents on the Treasurer's Report agenda item. Pentamation Enterprises format, ~30 pages each. Located at `source_data/BoardDocs_PDFs/`. *(Note: earlier versions of this doc said "Aug 2020 onward" — verified 2026-05-13 via BoardDocs API probe that the May 2020 Treasurer's Report on the 2020-07-21 meeting was already standalone.)*
- **Embedded format (2011-2019)**: Check registers are pages within larger meeting-packet PDFs (typically pages 30-100 of 100-250 page packets), same Pentamation format but with em-dash characters (`−`) instead of ASCII hyphens. The pre-2020 extractor normalizes dashes. Productive source PDFs copied to `source_data/BoardDocs_PDFs_pre2020/`.

## One fiscal year — the transaction date governs

Michigan school districts run a July 1 – June 30 fiscal year, named by the
ending year (FY26 = 2025-07-01 through 2026-06-30). Every line item is
attributed to the FY containing its **issue date** — the date the disbursement
was actually made. There is a single `Fiscal Year` column.

`Source Meeting` is retained as provenance (which board meeting approved the
register) but does not drive attribution. The earlier scheme carried a second,
meeting-keyed FY column; because a register is approved 1-2 months after the
activity it covers, that convention shifted spend into the following year and,
at the July boundary, into the following FY entirely — the May 2026 register,
approved 2026-07-22, would have opened a spurious FY27 holding FY26 money.
Retired 2026-07-27.

## Specific known gaps (transaction months with no substantive register data)

Months below hold fewer than 100 line items — only stray adjustments carried in
by an adjacent register.

- **FY11**: 2010-07 through 2010-10 (4 months, before the corpus starts)
- **FY12**: complete ✅
- **FY13**: 2013-04 (4 lines), 2013-05 (5 lines)
- **FY14**: 2013-09 (1 line)
- **FY15**: 2014-12 (4 lines)
- **FY16, FY17**: complete ✅
- **FY18**: 2018-04 (5 lines), 2018-05 (51 lines)
- **FY19**: 2019-05 (16 lines)
- **FY20**: 2019-11 through 2020-04 (6 months — the biggest residual gap; the BoardDocs transition window). *May 2020 is listed on BoardDocs but the AWS S3 backend returns 404 for all attachments — likely lifecycle-deleted.*
- **FY21**: 2020-11 (3 lines)
- **FY22, FY23, FY24, FY25**: complete ✅ *(FY24 despite the Nov 2023 register never being posted — adjacent registers carry those dates)*
- **FY26**: 2026-06 (1 line) — the June 2026 register is approved at the August 2026 meeting, not yet held. Complete through May 2026.
- Pre-FY11 BoardDocs records are not available in the local TroySD corpus.

## Bug/recovery history

- **2026-05-01 bundle-date bug fix**: Original pre-2020 extractor used the parent-folder date for PDFs in 2011/2012 "Board Packets and Minutes" bundle folders (always 2011-12-31 / 2012-12-31), collapsing all 12 months of each year onto one meeting-date label. This made the audit appear far worse than reality (e.g., "FY12: only 1 month captured" was actually all 12 collapsed). Fixed by extracting date from the filename (e.g., `040913Mtg.pdf` → 2013-04-09) for bundle-folder PDFs.
- **2026-05-01 Oct 2019 pypdf recovery**: The 2019-10-15 Reg meeting PDF (`101519RegMtg.pdf`) errored under pdfplumber with `'dict' object has no attribute 'decode'`. Recovered separately using `pypdf` (1,418 rows / $9.5M of FY20 data). The main extractor now has a pypdf fallback for future runs.
- **2026-05-01 Wksp/Sp/Retreat inclusion**: Original 2011/2012 bundle filter excluded workshop/special meetings. Now includes all PDFs and lets the PENTAMATION marker decide; this caught 0 additional registers (workshops have no register attachments).
- **2026-05-13 BoardDocs API probe + FY20/FY21 recovery**: Reviewed the 19 "Maybe" months from the gap list via direct BoardDocs API (BD-GetMeetingsList → BD-GetAgenda → BD-GetPublicFiles, using committee `A4EP6J588C05`). Found three standalone register PDFs missing from the corpus: `Check register by fund Jun 2020 period 12.pdf`, `Check register by fund Jul 2020.pdf`, `Check register by fund Jan 21.pdf`. Downloaded to `source_data/BoardDocs_PDFs/`. May 2020 register is listed on the 2020-07-21 agenda but every file in that Treasurer's Report item returns HTTP 404 from BoardDocs' S3 backend (lifecycle-cleaned). Five "Maybe" months (FY12 2011-09/2012-02/2012-05, FY13 2012-09, FY18 2018-06) have no meetings in the BoardDocs Public feed at all — those years are heavily culled (1 meeting each visible). Also corrected the "Aug 2020 onward" transition claim above to "May 2020 onward".
- **2026-07-27 new registers + single-FY refactor + three defect fixes**: Pulled the Mar, Apr and May 2026 registers from BoardDocs (approved 2026-05-19, 2026-06-16, 2026-07-22) — +2,799 lines / +$50,768,973.41, bringing FY26 to complete through May 2026. Four changes shipped alongside:
  1. **Single fiscal-year attribution.** The dual `Fiscal Year` (meeting) / `Issue Date FY` scheme was collapsed to one `Fiscal Year` derived from the issue date on the Jul 1 – Jun 30 boundary (`build/fiscal_year.py`). This was forced by the May 2026 register: approved 2026-07-22, it would have opened an FY27 bucket holding entirely FY26 money. Workbook drops from 8 sheets to 7 (`By Issue-Date FY x Fund` became redundant).
  2. **Parser fix — 16-digit budget units.** `LINE_RE` capped the budget-unit group at `\d{3,15}`, so detail lines on capital-projects fund 423 (e.g. `4230514556430000`) were silently dropped. Caught by reconciling against the PDFs' own `TOTAL REPORT`: the Apr 2026 register was short exactly $35,188.11 across 4 lines. Widened to `\d{3,20}`; all 48 standalone registers now reconcile (see "Parser provenance").
  3. **Dashboard regex fix.** `write_dashboard` ran a blanket `re.sub(r'FY\d\d-FY\d\d', ...)` across the whole page, so the 2026-06-02 rebuild overwrote 8 hand-written adoption-cycle spans in the curriculum narrative — "Cycle 1 (FY12-FY15)" had become "Cycle 1 (FY11-FY26)", "peaked off-cycle in FY17-FY18" became "...in FY11-FY26", and so on. Now anchored to the five real site-wide range labels; the 8 originals were restored from commit `13169de`.
  4. **Issue-date corrections.** The 3 implausible dates are repaired against source — see "Date anomalies".
  5. **Curriculum spotlight and coverage tables rebuilt from the data.** Both were hand-maintained. The spotlight ran on `split_curriculum_pd_v2.py`, which applied a computed PD percentage to a **hard-coded per-FY total** for three of the four swimlanes and printed JS arrays to paste into `index.html`; the coverage table was typed by hand. Now `build/curriculum.py` and `build/coverage.py` derive both, they travel in the dashboard payload, and the page renders from it — see "Curriculum swimlanes" below for what the numbers moved to and why.
  6. **Two dashboard header fixes.** The "Source: Troy SD BoardDocs" link pointed at `go.boarddocs.com/mi/troymi/` (Troy city) instead of `/mi/troysd/` (the school district) — the only wrong slug in the project. And the hand-written "FY26 partial (through April 2026)" caption is now derived by `write_dashboard` from the last transaction month carrying 100+ line items, so it tracks the data instead of going stale.
- **2026-06-02 pipeline consolidation + deliverable regeneration**: The build pipeline was consolidated into a single portable `rebuild.py` + `validate.py` under `build/` (machine-specific `C:\Dev` / `%TEMP%` paths removed; the two lost classification lookups re-derived from committed artifacts into `build/lookups/`). The workbook and `index.html` were then regenerated from the committed data via `rebuild.py --assemble-only`, resolving two inconsistencies in the prior (patchwork) artifacts: the dashboard data had lagged the workbook at 222,132 lines (now 224,267, matching), and the workbook's README/pivot/PD-summary sheets had been built by mixed script versions. Because the original per-row categorization was never persisted (the dashboard retained only the top-25 vendors per category), regeneration re-derives categories from the committed seed (`vendor_categories.json`) — a one-time **~0.56% category restatement** (~$6.9M of $1.227B, entirely long-tail vendors below the top-25 cutoff; grand total and per-FY totals unchanged). Categorization is now deterministic and reproducible from the committed seed.

## Date anomalies (3 lines) — corrected 2026-07-27

3 lines carried implausible issue dates. Re-pulling the source registers from
BoardDocs confirmed the bad dates are **printed that way in the PDFs** — a
defect in the district's Pentamation output, not an OCR or parse error, so a
re-parse would reintroduce them. They are now repaired in the pipeline by an
explicit, documented override in `build/fiscal_year.py` (`DATE_CORRECTIONS`):

| Check | Vendor | Source date | Corrected | Amount | Basis |
|---|---|---|---|---:|---|
| W22-042 | COMPASS GROUP USA | 2061-09-09 | 2021-09-09 | $163,953.74 (2 lines) | Sep 2021 register (approved 2021-11-16); day/month intact, year 61 → 21 |
| W22-120 | A D N ADMINISTRATOR | 2031-01-01 | 2022-01-01 | $15,982.12 | Jan 2022 register (approved 2022-03-15); description "DEC 21 CLAIMS", year 31 → 22 |

Both checks carry the `W22-` warrant prefix (FY22) and both corrections land in
FY22. Under the single issue-date FY these would otherwise have created bogus
FY62 / FY31 buckets; the FY range is now clean at FY11–FY26.

## Known data-quality note — duplicate lines across adjacent registers

14 line signatures (identical check number, vendor, budget unit, account, issue
date and amount) appear under two different source meetings, all in the
embedded-packet era: 2015-03/04, 2016-08/09, 2016-11 + 2017-01, and 2019-02/03.
Potential double-count is **$24,467.23 of $1.278B (0.0019%)**.

Left as-is deliberately: the embedded source packets are not tracked in git, so
this cannot be adjudicated against source, and removing rows without evidence
would silently alter historical totals. Re-check if the pre-2020 corpus is ever
restored (see "Source PDFs in repo").

## Parser provenance

- Standalone PDFs: `parser.py` (regex-based). Validated against original FY23-FY26 workbook exactly: 47,917 rows / $417,275,260.96. Independently reconciled 2026-07-27 against the `TOTAL REPORT` figure each PDF prints for itself: **47 of 48 standalone registers match to the cent**. The one exception is the 2023-12-12 meeting, which carried two registers (Sep + Oct 2023) while only the Sep PDF is tracked in git — the Oct rows are present and correct, its PDF simply is not in the repo.
- Embedded PDFs: `pre2020_extract.py` (same regex with em-dash normalization + bundle-date fix + pypdf fallback). No equivalent ground truth exists for these.

## Categorization

`categorize_v2.py` applies a vendor-lookup-first rule (built from FY23-FY26 vendor frequencies) with Michigan PSAM function-code fallback. New vendors that appear only in FY11-FY19 get categorized purely by function-code rules. Estimated category-level accuracy is ~83% (matches original payload to within 2% for 7 of 28 categories; remaining categories have 5-50% drift). Grand totals exact.

## Curriculum swimlanes (dashboard spotlight)

`build/curriculum.py` classifies each line into one of four swimlanes — K-5 ELA,
K-5 Math, 6-12 ELA, 6-12 Math — and splits it into curriculum/materials vs
professional development. Every figure the spotlight shows is derived from the
rows; nothing is written down.

Published totals moved when the hard-coded anchors were retired on 2026-07-27:

| Swimlane | Retired anchor | Derived | PD share |
|---|---:|---:|---:|
| K-5 ELA | $3.75M | $3.38M | 48% |
| K-5 Math | $3.46M | $3.11M | 43% |
| 6-12 ELA | (was already derived) | $1.50M | 5% |
| 6-12 Math | $1.69M | $1.31M | 6% |
| **Combined** | **$10.46M** | **$9.30M** | |

Three things changed the numbers, in order of size:

1. **A false positive the anchors were hiding.** The 6-12 Math filter matched
   `LARSON` in a description to catch Ron Larson's Big Ideas texts. *Larson* is
   also a Troy school building, so the rule swept in **$8.4M** of construction,
   utilities, paving, architecture and transport for Larson School — Barton
   Malow alone was $4.7M, most of it in bond fund 414. Because the published
   totals were anchored, none of this ever surfaced. The token now only counts
   when the vendor is an actual textbook publisher.
2. **A false negative.** Illustrative Math ships through Imagine Learning, and
   only the rows whose truncated description happened to read `ILLUSTRATIVE`
   were caught — $44K of $748K. The IM product lines (`IMAGINE IM`,
   `IM MATHEMATICS`, `IM ALGEBRA`) are now matched directly, while the same
   vendor's Edgenuity licences and Imagine Language & Literacy are correctly
   left out.
3. **No more double counting.** 60 rows matched both grade bands of one subject
   — nearly all function-code 221 (improvement of instruction), which is
   grade-neutral. Summing lanes counted them twice. `assign_lane()` now places
   every row in exactly one lane, resolving by function code first (112/113
   secondary, 111 elementary), then by wording ("GEOMETRY COHORT" is secondary
   PD, "GRADE K" is elementary), defaulting to elementary. This is why 6-12 ELA's
   PD share fell from 11% to 5%: the TCRWP "Units of Study" PD is elementary and
   moved to K-5 ELA.

The swimlane filters remain tuned heuristics over 19-character truncated vendor
names and descriptions — that is the analytical judgement in the module, and it
is worth re-reading when a new adoption lands. What is no longer true is that a
bad rule can hide behind a fixed total.

## Subject classification (Curriculum_PD sheet)

Vendor → subject mapping originally built from the FY23-FY26 Curriculum_PD sheet (87 vendors), expanded 2026-05-01 with 51 pre-2020 vendors identified by manual review of the Curriculum_PD "Not Directly Attributable" tail (now 138 vendors total). Falls back to keyword matching on truncated descriptions for unmatched vendors. Confidence "high" = exact vendor match; "med" = keyword match; "low" = no signal.

After lookup expansion, only 30 pre-2020 PD lines / $8,703 remain unclassified (down from 256 lines / $326,374 — a 97% improvement). The remaining tail consists of generic conference registrations, single-line presenter honorariums, and Aplia/Saga course platforms with no subject signal in the truncated description.

## Source PDFs in repo

- `source_data/BoardDocs_PDFs/` — 71 standalone "Check register by fund" PDFs (~75 MB); 48 tracked in git (May 2022 → May 2026)
- `source_data/BoardDocs_PDFs_pre2020/` — 83 board-meeting packet PDFs containing embedded registers (~640 MB). Note: a few additional productive PDFs from the re-extraction (with widened filter) remain at the original `C:\Dev\TroySD\` path; they would need to be re-copied if a fully-self-contained build is desired.
