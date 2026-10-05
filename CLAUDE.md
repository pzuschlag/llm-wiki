# llm-wiki — Konzept-Repo

Dieses Repo enthält das LLM-Wiki-Konzept (`CONCEPT.md`) und die Copier-Vorlage für Wiki-Instanzen (`template/`). Es enthält **keine Wiki-Inhalte** — Beispiele sind immer synthetisch, nie aus einer Instanz kopiert (Instanzen enthalten vertrauliche Daten; dieses Repo ist öffentlich).

## Arbeitsregeln
- Konzept und Template ändern sich gemeinsam: Jede Regel in `CONCEPT.md` muss sich in `template/.llm-wiki/CORE.md`, im Lint oder in einem Skill wiederfinden — und umgekehrt.
- Jede Änderung → Eintrag in `CHANGELOG.md` mit SemVer-Einordnung (MAJOR = Instanzen brauchen Migration).
- Datenmigrationen als idempotentes Skript unter `template/.llm-wiki/migrations/NNNN_<name>.py` + Eintrag in `copier.yml` → `_migrations`.
- Grundsatzentscheidungen als ADR unter `decisions/`.
- Beobachtungen aus Instanzen oder externen Quellen → `research/`.
- Vor jedem Merge: `bash tests/test_template.sh`.
- Skripte im Template laufen mit Python ≥ 3.9 ohne Fremdpakete (macOS-System-Python).
- Änderungen per Branch + Pull Request; Release = Git-Tag `vX.Y.Z` nach dem Merge.
- Sprache: Deutsch; Code, IDs und Tool-Namen Englisch.
