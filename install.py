#!/usr/bin/env python3
"""devenv-development — run-once installer.

Run this **once**, right after cloning the template into a fresh directory, to
turn the clone into a real, configured project:

    python3 install.py              # interactive
    python3 install.py --dry-run    # show the full plan, change nothing
    python3 install.py --yes --name my-project --desc "..."   # non-interactive

Invoke with `python3`, not `uv run` — this script is **stdlib-only** so it runs
before any dependencies are installed, and it performs `uv sync` itself as one of
its steps. It is destructive and transforms the clone **in place** (re-inits git,
strips the template's lineage), so it always prints a dry-run plan and asks for
confirmation before touching anything (unless `--yes`). On success it tucks the
scaffolder machinery into `.bootstrap/` and removes itself.

Real logic lives in the `devenv` package; this file is the thin entry point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# `devenv` ships at the repo root in the template; after bootstrap it lives under
# `.bootstrap/`. install.py is normally gone post-bootstrap, but `--force` (or a
# copied-back installer) must still import it from there and refuse gracefully.
_CP = ROOT / ".bootstrap"
if (_CP / "devenv").is_dir():
    sys.path.insert(0, str(_CP))

from devenv import Ctx, Runner, is_bootstrapped  # noqa: E402
from devenv import commands, flow, prompts  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="install.py",
        description="Run-once installer: turn this template clone into a fresh project.",
    )
    p.add_argument("--name", help="project name (default: the directory name)")
    p.add_argument("--desc", default="", help="one-line project description")
    p.add_argument("--libs", default="", help="libs to include, comma-separated or 'all'")
    p.add_argument("--container", help="container template to stamp (e.g. python)")
    p.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    p.add_argument("--force", action="store_true", help="bootstrap again even if already done")
    return p


def _resolve_config(args: argparse.Namespace) -> dict:
    """Collect project settings — non-interactive when --name is given, else ask."""
    if args.name:
        return {
            "name": args.name,
            "desc": args.desc,
            "libs": prompts.parse_libs(args.libs),
            "container": args.container,
        }
    answers = prompts.gather(default_name=ROOT.name)
    # Flags still override what the interactive pass collected, when provided.
    if args.libs:
        answers["libs"] = prompts.parse_libs(args.libs)
    if args.container:
        answers["container"] = args.container
    return answers


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Refuse to re-bootstrap an already-finished project unless forced.
    if is_bootstrapped(ROOT) and not args.force:
        print("This clone is already bootstrapped. Re-run with --force to bootstrap again.")
        return 1

    problems = flow.preflight(ROOT)
    if problems:
        print("Cannot bootstrap — fix these first:")
        for pr in problems:
            print(f"  - {pr}")
        return 1

    cfg = _resolve_config(args)
    ctx = Ctx(
        root=ROOT,
        name=cfg["name"],
        desc=cfg["desc"],
        libs=cfg["libs"],
        container=cfg["container"],
        dry_run=args.dry_run,
        assume_yes=args.yes,
        force=args.force,
    )

    # Always show the plan first by executing the whole flow in dry-run.
    print(f"\nPlan to bootstrap '{ctx.name}' in {ROOT}:")
    flow.run(ctx, Runner(dry_run=True))

    if args.dry_run:
        print("\nDry run only — nothing changed.")
        return 0

    if not args.yes:
        try:
            reply = input("\nProceed? This re-inits git and rewrites files. (y/N): ").strip().lower()
        except EOFError:
            reply = ""
        if reply not in ("y", "yes"):
            print("Aborted — nothing changed.")
            return 1

    print("\nBootstrapping…")
    flow.run(ctx, Runner(dry_run=False))

    print("\nSelf-check:")
    commands.doctor(ROOT)
    print(f"\nDone. '{ctx.name}' is ready — try `uv run main.py doctor`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
