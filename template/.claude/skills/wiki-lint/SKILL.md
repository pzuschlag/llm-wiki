---
name: wiki-lint
description: Health check for the LLM wiki — mechanical lint plus a content review for contradictions, outdated statements, and missing pages. Use on request or regularly (e.g. weekly).
---
<!-- Managed by pzuschlag/llm-wiki — do not change in instances. -->

# Lint

1. Run `python3 .llm-wiki/lint_wiki.py`.
   - Fix **errors** immediately (frontmatter, status, source format, links, orphans, index).
   - Report **warnings** as a backlog, grouped: overdue pages (`stale`), missing/vague sources, ambiguous filenames, tracked-but-ignored files (`tracked-ignored` → compliance, inform the human).
2. Run `python3 .llm-wiki/lint_wiki.py --stats` (consultation rate from `.llm-wiki/.stats.jsonl`, if present) and briefly assess: does the agent read wiki pages mid-task, or only at session start?
3. Content review (sample, focus on recently changed and overdue pages):
   - contradictions between pages (same entity, different facts)
   - statements overtaken by newer sources
   - important terms with no page of their own; missing cross-links
   - append-only files (`log.md`, meeting collections) over ~25k tokens → suggest archiving (`wiki/archive/YYYY-Qn/`)
4. Output: a list of concrete suggestions (page, problem, suggestion). Changes only after approval.
5. Log: `## [YYYY-MM-DD] lint | <summary>`.
