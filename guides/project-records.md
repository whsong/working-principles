# Guide: Project records

**Applies to:** any project lasting more than a few sessions.

**Last checked:** 2026-11-15.

A project keeps two logs in its repository, by default `docs/decisions.md` and `docs/open-questions.md`. Agents read both at the start of a session and review the open questions at each milestone.

## Decision log

One row per decision. Never delete a row; when a decision is replaced, mark it superseded and add the new one.

```markdown
| ID | Decision | Why | Hardness | Date | Status |
|---|---|---|---|---|---|
| D1 | Results are validated against the game's data files | They are the ground truth | Firm | 2026-11-15 | Active |
```

- **Hardness** is Hard, Firm or Provisional, as defined in the principles.
- **Why** records the reason and, for Provisional decisions, what evidence would overturn it.
- A decision that needs more than a few lines of reasoning gets its own document (an architecture decision record) and the row links to it.

## Open questions

One row per question set aside. A question leaves the list only by becoming a decision.

```markdown
| ID | Question | Blocking? | Working assumption | What would settle it | Raised |
|---|---|---|---|---|---|
| Q1 | Which UI form: web page or desktop? | No | None yet | A prototype of each | 2026-11-15 |
```

- A question that blocks work is put to the owner at once, with background, options and a recommendation.
- A question that does not block gets a working assumption, which is also entered in the decision log as Provisional.
