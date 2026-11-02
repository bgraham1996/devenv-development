---
name: architecture-doc
description: Create or refresh an engineer-oriented "how it works under the hood" architecture doc for this project, with Mermaid diagrams (layer map, runtime sequence, data-model class diagram, persistence schema). Use when asked to document the architecture, explain how the system/MVP works for developers, visualize what's going on under the hood, draw diagrams of the codebase, or onboard an engineer. Grounds every diagram in the actual source — never guesses.
---

# Architecture Doc

Produce `project/vault/wiki/architecture.md` that explains, for an engineer, **how the project
actually works** — the layers, the runtime flow of one operation, the data shape, and how state is
persisted — each illustrated with a Mermaid diagram.

This is engineering writing, so it lives in `wiki/` (not `docs/`, which is feature-facing). It is
distinct from three neighbours:

- **`README.md`** — usage / how to run.
- **`CLAUDE.md`** — quick reference for Claude Code.
- **`wiki/design.md`** — the *intended* architecture and open decisions.

`architecture.md` is the *narrative + visual* account of how the **built** code works right now. When
little code exists yet, say so and document what's real; don't draw aspirational diagrams — that's
`design.md`'s job.

## When to use

- "Document how this project / MVP works (for a developer)"
- "Visualize what's going on under the hood" / "draw diagrams of the architecture"
- "Onboard an engineer to this codebase"
- Refreshing the doc after the architecture changed materially.

## Core rule: ground everything in source — never guess

Mermaid diagrams that drift from the code are worse than none. Before writing a single diagram:

1. **Read the actual files** for every component you'll draw — the data models, the orchestration
   layer, the service/API seam, the persistence layer, the entry point. Use the real class names,
   fields, method names, table columns.
2. If you state a dependency arrow, confirm the import exists. If you draw a field, it must be in the
   model. If you draw a DB column, it must be in the schema/DDL.
3. Prefer reading the source over trusting an existing `README`/`CLAUDE.md`/`design.md` — those can be
   stale; the code is truth.

## Workflow

1. **Assess what already exists.** List `project/vault/`, read `README.md`, `CLAUDE.md`, and
   `wiki/design.md`. State plainly what's covered and what's missing. Don't duplicate the README or
   restate design.md's intentions.
2. **Map the layers from code.** Identify each package/module's single concern and the dependency
   direction (usually front-end → orchestration → service → data models, pointing inward). Note
   external boundaries (an API, a DB) and empty/reserved seams (e.g. the empty `libs/*` domains).
3. **Pick the operation to trace.** Find the one central runtime path (e.g. "run `uv run main.py`",
   "stamp a container", "add a lib") and read it end to end so the sequence diagram is exact.
4. **Read the data models and persistence/DDL.** Capture field names, types, relationships, table
   columns, keys.
5. **Write `project/vault/wiki/architecture.md`** using the structure below.
6. **Link it** from `Home.md` under the engineering material, next to `[[design]]`, and from
   `README.md` — use the `new-vault-note` linkage convention so it isn't orphaned.
7. **Flag drift risk.** Diagrams go stale; offer to keep the doc in sync when the architecture changes.

## Frontmatter

Match `wiki/design.md`'s shape:

```yaml
---
type: wiki
subtype: architecture
created: YYYY-MM-DD
tags: [architecture, diagrams]
---
```

## Document structure

Use these sections (drop any that genuinely don't apply; add project-specific ones as needed):

1. **Title + one-line scope** — and a line distinguishing this doc from `README` / `CLAUDE.md` /
   `design.md`, with links to each.
2. **What it is, in one paragraph** — plain-language summary of what the system does and its single
   most important design decision.
3. **Layered architecture** — a `flowchart TD` of packages/modules with dependency arrows; external
   systems as dashed nodes. Follow with a bullet per layer (its one concern). Note empty/reserved seams.
4. **Runtime flow — one <operation>** — a `sequenceDiagram` (`autonumber`) tracing the central path
   through the components, with `Note over` for non-obvious transforms. Call out the key step in prose.
5. **Data model** — a `classDiagram` of core types, fields, relationships. Follow with the rationale
   for the central modelling choice.
6. **Persistence** (if any) — an `erDiagram` of the schema (PK/FK, nullable, what JSON columns hold),
   plus a one-line round-trip description.
7. **Entry / CLI / API surface** — the commands or endpoints and key options.
8. **Comparison tables** where two things are easily confused.

## Mermaid diagram cheatsheet

Renders in both Obsidian and GitHub. Keep diagrams readable (≤ ~12 nodes); split if larger.

- **Layers** — `flowchart TD`; `subgraph` to group tiers; dashed `classDef` for external systems:
  ```
  classDef ext fill:#eee,stroke:#999,stroke-dasharray:4 3;
  class EXT ext;
  ```
  Use `<br/>` for multi-line node labels.
- **Runtime flow** — `sequenceDiagram` with `autonumber`; `actor` for the human, `participant` for
  components; `Note over X: …` for transforms; `-->>` for returns.
- **Data model** — `classDiagram`; `*--` composition, `<|--` inheritance, `<<union>>`/`<<interface>>`
  stereotypes; multiplicities like `"1" *-- "many"`.
- **Schema** — `erDiagram`; `||--o{` one-to-many; mark `PK`/`FK` and note nullable / JSON columns in
  the comment column.

## Gotchas

- Don't let the layer diagram and the prose disagree — generate the bullets from the same reading that
  produced the arrows.
- A "must replay unchanged" constraint, an ON DELETE CASCADE, a stateless-vs-stateful split — these
  *rationale* points are the most valuable part; don't omit them for pure structure.
- Verify every wikilink/relative path you add actually resolves.
- This is engineer-facing: assume the reader can read code, so spend words on *why* and *flow*, not on
  restating obvious field names.
