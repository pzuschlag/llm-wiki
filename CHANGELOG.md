# Changelog

Versioned per SemVer:
- **MAJOR**: instances need a data migration or manual steps
- **MINOR**: new rule, new check, new skill — no data migration
- **PATCH**: fixes, wording

## [0.4.3] — 2026-10-05

- Page types stay a narrow shared core — only the type name and its default review interval, no mandatory per-type fields across instances ([ADR 0003](decisions/0003-narrow-core-page-types.md)). Resolves the last §9 question. Renamed `decisions/0001`/`0002` filenames to English for consistency (content was already translated; links updated).

## [0.4.2] — 2026-10-05

- §6 adds a quarterly practice: re-read the gist thread, evaluate new comments against the current concept, and actively decide whether to act — feeds into the normal "idea/problem → issue → ADR" flow. Resolves the second §9 question (how gist findings regularly flow into `research/`).

## [0.4.1] — 2026-10-05

- Removed `product`/`source-summary` from the default `page_types` in `template/wiki.config.yaml.jinja` — leftover from the work-wiki instance that was never part of the documented core set (`area, person, project, decision, concept, draft, meta, template`); instances can still add their own domain-specific types. Genericized a `lint_wiki.py` comment that used real industry jargon as an example.

## [0.4.0] — 2026-10-05

- **Breaking**: the `status` frontmatter value is now English — `aktuell` → `current`, `entwurf` → `draft`, `veraltet` → `outdated` (`superseded` unchanged). Migration: `template/.llm-wiki/migrations/0001_status_en.py`, idempotent, registered in `copier.yml` → `_migrations`
- Concept and template fully translated to English (prose, comments, docstrings, CLI output); historical `CHANGELOG.md`/`decisions/`/`research/` entries translated too — originals are in git history. No other functional change.

## [0.3.0] — 2026-10-05

- Consultation rate: a PostToolUse hook (`template/.llm-wiki/log_wiki_access.py`, registered in `template/.claude/settings.json`) counts Read/Grep access to `wiki/**` during a task (local, `.llm-wiki/.stats.jsonl`, gitignored); evaluated via `lint_wiki.py --stats`, wired into the `wiki-lint` skill (resolves issue #3)

## [0.2.0] — 2026-10-05

- Data protection: instances with sensitive content encrypt fully or partially with `git-crypt` instead of relying on visibility settings; cloud access is the instance's own call in its `CLAUDE.md` ([ADR 0002](decisions/0002-sensitive-data-git-crypt.md))

## [0.1.0] — 2026-10-02

First version, derived from running a work wiki and from analyzing the comment thread on Karpathy's gist.

- Concept: principles, instance architecture, page schema, workflows, distribution via Copier, scaling tiers, compliance
- Page schema with `status`, `review_by`, `superseded_by`, and fixed source prefixes
- `lint_wiki.py`: errors/warnings, configurable via `wiki.config.yaml`, `--stale`, `--strict`
- Pre-commit hook (only for staged `wiki/*.md`)
- Skills: `wiki-ingest` (with contradiction check), `wiki-query`, `wiki-lint`, `wiki-upgrade`
