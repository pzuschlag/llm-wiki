---
name: wiki-upgrade
description: Diese Wiki-Instanz auf eine neue Version des LLM-Wiki-Konzepts (pzuschlag/llm-wiki) heben — per copier update auf einem Branch, mit Migrationen, Lint und Pull Request. Verwenden, wenn eine neue Konzept-Version erschienen ist oder auf Nachfrage.
---
<!-- Verwaltet von pzuschlag/llm-wiki — in Instanzen nicht ändern. -->

# Upgrade auf neue Konzept-Version

1. **Stand prüfen**: `git status` muss sauber sein. Installierte Version: `_commit` in `.copier-answers.yml`. Verfügbare Versionen: `git ls-remote --tags https://github.com/pzuschlag/llm-wiki`.
2. **Changelog lesen**: `CHANGELOG.md` im Konzept-Repo zwischen installierter und Zielversion; MAJOR-Versionen (Migrationen, manuelle Schritte) dem Menschen vorab zusammenfassen.
3. **Branch**: `git checkout -b llm-wiki-upgrade-<version>`.
4. **Update**: `copier update --skip-answered --vcs-ref <tag>` (Copier ≥ 9, `pipx install copier`). Copier führt einen 3-Wege-Merge aus und startet registrierte Migrationen.
5. **Konflikte**: Konfliktmarker in verwalteten Dateien (`.llm-wiki/`, `.claude/skills/wiki-*`) zugunsten der neuen Version lösen — dort gibt es keine legitimen lokalen Änderungen. Instanz-Dateien (`CLAUDE.md`, `wiki.config.yaml`, `wiki/`) überschreibt Copier nicht; neue Pflicht-Einträge aus dem Changelog dort von Hand ergänzen.
6. **Prüfen**: `python3 .llm-wiki/lint_wiki.py` ohne Errors; Hook aktiv (`git config core.hooksPath` → `.llm-wiki/hooks`).
7. **Log**: `## [YYYY-MM-DD] upgrade | llm-wiki <alt> → <neu>` mit den Änderungen aus dem Changelog.
8. **Commit + Pull Request** zum Review — nie direkt auf main.
