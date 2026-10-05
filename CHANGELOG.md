# Changelog

Versionierung nach SemVer:
- **MAJOR**: Instanzen brauchen eine Datenmigration oder manuelle Schritte
- **MINOR**: neue Regel, neuer Check, neuer Skill — ohne Datenmigration
- **PATCH**: Korrekturen, Formulierungen

## [0.2.0] — 2026-10-05

- Datenschutz: Instanzen mit sensiblen Inhalten verschlüsseln ganz oder teilweise mit `git-crypt` statt sich auf Sichtbarkeits-Einstellungen zu verlassen; Cloud-Zugriff regelt die Instanz in ihrer `CLAUDE.md` ([ADR 0002](decisions/0002-sensible-daten-git-crypt.md))

## [0.1.0] — 2026-10-02

Erste Version, abgeleitet aus dem Betrieb eines Arbeits-Wikis und der Analyse des Kommentar-Threads zu Karpathys Gist.

- Konzept: Prinzipien, Instanz-Architektur, Seitenschema, Workflows, Verteilung per Copier, Skalierungsstufen, Compliance
- Seitenschema mit `status`, `review_by`, `superseded_by` und festen Quellen-Präfixen
- `lint_wiki.py`: Errors/Warnings, konfigurierbar über `wiki.config.yaml`, `--stale`, `--strict`
- Pre-Commit-Hook (nur bei gestagten `wiki/*.md`)
- Skills: `wiki-ingest` (mit Widerspruchs-Check), `wiki-query`, `wiki-lint`, `wiki-upgrade`
