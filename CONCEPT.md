---
title: "LLM-Wiki — Konzept"
version: 0.1.0
status: entwurf
last_updated: 2026-10-02
---

# LLM-Wiki — Konzept

Ein LLM-Wiki ist ein persistentes, vom LLM gepflegtes Markdown-Wiki, das Wissen aus Rohquellen kompiliert, statt es bei jeder Frage neu abzuleiten. Dieses Dokument beschreibt eine konkrete, im Alltag erprobte Variante des Patterns. Es ist die zentrale Quelle für alle Wikis, die das Konzept anwenden, und unabhängig von deren Inhalt.

Grundlage: [Karpathys LLM-Wiki-Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (04/2026), erweitert um Erkenntnisse aus dem Kommentar-Thread und dem Betrieb eines Arbeits-Wikis (~100 Seiten, seit 04/2026).

**Status**: v0.x — experimentell. Das Konzept läuft in einem Arbeits-Wiki (Referenz für v0.1); ein Privat-Wiki ist geplant. Instanzen sind eigene, private Repos und nicht Teil dieses Repos.

---

## 1. Prinzipien

1. **Kompilieren statt suchen.** Neue Quellen werden eingearbeitet (Entity-Seiten aktualisiert, Querverweise gesetzt), nicht nur indiziert.
2. **Jede Aussage ist zurückführbar.** Seiten nennen ihre Quellen; Entscheidungen, Zahlen, Termine und Zusagen tragen eine Quelle pro Aussage.
3. **Wissen hat einen Lebenszyklus.** Seiten sind `aktuell`, `entwurf`, `veraltet` oder `superseded` und haben ein Review-Datum. Geänderte Fakten werden historisiert, nicht überschrieben.
4. **Widersprüche beim Schreiben, nicht beim Lesen.** Der Ingest prüft neue gegen bestehende Aussagen, bevor er etwas ändert.
5. **Erzwingen statt hoffen.** Was mechanisch prüfbar ist (Schema, Quellen-Format, Links, Index), prüft ein Skript und blockiert Commits. Das Modell-Verhalten wird nicht als Kontrolle betrachtet.
6. **Mensch an den Weichen.** Ingest beginnt mit einer Diskussion der Key Takeaways; echte Widersprüche entscheidet der Mensch; strukturelle Änderungen laufen per Pull Request.
7. **Inhalt und Methode getrennt.** Das Konzept enthält keinen Inhalt. Jedes Wiki ist ein eigenes Repo mit eigenen Zugriffs- und Compliance-Regeln. Wikis verlinken nicht untereinander.

## 2. Architektur einer Instanz

| Schicht | Ort | Wer schreibt | Regel |
|---|---|---|---|
| Rohquellen | `raw/` | Sync-Skripte, Mensch | unveränderlich; sensible Daten gitignored |
| Wiki | `wiki/` | LLM | Schema siehe §3 |
| Schema & Workflows | `CLAUDE.md` + `.llm-wiki/` | Konzept (verwaltet) + Instanz | siehe §6 |
| Prüfung | `.llm-wiki/lint_wiki.py`, Pre-Commit-Hook | Konzept (verwaltet) | Errors blockieren |
| Betrieb | `.claude/skills/`, `scripts/` | Instanz | domänenspezifische Syncs |

Pflichtseiten: `wiki/index.md` (Katalog, „Seiten gesamt"), `wiki/log.md` (append-only Operationslog), `wiki/overview.md` (Synthese).

## 3. Seitenschema

```yaml
---
title: "Seitentitel"
type: <aus wiki.config.yaml>          # Kern: area, person, project, decision, concept, meta, draft, template
tags: [tag1, tag2]
sources: ["confluence:123", "raw/…"] # feste Präfixe, immer gequotet
last_updated: YYYY-MM-DD
status: aktuell | entwurf | veraltet | superseded
review_by: YYYY-MM-DD                # last_updated + Intervall je Typ
superseded_by: "[[Nachfolger]]"      # Pflicht bei superseded
---
```

- **Quellen-Formate**: Kern-Präfixe `raw/`, `wiki/`, `url:`, `meeting:`, `note:`. Domänen-Präfixe (z. B. `confluence:`, `jira:`, `notion:`) definiert die Instanz in `wiki.config.yaml`. `wiki/…` allein ist keine Quelle; `note:` ist Notlösung (Lint warnt).
- **Review-Intervalle** je Typ in `wiki.config.yaml` (Vorgabe: person 60 T., project/area 45, product 90, concept/decision 180).
- **Seitenaufbau**: 1-Satz-Summary → `##`-Sektionen → `[[Links]]` → optional `## Historie` → optional `## Quellen`.
- **Historie**: `- YYYY-MM-DD: <alt> → <neu> (<quelle alt> → <quelle neu>)`.
- **Widerspruch**: `> [!warning] Widerspruch (YYYY-MM-DD): <A> sagt X, <B> sagt Y`.

## 4. Workflows

**Ingest**: Quelle in `raw/` → Key Takeaways mit dem Menschen → Summary-Seite → *Widerspruchs-Check je betroffener Seite* (geändert → Historie; uneinig → Callout + fragen; überholt → superseded/veraltet) → Entity-Seiten inkl. `sources`/`last_updated`/`review_by` → Index → Log (inkl. „Geändert/superseded") → Overview.

**Query**: Index → Seiten → Antwort mit Seitenreferenzen, `status`/`review_by` beachten → dauerhaft wertvolle Antworten als Seite speichern → Log.

**Lint**: `lint_wiki.py` (mechanisch) + inhaltliche Prüfung durch das LLM (Widersprüche, fehlende Seiten, fehlende Querverweise).

**Session-Start**: Instanz-Syncs (Skills) → Staleness-Report (`lint_wiki.py --stale`) → Auffrischen anbieten.

**Konsultations-Regeln** (verbindlich in jeder Instanz): vor Aussagen zu Entities zuerst die Seite lesen; Widerspruch zu einer Quelle → Ingest-Check statt Überschreiben; veraltete Seite → in der Antwort sagen.

## 5. Prüfung (Lint)

| Stufe | Checks | Wirkung |
|---|---|---|
| Error | Frontmatter/Pflichtfelder, `status`-Wert, superseded ohne Nachfolger, Quellen-Format, broken links, Orphans, Seite fehlt im Index, „Seiten gesamt" falsch | blockiert Commit (Pre-Commit-Hook, nur bei `wiki/*.md`) |
| Warning | keine Quellen, nur Wiki-Quellen, `note:`-Quellen, `review_by` überschritten, mehrdeutige Dateinamen | Report, Session-Start |

Link-Auflösung: Pfad, `title` und `aliases` vor Dateiname.

## 6. Verteilung: vom Konzept in die Instanzen

**Ziel**: Konzept-Änderungen erreichen alle Instanzen, aber jede Instanz übernimmt sie bewusst (Pull, nicht Push), mit Review und, wo nötig, Datenmigration.

**Zentrales Repo `llm-wiki`** (Entscheidung: [ADR 0001](decisions/0001-verteilung-per-copier.md)):

```
llm-wiki/
├── CONCEPT.md            # dieses Dokument
├── CHANGELOG.md          # SemVer: MAJOR = Migration nötig, MINOR = neue Regel/Check, PATCH = Fix
├── decisions/            # ADRs zum Konzept
├── research/             # Notizen aus Gist-Thread, anderen Implementierungen
├── template/             # Copier-Template einer Instanz
│   ├── .llm-wiki/        # VERWALTET: CORE.md (Regeln), lint_wiki.py, hooks/pre-commit, migrations/
│   ├── .claude/skills/wiki-*/   # VERWALTET: ingest, query, lint, upgrade
│   ├── CLAUDE.md.jinja   # einmalig erzeugt, danach Instanz-Eigentum; importiert @.llm-wiki/CORE.md
│   ├── wiki.config.yaml.jinja   # Instanz-Parameter: Typen, Intervalle, Quellen-Präfixe, Sprache
│   └── wiki/index.md, log.md, overview.md
└── copier.yml            # Fragen, _migrations je Version
```

**Eigentum** ist die zentrale Regel: Dateien unter `.llm-wiki/` und `.claude/skills/wiki-*` gehören dem Konzept und werden in Instanzen nie von Hand geändert. `CLAUDE.md`, `wiki/`, `raw/`, Instanz-Skills und `wiki.config.yaml` gehören der Instanz. Die Instanz-`CLAUDE.md` bindet die Kernregeln per `@.llm-wiki/CORE.md` ein und ergänzt nur Domänen-Spezifisches.

**Ablauf einer Konzept-Änderung**:
1. Idee/Problem entsteht (oft in einer Instanz) → Issue im `llm-wiki`-Repo, ggf. ADR.
2. Umsetzung im Template + Migrationsskript, falls Daten betroffen sind (wie `migrate_frontmatter_wq45.py`) → Release-Tag `vX.Y.Z` + Changelog.
3. Pro Instanz: Skill `wiki-upgrade` → `copier update` auf einem Branch → Migrationen laufen → `lint_wiki.py` → Pull Request → Merge. Die installierte Version steht in `.copier-answers.yml` (`_commit`).

**Neue Instanz**: `copier copy gh:pzuschlag/llm-wiki <ordner>` → Fragen beantworten → `git config core.hooksPath .llm-wiki/hooks`. Details im [README](README.md).

**Warum Copier statt Plugin, Submodul oder Symlink**

| Option | Pro | Contra |
|---|---|---|
| **Copier-Template** (empfohlen) | 3-Wege-Merge bei Updates, Versionen per Git-Tag, `_migrations` je Version, Dateien liegen versioniert in der Instanz (funktioniert auch in Cloud-Sessions und auf anderen Rechnern) | zusätzliches Tool (`pipx install copier`) |
| Claude-Code-Plugin | Skills/Hooks versioniert, Update per `/plugin` | liefert keine immer geladenen Regeln (kein CLAUDE.md), migriert keine Daten, wird in Cloud-Sessions nicht geladen |
| Git-Submodul | einfach, exakt versioniert | Regeln nicht anpassbar, kein Migrationsmechanismus, umständliche Updates |
| Symlink auf lokalen Ordner | sofort überall aktiv | nur auf einem Rechner, keine Versionen, Externe-Import-Freigabe nötig, jede Änderung wirkt ungeprüft in allen Wikis |

Ein Plugin kann später ergänzen (z. B. `/wiki:ingest` als Befehl), ist aber nicht der Verteilmechanismus.

## 7. Skalierung

Die Navigation über `index.md` + Volltext-`grep` trägt, solange der Index bequem in den Kontext passt und eine typische Frage wenige Seiten braucht. Umgestellt wird nach **Signalen**, nicht nach Seitenzahl allein.

| Stufe | Typische Größe | Navigation | Wann wechseln (Signale) |
|---|---|---|---|
| **1 — Index** | bis ~200–300 Seiten | `index.md` → Seiten lesen, `grep` | — |
| **2 — Index + lokale Suche** | ~300–1.000 Seiten | Index pro Bereich (`areas/index.md` …) + lokale Volltextsuche (SQLite FTS5 / BM25, z. B. qmd) als Tool/Skill | Index > ~10k Tokens · Queries brauchen regelmäßig > 8 Seiten-Reads · der Agent übersieht vorhandene Seiten · Duplikate tauchen auf |
| **3 — Hybrid + strukturierte Fakten** | > 1.000 Seiten oder viele Quellen pro Tag | BM25 + lokale Embeddings, Fakten (Entity, Attribut, Wert, Quelle, gültig ab) in SQLite, Markdown-Seiten daraus gerendert; Widerspruchs-Check als Abfrage statt LLM-Vergleich | Widerspruchs-Check im Ingest wird unzuverlässig/teuer · Lint-Laufzeit > 1 min · Faktenfragen über viele Seiten („alle Deadlines im Q4") |

**Querschnitt, unabhängig von der Stufe**:
- **Append-only-Dateien begrenzen**: `log.md` und Meeting-Sammlungen pro Quartal nach `wiki/archive/YYYY-Qn/` auslagern, sobald sie > ~25k Tokens sind.
- **Kontext-Schichten**: Kernregeln (`CORE.md`) immer geladen und kurz (< 200 Zeilen); Betriebsabläufe als Skills (laden bei Bedarf); Seiteninhalte nur über Index/Suche.
- **Lokal vor Cloud**: Suchindex und Embeddings laufen lokal; keine Inhalte an Drittdienste (Compliance, siehe §8).

*Referenz Arbeits-Wiki (10/2026)*: ~100 Seiten, `index.md` ≈ 16 KB (~4–5k Tokens), Wiki gesamt ≈ 1,2 MB, `log.md` ≈ 220 KB (~60k Tokens). → Stufe 1; `log.md` hat die Archivierungsschwelle bereits überschritten.

## 8. Datenschutz & Compliance

- Jede Instanz klärt in ihrem `CLAUDE.md`: Wer darf das Repo sehen? Welche Daten bleiben lokal (`raw/` gitignored)? Welche Themen gehören gar nicht ins Wiki?
- Das Konzept-Repo enthält nie Instanz-Inhalte; Beispiele sind synthetisch.
- Keine Drittanbieter-Tools, die Inhalte an fremde Server oder LLM-Anbieter senden; Tools aus der Community werden als Ideenquelle genutzt, nicht installiert.
- Memory-Sync und Auto-Commits respektieren Ausschlusslisten (`.memory-syncignore`, `.gitignore`); Lint prüft, dass nichts Ignoriertes getrackt ist.

## 9. Offene Fragen

- Soll ein Privat-Wiki Personen-Seiten mit sensiblen Inhalten (Gesundheit, Finanzen) führen, und wenn ja, mit welchem Schutz (lokal-only, verschlüsselt)?
- Gibt es Seitentypen, die über alle Instanzen gleich sind (z. B. `person`), und gemeinsame Felder dafür?
- Wie fließen Erkenntnisse aus dem Gist-Thread regelmäßig in `research/` (z. B. monatlicher Abgleich)?

## Historie
- 2026-10-02: v0.1.0 — Erstentwurf, abgeleitet aus einem Arbeits-Wiki nach der Analyse des Gist-Threads.
