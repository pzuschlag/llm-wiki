---
title: "LLM Wiki — Concept"
version: 0.4.2
status: draft
last_updated: 2026-10-05
---

# LLM Wiki — Concept

An LLM wiki is a persistent, LLM-maintained Markdown wiki that compiles knowledge from raw sources instead of re-deriving it on every question. This document describes one concrete variant of the pattern, in daily use since 04/2026. It is the central source for every wiki that applies the concept, and is independent of their content.

Based on: [Karpathy's LLM-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (04/2026), extended with findings from the comment thread and from running a work wiki (~100 pages, since 04/2026).

**Status**: v0.x — experimental. The concept runs in a work wiki (reference for v0.1); a personal wiki is planned. Instances are their own, private repos and not part of this repo.

---

## 1. Principles

1. **Compile, don't search.** New sources are worked in (entity pages updated, cross-links set), not just indexed.
2. **Every statement is traceable.** Pages name their sources; decisions, numbers, dates, and commitments carry a source per statement.
3. **Knowledge has a lifecycle.** Pages are `current`, `draft`, `outdated`, or `superseded`, and carry a review date. Changed facts are moved to history, never overwritten.
4. **Contradictions at write time, not read time.** Ingest checks new statements against existing ones before changing anything.
5. **Enforce, don't hope.** Whatever is mechanically checkable (schema, source format, links, index) is checked by a script and blocks commits. Model behavior is not treated as a control.
6. **A human at the switches.** Ingest starts with a discussion of the key takeaways; the human decides real contradictions; structural changes go through a pull request.
7. **Content and method are separate.** The concept contains no content. Every wiki is its own repo with its own access and compliance rules. Wikis don't link to each other.

## 2. Architecture of an instance

| Layer | Location | Who writes | Rule |
|---|---|---|---|
| Raw sources | `raw/` | sync scripts, human | immutable; sensitive data gitignored |
| Wiki | `wiki/` | LLM | schema, see §3 |
| Schema & workflows | `CLAUDE.md` + `.llm-wiki/` | concept (managed) + instance | see §6 |
| Checking | `.llm-wiki/lint_wiki.py`, pre-commit hook | concept (managed) | errors block |
| Operations | `.claude/skills/`, `scripts/` | instance | domain-specific syncs |

Required pages: `wiki/index.md` (catalog, "Total pages"), `wiki/log.md` (append-only operations log), `wiki/overview.md` (synthesis).

## 3. Page schema

```yaml
---
title: "Page title"
type: <from wiki.config.yaml>          # core: area, person, project, decision, concept, meta, draft, template
tags: [tag1, tag2]
sources: ["confluence:123", "raw/…"]   # fixed prefixes, always quoted
last_updated: YYYY-MM-DD
status: current | draft | outdated | superseded
review_by: YYYY-MM-DD                  # last_updated + interval per type
superseded_by: "[[successor]]"         # required when superseded
---
```

- **Source formats**: core prefixes `raw/`, `wiki/`, `url:`, `meeting:`, `note:`. Domain prefixes (e.g. `confluence:`, `jira:`, `notion:`) are defined by the instance in `wiki.config.yaml`. `wiki/…` alone is not a source; `note:` is a fallback (lint warns).
- **Review intervals** per type in `wiki.config.yaml` (default: person 60d, project/area 45, concept/decision 180).
- **Page structure**: 1-sentence summary → `##` sections → `[[Links]]` → optional `## History` → optional `## Sources`.
- **History**: `- YYYY-MM-DD: <old> → <new> (<old source> → <new source>)`.
- **Contradiction**: `> [!warning] Contradiction (YYYY-MM-DD): <A> says X, <B> says Y`.

## 4. Workflows

**Ingest**: source lands in `raw/` → key takeaways with the human → summary page → *contradiction check per affected page* (changed → history; disagreement → callout + ask; superseded → superseded/outdated) → entity pages incl. `sources`/`last_updated`/`review_by` → index → log (incl. "Changed/superseded") → overview.

**Query**: index → pages → answer with page references, respecting `status`/`review_by` → durably valuable answers are saved as a page → log.

**Lint**: `lint_wiki.py` (mechanical) + a content review by the LLM (contradictions, missing pages, missing cross-links).

**Session start**: instance syncs (skills) → staleness report (`lint_wiki.py --stale`) → offer to refresh.

**Consultation rules** (binding in every instance): read the page first before making statements about entities; a contradiction with a source → run the ingest check instead of overwriting; an outdated page → say so in the answer. Whether this actually happens is measured by a PostToolUse hook (`.llm-wiki/log_wiki_access.py` → `.llm-wiki/.stats.jsonl`, local); evaluated via `lint_wiki.py --stats` in the `wiki-lint` skill.

## 5. Checking (lint)

| Level | Checks | Effect |
|---|---|---|
| Error | frontmatter/required fields, `status` value, superseded without a successor, source format, broken links, orphans, page missing from the index, "Total pages" wrong | blocks the commit (pre-commit hook, only for `wiki/*.md`) |
| Warning | no sources, only wiki sources, `note:` sources, `review_by` passed, ambiguous filenames | report, session start |

Link resolution: path, `title`, and `aliases` before filename.

## 6. Distribution: from the concept to instances

**Goal**: concept changes reach every instance, but each instance adopts them deliberately (pull, not push), with review and, where needed, a data migration.

**Central repo `llm-wiki`** (decision: [ADR 0001](decisions/0001-verteilung-per-copier.md)):

```
llm-wiki/
├── CONCEPT.md            # this document
├── CHANGELOG.md          # SemVer: MAJOR = migration needed, MINOR = new rule/check, PATCH = fix
├── decisions/            # ADRs on the concept
├── research/             # notes from the gist thread, other implementations
├── template/             # Copier template for an instance
│   ├── .llm-wiki/        # MANAGED: CORE.md (rules), lint_wiki.py, log_wiki_access.py,
│   │                     #          hooks/pre-commit, migrations/ (e.g. 0001_status_en.py)
│   ├── .claude/skills/wiki-*/   # MANAGED: ingest, query, lint, upgrade
│   ├── .claude/settings.json    # MANAGED: registers the consultation-rate hook (PostToolUse)
│   ├── CLAUDE.md.jinja   # created once, then instance-owned; imports @.llm-wiki/CORE.md
│   ├── wiki.config.yaml.jinja   # instance parameters: types, intervals, source prefixes, language
│   └── wiki/index.md, log.md, overview.md
└── copier.yml            # questions, _migrations per version
```

**Ownership** is the central rule: files under `.llm-wiki/`, `.claude/skills/wiki-*`, and `.claude/settings.json` belong to the concept and are never changed by hand in instances. `CLAUDE.md`, `wiki/`, `raw/`, instance skills, and `wiki.config.yaml` belong to the instance. The instance `CLAUDE.md` pulls in the core rules via `@.llm-wiki/CORE.md` and only adds domain-specific things.

**Flow of a concept change**:
1. An idea/problem comes up (often in an instance) → an issue in the `llm-wiki` repo, possibly an ADR.
2. Implementation in the template + a migration script if data is affected (like `migrations/0001_status_en.py`) → release tag `vX.Y.Z` + changelog.
3. Per instance: skill `wiki-upgrade` → `copier update` on a branch → migrations run → `lint_wiki.py` → pull request → merge. The installed version lives in `.copier-answers.yml` (`_commit`).

**New instance**: `copier copy gh:pzuschlag/llm-wiki <folder>` → answer the questions → `git config core.hooksPath .llm-wiki/hooks`. Details in the [README](README.md).

**Why Copier instead of a plugin, submodule, or symlink**

| Option | Pro | Con |
|---|---|---|
| **Copier template** (recommended) | 3-way merge on updates, versions via git tags, `_migrations` per version, files live versioned in the instance (also works in cloud sessions and on other machines) | an extra tool (`pipx install copier`) |
| Claude Code plugin | skills/hooks are versioned, update via `/plugin` | provides no always-loaded rules (no CLAUDE.md), doesn't migrate data, isn't loaded in cloud sessions |
| Git submodule | simple, exactly versioned | rules aren't customizable, no migration mechanism, awkward updates |
| Symlink to a local folder | active everywhere instantly | only on one machine, no versions, needs external-import approval, every change takes effect unchecked in every wiki |

A plugin could complement this later (e.g. `/wiki:ingest` as a command), but it isn't the distribution mechanism.

## 7. Scaling

Navigating via `index.md` + full-text `grep` holds up as long as the index comfortably fits the context and a typical question needs only a few pages. Switch tiers based on **signals**, not page count alone.

| Tier | Typical size | Navigation | When to switch (signals) |
|---|---|---|---|
| **1 — Index** | up to ~200–300 pages | `index.md` → read pages, `grep` | — |
| **2 — Index + local search** | ~300–1,000 pages | per-area index (`areas/index.md` …) + local full-text search (SQLite FTS5 / BM25, e.g. qmd) as a tool/skill | index > ~10k tokens · queries regularly need > 8 page reads · the agent misses existing pages · duplicates appear |
| **3 — Hybrid + structured facts** | > 1,000 pages or many sources per day | BM25 + local embeddings, facts (entity, attribute, value, source, valid-from) in SQLite, Markdown pages rendered from them; contradiction check as a query instead of an LLM comparison | the ingest contradiction check becomes unreliable/expensive · lint runtime > 1 min · fact questions spanning many pages ("all Q4 deadlines") |

**Cross-cutting, independent of tier**:
- **Bound append-only files**: move `log.md` and meeting collections per quarter to `wiki/archive/YYYY-Qn/` once they exceed ~25k tokens.
- **Context layers**: core rules (`CORE.md`) always loaded and short (< 200 lines); operational workflows as skills (loaded on demand); page content only via index/search.
- **Local before cloud**: search index and embeddings run locally; no content to third-party services (compliance, see §8).

*Work-wiki reference (10/2026)*: ~100 pages, `index.md` ≈ 16 KB (~4–5k tokens), wiki total ≈ 1.2 MB, `log.md` ≈ 220 KB (~60k tokens). → Tier 1; `log.md` has already crossed the archiving threshold.

## 8. Data protection & compliance

- Every instance clarifies in its `CLAUDE.md`: who may see the repo? Which data stays local (`raw/` gitignored)? Which topics don't belong in the wiki at all?
- The concept repo never contains instance content; examples are synthetic.
- No third-party tools that send content to foreign servers or LLM providers; tools from the community are used as a source of ideas, not installed.
- Memory sync and auto-commits respect exclusion lists (`.memory-syncignore`, `.gitignore`); lint checks that nothing ignored is tracked.
- Instances with sensitive content (e.g. health, finances, relationships) encrypt their repo fully or partially with `git-crypt`, instead of relying on the remote's visibility setting alone; whether cloud sessions may access it is the instance's own call in its `CLAUDE.md` (decision: [ADR 0002](decisions/0002-sensible-daten-git-crypt.md)).

## 9. Open questions

- Are there page types that are the same across every instance (e.g. `person`), and shared fields for them?
- How do findings from the gist thread regularly flow into `research/` (e.g. a monthly review)?

## History
- 2026-10-05: v0.4.2 — consistency fixes: §6 tree lists `log_wiki_access.py`, `.claude/settings.json`, and the migrations folder; the migration example points to a script that exists in this repo; intro no longer calls the experimental concept "battle-tested".
- 2026-10-05: v0.4.1 — removed `product`/`source-summary` from the default `page_types` (leftover from the work-wiki instance, never part of the documented core set) and genericized a lint comment that used real industry jargon as an example.
- 2026-10-05: v0.4.0 — `status` frontmatter values translated to English (`current`/`draft`/`outdated`, migration 0001); concept and template fully translated to English.
- 2026-10-05: v0.3.0 — §4 extended with consultation-rate measurement (PostToolUse hook `log_wiki_access.py`, evaluated in `wiki-lint`); resolves issue #3.
- 2026-10-05: v0.2.0 — §8 extended with protection for sensitive content via `git-crypt` (ADR 0002); resolves the first question from §9.
- 2026-10-02: v0.1.0 — first draft, derived from a work wiki after analyzing the gist thread.
