# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is: a project template

`devenv-development` is a **template repository** — a scaffold that new projects are stamped from,
not an application being developed toward its own runtime. The files and directories here are the
skeleton every new project inherits, so when you work in this repo you are editing *the template
itself* (the thing that gets copied), not building a specific product.

Two consequences follow from that:

- **Seed files are placeholders, on purpose.** The empty `main.py`, the empty `README.md`, and the
  bare `pyproject.toml` are starting points for the generated project, not code to flesh out here.
  Keep them minimal and generic.
- **Structure is the product.** The value of this repo is its layout and conventions. When adding to
  the template, prefer things that make sense for *every* new project, and avoid baking in anything
  specific to one downstream use case.

Both halves of the template are now built: the `project/vault/` project-management vault (see below)
and the run-once bootstrap machinery (`install.py` + the `devenv/` package). Keep this file honest:
update it as the template's structure and conventions change.

## Template layout (directory names signal intent)

These files and directories form the skeleton a new project inherits:

- `install.py` — the **run-once installer**. Run it once (`python3 install.py`) right after cloning
  the template into a fresh dir; it transforms the clone in place into a real project. Stdlib-only
  (so it runs before `uv sync`, which it performs itself), destructive (re-inits git, strips
  lineage), so it always prints a dry-run plan and confirms first (`--dry-run` / `--yes` /
  `--name` / `--desc` / `--libs` / `--container` / `--force`). It removes itself on success.
- `main.py` — the **ongoing command router** the generated project keeps: `doctor`, `add-lib
  <domain>`, `container [name]`, `setup <uv|claude|mcp|obsidian>`. Also stdlib-only; a thin
  dispatcher into the `devenv` package.
- `devenv/` — the **scaffolder machinery** (stdlib-only package): `flow.py` (bootstrap steps),
  `prompts.py` (stdlib Q&A), `lineage.py` (sanitize-lineage), `commands.py` (the router's command
  impls), `__init__.py` (`Ctx`, `Runner`, constants). Every side effect goes through `Runner`, so
  `--dry-run` is uniform. **Lifecycle:** ships at the repo root; `install.py` *moves* it into
  `.bootstrap/devenv/` during bootstrap (the "machinery-only" move). `.bootstrap/` can't be a Python
  package (leading dot), so the importable package is always named `devenv`; entry points add the
  right parent to `sys.path`. After bootstrap the control plane holds `devenv/`, `templates/`, and
  the git-ignored `bootstrapped` sentinel.
- `templates/` — the **template sources** the scaffolder stamps (moved into `.bootstrap/templates/`
  on bootstrap). `app/` (project-code scaffold); `libs/<domain>/` building blocks — seed
  implementations for `db` (SQLite helper) and `logs` (configured logger), the other eight domains
  as documented empty slots; `libs/containers/python/` (a stampable Dockerfile + compose). Distinct
  from the vault's *note* templates under `project/vault/vault_infra/templates/`.
- `pyproject.toml` — stdlib-only runtime (`dependencies = []`); optional extras (`ux`, `servers`,
  `db`) to opt into per project, and a `dev` group with `pytest`.
