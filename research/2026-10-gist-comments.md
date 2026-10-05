---
title: "Comment thread on Karpathy's LLM-wiki gist — analysis"
date: 2026-10-05
source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
coverage: ~170 comments from 6 windows (Apr 5, Apr 8, Apr 10–11, Apr 30–May 4, Aug 19–Sep 10, Sep 13–23, 2026) plus May 15–Aug 15, 2026 (256 comments reviewed, ~40 with an independent argument or measurement analyzed below, the rest tool pitches); Sep 24–today still not reviewed (the thread keeps growing — last comment at fetch time was 2026-10-05)
---

# Comment thread on Karpathy's gist — analysis (10/2026)

The thread (gist from 2026-04-04) has several hundred comments, roughly two-thirds of them tool pitches. The substantive criticism boils down to six points. What made it into concept v0.1–v0.4 is in the last column.

| Problem | Observation in the thread | Proposed solution | Voices | In the concept |
|---|---|---|---|---|
| Persistent errors, missing provenance | Hallucination becomes "truth" that later pages cite | A source per statement; a lint finding only with a literal quote; a "NOT VERIFIED" status | Shagun0402, kkollsga, frankchu91, sshlg, a-a-k, pradocabreroalejandro (cite with a version pin `file@SHA:lines` instead of a snapshot copy, source stays live in the repo; a deterministic distiller with a provenance header per source type), antondzi-legacy (measured: a compiled wiki answers questions outside its knowledge with high confidence — 12 "hits" on a question the vault never saw; proposes an abstention rule in the schema, never write non-answers back), AbleVarghese (fix as a data model: a citation is a pointer into an immutable source, not a copy — prevents the synthesis from citing itself) | §1.2, §3 (source per statement, prefixes), `status: draft` |
| Outdated/contradictory knowledge | Pages live forever; lint finds conflicts too late | Check contradictions at write time; `superseded` instead of deleting; valid-from vs. known-since | crajah, kostey, gowtham0992, azaylamba, pursultani & demartinogiuseppe (long exchange: in subjective domains — literary criticism, philosophy — contradiction is content, not a defect; lint there should check for *missing* contradictions; a contradiction should be its own page with status/poles/resolution attempts, not just a typed edge), hmbseaotter (three-tier severity — soft/scope-mismatch/hard; commit gate purely via grep, no LLM, scales to any size; periodic lint stays the only expensive pass) | §1.3–1.4, ingest contradiction check, `review_by`, history |
| Scaling beyond Markdown | Index upkeep, duplicates, API cost from a few hundred pages | SQLite/graph index under Markdown; BM25 instead of vectors only; L1/L2 split | mpazik, QipengGuo, arpitnath, MehmetGoekce, distorx (production instance, ~7,500 notes, FTS5 trigram + embeddings, ~0.07s keyword / ~1.1s semantic, content-hash integrity guard against drift — confirms the tier-2 recommendation with real numbers) | §7 scaling tiers |
| Agent doesn't consult the wiki | The wiki is only read at session start | explicit triggers; lessons in tool descriptions; measure the consultation rate | orcosto-lab | §4 consultation rules (measuring: now implemented, see v0.3.0) |
| Format drift | Models/sessions write frontmatter inconsistently | Enforce the schema via a script | securityguy, sidleo, distorx, blurman-ai ("lint isn't optional" — confirmation, no new angle) | §5 lint + pre-commit hook |
| Missing benchmarks | No independent comparison against RAG | blurman-ai (the only real A/B measurement in the window: a 28-page code wiki brings *nothing* over grep at the same token count; only a condensed one-page map brings 2–4x fewer calls/tokens — the pattern only pays off when a page *compresses* scattered facts, not for small greppable files), lucianfialho (Neo4j variant: graph traversal 6/6 vs. flat RAG 4/6 on multi-hop questions; entity-resolution F1 0.667→1.000 with a two-stage embedding+LLM check) | — | open |

**New in this window — knowledge contradicts reality, not itself**: lint checks notes against notes; if the system being described (code, state) changes independently, the contradiction goes undetected (example: docs claim a permission check, code has unconditionally returned `true` all along). Proposed: anchor statements about code to file+line, flag on code change; for state or cross-service decisions with no code anchor, this stays open. Voices: pollockchris083-arch, tonydzi.

**Tools**: borrow ideas, don't install the tools (compliance, maturity, self-promotion). Candidate for tier 2: local full-text search (SQLite FTS5/BM25, e.g. qmd).

**Open for later versions**
- Measure the consultation rate (how often does the agent read the wiki mid-task?) — **done**, see CHANGELOG v0.3.0
- Track "valid from" and "known since" separately (crajah)
- A "counterarguments & data gaps" section per page (localwolfpackai)
- Multiple agents/sessions writing concurrently: a git merge resolves only textual, not semantic conflicts (two agents phrase the same fact differently → a clean merge, a duplicate in the wiki); the fix is data modeling (append-only, one writer per file/section), not merge mechanics — dedup via a stable citation identity rather than text similarity (watsonrm)
- An abstention threshold: the agent must be able to say "no confident answer" instead of synthesizing from weak relevance; such non-answers should never be written back (antondzi-legacy)
- Team governance with multiple humans: a secrets/PII check in the diff before commit, steward approval for new entities, visibility via a path rule (sturlese) — the concept currently assumes a single human

Further responses to the gist: [LLM Wiki v2 (rohitg00)](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2), [four structural gaps (V-interactions)](https://gist.github.com/V-interactions/a0d2a62c1b16d1fecf1bd81e8f611fba), [ednawnika, "The LLM Wiki Is Real. The Interesting Part Is What You Attach to It"](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6308636#gistcomment-6308636) (a reflective essay — Vannevar Bush reference, decisions as accumulated knowledge — not a tool pitch), [pollockchris083-arch, counterentry/ESSAY.md](https://github.com/pollockchris083-arch/counterentry/blob/main/ESSAY.md) (basis for the new row above, explicitly marks what's specified vs. built).
