"""Sanitize lineage — make the clone stop being the template.

The riskiest part of the bootstrap: it re-seeds/clears files so the new project
carries no trace that it was stamped from `devenv-development`. Two jobs:

1. **Strip template identity** — rewrite CLAUDE.md / README.md and re-seed the
   vault's narrative notes (Home / docs / wiki) to clean, project-named stubs.
2. **Reset the vault's working content** — empty `items/` and `logs/` and blank
   `notes/todo.md`, so the stamped project starts with an empty board rather than
   inheriting devenv-development's own dev-items and logs. The reusable structure
   (Dashboards, `vault_infra/templates/`) is kept.

It only ever runs *after* the user has confirmed (install.py shows a full dry-run
plan first), and every mutation goes through `Runner`, so a dry-run changes
nothing.
"""

from __future__ import annotations

from pathlib import Path

from . import Ctx, Runner


def reset_vault(ctx: Ctx, runner: Runner) -> None:
    """Reset the vault to a clean seed state: generic notes, empty board.

    Re-seeds the narrative notes (Home / docs / wiki / todo) and empties the
    working folders (`items/`, `logs/`). The reusable structure — Dashboards and
    `vault_infra/templates/` — is untouched. Shared by `sanitize` (bootstrap) and
    the `publish.py` tool (produces the cleaned public template).
    """
    vault = ctx.root / "project" / "vault"

    # Re-seed the vault's narrative notes (full overwrite — robust vs. edits).
    runner.write(vault / "Home.md", _seed_home(ctx))
    runner.write(vault / "docs" / "overview.md", _seed_overview(ctx))
    runner.write(vault / "wiki" / "design.md", _seed_design(ctx))

    # notes/: drop generated working reports (status/git, written there by the
    # status-report and git-report skills) and keep only a freshly seeded todo.md,
    # so dev-repo notes don't leak into a stamped project or the public template.
    _reset_dir(vault / "notes", runner, keep=("todo.md",), gitkeep=False)
    runner.write(vault / "notes" / "todo.md", _seed_todo())

    # Empty the working folders so the board starts clean.
    _reset_dir(vault / "items", runner)
    _reset_dir(vault / "logs", runner)


def sanitize(ctx: Ctx, runner: Runner) -> None:
    """Strip template identity and reset the vault's working content."""
    root = ctx.root

    # 1. Replace repo-level identity files with project seeds.
    runner.write(root / "CLAUDE.md", _seed_claude_md(ctx))
    runner.write(root / "README.md", _seed_readme(ctx))

    # 2. Reset the vault (generic notes + empty board).
    reset_vault(ctx, runner)

    # 3. The run-once installer is single-use lineage — remove it on success.
    runner.remove(root / "install.py")


def _reset_dir(
    path: Path,
    runner: Runner,
    *,
    keep: tuple[str, ...] = (".gitkeep",),
    gitkeep: bool = True,
) -> None:
    """Remove everything in `path` except names in `keep`.

    By default keeps/(re)creates a `.gitkeep` so the folder survives as an empty,
    git-tracked slot (items/, logs/). Pass `gitkeep=False` with a `keep` set for a
    folder that should retain specific files instead (notes/ keeps `todo.md`).
    """
    if path.is_dir():
        for child in sorted(path.iterdir()):
            if child.name in keep:
                continue
            if child.is_dir():
                runner.rmtree(child)
            else:
                runner.remove(child)
    if gitkeep:
        runner.write(path / ".gitkeep", "")


# --------------------------------------------------------------------------- #
# Canonical project seeds (what a freshly stamped project starts with)
# --------------------------------------------------------------------------- #

def _seed_claude_md(ctx: Ctx) -> str:
    return f"""# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## {ctx.name}

{ctx.desc or "_One-line description of this project._"}

Python 3.13 managed with [`uv`](https://docs.astral.sh/uv/). Run from inside this directory:

```bash
uv sync             # create/refresh .venv and install deps
uv run main.py      # ongoing project commands (doctor | add-lib | container | setup)
uv run pytest       # run tests
```

## Layout

- `app/` — project code.
- `libs/` — reusable building blocks (add more with `uv run main.py add-lib <domain>`).
- `project/vault/` — the Obsidian project-management vault (dev-item board + docs/wiki/notes).
- `.bootstrap/` — scaffolder machinery kept out of the project's way (the `main.py` command
  surface dispatches into it). Not application code.

Follow the cascading conventions in `~/dev/CLAUDE.md` and `~/CLAUDE.md`.
"""


def _seed_readme(ctx: Ctx) -> str:
    return f"""# {ctx.name}

{ctx.desc or "_Add your description here._"}

```bash
uv sync
uv run main.py doctor
```
"""


def _seed_home(ctx: Ctx) -> str:
    return f"""# Home

Map of content for **{ctx.name}**'s vault — its project-management and documentation layer.

## Start here

- [[Dashboards]] — the live [[Dev Items]] board (status / backlog / by-area / by-cycle)
- `docs/overview.md` — what this project does (feature-facing)
- `wiki/design.md` — architecture & decisions (engineering-facing)
- `notes/todo.md` — the live working list

## Registry files

`metadata.json` and `config.json` sit at the vault root so Obsidian can read them and
`project-registry` can discover them.
"""


def _seed_overview(ctx: Ctx) -> str:
    return f"""# Overview

{ctx.desc or f"_Feature-facing documentation for {ctx.name}._"}

## Purpose

*One paragraph: what problem does this project solve, for whom?*

## Docs vs. wiki

- **`docs/`** (here) — feature-facing: what the project does and how to use it.
- **`wiki/`** — engineering-facing: architecture, decisions, dev process.
"""


def _seed_design(ctx: Ctx) -> str:
    return f"""---
type: wiki
subtype: design
tags: [design, architecture]
---

# Design

*Engineering-facing design notes for {ctx.name}: architecture, decisions, process.*

## Project-management vault

Dev items are notes carrying `FileType: 🚥 Dev Item` frontmatter (create with the `dev-item`
template in `vault_infra/templates/`); the [[Dev Items]] Obsidian **Bases** board queries them
into Board / Backlog / By Bucket / By Cycle views.
"""


def _seed_todo() -> str:
    return """---
type: note
subtype: working
tags: [todo, working]
---

# Working List

*Quick capture. For anything substantial, prefer a dev-item note in `items/` so it shows up on the
[[Dev Items]] board.*

## Now

- [ ]

## Next

- [ ]
"""
