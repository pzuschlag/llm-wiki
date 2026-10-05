# llm-wiki

Ein Konzept für LLM-gepflegte Wikis, aufbauend auf [Karpathys LLM-Wiki-Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), plus eine Vorlage, um es in einzelnen Wikis anzuwenden und aktuell zu halten.

> **Status: v0.x, experimentell.** Ideen und Erfahrungsberichte gern als Issue.

- **[CONCEPT.md](CONCEPT.md)** — das Konzept: Prinzipien, Schema, Workflows, Verteilung, Skalierung
- **[CHANGELOG.md](CHANGELOG.md)** — Versionen des Konzepts
- **[decisions/](decisions/)** — Entscheidungen zum Konzept (ADRs)
- **[research/](research/)** — Quellen und Beobachtungen, aus denen das Konzept lernt
- **[template/](template/)** — [Copier](https://copier.readthedocs.io/)-Vorlage einer Wiki-Instanz

Dieses Repo enthält keine Wiki-Inhalte. Jede Instanz ist ein eigenes Repo.

## Neue Wiki-Instanz anlegen

```bash
pipx install copier            # einmalig
copier copy gh:pzuschlag/llm-wiki ~/repos/mein-wiki
cd ~/repos/mein-wiki
git init && git config core.hooksPath .llm-wiki/hooks
git add -A && git commit -m "wiki: init aus llm-wiki"
```

Copier fragt Name, Zweck, Sprache und domänenspezifische Quellen-Präfixe ab und schreibt die Antworten nach `.copier-answers.yml`.

## Instanz auf neue Konzept-Version heben

In der Instanz den Skill **`wiki-upgrade`** ausführen, oder von Hand:

```bash
git checkout -b llm-wiki-upgrade
copier update --skip-answered     # 3-Wege-Merge + Migrationen der übersprungenen Versionen
python3 .llm-wiki/lint_wiki.py
# Konflikte (Konfliktmarker) lösen, committen, Pull Request
```

## Was gehört wem

| Verwaltet vom Konzept (in Instanzen nicht von Hand ändern) | Gehört der Instanz |
|---|---|
| `.llm-wiki/` (CORE.md, lint_wiki.py, log_wiki_access.py, hooks/, migrations/) | `CLAUDE.md`, `wiki.config.yaml` |
| `.claude/skills/wiki-*`, `.claude/settings.json` | `wiki/`, `raw/`, `scripts/`, eigene Skills |

Verbesserungsideen aus einer Instanz → Issue in diesem Repo, nicht lokal in `.llm-wiki/` ändern.

## Neue Konzept-Version veröffentlichen

1. Änderung im Template (+ Migrationsskript unter `template/.llm-wiki/migrations/` und Eintrag in `copier.yml` → `_migrations`, falls Daten betroffen) und in `CONCEPT.md`
2. `CHANGELOG.md` ergänzen, Version in `template/.llm-wiki/CORE.md` und `CONCEPT.md` anheben
3. `tests/test_template.sh` ausführen
4. Merge, dann Tag `vX.Y.Z` — Copier nutzt Git-Tags als Versionen

## Lizenz

- Vorlage, Skripte und Tests (`template/`, `tests/`, `copier.yml`): [MIT](LICENSE)
- Konzept und Dokumentation (`CONCEPT.md`, `decisions/`, `research/`, `CHANGELOG.md`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de) — Weiterverwendung mit Namensnennung
