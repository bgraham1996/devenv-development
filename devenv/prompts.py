"""Interactive setup Q&A — stdlib `input()` only.

The bootstrap's questions run *before* `uv sync`, so this cannot use `rich` /
`questionary`. A richer TUI can replace this later (post-sync); the parsing
helpers here are kept pure and testable so that swap is cheap.
"""

from __future__ import annotations

from . import LIB_DOMAINS


def _ask(prompt: str, default: str = "") -> str:
    """One text prompt with an optional default shown in brackets."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        answer = ""
    return answer or default


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """A y/n prompt. Blank input takes the default."""
    hint = "Y/n" if default else "y/N"
    answer = _ask(f"{prompt} ({hint})")
    return parse_yes_no(answer, default)


def parse_yes_no(answer: str, default: bool) -> bool:
    """Pure parser for a yes/no answer (blank → default)."""
    answer = answer.strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes", "true", "1")


def parse_libs(answer: str) -> list[str]:
    """Parse a comma/space-separated libs selection into known domains.

    Accepts `all` (every domain) or a list; unknown tokens are dropped. Order is
    normalised to `LIB_DOMAINS` order and de-duplicated.
    """
    answer = answer.strip().lower()
    if not answer:
        return []
    if answer == "all":
        return list(LIB_DOMAINS)
    tokens = {t for chunk in answer.split(",") for t in chunk.split()}
    return [d for d in LIB_DOMAINS if d in tokens]


def gather(default_name: str) -> dict:
    """Run the interactive Q&A and return the collected answers.

    Only used in the interactive path; the non-interactive path (all of
    `--name`/`--desc` provided) skips this entirely.
    """
    print("\nSet up this project (press Enter to accept defaults):\n")
    name = _ask("Project name", default_name)
    desc = _ask("One-line description", "")
    print(f"\nAvailable libs/ building blocks: {', '.join(LIB_DOMAINS)}")
    print("  (seed implementations exist for: db, logs)")
    libs = parse_libs(_ask("Include which libs? (comma-separated, 'all', or blank)", ""))
    container = None
    if ask_yes_no("Add a container template (Dockerfile + compose)?", default=False):
        container = "python"
    return {"name": name, "desc": desc, "libs": libs, "container": container}
