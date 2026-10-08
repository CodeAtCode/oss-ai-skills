#!/usr/bin/env python3
"""Lint skills in oss-ai-skills repository.

Read-only scanner checking SKILL.md frontmatter, line counts, reference markers,
link resolution, and README sync.
"""

import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

SKILL_DIRS = ["extend", "frameworks", "languages", "tool"]
SKIP_DIRS = {".git", "node_modules", ".cortexkit", "scripts", ".github"}
MAX_ENTRY_LINES = 600
MAX_SCAN_DEPTH = 3

# pyqt sub-skills predate the name-matches-directory rule and keep pyqt-* names
ALLOWED_NAME_MAPPINGS = {
    "frameworks/pyqt/core": "pyqt-core",
    "frameworks/pyqt/dialogs": "pyqt-dialogs",
    "frameworks/pyqt/multimedia": "pyqt-multimedia",
    "frameworks/pyqt/styling": "pyqt-styling",
    "frameworks/pyqt/testing": "pyqt-testing",
    "frameworks/pyqt/threading": "pyqt-threading",
    "frameworks/pyqt/widgets": "pyqt-widgets",
}

KEBAB_CASE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")

# mutation-decisions.md convention: each kept-survivor line needs a closed-set reason and a date
DECISION_REASONS = re.compile(r"\b(equivalent|untestable|cost)\b")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


class Violation(NamedTuple):
    path: str
    line: int
    message: str


def parse_frontmatter(content: str) -> tuple[dict, str] | None:
    """Parse YAML frontmatter. Returns (dict, body) or None if no frontmatter."""
    if not content.startswith("---\n"):
        return None

    end_idx = content.find("\n---\n", 4)
    if end_idx == -1:
        return None

    frontmatter_text = content[4:end_idx]
    body = content[end_idx + 5:]

    frontmatter = {}
    metadata = {}
    current_key = None
    in_metadata = False

    lines = frontmatter_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        stripped = line.strip()

        # List item under the previous key
        if (m := re.match(r"^- (.+)$", stripped)):
            target = metadata if in_metadata else frontmatter
            if isinstance(target.get(current_key), list):
                target[current_key].append(m.group(1).strip())
            i += 1
            continue

        if (m := re.match(r"^(\w+):\s*(.*)$", stripped)):
            key, value = m.group(1), m.group(2).strip()

            if key == "metadata":
                in_metadata = True
                current_key = None
                i += 1
                continue

            target = metadata if in_metadata else frontmatter
            if value:
                target[key] = value
            else:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].strip().startswith("- "):
                    target[key] = []
                else:
                    target[key] = ""
            current_key = key

        i += 1

    if in_metadata:
        frontmatter["metadata"] = metadata

    return frontmatter, body


def check_name(skill_md: str, skill_rel: str, frontmatter: dict) -> list[Violation]:
    name = frontmatter.get("name")
    if not name:
        return [Violation(skill_md, 2, "name is missing")]

    violations = []
    if not KEBAB_CASE.fullmatch(name):
        violations.append(Violation(skill_md, 2, f"name '{name}' is not kebab-case"))

    expected = ALLOWED_NAME_MAPPINGS.get(skill_rel, os.path.basename(skill_rel))
    if name != expected:
        violations.append(Violation(skill_md, 2, f"name '{name}' does not match directory '{expected}'"))
    return violations


def check_description(skill_md: str, frontmatter: dict) -> list[Violation]:
    desc = frontmatter.get("description")
    if not desc or not desc.strip():
        return [Violation(skill_md, 3, "description is missing or empty")]

    first_line = desc.strip().strip("\"'").split("\n")[0].strip()
    if first_line.startswith((">", "|")):
        return []
    if not first_line.startswith("Use when"):
        return [Violation(skill_md, 3, f"description does not start with 'Use when': '{first_line[:60]}'")]
    return []


def check_metadata(skill_md: str, frontmatter: dict) -> list[Violation]:
    meta = frontmatter.get("metadata")
    if not isinstance(meta, dict) or not meta:
        return [Violation(skill_md, 4, "metadata section is missing")]

    violations = []
    if not meta.get("author"):
        violations.append(Violation(skill_md, 5, "metadata.author is missing"))

    version = str(meta.get("version") or "").strip("\"'")
    if not version:
        violations.append(Violation(skill_md, 6, "metadata.version is missing"))
    elif not re.fullmatch(r"\d+\.\d+\.\d+", version):
        violations.append(Violation(skill_md, 6, f"metadata.version '{version}' is not semver X.Y.Z"))

    tags = meta.get("tags")
    if tags is None:
        violations.append(Violation(skill_md, 7, "metadata.tags is missing"))
    elif isinstance(tags, list):
        if not tags:
            violations.append(Violation(skill_md, 7, "metadata.tags is empty"))
    elif not str(tags).strip("[]\"' ,"):
        violations.append(Violation(skill_md, 7, "metadata.tags is empty"))
    return violations


def check_line_count(skill_md: str) -> list[Violation]:
    with open(skill_md, "r") as f:
        n = sum(1 for _ in f)
    if n > MAX_ENTRY_LINES:
        return [Violation(skill_md, 0, f"SKILL.md has {n} lines, exceeds {MAX_ENTRY_LINES}")]
    return []


