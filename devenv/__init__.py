"""devenv — the scaffolder machinery for the devenv-development template.

This package is **stdlib-only**: it is imported by the root `install.py` (run-once
bootstrapper) and `main.py` (ongoing router), both of which must run on a fresh
clone *before* `uv sync` has installed anything.

Lifecycle of this package on disk:

- **Shipped template (pre-bootstrap):** lives at the repo root as `./devenv/`.
- **After bootstrap:** moved into the control plane at `./.bootstrap/devenv/`
  (the "machinery-only" move). `main.py` then imports it from there.

So the import name is always `devenv`; only its parent directory changes. Entry
points locate it by adding the right directory to `sys.path` (see
`machinery_parent`).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# The libs/ building-block domains the scaffolder knows about. Kept in sync with
# the template sources under `templates/libs/` and project/vault/wiki/design.md.
LIB_DOMAINS: tuple[str, ...] = (
    "apis", "caches", "containers", "db", "deploy",
    "logs", "servers", "tests", "utils", "ux",
)

# Hidden control-plane directory the machinery + template sources move into on
# bootstrap. Mirrors the .git / .obsidian / .claude convention for our own tooling.
CONTROL_PLANE = ".bootstrap"

# Run-once sentinel written at the end of a successful bootstrap. Git-ignored:
# it marks local state ("this clone has been turned into a project"), not lineage.
SENTINEL = "bootstrapped"


def control_plane(root: Path) -> Path:
    """The `.bootstrap/` control-plane directory for a project rooted at `root`."""
    return root / CONTROL_PLANE


def sentinel_path(root: Path) -> Path:
    """Path to the run-once `.bootstrap/bootstrapped` sentinel."""
    return control_plane(root) / SENTINEL


def is_bootstrapped(root: Path) -> bool:
    """True once this clone has been turned into a real project."""
    return sentinel_path(root).exists()


def machinery_parent(root: Path) -> Path:
    """Directory to put on `sys.path` so `import devenv` resolves.

    Post-bootstrap the package lives under the control plane; in the shipped
    template it sits at the repo root (already importable when running a root
    script). Returns the control plane when it exists, else the root.
    """
    cp = control_plane(root)
    return cp if (cp / "devenv").is_dir() else root


@dataclass
class Ctx:
    """Everything a bootstrap run needs, threaded through the flow."""

    root: Path
    name: str
    desc: str = ""
    libs: list[str] = field(default_factory=list)
    container: str | None = None
    dry_run: bool = False
    assume_yes: bool = False
    force: bool = False


class Runner:
    """Executes (or, in dry-run, narrates) the filesystem/subprocess side effects.

    Every mutating operation in the bootstrap goes through here so `--dry-run`
    is uniform: in dry-run mode each call prints what it *would* do and changes
    nothing. Read-only probing does not belong here — do that directly.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def _say(self, verb: str, detail: str) -> None:
        prefix = "[dry-run] would " if self.dry_run else ""
        print(f"  {prefix}{verb} {detail}")

    def mkdir(self, path: Path) -> None:
        self._say("create dir", str(path))
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)

    def move(self, src: Path, dst: Path) -> None:
        self._say("move", f"{src} -> {dst}")
        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

    def write(self, path: Path, text: str) -> None:
        self._say("write", str(path))
        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def replace_in_file(self, path: Path, old: str, new: str) -> None:
        """Substring-replace `old` with `new` in a text file (best-effort)."""
        self._say("edit", f"{path} ({old!r} -> {new!r})")
        if not self.dry_run:
            try:
                text = path.read_text()
            except OSError:
                return
            path.write_text(text.replace(old, new))

    def remove(self, path: Path) -> None:
        self._say("remove file", str(path))
        if not self.dry_run and path.exists():
            path.unlink()

    def rmtree(self, path: Path) -> None:
        self._say("remove tree", str(path))
        if not self.dry_run and path.exists():
            shutil.rmtree(path)

    def copytree(self, src: Path, dst: Path) -> None:
        """Copy a directory tree (merging into an existing `dst`)."""
        self._say("copy tree", f"{src} -> {dst}")
        if not self.dry_run:
            shutil.copytree(src, dst, dirs_exist_ok=True)

    def run(self, cmd: list[str], cwd: Path | None = None) -> int:
        """Run a subprocess; return its exit code (0 in dry-run)."""
        self._say("run", " ".join(cmd) + (f"  (cwd={cwd})" if cwd else ""))
        if self.dry_run:
            return 0
        return subprocess.run(cmd, cwd=cwd).returncode
