#!/usr/bin/env python3
"""Convert a Markdown file to the HTML that the Atlassian connector accepts for Jira bodies.

The result is passed as the description (or comment) with contentFormat "html".
Bare URLs become smart-link anchors (<a href="URL" data-card-appearance="inline"></a>), which Jira
renders as preview cards; [text](url) stays a plain link. Raw HTML in the Markdown is passed through,
so Jira-specific nodes (mention, date, status, panel, media) can be written in the connector's HTML
form where needed. Everything else is CommonMark plus tables and strikethrough.

Usage: <python> md2jirahtml.py input.md output.html
  Without output.html the result goes to standard output; prefer the file, because some shells re-encode
  redirected output (Windows PowerShell 5 writes UTF-16).
  <python> is the machine's Python 3: `py -3` on Windows, `python3` elsewhere.
  The input is read as UTF-8; the output is UTF-8 with LF line endings on every platform.
  Needs the package pinned in requirements.txt beside this file.
"""
import re
import sys
from pathlib import Path

try:
    from markdown_it import MarkdownIt
    from markdown_it.common.utils import escapeHtml
except ModuleNotFoundError:
    sys.exit("markdown-it-py is missing; install it with: <python> -m pip install -r "
             f'"{Path(__file__).resolve().parent / "requirements.txt"}"')

URL_RE = re.compile(r"https?://[^\s<>]+")
TRAILING_PUNCT = ".,;:!?"


def card(match):
    """Smart-link anchor for a bare URL; sentence punctuation and an unbalanced ')' stay outside."""
    url, tail = match.group(0), ""
    while url[-1] in TRAILING_PUNCT or (url[-1] == ")" and url.count("(") < url.count(")")):
        url, tail = url[:-1], url[-1] + tail
    return f'<a href="{escapeHtml(url)}" data-card-appearance="inline"></a>{escapeHtml(tail)}'


def render_text(self, tokens, idx, options, env):
    text = tokens[idx].content
    opened = sum(t.type == "link_open" for t in tokens[:idx])
    closed = sum(t.type == "link_close" for t in tokens[:idx])
    if opened > closed:  # the text of a [text](url) link is not turned into a card
        return escapeHtml(text)
    out, pos = [], 0
    for m in URL_RE.finditer(text):
        out += [escapeHtml(text[pos:m.start()]), card(m)]
        pos = m.end()
    return "".join(out) + escapeHtml(text[pos:])


def convert(markdown):
    md = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    md.add_render_rule("text", render_text)
    return md.render(markdown)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: md2jirahtml.py input.md [output.html]")
    with open(sys.argv[1], encoding="utf-8") as f:
        result = convert(f.read()).encode("utf-8")  # bytes: no CRLF, no locale encoding
    if len(sys.argv) == 3:
        with open(sys.argv[2], "wb") as f:
            f.write(result)
    else:
        sys.stdout.buffer.write(result)
