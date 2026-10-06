#!/usr/bin/env bash
# End-to-end test of the Copier template:
#   1. create a new instance (copier copy)
#   2. lint with no errors (with python3 and, if available, Python 3.9)
#   3. the consultation hook counts only wiki/-reads, --stats reports it, the stats file is gitignored
#   4. pre-commit hook blocks a broken page, lets other commits through
#   5. copier update to a new version: managed file updated, instance customizations survive
# Usage: bash tests/test_template.sh   (needs: copier, git, python3)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com
ok()   { echo "✅ $*"; }
fail() { echo "❌ $*"; exit 1; }

# Template as its own git repo tagged v0.0.1 (current working tree, including uncommitted changes)
TPL="$WORK/template-repo"
mkdir -p "$TPL"
(cd "$REPO" && tar --exclude=.git -cf - .) | (cd "$TPL" && tar -xf -)
git -C "$TPL" init -q && git -C "$TPL" add -A && git -C "$TPL" commit -qm base && git -C "$TPL" tag v0.0.1

ANSWERS=(--data wiki_name="Test Wiki" --data owner_name="Jane Doe" --data wiki_purpose="Test instance of the template." \
         --data git_email=test@example.com --data extra_source_prefixes="jira, confluence" \
         --defaults --trust)

# 1. copy
INST="$WORK/instance"
copier copy -q --vcs-ref v0.0.1 "${ANSWERS[@]}" "$TPL" "$INST" >/dev/null
for f in CLAUDE.md wiki.config.yaml .copier-answers.yml .llm-wiki/CORE.md .llm-wiki/lint_wiki.py \
         .llm-wiki/check_version.py .llm-wiki/hooks/pre-commit .llm-wiki/log_wiki_access.py \
         .claude/settings.json .claude/skills/wiki-ingest/SKILL.md wiki/index.md wiki/log.md wiki/overview.md; do
  [ -e "$INST/$f" ] || fail "copy: $f missing"
done
grep -q "@.llm-wiki/CORE.md" "$INST/CLAUDE.md" || fail "CLAUDE.md does not import CORE.md"
grep -q "source_prefixes: \[jira, confluence\]" "$INST/wiki.config.yaml" || fail "source_prefixes not rendered"
ok "copy: instance created completely"

cd "$INST"
git init -q && git config core.hooksPath .llm-wiki/hooks && git add -A && git commit -qm init

# 2. Lint
python3 .llm-wiki/lint_wiki.py >/dev/null || { python3 .llm-wiki/lint_wiki.py; fail "lint: errors in a fresh instance"; }
ok "lint: fresh instance has no errors"
if command -v uv >/dev/null && PY39="$(uv python find 3.9 2>/dev/null)"; then
  "$PY39" .llm-wiki/lint_wiki.py >/dev/null || fail "lint: breaks under Python 3.9"
  ok "lint: runs under Python 3.9"
fi

# Valid page with an instance prefix
cat > wiki/example.md <<'EOF'
---
title: "Example"
type: concept
sources: ["jira:ABC-1", "url:https://example.com"]
last_updated: 2026-01-01
status: current
review_by: 2099-01-01
---
Example page. See [[Overview]].
EOF
sed -i.bak 's/^- \*\*Total pages\*\*: 1/- **Total pages**: 2/' wiki/index.md && rm wiki/index.md.bak
printf '| [Example](example.md) | concept | Test |\n' >> wiki/index.md
printf '\nRelated: [[Example]]\n' >> wiki/overview.md
python3 .llm-wiki/lint_wiki.py >/dev/null || { python3 .llm-wiki/lint_wiki.py; fail "lint: rejects a valid page"; }
ok "lint: instance prefix (jira:) accepted"

# 3. Pre-commit hook
git add -A && git commit -qm "valid page" || fail "hook: blocks a valid commit"
sed -i.bak 's/^status: current/status: broken/' wiki/example.md && rm wiki/example.md.bak
git add wiki/example.md
if git commit -qm "broken" >/dev/null 2>&1; then fail "hook: invalid status not blocked"; fi
git checkout -q HEAD -- wiki/example.md
ok "hook: invalid page blocked"
echo "note" > notes.txt && git add notes.txt && git commit -qm "no wiki" || fail "hook: blocks a non-wiki commit"
ok "hook: non-wiki commits go through"

