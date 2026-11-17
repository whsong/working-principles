# Guide: AI coding agents

**Applies to:** any project where AI coding agents work (Claude Code, Cursor, Codex, GitHub Copilot and similar).

**Last checked:** 2026-11-16, against the official Claude Code and Cursor documentation. Codex and Copilot details are not verified here.

## The project instruction file

- The canonical file is `AGENTS.md` at the project root. Cursor, Codex, Copilot and Claude Code read it without any setup. What it holds, and how to split it when it grows, is in `guides/project-records.md`.
- A subdirectory may have its own `AGENTS.md` for rules that hold only there, for example the conventions of `frontend/` and those of `backend/`. Cursor combines it with the files of the parent directories, the more specific taking precedence. Claude Code loads it when it first reads a file in that subdirectory. Module rules therefore stay out of the context until they are needed.

## No project-level `CLAUDE.md`

- A new project does not create a `CLAUDE.md`. In an existing project, move whatever its `CLAUDE.md` holds into `AGENTS.md` and delete the file.
- The deletion is required, not cosmetic. Claude Code reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or in any directory above it. One leftover file, including one in a parent folder, silently stops `AGENTS.md` from loading.
- This needs Claude Code v2.1.281 or later. Direct reading arrived in v2.1.277, and until v2.1.281 some sessions (Amazon Bedrock, telemetry disabled) still read `CLAUDE.md` only. It is also unavailable when the built-in plugin that reads `AGENTS.md` has been disabled, and in some cases in the first session after upgrading from v2.1.276 or earlier.
- To check: an interactive session prints a line such as `no CLAUDE.md found; AGENTS.md loaded: <path>` when it starts.
- The user-level file `~/.claude/CLAUDE.md` is a different thing. It belongs to the personal level (see Per-machine setup), stays, and does not stop `AGENTS.md` from loading.

## Where each instruction lives

The principle is in the handbook, chapter 10. This table is one layout that fits a single repository worked on by one person or one team.

| Level | What belongs there | Where it is kept | In the project's repository? |
|---|---|---|---|
| Organisation | Rules every member must follow: security, compliance, company standards | Installed by administrators. Claude Code: a managed policy file such as `C:\Program Files\ClaudeCode\CLAUDE.md` or `/etc/claude-code/CLAUDE.md`. Cursor: Team Rules in the dashboard | No |
| Personal | Communication preferences, working principles, skills useful in every project, anything that contains local absolute paths or refers to personal credentials | The home directory (`~/.claude/`), or a repository of its own such as this one, divided into general principles and personal preferences. Cursor: User Rules in the settings screen | No |
| Project | Build and test commands, architecture, conventions, the project's records, skills written for this project | `AGENTS.md` at the root, `.claude/skills/` | Usually yes |
| Subdirectory | The technology and conventions of one module | `<directory>/AGENTS.md` | Same as the project |
| Plugin or skill | The procedure for one kind of task, loaded only while doing it | A skill directory, at the project or the personal level, or a plugin that packages several | Depends on which level it serves |

Project-level files kept in the repository are executable documentation and are versioned like code and CI configuration.

Situations where this layout does not fit:

- **Several related repositories worked on together.** No single repository can hold what is true across all of them. Put the shared instructions in an `AGENTS.md` in the parent folder from which the agent is started (Claude Code loads every `AGENTS.md` in the working directory and the directories above it), or in a repository of their own.
- **A repository that belongs to others, or a public repository with private notes.** Keep the project's documents outside the repository.

Decide per project, and say in the file the agent loads first where the rest is.

## Personal instructions for one project

Sometimes one person wants an instruction in one project without committing it, for example to concentrate on debugging one module.

- If it is temporary, say it in the conversation.
- Otherwise write it in a file whose name carries `.local`, such as `AGENTS.local.md`. The suffix tells a reader that the file is not committed (handbook, chapter 3, Names carry the meaning). What keeps it out of commits is an entry in the project's `.gitignore`, in the personal global ignore file, or in the repository's `.git/info/exclude`; the last two leave the project's `.gitignore` untouched.
- Whether an agent loads such a file by itself is a separate matter:
  - Claude Code loads `CLAUDE.local.md` but not `AGENTS.local.md`. A `CLAUDE.local.md` stops `AGENTS.md` from loading (see above) unless Claude Code's Project instructions setting is `claude-md-and-agents-md`, which loads both.
  - The Cursor documentation mentions no local rule file.
  - A file that the agent does not load by itself has to be named to the agent at the start of the session.

## Referencing the working principles

Put this near the top of a project's `AGENTS.md`:

```markdown
## Working principles

This project follows the owner's working principles. If "Working Principles: Core" is not already in your context, read it before starting work: https://raw.githubusercontent.com/whsong/working-principles/main/CORE.md

It says when to read the longer handbook and guides in the same repository. This file adds only what is specific to this project.
```

An agent reads a URL only if it follows this instruction and has network access, so loading is likely but not guaranteed. On a machine used regularly, also load the core from a local clone (see Per-machine setup).

## Skills

- A skill is a directory with a `SKILL.md` in the open Agent Skills format (agentskills.io). Frontmatter needs `name` (lowercase, hyphens, equal to the directory name) and `description` (what it does and when to use it). Keep `SKILL.md` under 500 lines; put detail in files beside it.
- Put project skills in `.claude/skills/<name>/`. Claude Code scans only that location, and Cursor loads it for compatibility, so it is the one directory both read. Cursor also reads `.agents/skills/`; Claude Code does not.
- Optional: the `grill-me` skill (`skills/productivity/grill-me/` in `github.com/mattpocock/skills`) carries out the start-of-project interview described in the handbook, Part II. Its existence was checked on 2026-11-16; its content was not reviewed. Without it, the agent conducts the interview directly.

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
