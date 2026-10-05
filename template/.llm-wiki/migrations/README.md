# Migrationen

Datenmigrationen zwischen Konzept-Versionen. Verwaltet von `pzuschlag/llm-wiki`.

- Ein Skript pro Änderung: `NNNN_<kurzname>.py`, **idempotent** (zweiter Lauf ändert nichts), Python ≥ 3.9 ohne Fremdpakete, `--dry-run` unterstützen.
- Registriert in `copier.yml` → `_migrations` des Konzept-Repos mit der Version, ab der es gilt. `copier update` führt es aus, wenn eine Instanz diese Version überspringt.
- Nach jeder Migration: `python3 .llm-wiki/lint_wiki.py` muss ohne Errors durchlaufen.

Muster: Parser für das Frontmatter, Normalisierung je Feld, Schreiben nur bei Änderung, Zähler „Changed: N pages“ als Ausgabe.