def check_references(skill_path: str) -> list[Violation]:
    refs_dir = os.path.join(skill_path, "references")
    if not os.path.isdir(refs_dir):
        return []

    violations = []
    for filename in sorted(os.listdir(refs_dir)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(refs_dir, filename)
        with open(filepath, "r") as f:
            head = "".join(f.readline() for _ in range(5)).lower()
        if "on demand" not in head:
            violations.append(Violation(os.path.join(skill_path, "references", filename), 1,
                "no 'loaded on demand' note within the first 5 lines"))
    return violations


def check_links(skill_md: str, skill_path: str, repo_root: str) -> list[Violation]:
    violations = []
    with open(skill_md, "r") as f:
        for line_num, line in enumerate(f, 1):
            for match in re.finditer(r"\[([^\]]+)\]\(([^)\s]+)\)", line):
                link = match.group(2)
                if link.startswith(("http://", "https://", "#")):
                    continue
                target = link.split("#", 1)[0]
                if not target:
                    continue
                candidates = [
                    os.path.normpath(os.path.join(skill_path, target)),
                    os.path.normpath(os.path.join(repo_root, target)),
                ]
                if not any(os.path.exists(c) for c in candidates):
                    violations.append(Violation(skill_md, line_num, f"link '{link}' not found"))
    return violations


def check_mutation_decisions(skill_path: str) -> list[Violation]:
    """When mutation-decisions.md exists, every kept-survivor line needs a
    reason (equivalent|untestable|cost) and a YYYY-MM-DD date, so decisions
    cannot silently decay."""
    path = os.path.join(skill_path, "mutation-decisions.md")
    if not os.path.isfile(path):
        return []

    violations = []
    with open(path, "r") as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            missing = []
            if not DECISION_REASONS.search(stripped):
                missing.append("reason equivalent|untestable|cost")
            if not ISO_DATE.search(stripped):
                missing.append("YYYY-MM-DD date")
            if missing:
                violations.append(Violation(path, line_num,
                    f"decision line missing {', '.join(missing)}"))
    return violations


def count_skill_lines(skill_path: str) -> int:
    """Count lines in the skill's own .md files, excluding nested skill dirs."""
    total = 0
    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if not os.path.isfile(os.path.join(root, d, "SKILL.md"))]
        for f in files:
            if f.endswith(".md"):
                with open(os.path.join(root, f), "r") as fp:
                    total += sum(1 for _ in fp)
    return total


def find_skill_dirs(repo_root: str) -> list[str]:
    """Find every directory containing a SKILL.md, up to MAX_SCAN_DEPTH."""
    skills = []
    for top in SKILL_DIRS:
        top_path = os.path.join(repo_root, top)
        if not os.path.isdir(top_path):
            continue
        for root, dirs, files in os.walk(top_path):
            depth = len(Path(root).relative_to(top_path).parts)
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            if depth >= MAX_SCAN_DEPTH:
                dirs[:] = []
            if "SKILL.md" in files:
                skills.append(os.path.relpath(root, repo_root))
    return sorted(skills)


def check_readme_sync(repo_root: str, skill_rels: list[str]) -> list[Violation]:
    readme_path = os.path.join(repo_root, "README.md")
    if not os.path.isfile(readme_path):
        return [Violation("README.md", 0, "README.md not found")]

    violations = []
    rows = {}
    with open(readme_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            for match in re.finditer(r"\[([^\]]+)\]\(([^)\s]+)\)", line):
                path = match.group(2)
                if path.startswith(("http://", "https://")):
                    continue
                if not path.endswith("SKILL.md"):
                    continue
                if not os.path.exists(os.path.join(repo_root, path)):
                    violations.append(Violation("README.md", line_num, f"link to nonexistent '{path}'"))
                    continue
                rows[path[: -len("SKILL.md")].rstrip("/")] = (line_num, line)

    for rel in skill_rels:
        if rel not in rows:
            violations.append(Violation("README.md", 0, f"no README row for skill '{rel}'"))
            continue
        line_num, line = rows[rel]
        numbers = re.findall(r"\|\s*([\d,]+)\s*\|", line)
        if not numbers:
            violations.append(Violation("README.md", line_num, f"row for '{rel}' has no line-count column"))
            continue
        reported = int(numbers[-1].replace(",", ""))
        actual = count_skill_lines(os.path.join(repo_root, rel))
        if reported != actual:
            violations.append(Violation("README.md", line_num,
                f"line count for '{rel}' is {reported}, actual {actual}"))
    return violations


def scan(repo_root: str) -> tuple[list[Violation], int]:
    violations = []
    skill_rels = find_skill_dirs(repo_root)

    for rel in skill_rels:
        skill_path = os.path.join(repo_root, rel)
        skill_md = os.path.join(skill_path, "SKILL.md")
        with open(skill_md, "r") as f:
            content = f.read()

        result = parse_frontmatter(content)
        if result is None:
            violations.append(Violation(skill_md, 1, "no frontmatter found"))
            continue

        frontmatter, _ = result
        violations.extend(check_name(skill_md, rel, frontmatter))
        violations.extend(check_description(skill_md, frontmatter))
        violations.extend(check_metadata(skill_md, frontmatter))
        violations.extend(check_line_count(skill_md))
        violations.extend(check_references(skill_path))
        violations.extend(check_links(skill_md, skill_path, repo_root))
        violations.extend(check_mutation_decisions(skill_path))

    violations.extend(check_readme_sync(repo_root, skill_rels))
    return violations, len(skill_rels)


def main():
    repo_root = str(Path(__file__).parent.parent.resolve())
    violations, skills_checked = scan(repo_root)

    for v in violations:
        print(f"{v.path}:{v.line}: {v.message}")

    print(f"\n{skills_checked} skills checked, {len(violations)} violations")
    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()
