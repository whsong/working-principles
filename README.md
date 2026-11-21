# working-principles

Working principles for engineering projects done with AI agents: general principles, one person's fixed preferences, and guides with concrete defaults for particular kinds of project.

- [CORE.md](CORE.md): the short version, kept in an agent's context in every session. Start here.
- [HANDBOOK.md](HANDBOOK.md): the long version, with the reasons and examples. Read when starting a project or when a rule in the core needs explaining.
- [guides/](guides/): concrete tools, defaults and templates. Each guide states what it applies to and when it was last checked.
- [skills/](skills/): skills for AI agents that are useful in every project, one folder each: `jira-issues` (issue tracking in Jira) and `confluence-organization` (keeping a Confluence site in order). They hold the method only; your site and project facts go into settings files that you keep yourself. How to install one is in [guides/ai-agents.md](guides/ai-agents.md), Per-machine setup.
- [AGENTS.md](AGENTS.md): how to work on this repository itself.

## Using it in a project

Reference `CORE.md` from the project's `AGENTS.md`; do not copy it. The exact text to paste and the optional per-machine setup are in [guides/ai-agents.md](guides/ai-agents.md).

## Starting a project

An agent asked to initialise a project folder by these principles does the following, in this order. Each step names the place where the rule is written; this list adds no rule of its own.

1. Read [CORE.md](CORE.md), then [HANDBOOK.md](HANDBOOK.md) in full.
2. Read what the folder already holds before changing anything (handbook, chapter 1).
3. Interview the owner until the background, the requirements, the phases and the acceptance criteria are clear, and for a code project the refactoring policy (handbook, Part II, Interview at the start).
4. Decide with the owner whether the folder is kept in git; many are not (handbook, chapter 6, Keep history). Only if it is, set up the repository as in [guides/git-repository.md](guides/git-repository.md).
5. Write `AGENTS.md` at the root of the folder from the interview. What it holds is in [guides/project-records.md](guides/project-records.md); the paragraph that references `CORE.md`, and what to do with an existing `CLAUDE.md`, are in [guides/ai-agents.md](guides/ai-agents.md).
6. If the project will have tool code or intermediate outputs, lay out the folder as in [guides/tool-code-and-outputs.md](guides/tool-code-and-outputs.md).
7. Report what was set up and what is still open (handbook, chapter 9).

## License

[CC BY-SA 4.0](LICENSE).
