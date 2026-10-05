#!/usr/bin/env python3
"""
Migration 0001: translate the `status` frontmatter value to English.

aktuell -> current, entwurf -> draft, veraltet -> outdated. `superseded` is
unchanged (was already English). Idempotent: a second run finds nothing left
to change. Only touches the `status:` line inside each page's frontmatter
block, nothing else (quoting style preserved).

Usage:
  python3 .llm-wiki/migrations/0001_status_en.py            # apply
  python3 .llm-wiki/migrations/0001_status_en.py --dry-run  # report only
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WIKI_DIR = REPO_ROOT / "wiki"

MAPPING = {"aktuell": "current", "entwurf": "draft", "veraltet": "outdated"}
STATUS_LINE = re.compile(
    r'^(status:\s*)(["\']?)(' + "|".join(MAPPING) + r')(["\']?)\s*$', re.MULTILINE
)


def frontmatter_block(content: str) -> tuple[int, int] | None:
    m = re.match(r"^---\n.*?\n---", content, re.DOTALL)
    return (m.start(), m.end()) if m else None


def migrate_file(path: Path, dry_run: bool) -> bool:
    content = path.read_text(encoding="utf-8")
    span = frontmatter_block(content)
    if not span:
        return False
    start, end = span
    block = content[start:end]

    def repl(m: re.Match) -> str:
        return f"{m.group(1)}{m.group(2)}{MAPPING[m.group(3)]}{m.group(4)}"

    new_block, n = STATUS_LINE.subn(repl, block)
    if n == 0:
        return False
    if not dry_run:
        path.write_text(content[:start] + new_block + content[end:], encoding="utf-8")
    return True


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    changed = 0
    for f in sorted(WIKI_DIR.rglob("*.md")):
        if migrate_file(f, dry_run):
            changed += 1
            print(f"{'would change' if dry_run else 'changed'}: {f.relative_to(REPO_ROOT)}")
    print(f"Changed: {changed} page(s)." + (" (--dry-run)" if dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
