<!-- Managed by pzuschlag/llm-wiki — do not change by hand in instances. Changes: file an issue in the llm-wiki repo, then the wiki-upgrade skill. -->
# LLM Wiki — Core Rules (Concept v0.4.0)

This repo is an LLM wiki: the LLM compiles raw sources from `raw/` into a persistent, cross-linked Markdown wiki under `wiki/`. The wiki is the primary knowledge source for this domain.

## When to check the wiki (binding)

- **Before any statement about people, projects, decisions, dates, or other entities in this domain**: read the wiki page first (`wiki/index.md` → page). Don't answer from memory.
- **A source contradicts the wiki**: apply the contradiction check from the `wiki-ingest` skill — never silently overwrite.
- **Page has `status: outdated`/`superseded` or a passed `review_by`**: say so in the answer and check the primary source.

## Page schema
```yaml
---
title: "Page title"
type: <from wiki.config.yaml → page_types>
tags: [tag1, tag2]
sources: ["raw/…", "<prefix>:<value>"]
last_updated: YYYY-MM-DD
status: current | draft | outdated | superseded
review_by: YYYY-MM-DD
superseded_by: "[[successor]]"   # required when superseded
---
```
- **`status`** says whether the page can be trusted (not project progress — use a separate field like `phase` for that): `current` verified · `draft` unconfirmed · `outdated` superseded with no successor · `superseded` replaced.
- **`review_by`**: reset on every substantive update: `last_updated` + the interval from `wiki.config.yaml` → `review_days`.
- **`sources`**, always quoted. Core prefixes: `raw/…`, `wiki/…`, `scripts/…` (paths), `url:https://…`, `meeting:YYYY-MM-DD`, `note:<free text>` (fallback, use sparingly). Instance prefixes in `wiki.config.yaml` → `source_prefixes`. `wiki/…` alone is not a source — at least one primary source is required.
- **Page structure**: 1-sentence summary right after the frontmatter → `##` sections → `[[Links]]` (Obsidian) → optional `## History` → optional `## Sources`.
- **Source per statement** for decisions, numbers, dates, and commitments: `(<source>, YYYY-MM-DD)` right after it. Otherwise the page-level source is enough.
- **History**: `- YYYY-MM-DD: <old> → <new> (<old source> → <new source>)` — changed facts are moved, never deleted.
- **Contradiction**: `> [!warning] Contradiction (YYYY-MM-DD): <source A> says X, <source B> says Y` — ask the human, overwrite nothing.

## Required pages
- `wiki/index.md` — catalog of all pages with "Total pages: N"
- `wiki/log.md` — append-only: `## [YYYY-MM-DD] <ingest|query|lint|upgrade> | <title>`
- `wiki/overview.md` — synthesis of the overall knowledge base

## Workflows (skills)
| Task | Skill |
|---|---|
| Incorporate a new source | `wiki-ingest` |
| Answer a question | `wiki-query` |
| Health check | `wiki-lint` |
| Adopt a new concept version | `wiki-upgrade` |

## Checking
`python3 .llm-wiki/lint_wiki.py` — errors block commits (pre-commit hook, enable with `git config core.hooksPath .llm-wiki/hooks`), warnings are a backlog. `--stale` = overdue pages only.

## Managed files
`.llm-wiki/`, `.claude/skills/wiki-*`, and `.claude/settings.json` belong to the concept repo `pzuschlag/llm-wiki` and are not changed here. Improvement ideas → file an issue there. Instance-specific things belong in `CLAUDE.md`, `wiki.config.yaml`, or your own skills.

`.claude/settings.json` registers a PostToolUse hook (`log_wiki_access.py`) that counts Read/Grep access to `wiki/**` (`.llm-wiki/.stats.jsonl`, local) — the consultation rate during a task, not just at session start. Evaluation: `python3 .llm-wiki/lint_wiki.py --stats`, wired into the `wiki-lint` skill.
