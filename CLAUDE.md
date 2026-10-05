# llm-wiki — concept repo

This repo contains the LLM-wiki concept (`CONCEPT.md`) and the Copier template for wiki instances (`template/`). It contains **no wiki content** — examples are always synthetic, never copied from an instance (instances hold confidential data; this repo is public).

## Working rules
- Concept and template change together: every rule in `CONCEPT.md` must show up in `template/.llm-wiki/CORE.md`, in the lint, or in a skill — and vice versa.
- Every change → an entry in `CHANGELOG.md` with a SemVer classification (MAJOR = instances need a migration).
- Data migrations as an idempotent script under `template/.llm-wiki/migrations/NNNN_<name>.py` + an entry in `copier.yml` → `_migrations`.
- Fundamental decisions as an ADR under `decisions/`.
- Observations from instances or external sources → `research/`.
- Before every merge: `bash tests/test_template.sh`.
- Template scripts run on Python ≥ 3.9 with no third-party packages (macOS system Python).
- Changes via branch + pull request; a release is a git tag `vX.Y.Z` after the merge.
- Language: English, including `CHANGELOG.md`/`decisions/`/`research/` (translated 2026-10-05; was German, see git history for the originals).
