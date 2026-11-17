# working-principles

The owner's working principles for projects done with AI agents. Read `CORE.md` before working here; it applies to this repository as to any other project.

This is a non-code project. The deliverable is the documents; `tools/` holds tool code.

## Map

| Path | Holds |
|---|---|
| `CORE.md` | The short version, loaded into every session on the owner's machines |
| `HANDBOOK.md` | The long version, with reasons and examples |
| `guides/` | Concrete tools, defaults and templates, one kind of project each |
| `tools/check_consistency.py` | The check below |

## Check

```
python tools/check_consistency.py
```

Run it before reporting a change as finished. It compares the version lines, the principle titles and the list of guides across the documents.

## Rules for editing

- `HANDBOOK.md` governs. `CORE.md` states each handbook rule in one line. Change both in the same change, and raise the version line in both. The check does not compare the wording of the rules; that is done by reading.
- State each rule once. A guide points to the handbook chapter and adds only what is concrete.
- Change a guide's "Last checked" date only after checking its tool facts against the official documentation again.
- The repository is public, so everything in it is written in English.
- A fact about a named tool comes from that tool's official documentation, not from memory.
