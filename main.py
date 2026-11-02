#!/usr/bin/env python3
"""Project command router — the ongoing CLI a bootstrapped project keeps.

    uv run main.py doctor               # toolchain + bootstrap-state health check
    uv run main.py add-lib <domain>     # copy a libs/ building block into the project
    uv run main.py container [name]     # stamp a container template
    uv run main.py setup <area>         # re-run a setup slice (uv | claude | mcp | obsidian)

Stdlib-only, like the installer, so it runs on a fresh clone before `uv sync`.
Real logic lives in the `devenv` package; this file is a thin dispatcher.

Unlike the run-once `install.py`, this does **not** bootstrap — on a template
clone that hasn't been installed yet it points you at `install.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Locate the `devenv` package: under .bootstrap/ once bootstrapped, else at the
# repo root (the shipped template). Done before importing it.
_CP = ROOT / ".bootstrap"
if (_CP / "devenv").is_dir():
    sys.path.insert(0, str(_CP))

from devenv import LIB_DOMAINS, Runner, commands, is_bootstrapped  # noqa: E402


def _require_bootstrapped() -> bool:
    if is_bootstrapped(ROOT):
        return True
    print("This project isn't bootstrapped yet — run `python3 install.py` first.")
    return False


def cmd_doctor(_args: argparse.Namespace) -> int:
    return commands.doctor(ROOT)


def cmd_add_lib(args: argparse.Namespace) -> int:
    if not _require_bootstrapped():
        return 1
    return commands.add_lib(ROOT, args.domain, Runner(dry_run=args.dry_run))


def cmd_container(args: argparse.Namespace) -> int:
    if not _require_bootstrapped():
        return 1
    return commands.stamp_container(ROOT, args.template or "python", Runner(dry_run=args.dry_run))


def cmd_setup(args: argparse.Namespace) -> int:
    if not _require_bootstrapped():
        return 1
    return commands.setup(ROOT, args.area, Runner(dry_run=args.dry_run))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="main.py", description="Project command router.")
    parser.add_argument("--dry-run", action="store_true", help="narrate actions, change nothing")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    sub.add_parser("doctor", help="toolchain + bootstrap-state health check").set_defaults(
        func=cmd_doctor
    )

    p_lib = sub.add_parser("add-lib", help="add a libs/ building block")
    p_lib.add_argument("domain", choices=LIB_DOMAINS, help="which libs/ domain")
    p_lib.set_defaults(func=cmd_add_lib)

    p_con = sub.add_parser("container", help="stamp a container template")
    p_con.add_argument("template", nargs="?", help="template name (default: python)")
    p_con.set_defaults(func=cmd_container)

    p_set = sub.add_parser("setup", help="re-run a setup slice")
    p_set.add_argument("area", choices=("uv", "claude", "mcp", "obsidian"), help="which slice")
    p_set.set_defaults(func=cmd_setup)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
