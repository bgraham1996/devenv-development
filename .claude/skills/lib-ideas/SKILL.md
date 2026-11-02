---
name: lib-ideas
description: Capture and develop functionality ideas for the libs/ building-block domains — add a new idea, or expand/edit/critique an existing one — as structured markdown under libs/<domain>/ideas/. Use when the user wants to brainstorm, record, refine, reconsider, or critique ideas for the shared libs (apis, caches, containers, db, deploy, logs, servers, tests, utils, ux).
---

# lib-ideas

Capture functionality ideas for the `libs/` building blocks **before they become code**, and keep
developing them in place. The `libs/` dir is organised by general **domain**; this skill files an
idea into the right domain and supports three operations: **add** a new idea, **expand** an existing
one, or **critique** it. Ideas accrete here; over time the best ones get built into real code in the
same domain — the accretion loop described in `wiki/design.md`.

## The libs/ domains

File every idea under the domain it belongs to. The menu (the project's standard `libs/` catalog):

- **apis/** — external API clients & integrations.
- **caches/** — caching layers (redis, in-memory, memoization).
- **containers/** — Docker / compose templates & container tooling.
- **db/** — database helpers (sqlite, postgres connections, migrations).
- **deploy/** — deployment / release / environment tooling.
- **logs/** — logging & observability.
- **servers/** — server frameworks & app skeletons (e.g. fastapi).
- **tests/** — test scaffolding, fixtures, harnesses.
- **utils/** — general shared utilities.
- **ux/** — CLI / TUI / user-interaction helpers.

If an idea fits none of these, **ask before adding a new domain folder** — new domains change the
`libs/` menu referenced by `design.md`, the dev-items, and the installer (`devenv.LIB_DOMAINS`), so
they're a deliberate decision, not a side effect.

## Where idea files live

```
libs/<domain>/ideas/<kebab-slug>.md
```

The `ideas/` subfolder keeps thinking separate from the eventual implementation code in
`libs/<domain>/`. Create the `ideas/` folder on first use.

## File format

Frontmatter (keeps ideas queryable across the vault):

```
---
type: lib-idea
domain: db
status: idea          # idea | exploring | critiqued | accepted | rejected | built
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
---
```

Body template:

```
# <Idea title>

> One-line summary.

## What & why
The capability it adds / the problem it solves.

## Proposed shape
Sketch the API surface, key dependencies, rough structure. Pseudocode is fine.

## Open questions
- …

## Discussion
Append-only, newest first. Critiques, alternatives, and revisions go here — dated.
```

## Status lifecycle

`idea` → `exploring` → `critiqued` → `accepted` | `rejected` → `built`. Set `status` to reflect where
the idea actually is; never silently delete an idea — `rejected` with a reason is the record. When an
idea is implemented, set `status: built` and link to the implementing module.

## Operations

**1. Add a new idea**
1. Determine the domain (above). Confirm if ambiguous.
2. Pick a kebab-case slug; create `libs/<domain>/ideas/<slug>.md` with frontmatter (`status: idea`)
   and the body template.
3. Fill **What & why** and **Proposed shape** from the user's input; leave **Open questions** seeded.

**2. Expand / edit an existing idea**
1. Open the target file (search `libs/*/ideas/` if the domain is unknown).
2. Flesh out the relevant section (usually **Proposed shape**), tighten the summary, add open
   questions. Bump `updated`; advance `status` (e.g. `idea` → `exploring`) if warranted.

**3. Critique an existing idea**
1. Append a dated entry to **## Discussion** (newest first) with the critique, alternative, or
   counter-argument. Keep the original text intact — the trail is the point.
2. If the critique changes the verdict, update `status` (`critiqued`, or `rejected`/`accepted`) and
   bump `updated`. State *why* in the discussion entry.

## Notes

- Ideas are **pre-code**: this is for thinking. Real implementation later lives beside the `ideas/`
  folder in the same domain. When an idea is ready to build, `uv run main.py add-lib <domain>` stamps
  the starter layout for that domain.
- Link related ideas with `[[slug]]`; cross-domain links are welcome (e.g. a `db` idea that needs a
  `caches` idea).
- When an idea affects architecture or the build plan, cross-reference `wiki/design.md` /
  `notes/todo.md`, or promote it to a dev-item on the **[[Dev Items]]** board.
- Keep entries concise — an idea file is a seed, not a spec. Promote mature ideas to a proper `wiki/`
  design note via `new-vault-note` if they outgrow this format.
