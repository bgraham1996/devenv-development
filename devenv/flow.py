"""The ordered bootstrap steps the run-once `install.py` orchestrates.

Each step is idempotent where it can be and routes every side effect through
`Runner`, so the whole flow can be executed in dry-run first (that dry-run *is*
the plan the user confirms). Steps map 1:1 onto the original `install.py` sketch.

Import note: `establish_control_plane` moves this very package's directory
(`./devenv/` -> `./.bootstrap/devenv/`). All sibling modules are imported at load
time below, so they are resident in memory before any move happens; nothing
imports a fresh `devenv.*` submodule after that point.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import CONTROL_PLANE, Ctx, Runner, control_plane, sentinel_path
from . import commands, lineage


def preflight(root: Path) -> list[str]:
    """Return a list of blocking problems (empty == good to go). Read-only."""
    problems: list[str] = []
    if shutil.which("uv") is None:
        problems.append("`uv` is not on PATH — install uv first (https://docs.astral.sh/uv/).")
    if shutil.which("git") is None:
        problems.append("`git` is not on PATH.")
    if not (root / "devenv").is_dir() and not (control_plane(root) / "devenv").is_dir():
        problems.append("scaffolder machinery (devenv/) is missing — is this the template?")
    return problems


def establish_control_plane(ctx: Ctx, runner: Runner) -> None:
    """Step 1 — move machinery + template sources into `.bootstrap/` (machinery-only).

    The generated project's files (project/, main.py, pyproject.toml, …) stay at
    the root; only the scaffolder's own machinery is tucked away.
    """
    cp = control_plane(ctx.root)
    runner.mkdir(cp)
    for name in ("devenv", "templates"):
        src = ctx.root / name
        if src.exists():
            runner.move(src, cp / name)


def environment(ctx: Ctx, runner: Runner) -> None:
    """Step 2 — rename the project, sync the env, and re-init git with a clean history."""
    pyproject = ctx.root / "pyproject.toml"
    runner.replace_in_file(pyproject, 'name = "devenv-development"', f'name = "{ctx.name}"')
    if ctx.desc:
        runner.replace_in_file(
            pyproject, 'description = "Add your description here"', f'description = "{ctx.desc}"'
        )

    runner.run(["uv", "sync"], cwd=ctx.root)

    # Strip the template's git history: the clone becomes its own fresh repo.
    runner.rmtree(ctx.root / ".git")
    runner.run(["git", "init", "-q"], cwd=ctx.root)


def apply_templates(ctx: Ctx, runner: Runner) -> None:
    """Step 3 — stamp the standard scaffold from `.bootstrap/templates/`."""
    templates = control_plane(ctx.root) / "templates"

    app_src = templates / "app"
    if app_src.is_dir():
        runner.copytree(app_src, ctx.root / "app")

    for domain in ctx.libs:
        commands.add_lib(ctx.root, domain, runner)

    if ctx.container:
        commands.stamp_container(ctx.root, ctx.container, runner)


def finalize(ctx: Ctx, runner: Runner) -> None:
    """Step 4 — write metadata/logs, make the first commit, drop the sentinel."""
    vault = ctx.root / "project" / "vault"
    runner.write(
        vault / "metadata.json",
        _json({"name": ctx.name, "version": "0.1.0", "branchVersion": "0.1.0-dev", "cycle": "active"}),
    )
    runner.write(
        vault / "config.json",
        _json({"track": True, "tags": [], "notes": ctx.desc or f"{ctx.name} project."}),
    )
    runner.write(
        vault / "logs" / "bootstrap.md",
        f"# Bootstrap\n\nProject `{ctx.name}` created from the devenv-development template.\n",
    )

    runner.run(["git", "add", "-A"], cwd=ctx.root)
    runner.run(["git", "commit", "-q", "-m", f"Initial commit for {ctx.name}"], cwd=ctx.root)

    runner.write(sentinel_path(ctx.root), f"{ctx.name}\n")


def run(ctx: Ctx, runner: Runner) -> None:
    """Execute all steps in order with the given runner (real or dry-run)."""
    establish_control_plane(ctx, runner)
    environment(ctx, runner)
    apply_templates(ctx, runner)
    lineage.sanitize(ctx, runner)
    finalize(ctx, runner)


def _json(obj: dict) -> str:
    import json

    return json.dumps(obj, indent=2) + "\n"
