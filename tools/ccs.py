#!/usr/bin/env python3
"""ccs: browse, preview, resume and delete Claude Code sessions in the terminal.
One file, standard library only, for Windows and Linux.

    ccs             the sessions of the current folder
    ccs -a          the sessions of every folder, grouped by folder
    ccs install     copy this file into ~/.local/bin so that `ccs` runs from anywhere

Keys: Up/Down, PgUp/PgDn, Home/End move; Space previews the conversation;
Enter resumes the session (`claude --resume`) in its folder; d deletes after a
y, in the list and in the preview; Ctrl+A switches between the current folder
and all folders; Esc goes back, and quits from the list.

Where Claude Code keeps a session (measured with version 2.1.330, 2026-11-25),
under ~/.claude, or under $CLAUDE_CONFIG_DIR when that is set:

    projects/<folder, every non-alphanumeric character replaced by "-">/<id>.jsonl
    projects/<same>/<id>/        side files of the session; not always present
    file-history/<id>/           not always present
    session-env/<id>/            not always present
    sessions/<pid>.json          one per running Claude Code process, naming its session

Deleting moves the first four to the trash: the Recycle Bin on Windows, the
home trash of freedesktop.org on Linux.

The Claude desktop app keeps a record of its own for each of its sessions, and
deleting here does not touch it: the entry stays in the app (seen 2026-11-25),
and opening it there reports that the earlier messages are gone and starts a
new session. To remove a desktop session completely, delete it in the app.

A session whose process is alive is not deleted and is marked LIVE, with the
status the process reports ("busy" while a turn runs, "idle" while it waits).
The desktop app keeps such a process for a session it has opened, until the
session is archived there; a terminal session has one until `/exit`.
"""
import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import unicodedata
from pathlib import Path

WINDOWS = os.name == "nt"
CONFIG = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
PROJECTS = CONFIG / "projects"
FIRST_INPUT_LIMIT = 400  # characters of the first paragraph that are kept


# ---------------------------------------------------------------- reading

def project_dir_name(folder):
    return re.sub(r"[^a-zA-Z0-9]", "-", folder)


def typed_text(record):
    """The text the user typed in a `user` record, or "" when the record holds
    none (a tool result, an injected skill body, the output of a local command)."""
    if record.get("isMeta") or record.get("isSidechain"):
        return ""
    content = record.get("message", {}).get("content", "")
    if isinstance(content, list):
        content = "\n\n".join(b.get("text", "") for b in content if b.get("type") == "text")
    command = re.search(r"<command-name>(.*?)</command-name>", content, re.S)
    if command:
        args = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
        return (command.group(1) + " " + (args.group(1) if args else "")).strip()
    for tag in ("system-reminder", "local-command-stdout", "local-command-stderr",
                "local-command-caveat"):
        content = re.sub(rf"<{tag}>.*?</{tag}>", "", content, flags=re.S)
    return content.strip()


def read_session(path):
    """Folder, title and first typed paragraph of one transcript file."""
    folder = title = ai_title = first = None
    desktop = False
    with open(path, encoding="utf-8") as lines:
        for line in lines:
            desktop = desktop or '"entrypoint":"claude-desktop"' in line
            if '"type":"custom-title"' in line:
                title = json.loads(line).get("customTitle") or title
            elif '"type":"ai-title"' in line:
                ai_title = json.loads(line).get("aiTitle") or ai_title
            elif folder is None and '"cwd":"' in line:
                folder = json.loads(line).get("cwd")
            if first is None and '"type":"user"' in line:
                record = json.loads(line)
                if record.get("type") == "user":
                    first = typed_text(record) or None
    stat = path.stat()
    if first:
        first = " ".join(re.split(r"\n\s*\n", first)[0].split())
        if len(first) > FIRST_INPUT_LIMIT:
            first = first[:FIRST_INPUT_LIMIT] + " ..."
    return {
        "id": path.stem,
        "path": path,
        "folder": folder or f"(folder not recorded; stored under {path.parent.name})",
        "title": title or ai_title or "(no title)",
        "first": first or "(no typed input)",
        "desktop": desktop,  # a turn of it ran in the Claude desktop app, which then has an entry for it
        "modified": stat.st_mtime,
        "size": stat.st_size,
    }


def read_conversation(path):
    """(speaker, text) for every typed input and every answer of the main thread."""
    turns = []
    with open(path, encoding="utf-8") as lines:
        for line in lines:
            if '"type":"user"' in line or '"type":"assistant"' in line:
                record = json.loads(line)
                if record.get("type") == "user":
                    text = typed_text(record)
                elif record.get("type") == "assistant" and not record.get("isSidechain"):
                    text = "\n\n".join(b.get("text", "") for b in record["message"]["content"]
                                       if b.get("type") == "text").strip()
                else:
                    continue
                if text:
                    turns.append(("You" if record["type"] == "user" else "Claude", text))
    return turns


