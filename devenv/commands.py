"""The ongoing command surface — what `main.py` exposes after bootstrap.

`doctor`, `add-lib`, `container`, and `setup`. These are plain functions taking a
project root and a `Runner`; `main.py` wires them to argparse. `add_lib` and
`stamp_container` are also called by the bootstrap flow when the user opts into
libs/container at install time.

Stdlib-only, like everything in this package.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from . import LIB_DOMAINS, Runner, control_plane, is_bootstrapped


def templates_dir(root: Path) -> Path:
    """Where the template sources live — under the control plane once bootstrapped."""
    cp = control_plane(root) / "templates"
    return cp if cp.is_dir() else root / "templates"


def doctor(root: Path) -> int:
    """Health check: toolchain + bootstrap state. Read-only; returns 0 if healthy."""
    ok = True

    def check(label: str, good: bool, detail: str = "") -> None:
        nonlocal ok
        ok = ok and good
        mark = "ok " if good else "FAIL"
        print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))

    print("devenv doctor:")
    check("uv on PATH", shutil.which("uv") is not None)
    check("git on PATH", shutil.which("git") is not None)
    check("python >= 3.13", sys.version_info[:2] >= (3, 13), sys.version.split()[0])
    check("bootstrapped", is_bootstrapped(root))
    check("control plane", (control_plane(root)).is_dir(), str(control_plane(root)))
    check("venv present", (root / ".venv").is_dir())
    check("git repo", (root / ".git").is_dir())
    check("vault present", (root / "project" / "vault").is_dir())
    return 0 if ok else 1


def add_lib(root: Path, domain: str, runner: Runner) -> int:
    """Copy the `libs/<domain>` building block from template sources into the project."""
    if domain not in LIB_DOMAINS:
        print(f"unknown lib domain '{domain}'. Known: {', '.join(LIB_DOMAINS)}")
        return 2
    src = templates_dir(root) / "libs" / domain
    if not src.is_dir():
        print(f"no template source for libs/{domain} (looked in {src}).")
        return 1
    dst = root / "libs" / domain
    if dst.exists() and any(dst.iterdir()):
        print(f"libs/{domain} already exists and is non-empty — leaving it untouched.")
        return 0
    runner.copytree(src, dst)
    return 0


def stamp_container(root: Path, template: str, runner: Runner) -> int:
    """Stamp a container template (Dockerfile + compose) into the project root."""
    src = templates_dir(root) / "libs" / "containers" / template
    if not src.is_dir():
        available = _list_dir(templates_dir(root) / "libs" / "containers")
        print(f"no container template '{template}'. Available: {', '.join(available) or '(none)'}")
        return 1
    runner.copytree(src, root)
    return 0


def setup(root: Path, area: str, runner: Runner) -> int:
    """Re-run a single setup slice. `uv` is real; the rest are informative stubs."""
    if area == "uv":
        return runner.run(["uv", "sync"], cwd=root)
    print(f"[setup:{area}] not implemented yet — would (re)run the '{area}' setup slice.")
    return 0


def _list_dir(path: Path) -> list[str]:
    try:
        return sorted(p.name for p in path.iterdir() if p.is_dir())
    except OSError:
        return []
