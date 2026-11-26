---
name: jira-issues
description: "Issue tracking in Jira through the Atlassian connector: which events get a Story, Task, Bug or Subtask, how to write them (templates, smart links, pictures), how to query and update them without destroying content, how commits, branches and pull requests are linked, and how to list the open work in priority order. Use whenever the user mentions Jira, an issue or an issue key, the backlog, asks what to work on next, or asks to list the things to do, the to-do list or the priorities."
---

# Jira issue tracking

This skill is the method. It holds no site, project or person: those are settings, kept outside this skill (section 0). Issues live only in Jira. Local notes hold at most an issue key: never copy an issue's status, assignee, plan, findings or pending decisions into a local file, and query Jira before stating anything about an issue. Before finishing a task that touched an issue, search the notes written in the session for its key and delete every sentence that repeats what the issue says.

## 0. Find the settings before any call

1. Decide which project this request belongs to. The instructions of the working folder (AGENTS.md) either describe one project or list several, each with its two settings files: the site settings and the project settings. If the request does not make the project clear, ask. Read both files of that project.
2. If the instructions name no settings, or a needed value is missing: use the connector to discover what it can tell (accessible sites, required fields, transitions), and ask the user for the rest. Offer to write the answers into settings files made from [settings-template.md](settings-template.md).
3. Never guess a site, a project, a parent issue, a space or a page, and never write to one the user has not named.
4. Before the first write of a session, say which project and which parent or page the write goes to.

The section names used below (`Site`, `Jira project`, `People`, `Personal conventions`, `Code hosting`, `Parent`, `Labels`, `Repository`, `Queries`, `Local sources for the to-do list`, `Exceptions`) are the headings of the settings files.

## 1. The connector

