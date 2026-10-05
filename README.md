# llm-wiki

A concept for LLM-maintained wikis, building on [Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), plus a template to apply it to individual wikis and keep them up to date.

The idea: instead of re-deriving knowledge from raw sources on every question, an LLM *compiles* it once into a persistent, cross-linked Markdown wiki — with sources, a review lifecycle, and a lint that mechanically enforces the schema.

> **Status: v0.x, experimental.** Ideas and experience reports are welcome as issues.

- **[CONCEPT.md](CONCEPT.md)** — the concept: principles, schema, workflows, distribution, scaling
- **[CHANGELOG.md](CHANGELOG.md)** — versions of the concept
- **[decisions/](decisions/)** — decisions on the concept (ADRs)
- **[research/](research/)** — sources and observations the concept learns from
- **[template/](template/)** — [Copier](https://copier.readthedocs.io/) template for a wiki instance

This repo contains no wiki content. Every instance is its own repo.

## Create a new wiki instance

```bash
pipx install copier            # once
copier copy gh:pzuschlag/llm-wiki ~/repos/my-wiki
cd ~/repos/my-wiki
git init && git config core.hooksPath .llm-wiki/hooks
git add -A && git commit -m "wiki: init from llm-wiki"
```

Copier asks for the name, purpose, language, and domain-specific source prefixes, and writes the answers to `.copier-answers.yml`.

## Lift an instance to a new concept version

Run the **`wiki-upgrade`** skill in the instance, or by hand:

```bash
git checkout -b llm-wiki-upgrade
copier update --skip-answered     # 3-way merge + migrations for the skipped versions
python3 .llm-wiki/lint_wiki.py
# resolve conflicts (conflict markers), commit, pull request
```

## Who owns what

| Managed by the concept (never change by hand in instances) | Belongs to the instance |
|---|---|
| `.llm-wiki/` (CORE.md, lint_wiki.py, log_wiki_access.py, hooks/, migrations/) | `CLAUDE.md`, `wiki.config.yaml` |
| `.claude/skills/wiki-*`, `.claude/settings.json` | `wiki/`, `raw/`, `scripts/`, your own skills |

Improvement ideas from an instance → an issue in this repo, not a local change under `.llm-wiki/`.

## Publish a new concept version

1. Change the template (+ a migration script under `template/.llm-wiki/migrations/` and an entry in `copier.yml` → `_migrations`, if data is affected) and `CONCEPT.md`
2. Add to `CHANGELOG.md`, bump the version in `template/.llm-wiki/CORE.md` and `CONCEPT.md`
3. Run `tests/test_template.sh`
4. Merge, then tag `vX.Y.Z` — Copier uses git tags as versions

## License

- Template, scripts, and tests (`template/`, `tests/`, `copier.yml`): [MIT](LICENSE)
- Concept and documentation (`CONCEPT.md`, `decisions/`, `research/`, `CHANGELOG.md`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse with attribution
