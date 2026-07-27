# Running Prompt Log — Check Register Project

Total chronological history of user prompts for this project. Each entry is
timestamped `YYYY-MM-DD HH:MM:SS`. New prompts are appended at the bottom,
oldest at the top.

The full prompt body for each entry lives in
`Working Folder/Prompts/<timestamp>/prompt_<timestamp>.md`. This file is the
one-line index.

---

## Initial build (Claude.ai web interface, pre-version-control)

The original BoardDocs pull, PDF extraction, master workbook construction, and
`index.html` build were performed through the Claude.ai web interface before
this repo was set up. The exact prompts were **not captured** and are not
present in this folder.

If those conversations are later recovered (e.g., via a Claude.ai data export),
backfill them as timestamped folders under this directory using the timestamp
of the original message, and add a one-liner here for each.

See [`../../PROMPTS.md`](../../PROMPTS.md) for the structured-prompt scaffold
covering the major build steps.

---

## Post-version-control prompts

> Append new entries below as the project evolves. Format:
>
> ```
> ## YYYY-MM-DD HH:MM:SS
>
> > One-line summary of what was asked.
> ```

Entries before 2026-07-27 were not logged at the time; the April and May 2026
backfills are reconstructable from `project_docs/INDEX.md` ("Bug/recovery
history") and the git history.

## 2026-07-27 14:53:00

> Review the repo and the published site, clone locally, then ingest the newly
> posted registers, run a data-accuracy pass, and move to a single Jul 1 – Jun 30
> fiscal-year attribution.

[`2026-07-27_14-53-00/`](2026-07-27_14-53-00/prompt_2026-07-27_14-53-00.md) —
Mar/Apr/May 2026 registers ingested (227,066 lines / $1,277,793,488.14); dual FY
columns collapsed to one keyed on issue date; parser bug dropping 16-digit budget
units, a dashboard regex overwriting hand-written FY spans, three bad source
dates, and a wrong BoardDocs link all fixed.