- The connector is the claude.ai Atlassian MCP, second version. Common operations are tools that can be called directly (`getJiraIssue`, `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `searchJiraIssuesUsingJql` and others). For any other operation, call `discover` with the goal to get the exact name, then run it with `executeRead`, `executeWrite` or `executeDestructive` according to its risk. `cloudId` is written at the same level as `name` and `inputs`, never inside `inputs`. Operation names in this skill that are not in the tool list (for example `listJiraIssueTransitions`) are called this way.
- `cloudId` takes the site's host name directly (`Site` in the site settings).
- When the connector is not authorised (the tool list shows Atlassian as needing authorisation), do not use local files instead. Tell the user to authorise it in the connector settings of claude.ai.

## 2. Which issue type for what

The readers are the people who use the product and its maintainers, not agents. Every issue is a complete story for a person: what led to it, what was done, what came out.

| Type | Use | Size |
|---|---|---|
| **Story** | A new capability: something users could not do before and can do now (a new command-line switch, a new flow, a new output) | A group of commits or one or two pull requests; done within one or two weeks |
| **Task** | A maintainer-led change to existing behaviour that users can see: usage, output, performance, aligned parameters, supported configurations, and clean-up or retirement | The same |
| **Bug** | One per root cause. Anyone may fill in only the symptom and the environment; a maintainer adds root cause, fix, commit and verification | One fix commit or one pull request |
| **Subtask** | Work under a parent that needs its own branch or pull request, its own status or owner, or a reason that needs explaining | At most 8 per parent |

Which types the project has and how they nest is in `Jira project`.

Rules:

- Work that one or two sentences explain is a numbered step in the parent's description, not a Subtask.
- Behind-the-scenes adjustments get no issue: code formatting, hook configuration, merging documents, one-off git operations, work that touches only a local notes folder.
- On finding a defect, first look for an existing Bug with the same root cause. If there is one, add to it.
- A small fix gets no issue of its own when an issue on the same topic exists: update that issue, and adjust its title and content so that they describe the problem better.
- Several Bugs that serve one Task are linked with Relates or "is caused by". They are not made its children.
- The progress bar of an Epic counts only its direct children, not Subtasks. Accept that; do not split issues for the bar.
- Before creating an issue, read `Personal conventions`: a site may, for example, reuse issue keys that were freed instead of creating new ones.

## 3. How to write

- Write in English unless `Jira project` names another language. The title is a specific imperative or noun phrase of at most 80 characters, without a key prefix and without empty phrases such as "Fix bug".
- The description states the **current state** and is rewritten as a whole, like a document. Do not append "Update <date>" logs. Discussion goes into comments.
- **Mention nothing that exists only on one machine**: files, numbering and paths of a local notes folder, tools kept there and their output folders, local work trees and branches that are not pushed, handover documents, and phrases that mean something only to the person who did the work ("as received", "local branch"). Readers see only Jira, the code host and the wiki. A verification result says which check was made and what it concluded, and every reference is something the reader can open: a pushed commit, a branch, a pull request, a file in the repository, an issue, a wiki page. So write the issue after the push when its text cites the commit. The same holds for pull request descriptions.
- **Everything clickable is a smart link, and the description is written as HTML**, so that Jira shows a preview card with the title (an issue shows its key and title, a commit its message). How:
  1. Write the description as a Markdown file in the session's temporary folder. Keep no copy in a notes folder: the text of an issue lives only in Jira. Write links as bare URLs with a space on each side, not touching punctuation.
  2. Convert it: `<python> "${CLAUDE_SKILL_DIR}/md2jirahtml.py" <file>.md <file>.html`, where `<python>` is `py -3` on Windows and `python3` elsewhere. Give the output file as the second argument instead of redirecting standard output: some shells re-encode redirected output. The script needs the package pinned in `requirements.txt` beside it and says so when it is missing.
  3. Pass the HTML to `createJiraIssue` or `editJiraIssue` with `contentFormat: "html"`.

  The converter turns a bare URL into `<a href="URL" data-card-appearance="inline"></a>` (an `inlineCard` node), leaves `[text](url)` as a plain link, and escapes `<` and `&`. Do not write with `contentFormat: "markdown"`: on that path a bare URL stays a plain link. The second-version connector does not accept ADF. Verified on 2026-11-13 by writing and reading back: headings, bold, italic, strikethrough, inline code, bullet and numbered lists of two levels, code blocks with a language, tables, block quotes, cards and plain links all came back unchanged. Nodes that only Jira has (mention, date, status lozenge, panel, expand, picture) have no Markdown form: write the connector's HTML for them directly in the Markdown file, which the converter passes through. Get that HTML syntax with `executeRead` on `getContentFormatGuide` (`inputs: {"toolName": "editJiraIssue"}`).
  - Issue: `https://<site>/browse/<KEY>`
  - Commit: the URL of the full hash on the code host (`git rev-parse <short hash>` gives the full hash)
  - File in the repository: its URL on the branch that readers use (`Repository`). When that branch is renamed the old links die: replace them when the issue is next rewritten.
  - Attachment: `https://<site>/secure/attachment/<attachment id>/<file name>`; the id is in the `attachment` field that `getJiraIssue` returns
  - External pages (wiki and others): the bare URL
- A finished step carries its commit link. A result with data gives the numbers before and after (throughput, duration, pass rate).
- To point at a person, use a Jira mention or write nothing.
- **Pictures.** Upload with `uploadAttachmentToJiraIssue`: it returns an upload command to run on the local machine, which returns a file id. Embed the picture as a media node in the HTML: `<figure data-type="media-single" data-layout="center"><div data-type="media" data-media-type="file" data-id="<id>"></div></figure>`. Several pictures stacked as separate captioned blocks leave wide gaps on the page; putting them into the cells of one table keeps them together.

### Story and Task template (the same template)

```
## Background
Why this change is needed: what users hit today, and which configurations, setups or outputs are affected.

## Change
What is different after this work, in user-visible terms (usage, outputs, performance).

## Steps
1. <step> — done, <commit link>
2. <step> — in progress
3. <step> — to do (what decision or validation it waits for)

## Results
Measurements and validation runs: setup, configuration, what was run, before/after numbers, date.
```

### Bug template

```
## Environment
Branch and commit, configuration, setup (hardware or software environment), what was run.

## Symptom
What happened, with the exact message or output; how to reproduce in one command.

## Expected
What should have happened.

## Root cause
(maintainer) The mechanism, in one paragraph.

## Fix
(maintainer) What changed and where, <commit link>; side effects or follow-ups.

## Verification
(maintainer) Which run on which setup confirmed it, date.
```

A Subtask uses a short form of the Task template: one paragraph of Background, then Steps and Results.

## 4. Query and update without destroying content

List the open issues with the query from `Queries`, and limit the fields so that avatar links and similar bulk are not returned:

```
searchJiraIssuesUsingJql
  jql: <the query from the project settings>
  fields: ["summary", "status", "issuetype", "labels", "assignee"]
```

- Read one issue in full with `getJiraIssue`. The description comes back as Markdown by default; custom fields need `view: "evidence"` or their `customfield_*` ids in `fields`. Comments: `listJiraIssueComments`.
- Create with `createJiraIssue`: `parent` from `Parent` (for a Subtask, the key of its parent), labels from `Labels`, and the fields that `Jira project` lists as required in `additional_fields`.
- Change fields with `editJiraIssue`; the parent with `{"parent": {"key": "<KEY>"}}`; the type, between types of the same level, with `{"issuetype": {"name": "Story"}}` in `fields`.
- Change the status with `listJiraIssueTransitions`, then `transitionJiraIssue`. When closing a Bug, set the resolution in the same call. Which statuses the agent may set is in `Personal conventions`.
- Link issues with `createJiraIssueLink`; the type names come from `listJiraIssueLinkTypes`.
- Empty a description with `{"description": ""}` in the `fields` of `editJiraIssue`.

**Destructive edits are forbidden.** `editJiraIssue` replaces the whole description, so the test is: can everything in the old description be produced again, unchanged, by writing the new draft? Before every edit, read the current description with `getJiraIssue` (with `description` and `attachment` in `fields`) and decide in three steps:

1. **Look at `descriptionEditable` in the result.** When it is `true` after reading the description, the description holds only what Markdown can express (text, headings, lists, tables, code blocks, quotes, plain links, smart-link cards), and the agent may rewrite it as a whole. When it is `false`, the description holds nodes that Markdown cannot express: go to step 2. (The value means something only when the request included the `description` field. Without it the value is always `false`.)
2. **When `descriptionEditable` is `false`, the agent does not write the description, whatever the request says.** A request such as "update the description" asks for the new text; it is not consent to overwrite what is there. The agent does three things and then stops:
   - **It tells the user what the description holds that Markdown cannot express**, or that it could not find out. Visible in the Markdown that comes back: pictures and embedded attachments (`![](blob:...)`), mentions, dates, status lozenges (`<custom data-type="mention"|"date"|"status">`). **Not visible**: panels and expands come back flattened into ordinary paragraphs, and the title of an expand disappears; text colour and other formatting that Markdown lacks leaves no trace at all. To find these, read the history of the field with `listJiraIssueChangelogs`: it returns every earlier and later value of the description as wiki markup, in which `{color}`, `{panel}`, `{expand}` and `!picture!` show. The latest `toString` of the field `description` is the current description; a description that was never edited has no entry. (Tried once, on 2026-11-24: the only such node of that description was `{color:#bf2600}` around two words.)
   - **It gives the complete new draft** for the user to paste in the web page, and says which of those nodes the draft does not carry over.
   - **It writes only after the user has seen both and then says explicitly that the agent shall overwrite.** Consent given before the report does not count.

   Do not count on the History of the issue as a way back. Whether the user can open it is in `Personal conventions`, and the changelog the connector returns holds text, not pictures or files. Lesson of 2026-11-24: an agent read "update the description" as consent, overwrote a description whose `descriptionEditable` was `false`, and reported afterwards that the old text "is in the History"; the user had no access to it. Nothing was lost only because the hidden node happened to be a text colour.

   Why there is no lossless path: reading the description as HTML, changing one place and writing it back was not possible on 2026-11-13: a request with `responseContentFormat: "html"` still returned Markdown, so there was no lossless path. The connector's tool descriptions have since said that such bodies come back as HTML, but on 2026-11-20 a search with `responseContentFormat: "html"` still returned a description with pictures as Markdown. Before relying on an HTML read, check the `appliedContentFormat` of the response; until a read, edit and write-back in HTML has been tried on a spare issue, keep to this step. Once overwritten, a picture, a file, a panel or an expand cannot be restored by the connector.
3. **In the Markdown that comes back, a bare URL is a smart-link card and `[text](url)` is a plain link.** An old description may also show `<custom data-type="smartlink">URL</custom>`. A smart link is only a URL: write it as a bare URL in the new draft and the converter makes it a card again, with the same appearance. The agent writes these itself; it does not ask the user to paste.

Right after writing, read the description back and check: the number of bare URLs equals that of the draft, `descriptionEditable` is still `true`, and no literal `<custom` or HTML tag text is left.

Commit links in an issue are **not** a reason to avoid rewriting git history where the repository's rules allow rewriting (`Repository`). Rewrite as usual, then update the affected issues by the rules of this section.

Other limits of the connector (verified on 2026-11-13 with the second-version connector, by writing and reading back ordinary content, rich nodes and a picture, one trial each):

- **A picture can be produced again from its media id**, but a description with pictures still goes to the user under step 2. In the trial a picture was uploaded through the connector and written into a description; the whole description was then rewritten, with the media node written again from the media id that came back (the `<figure>` form in section 3), and the picture showed normally on the web page. Two reasons to hand over all the same: the Markdown that comes back does not carry the picture's width, alignment or caption, so these return to their defaults; and with `descriptionEditable` at `false`, invisible panels or expands in the same description cannot be ruled out. When the user, after the report and the draft of step 2, explicitly tells the agent to overwrite a description that holds pictures: such a description reads back as Markdown with each picture as a `blob:` link that carries its media id. Write HTML again, rebuild each picture as a media node from that id, and ask the user to check the pictures on the web page afterwards.
- **Converting between a Subtask and a standard type** uses `convertJiraIssueHierarchy` (through `executeWrite`; inputs `issueIdOrKey`, `targetIssueType`, `mode`). Where it goes through Jira's Move (`Jira project` says whether it does), explain it to the user and get consent each time, look at the field plan with `mode: "preview_step2"`, then run with `mode: "confirm"` and `acknowledgeMove: true`. Standard type to Subtask: `targetIssueType: "Subtask"`, and the user names `parentIssueKey`; the agent does not choose it. Subtask to a type that has a required user field: the conversion's `fieldRemap` was rejected for user fields, so first fill the field on the Subtask with `editJiraIssue` (`additional_fields`), then convert. In the trial the value was not kept after the conversion and had to be filled in again, and the conversion cleared the parent, which was set again with `editJiraIssue`.
- **Only the web page can** delete a link between issues, delete an attachment, or delete a comment: the connector has no operation for these.

## 5. Code hosting links

Jira scans branch names, commit messages, and the titles and descriptions of pull requests. Whatever contains an issue key appears in the Development panel of that issue. Conventions (recommended, not enforced, because not every contributor uses Jira; a repository states them in its own README):

- A commit that a maintainer pushes directly carries the key in its message: `<KEY> fix: <area>: ...`.
- Other contributors create the branch from the issue page (Create branch names it `<KEY>-summary`), and the pull request title then carries the key.
- A Task has a series of commits or one or two pull requests; a Bug has one fix commit or pull request; a Subtask with its own branch has its own pull request.

When the code host is Bitbucket, the second-version connector reads and writes it directly; the workspace and repository are in `Code hosting` and `Repository`.

- Read (`executeRead`): repositories, branches, commits, file contents, and for pull requests the list, details, diff, comments, tasks, the mergeability check (`getBitbucketRepoPullRequestMergeability`), default reviewers, pipelines.
- Write (`executeWrite`): open a pull request (`createBitbucketRepoPullRequest`, used on 2026-11-13), change one, post comments and tasks, approve or request changes, create a branch, create a commit through the interface, trigger a pipeline.
- Destructive (`executeDestructive`): merge or decline a pull request.
- The connector has no operation to delete a branch or to change repository settings or branch permissions.
- A pull request opened through the interface does not get the repository's default reviewers: the reviewers are exactly those passed in `reviewers`. Naming a reviewer notifies that person, so ask the user first.
- Who pushes and who merges is in `Code hosting`. Without a statement there, the agent pushes only when the user says so and does not merge.

## 6. Work loop

1. The user finds a problem → look for a Bug with the same root cause → if there is none, create one from the Bug template (the first three sections are enough).
2. Locate and fix → add Root cause, Fix and Verification to the same issue → the commit message carries the key → after verification, move the issue on as `Personal conventions` allows.
3. A change affects usage or output → create a Task, advance its steps one by one, and rewrite the description as the work proceeds.
4. A decision by the user is needed → mark the issue as `Labels` says for decisions, and write the options and a recommendation into the description. Remove the mark once the user has decided.
5. At the start of a session, run the query of section 4 and treat the issues in progress as the current work.

## 7. Listing the open work in priority order

When the user asks for the things to do, query again every time. Do not answer from memory or from an earlier result. There are three sources, and none may be left out:

1. **Jira**: the to-do query from `Queries`, with the fields `summary`, `status`, `issuetype`, `labels`, `duedate`, `priority`, `assignee`, `subtasks`, `updated`. List issues assigned to other people as well, with the assignee the query returned. Query open Subtasks separately (`parent in (<issues that have subtasks>) AND statusCategory != Done`). Keys that `Personal conventions` describes as freed are not work to do. Read the description of every issue changed in the last few days to see what the user changed.
2. **The local sources** that `Local sources for the to-do list` names: open questions, a suggested order, and items marked as undecided in the project's documents. Many of these have no issue.
3. **The state of the repository and the code host**: after `git fetch`, the new commits on the branches the project follows, the branches with commits in the last few days, and the open pull requests towards the main branch. When a fact in the project's notes turns out to be stale, correct the notes in the same step.

Order by, in this sequence: the focus the user stated most recently (in the project's instructions), whether an item blocks other people or affects the correctness of data, the due date and priority fields of Jira, and the order the project's notes suggest. For each item give: the key or the source, the status and due date, the concrete next step, and who it waits for (a decision by the user, another person, or nothing: the agent can do it now). Sum up once "what needs a decision by the user" and once "what the agent can do now". Point out where Jira's priority or due date disagrees with the order given.
