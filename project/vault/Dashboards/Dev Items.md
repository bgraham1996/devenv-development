# Dev Items

Planning board for this project's dev items. New item → create a note in `items/` and apply
the **`dev-item`** template (Obsidian: *Insert template*). All views below read from
[[Dev Items.base]] — open it directly to filter/sort ad-hoc, or use the embedded views here.

> [!tip]- If an embedded view shows as a plain link
> Older Obsidian builds don't render `![[…#View]]` embeds — open [[Dev Items.base]] and switch
> views via its tab bar instead.

> [!note]- Board shows items regardless of folder
> The board filters on the `FileType: 🚥 Dev Item` frontmatter, not the folder, so items can
> live anywhere in the vault. The `dev-item` template itself is excluded by folder
> (`vault_infra/templates`) so it never shows up as a real item.

## Board — grouped by status
*The working board: every item, grouped Backlog → Planned → In Progress → Blocked → Done → Won't Do.*

![[Dev Items.base#Board]]

## Backlog — open items
*Everything not yet Done (or shelved). This is the "what's next" worklist.*

![[Dev Items.base#Backlog]]

## By area (bucket)
*Grouped by area of the codebase — e.g. core · ui · data · api · docs · tech-debt · infra.*

![[Dev Items.base#By Bucket]]

## By cycle / version
*What's slated for each release. Ties into releases and the version cycles.*

![[Dev Items.base#By Cycle]]
