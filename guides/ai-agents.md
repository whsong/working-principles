# Guide: AI coding agents

**Applies to:** any repository where AI coding agents work (Claude Code, Cursor, Codex, GitHub Copilot and similar).

**Last checked:** 2026-11-15, against the official Claude Code and Cursor documentation. Codex and Copilot details are not verified here.

## Instruction files

- The canonical file is `AGENTS.md` at the repository root. Cursor, Codex, Copilot and Claude Code (v2.1.277 and later, when the repository has no `CLAUDE.md`) read it without any setup. A subdirectory may have its own `AGENTS.md`; the nearest one takes precedence.
- Keep it under 200 lines. It holds only what is specific to the project and cannot be seen from the code:
  - the one command each for set up, test, lint and run;
  - a short map of the architecture and where things live;
  - the project's ground-truth sources;
  - where the decision log and open-questions log are;
  - project rules that have no automatic check yet.
- Leave out what a linter enforces, what an agent already knows about common tools, and anything that restates the working principles.

## Referencing the working principles

Put this near the top of a project's `AGENTS.md`:

```markdown
## Working principles

This project follows the owner's working principles. If "Working Principles: Core" is not already in your context, read it before starting work: https://raw.githubusercontent.com/whsong/working-principles/main/CORE.md

It says when to read the longer handbook and guides in the same repository. This file adds only what is specific to this project.
```

An agent reads a URL only if it follows this instruction and has network access, so loading is likely but not guaranteed. On a machine used regularly, also load the core from a local clone (see Per-machine setup).

## Bridges for tool-specific filenames

- **Claude Code.** Add a `CLAUDE.md` next to `AGENTS.md` whose only content is the line `@AGENTS.md`. This covers versions before v2.1.277 and sessions where native `AGENTS.md` reading is unavailable, and never loads the file twice. Use the import, not a symlink: symlinks need extra privileges on Windows and git may check them out as plain text.
- **Cursor.** Reads `AGENTS.md` natively. Use `.cursor/rules/*.mdc` only for a rule that must attach to particular file patterns (`globs` in the frontmatter).

## Skills

- A skill is a directory with a `SKILL.md` in the open Agent Skills format (agentskills.io). Frontmatter needs `name` (lowercase, hyphens, equal to the directory name) and `description` (what it does and when to use it). Keep `SKILL.md` under 500 lines; put detail in files beside it.
- Put project skills in `.claude/skills/<name>/`. Claude Code scans only that location, and Cursor loads it for compatibility, so it is the one directory both read. Cursor also reads `.agents/skills/`; Claude Code does not.
- Create a skill when a procedure or a failure has repeated, not before.

## Rules that must not be broken

Instruction files are guidance; an agent may decide a line does not apply. A rule with no exceptions needs enforcement outside the model:

- a linter rule, test or CI job where possible, since those bind every agent;
- otherwise a hook in the agent's own configuration, for example a `PreToolUse` or `Stop` hook in `.claude/settings.json` for Claude Code.

Keep the enforced set small. Each check sometimes fires wrongly and must be maintained.

## Per-machine setup

Decide on each machine whether to do this. It makes the core load in every session there, without depending on the agent fetching a URL.

1. Clone `https://github.com/whsong/working-principles` to a directory outside any file-sync folder.
2. **Claude Code:** in `~/.claude/CLAUDE.md`, import the clone's `CORE.md` with an `@` line and state the clone's path, so the handbook and guides can be found.
3. **Cursor:** global rules live in the settings screen (Customize → Rules), not in a file. Paste one sentence there pointing to the clone's `CORE.md`.

A cloud sandbox sees only the repository, so there the URL reference is the only route.
