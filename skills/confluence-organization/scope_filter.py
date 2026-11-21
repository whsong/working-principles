#!/usr/bin/env python3
"""Apply the monitoring scope to a groups.json: drop the pages of excluded spaces, except pages that a page of a
monitored space links to, and write the result as a new groups.json.

A kept page of an excluded space gets the field `kept_because` ("linked from <space> <id>"). A group left with fewer
than two pages is dropped and named in `removed_groups`. Every group gets a stable `id` (S1.., R1.. in the order of
the input file, unless it already has one) so that numbers on the tracker page do not shift when groups are dropped.
Text of a group (finding, suggestion) is not rewritten here: give corrected text in an overrides file.

Usage: <python> scope_filter.py groups.json --exclude KEY --links links.tsv [--overrides overrides.json] --out new_groups.json
  --out FILE     write the result there. Without it the result goes to standard output; prefer --out, because some
                 shells re-encode redirected output (Windows PowerShell 5 writes UTF-16).
  links.tsv      tab-separated with header; columns source_id, source_space, target_id are used
  overrides.json {"groups": {"S4": {"evolution": "...", "drop": false, "remove_pages": ["<id of a deleted page>"]}, ...}, "not_examined": [...],
                  "space_observations": {"KEY": [...]}}   (every key optional)
  <python> is the machine's Python 3: `py -3` on Windows, `python3` elsewhere. Standard library only.
  The output is UTF-8 with LF line endings on every platform.
"""
import argparse
import csv
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("groups"); ap.add_argument("--exclude", nargs="+", required=True); ap.add_argument("--links", required=True)
ap.add_argument("--overrides"); ap.add_argument("--out")
a = ap.parse_args()

g = json.load(open(a.groups, encoding="utf-8"))
ov = json.load(open(a.overrides, encoding="utf-8")) if a.overrides else {}
linked = {}   # excluded-space page id -> "SPACE id" of the first monitored page that links to it
for r in csv.DictReader(open(a.links, encoding="utf-8"), delimiter="\t"):
    if r["source_space"] not in a.exclude:
        linked.setdefault(r["target_id"], f'{r["source_space"]} {r["source_id"]}')

removed = []
for key, prefix in (("similarity_groups", "S"), ("related_unlinked", "R")):
    kept_groups = []
    for n, s in enumerate(g[key], 1):
        s.setdefault("id", f"{prefix}{n}")
        o = ov.get("groups", {}).get(s["id"], {})
        pages = []
        for p in s["pages"]:
            if p["id"] in o.get("remove_pages", []):
                continue
            if p["space"] in a.exclude:
                if p["id"] not in linked:
                    continue
                p["kept_because"] = f"linked from {linked[p['id']]}"
            pages.append(p)
        s["pages"] = pages
        s.update({k: v for k, v in o.items() if k not in ("drop", "remove_pages")})
        if len(pages) < 2 or o.get("drop"):
            removed.append({"id": s["id"], "topic": s["topic"]})
        else:
            kept_groups.append(s)
    g[key] = kept_groups

g["spaces"] = [s for s in g["spaces"] if s["key"] not in a.exclude]
for s in g["spaces"]:
    s["observations"] = ov.get("space_observations", {}).get(s["key"], s["observations"])
g["not_examined"] = ov.get("not_examined", g["not_examined"])
g["excluded_spaces"] = a.exclude
g["removed_groups"] = g.get("removed_groups", []) + removed
result = json.dumps(g, ensure_ascii=False, indent=1).encode("utf-8")  # bytes: no CRLF, no locale encoding
if a.out:
    with open(a.out, "wb") as f:
        f.write(result)
else:
    sys.stdout.buffer.write(result)
