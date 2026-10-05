#!/usr/bin/env python3
"""
Managed by pzuschlag/llm-wiki.

PostToolUse hook (see .claude/settings.json): counts Read/Grep access to
wiki/** during a task (not just at session start) and appends it to
.llm-wiki/.stats.jsonl (local, gitignored). Evaluation: `lint_wiki.py --stats`,
wired into the wiki-lint skill. Never blocks — errors are swallowed.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATS_PATH = REPO_ROOT / ".llm-wiki" / ".stats.jsonl"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Read", "Grep"):
        return 0

    tool_input = payload.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or tool_input.get("path") or ""
    path = str(raw_path).replace("\\", "/")
    if "/wiki/" not in f"/{path.lstrip('/')}":
        return 0  # no path, or not under wiki/ (e.g. Grep without a path)

    entry = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "tool": tool_name,
        "path": path,
    }
    try:
        with STATS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
