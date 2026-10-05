---
title: "Kommentar-Thread zu Karpathys LLM-Wiki-Gist — Auswertung"
date: 2026-10-01
source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
coverage: ~170 Kommentare aus 6 Zeiträumen (5.4., 8.4., 10.–11.4., 30.4.–4.5., 19.8.–10.9., 13.–23.9.2026); Mitte Mai bis Mitte August nicht ausgewertet
---

# Kommentar-Thread zu Karpathys Gist — Auswertung (10/2026)

Der Thread (Gist vom 04.04.2026) hat mehrere hundert Kommentare, grob zwei Drittel Tool-Vorstellungen. Die inhaltliche Kritik läuft auf fünf Punkte hinaus. Was davon ins Konzept v0.1 eingeflossen ist, steht in der letzten Spalte.

| Problem | Beobachtung im Thread | Vorgeschlagene Lösung | Stimmen | Im Konzept |
|---|---|---|---|---|
| Persistente Fehler, fehlende Herkunft | Halluzination wird zur „Wahrheit", die spätere Seiten zitieren | Quelle pro Aussage; Lint-Befund nur mit wörtlichem Zitat; Status „NOT VERIFIED" | Shagun0402, kkollsga, frankchu91, sshlg, a-a-k | §1.2, §3 (Quelle pro Aussage, Präfixe), `status: entwurf` |
| Veraltetes/widersprüchliches Wissen | Seiten bleiben ewig; Lint findet Konflikte zu spät | Widerspruch beim Schreiben prüfen; superseded statt löschen; gültig-ab vs. bekannt-seit | crajah, kostey, gowtham0992, azaylamba | §1.3–1.4, Ingest-Widerspruchs-Check, `review_by`, Historie |
| Skalierung jenseits Markdown | Index-Pflege, Duplikate, API-Kosten ab einigen hundert Seiten | SQLite/Graph-Index unter Markdown; BM25 statt nur Vektoren; L1/L2-Trennung | mpazik, QipengGuo, arpitnath, MehmetGoekce | §7 Skalierungsstufen |
| Agent konsultiert das Wiki nicht | Wiki wird nur zu Sessionbeginn gelesen | explizite Auslöser; Lessons in Tool-Beschreibungen; Konsultationsrate messen | orcosto-lab | §4 Konsultations-Regeln (Messen: offen) |
| Format-Drift | Modelle/Sessions schreiben Frontmatter unterschiedlich | Schema per Skript erzwingen | securityguy, sidleo | §5 Lint + Pre-Commit-Hook |
| Fehlende Benchmarks | Kein unabhängiger Vergleich mit RAG | — | a-a-k, oefi | offen |

**Tools**: Ideen übernehmen, Tools nicht installieren (Compliance, Reife, Eigenwerbung). Kandidat für Stufe 2: lokale Volltextsuche (SQLite FTS5/BM25, z. B. qmd).

**Offen für spätere Versionen**
- Konsultationsrate messen (wie oft liest der Agent das Wiki mitten in einer Aufgabe?)
- „gültig ab" und „bekannt seit" getrennt führen (crajah)
- Abschnitt „Gegenargumente & Datenlücken" je Seite (localwolfpackai)
- Kommentare Mitte Mai bis Mitte August nachholen: `gh api --paginate gists/442a6bf555914893e9891c11519de94f/comments`

Weitere Antworten auf das Gist: [LLM Wiki v2 (rohitg00)](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2), [vier strukturelle Lücken (V-interactions)](https://gist.github.com/V-interactions/a0d2a62c1b16d1fecf1bd81e8f611fba).
