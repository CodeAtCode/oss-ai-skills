# AGENTS.md — oss-ai-skills

Rules for creating and maintaining skills in this repository. Read this before editing any `SKILL.md`.

## Repository layout

- `frameworks/` — library and framework skills (django, ratatui, pytest, sqlalchemy, …)
- `languages/` — language-level skills (rust-common-pitfalls)
- `tools/` — CLI tool skills
- `extend/` — plugin and extension skills (firefox-extension, opencode, zed-editor, …)
- Skill directories use kebab-case. One skill per directory.
- `README.md` must stay in sync: one row per skill with trigger-style description, current line count, and tags. Hub skills list sub-skills with `↳` indentation.

## Skill format

Every `SKILL.md` must follow the frontmatter syntax documented in the README ("Skill Format" section), per the [skillreg.dev specification](https://skillreg.dev/docs/skill-md-reference):

- `name` — kebab-case, must match the parent directory name
- `description` — trigger-focused, one line (see writing rules below)
- `metadata.author` — the maintainer name
- `metadata.version` — semver string, bumped on content changes, never downgraded
- `metadata.tags` — lowercase, comma-relevant keywords also used in the README row

Do not introduce alternative frontmatter shapes; the README example is canonical.

## Writing rules

### Description = when to trigger, not what's inside

The frontmatter `description` decides when an agent loads the skill. Write the triggering conditions.

- Bad: `"Rust terminal UI framework - widgets, components, layouts, events, input handling, and state management"`
- Good: `"Use when building terminal UIs in Rust with the ratatui crate - layout system, widget usage, input/event handling, app state architecture, TUI testing, or migrating between ratatui 0.29 and 0.30"`

### Size budget and split pattern

- `SKILL.md` is the entry file: target ≤ 600 lines (~25 KB).
- Above that, split: `SKILL.md` (quick start, core reference, pointers) + `references/*.md` deep dives that the agent loads on demand. Each reference file opens with a one-line note that it is loaded on demand from the entry file.
- Bloat smell: duplicated sections and mirrored documentation (e.g. four widget sections and three examples in one file). Merge duplicates before anything else.
- Splitting into separate skills (hub + sub-skills) is reserved for genuinely independent domains, like `pyqt` or `django-admin`/`django-transaction`.

### Content = concrete tasks, not a history lesson

- Write recipes, decision guides, and pitfalls the agent can act on.
- No feature-history narration: no "added in vX.Y.Z", no release dates sprinkled through sections. Terse minimum-version markers like `(v0.30+)` on a heading are allowed; prose about releases is not.
- Version upgrades and breaking changes live in ONE compact migration table, not in scattered annotations.
- Do not reproduce official documentation — API listings, config tables, color palettes, basic usage prose. Link the official docs; keep only what is non-obvious: pitfalls, recipes, patterns, gotchas.
- Examples must be generic, not project-specific (no real project names, no internal module paths).

### Updating an existing skill

- Updates are additive by default: never delete or replace curated sections to make room for new content. Add new sections; fix facts in place.
- Never downgrade a version number. Bump semver: minor for content additions, major for restructures.
- Cite source URLs for researched material (repo/docs links next to each library or feature).
- After any content change, update the skill's `README.md` row: description and line count.

### Verification

- Before planning a skill rework, run `scripts/skill_update_report.py <skill>` to mine session evidence, and `scripts/analyze_skills.py` for baseline evaluation scores (the latter needs the OpenCode server on `127.0.0.1:18889`).
- After edits: recheck line counts, grep for leftover duplicated sections, verify every internal link in `SKILL.md` resolves to an existing file, confirm no version downgrade happened.
