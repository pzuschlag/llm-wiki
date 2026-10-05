---
name: wiki-query
description: Answer a question from the LLM wiki — via the index and pages, with page references and a note on outdated pages. Use for questions about entities, decisions, or relationships in this wiki domain.
---
<!-- Managed by pzuschlag/llm-wiki — do not change in instances. -->

# Query

1. Read `wiki/index.md` → identify relevant pages. If needed, also `grep -ril "<term>" wiki/`.
2. Read the pages. For every page used, check `status` and `review_by`.
3. Synthesize the answer:
   - with page references (`wiki/projects/x.md`) and, where available, the inline sources
   - call out outdated/superseded pages or a passed `review_by` explicitly, and check the primary source
   - name gaps openly instead of filling them from memory
4. If the answer is durably valuable (synthesis across multiple pages, a recurring question) → save it as a new page (index, cross-links).
5. Log: `## [YYYY-MM-DD] query | <question>`.
