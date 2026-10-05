---
name: wiki-query
description: Frage aus dem LLM-Wiki beantworten — über Index und Seiten, mit Seitenreferenzen und Hinweis auf veraltete Seiten. Verwenden bei Fragen zu Entities, Entscheidungen oder Zusammenhängen dieser Wiki-Domäne.
---
<!-- Verwaltet von pzuschlag/llm-wiki — in Instanzen nicht ändern. -->

# Query

1. `wiki/index.md` lesen → relevante Seiten bestimmen. Bei Bedarf zusätzlich `grep -ril "<begriff>" wiki/`.
2. Seiten lesen. Für jede genutzte Seite `status` und `review_by` prüfen.
3. Antwort synthetisieren:
   - mit Seitenreferenzen (`wiki/projects/x.md`) und, wo vorhanden, den Inline-Quellen
   - veraltete/superseded Seiten oder überschrittenes `review_by` ausdrücklich nennen und die Primärquelle prüfen
   - Lücken offen benennen statt aus dem Gedächtnis zu ergänzen
4. Ist die Antwort dauerhaft wertvoll (Synthese über mehrere Seiten, wiederkehrende Frage) → als neue Seite speichern (Index, Querverweise).
5. Log: `## [YYYY-MM-DD] query | <Fragestellung>`.
