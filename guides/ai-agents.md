# Guide: AI coding agents

**Applies to:** any project where AI coding agents work (Claude Code, Cursor, Codex, GitHub Copilot and similar).

**Last checked:** 2026-11-16, against the official Claude Code and Cursor documentation. Codex and Copilot details are not verified here.

## The project instruction file

- The canonical file is `AGENTS.md` at the project root. Cursor, Codex, Copilot and Claude Code read it without any setup. What it holds, and how to split it when it grows, is in `guides/project-records.md`.
- A subdirectory may have its own `AGENTS.md` for rules that hold only there, for example the conventions of `frontend/` and those of `backend/`. Cursor combines it with the files of the parent directories, the more specific taking precedence. Claude Code loads it when it first reads a file in that subdirectory. Module rules therefore stay out of the context until they are needed.

## No project-level `CLAUDE.md`

- A new project does not create a `CLAUDE.md`. In an existing project, move whatever its `CLAUDE.md` holds into `AGENTS.md` and delete the file.
- This applies to the owner's own projects. In a repository that belongs to a team or to others, its `CLAUDE.md` and `AGENTS.md` are theirs: leave them as they are, and add none of the owner's personal principles to them. The owner's principles reach such a repository through the personal level (see Per-machine setup); the owner's own notes about it are kept outside it (see "Where each instruction lives").
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
- Skills that one person uses in every project live at the personal level. `skills/` in this repository holds such skills, one folder each. A skill there holds the method only. What is true of one site, one person or one project is a setting: each skill has a `settings-template.md` that lists its settings, the filled-in settings files are kept outside this repository beside the project's documents, and the project's `AGENTS.md` names them. A skill asks when a setting is missing; it does not guess.
- A script that belongs to a skill sits in the skill's folder and is called through `${CLAUDE_SKILL_DIR}`, so it is present wherever the skill is. Its dependencies are pinned in a `requirements.txt` beside it.

## Rules that must not be broken

Instruction files are guidance; an agent may decide a line does not apply. A rule with no exceptions needs enforcement outside the model:

- a linter rule, test or CI job where possible, since those bind every agent;
- otherwise a hook in the agent's own configuration, for example a `PreToolUse` or `Stop` hook in `.claude/settings.json` for Claude Code.

Keep the enforced set small. Each check sometimes fires wrongly and must be maintained.

## Per-machine setup

Decide on each machine whether to do this. It makes the core load in every session there, without depending on the agent fetching a URL.

1. Clone `https://github.com/whsong/working-principles` to a directory outside any file-sync folder.
2. **Claude Code:** in `~/.claude/CLAUDE.md`, import the clone's `CORE.md` with an `@` line and state the clone's path, so the handbook and guides can be found.
3. **Claude Code, keeping the clone current:** without this step the clone is only as new as the last manual `git pull`. In `~/.claude/settings.json`, add a `SessionStart` hook that pulls when a new session starts:

   ```json
   "hooks": {
     "SessionStart": [
       {
         "matcher": "startup",
         "hooks": [
           {
             "type": "command",
             "command": "git",
             "args": ["-C", "<absolute path of the clone>", "pull", "--ff-only", "--quiet"],
             "timeout": 30
           }
         ]
       }
     ]
   }
   ```

   A pull that fails, for example with no network or over local changes that conflict, shows a notice and the session starts anyway. The documentation does not say whether the hook runs before `CLAUDE.md` is read, so assume that a pull which brings changes takes effect in the next session. Checked on 2026-11-18 against the Claude Code hooks documentation.
4. **Cursor:** global rules live in the settings screen (Customize → Rules), not in a file. Paste one sentence there pointing to the clone's `CORE.md`.
5. **Claude Code, skills:** to use a skill from the clone's `skills/`, link its folder into the personal skill directory, so that the clone stays the only copy:

   ```powershell
   # Windows: a directory junction needs no administrator rights
   New-Item -ItemType Junction -Path "$HOME\.claude\skills\<name>" -Target "<absolute path of the clone>\skills\<name>"
   ```

   ```bash
   # Linux and WSL
   ln -s "<absolute path of the clone>/skills/<name>" ~/.claude/skills/<name>
   ```

   The Claude Code documentation says that a skill folder may be a symbolic link; it does not mention junctions. A junction was tested on 2026-11-20 on Windows 11: the skill loaded in a new session. Then install what the skill's `requirements.txt` names, if it has one, and fill in its settings (see Skills).

Each machine, and each WSL distribution, has its own clone and its own `~/.claude/` (`guides/environments.md`); do not share one clone across the Windows and WSL file systems.

Do not do this on a machine where several people work under one shared login account: a personal `~/.claude/CLAUDE.md` there would apply to everyone's sessions. On such a machine, rely on the URL reference in the project's `AGENTS.md`, or run the agent on a personal machine and reach the shared one over SSH.

A cloud sandbox sees only the repository, so there the URL reference is the only route.
