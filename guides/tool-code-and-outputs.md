# Guide: Tool code and outputs

**Applies to:** any task that writes tool code or produces intermediate outputs on the way to its deliverable. This is the normal case in a non-code project. "Tool code" and "non-code project" are defined in the handbook, Terms.

**Last checked:** 2026-11-16.

## Working folder

A task of some complexity gets a folder of its own. A typical division:

| Subfolder | Holds |
|---|---|
| `docs/` | The project's documents beyond `AGENTS.md` (see `guides/project-records.md`) |
| `tools/` | Tool code |
| `outputs/` | Intermediate outputs, when there are any |

`AGENTS.md` sits at the root of the folder.

## Tool code

- How to clean it up and how freely to refactor it is in the handbook, chapters 3 and 6.
- Every code file opens with a header comment that states what the file is for and how to invoke it.

## Code index

One or two scripts that may be used again are listed in the map in `AGENTS.md`. From the third, create `code-index.md` beside the code and point to it from that map. It answers three questions for the owner and for agents: where a file is, what it does, and how to call it.

- It is a table with one row per code file: the path, the purpose, the invocation.
- A script generates the table from the header comments of the code files, or checks the table against them and fails on a difference. Nobody edits the table by hand.
- Regenerate it in the same change that adds, removes or renames a code file.

No generator ships with this guide. Write one as tool code in the project.

## Intermediate outputs

- Give each kind of output its own subfolder under `outputs/`.
- For a generating task with randomness in it, such as producing images, name every run's output with a sequence number or a timestamp so that no run replaces another (handbook, chapter 6).
- Large or binary outputs stay out of version control (see `guides/git-repository.md`).
