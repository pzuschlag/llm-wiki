# Migrations

Data migrations between concept versions. Managed by `pzuschlag/llm-wiki`.

- One script per change: `NNNN_<short-name>.py`, **idempotent** (a second run changes nothing), Python ≥ 3.9 with no third-party packages, support `--dry-run`.
- Registered in the concept repo's `copier.yml` → `_migrations`, with the version it applies from. `copier update` runs it when an instance skips past that version.
- After every migration: `python3 .llm-wiki/lint_wiki.py` must pass with no errors.

Pattern: parse the frontmatter, normalize per field, write only on change, print a "Changed: N pages" counter.
