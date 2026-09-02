#!/usr/bin/env python3
"""
Skill Update Report Generator
Mines OpenCode DB usage history to report what to update in a cwd skill.
"""

import argparse
import glob
import json
import os
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


STOPWORDS = {
    "the", "and", "for", "with", "from", "this", "that", "into", "code", "file",
    "test", "refactor", "fix", "add", "new", "update", "remove", "change", "make",
    "set", "get", "create", "delete", "using", "when", "your", "you", "are", "be",
    "to", "of", "in", "on", "at", "by", "an", "as", "is", "it", "or", "so", "if",
    "but", "not", "can", "will", "all", "any", "been", "have", "has", "had", "was",
    "were", "been", "being", "do", "does", "did", "doing", "a", "i", "my", "we",
    "our", "they", "them", "their", "he", "she", "his", "her", "what", "which",
    "who", "how", "where", "why", "when", "about", "after", "before", "between",
    "through", "during", "without", "again", "further", "once", "here", "there",
    "then", "than", "very", "just", "also", "only", "most", "some", "such", "no",
    "up", "down", "out", "off", "over", "under", "too", "even", "both", "each",
    "few", "more", "many", "other", "these", "those", "am", "because", "become",
    "now", "while", "about", "above", "below", "same", "different", "way", "use",
    "used", "used", "like", "like", "much", "really", "well", "back", "still",
    "should", "could", "would", "may", "might", "must", "shall", "need", "want",
    "try", "help", "work", "look", "find", "give", "take", "see", "know", "think",
    "get", "put", "end", "go", "come", "make", "let", "begin", "keep", "hold",
    "write", "show", "change", "move", "turn", "call", "ask", "play", "run", "start",
}


def find_db(custom_path=None):
    """Locate the OpenCode SQLite database."""
    if custom_path:
        p = Path(custom_path).expanduser()
        if p.exists():
            return str(p)
        print(f"ERROR: Specified DB path does not exist: {custom_path}", file=sys.stderr)
        sys.exit(1)

    candidates = [
        Path(os.environ.get("OPENCODE_DB_PATH", "")),
        Path.home() / ".local" / "share" / "opencode" / "opencode.db",
    ]
    share_dir = Path.home() / ".local" / "share" / "opencode"
    if share_dir.exists():
        for f in sorted(share_dir.glob("opencode*.db"), key=lambda x: x.stat().st_mtime, reverse=True):
            candidates.insert(0, f)

    for c in candidates:
        if c and c.exists() and c.is_file():
            return str(c)

    print(
        "ERROR: No OpenCode database found.\n"
        "Searched:\n"
        "  $OPENCODE_DB_PATH\n"
        "  ~/.local/share/opencode/opencode*.db\n"
        "Pass --db to specify a custom location.",
        file=sys.stderr,
    )
    sys.exit(1)


def find_skill_in_cwd(skill_name):
    """Find a skill in the current working directory under frameworks/, languages/, extend/, tool/."""
    cwd = Path.cwd()
    base_dirs = ["frameworks", "languages", "extend", "tool"]
    
    for base in base_dirs:
        base_path = cwd / base
        if not base_path.exists():
            continue
        for skill_dir in base_path.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            # Match by directory name
            if skill_dir.name == skill_name:
                return str(skill_md), skill_dir.name
            
            # Match by frontmatter name
            try:
                content = skill_md.read_text(encoding="utf-8")
                fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if fm_match:
                    fm = fm_match.group(1)
                    name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
                    if name_m and name_m.group(1).strip().strip('"').strip("'") == skill_name:
                        return str(skill_md), skill_dir.name
            except Exception:
                continue
    
    return None, None


def list_available_skills():
    """List all available skills in cwd."""
    cwd = Path.cwd()
    base_dirs = ["frameworks", "languages", "extend", "tool"]
    skills = []
    
    for base in base_dirs:
        base_path = cwd / base
        if not base_path.exists():
            continue
        for skill_dir in base_path.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                skills.append(skill_dir.name)
    
    return sorted(skills)


