#!/usr/bin/env python3
"""
Wiki Lint — quality check for LLM-wiki instances (managed by pzuschlag/llm-wiki).

Configuration: wiki.config.yaml at the repo root (page_types, review_days, source_prefixes,
meta_pages, orphan_exempt). Runs on Python >= 3.9 with no third-party packages.

ERRORS (exit code 1, block the pre-commit hook):
  frontmatter   frontmatter missing or a required field is missing (title, type, last_updated, status, review_by)
  status        status not in {current, draft, outdated, superseded}; superseded without superseded_by
  source-format a source in `sources` has an invalid format (see .llm-wiki/CORE.md)
  broken-link   [[Link]] points to no page (title-/alias-aware, log.md exempt)
  orphan        page with no incoming links
  index         index.md references a missing file, a page is missing from the index, or "Total pages" is wrong

WARNINGS (reported, don't block; --strict turns them into errors):
  no-source     no sources
  wiki-only     only wiki pages as a source (no primary source)
  vague-source  `note:` source — make it more specific if possible
  stale         review_by has passed
  ambiguous     filename exists in multiple folders ([[name]] is ambiguous)
  unknown-type  `type` not in wiki.config.yaml → page_types
  tracked-ignored  file is tracked even though .gitignore excludes it (compliance)

Link resolution is title-/alias-aware: [[Display Name]] is resolved against the
filename, frontmatter `title`, AND `aliases` (Obsidian-compatible). Section anchors
(`#...`) and the alias pipe (`|Display Text`) are stripped before matching.

Usage:
  python3 .llm-wiki/lint_wiki.py            # full report
  python3 .llm-wiki/lint_wiki.py --strict   # warnings count as errors
  python3 .llm-wiki/lint_wiki.py --stale    # staleness report only (for session start)
  python3 .llm-wiki/lint_wiki.py --stats    # consultation rate from .llm-wiki/.stats.jsonl (see log_wiki_access.py)
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
STATS_PATH = REPO_ROOT / ".llm-wiki" / ".stats.jsonl"
TODAY = datetime.date.today()

CONFIG_PATH = REPO_ROOT / "wiki.config.yaml"
LIFECYCLE = {"current", "draft", "outdated", "superseded"}
REQUIRED_FRONTMATTER = ["title", "type", "last_updated", "status", "review_by"]
CORE_SOURCE_FORMATS = (
    r"^(raw/|wiki/|scripts/)\S"
    r"|^meeting:\d{4}-\d{2}-\d{2}"
    r"|^url:https?://\S+"
    r"|^note:.+"
)
DEFAULT_CONFIG = {
    "page_types": [],
    "review_days": {},
    "source_prefixes": [],
    "meta_pages": ["index.md", "log.md"],
    "orphan_exempt": ["backlog.md", "overview.md"],
}


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Minimal YAML reader for wiki.config.yaml: `key: value`, `key: [a, b]`,
    and one level of indented `sub: value` pairs. Comments with #."""
    cfg = {k: (list(v) if isinstance(v, list) else dict(v)) for k, v in DEFAULT_CONFIG.items()}
    if not path.exists():
        return cfg
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        indented = line.startswith((" ", "\t"))
        key, _, value = line.strip().partition(":")
        key, value = key.strip(), value.strip()
        if indented and current is not None:
            if not isinstance(cfg.get(current), dict):
                cfg[current] = {}
            cfg[current][key] = int(value) if value.isdigit() else value.strip("\"'")
            continue
        current = key
        if value.startswith("["):
            cfg[key] = parse_list(value)
        elif value:
            cfg[key] = value.strip("\"'")
        else:
            cfg[key] = {}
    return cfg


# ── Parsing ──────────────────────────────────────────────────────────────────

def normalize(name: str) -> str:
    """Link/title string → comparison key: lowercase, strip special characters, whitespace → hyphen."""
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"[\s_]+", "-", name).strip("-")
    return name


def clean_link_target(link: str) -> str:
    """[[File#Section|Display Text]] → 'File'. The `/` is kept (can be part of a title)."""
    return link.split("|", 1)[0].split("#", 1)[0].strip()


