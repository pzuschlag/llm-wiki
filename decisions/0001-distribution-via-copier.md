---
title: "ADR 0001: Concept distribution via a Copier template"
status: accepted
date: 2026-10-02
---

# ADR 0001: Concept distribution via a Copier template

## Context
The LLM-wiki concept should run in multiple wikis (work wiki, personal wiki, projects). Concept changes should reach every instance without instances losing their domain-specific customizations. Concept changes often affect data too (example: the frontmatter migration for `status`/`review_by` in the work wiki, ~100 pages).

## Decision
The concept repo contains a [Copier](https://copier.readthedocs.io/) template. Instances are created via `copier copy` and adopt new versions via `copier update` on a branch with a pull request. Versions are git tags. Data migrations run as scripts under `.llm-wiki/migrations/`.

Files under `.llm-wiki/` and `.claude/skills/wiki-*` are managed by the concept; `CLAUDE.md`, `wiki.config.yaml`, `wiki/`, and `raw/` belong to the instance (`_skip_if_exists`). The instance `CLAUDE.md` pulls in the core rules via `@.llm-wiki/CORE.md`.

## Alternatives
| Option | Why not |
|---|---|
| Claude Code plugin | provides no always-loaded rules (CLAUDE.md), doesn't migrate data, isn't loaded from local settings in cloud sessions ([docs](https://code.claude.com/docs/en/plugins)). Could complement this later. |
| Git submodule | no migration mechanism, awkward updates, no instance customization in the same path |
| Symlink to a local folder | only works on one machine, unversioned, changes take effect everywhere unchecked; external `@` imports need approval |
| Manual copying | drifts apart, no traceability |

## Consequences
- Copier must be installed (`pipx install copier`).
- Managed files are never changed by hand in instances; improvements go to the concept repo as an issue.
- The copy in every instance makes the core rules available in cloud sessions and on other machines too.