def parse_skill_md(path):
    """Parse a SKILL.md file and extract frontmatter + body."""
    try:
        content = Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return {"error": str(e), "path": path}

    result = {"path": path, "name": "", "description": "", "version": "", "body": ""}

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        version_m = re.search(r'version:\s*["\']?([^"\'\n]+)["\']?', fm, re.MULTILINE)
        if name_m:
            result["name"] = name_m.group(1).strip().strip('"').strip("'")
        if desc_m:
            result["description"] = desc_m.group(1).strip().strip('"').strip("'")
        if version_m:
            result["version"] = version_m.group(1).strip()

    body = re.sub(r"^---.*?---", "", content, flags=re.DOTALL).strip()
    result["body"] = body
    result["line_count"] = len(content.splitlines())
    result["section_count"] = len(re.findall(r"^#{1,6}\s+", body, re.MULTILINE))

    return result


def derive_domain_keywords(skill_info, dir_name):
    """Derive domain keywords from skill info."""
    tokens = []
    
    # Directory name tokens
    tokens.extend(re.findall(r"[a-zA-Z]{3,}", dir_name.lower()))
    
    # Frontmatter tokens
    if skill_info.get("name"):
        tokens.extend(re.findall(r"[a-zA-Z]{3,}", skill_info["name"].lower()))
    if skill_info.get("description"):
        tokens.extend(re.findall(r"[a-zA-Z]{3,}", skill_info["description"].lower()))
    
    # Filter stopwords
    return [t for t in tokens if t not in STOPWORDS and len(t) >= 3]


def get_schema_info(conn):
    """Discover available columns in session/part tables."""
    cur = conn.cursor()
    schema = {}
    
    for table in ("session", "part", "message"):
        try:
            cur.execute(f"PRAGMA table_info({table})")
            schema[table] = [row[1] for row in cur.fetchall()]
        except Exception:
            pass
    
    return schema


def extract_candidates_from_part(part_data):
    """Extract error codes, exceptions, library names from part data."""
    candidates = {
        "error_codes": [],
        "exceptions": [],
        "libraries": [],
        "file_paths": [],
    }
    
    try:
        text = str(part_data)
        
        # Error codes: E####, E[0-9]{4}, error[XXX]
        for m in re.finditer(r"\b[Ee](\d{4})\b", text):
            candidates["error_codes"].append(f"E{m.group(1)}")
        for m in re.finditer(r"error\[(\w+)\]", text):
            candidates["error_codes"].append(m.group(1))
        
        # Traceback
        if "Traceback (most recent call last)" in text:
            for m in re.finditer(r"Traceback.*?(\w+Error|Exception):\s*(\w+)", text, re.DOTALL):
                candidates["exceptions"].append(m.group(2))
        
        # Exception/Error class names
        for m in re.finditer(r"(?:Exception|Error|Warning):\s*(\w+)", text):
            candidates["exceptions"].append(m.group(1))
        
        # Library mentions: pip install X, cargo add X, npm i X
        for m in re.finditer(r"pip\s+install\s+(\S+)", text):
            candidates["libraries"].append(m.group(1).lstrip("-"))
        for m in re.finditer(r"cargo\s+add\s+(\w+)", text):
            candidates["libraries"].append(m.group(1))
        for m in re.finditer(r"npm\s+(?:i|install)\s+(\S+)", text):
            candidates["libraries"].append(m.group(1).lstrip("@"))
        
        # File paths
        for m in re.finditer(r"[/\\][\w./\-]+\.(py|rs|ts|js|go|java|c|h|cpp|sol|vue|tsx|jsx)", text):
            candidates["file_paths"].append(m.group(0))
            
    except Exception:
        pass
    
    return candidates


