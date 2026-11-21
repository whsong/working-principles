# Settings for the skill `confluence-organization`: template

The skill holds the method only. What is true of one site, one person or one run of this routine goes into two settings files that you keep outside this repository:

- **Site settings**: one file per Atlassian site. When you also use the skill `jira-issues`, it is the same file: add these sections to it.
- **Project settings**: one file for this routine on this site.

Copy the part you need, keep the headings exactly as they are (the skill refers to them by name), and fill in the last column. Then name both files in the `AGENTS.md` of the folder you start sessions from, so that step 0 of the skill finds them. Leave a value as "not decided; ask" when it is open: the agent then asks instead of guessing.

## Part 1: site settings

### Site

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Site host name | The `cloudId` the connector takes, for example `<name>.atlassian.net` | The address of your Confluence | |
| Site UUID | The same site as a UUID; some operations return it | `getAccessibleAtlassianResources` | |

### Confluence

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Personal space key | The space where the tracker page lives; it starts with `~` | `getConfluencePersonalSpace` | |
| Personal space id | The numeric id of that space | The same | |

## Part 2: project settings

### Scope

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Exclusion list | Starred spaces that are not watched, each with the reason and the date | Your decisions | |
| Watched spaces at the last run | For the record; the current set comes from `space in favouriteSpaces()` at every run | The last run | |

### Tracker page

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Title | | | |
| Page id and space | The one page every run updates | The page's address | |
| Kind | A live doc or a classic page; a live doc is updated node by node (section 6 of the skill) | The page | |
| Visibility | Who can see it, and why | Your decision | |
| Language | Only when it is not English | | |
| Note of the last run | The text last passed as `--note` to `tracker_page.py`: the limits of that run's method. Rewrite it at every run | The last run | |

### Working folder

| Setting | Meaning | Where to find it | Value |
|---|---|---|---|
| Path | The folder with this routine's `AGENTS.md` (background, current state, lessons, open questions) and its dated `artefacts/` | Your choice | |
