---
name: wiki-ingest
description: Incorporate a new source (document, meeting note, export) into the LLM wiki — including a contradiction check against existing pages. Use when a file lands in raw/ or new information should go into the wiki.
---
<!-- Managed by pzuschlag/llm-wiki — do not change in instances. -->

# Ingest

1. **Review the source**: the raw document lives in `raw/` (or a sync subfolder). Read only, never modify.
2. **Clarify key takeaways with the human**: propose 3–7 points, wait for confirmation. For automatic syncs, a short summary with y/n is enough.
3. **Write a summary page** (matching `type`, frontmatter per `.llm-wiki/CORE.md`), if the source warrants its own page.
4. **Contradiction check** — for every affected entity page, *before* changing it:
   - Read the page; compare new statements against existing ones: dates, ownership, numbers, decisions, status.
   - **Fact has changed** (newer source, clear successor): add the new statement, move the old one to `## History` — `- YYYY-MM-DD: <old> → <new> (<old source> → <new source>)`.
   - **Sources disagree** (unclear which holds): `> [!warning] Contradiction (YYYY-MM-DD): <source A> says X, <source B> says Y` at that spot; ask the human; overwrite nothing.
   - **Whole page superseded**: `status: superseded` + `superseded_by`, or `status: outdated` (no successor).
5. **Update entity pages**: content, cross-links `[[…]]`, add to `sources` (prefix formats), `last_updated` = today, `review_by` = today + `review_days[type]` from `wiki.config.yaml`. Decisions, numbers, dates, commitments get an inline source `(<source>, YYYY-MM-DD)`.
6. **Index**: register new pages, adjust "Total pages".
7. **Log**: `## [YYYY-MM-DD] ingest | <source title>` with bullet points; a `Changed/superseded: …` line for each change from step 4.
8. **Overview**: adjust if the overall picture changes.
9. `python3 .llm-wiki/lint_wiki.py` → fix errors → commit (instance rules in `CLAUDE.md`).
