# Guide: Environments

**Applies to:** work that may run on Windows, WSL, Linux over SSH, or a cloud sandbox.

**Last checked:** 2026-11-15.

## Everywhere

- Quote paths. Paths may contain spaces and non-ASCII characters.
- State the text encoding explicitly when reading and writing files; use UTF-8 without a byte-order mark.

## Windows

- Two shells are common: PowerShell and Git Bash. Their syntax differs (quoting, environment variables, path separators, `/dev/null`). Write project scripts in a cross-platform language such as Python when they must run everywhere.
- Windows PowerShell 5 writes UTF-16 or adds a byte-order mark by default. PowerShell 7 writes UTF-8 without one.
- Git may convert line endings on checkout; the repository's `.gitattributes` settles it (see the git guide).
- Creating symlinks needs Developer Mode or administrator rights.
- Very long paths can fail; keep repositories near the drive root or the user directory.

## WSL

- Keep repositories inside the Linux file system (under the home directory), not under `/mnt/c`. Access across the boundary is slow and file permissions and line endings behave differently.
- A WSL distribution has its own tools, configuration and credentials, separate from Windows.

## Linux over SSH

- Run long jobs detached (`tmux`, or `nohup`) with output written to a log file, so a dropped connection does not kill them.
- Do not assume administrator rights. Install into the user directory or a project environment.
- A shared machine has other users: check free disk, memory and processors or GPUs before starting heavy work, and do not leave secrets in shared locations.

## Cloud sandbox

- Only the repository is present. No home-directory configuration, no local clones, no credentials beyond what the platform injects.
- Network access may be restricted, so fetching a URL can fail.
- The machine is temporary. Anything not committed and pushed is lost.
