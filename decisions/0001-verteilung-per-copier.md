---
title: "ADR 0001: Konzept-Verteilung per Copier-Template"
status: angenommen
date: 2026-10-02
---

# ADR 0001: Konzept-Verteilung per Copier-Template

## Kontext
Das LLM-Wiki-Konzept soll in mehreren Wikis laufen (Arbeits-Wiki, Privat-Wiki, Projekte). Konzept-Änderungen sollen alle Instanzen erreichen, ohne dass Instanzen ihre domänenspezifischen Anpassungen verlieren. Konzept-Änderungen betreffen oft auch Daten (Beispiel: Frontmatter-Migration `status`/`review_by` im Arbeits-Wiki, ~100 Seiten).

## Entscheidung
Das Konzept-Repo enthält ein [Copier](https://copier.readthedocs.io/)-Template. Instanzen entstehen per `copier copy` und übernehmen neue Versionen per `copier update` auf einem Branch mit Pull Request. Versionen sind Git-Tags. Datenmigrationen laufen als Skripte unter `.llm-wiki/migrations/`.

Dateien unter `.llm-wiki/` und `.claude/skills/wiki-*` sind vom Konzept verwaltet; `CLAUDE.md`, `wiki.config.yaml`, `wiki/` und `raw/` gehören der Instanz (`_skip_if_exists`). Die Instanz-`CLAUDE.md` bindet die Kernregeln per `@.llm-wiki/CORE.md` ein.

## Alternativen
| Option | Warum nicht |
|---|---|
| Claude-Code-Plugin | liefert keine immer geladenen Regeln (CLAUDE.md), migriert keine Daten, wird in Cloud-Sessions nicht aus lokalen Einstellungen geladen ([Doku](https://code.claude.com/docs/en/plugins)). Später als Ergänzung möglich. |
| Git-Submodul | kein Migrationsmechanismus, Updates umständlich, keine Instanz-Anpassung im selben Pfad |
| Symlink auf lokalen Ordner | nur auf einem Rechner, unversioniert, Änderungen wirken ungeprüft in allen Wikis; externe `@`-Imports brauchen Freigabe |
| Manuelles Kopieren | driftet auseinander, keine Nachvollziehbarkeit |

## Konsequenzen
- Copier muss installiert sein (`pipx install copier`).
- Verwaltete Dateien werden in Instanzen nicht von Hand geändert; Verbesserungen laufen als Issue ins Konzept-Repo.
- Die Kopie in jeder Instanz macht Kernregeln auch in Cloud-Sessions und auf anderen Rechnern verfügbar.
