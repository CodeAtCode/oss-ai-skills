# Loaded on demand from ../SKILL.md — mutation testing (mutmut, cargo-mutants, Stryker) to verify tests actually assert something.

Source: https://mutmut.readthedocs.io/en/latest/

## What Mutation Testing Answers That Coverage Cannot

**Coverage says:** "This line ran during tests."  
**Mutation testing says:** "If this line were wrong, would a test notice?"

A high-coverage suite with weak assertions (e.g., no real value checks, just `assert result is not None`) scores badly on mutation testing. Coverage measures execution; mutation testing measures assertion quality.

## Choose Your Tool

| Language | Tool | Notes |
| --- | --- | --- |
| Python | mutmut | Full workflow in the rest of this file |
| Rust | cargo-mutants | See "cargo-mutants (Rust)" below |
| JavaScript/TypeScript | Stryker | See "Stryker (JavaScript/TypeScript)" below |

## The mutmut Workflow

**Install and run:**
```bash
pip install mutmut
mutmut run  # Runs tests against mutated code
```

**Browse survivors (TUI):**
```bash
mutmut browse  # Interactive TUI to review surviving mutants
```

In the TUI:
- Write a new test that would kill the current mutant
- Press `r` to re-run just that mutant and see if it's now killed
- Press `f` to re-test a function, `m` to re-test a module
- Navigate with arrow keys, `q` to quit

**Inspect a mutant without running the full suite:**
```bash
mutmut apply <mutant_number>  # Writes the mutant to disk
```
**Warning:** Have the mutated file committed under source control first, so you can revert with `git checkout`.

**Example mutations mutmut applies:**
- Integer literals: `5` becomes `6` (add 1)
- Comparisons: `<` becomes `<=`
- Control flow: `break` becomes `continue` and vice versa

## Scoping to Keep It Affordable

**Run on specific modules/functions:**
```bash
mutmut run "my_module*"           # All functions in my_module
mutmut run "my_module.my_function*"  # Specific function
```

**Mutate only covered lines (uses coverage.py):**
```bash
# In pyproject.toml
[tool.mutmut]
mutate_only_covered_lines = true
```
This honors `# pragma: no cover` directives and skips uncovered code entirely.

**Limit stack depth to avoid dragging in irrelevant tests:**
```toml
[tool.mutmut]
max_stack_depth = 3  # Default is higher; lower = faster but more survivors
```
Lower values prevent base utility functions from pulling hundreds of unrelated tests into each mutant run. Tradeoff: speed vs. missing some survivors.

**Cache:** State lives in `mutants/` directory. Delete it to force a full re-run:
```bash
rm -rf mutants/
```

## Noise Control

**Exclude specific mutations:**
```toml
[tool.mutmut]
only_mutate = ["my_module.py"]           # Only mutate these files
do_not_mutate = ["my_module.utils"]      # Skip these modules
do_not_mutate_patterns = ["test_*"]      # Skip files matching pattern
```

**Pragmas in code:**
```python
# Skip entire function/class
def utility_function():  # pragma: no mutate
    return 42

class InternalHelper:  # pragma: no mutate
    pass

# Skip a code region
# pragma: no mutate start
def untestable_helper():
    logger.debug("internal state")
# pragma: no mutate end

# Single-line skip
raise ValueError("invalid")  # pragma: no mutate
```

**Why exclude?** Some mutations are "equivalent" — changing `break` to `continue` might still produce correct behavior (just slower). Don't chase 100% score; decide per survivor whether it's a real test gap or an equivalent mutant, then record the decision with a pragma or config exclusion.

## The Fork Hazard

**POSIX-only:** mutmut requires `fork` support. On Windows, run inside WSL.

**The forkserver escape hatch:**
```toml
[tool.mutmut]
process_isolation = "forkserver"  # Default is "fork"
```
With the default `fork`, every mutant worker inherits whatever the pytest session left behind (monkey-patched sockets, running event loops, background threads, open DB connections, CUDA contexts). Symptoms that trigger switching to `forkserver`:
- Runs hang indefinitely
- Segfaults
- Irreproducible results between runs

**mutmut 3 vs mutmut 2:** mutmut 3 only mutates inside functions. For mutations outside functions (module-level code), the docs point to mutmut 2. Any guidance must name this distinction.

## Equivalent and Unkillable Mutants

**Common patterns:**
- Integer `+1` on a value nothing asserts: `count = 5` → `count = 6` (no test checks the exact value)
- Boundary `<` → `<=` on a condition no test probes: `if x < 10:` with no test at exactly `x = 10`

**The rule:** Do not chase a perfect score. For each survivor:
1. Decide if it's a real test gap → write a test
2. Or an equivalent mutant → exclude with pragma/config
3. Record the decision

## Survivor Decision Log

Record survivors you choose to keep (equivalent, or not worth killing) in a `mutation-decisions.md` file in the skill directory — one line each: mutant id or name, reason (`equivalent`, `untestable`, or `cost`), date, and the exclusion or pragma covering it. The repo linter enforces this format when the file exists:

```text
- format_isqrt_equivalent — equivalent — 2026-10-08 — `--re "isqrt"` scoped out: pure math identity
```

## CI Reality

