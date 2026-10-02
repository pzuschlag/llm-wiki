#!/usr/bin/env bash
# Testet die Copier-Vorlage end-to-end:
#   1. neue Instanz anlegen (copier copy)
#   2. Lint ohne Errors (mit python3 und, falls vorhanden, Python 3.9)
#   3. Pre-Commit-Hook blockiert eine fehlerhafte Seite, lässt andere Commits durch
#   4. copier update auf eine neue Version: verwaltete Datei aktualisiert, Instanz-Anpassungen bleiben
# Usage: bash tests/test_template.sh   (braucht: copier, git, python3)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com
ok()   { echo "✅ $*"; }
fail() { echo "❌ $*"; exit 1; }

# Vorlage als eigenes Git-Repo mit Tag v0.0.1 (aktueller Arbeitsstand, auch uncommitted)
TPL="$WORK/template-repo"
mkdir -p "$TPL"
(cd "$REPO" && tar --exclude=.git -cf - .) | (cd "$TPL" && tar -xf -)
git -C "$TPL" init -q && git -C "$TPL" add -A && git -C "$TPL" commit -qm base && git -C "$TPL" tag v0.0.1

ANSWERS=(--data wiki_name="Test-Wiki" --data owner_name="Erika Mustermann" --data wiki_purpose="Testinstanz der Vorlage." \
         --data git_email=test@example.com --data extra_source_prefixes="jira, confluence" \
         --defaults --trust)

# 1. copy
INST="$WORK/instanz"
copier copy -q --vcs-ref v0.0.1 "${ANSWERS[@]}" "$TPL" "$INST" >/dev/null
for f in CLAUDE.md wiki.config.yaml .copier-answers.yml .llm-wiki/CORE.md .llm-wiki/lint_wiki.py \
         .llm-wiki/hooks/pre-commit .claude/skills/wiki-ingest/SKILL.md wiki/index.md wiki/log.md wiki/overview.md; do
  [ -e "$INST/$f" ] || fail "copy: $f fehlt"
done
grep -q "@.llm-wiki/CORE.md" "$INST/CLAUDE.md" || fail "CLAUDE.md importiert CORE.md nicht"
grep -q "source_prefixes: \[jira, confluence\]" "$INST/wiki.config.yaml" || fail "source_prefixes nicht gerendert"
ok "copy: Instanz vollständig angelegt"

cd "$INST"
git init -q && git config core.hooksPath .llm-wiki/hooks && git add -A && git commit -qm init

# 2. Lint
python3 .llm-wiki/lint_wiki.py >/dev/null || { python3 .llm-wiki/lint_wiki.py; fail "lint: Errors in frischer Instanz"; }
ok "lint: frische Instanz ohne Errors"
if command -v uv >/dev/null && PY39="$(uv python find 3.9 2>/dev/null)"; then
  "$PY39" .llm-wiki/lint_wiki.py >/dev/null || fail "lint: bricht unter Python 3.9"
  ok "lint: läuft unter Python 3.9"
fi

# Gültige Seite mit Instanz-Präfix
cat > wiki/beispiel.md <<'EOF'
---
title: "Beispiel"
type: concept
sources: ["jira:ABC-1", "url:https://example.com"]
last_updated: 2026-01-01
status: aktuell
review_by: 2099-01-01
---
Beispielseite. Siehe [[Overview]].
EOF
sed -i.bak 's/^- \*\*Seiten gesamt\*\*: 1/- **Seiten gesamt**: 2/' wiki/index.md && rm wiki/index.md.bak
printf '| [Beispiel](beispiel.md) | concept | Test |\n' >> wiki/index.md
printf '\nVerwandt: [[Beispiel]]\n' >> wiki/overview.md
python3 .llm-wiki/lint_wiki.py >/dev/null || { python3 .llm-wiki/lint_wiki.py; fail "lint: gültige Seite wird abgelehnt"; }
ok "lint: Instanz-Präfix (jira:) akzeptiert"

# 3. Hook
git add -A && git commit -qm "gültige Seite" || fail "hook: blockiert gültigen Commit"
sed -i.bak 's/^status: aktuell/status: kaputt/' wiki/beispiel.md && rm wiki/beispiel.md.bak
git add wiki/beispiel.md
if git commit -qm "kaputt" >/dev/null 2>&1; then fail "hook: ungültiger status nicht blockiert"; fi
git checkout -q HEAD -- wiki/beispiel.md
ok "hook: ungültige Seite blockiert"
echo "notiz" > notes.txt && git add notes.txt && git commit -qm "kein wiki" || fail "hook: blockiert Nicht-Wiki-Commit"
ok "hook: Nicht-Wiki-Commits laufen durch"

# 4. Update: Instanz passt CLAUDE.md an, Vorlage ändert CORE.md und CLAUDE.md-Vorlage
echo "Instanz-spezifische Regel XYZ" >> CLAUDE.md && git commit -qam "instanz-anpassung"
echo "<!-- Neue Kernregel aus v0.0.2 -->" >> "$TPL/template/.llm-wiki/CORE.md"
echo "Vorlagen-Änderung, die die Instanz NICHT bekommen darf" >> "$TPL/template/CLAUDE.md.jinja"
git -C "$TPL" commit -qam "v0.0.2" && git -C "$TPL" tag v0.0.2
copier update -q --skip-answered --defaults --trust --vcs-ref v0.0.2 >/dev/null
grep -q "Neue Kernregel aus v0.0.2" .llm-wiki/CORE.md || fail "update: CORE.md nicht aktualisiert"
grep -q "Instanz-spezifische Regel XYZ" CLAUDE.md || fail "update: Instanz-Anpassung in CLAUDE.md verloren"
! grep -q "NICHT bekommen" CLAUDE.md || fail "update: CLAUDE.md (Instanz-Eigentum) wurde überschrieben"
grep -q "_commit: v0.0.2" .copier-answers.yml || fail "update: Version nicht in .copier-answers.yml"
python3 .llm-wiki/lint_wiki.py >/dev/null || fail "lint: Errors nach Update"
ok "update: verwaltete Datei aktualisiert, Instanz-Dateien unverändert, Version v0.0.2 vermerkt"

echo "Alle Tests bestanden."