def load_sessions(all_folders):
    """Grouped by folder; the newest session first in a group, and the group
    with the newest session first."""
    if all_folders:
        files = PROJECTS.glob("*/*.jsonl")
    else:
        files = (PROJECTS / project_dir_name(os.getcwd())).glob("*.jsonl")
    by_folder = {}
    for session in sorted((read_session(f) for f in files), key=lambda s: -s["modified"]):
        by_folder.setdefault(folder_key(session), []).append(session)
    return [session for group in by_folder.values() for session in group]


def folder_key(session):
    # normcase: on Windows the same folder is recorded as "I:\..." and as "i:\..."
    return os.path.normcase(session["folder"])


def process_is_alive(pid):
    if WINDOWS:  # os.kill would terminate the process on Windows
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32")
        kernel32.OpenProcess.restype = wintypes.HANDLE
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = wintypes.DWORD()
        kernel32.GetExitCodeProcess(wintypes.HANDLE(handle), ctypes.byref(code))
        kernel32.CloseHandle(wintypes.HANDLE(handle))
        return code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    return True


def live_sessions():
    """Session id -> (label, how to close it), for every session that a living
    Claude Code process holds. The label carries the status the process reports,
    when it reports one: "busy" while a turn runs, "idle" while it waits."""
    live = {}
    for record_file in (CONFIG / "sessions").glob("*.json"):
        record = json.loads(record_file.read_text(encoding="utf-8"))
        if process_is_alive(record["pid"]):
            status = record.get("status")
            how = ("archive it in the Claude desktop app" if record.get("entrypoint") == "claude-desktop"
                   else "type /exit in its terminal")
            live[record["sessionId"]] = (f"LIVE ({status})" if status else "LIVE", how)
    return live


def when(session):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(session["modified"]))


def total(sessions, all_folders):
    count = f"{len(sessions)} session" + ("" if len(sessions) == 1 else "s")
    if all_folders:
        folders = len({folder_key(s) for s in sessions})
        return f"{count} in {folders} folder" + ("" if folders == 1 else "s")
    return f"{count} in {os.getcwd()}"


# ---------------------------------------------------------------- deleting

def trash_windows(paths):
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR), ("pTo", wintypes.LPCWSTR),
                    ("fFlags", ctypes.c_uint16), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", wintypes.LPVOID), ("lpszProgressTitle", wintypes.LPCWSTR)]

    FO_DELETE = 3
    flags = 0x0040 | 0x0010 | 0x0004 | 0x0400  # ALLOWUNDO, NOCONFIRMATION, SILENT, NOERRORUI
    source = ctypes.create_unicode_buffer("\0".join(str(p) for p in paths) + "\0")
    operation = SHFILEOPSTRUCTW(None, FO_DELETE, ctypes.cast(source, wintypes.LPCWSTR),
                                None, flags, False, None, None)
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
    if result or operation.fAnyOperationsAborted:
        sys.exit(f"Moving to the Recycle Bin failed (SHFileOperationW returned {result}).")


def trash_linux(paths):
    """The home trash of the freedesktop.org Trash specification 1.0."""
    from urllib.parse import quote
    trash = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "Trash"
    (trash / "files").mkdir(parents=True, exist_ok=True)
    (trash / "info").mkdir(exist_ok=True)
    for path in paths:
        name, n = path.name, 1
        while (trash / "files" / name).exists() or (trash / "info" / f"{name}.trashinfo").exists():
            n += 1
            name = f"{path.name}.{n}"
        (trash / "info" / f"{name}.trashinfo").write_text(
            f"[Trash Info]\nPath={quote(str(path))}\n"
            f"DeletionDate={time.strftime('%Y-%m-%dT%H:%M:%S')}\n", encoding="utf-8")
        shutil.move(str(path), trash / "files" / name)


def paths_of(session):
    candidates = [session["path"], session["path"].with_suffix(""),
                  CONFIG / "file-history" / session["id"], CONFIG / "session-env" / session["id"]]
    return [p for p in candidates if p.exists()]


def trash(session):
    (trash_windows if WINDOWS else trash_linux)(paths_of(session))


# ---------------------------------------------------------------- interactive picker

