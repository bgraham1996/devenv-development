---
name: new-vault-note
description: Create a new Obsidian note in the correct vault folder (docs vs wiki vs notes/items/logs/periodic), with frontmatter and a link back from Home.md. Use when the user wants to add a doc, wiki page, working note, dev-item, log entry, or periodic note to the project vault.
---

# new-vault-note

Add a note to the project's Obsidian vault in the **right folder for its kind**, with consistent
frontmatter, and wire it into the map-of-content (`Home.md`) so it doesn't get orphaned.

The vault lives at `project/vault/`.

## Pick the folder by intent

The split is deliberate — route by what the note *is*, not by guesswork:

- **`docs/`** — **feature-facing**: what the project does, how to use a feature, user reference.
- **`wiki/`** — **engineering-facing**: architecture, design decisions, rationale, process.
- **`notes/`** — general working notes / scratch thinking (also where status & git reports land).
- **`items/`** — a **dev-item**: a discrete tracked feature / bug / chore. These are special — see below.
- **`logs/`** — a dated work-log entry (what happened on a given day).
- **`periodic/`** — daily / weekly periodic notes.

If it's ambiguous between docs and wiki, ask which lens it's written from (user-facing feature vs.
engineering).

## Dev-items are special — use the template

A note in `items/` only shows up on the **[[Dev Items]]** Bases board if it carries the right
frontmatter (`FileType: 🚥 Dev Item`, `Type`, `Status`, `Priority`, `Bucket`, `Cycle`, …). Don't
hand-write that frontmatter — copy the canonical template at
`project/vault/vault_infra/templates/dev-item.md` (or, in Obsidian, *Insert template → dev-item*) and
fill it in. The template's inline field guide documents the allowed values. Give the file a
human-readable title (`Grow the libs catalog.md`), not a kebab slug — it's a board card.

## Procedure

1. Determine the target subfolder above (vault root is `project/vault/`).
2. Choose a filename. Dev-items get a human title; everything else is kebab-case. For `logs/` and
   `periodic/`, prefix with the date (`YYYY-MM-DD-...` or `YYYY-MM-DD ...`); today's date is in context.
3. Create the note:
   - **Dev-item** → from the `dev-item` template (see above).
   - **Everything else** → frontmatter fitting the kind, then a single `# Title` H1 + one-line summary:
     ```
     ---
     type: doc        # or: wiki | note | log | periodic
     created: YYYY-MM-DD
     tags: []
     ---
     ```
4. **Link it from `Home.md`** — add a wikilink under the matching section (dev-items surface on the
   board automatically, but a pointer under *Recent work* is still friendly). Keeps the vault navigable.
5. Preserve Obsidian syntax in any note bodies you touch — wikilinks `[[...]]`, Bases/dataview blocks,
   `tasks`-plugin syntax, templater calls.

## Notes

- Keep `docs/` and `wiki/` from drifting into each other; that separation is the point.
- If a wikilink name might collide across the vault, use the path-qualified form
  `[[docs/overview|overview]]`.
- `metadata.json` / `config.json` live at the vault *root* (not a folder) — they're registry files,
  not notes; don't create notes there.
