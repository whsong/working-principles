# Guide: Project records

**Applies to:** any project lasting more than a few sessions.

**Last checked:** 2026-11-15.

A project keeps two records in its repository, by default `docs/decisions.md` and `docs/open-questions.md`. Agents read both at the start of a session and review the open questions at each milestone.

## Keep records current and short

- Record only what is in force now, one entry per topic. When a decision changes, replace its entry. Do not keep the superseded entry, a status column or a change log; version control holds the history.
- Write each decision once. If its text already lives in another document (the project's `AGENTS.md`, a scope or design document, an architecture decision record), the entry points there and adds only the reason and the hardness.
- The same holds for every project document: no duplicated statements, no finished to-do lists, no correction banners. Fix a wrong statement in place.
- A long record is hard on both human and agent memory.

## Decisions

```markdown
| Topic | Where it is written | Why | Hardness |
|---|---|---|---|
| Ground-truth order | `AGENTS.md`, Ground truth | The notes are mostly right but not guaranteed | Firm |
```

- **Hardness** is Hard, Firm or Provisional, as defined in the principles.
- **Why** records the reason and, for a Provisional decision, what evidence would overturn it.
- A decision whose text lives nowhere else is written in the entry itself.
- A decision that needs more than a few lines of reasoning gets its own document (an architecture decision record) and the entry points to it.

## Open questions

```markdown
| ID | Question | Blocking? | Working assumption | What would settle it | Raised |
|---|---|---|---|---|---|
| Q1 | Which UI form: web page or desktop? | No | None yet | A prototype of each | 2026-11-15 |
```

- A question that blocks work is put to the owner at once, with background, options and a recommendation.
- A question that does not block gets a working assumption, which is acted on as a Provisional decision.
- A question leaves the list when it is decided or stops mattering.
