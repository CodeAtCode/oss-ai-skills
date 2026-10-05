# Loaded on demand from ../SKILL.md — mutation testing with mutmut to verify tests actually assert something.

Source: https://mutmut.readthedocs.io/en/latest/

## What Mutation Testing Answers That Coverage Cannot

**Coverage says:** "This line ran during tests."  
**Mutation testing says:** "If this line were wrong, would a test notice?"

A high-coverage suite with weak assertions (e.g., no real value checks, just `assert result is not None`) scores badly on mutation testing. Coverage measures execution; mutation testing measures assertion quality.

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
