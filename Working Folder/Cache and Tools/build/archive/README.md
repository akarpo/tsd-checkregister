# Archived build scripts

These are **superseded one-off scripts** kept for historical reference. They are
*not* part of the current pipeline and are not maintained — several still carry
the original hardcoded `C:\Dev\CheckRegister` / `C:\Dev\TroySD` / `%TEMP%` paths
and will not run as-is. Use the consolidated pipeline in the parent `build/`
directory (`rebuild.py`) instead.

They also predate the 2026-07-27 schema change, so any that touch fiscal year
assume the retired two-column scheme (a meeting-keyed `Fiscal Year` plus an
`Issue Date FY`) and would produce a workbook that no longer matches the current
one. Do not resurrect them without porting to `../fiscal_year.py`.

| Archived script | Superseded by | Why |
|---|---|---|
| `categorize.py` | `../categorize_v2.py` | v1 categorizer; v2 adds fund/function disambiguation for multi-category vendors. |
| `build_combined_wb.py` | `../rebuild_final.py` | Built a workbook under the old `…FY12-FY26.xlsx` name; `rebuild_final.build_workbook()` builds the current 7-sheet workbook. |
| `rebuild_with_issue_fy.py` | `../fiscal_year.py` + `../rebuild_after_bundlefix.py` | Added a second, issue-date-keyed FY column alongside the meeting-keyed one. Both are obsolete: since 2026-07-27 there is a single `Fiscal Year`, derived from the issue date in `fiscal_year.py` and applied during the merge stage. |
| `rebuild_workbook.py` | `../rebuild_final.py` | Post-2020-only workbook builder (read `all_lines.pkl`); replaced by the full FY11-FY26 builder. |
| `rebuild_dashboard.py` | `../rebuild_dashboard_full.py` | Post-2020-only dashboard payload (read `all_lines.pkl`); replaced by the full FY11-FY26 dashboard builder. |
| `split_curriculum_pd.py` | `../curriculum.py` | v1 of the curriculum/PD spotlight split. |
| `split_curriculum_pd_v2.py` | `../curriculum.py` | Semi-manual generator: it applied a computed PD percentage to a **hard-coded per-FY total** for three of the four swimlanes, then printed JS arrays to paste into `index.html` by hand. The anchors came from the original FY23-FY26 build and were never refreshed, so they did not move when registers were ingested — and they masked a filter bug that booked $8.4M of Larson *School* construction as Larson *textbook* spend. `curriculum.py` derives every figure from the rows and feeds the dashboard payload directly. |
| `expand_subject_lookup.py` | `../build_lookups.py` | Its hand-identified vendor→subject `EXPANDED` table is now embedded in `build_lookups.py`, which emits the committed `lookups/vendor_subject.json`. |
| `tcrwp_post2018_search.py` | — | One-off ad-hoc search utility (TCRWP vendor lines); never part of the build. |

See `../../project_docs/INDEX.md` for full provenance and the repo `README.md`
"Reproducibility" section for the current pipeline.
