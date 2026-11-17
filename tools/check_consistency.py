"""Check that CORE.md, HANDBOOK.md and the guides agree with each other.

Usage: python tools/check_consistency.py
Prints every mismatch and exits with status 1 if there is any.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
core = (ROOT / "CORE.md").read_text(encoding="utf-8")
handbook = (ROOT / "HANDBOOK.md").read_text(encoding="utf-8")
guides = {p.name: p.read_text(encoding="utf-8") for p in (ROOT / "guides").glob("*.md")}
others = {name: (ROOT / name).read_text(encoding="utf-8") for name in ("README.md", "AGENTS.md")}
problems = []

# CORE.md and HANDBOOK.md carry the same version line.
version_line = r"^Draft v[\d.]+, \d{4}-\d{2}-\d{2}"
core_version = re.findall(version_line, core, re.M)
handbook_version = re.findall(version_line, handbook, re.M)
if len(core_version) != 1 or core_version != handbook_version:
    problems.append(f"version lines differ: CORE.md {core_version}, HANDBOOK.md {handbook_version}")

# Principle n in CORE.md has the title of chapter n in HANDBOOK.md.
core_titles = re.findall(r"^(\d+)\. \*\*(.+?)\.\*\*", core, re.M)
handbook_titles = re.findall(r"^### (\d+)\. (.+)$", handbook, re.M)
for pair in sorted(set(core_titles) ^ set(handbook_titles)):
    problems.append(f"principle title is not the same in CORE.md and HANDBOOK.md: {pair}")

# The guide table in CORE.md lists exactly the files in guides/.
listed = set(re.findall(r"^\| `guides/(.+?)` \|", core, re.M))
for name in sorted(listed ^ set(guides)):
    problems.append(f"guides/{name} is missing from guides/ or from the guide table in CORE.md")

# Every guide states what it applies to and when it was last checked.
for name, text in guides.items():
    for field in ("**Applies to:**", "**Last checked:**"):
        if field not in text:
            problems.append(f"guides/{name} has no {field} line")

# Every guide mentioned in any document exists.
for name, text in {"CORE.md": core, "HANDBOOK.md": handbook, **guides, **others}.items():
    for mentioned in sorted(set(re.findall(r"guides/([\w-]+\.md)", text)) - set(guides)):
        problems.append(f"{name} mentions guides/{mentioned}, which does not exist")

print("\n".join(problems) or "consistent")
sys.exit(1 if problems else 0)
