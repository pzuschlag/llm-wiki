---
title: "ADR 0002: Sensible Daten in Instanzen — Schutz per git-crypt"
status: angenommen
date: 2026-10-05
---

# ADR 0002: Sensible Daten in Instanzen — Schutz per git-crypt

## Kontext
Issue #2: Ein Privat-Wiki soll Seiten mit sensiblen Inhalten (z. B. Gesundheit, Finanzen, Beziehungen) führen können. Offen war, mit welchem Schutzmechanismus und ob Cloud-Sessions zugreifen dürfen. Erwogen wurde auch ein selbst gehosteter Git-Server für ortsunabhängigen Zugriff ohne Drittanbieter — das würde aber ein durch Verschlüsselung lösbares Risiko (falsche Sichtbarkeit, kompromittierter Account) gegen ein neues eintauschen: einen zusätzlichen, vom Internet erreichbaren Dienst.

## Entscheidung
Instanzen mit sensiblen Inhalten verschlüsseln ihr Repo — ganz oder in sensiblen Teilbereichen — mit [git-crypt](https://github.com/AGWA/git-crypt), statt sich auf Self-Hosting oder die Sichtbarkeits-Einstellung des Remotes allein zu verlassen. Das Repo bleibt ein gewöhnliches privates Remote-Repo; git-crypt schützt den Inhalt zusätzlich, falls Sichtbarkeit oder Account-Zugriff versagen.

Jede Instanz legt in ihrer `CLAUDE.md` fest:
- welche Pfade git-crypt-verschlüsselt sind (`.gitattributes`), ggf. das gesamte Repo,
- wer die Schlüssel (GPG-Keys oder symmetrischer Key) hält,
- ob Cloud-Sessions auf das Repo zugreifen dürfen — git-crypt entschlüsselt lokal beim Checkout, Cloud-Zugriff setzt voraus, dass der Schlüssel dort verfügbar ist.

Das gilt für jede Instanz mit sensiblen Themen, nicht nur neue — bestehende Instanzen können git-crypt nachträglich einführen.

## Alternativen
| Option | Warum nicht (allein) |
|---|---|
| Selbst gehosteter Git-Server | tauscht ein durch Verschlüsselung lösbares Risiko (falsche Sichtbarkeit) gegen ein neues (zusätzlicher, internetseitig erreichbarer Dienst) |
| Nur Remote-Sichtbarkeit "privat" | schützt nicht bei Fehlkonfiguration oder kompromittiertem Account |
| Separates Repo pro Themenbereich, unverschlüsselt | Mehraufwand ohne zusätzlichen Schutz gegenüber git-crypt |

## Konsequenzen
- `git-crypt` muss lokal installiert sein; Setup pro Instanz: `git-crypt init`, `.gitattributes` (Pfade oder gesamtes Repo), `git-crypt add-gpg-user` oder Export des symmetrischen Keys als Backup.
- Lint und Skills arbeiten wie gewohnt auf dem entschlüsselten Working Tree — keine Sonderbehandlung im Konzept nötig.
- Welche Themen konkret ins Repo gehören und wie Cloud-Zugriff genutzt wird, entscheidet jede Instanz selbst (Prinzip 7) und dokumentiert es in ihrer `CLAUDE.md`.
