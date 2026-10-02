---
name: wiki-lint
description: Gesundheitscheck des LLM-Wikis — mechanischer Lint plus inhaltliche Prüfung auf Widersprüche, veraltete Aussagen und fehlende Seiten. Verwenden auf Nachfrage oder regelmäßig (z. B. wöchentlich).
---
<!-- Verwaltet von pzuschlag/llm-wiki — in Instanzen nicht ändern. -->

# Lint

1. `python3 .llm-wiki/lint_wiki.py` ausführen.
   - **Errors** sofort beheben (Frontmatter, Status, Quellen-Format, Links, Orphans, Index).
   - **Warnings** als Arbeitsvorrat melden, gruppiert: überfällige Seiten (`stale`), fehlende/vage Quellen, mehrdeutige Dateinamen, getrackte ignorierte Dateien (`tracked-ignored` → Compliance, Mensch informieren).
2. Inhaltlich prüfen (Stichprobe, Fokus auf zuletzt geänderte und überfällige Seiten):
   - Widersprüche zwischen Seiten (gleiche Entity, unterschiedliche Fakten)
   - Aussagen, die neuere Quellen überholt haben
   - wichtige Begriffe ohne eigene Seite; fehlende Querverweise
   - Append-only-Dateien (`log.md`, Meeting-Sammlungen) über ~25k Tokens → Archivierung vorschlagen (`wiki/archive/YYYY-Qn/`)
3. Ausgabe: Liste konkreter Vorschläge (Seite, Problem, Vorschlag). Änderungen erst nach Freigabe.
4. Log: `## [YYYY-MM-DD] lint | <Kurzfazit>`.
