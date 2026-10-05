#!/usr/bin/env python3
"""
Verwaltet von pzuschlag/llm-wiki.

PostToolUse-Hook (siehe .claude/settings.json): zählt Read/Grep-Zugriffe auf
wiki/** während einer Aufgabe (nicht nur am Session-Start) und hängt sie an
.llm-wiki/.stats.jsonl an (lokal, gitignored). Auswertung: `lint_wiki.py --stats`,
eingebunden in den Skill wiki-lint. Blockiert nie — Fehler werden verschluckt.
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
        return 0  # kein Pfad oder nicht unter wiki/ (z. B. Grep ohne path)

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
