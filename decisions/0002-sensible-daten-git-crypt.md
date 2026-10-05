---
title: "ADR 0002: Sensitive data in instances — protection via git-crypt"
status: accepted
date: 2026-10-05
---

# ADR 0002: Sensitive data in instances — protection via git-crypt

## Context
Issue #2: a personal wiki should be able to hold pages with sensitive content (e.g. health, finances, relationships). Open question: which protection mechanism, and whether cloud sessions may access it. A self-hosted git server for location-independent access without a third party was also considered — but that would trade a risk that encryption already solves (wrong visibility, a compromised account) for a new one: an additional, internet-reachable service.

## Decision
Instances with sensitive content encrypt their repo — entirely or in sensitive subpaths — with [git-crypt](https://github.com/AGWA/git-crypt), instead of relying on self-hosting or the remote's visibility setting alone. The repo stays an ordinary private remote repo; git-crypt protects the content on top, in case visibility or account access ever fails.

Each instance sets, in its `CLAUDE.md`:
- which paths are git-crypt-encrypted (`.gitattributes`), possibly the whole repo,
- who holds the keys (GPG keys or a symmetric key),
- whether cloud sessions may access the repo — git-crypt decrypts locally on checkout, so cloud access requires the key to be available there too.

This applies to any instance with sensitive topics, not just new ones — existing instances can adopt git-crypt retroactively.

## Alternatives
| Option | Why not (alone) |
|---|---|
| Self-hosted git server | trades a risk encryption already solves (wrong visibility) for a new one (an additional, internet-reachable service) |
| Remote visibility "private" only | doesn't protect against misconfiguration or a compromised account |
| A separate, unencrypted repo per topic | extra effort with no additional protection over git-crypt |

## Consequences
- `git-crypt` must be installed locally; per-instance setup: `git-crypt init`, `.gitattributes` (paths or the whole repo), `git-crypt add-gpg-user` or exporting the symmetric key as a backup.
- Lint and skills operate as usual on the decrypted working tree — no special handling needed in the concept.
- Which topics actually belong in the repo, and how cloud access is used, is each instance's own decision (principle 7), documented in its `CLAUDE.md`.
