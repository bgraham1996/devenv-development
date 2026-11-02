---
name: terminal-tool
description: Create a small standalone terminal tool — a read-only, rich-powered script (report / inspector / dashboard) run directly via `uv run tools/<tool>.py`, decoupled from the project's main CLI. Use when the user wants a quick command-line utility that prints a formatted report about the project or its data, kept independent of main.py.
---

# terminal-tool

Build a **little standalone terminal tool**: a single-file script that prints a nicely formatted
report to the terminal and is run **directly** — `uv run tools/<tool>.py` — rather than wired into the
project's `main.py` command router.

These tools are **lenses on the project**, not part of its product. Keeping them standalone means they
keep working no matter what the coder does to `main.py` — that independence is the whole point.

## When to use

Reach for this when the ask is a quick, self-contained command-line utility that **observes and
reports**: a structure/LOC inspector, a status/health dashboard, a data summary, a "what changed" diff
view. If instead the feature is a real product subcommand users invoke as part of the app's workflow,
it belongs in the `main.py` router, not here. (The `doctor` command already lives in `main.py` — a
standalone tool is for richer or more specialized read-only reports.)

## Non-negotiable conventions

1. **Standalone, not routed.** Invoked as `uv run tools/<tool>.py`. Do **not** add it to the `main.py`
   argparse router. State this in the module docstring so a future edit doesn't "helpfully" fold it in.
2. **Read-only by default.** Observe and print; never write, move, or delete. If a tool ever needs to
   mutate, that's a deliberate, confirmed exception — say so loudly in the docstring.
3. **Anchored to its own location.** Derive the project root from `Path(__file__).resolve()`, not from
   `cwd`, so it works regardless of where it's invoked. (A tool in `tools/` reaches root with `.parent.parent`.)
4. **`rich` for output.** Use `rich` (`Console`, `Panel`, `Table`, `Tree`, `Text`). `rich` is not a
   default dependency here — it ships in the **`ux` optional extra**. Make sure it's installed first:
   `uv sync --extra ux` (or `uv add rich` to adopt it as a project dep). Unlike the stdlib-only
   `main.py`/`install.py` shims, these tools may assume their deps are synced.
5. **Return an int; `raise SystemExit(main())`.** Exit-code discipline, same as `main.py`.

## Structure pattern

Separate **gathering** from **rendering** so the tool stays testable and easy to extend:

- **Data layer** — plain functions that scan/collect and return data, with `@dataclass` holders for
  any non-trivial record or rolled-up bucket. No printing here.
- **Render layer** — one function per section, each returning a `rich` renderable (a `Table`, `Panel`,
  or `Tree`) built from the gathered data. No scanning here.
- **`main()`** — composes: gather once, then print each section's renderable to a single `Console`.
  Blank `console.print()` between sections for breathing room.

Nice touches: colour-code by category via a small style map; mark empty/placeholder dirs inline (the
`libs/*` slots are the obvious case); add a bold "total" row to summary tables.

## The stdlib-shadow gotcha

A single-file script puts its **own directory on `sys.path[0]`**, so a tool named after a stdlib
module (`inspect.py`, `types.py`, `tokenize.py`, `code.py`, `select.py`…) will **shadow** that module
— and `rich`/`dataclasses` import several of them, so you get a confusing circular-import error at
startup.

- **Prefer** a name that doesn't collide with a stdlib module.
- If a colliding name is wanted anyway, strip the script's own dir from `sys.path` **before any other
  import**, using only `os`/`sys` (which don't pull in the shadowed modules):

  ```python
  import os, sys
  _here = os.path.dirname(os.path.abspath(__file__))
  sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != _here]
  # ... now safe to import dataclasses, rich, etc.
  ```

## Procedure

1. **Confirm scope** with the user: what should it report, and where should it live (default: a
   `tools/` dir at the project root). Pick a `snake_case` filename — check it doesn't shadow a stdlib
   module (see above).
2. **Write the module docstring first**: one-line purpose, the `uv run tools/<tool>.py` invocation,
   "read-only", and the explicit "standalone — do not wire into `main.py`" note.
3. **Ensure deps**: `uv sync --extra ux` (rich lives in the `ux` extra); `uv add <other>` for anything new.
4. **Implement** in the data / render / `main` shape above. Anchor paths to `__file__`.
5. **Run it** (`uv run tools/<tool>.py`) and eyeball the output. Iterate on layout.
6. **Log + document**: append a `~/.claude/worklog.md` entry (file-changing work), and if the tool is
   a lasting part of the project, add a short note via the `new-vault-note` skill (a `wiki/`
   engineering note or a `docs/` usage note).

## Keep this skill alive

When you build a new terminal tool and discover a reusable convention or gotcha not captured here, add
it. After materially changing this skill, refresh its documentation note in `project/vault/wiki/` via
the `new-vault-note` skill so humans can navigate it from Obsidian.