def mine_sessions(conn, skill_info, dir_name, schema, days=180, limit=200):
    """Mine sessions for update candidates."""
    cur = conn.cursor()
    keywords = derive_domain_keywords(skill_info, dir_name)
    
    if not keywords:
        return [], {}
    
    # Get sessions from relevant directory (if directory column exists)
    session_table = "session"
    dir_col = "directory" if "directory" in schema.get("session", []) else None
    
    # Date filter - timestamps are in milliseconds
    cutoff_ms = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
    
    # Query sessions
    session_query = f"SELECT id, title, directory, time_created, time_updated FROM {session_table} WHERE time_created > ? ORDER BY time_created DESC LIMIT ?"
    try:
        sessions = cur.execute(session_query, (cutoff_ms, limit * 2)).fetchall()
    except Exception:
        return [], {}
    
    # Filter by relevance
    relevant_sessions = []
    for sess in sessions:
        sid, title, directory, created, updated = sess
        # Check if directory matches skill domain or title contains keywords
        if dir_col and directory:
            dir_lower = directory.lower()
            if any(k in dir_lower for k in keywords[:5]):
                relevant_sessions.append(sess)
                continue
        
        # Check title for keywords
        if title and any(k in title.lower() for k in keywords):
            relevant_sessions.append(sess)
            continue
    
    # Limit to requested
    relevant_sessions = relevant_sessions[:limit]
    
    # Extract candidates from parts
    all_candidates = {
        "error_codes": Counter(),
        "exceptions": Counter(),
        "libraries": Counter(),
        "file_paths": Counter(),
    }
    evidence = {}  # value -> list of {session, title, snippet}
    
    for sess in relevant_sessions:
        sid, title, directory, created, updated = sess
        short_id = sid[:8] if sid else "unknown"
        
        # Get parts for this session
        try:
            parts = cur.execute(
                f"SELECT data FROM part WHERE session_id = ? ORDER BY time_created",
                (sid,)
            ).fetchall()
        except Exception:
            continue
        
        for (part_data,) in parts:
            extracted = extract_candidates_from_part(part_data)
            
            for cat, items in extracted.items():
                for item in items:
                    all_candidates[cat][item] += 1
                    if item not in evidence:
                        evidence[item] = []
                    snippet = str(part_data)[:200].replace("\n", " ")
                    evidence[item].append({
                        "session": short_id,
                        "title": title[:50] if title else "untitled",
                        "snippet": snippet,
                    })
    
    return relevant_sessions, all_candidates, evidence


