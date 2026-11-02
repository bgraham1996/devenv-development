---
name: project-status-report
description: Generate a "where are we with this project?" status report grounded in the actual files/git state rather than docs alone, and save it as a dated note in the project vault (project/vault/notes/) so it surfaces in Obsidian. Use when asked where the project stands, for a status snapshot/health check, or to report on progress.
---

# Project Status Report

Produce an honest, evidence-based snapshot of the project and persist it to the vault. The value is
*grounding*: read the real tree, code, and git state — never summarize from `CLAUDE.md` / `README` /
`wiki/design.md` alone, because docs drift ahead of (or behind) the code.

## Where reports are saved

```
project/vault/notes/status-<YYYY-MM-DD>.md
```

One file per report; the date makes the reports a natural time series. If a same-day report exists,
overwrite it.

## How to gather (don't skip — this is the whole point)

Run from the project directory. Gather signal in this order:

1. **Tree shape** — list source files and *directories*, including empty ones:
   ```bash
   find . -type f -name '*.py' -not -path '*/__pycache__/*' -not -path './.git/*' | sort
   find . -type d -not -path '*/__pycache__/*' -not -path './.git/*' | sort
   ```
   Count files per top-level dir — **empty dirs are signal** (intended-but-unbuilt modules; e.g. the
   `libs/*` building-block slots). `uv run main.py doctor` is a fast first read of toolchain + state.
2. **Git state** — `git log --oneline -15` and `git status --short`. A non-zero `git` exit (not yet a
   repo, no commits) is itself a finding, not an error to hide.
3. **Read the working code** — actually read the entry point (`main.py`) and the core modules, enough
   to describe what runs end-to-end vs. what's scaffolding. Quote real symbols/commands.
4. **Loose ends** — empty `README`, TODO fragments, unresolved design questions in `CLAUDE.md` /
   `wiki/design.md` / `notes/todo.md`, missing tests/linter. Cross-check against the **[[Dev Items]]**
   board (`project/vault/items/`) — open items are the project's own statement of what's unfinished.

## Report shape

Mirror a good verbal status answer. Keep it concrete; cite `path:line` where useful. Sections:

- **One-line verdict** — e.g. "Installer + router working end-to-end; libs catalog mostly empty slots."
- **What actually works** — features that run end-to-end, with the commands to invoke them.
- **Architecture** — the real layering/seams as built (not aspirational).
- **What's not built yet** — name the empty dirs / intended modules explicitly.
- **Loose ends** — empty docs, fragments, unresolved design questions, missing tooling.
- **Natural next step** — the single most obvious move, and why.

Be honest about immaturity. "Early but real" beats inflating a stub.

## Frontmatter

```yaml
---
type: note
subtype: status-report
created: YYYY-MM-DD
tags: [status-report]
---
```

After the frontmatter, lead with a `> [!summary]` callout holding the one-line verdict so the report
reads well in Obsidian preview.

## After writing

- Tell the user the vault path written, and link it from `Home.md` (under *Recent work*) if it should
  be navigable — use the `new-vault-note` linkage convention.
- These reports are a time series — when generating a new one, glance at the previous dated report and
  add a "Since last report" line noting what changed, when one exists.