**Full runs are expensive.** Run on a schedule or on changed paths, not every push:
```yaml
# GitHub Actions example
mutation-testing:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: pip install mutmut
    - run: mutmut run --pytest-args="-q"
```

**Gate on a deliberate threshold, not 100%:**
```bash
# Fail if mutation score below 70%
mutmut run --exit-code-under-coverage=70
```

**Publish the score:**
```bash
mutmut export-cicd-stats
mutmut badge --output mutation-score.json  # Shields endpoint payload
```

**How mutmut stays efficient:** It knows which tests exercise which function, so it runs a subset per mutant rather than the entire suite.

## Configuration Reference

Full configuration in `pyproject.toml`:
```toml
[tool.mutmut]
source_paths = ["src"]                           # Where to find code to mutate
pytest_add_cli_args = "-q"                       # Args for test runs
pytest_add_cli_args_test_selection = "-q"        # Args for test selection
also_copy = ["data/*.json"]                      # Non-Python files needed by tests
max_stack_depth = 3                              # Limit call stack depth
only_mutate = ["my_module.py"]                   # Only mutate these
do_not_mutate = ["utils.py"]                     # Skip these
do_not_mutate_patterns = ["test_*", "*_test.py"] # Skip matching patterns
mutate_only_covered_lines = true                 # Use coverage to skip uncovered
type_check_command = "mypy --json-error-schema"  # Filter type-invalid mutants
debug = false                                    # Debug mode
use_setproctitle = false                         # Use setproctitle for workers
process_isolation = "fork"                       # "fork" or "forkserver"
forkserver_warmup = "collect"                    # "collect", "import", or "none"
preload_modules_file = "preload.txt"             # Modules to preload in forkserver
max_forkserver_restarts = 5                      # Max restarts for hanging workers
log_to_file = true                               # Log to file
log_file_path = "mutmut.log"                     # Log file location
cache_invalidation_files = ["pyproject.toml"]    # Files that invalidate cache
cache_invalidation_exclude = []                  # Exclude from cache invalidation
on_dependency_change = "warn"                    # "warn", "rerun", or "ignore"
use_git_change_detection = false                 # Use git to detect changes
```

Or in `setup.cfg`:
```ini
[mutmut]
source_paths = src
mutate_only_covered_lines = true
max_stack_depth = 3
```

## cargo-mutants (Rust)

Sources: https://github.com/sourcefrog/cargo-mutants and https://mutants.rs/ci.html — full guide at https://mutants.rs

Stable and actively maintained (CalVer releases; v27.1.0 as of 2026-10). Quick start: run `cargo mutants` at the workspace root; to mutate one file only, `-f src/something.rs`.

```bash
cargo mutants                 # Generate and test mutants
cargo mutants -f src/parse.rs # Scope to a single file
cargo mutants --list --diff   # Preview mutant diffs without running tests
cargo mutants --jobs 4        # Parallel mutant testing
```

Selection: `--file` / `--exclude` take paths, `--re` / `--exclude-re` take regexes. Skip a function or module in source with `#[mutants::skip]`.

Timeouts: `--timeout`, `--timeout-multiplier`, `--minimum-test-timeout` control when a mutant is declared to hang the tests instead of failing them.

Results land in machine-readable JSON — `mutants.json` (the run summary) and `outcomes.json` (per-mutant outcomes) — so CI can diff scores over time.

CI: cargo-mutants recommends `--in-place` (mutate the checkout directly instead of copying the tree), and annotation output via `--annotations=github` (or `--annotations=none` to disable). Works with plain `cargo test` or cargo-nextest.

## Stryker (JavaScript/TypeScript)

Source: https://stryker-mutator.io/docs/stryker-js/incremental/ — StrykerJS is the JavaScript/TypeScript engine of Stryker.

The PR-friendly recipe is incremental mode: enable with the `--incremental` flag (or `"incremental": true` in `stryker.config.json`). Available since Stryker 6.2. StrykerJS stores the previous result in `reports/stryker-incremental.json` (path set by the `--incrementalFile` option) and on the next run only re-tests code affected by your diff instead of every mutant.

```bash
npx stryker run --incremental   # Full run on main; later PRs only re-test what changed
```

Commit the `reports/stryker-incremental.json` state file so PR runs start from the main-branch baseline.

## Assertion-Strength Rubric

Mutation testing is the oracle for assertion quality: every surviving mutant points at an assertion too weak to notice the change. Grade your own assertions from weakest to strongest — weaker rungs let mutant classes through:

1. **Smoke** — no assertion, or only "did not raise". Kills nothing.
2. **Truthiness** — `assert result is not None`. Kills only hard-crash mutants.
3. **Exact value** — `assert total() == 42`. Kills value mutants on the asserted path.
4. **Relational / invariant** — roundtrip `decode(encode(x)) == x`, boundary probes at exactly the limit, model-vs-implementation comparisons. Kills entire classes of mutants.

When a mutant survives at rung 3, the fix is usually a rung-4 assertion, not another example test. Industry evidence that this scales: Meta runs mutation testing in production to guide LLM-based test generation — Harman et al., "Mutation-Guided LLM-based Test Generation at Meta", FSE Companion '25, DOI 10.1145/3696630.3728544.
