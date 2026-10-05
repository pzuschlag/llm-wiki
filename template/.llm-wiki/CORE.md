<!-- Verwaltet von pzuschlag/llm-wiki — in Instanzen NICHT von Hand ändern. Änderungen: Issue im llm-wiki-Repo, dann Skill wiki-upgrade. -->
# LLM-Wiki — Kernregeln (Konzept v0.3.0)

Dieses Repo ist ein LLM-Wiki: Das LLM kompiliert Rohquellen aus `raw/` in ein persistentes, vernetztes Markdown-Wiki unter `wiki/`. Das Wiki ist die primäre Wissensquelle dieser Domäne.

## Wann ins Wiki schauen (verbindlich)
- **Vor jeder Aussage zu Personen, Projekten, Entscheidungen, Terminen oder anderen Entities dieser Domäne**: zuerst die Wiki-Seite lesen (`wiki/index.md` → Seite). Nicht aus dem Gedächtnis antworten.
- **Eine Quelle widerspricht dem Wiki**: Widerspruchs-Check aus Skill `wiki-ingest` anwenden — nie stillschweigend überschreiben.
- **Seite hat `status: veraltet`/`superseded` oder überschrittenes `review_by`**: das in der Antwort sagen und die Primärquelle prüfen.

## Seitenschema
```yaml
---
title: "Seitentitel"
type: <aus wiki.config.yaml → page_types>
tags: [tag1, tag2]
sources: ["raw/…", "<präfix>:<wert>"]
last_updated: YYYY-MM-DD
status: aktuell | entwurf | veraltet | superseded
review_by: YYYY-MM-DD
superseded_by: "[[Nachfolger]]"   # Pflicht bei superseded
---
```
- **`status`** sagt, ob man der Seite trauen kann (nicht den Projektfortschritt — dafür ein eigenes Feld wie `phase`): `aktuell` geprüft · `entwurf` unbestätigt · `veraltet` überholt, kein Nachfolger · `superseded` ersetzt.
- **`review_by`** bei jedem inhaltlichen Update neu setzen: `last_updated` + Intervall aus `wiki.config.yaml` → `review_days`.
- **`sources`**, immer gequotet. Kern-Präfixe: `raw/…`, `wiki/…`, `scripts/…` (Pfade), `url:https://…`, `meeting:YYYY-MM-DD`, `note:<Freitext>` (Notlösung). Instanz-Präfixe in `wiki.config.yaml` → `source_prefixes`. `wiki/…` allein ist keine Quelle — mindestens eine Primärquelle.
- **Seitenaufbau**: 1-Satz-Summary nach dem Frontmatter → `##`-Sektionen → `[[Links]]` (Obsidian) → optional `## Historie` → optional `## Quellen`.
- **Quelle pro Aussage** bei Entscheidungen, Zahlen, Terminen und Zusagen: `(<quelle>, YYYY-MM-DD)` direkt dahinter. Sonst reicht die Seitenebene.
- **Historie**: `- YYYY-MM-DD: <alt> → <neu> (<quelle alt> → <quelle neu>)` — geänderte Fakten werden verschoben, nie gelöscht.
- **Widerspruch**: `> [!warning] Widerspruch (YYYY-MM-DD): <Quelle A> sagt X, <Quelle B> sagt Y` — Mensch fragen, nichts überschreiben.

## Pflichtseiten
- `wiki/index.md` — Katalog aller Seiten mit „Seiten gesamt: N"
- `wiki/log.md` — append-only: `## [YYYY-MM-DD] <ingest|query|lint|upgrade> | <Titel>`
- `wiki/overview.md` — Synthese des Gesamtwissens

## Workflows (Skills)
| Aufgabe | Skill |
|---|---|
| Neue Quelle einarbeiten | `wiki-ingest` |
| Frage beantworten | `wiki-query` |
| Gesundheitscheck | `wiki-lint` |
| Neue Konzept-Version übernehmen | `wiki-upgrade` |

## Prüfung
`python3 .llm-wiki/lint_wiki.py` — Errors blockieren Commits (Pre-Commit-Hook, aktivieren mit `git config core.hooksPath .llm-wiki/hooks`), Warnings sind Arbeitsvorrat. `--stale` = nur überfällige Seiten.

## Verwaltete Dateien
`.llm-wiki/`, `.claude/skills/wiki-*` und `.claude/settings.json` gehören dem Konzept-Repo `pzuschlag/llm-wiki` und werden hier nicht geändert. Verbesserungsideen → Issue dort. Instanz-Spezifisches gehört in `CLAUDE.md`, `wiki.config.yaml` oder eigene Skills.

`.claude/settings.json` registriert einen PostToolUse-Hook (`log_wiki_access.py`), der Reads/Greps auf `wiki/**` zählt (`.llm-wiki/.stats.jsonl`, lokal) — Konsultationsrate während der Aufgabe, nicht nur am Session-Start. Auswertung: `python3 .llm-wiki/lint_wiki.py --stats`, eingebunden im Skill `wiki-lint`.
