"""Tests for the non-destructive units of the `devenv` scaffolder.

The installer transforms a clone in place, so these never run the full flow
against the repo — they exercise the pure helpers and the individual steps
against throwaway `tmp_path` fixtures, relying on `Runner(dry_run=...)` to prove
dry-run changes nothing.
"""

from __future__ import annotations

from pathlib import Path

from devenv import Ctx, Runner, control_plane, is_bootstrapped
from devenv import commands, flow, lineage, prompts


# --------------------------------------------------------------------------- #
# prompts: pure parsers
# --------------------------------------------------------------------------- #

def test_parse_yes_no_default_on_blank():
    assert prompts.parse_yes_no("", default=True) is True
    assert prompts.parse_yes_no("", default=False) is False


def test_parse_yes_no_variants():
    for yes in ("y", "Y", "yes", "YES", "1", "true"):
        assert prompts.parse_yes_no(yes, default=False) is True
    for no in ("n", "no", "0", "nope"):
        assert prompts.parse_yes_no(no, default=True) is False


def test_parse_libs():
    assert prompts.parse_libs("") == []
    assert prompts.parse_libs("all") == list(__import__("devenv").LIB_DOMAINS)
    # unknown dropped, order normalised to LIB_DOMAINS order, de-duplicated
    assert prompts.parse_libs("logs, db, nonsense, db") == ["db", "logs"]
    assert prompts.parse_libs("ux apis") == ["apis", "ux"]


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #

def _make_project(tmp_path: Path) -> Path:
    (tmp_path / "CLAUDE.md").write_text("# template CLAUDE\nthis is a template\n")
    (tmp_path / "README.md").write_text("")
    (tmp_path / "install.py").write_text("# installer\n")
    (tmp_path / "devenv").mkdir()
    (tmp_path / "devenv" / "__init__.py").write_text("")
    (tmp_path / "templates" / "libs" / "db").mkdir(parents=True)
    (tmp_path / "templates" / "libs" / "db" / "__init__.py").write_text("# db\n")
    vault = tmp_path / "project" / "vault"
    (vault / "wiki").mkdir(parents=True)
    (vault / "logs").mkdir(parents=True)
    (vault / "items").mkdir(parents=True)
    (vault / "Home.md").write_text(
        "This vault is the project-management and\n"
        "documentation layer that ships with every project stamped from `devenv-development`."
    )
    (vault / "wiki" / "design.md").write_text("design\n")
    # devenv-development's own working content that must NOT leak into a new project
    (vault / "items" / "old-dev-item.md").write_text("---\nFileType: 🚥 Dev Item\n---\n")
    (vault / "logs" / "old-log.md").write_text("old log\n")
    (vault / "notes").mkdir(parents=True)
    (vault / "notes" / "todo.md").write_text("old todo\n")
    (vault / "notes" / "status-2026-01-01.md").write_text("a dev-repo status report\n")
    return tmp_path


def _ctx(root: Path, **kw) -> Ctx:
    base = dict(root=root, name="demo", desc="a demo", libs=[], container=None)
    base.update(kw)
    return Ctx(**base)


# --------------------------------------------------------------------------- #
# doctor
# --------------------------------------------------------------------------- #

def test_doctor_reports_unbootstrapped(tmp_path, capsys):
    rc = commands.doctor(tmp_path)
    out = capsys.readouterr().out
    assert "bootstrapped" in out
    assert rc in (0, 1)  # unbootstrapped tmp dir fails some checks


# --------------------------------------------------------------------------- #
# lineage: dry-run vs real
# --------------------------------------------------------------------------- #

def test_lineage_dry_run_changes_nothing(tmp_path):
    root = _make_project(tmp_path)
    before = (root / "CLAUDE.md").read_text()
    lineage.sanitize(_ctx(root), Runner(dry_run=True))
    assert (root / "CLAUDE.md").read_text() == before
    assert (root / "install.py").exists()


def test_lineage_real_rewrites_and_removes_installer(tmp_path):
    root = _make_project(tmp_path)
    lineage.sanitize(_ctx(root), Runner(dry_run=False))
    claude = (root / "CLAUDE.md").read_text()
    assert "demo" in claude and "template" not in claude.lower()
    assert "demo" in (root / "README.md").read_text()
    assert not (root / "install.py").exists()
    # vault identity wording neutralised
    assert "devenv-development" not in (root / "project" / "vault" / "Home.md").read_text()


def test_lineage_resets_vault_working_content(tmp_path):
    root = _make_project(tmp_path)
    lineage.sanitize(_ctx(root), Runner(dry_run=False))
    items = root / "project" / "vault" / "items"
    logs = root / "project" / "vault" / "logs"
    # devenv's own dev-items/logs are gone; only .gitkeep remains
    assert not (items / "old-dev-item.md").exists()
    assert not (logs / "old-log.md").exists()
    assert (items / ".gitkeep").exists()
    # the freshly seeded notes/todo exists and is blank-ish
    notes = root / "project" / "vault" / "notes"
    todo = notes / "todo.md"
    assert todo.exists()
    assert todo.read_text() != "old todo\n"  # re-seeded, not the dev-repo copy
    # generated reports (status/git) in notes/ must NOT leak into the new project
    assert not (notes / "status-2026-01-01.md").exists()


# --------------------------------------------------------------------------- #
# steps: establish control plane, add-lib
# --------------------------------------------------------------------------- #

def test_establish_control_plane_moves_machinery(tmp_path):
    root = _make_project(tmp_path)
    flow.establish_control_plane(_ctx(root), Runner(dry_run=False))
    cp = control_plane(root)
    assert (cp / "devenv").is_dir()
    assert (cp / "templates").is_dir()
    assert not (root / "devenv").exists()
    assert not (root / "templates").exists()


def test_establish_control_plane_dry_run_noop(tmp_path):
    root = _make_project(tmp_path)
    flow.establish_control_plane(_ctx(root), Runner(dry_run=True))
    assert (root / "devenv").is_dir()
    assert not control_plane(root).exists()


def test_add_lib_copies_building_block(tmp_path):
    root = _make_project(tmp_path)
    rc = commands.add_lib(root, "db", Runner(dry_run=False))
    assert rc == 0
    assert (root / "libs" / "db" / "__init__.py").is_file()


def test_add_lib_unknown_domain(tmp_path):
    assert commands.add_lib(tmp_path, "nope", Runner(dry_run=False)) == 2


def test_sentinel_roundtrip(tmp_path):
    assert is_bootstrapped(tmp_path) is False
    Runner(dry_run=False).write(control_plane(tmp_path) / "bootstrapped", "demo\n")
    assert is_bootstrapped(tmp_path) is True
