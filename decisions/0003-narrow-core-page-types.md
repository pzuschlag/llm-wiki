---
title: "ADR 0003: Page types across instances — a narrow shared core, no mandatory shared fields"
status: accepted
date: 2026-10-05
---

# ADR 0003: Page types across instances — a narrow shared core, no mandatory shared fields

## Context
Open question from CONCEPT.md §9: are there page types that are the same across every instance (e.g. `person`), and shared fields for them? Shared types would help: lint and future tooling (e.g. tier-3 structured facts) could rely on a known shape, and migrations could safely assume it across instances. But instances differ a lot in what a type actually means — Work Wiki's `person` is a colleague (role, team), a personal wiki's `person` is family or friends (relationship, birthday). A single mandatory field set per type would force irrelevant fields into some instances, conflicting with principle 7 (content and method are separate; every wiki has its own rules).

## Decision
Keep the shared core narrow: only the type *name* and its default review interval are standardized, via the default `page_types`/`review_days` shipped in `template/wiki.config.yaml.jinja`. No type-specific *required* fields are mandated at the concept level beyond the universal frontmatter already enforced by `lint_wiki.py` (`title`, `type`, `last_updated`, `status`, `review_by`). Instances remain free to use additional fields per type (e.g. `role` on `person` pages) — that's instance-owned content, not something the concept checks or migrates.

This mostly formalizes the status quo rather than changing behavior: `wiki.config.yaml` is already instance-owned (`_skip_if_exists`), so an instance could already deviate from the defaults. This ADR records that the deviation is intended, not an oversight to "fix" later with a rigid shared schema.

## Alternatives
| Option | Why not |
|---|---|
| Rigid shared schema per type (e.g. `person` always has `role`, `email`, `aliases`) | Conflicts with principle 7; forces irrelevant or empty fields where a type means something different per instance |
| No shared type system at all | Loses the tooling benefit that already exists today — a known default `page_types`/`review_days` list, and the ability to write cross-instance migrations assuming a baseline shape |
| **Narrow core** (chosen) | Minimal shared surface (name + review interval), keeps today's tooling benefits, instances stay free to extend locally |

## Consequences
- No change to `lint_wiki.py` or the schema — `type` stays a free string checked only against the instance's own `wiki.config.yaml` → `page_types`.
- Resolves the last open question in CONCEPT.md §9.
