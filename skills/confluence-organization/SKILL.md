---
name: confluence-organization
description: "Routine task: organise a Confluence site through the Atlassian connector. Across the spaces the user watches and the pages they link to, find groups of similar or superseded pages and pages that belong together but are neither linked nor filed together, and keep ONE tracker page up to date. Use when the user says Confluence organisation, organise or clean up Confluence pages, similar or duplicate or outdated pages, the Confluence tracker page, or asks to update a Confluence page as part of this routine."
---

# Routine task: organising Confluence pages

This skill is the method. It holds no site, space or page: those are settings, kept outside this skill (section 0).

## 0. Find the settings before any call

1. Decide which project this request belongs to. The instructions of the working folder (AGENTS.md) either describe one project or list several, each with its two settings files: the site settings and the project settings. If the request does not make the project clear, ask. Read both files of that project.
2. If the instructions name no settings, or a needed value is missing: use the connector to discover what it can tell (accessible sites, the user's starred spaces, the personal space), and ask the user for the rest. Offer to write the answers into settings files made from [settings-template.md](settings-template.md).
3. Never guess a site, a project, a parent issue, a space or a page, and never write to one the user has not named.
4. Before the first write of a session, say which project and which parent or page the write goes to.

The project settings name a working folder (`Working folder`). Its `AGENTS.md` holds the background, the current state, the lessons learned and the open questions of this routine for this site. Read its current state and open questions before starting.

The section names used below (`Site`, `Confluence`, `Scope`, `Tracker page`, `Working folder`) are the headings of the settings files.

## 1. The connector

- The connector is the claude.ai Atlassian MCP, second version. Tools that can be called directly: `searchConfluence` (CQL), `getConfluenceContent`, `createConfluenceContent`, `updateConfluenceContent`. For any other operation (`listConfluenceContent`, `listConfluenceSpaces`, `getConfluenceSpace`, `getConfluenceContentAncestors`, `getConfluencePersonalSpace` and others), call `discover` to get its inputs, then run it with `executeRead` or `executeWrite`.
- **Scope.** The watched spaces, and the pages that pages in those spaces link to (one level only). The watched spaces are the spaces the user starred (get the current set each time with the CQL `space in favouriteSpaces()`) minus the exclusion list in `Scope`. An excluded space that still carries a star must be excluded explicitly: add `AND space != "<KEY>"` to the CQL. A page of an excluded space appears only when a page of a watched space links to it.
- **Permissions.** The user can write in some spaces and not in others. This routine is read-only by default: apart from the tracker page, it does not change, move, archive or comment on any page unless the user has explicitly agreed for one specific group of pages.

## 2. The two kinds of problem

1. **Groups of similar pages**: several pages about the same thing (a copy, successive versions, the same guide rewritten in another space). For each group say: which page is current; which are superseded, outdated or apply only to an old product; how the content changed over time; and what to do.
2. **Related pages that are scattered**: pages whose content clearly belongs together (the same flow, the same component, one page is the background of another) but that neither link to each other nor sit next to each other in the page tree.

Record along the way the structural problems of each space: meeting notes mixed with reference pages, deep folders with a single child, untitled pages or pages named "Copy of", empty pages.

## 3. The steps of one run

1. Read the current state in the working folder's `AGENTS.md`. Then read the current content of the tracker page with `getConfluenceContent` (`detail: "full"`, `content_format: "html"`). The user writes decisions and remarks on that page; they must be kept exactly as they are.
2. **Inventory.** The first run is complete; later runs take only the pages changed since the last run (CQL `space in favouriteSpaces() AND type = page AND lastmodified > "<date of the last run>"`, plus the exclusions). How to take the inventory and the limits of the tools are in section 6. Store the result in `artefacts/<date>_<content>/` of the working folder. Give large inventories, the reading and the writing of the tracker page to subagents; the main session takes only the conclusions.
3. **Find candidates**: similar titles, series of versions or dates, the same topic in several spaces, a guide that exists once for an old product and once for a new one.
4. **Confirm by reading the pages.** Start with `detail: "summary"` or `"outline"`; use `"full"` only to compare bodies or to check links between pages. A conclusion reached without reading the body is marked "title only". Meeting notes and weekly reports are not read page by page; they are reported only as a structural problem.
5. **Update the tracker page** (section 4).
6. Update the current state and the lessons learned in the working folder's `AGENTS.md`. Inventory and grouping results go into a dated folder under `artefacts/` and never replace earlier ones.

## 4. The tracker page

- It is written for people, in English unless `Tracker page` names another language. It mentions only what a reader can open (Confluence pages, issues), never files, tools or paths of a local machine.
- There is ONE tracker page (`Tracker page`). Every run updates that same page; no run creates a new one.
- Every reference to a page is a smart link: `<a href="https://<site>/wiki/spaces/<KEY>/pages/<id>" data-card-appearance="inline"></a>`. The body is written as HTML (`body: {"format": "html", "value": ...}`); get the syntax with `executeRead` on `getContentFormatGuide` (`inputs: {"toolName": "createConfluencePage"}`). Do not use Confluence's storage format XML (`<ac:...>`).
- Structure: first the scope, the date of the latest run and the limits of the method; then two tables, "similar page groups" and "related but scattered pages", one row per group, with the columns topic, pages (each marked current, superseded, old product or duplicate), basis (body read, or title only), suggestion, status, and the user's decision; last the structural observations per space and what was not examined.
- **Every page of every group is listed. Nothing is shortened to "and N more".** The tracker page is the only place where the user sees which pages a group holds; an omitted page cannot be known. For the same reason, any count on the page whose members a reader may want to know is followed by the members.
- Group numbers (S1, R1 and so on) are fixed: every group carries an `id` field in the grouping result. When a group is dropped the others keep their numbers, and the dropped groups are listed at the top of the page.
- Status is shown as a status lozenge: `NEW` (found in this run), `OPEN` (reported, waiting for the user's decision), `AGREED` (the user agreed how to handle it), `DONE`, `WON'T DO`. A finished group stays in the table, so that the page is its own history.
- The body is generated from the grouping result `groups.json` by `<python> "${CLAUDE_SKILL_DIR}/tracker_page.py" groups.json --date <date> --note "<limits of this run's method>" --out tracker.html`. The note says how much was read and what rests on titles only; it becomes the note panel at the top of the page. When the scope changes, first make a new `groups.json` from the previous one with `<python> "${CLAUDE_SKILL_DIR}/scope_filter.py"` (its header comment gives the arguments). Give both scripts `--out` instead of redirecting standard output: some shells re-encode redirected output. `<python>` is `py -3` on Windows and `python3` elsewhere; both scripts use the standard library only. The body is tens of kilobytes: have a subagent pass it to the connector unchanged, and have it read the page back and check the numbers of smart links, tables and rows.
- An update merges with what step 1 of section 3 read: the user's decisions and remarks stay word for word. `updateConfluenceContent` needs the `snapshotToken` that the last read returned. Read back after writing. When the page read back holds rich nodes that this skill did not write, stop and ask the user; do not overwrite them.

## 5. Acting on the pages themselves (every group needs the user's agreement first)

Prefer ways that do not move pages, because the user cannot write in many spaces and links to a page are scattered everywhere:

1. Put a note panel at the top of a superseded page that names the current page and links to it; label the page (for example `superseded`, `outdated`, a product name).
2. Add "See also" links between related pages; where it helps, create an index page for the topic that lists the current pages, instead of moving them.
3. In a space where the user cannot write: list the suggestion on the tracker page for the owner of the space, or, after the user agrees, propose a change to the page (`addConfluenceContentSuggestions`; confirm with `discover` that it is available).
4. Archive, move, merge or delete only after the owner of the page has agreed, and note the page's original place first.

Before editing someone else's page, read the original and confirm that every part of it can be written back unchanged. When it holds macros or embedded content that this skill has not written, give the change to the user to make in the web page.

## 6. Limits of the connector, and how to take the inventory

Measured during a complete inventory on 2026-11-13 unless another date is given.

- `listConfluenceContent` returns only id, type, title, status and space id. It has no parent page, dates or author, so it cannot build the inventory.
- Build the inventory with `searchConfluence` called through `executeRead` (not the directly callable tool of the same name, which ignores `expand`): CQL `space = <KEY> AND type = page`, `expand: "content.version,content.ancestors,content.history"`, at most 100 results per call, paged with the cursor. In CQL a live doc is `type = page` with `subType` equal to `live`.
- A batch of 100 results is three to four hundred kilobytes. A result above the output limit is stored as a file by the runtime and can then be parsed by a script; a batch of fewer than about 30 results goes straight into the context. So read every space from both ends (`created` ascending and descending), to avoid a short last batch.
- Selecting `results.content.subType` in `responseFields` makes the whole `content` object of a live doc disappear. Do not select that field.
- `getConfluenceContent` with `detail: "summary"` gives a summary, the word count, the number of sections and the view count. The Markdown conversion of `"full"` loses content on most pages (pictures, attachments and macros are dropped), and a page that holds only pictures shows 0 words. Whether a page is empty cannot be judged from the word count alone.
- There is no operation for "which pages link here". Links between pages can be judged only from the outgoing links of pages whose body was read. A short link (`/wiki/x/...`) does not show its target; it can be decoded locally (base64 of the page id as little-endian bytes) and matched against the inventory.
- The inventory does not contain containers such as folders and whiteboards.
- **A live doc can be updated only node by node with `edits`, not replaced as a whole** (measured on 2026-11-18). `updateConfluenceContent` with `body`, replacing the whole page, was rejected twice as `snapshot_stale` ("The collaborative draft changed ..."), although the token from a fresh read had not changed. With the same token, `edits` (`replaceNode`, `insertNodeBefore`, addressed by a node's `data-local-id`, which is persistent) succeeded at once. So: read the page to get the `data-local-id` of the top-level nodes, split the new body into fragments by top-level node, replace one or a few nodes per call, and use the `data.snapshot.token` that each call returns for the next call. Each large table takes one call; give this to a subagent. Updating node by node is also the right way to keep the user's remarks: only the nodes whose content changed are replaced.
- The `markdown` format loses links (the block that holds a macro disappears as a whole, and the `lossyConversion` flag is not reliable). To extract outgoing links, read `html`.