WINDOWS_KEYS = {"H": "up", "P": "down", "I": "pageup", "Q": "pagedown", "G": "home", "O": "end"}
POSIX_KEYS = {"[A": "up", "[B": "down", "[5~": "pageup", "[6~": "pagedown", "[H": "home",
              "[F": "end", "[1~": "home", "[4~": "end", "OA": "up", "OB": "down",
              "OH": "home", "OF": "end"}


def read_key():
    """One key press: a name such as "up" or "enter", or the character itself."""
    if WINDOWS:
        import msvcrt
        char = msvcrt.getwch()
        if char in "\x00\xe0":
            return WINDOWS_KEYS.get(msvcrt.getwch(), "")
    else:
        import select
        char = os.read(0, 1).decode(errors="replace")
        if char == "\x1b":
            sequence = ""
            while select.select([0], [], [], 0.05)[0]:
                sequence += os.read(0, 1).decode(errors="replace")
            return POSIX_KEYS.get(sequence, "") if sequence else "escape"
    return {"\r": "enter", "\n": "enter", "\x1b": "escape", "\x03": "escape", " ": "space",
            "\x01": "ctrl-a"}.get(char, char)


@contextlib.contextmanager
def full_screen():
    """Alternate screen without a cursor, keys delivered one at a time."""
    if WINDOWS:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32")
        kernel32.GetStdHandle.restype = wintypes.HANDLE
        console = wintypes.HANDLE(kernel32.GetStdHandle(-11))  # STD_OUTPUT_HANDLE
        mode = wintypes.DWORD()
        kernel32.GetConsoleMode(console, ctypes.byref(mode))
        kernel32.SetConsoleMode(console, mode.value | 0x0004)  # VIRTUAL_TERMINAL_PROCESSING
    else:
        import termios
        import tty
        saved = termios.tcgetattr(0)
        tty.setcbreak(0)
    sys.stdout.write("\x1b[?1049h\x1b[?25l")
    try:
        yield
    finally:
        sys.stdout.write("\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()
        if WINDOWS:
            kernel32.SetConsoleMode(console, mode.value)
        else:
            termios.tcsetattr(0, termios.TCSADRAIN, saved)


def clip(text, width):
    """`text` cut to `width` screen columns; East Asian wide characters take two."""
    used = 0
    for position, char in enumerate(text):
        used += 2 if unicodedata.east_asian_width(char) in "WF" else 1
        if used > width:
            return text[:max(0, position - 1)] + "~"
    return text


def draw(lines):
    """`lines` are (style, text); style is an SGR code such as "1" or ""."""
    width, height = shutil.get_terminal_size()
    out = ["\x1b[H"]
    for style, text in lines[:height]:
        out.append(f"\x1b[{style}m{clip(text, width - 1)}\x1b[0m\x1b[K\r\n")
    out[-1] = out[-1][:-2]  # no line feed after the last line: it would scroll
    out.append("\x1b[J")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def move(position, key, count, page):
    step = {"up": -1, "down": 1, "pageup": -page, "pagedown": page,
            "home": -count, "end": count}.get(key, 0)
    return max(0, min(count - 1, position + step))


def ask_delete(session, screen):
    """Asks on the last line of `screen`. Returns (deleted, message)."""
    live = live_sessions()
    if session["id"] in live:
        return False, f"This session is live. To close it, {live[session['id']][1]}; then delete."
    warning = "Its entry stays in the desktop app. " if session["desktop"] else ""
    draw(screen[:-1] + [("1;33", f"Move to the trash (y/n)? {warning}"
                                 f"{session['id'][:8]} \"{session['title']}\"")])
    if read_key() not in ("y", "Y"):
        return False, ""
    trash(session)
    return True, f"Moved {session['id']} to the trash."


def preview(session):
    """Returns ("back" | "resume" | "deleted", message)."""
    width, _ = shutil.get_terminal_size()
    body = []
    for speaker, text in read_conversation(session["path"]):
        body.append(("1", f"{speaker}:"))
        for paragraph in text.splitlines():
            body += [("", "  " + line) for line in textwrap.wrap(
                paragraph, max(20, width - 4), break_on_hyphens=False)] or [("", "")]
        body.append(("", ""))
    top, message = 0, ""
    while True:
        page = max(1, shutil.get_terminal_size().lines - 4)
        screen = [("1", session["title"]),
                  ("2", f"{session['id']}  {when(session)}  {session['folder']}"), ("", "")]
        screen += body[top:top + page]
        screen += [("", "")] * (3 + page - len(screen))
        screen.append(("1;33", message) if message else
                      ("2", f"lines {top + 1}-{min(top + page, len(body))} of {len(body)}  "
                            "Enter resume  d delete  Space or Esc back"))
        draw(screen)
        message = ""
        key = read_key()
        if key in ("space", "escape"):
            return "back", ""
        if key == "enter":
            return "resume", ""
        if key == "d":
            deleted, message = ask_delete(session, screen)
            if deleted:
                return "deleted", message
        top = move(top, key, max(1, len(body) - page + 1), page)


def picker(all_folders):
    """Returns the session to resume, or None."""
    sessions = load_sessions(all_folders)
    selected = top = 0
    message = ""
    while True:
        live = live_sessions()
        height = max(4, shutil.get_terminal_size().lines - 4)  # lines for the list itself
        selected = max(0, min(selected, len(sessions) - 1))
        body, first_line, last_line = [], 0, 0
        for index, s in enumerate(sessions):
            start = len(body)
            if index == 0 or folder_key(s) != folder_key(sessions[index - 1]):
                body += [("1;4", s["folder"]), ("", "")]
            chosen = index == selected
            mark = f"   {live[s['id']][0]}" if s["id"] in live else ""
            body += [("1;36" if chosen else "1", ("> " if chosen else "  ") + s["title"] + mark),
                     ("36" if chosen else "", "    " + s["first"]),
                     ("36" if chosen else "2",
                      f"    {s['id']}  {when(s)}  {s['size'] / 1e6:.1f} MB"
                      + ("  desktop app" if s["desktop"] else "")), ("", "")]
            if chosen:
                first_line, last_line = start, len(body)
        if not sessions:
            body.append(("", "  No sessions here. Press Ctrl+A for the sessions of every folder."))
        top = max(last_line - height, min(top, first_line))
        screen = [("1", f"Claude Code sessions: {total(sessions, all_folders)}"), ("", "")]
        screen += body[top:top + height]
        screen += [("", "")] * (2 + height - len(screen))
        other = "current folder" if all_folders else "all folders"
        screen.append(("1;33", message) if message else
                      ("2", f"{selected + 1 if sessions else 0}/{len(sessions)}  Space preview  "
                            f"Enter resume  d delete  Ctrl+A {other}  Esc quit"))
        draw(screen)
        message = ""
        key = read_key()
        if key == "escape":
            return None
        if key == "ctrl-a":
            all_folders = not all_folders
            sessions, selected, top = load_sessions(all_folders), 0, 0
            continue
        if not sessions:
            continue
        outcome = ""
        if key == "space":
            outcome, message = preview(sessions[selected])
        if key == "enter" or outcome == "resume":
            return sessions[selected]
        if key == "d":
            deleted, message = ask_delete(sessions[selected], screen)
            outcome = "deleted" if deleted else ""
        if outcome == "deleted":
            del sessions[selected]
        selected = move(selected, key, len(sessions), max(1, height // 4))


def command_pick(args):
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        sys.exit("ccs is interactive: run it in a terminal.")
    try:
        with full_screen():
            session = picker(args.all)
    except KeyboardInterrupt:
        session = None
    if session:
        claude = shutil.which("claude")
        if not claude:
            sys.exit(f"claude is not on PATH. In {session['folder']} run: claude --resume {session['id']}")
        if not os.path.isdir(session["folder"]):
            sys.exit(f"The folder of this session no longer exists: {session['folder']}")
        os.chdir(session["folder"])
        sys.exit(subprocess.call([claude, "--resume", session["id"]]))


# ---------------------------------------------------------------- installing

def command_install(args):
    target = Path.home() / ".local" / "bin"
    on_path = {os.path.normcase(os.path.normpath(p)) for p in os.environ["PATH"].split(os.pathsep) if p}
    if os.path.normcase(str(target)) not in on_path:
        sys.exit(f"{target} is not on PATH. Add it to PATH, open a new terminal, and run this again.")
    target.mkdir(parents=True, exist_ok=True)
    if WINDOWS:
        shutil.copyfile(__file__, target / "ccs.py")
        (target / "ccs.cmd").write_text(f'@"{sys.executable}" "%~dp0ccs.py" %*\n', encoding="utf-8")
    else:
        shutil.copyfile(__file__, target / "ccs")
        (target / "ccs").chmod(0o755)
    print(f"Installed in {target}. Run: ccs")


def main():
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(prog="ccs", description="Browse, resume and delete Claude Code sessions.")
    parser.add_argument("-a", "--all", action="store_true", help="the sessions of every folder")
    parser.set_defaults(run=command_pick)
    commands = parser.add_subparsers()
    install = commands.add_parser("install", help="copy this file into ~/.local/bin")
    install.set_defaults(run=command_install)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
