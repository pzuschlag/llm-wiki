---
name: wiki-ingest
description: Neue Quelle (Dokument, Meeting-Notiz, Export) ins LLM-Wiki einarbeiten — inkl. Widerspruchs-Check gegen bestehende Seiten. Verwenden, wenn eine Datei in raw/ liegt oder neue Informationen ins Wiki sollen.
---
<!-- Verwaltet von pzuschlag/llm-wiki — in Instanzen nicht ändern. -->

# Ingest

1. **Quelle sichten**: Rohdokument liegt in `raw/` (oder einem Sync-Unterordner). Nur lesen, nie ändern.
2. **Key Takeaways mit dem Menschen klären**: 3–7 Punkte vorschlagen, Bestätigung abwarten. Bei automatischen Syncs reicht eine kurze Zusammenfassung mit j/n.
3. **Summary-Seite** schreiben (passender `type`, Frontmatter nach `.llm-wiki/CORE.md`), sofern die Quelle eine eigene Seite trägt.
4. **Widerspruchs-Check** — für jede betroffene Entity-Seite *vor* dem Ändern:
   - Seite lesen; neue Aussagen gegen bestehende abgleichen: Termine, Zuständigkeiten, Zahlen, Entscheidungen, Status.
   - **Fakt hat sich geändert** (neuere Quelle, klarer Nachfolger): neue Aussage eintragen, alte nach `## Historie` verschieben — `- YYYY-MM-DD: <alt> → <neu> (<quelle alt> → <quelle neu>)`.
   - **Quellen widersprechen sich** (unklar, was gilt): `> [!warning] Widerspruch (YYYY-MM-DD): <Quelle A> sagt X, <Quelle B> sagt Y` an der Stelle; Mensch fragen; nichts überschreiben.
   - **Ganze Seite überholt**: `status: superseded` + `superseded_by`, bzw. `status: veraltet`.
5. **Entity-Seiten aktualisieren**: Inhalte, Querverweise `[[…]]`, `sources` ergänzen (Präfix-Formate), `last_updated` = heute, `review_by` = heute + `review_days[type]` aus `wiki.config.yaml`. Entscheidungen, Zahlen, Termine, Zusagen mit Inline-Quelle `(<quelle>, YYYY-MM-DD)`.
6. **Index**: neue Seiten eintragen, „Seiten gesamt" anpassen.
7. **Log**: `## [YYYY-MM-DD] ingest | <Quelltitel>` mit Stichpunkten; Zeile `Geändert/superseded: …` für jede Änderung aus Schritt 4.
8. **Overview** anpassen, wenn sich das Gesamtbild ändert.
9. `python3 .llm-wiki/lint_wiki.py` → Errors beheben → committen (Instanz-Regeln in `CLAUDE.md`).
