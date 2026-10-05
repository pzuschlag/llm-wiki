---
name: wiki-upgrade
description: Lift this wiki instance to a new version of the LLM-wiki concept (pzuschlag/llm-wiki) — via copier update on a branch, with migrations, lint, and a pull request. Use when a new concept version has been released, or on request.
---
<!-- Managed by pzuschlag/llm-wiki — do not change in instances. -->

# Upgrade to a new concept version

1. **Check status**: `git status` must be clean. Installed version: `_commit` in `.copier-answers.yml`. Available versions: `git ls-remote --tags https://github.com/pzuschlag/llm-wiki`.
2. **Read the changelog**: `CHANGELOG.md` in the concept repo, between the installed and target version; summarize MAJOR versions (migrations, manual steps) for the human up front.
3. **Branch**: `git checkout -b llm-wiki-upgrade-<version>`.
4. **Update**: `copier update --skip-answered --vcs-ref <tag>` (Copier ≥ 9, `pipx install copier`). Copier runs a 3-way merge and triggers registered migrations.
5. **Conflicts**: resolve conflict markers in managed files (`.llm-wiki/`, `.claude/skills/wiki-*`) in favor of the new version — there are no legitimate local changes there. Copier doesn't overwrite instance files (`CLAUDE.md`, `wiki.config.yaml`, `wiki/`); add any new required entries from the changelog there by hand.
6. **Verify**: `python3 .llm-wiki/lint_wiki.py` with no errors; hook active (`git config core.hooksPath` → `.llm-wiki/hooks`).
7. **Log**: `## [YYYY-MM-DD] upgrade | llm-wiki <old> → <new>` with the changes from the changelog.
8. **Commit + pull request** for review — never directly on main.
