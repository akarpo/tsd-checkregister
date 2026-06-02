# Build Prompts

This project's deliverables (`index.html` and the master workbook — originally
`Troy_SD_Check_Register_FY23-FY26.xlsx`, since extended and renamed
`Troy_SD_Check_Register_FY11-FY26.xlsx`) were built through the Claude.ai web
interface during the initial pull from BoardDocs. The original prompts were
**not captured at the time** and are not preserved in this repository.

> **Note on figures below:** Sections 1-4 describe the *original* FY23-FY26 build
> (≈47,918 rows, a 7-sheet workbook, ~45 monthly PDFs). The project has since been
> extended to FY11-FY26 — **224,267 line items** across an **8-sheet** workbook (the
> `By Issue-Date FY x Fund` sheet was added during the FY11-FY22 backfill). See the
> root [`README.md`](README.md) for current totals.

This file is a scaffold for two purposes:

1. **Drop in historical prompts** — if the original Claude.ai conversations
   are recovered (e.g., via a Claude.ai data export), the relevant prompts
   should be pasted into the sections below and into
   `Working Folder/Prompts/<timestamp>/` for archival.
2. **Capture future prompts going forward** — any subsequent revision,
   refresh, or extension of the dashboard or workbook should be done through
   Claude Code (or a comparable agent), with the prompt logged here so the
   project remains reproducible end-to-end.

Each prompt below should follow a consistent pattern (modeled on the sibling
`mi-nwea-standards-matrix` repo):

1. **Background** — what's already known.
2. **What to research / build** — specific questions and source pointers.
3. **What to return** — format expectations (Markdown, tables, citations).
4. **Caveats** — flag uncertainty rather than invent.

## How to re-run

In Claude Code:

```bash
claude
> [paste the prompt below into a new conversation]
```

Or in any LLM tool with web access. Prompts are intentionally self-contained —
each one briefs the agent like a smart colleague who hasn't seen the prior
conversation.

## How to log a new prompt

Each major prompt should also be archived under
`Working Folder/Prompts/<YYYY-MM-DD_HH-MM-SS>/prompt_<YYYY-MM-DD_HH-MM-SS>.md`
and added to `Working Folder/Prompts/running.md` as a chronological one-liner.
See `Working Folder/Prompts/TEMPLATE/` for the file shape.

---

## 1. BoardDocs PDF discovery and download

> **TODO: paste original prompt here.**
>
> Should cover: enumerating Treasurer's Report agenda items on
> https://go.boarddocs.com/mi/troysd/Board.nsf/Public, locating the
> check-register PDF attached to each, and downloading 45 monthly PDFs
> (FY22 tail through Feb 2026) named with their `YYYY-MM-DD` meeting date
> prefix.

```
TODO: prompt body
```

---

## 2. Check-register PDF → tabular extraction

> **TODO: paste original prompt here.**
>
> Should cover: parsing each monthly PDF into rows of (date, vendor, fund,
> budget unit, amount, …), reconciling formatting differences across
> fiscal years, and producing the master tidy table that becomes the
> "All Lines" sheet (47,918 rows).

```
TODO: prompt body
```

---

## 3. Master workbook construction

> **TODO: paste original prompt here.**
>
> Should cover: building the 7-sheet xlsx (`README`, `All Lines`,
> `By Year × Fund`, `By Budget Unit`, `PD_Yearly_Summary`, `Curriculum_PD`,
> `PD by Subject`), with the cross-sheet aggregations and PD-specific
> categorizations that surface in the dashboard.

```
TODO: prompt body
```

---

## 4. Dashboard (`index.html`) construction

> **TODO: paste original prompt here.**
>
> Should cover: building the static, single-file dashboard with all data
> inlined, the slicer/filter UI, the Chart.js visualizations, and the
> footer link to the GitHub repo. No build step — open in any browser.

```
TODO: prompt body
```

---

## 5. Subsequent corrections / extensions

> Capture any post-initial-build prompts here as separate sub-sections,
> with the date and a short description of what was changed and why.
> Mirror the chronological log in `Working Folder/Prompts/running.md`.
