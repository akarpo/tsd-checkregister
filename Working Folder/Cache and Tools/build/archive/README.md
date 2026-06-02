# Archived build scripts

These are **superseded one-off scripts** kept for historical reference. They are
*not* part of the current pipeline and are not maintained — several still carry
the original hardcoded `C:\Dev\CheckRegister` / `C:\Dev\TroySD` / `%TEMP%` paths
and will not run as-is. Use the consolidated pipeline in the parent `build/`
directory (`rebuild.py`) instead.

| Archived script | Superseded by | Why |
|---|---|---|
| `categorize.py` | `../categorize_v2.py` | v1 categorizer; v2 adds fund/function disambiguation for multi-category vendors. |
| `build_combined_wb.py` | `../rebuild_final.py` | Built a 7-sheet workbook and wrote the old `…FY12-FY26.xlsx` name; `rebuild_final.build_workbook()` builds the current 8-sheet workbook (adds `By Issue-Date FY x Fund`). |
| `rebuild_with_issue_fy.py` | `../rebuild_after_bundlefix.py` + `../rebuild_final.py` | Intermediate step that added the Issue-Date-FY column and re-classified; that logic now lives in the merge stage, and the workbook build in `rebuild_final.py`. |
| `rebuild_workbook.py` | `../rebuild_final.py` | Post-2020-only workbook builder (read `all_lines.pkl`); replaced by the full FY11-FY26 builder. |
| `rebuild_dashboard.py` | `../rebuild_dashboard_full.py` | Post-2020-only dashboard payload (read `all_lines.pkl`); replaced by the full FY11-FY26 dashboard builder. |
| `split_curriculum_pd.py` | `../split_curriculum_pd_v2.py` | v1 of the curriculum/PD spotlight split; v2 is the kept (semi-manual) generator. |
| `expand_subject_lookup.py` | `../build_lookups.py` | Its hand-identified vendor→subject `EXPANDED` table is now embedded in `build_lookups.py`, which emits the committed `lookups/vendor_subject.json`. |
| `tcrwp_post2018_search.py` | — | One-off ad-hoc search utility (TCRWP vendor lines); never part of the build. |

See `../../project_docs/INDEX.md` for full provenance and the repo `README.md`
"Reproducibility" section for the current pipeline.
