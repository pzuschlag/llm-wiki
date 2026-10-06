#!/usr/bin/env python3
"""Checks this instance's installed concept version against the latest release
of the concept repo, and flags whether catching up needs manual steps.

Self-contained on purpose: it only ever looks at *this* instance (reads its own
`.copier-answers.yml`, derives the concept repo from `_src_path`) — no instance
should need to know about any other instance. Wire this into your own local
scheduling (cron, a macOS LaunchAgent, whatever) at whatever cadence you like;
the concept repo doesn't prescribe one.

It never runs `copier update` itself — that needs review (3-way merge,
conflict resolution, lint, a pull request), i.e. an LLM session in this repo.
See the `wiki-upgrade` skill for the actual upgrade. This script is just the
nudge: it writes `raw/.llm_wiki_upgrade_pending.json` when behind, with an
`installed`/`latest`/`breaking` summary (`breaking` = a CHANGELOG.md entry
newer than the installed version contains "**Breaking**", i.e. likely needs a
migration, not just a routine patch).

The marker is not overwritten while unread (same idempotency as other
instance-local nudges) unless --force; it's removed automatically once the
instance has caught up.

Usage: python3 .llm-wiki/check_version.py [--force]
Exit: 0 always — this never fails a caller (e.g. a LaunchAgent run).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request

REPO_ROOT = os.getcwd()
ANSWERS_FILE = os.path.join(REPO_ROOT, ".copier-answers.yml")
MARKER = os.path.join(REPO_ROOT, "raw", ".llm_wiki_upgrade_pending.json")


def version_tuple(tag: str) -> tuple[int, int, int]:
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def read_answers() -> tuple[str | None, str | None]:
    """(installed version, concept repo URL) from .copier-answers.yml, or (None, None)."""
    installed = src_path = None
    try:
        with open(ANSWERS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("_commit:"):
                    installed = line.split(":", 1)[1].strip()
                elif line.startswith("_src_path:"):
                    src_path = line.split(":", 1)[1].strip()
    except OSError:
        return None, None
    return installed, src_path


def repo_urls(src_path: str) -> tuple[str, str]:
    """(clone URL, raw-content base URL) from a copier `_src_path` like `gh:org/repo`."""
    m = re.match(r"gh:([^/]+)/(.+)", src_path)
    if m:
        org, repo = m.groups()
        return f"https://github.com/{org}/{repo}", f"https://raw.githubusercontent.com/{org}/{repo}"
    # Already a plain URL (git@, https://, etc.) — best effort, no raw-content mirror.
    return src_path, src_path


def latest_tag(clone_url: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "ls-remote", "--tags", clone_url],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except Exception:
        return None
    tags = [
        line.split("refs/tags/")[-1]
        for line in out.splitlines()
        if "refs/tags/v" in line and "^{}" not in line
    ]
    return max(tags, key=version_tuple) if tags else None


def has_breaking_change(raw_base: str, installed: str, latest: str) -> bool:
    """Fetch CHANGELOG.md at `latest`, check entries newer than `installed`."""
    try:
        url = f"{raw_base}/{latest}/CHANGELOG.md"
        with urllib.request.urlopen(url, timeout=15) as r:
            changelog = r.read().decode("utf-8")
    except Exception:
        return False  # unknown — don't block the nudge on a network hiccup
    installed_v = version_tuple(installed)
    # Entries look like "## [0.4.3] — 2026-10-05"; collect ones newer than installed.
    sections = re.split(r"^## \[(\d+\.\d+\.\d+)\]", changelog, flags=re.MULTILINE)
    # sections = [preamble, version1, body1, version2, body2, ...]
    for i in range(1, len(sections), 2):
        v, body = sections[i], sections[i + 1]
        if version_tuple(v) > installed_v and "**Breaking**" in body:
            return True
    return False


def main() -> int:
    force = "--force" in sys.argv
    installed, src_path = read_answers()
    if not installed or not src_path:
        print("skip: no .copier-answers.yml / _commit / _src_path found (not a copier instance?)")
        return 0

    clone_url, raw_base = repo_urls(src_path)
    latest = latest_tag(clone_url)
    if not latest:
        print("could not determine latest concept tag (network issue?)")
        return 0

    print(f"installed: {installed}  latest: {latest}")

    if version_tuple(installed) >= version_tuple(latest):
        print("up to date")
        try:
            os.unlink(MARKER)
            print("cleared stale marker")
        except OSError:
            pass
        return 0

    if os.path.exists(MARKER) and not force:
        print("marker already set (unread) — not overwriting")
        return 0

    breaking = has_breaking_change(raw_base, installed, latest)
    os.makedirs(os.path.dirname(MARKER), exist_ok=True)
    with open(MARKER, "w", encoding="utf-8") as f:
        json.dump({
            "installed": installed,
            "latest": latest,
            "breaking": breaking,
            "note": (
                "A newer llm-wiki concept release is available. Use the "
                "wiki-upgrade skill in a session in this repo to review the "
                "changelog and apply it (copier update, branch + pull request)."
            ),
        }, f, indent=2, ensure_ascii=False)
    print(f"{'UPGRADE (breaking, likely manual steps)' if breaking else 'UPGRADE (routine)'}: {installed} -> {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
