#!/usr/bin/env python3
"""Render the body of the Confluence tracker page (HTML in the Atlassian connector's dialect) from a groups.json.

Each group becomes one table row: topic, every page of the group as a smart-link card (grouped by role, current
pages first), finding and recommendation, basis, status, and an empty cell for the owner's decision. The page is the
only place where the owner sees which pages a group holds, so no page is left out or summarised as a count.
Decisions already written on the live page are NOT merged here: read the page, keep its decision and status cells,
and replace only rows whose content changed.

Usage: <python> tracker_page.py groups.json --date 2026-11-18 [--note TEXT] --out tracker.html
  --note TEXT  one paragraph on the limits of this run's method (how much was read, what rests on titles only);
               it becomes the note panel at the top of the page. Without it the page has no such panel.
  --out FILE   write the page there. Without it the page goes to standard output; prefer --out, because some
               shells re-encode redirected output (Windows PowerShell 5 writes UTF-16).
  <python> is the machine's Python 3: `py -3` on Windows, `python3` elsewhere. Standard library only.
  The output is UTF-8 with LF line endings on every platform.
"""
import argparse
import html
import json
import sys

ROLE_ORDER = ["current", "unclear", "duplicate", "superseded", "old-product"]
ROLE_COLOR = {"current": "green", "unclear": "yellow", "duplicate": "purple", "superseded": "red", "old-product": "neutral"}
esc = html.escape


def lozenge(text, color):
    return f'<span data-type="status" data-color="{color}">{esc(text)}</span>'


def pages_cell(pages):
    """One line per role (current first), every page as a smart-link card; a page kept from an excluded space says why."""
    ranked = sorted(pages, key=lambda p: ROLE_ORDER.index(p["role"]) if p["role"] in ROLE_ORDER else len(ROLE_ORDER))
    lines = {}
    for p in ranked:
        why = f' ({esc(p["space"])}, {esc(p["kept_because"])})' if p.get("kept_because") else ""
        lines.setdefault(p["role"], []).append(f'<a href="{esc(p["url"])}" data-card-appearance="inline"></a>{why}')
    return "".join(f'<p>{lozenge(role, ROLE_COLOR.get(role, "neutral"))} {" ".join(cards)} </p>' for role, cards in lines.items())


def table(rows, headers):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table data-layout="full-width"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def render(g, date, note=None):
    n_pages = sum(s["pages"] + s["live_docs"] for s in g["spaces"])
    excluded = g.get("excluded_spaces", [])
    scope = (f"Scope: {len(g['spaces'])} spaces ({', '.join(s['key'] for s in g['spaces'])}), {n_pages} pages"
             + (f"; space {', '.join(excluded)} is not monitored, and its pages appear only where a monitored page links to them" if excluded else "") + ".")
    removed = g.get("removed_groups", [])
    out = [
        f"<p>{esc(scope)} Last update: <time datetime=\"{date}\">{date}</time>. Status of a row: NEW (found in the last run), OPEN (waiting for a decision), "
        "AGREED, DONE, WON'T DO. Write decisions in the last column; they are kept when the page is updated.</p>",
    ]
    if note:
        out.append(f'<div data-type="panel-note"><p>{esc(note, quote=False)}</p></div>')
    if removed:
        out.append("<p>Rows removed because their pages are outside the scope: " + "; ".join(f'{esc(r["id"])} {esc(r["topic"])}' for r in removed) + ".</p>")
    out.append("<h2>Similar pages</h2>")
    rows = []
    for s in g["similarity_groups"]:
        basis = "read" if s["confidence"] == "confirmed-by-reading" else "titles only"
        rows.append([esc(s["id"]), esc(s["topic"]), pages_cell(s["pages"]),
                     f'<p>{esc(s["evolution"])}</p><p><strong>Suggested:</strong> {esc(s["recommendation"])}</p>',
                     f'{basis}; cross-linked: {esc(s["cross_linked"])}', lozenge("NEW", "blue"), ""])
    out.append(table(rows, ["#", "Topic", "Pages", "Finding and suggestion", "Basis", "Status", "Decision"]))
    out.append("<h2>Related pages that are neither linked nor filed together</h2>")
    rows = []
    for s in g["related_unlinked"]:
        rows.append([esc(s["id"]), esc(s["topic"]), pages_cell(s["pages"]),
                     f'<p>{esc(s["why_related"])}</p><p><strong>How far apart:</strong> {esc(s["how_far_apart"])}</p>',
                     f'cross-linked: {esc(s["cross_linked"])}', lozenge("NEW", "blue"), ""])
    out.append(table(rows, ["#", "Topic", "Pages", "Why they belong together", "Basis", "Status", "Decision"]))
    out.append("<h2>Structure of each space</h2>")
    out.append(table([[esc(s["key"]), f'{s["pages"]} + {s["live_docs"]}', "<ul>" + "".join(f"<li>{esc(o)}</li>" for o in s["observations"]) + "</ul>"]
                      for s in g["spaces"]], ["Space", "Pages + live docs", "Observations"]))
    out.append("<h2>Not examined yet</h2><ul>" + "".join(f"<li>{esc(x)}</li>" for x in g["not_examined"]) + "</ul>")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("groups"); ap.add_argument("--date", required=True)
    ap.add_argument("--note"); ap.add_argument("--out")
    a = ap.parse_args()
    g = json.load(open(a.groups, encoding="utf-8"))
    for key, prefix in (("similarity_groups", "S"), ("related_unlinked", "R")):
        for n, s in enumerate(g[key], 1):
            s.setdefault("id", f"{prefix}{n}")
    page = (render(g, a.date, a.note) + "\n").encode("utf-8")  # bytes: no CRLF, no locale encoding
    if a.out:
        with open(a.out, "wb") as f:
            f.write(page)
    else:
        sys.stdout.buffer.write(page)