def generate_report(skill_info, dir_name, sessions, candidates, evidence, skill_body, json_output=False):
    """Generate the update report."""
    # Filter candidates: only "missing" if not in skill body
    skill_body_lower = skill_body.lower()
    
    missing = {
        "error_codes": [],
        "exceptions": [],
        "libraries": [],
        "file_hotspots": [],
    }
    
    for cat, counter in candidates.items():
        for value, count in counter.most_common(20):
            # Check if already covered in skill
            if cat == "file_paths":
                dir_part = Path(value).parent.name.lower()
                if dir_part not in skill_body_lower:
                    missing["file_hotspots"].append((value, count, evidence.get(value, [])[:3]))
            elif value.lower() not in skill_body_lower:
                key = cat
                missing[key].append((value, count, evidence.get(value, [])[:3]))
    
    if json_output:
        report = {
            "skill": {
                "path": skill_info["path"],
                "name": skill_info["name"],
                "version": skill_info.get("version") or "unversioned",
                "line_count": skill_info.get("line_count", 0),
                "section_count": skill_info.get("section_count", 0),
            },
            "sessions_mined": {
                "count": len(sessions),
                "date_range": {
                    "earliest": sessions[-1][3] if sessions else None,
                    "latest": sessions[0][3] if sessions else None,
                },
                "top_titles": [s[1][:50] for s in sessions[:5] if s[1]],
            },
            "candidates": missing,
        }
        print(json.dumps(report, indent=2, default=str))
        return
    
    # Text report
    lines = []
    lines.append("=" * 70)
    lines.append(f"  SKILL UPDATE REPORT: {skill_info['name'] or dir_name}")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    
    # SKILL STATE
    lines.append("## SKILL STATE")
    lines.append(f"  Path: {skill_info['path']}")
    lines.append(f"  Version: {skill_info.get('version') or 'unversioned'}")
    lines.append(f"  Line count: {skill_info.get('line_count', 0)}")
    lines.append(f"  Section count: {skill_info.get('section_count', 0)}")
    lines.append("")
    
    # SESSIONS MINED
    lines.append("## SESSIONS MINED")
    lines.append(f"  Count: {len(sessions)}")
    if sessions:
        dates = [s[3] for s in sessions if s[3]]
        if dates:
            # Convert ms to readable date
            earliest = datetime.fromtimestamp(min(dates)/1000, tz=timezone.utc).strftime('%Y-%m-%d')
            latest = datetime.fromtimestamp(max(dates)/1000, tz=timezone.utc).strftime('%Y-%m-%d')
            lines.append(f"  Date range: {earliest} to {latest}")
        top_titles = [s[1][:50] for s in sessions[:5] if s[1]]
        if top_titles:
            lines.append("  Top session titles:")
            for t in top_titles:
                lines.append(f"    - {t}")
    else:
        lines.append("  (no relevant sessions found)")
    lines.append("")
    
    # UPDATE CANDIDATES
    lines.append("## UPDATE CANDIDATES")
    
    has_candidates = any(missing.values())
    
    if not has_candidates:
        lines.append("  No missing items found — skill appears to cover observed experience.")
    else:
        if missing["error_codes"]:
            lines.append("")
            lines.append("  Error Codes:")
            for val, count, ev in missing["error_codes"][:10]:
                lines.append(f"    - {val} ({count} occurrences)")
                if ev:
                    lines.append(f"      Evidence: {ev[0]['session']} — {ev[0]['title'][:30]}")
        
        if missing["exceptions"]:
            lines.append("")
            lines.append("  Exception Classes:")
            for val, count, ev in missing["exceptions"][:10]:
                lines.append(f"    - {val} ({count} occurrences)")
                if ev:
                    lines.append(f"      Evidence: {ev[0]['session']} — {ev[0]['title'][:30]}")
        
        if missing["libraries"]:
            lines.append("")
            lines.append("  Library Mentions:")
            for val, count, ev in missing["libraries"][:10]:
                lines.append(f"    - {val} ({count} occurrences)")
                if ev:
                    lines.append(f"      Evidence: {ev[0]['session']} — {ev[0]['title'][:30]}")
        
        if missing["file_hotspots"]:
            lines.append("")
            lines.append("  File Hotspots (top directories):")
            for val, count, ev in missing["file_hotspots"][:10]:
                lines.append(f"    - {val} ({count} occurrences)")
    
    lines.append("")
    
    # COVERAGE HINT
    lines.append("## COVERAGE HINT")
    keywords = derive_domain_keywords(skill_info, dir_name)
    skill_body_lower = skill_info.get("body", "").lower()
    for kw in keywords[:15]:
        covered = "✓" if kw in skill_body_lower else "⚠️"
        lines.append(f"  {covered} {kw}")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("  END OF REPORT")
    lines.append("=" * 70)
    
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Skill Update Report Generator — mine OpenCode DB for skill update candidates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 skill_update_report.py django
  python3 skill_update_report.py rust-common-pitfalls --days 90 --json
  python3 skill_update_report.py django rust --limit 100 --days 120
        """,
    )
    parser.add_argument("skills", nargs="+", help="Skill name(s) to analyze")
    parser.add_argument("--db", help="Path to OpenCode SQLite database")
    parser.add_argument("--limit", type=int, default=200, help="Max sessions per skill (default: 200)")
    parser.add_argument("--days", type=int, default=180, help="Days of history to consider (default: 180)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Find DB
    db_path = find_db(args.db)
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except Exception as e:
        print(f"ERROR: Cannot open database: {e}", file=sys.stderr)
        sys.exit(1)

    # Discover schema
    schema = get_schema_info(conn)
    
    # Process each skill
    for skill_name in args.skills:
        skill_path, dir_name = find_skill_in_cwd(skill_name)
        
        if not skill_path:
            available = list_available_skills()
            print(f"ERROR: Unknown skill '{skill_name}'", file=sys.stderr)
            print(f"Available skills: {', '.join(available) if available else '(none)'}", file=sys.stderr)
            conn.close()
            sys.exit(2)
        
        skill_info = parse_skill_md(skill_path)
        sessions, candidates, evidence = mine_sessions(
            conn, skill_info, dir_name, schema, 
            days=args.days, limit=args.limit
        )
        
        generate_report(
            skill_info, dir_name, sessions, candidates, evidence,
            skill_info.get("body", ""), args.json
        )

    conn.close()


if __name__ == "__main__":
    main()