def extract_links(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def frontmatter_block(content: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    return m.group(1) if m else None


def parse_frontmatter(content: str) -> dict:
    """Simple key/value parsing (one line per key)."""
    block = frontmatter_block(content)
    if block is None:
        return {}
    fields = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def parse_list(value: str) -> list[str]:
    """Inline list [a, "b, c"] → ['a', 'b, c'] (respects quotes)."""
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    items = re.findall(r'\s*("[^"]*"|\'[^\']*\'|[^,]+)', v)
    return [x.strip().strip("\"'").strip() for x in items if x.strip().strip("\"'").strip()]


def extract_list_field(content: str, key: str) -> list[str]:
    """Reads a list from the frontmatter — inline `[a, b]` or block (- a / - b)."""
    block = frontmatter_block(content)
    if block is None:
        return []
    lines = block.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{key}\s*:\s*(.*)$", line)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline:
            return parse_list(inline)
        items = []
        for follow in lines[i + 1:]:
            fm = re.match(r"^\s*-\s*(.+)$", follow)
            if not fm:
                break
            items.append(fm.group(1).strip().strip("\"'"))
        return items
    return []


def parse_date(value: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(value.strip().strip("\"'")[:10])
    except ValueError:
        return None


CONFIG = load_config()
META_PAGES = set(CONFIG["meta_pages"])
ORPHAN_EXEMPT = META_PAGES | set(CONFIG["orphan_exempt"])
_extra = "|".join(re.escape(p) for p in CONFIG["source_prefixes"] if p)
SOURCE_FORMATS = re.compile(CORE_SOURCE_FORMATS + (rf"|^({_extra}):\S+" if _extra else ""))


# ── Lint ─────────────────────────────────────────────────────────────────────

class Report:
    def __init__(self):
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []

    def error(self, kind, msg):
        self.errors.append((kind, msg))

    def warn(self, kind, msg):
        self.warnings.append((kind, msg))


def load_pages() -> dict[str, dict]:
    """{rel_path: {path, content, fm}} for all wiki pages."""
    pages = {}
    for f in sorted(WIKI_DIR.rglob("*.md")):
        rel = f.relative_to(WIKI_DIR).as_posix()
        content = f.read_text(encoding="utf-8")
        pages[rel] = {"path": f, "content": content, "fm": parse_frontmatter(content)}
    return pages


def build_name_map(pages: dict) -> tuple[dict[str, str], dict[str, list[str]]]:
    """{normalized name → rel_path} for filename, title, aliases; plus ambiguous filenames."""
    name_map: dict[str, str] = {}
    by_stem: dict[str, list[str]] = {}
    # Precedence: path, title and aliases before filename — otherwise e.g.
    # concepts/dark-mode.md would swallow the link [[Dark Mode]] that means projects/dark-mode.md.
    for rel, p in pages.items():
        names = {rel[:-3]}  # also [[projects/dark-mode]]
        title = p["fm"].get("title", "").strip().strip("\"'")
        if title:
            names.add(title)
        names.update(extract_list_field(p["content"], "aliases"))
        for n in names:
            name_map.setdefault(normalize(n), rel)
    for rel in pages:
        stem = Path(rel).stem
        by_stem.setdefault(normalize(stem), []).append(rel)
        name_map.setdefault(normalize(stem), rel)
    ambiguous = {k: v for k, v in by_stem.items() if len(v) > 1}
    return name_map, ambiguous


def check_page(rel: str, p: dict, r: Report):
    fm = p["fm"]
    name = Path(rel).name
    if name in META_PAGES:
        return
    if not fm:
        r.error("frontmatter", f"{rel}: missing frontmatter block")
        return
    for field in REQUIRED_FRONTMATTER:
        if field not in fm or not fm[field].strip("\"' "):
            r.error("frontmatter", f"{rel}: missing field '{field}'")

    ptype = fm.get("type", "").strip("\"' ")
    if CONFIG["page_types"] and ptype and ptype not in CONFIG["page_types"]:
        r.warn("unknown-type", f"{rel}: type '{ptype}' not in wiki.config.yaml → page_types")

    status = fm.get("status", "").strip("\"' ")
    if status and status not in LIFECYCLE:
        r.error("status", f"{rel}: status '{status}' invalid ({' | '.join(sorted(LIFECYCLE))})")
    if status == "superseded" and not fm.get("superseded_by", "").strip("\"' "):
        r.error("status", f"{rel}: status superseded without superseded_by")

    sources = extract_list_field(p["content"], "sources")
    for s in sources:
        if not SOURCE_FORMATS.match(s):
            r.error("source-format", f"{rel}: invalid source format '{s}'")
    if fm.get("type", "") in {"meta", "template"}:
        pass
    elif not sources:
        r.warn("no-source", f"{rel}: no sources")
    elif all(s.startswith("wiki/") for s in sources):
        r.warn("wiki-only", f"{rel}: only wiki pages as a source")
    for s in sources:
        if s.startswith("note:"):
            r.warn("vague-source", f"{rel}: '{s}'")

    review_by = parse_date(fm.get("review_by", ""))
    if review_by and review_by < TODAY and status != "superseded":
        r.warn("stale", f"{rel}: review_by {review_by} ({(TODAY - review_by).days} d. overdue)")


def check_links(pages: dict, name_map: dict, r: Report):
    incoming: dict[str, set] = {rel: set() for rel in pages}
    for rel, p in pages.items():
        is_history = Path(rel).name == "log.md"  # append-only, old links are allowed to go stale
        for link in extract_links(p["content"]):
            target = clean_link_target(link)
            if not target:
                continue
            resolved = name_map.get(normalize(target))
            if resolved is None:
                if not is_history:
                    r.error("broken-link", f"{rel}: [[{link}]] not found")
            elif resolved != rel:
                incoming[resolved].add(rel)
    for rel, inc in incoming.items():
        if not inc and Path(rel).name not in ORPHAN_EXEMPT:
            r.error("orphan", f"{rel}: no incoming [[links]] from other pages")


def check_index(pages: dict, r: Report):
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return
    content = index_path.read_text(encoding="utf-8")
    linked = set()
    for link in re.findall(r"\]\(([^)]+\.md)\)", content):
        if link.startswith("http"):
            continue
        if not (WIKI_DIR / link).exists():
            r.error("index", f"index.md references missing file: {link}")
        linked.add(Path(link).as_posix())
    catalog = [rel for rel in pages if Path(rel).name not in META_PAGES]
    for rel in catalog:
        if rel not in linked:
            r.error("index", f"{rel}: missing from index.md")
    m = re.search(r"Total pages\*\*:\s*(\d+)", content)
    if m and int(m.group(1)) != len(catalog):
        r.error("index", f"index.md: \"Total pages: {m.group(1)}\", actually {len(catalog)}")


def check_tracked_ignored(r: Report):
    """Compliance: tracked files that .gitignore excludes (e.g. raw data committed before the ignore rule)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "-ci", "--exclude-standard"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return
    if out.returncode != 0:
        return
    files = [f for f in out.stdout.splitlines() if f.strip()]
    if files:
        dirs = sorted({f.split("/")[0] + ("/" + f.split("/")[1] if f.count("/") > 1 else "") for f in files})
        r.warn("tracked-ignored", f"{len(files)} file(s) tracked despite .gitignore: {', '.join(dirs[:8])}"
               + (" …" if len(dirs) > 8 else "") + " → git rm --cached")


def print_group(title: str, items: list[tuple[str, str]]):
    by_kind: dict[str, list[str]] = {}
    for kind, msg in items:
        by_kind.setdefault(kind, []).append(msg)
    for kind, msgs in sorted(by_kind.items()):
        print(f"{title} [{kind}] — {len(msgs)}:")
        for msg in sorted(msgs):
            print(f"  {msg}")
        print()


def print_stale(r: Report):
    stale = [m for k, m in r.warnings if k == "stale"]
    stale.sort(key=lambda m: -int(re.search(r"\((\d+) d\.", m).group(1)))
    print(f"Staleness report — {len(stale)} page(s) past review_by")
    for m in stale:
        print(f"  {m}")


def print_stats():
    """Consultation rate from .llm-wiki/.stats.jsonl (written by log_wiki_access.py, PostToolUse hook)."""
    if not STATS_PATH.exists():
        print("No consultation data (.llm-wiki/.stats.jsonl missing — hook hasn't run yet).")
        return
    entries = []
    for line in STATS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not entries:
        print("Consultation log is empty.")
        return
    now = datetime.datetime.now()
    by_path: dict[str, int] = {}
    last_7d = last_30d = 0
    for e in entries:
        by_path[e.get("path", "?")] = by_path.get(e.get("path", "?"), 0) + 1
        try:
            ts = datetime.datetime.fromisoformat(e["ts"])
        except (KeyError, ValueError):
            continue
        age = (now - ts).days
        if age <= 7:
            last_7d += 1
        if age <= 30:
            last_30d += 1
    print(f"Consultation rate — {len(entries)} reads/greps on wiki/** total "
          f"({last_7d} in last 7d, {last_30d} in last 30d)")
    for path, count in sorted(by_path.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {count:>4}  {path}")


def run_lint(argv: list[str]) -> int:
    if "--stats" in argv:
        print_stats()
        return 0

    pages = load_pages()
    name_map, ambiguous = build_name_map(pages)
    r = Report()
    for rel, p in pages.items():
        check_page(rel, p, r)
    check_links(pages, name_map, r)
    check_index(pages, r)
    check_tracked_ignored(r)
    for stem, rels in ambiguous.items():
        r.warn("ambiguous", f"{stem}: {', '.join(rels)}")

    if "--stale" in argv:
        print_stale(r)
        return 0

    print(f"Wiki Lint — {WIKI_DIR}")
    print(f"Pages scanned: {len(pages)}\n")
    print_group("ERROR", r.errors)
    print_group("WARN", r.warnings)

    strict = "--strict" in argv
    failing = len(r.errors) + (len(r.warnings) if strict else 0)
    if not r.errors and not r.warnings:
        print("✅ No issues found.")
    else:
        print(f"Total: {len(r.errors)} error(s), {len(r.warnings)} warning(s)."
              + (" (--strict)" if strict else ""))
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(run_lint(sys.argv[1:]))
