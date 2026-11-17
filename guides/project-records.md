# Guide: Project records

**Applies to:** any project lasting more than a few sessions.

**Last checked:** 2026-11-16.

## `AGENTS.md` is the entry point

A project's documents start from the `AGENTS.md` at its root; how agents load that file is in `guides/ai-agents.md`. It holds what is specific to the project and cannot be seen from the work itself:

- the background: what the project is for and who uses the result;
- the requirements and the acceptance criteria: what done looks like and how it will be checked;
- the phases and the current status: what is finished, what is in progress, what comes next;
- working knowledge: lessons learned and pitfalls already met;
- the one command each for set up, check, build and run;
- a short map of where things live;
- the ground-truth sources;
- the decisions and the open questions, in the formats below;
- project rules that have no automatic check yet. For a code project these include the refactoring policy (handbook, chapter 6).

Leave out what a linter enforces, what an agent already knows about common tools, and anything that restates the working principles.

At the start of a project the agent fills these in from the interview described in the handbook, Part II.

## Splitting a large `AGENTS.md`

A small project keeps everything in `AGENTS.md`. When the file passes about 200 lines, move whole categories into documents of their own, by default under `docs/`, and leave in `AGENTS.md` an index table: every sub-document, what it holds, and when to read it. The decisions and the open questions usually move first, to `docs/decisions.md` and `docs/open-questions.md`. An agent then loads `AGENTS.md` in every session and opens a sub-document only when the task needs it.

## Where the documents are kept

Usually in the repository, with the work they describe, so that both change in the same commit. This is not always right: see "Where each instruction lives" in `guides/ai-agents.md` for the cases where the documents belong outside the repository or above it. Decide per project.

## Keeping the records current

The rules are in the handbook, chapter 8. Applied to these records:

- One entry per topic. When a decision changes, replace its entry.
- No superseded entries, status columns, change logs, finished to-do lists or correction banners.
- If the text of a decision already lives in another document (a scope or design document, an architecture decision record), the entry points there and adds only the reason and the hardness.

## Decisions

```markdown
| Topic | Where it is written | Why | Hardness |
|---|---|---|---|
| Ground-truth order | `AGENTS.md`, Ground truth | The notes are mostly right but not guaranteed | Firm |
```

- **Hardness** is Hard, Firm or Provisional, as defined in the handbook, Part II.
- **Why** records the reason and, for a Provisional decision, what evidence would overturn it.
- A decision whose text lives nowhere else is written in the entry itself.
- A decision that needs more than a few lines of reasoning gets its own document (an architecture decision record) and the entry points to it.

## Open questions

```markdown
| ID | Question | Blocking? | Working assumption | What would settle it | Raised |
|---|---|---|---|---|---|
| Q1 | Which UI form: web page or desktop? | No | None yet | A prototype of each | 2026-11-15 |
```

- A question that blocks work is put to the owner at once.
- A question that does not block gets a working assumption, which is acted on as a Provisional decision.
- A question leaves the list when it is decided or stops mattering. Where its answer is written is in the handbook, Part II.