# 3b. Consultation hook (PostToolUse): a Read on wiki/ is counted, on notes.txt it is not
echo '{"tool_name":"Read","tool_input":{"file_path":"wiki/index.md"},"cwd":"'"$INST"'"}' | python3 .llm-wiki/log_wiki_access.py
echo '{"tool_name":"Read","tool_input":{"file_path":"notes.txt"},"cwd":"'"$INST"'"}' | python3 .llm-wiki/log_wiki_access.py
[ -f .llm-wiki/.stats.jsonl ] || fail "hook: .stats.jsonl was not created"
[ "$(wc -l < .llm-wiki/.stats.jsonl | tr -d ' ')" = "1" ] || fail "hook: wrong number of entries (only wiki/ reads should count)"
python3 .llm-wiki/lint_wiki.py --stats | grep -q "wiki/index.md" || fail "lint --stats: entry missing from the report"
git check-ignore -q .llm-wiki/.stats.jsonl || fail ".stats.jsonl is not gitignored"
ok "hook: consultation log counts only wiki/ reads, --stats reports it, the file is gitignored"

# 3c. Migration 0001: old German status values get translated, idempotently
sed -i.bak 's/^status: current/status: aktuell/' wiki/example.md && rm wiki/example.md.bak
python3 .llm-wiki/migrations/0001_status_en.py --dry-run | grep -q "would change: wiki/example.md" || fail "migration 0001: --dry-run did not detect the page"
grep -q "^status: aktuell" wiki/example.md || fail "migration 0001: --dry-run must not write"
python3 .llm-wiki/migrations/0001_status_en.py | grep -q "Changed: 1 page" || fail "migration 0001: did not report a change"
grep -q "^status: current" wiki/example.md || fail "migration 0001: status not translated"
python3 .llm-wiki/migrations/0001_status_en.py | grep -q "Changed: 0 page" || fail "migration 0001: not idempotent"
python3 .llm-wiki/lint_wiki.py >/dev/null || fail "lint: errors after migration 0001"
git checkout -q HEAD -- wiki/example.md
ok "migration 0001: aktuell/entwurf/veraltet → current/draft/outdated, idempotent"

# 3d. check_version.py: up to date against its own installed tag, no marker
python3 .llm-wiki/check_version.py --force | grep -q "up to date" || fail "check_version: should report up to date against v0.0.1"
[ ! -f raw/.llm_wiki_upgrade_pending.json ] || fail "check_version: marker should not exist while up to date"
ok "check_version: up to date, no marker"

# 4. Update: instance customizes CLAUDE.md, template changes CORE.md and the CLAUDE.md template
echo "Instance-specific rule XYZ" >> CLAUDE.md && git commit -qam "instance customization"
echo "<!-- New core rule from v0.0.2 -->" >> "$TPL/template/.llm-wiki/CORE.md"
echo "Template change the instance must NOT receive" >> "$TPL/template/CLAUDE.md.jinja"
git -C "$TPL" commit -qam "v0.0.2" && git -C "$TPL" tag v0.0.2

# 4a. check_version.py: $TPL (acting as the concept repo) is now ahead — detect it, write the marker, don't re-upgrade here
python3 .llm-wiki/check_version.py | grep -q "UPGRADE (routine): v0.0.1 -> v0.0.2" || fail "check_version: did not detect v0.0.2 as latest"
[ -f raw/.llm_wiki_upgrade_pending.json ] || fail "check_version: marker not written when behind"
grep -q '"latest": "v0.0.2"' raw/.llm_wiki_upgrade_pending.json || fail "check_version: marker has wrong latest version"
python3 .llm-wiki/check_version.py | grep -q "marker already set" || fail "check_version: should not overwrite an unread marker"
ok "check_version: detects being behind, writes the marker once"
copier update -q --skip-answered --defaults --trust --vcs-ref v0.0.2 >/dev/null
grep -q "New core rule from v0.0.2" .llm-wiki/CORE.md || fail "update: CORE.md not updated"
grep -q "Instance-specific rule XYZ" CLAUDE.md || fail "update: instance customization in CLAUDE.md was lost"
! grep -q "must NOT receive" CLAUDE.md || fail "update: CLAUDE.md (instance-owned) was overwritten"
grep -q "_commit: v0.0.2" .copier-answers.yml || fail "update: version not recorded in .copier-answers.yml"
python3 .llm-wiki/lint_wiki.py >/dev/null || fail "lint: errors after update"
ok "update: managed file updated, instance files unchanged, version v0.0.2 recorded"

echo "All tests passed."
