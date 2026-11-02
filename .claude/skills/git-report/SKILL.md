---
name: git-report
description: Convert git activity — a push, a merge, or a range of commits — into a human-readable markdown report saved into the project vault (project/vault/notes/) so repo work surfaces in Obsidian. Use when asked to "write up", "document", "make a report/changelog of" a push/merge/release/commits, or to summarize what landed over some range. Grounded in real `git` output and diffs, not commit subjects alone.
---

# Git → Vault Report

Turn what actually happened in the git repo into a readable markdown note in the vault. The value is
**grounding + synthesis**: read the real commits *and diffs*, then group them into themes a human
would recognize — not just a flat reprint of `git log`.

`cd` into the project root before any `git` command. A non-zero `git` exit is a finding to report,
not an error to hide.

## Where reports are saved

```
project/vault/notes/git-<kind>-<YYYY-MM-DD>.md
```

`<kind>` is one of `commits`, `push`, `merge`, `release`. The date makes the reports a natural time
series. If a same-name file exists, append `(2)` rather than overwriting a distinct event.

## Step 1 — establish what to report on

Ask only if genuinely ambiguous; otherwise infer from the request:

- **commits / range** — a span of work: `<from>..<to>` (default `@{u}..HEAD`, or last N with `-n`).
- **push** — what just left local for the remote: `<remote>/<branch>..HEAD` *before* the push, or
  `<old>..<new>` from the reflog after.
- **merge** — a specific merge commit `<M>`; its two sides are `<M>^1` (base) and `<M>^2` (branch).
- **release** — commits between two tags: `<prev-tag>..<tag>`.

Confirm the repo path and range in one line before gathering if either is uncertain.

## Step 2 — gather (don't skip; this is the grounding)

Run from the repo directory.

```bash
git rev-parse --abbrev-ref HEAD            # branch
git remote -v | head -1                    # remote (for push/merge context)

# Commit list for the range (subjects + author + date)
git log --pretty='%h%x09%an%x09%ad%x09%s' --date=short <RANGE>

# Diffstat: scope of change
git diff --stat <RANGE>
git diff --shortstat <RANGE>               # one-line files/ins/del totals

# Who & how much
git shortlog -sn <RANGE>

# READ the actual changes to write themes (sample meaningful diffs, skip lockfiles)
git log --stat <RANGE>
git diff <RANGE> -- <a few key paths>      # read real hunks for the summary
```

Kind-specific extras:

- **push:** `git log <remote>/<branch>..HEAD --oneline` (pre-push), or `git reflog show <branch> -5`
  to recover `<old>..<new>` after the fact.
- **merge:** `git show --stat <M>`; `git log --oneline <M>^1..<M>^2` (what the branch added).
- **release:** `git tag --sort=-creatordate | head`; `git log <prev>..<tag>`.

**Read enough diff to describe *what changed and why*, not just titles.** Quote real symbols /
`path:line` where it sharpens the summary. Group commits by theme (feature, fix, refactor, infra,
docs) — the synthesis is the point.

## Step 3 — report shape

```markdown
# <Project> — <kind> report (<YYYY-MM-DD>)

> [!summary] <one line: what landed, e.g. "12 commits — bootstrap installer + router">

**Branch:** <branch>  ·  **Range:** `<from>..<to>`
**Scope:** N commits · M files · +X / −Y lines · authors: …

## Highlights
- The 2–5 changes that actually matter, in plain language (grouped by theme).

## Commits
| Hash | Subject | Author | Date |
|------|---------|--------|------|
| `abc1234` | … | … | YYYY-MM-DD |

## Files touched
- Top changed paths (from `--stat`), with a word on each cluster. Note new/deleted files.

## Notes
- Merges: branches joined, conflicts resolved, merge commit hash.
- Risks / follow-ups / anything unfinished or worth flagging.
```

Drop sections that don't apply. Be honest about scope — "small fix-up push" beats inflating it.

## Step 4 — frontmatter

```yaml
---
type: note
subtype: git-report
created: YYYY-MM-DD
git_range: <from>..<to>
tags: [git-report]
---
```

## Step 5 — after writing

- Print the vault path written; link it from `Home.md` if it should be navigable
  (`new-vault-note` linkage convention).
- If a prior git report exists, add a one-line "Since last report" pointer.
- Don't `git push`/commit anything yourself — this skill only *reports* on git state.
