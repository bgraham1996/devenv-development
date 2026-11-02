# devenv-development

A **template repository for starting new dev projects**. Clone it into a fresh directory, run it
once, and the clone transforms itself into a configured project — code scaffold, reusable `libs/`,
an Obsidian project-management vault, and an ongoing command CLI, all set up together.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) and Python ≥ 3.13 already installed.
- `git`.

That's the only chicken-and-egg seam: everything else flows from one command.

## Start a new project

```bash
git clone <this-repo-url> my-new-project
cd my-new-project

python3 install.py --dry-run        # preview the whole plan — changes nothing
python3 install.py                   # run it for real (interactive; asks name/desc/libs)
```

Run it with **`python3`, not `uv run`** — `install.py` is stdlib-only so it runs before any
dependencies are installed, and it performs `uv sync` itself.

Non-interactive:

```bash
python3 install.py --yes --name my-new-project --desc "what it does" --libs db,logs
```

Flags: `--dry-run`, `--yes` (skip confirm), `--name`, `--desc`, `--libs` (`all` or comma-separated),
`--container <name>`, `--force`.

### What `install.py` does (once)

It is **destructive and transforms the clone in place**, so it always prints a dry-run plan and asks
for confirmation first. In order:

1. Moves the scaffolder machinery into a hidden `.bootstrap/` control plane (your project's files
   stay at the root).
2. Renames the project in `pyproject.toml`, runs `uv sync`, and re-inits git with a clean history.
3. Stamps the `app/` scaffold, the `libs/` building blocks you chose, and an optional container.
4. Strips the template's identity (rewrites `CLAUDE.md`/`README.md`, re-seeds the vault's notes,
   clears the dev-item board) and **removes `install.py`**.
5. Writes the vault's `metadata.json`/`config.json`, makes the first commit, and marks the project
   bootstrapped.

## Ongoing commands

After bootstrap, `main.py` is the project's CLI (stdlib-only; `uv run` works too):

```bash
uv run main.py doctor               # toolchain + project health check
uv run main.py add-lib <domain>     # copy a libs/ building block in (db, logs, apis, …)
uv run main.py container [name]     # stamp a container template (default: python)
uv run main.py setup <area>         # re-run a setup slice: uv | claude | mcp | obsidian
```

## What a new project looks like

```
my-new-project/
  main.py            # the command router above
  app/               # your code
  libs/              # reusable building blocks (grow with `add-lib`)
  project/vault/     # Obsidian PM vault: a "Dev Items" Bases board + docs/wiki/notes
  .bootstrap/        # scaffolder machinery (kept out of the way)
  pyproject.toml  CLAUDE.md  README.md
```

The `project/vault/` is a working Obsidian vault: create a dev-item from the `dev-item` template and
it appears on the **Dev Items** board automatically (no code — the board is Obsidian Bases over
frontmatter). `metadata.json`/`config.json` live at the vault root so Obsidian reads them and the
`project-registry` tool can discover the project.

## Developing the template itself

Working *on* devenv-development (not using it)? See `CLAUDE.md` for the layout and `project/vault/`
(`wiki/design.md`, the [[Dev Items]] board) for the architecture and backlog. Tests:

```bash
uv sync
uv run pytest
```

> Note: `install.py` rewrites this `README.md` during bootstrap, so a stamped project starts with a
> minimal project README rather than these template instructions.
