---
name: ghidra
description: Use when running headless Ghidra analysis or decompilation of any binary - analyzeHeadless workflow, processor/language selection for unusual archs (GBA ARM, DOS real-mode, ROMs), export scripts that turn decompiled functions into bounded files, version-diffing binaries, or token-economical agent reading of decompilation output
metadata:
  author: mte90
  version: "1.0.0"
  tags:
    - ghidra
    - reverse-engineering
    - decompilation
    - headless
    - binary-analysis
    - disassembly
---

> **Objective:** Use this skill to prevent wasted analysis time and context blow-ups when reverse-engineering binaries by analyzing headless Ghidra once per binary version and reading exported function artifacts instead of full decompiled listings.

# Ghidra — headless analysis for agents

## Ground rules

- Ghidra analysis is slow (seconds to minutes per binary). Run it **once per binary version**, then work exclusively from exported artifacts.
- Never read a full decompiled listing into context. Export a **function index** first, then pull only the functions the task names.
- One project directory per binary version; reuse the analyzed project instead of re-importing.

## Headless basics

```bash
analyzeHeadless <project_dir> <project_name> \
  -import <binary>            # adds + analyzes + saves to project
  -processor <languageID>     # only when headers don't identify the arch
  -scriptPath <scripts_dir>   # where your export scripts live
  -postScript ExportIndex.py # runs after analysis completes
  -readOnly                   # analysis without saving (Ghidra 10.2+)
  -deleteProject              # scratch one-shot: project discarded at exit
```

First-contact flow:

1. **Index pass:** `-import <bin> -deleteProject -postScript ExportIndex.py` → writes `addr | name | body-size | calling-convention` for every function. This is the shopping list.
2. Read the index, pick the functions relevant to the task.
3. **Depth pass:** re-run with `-postScript ExportFunctions.py <names...>` writing one decompiled `.c` file per function.
4. Cache exports under `/tmp/ghidra-exports/<binary-version>/` — later sessions read files, not the emulator of the disassembly.

Check what you have first: `analyzeHeadless -version`, and list all supported languages with `-listLanguages` (run once locally; IDs vary slightly across Ghidra versions).

## Language IDs worth knowing

| Binary | `-processor` |
|---|---|
| GBA ROM (ARM7TDMI) | `ARM:LE:32:v4` |
| DOS `.exe`/`.com` (real mode) | `x86:LE:16:Real Mode` |
| Modern ELF / PE | omit — auto-detected |
| Other exotic targets | pick from `-listLanguages` output |

## Export scripts (Python / Jython)

ExportIndex: iterate `currentProgram.getFunctionManager().getFunctions(True)`; write one line per function.

ExportFunctions: use `ghidra.app.decompiler.DecompInterface` with a per-function timeout (~30 s), one output file per function, hard-cap each file (~8 KB) — oversized functions get chunk markers instead of truncation.

Write errors loudly (`print` + exit non-zero): a crashed postScript otherwise exits silently and you debug a missing file.

## Version diffing

Two projects (v1, v2), same export scripts. diff the indexes → added/removed/changed function sets; then export and diff only the changed functions. Never re-analyze both sides per question.

## Pitfalls

- Existing project with the same name → hard error. Generate project names from binary + version hash.
- Ghidra's bundled script runtime is Jython-era Python 2; Ghidra 11.x also offers PyGhidra (Python 3). Detect before writing f-strings.
- Wrong decompile ≠ bad code: if output looks anti-analysis-dumped, load anti-reversing-techniques and binary-analysis-patterns before blaming the decompiler.
- Wire-format confusion inside a binary → protocol-reverse-engineering; RAM dumps and crash artifacts → memory-forensics.
