# Settings for the skill `jira-issues`: template

The skill holds the method only. What is true of one site, one person or one project goes into two settings files that you keep outside this repository, next to your project's own documents:

- **Site settings**: one file per Jira site, shared by all your projects on that site.
- **Project settings**: one file per project.

Copy the part you need, keep the headings exactly as they are (the skill refers to them by name), and fill in the last column. Then name both files in the project's `AGENTS.md`, so that step 0 of the skill finds them. Leave a value as "not decided; ask" when it is open: the agent then asks instead of guessing.

## Part 1: site settings

### Site

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Site host name | The `cloudId` the connector takes, for example `<name>.atlassian.net` | The address of your Jira | |
| Site UUID | The same site as a UUID; some operations return it | `getAccessibleAtlassianResources` | |

### Jira project

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Project key and name | The key that starts every issue key | The project's page | |
| Project kind | Team-managed or company-managed; decides the issue hierarchy and whether a type conversion is a Move | Project settings in Jira | |
| Issue types | The types that exist and which may be a child of which | `discover` an operation that lists the project's issue types | |
| Workflow | The statuses in order, and every restriction on a transition (for example: Done only from Review; Review needs a reviewer) | `listJiraIssueTransitions` on an issue; a refused transition names the rule | |
| Required fields on create | Each field with its id (`duedate`, `customfield_...`), its format, and what to put in | Create an issue once by hand and note what the form demands; custom-field ids from `getJiraIssue` with `view: "evidence"` | |
| Other custom fields in use | Fields that are not required but that people read (for example actual start and end dates) | The same | |
| Resolutions | The values to choose from when closing | The close dialog of an issue | |
| Link types | The names and their direction (which side is the blocker) | `listJiraIssueLinkTypes` | |
| Type conversion | Whether Subtask ↔ standard type goes through Move, and what is lost | One trial on a spare issue | |
| Language of issues | Only when it is not English | Your team's habit | |

### People

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Your account id | Used for assignee and for user-list fields | `atlassianUserInfo` | |
| Assignee on create | Who the agent sets; note it when the project's default assignee is someone else | Your choice | |
| Reviewer on create | What the agent puts into a required reviewer field without notifying other people | Your choice | |

### Personal conventions

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Statuses the agent sets | Which transitions the agent makes itself and which stay with you | Your choice | |
| Access to the History of an issue | Whether you can open the History of an issue. It is the only place where a description that was overwritten can still be found, so without it nothing an agent overwrites comes back | Open an issue and look for History under Activity | |
| Issues that are no longer needed | What happens to them when the project has no "won't do" status: closed with a resolution, or emptied and kept as a free key | Your choice | |
| Reuse of free keys | Whether the agent must look for a free key before creating an issue, and the query that finds one | Your choice | |

### Code hosting

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Service and workspace | For example Bitbucket and its workspace id | The repository's address | |
| Pull requests through the connector | Who may be named as reviewer, and whether to ask first | Your choice | |
| Push and merge | Who pushes and who merges, and how | Your choice | |

## Part 2: project settings

### Parent

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Default parent | The Epic (or other parent) that new issues go under, or "none: ask before every create" | Your choice | |
| Related issues | Issues that explain the project's origin and are worth linking | Your choice | |

### Labels

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Labels on every issue | | Your team's habit | |
| Label for "needs a decision" | Put on an issue that waits for you; removed when you have decided | Your choice | |
| Area labels | One label per area of the code or the work, each with what it covers; at least one per issue | Your choice; use the same words as in commit messages | |

### Repository

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Repository | Its id on the code host, and where the local clone is | | |
| Branches | Which branch readers use (links to files point there), which branch takes daily work, and how a change gets from one to the other | The repository's README | |
| History rewriting | On which branches commits may be rewritten | The repository's rules | |
| Issue keys in commits | The form of a commit message that carries a key | The repository's README | |

### Queries

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Open issues | The JQL that lists this project's open issues | Usually `parent = <Epic> AND statusCategory != Done ORDER BY status DESC, created` | |
| To-do list | The JQL for the priority list of section 7 | Usually the same with `ORDER BY status DESC, duedate ASC` | |

### Local sources for the to-do list

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Documents | The files and sections that hold open questions, a suggested order, and undecided items | Your project's documents | |
| Order of priorities | What decides the order when the sources disagree | Your choice | |

### Exceptions

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Exceptions | Rules of the skill or of the site settings that this project sets aside, each with its reason and date | Your decisions | |