- `README.md` — seed (rewritten per project by `install.py`'s sanitize-lineage step).
- `.python-version` — pins Python 3.13. `.claude/settings.json` — sets `worktree.bgIsolation: none`.
- `.claude/skills/` — the **inherited skill set** a new project ships with (generalized from the
  canonical skills shared across the sibling `~/dev` projects). Six skills, all vault/dev-workflow
  oriented: `new-vault-note` (route a note to the right vault folder; dev-items via the template),
  `project-status-report` and `git-report` (grounded reports saved to `project/vault/notes/`),
  `architecture-doc` (Mermaid "how it works" doc → `wiki/`), `lib-ideas` (capture ideas under
  `libs/<domain>/ideas/`), `terminal-tool` (standalone read-only `rich` report scripts). They live at
  the repo root, so — like `.claude/settings.json` — they survive bootstrap untouched (the flow only
  moves `devenv/`+`templates/` into `.bootstrap/`) and ship to the public template via `publish.py`;
  they're written project-name-agnostic, so `install.py` needs no lineage step for them.
- `project/vault/` — the project-management / documentation vault a new project inherits. It is a
  real Obsidian vault with a working **Bases** board:
  - `Home.md` — map of content.
  - `Dashboards/` — `Dev Items.base` (a Bases board over item frontmatter: Board / Backlog / By
    Bucket / By Cycle views) plus its `Dev Items.md` / `Dashboards.md` host notes.
  - `items/` — dev-item notes (carry `FileType: 🚥 Dev Item` frontmatter so the board picks them up).
  - `vault_infra/templates/` — note templates (`dev-item`, `base-cycle`, `base-release`,
    `base template`). The `dev-item` template is the standout: typed frontmatter + an inline field
    guide. Apply via Obsidian's *Insert template*.
  - `docs/` (feature-facing) · `wiki/` (engineering-facing, incl. `design.md`) · `notes/` (working
    lists) · `logs/` · `versions/` · `periodic/`.
  - `metadata.json` / `config.json` live at the **vault root** (not the repo root) so Obsidian reads
    them and `project-registry` discovers them via its shallowest-file scan. `metadata.json` =
    project self-description (`name`/`version`/`branchVersion`/`cycle`); `config.json` =
    registry/tooling config (`track`/`tags`/`notes`). Schema mirrors `project-registry`'s scanner.

  The PM vault (templates + Bases board) was lifted and generalized from `rosmerta_neo`'s vault; the
  registry schema from the `project-registry` project.

The bootstrap flow (`devenv/flow.py`) maps onto four steps: (1) establish the `.bootstrap/` control
plane (machinery-only move); (2) rename in `pyproject.toml`, `uv sync`, re-init git; (3) apply
templates (stamp `app/`, chosen libs, optional container); (4) sanitize lineage, then write vault
metadata/logs, make the first commit, and drop the sentinel. The design derives from the sibling
`~/dev/cnfg` ("dev_project_setup"), which `devenv-development` restarts; see `cnfg`'s
`project/vault/wiki/design.md` for the fuller rationale (control-plane split, accretion of libs).

## Commands

Python 3.13 managed with [`uv`](https://docs.astral.sh/uv/) (pinned in `.python-version`). Run from
inside this directory:

```bash
python3 install.py --dry-run   # (on a fresh clone) preview the bootstrap, change nothing
python3 install.py             # run-once: transform the clone into a project

uv sync                        # create/refresh .venv and install deps (incl. dev group)
uv run main.py doctor          # health check (also: add-lib <domain>, container, setup <area>)
uv run pytest                  # run the test suite (tests/ — exercises the devenv package)
```

`pytest` is configured via the `dev` dependency group in `pyproject.toml`. Testing note: the
installer is destructive and in-place, so `tests/` only exercises the **non-destructive** units
(prompts parsing, dry-run planning, `doctor`) against temp fixtures; never run `install.py` against
the template repo itself — test it on a throwaway copy.

## Remotes and publishing

This project uses **two remotes**:

- **`origin` → `devenv-dev`** (private) — where development happens. Day-to-day `git push` goes here;
  it holds the full content (this dev vault with its dev-items/logs, `tests/`, `publish.py`).
- **`public` → `devenv-development`** (private for now; intended to go public) — the distributable
  "clone and use" template. It carries a **cleaned** snapshot: devenv-development's own dev-items and
  logs stripped, the vault reset to generic seeds, and `publish.py` removed.

Publish with `python3 publish.py` (`--dry-run` to preview). It exports `HEAD`, cleans it (via
`devenv.lineage.reset_vault` + dropping `publish.py`), and force-pushes a single fresh commit to
`public/main` — the public repo is a curated snapshot, not dev history. Commit to `origin` first;
`publish.py` only ever publishes committed `HEAD`.

## Conventions

Follow the cascading conventions in `~/dev/CLAUDE.md` and `~/CLAUDE.md` (extra-caution home
directory, standard `app/`/`libs/`/`project/` layout). This project is a standalone git repo — run
git/build/test from inside it. Design decisions are recorded in the vault at
`project/vault/wiki/design.md` (not a `project/design/` folder). Since this is a template, decisions
made here propagate to every project stamped from it, so record them deliberately as it evolves.
