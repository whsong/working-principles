# Guide: Git repository

**Applies to:** any project kept in git.

**Last checked:** 2026-11-15.

## Location

- Keep the working tree outside file-sync folders (OneDrive, Dropbox, iCloud). Git and the synchroniser would both manage the same files, and that corrupts them. On Windows, check that a folder such as Documents has not been redirected into OneDrive before cloning there.
- Reference material that is large or not text (archives, screenshots, exported game data) stays outside the repository, or in a path listed in `.gitignore`.

## Baseline files

- `.gitattributes` with `* text=auto eol=lf`, so every checkout has LF line endings whatever the operating system. Mark binary types explicitly if git misdetects them.
- `.gitignore` from the first commit: build output, virtual environments, caches, editor state, secrets files such as `.env`, large data.
- `README.md` saying what the project is and the commands to set it up and check it.
- A `LICENSE` if the repository is public.

## Commits

- One purpose per commit. Subject line in the imperative, about 72 characters or fewer; the body says why the change was made.
- Commit only what was checked. Do not commit secrets, personal data, or large binaries; removing them from history later is costly.
- Do not rewrite history that has been pushed.

## Branches

- Early solo work may go straight to the default branch.
- Once the default branch is shared, deployed, or protected by CI, work on a branch and merge through a pull request.

## Portability

- No symlinks in the repository; Windows checkouts turn them into text files unless specially configured.
- No absolute paths, drive letters or user names in committed files.
- File names that differ only in letter case collide on Windows and macOS.
