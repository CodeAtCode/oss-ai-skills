# Loaded on demand from ../SKILL.md — property-based testing with Hypothesis.

Source: https://hypothesis.readthedocs.io/en/latest/

## When Properties Beat Example-Based Tests

`pip install hypothesis` — `@given` turns a test into a generator-driven property checked over hundreds of inputs.

Reach for a property instead of hand-picked examples when:

| Signal | Property recipe |
| --- | --- |
| Parser / serializer | `parse(serialize(x)) == x` for generated `x`; parser never crashes on generated garbage |
| Roundtrip pairs | `decode(encode(s)) == s`, plus the inverse on mutated inputs |
| Invariants | Output stays sorted / non-negative / idempotent: `f(f(x)) == f(x)` |
| Algebraic relations | Commutativity, associativity, distribution between two operations |
| Model-based oracle | Simple reference implementation vs the optimized one under test |
| Existing slow oracle | Python reference vs SQL query, naive vs memoized — same result on generated inputs |

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_add_commutative(x, y):
    assert add(x, y) == add(y, x)

@given(payload=st.binary(), level=st.integers(min_value=0, max_value=9))
def test_roundtrip(payload, level):       # keyword form
    assert decompress(compress(payload, level)) == payload
```

Daily-driver strategies:

- Scalars: `integers(min_value=, max_value=)`, `floats`, `booleans`, `text`, `binary`, `dates`, `uuids`
- Collections: `lists(min_size=, max_size=, unique=)`, `sets`, `dictionaries(keys, values)`, `tuples`, `fixed_dictionaries({"a": st.integers()})`
- Selection: `sampled_from([...])` for enums/constants, `one_of(a, b)` for unions, `just(value)` for a fixed value
- Construction: `builds(Model, field=st.text())`, `from_type(MyClass)`, `from_regex(r"[a-z]{3,10}")`
- Recursive data: `recursive(base, extend)` for trees/JSON-like shapes, e.g. `recursive(st.none(), lambda kids: st.lists(kids))`

Reshape with `.filter(pred)`, `.map(fn)`, `.flatmap(fn)`.

Dependent values — `@st.composite` hands your function a `draw` callable; later draws can depend on earlier ones:

```python
@st.composite
def ordered_pair(draw):
    lo = draw(st.integers(min_value=0))
    hi = draw(st.integers(min_value=lo, max_value=lo + 100))
    return (lo, hi)

@given(ordered_pair())
def test_range_slice(pair): ...
```

`.example()` samples a strategy once for interactive exploration (REPL, prototyping). It is not a test API: running it in a suite emits `NonInteractiveExampleWarning`.

## Settings That Actually Bite

Source: https://hypothesis.readthedocs.io/en/latest/reference/api.html#hypothesis.settings

**`deadline` — the #1 surprise.** Default: 200 ms per test case (accepts int/float/`timedelta`). Slow I/O in the test body (network, `time.sleep`, heavy crypto) raises `DeadlineExceeded` even when the test is correct.

```python
@settings(deadline=None)                    # honest fix for I/O-bound properties
@settings(deadline=timedelta(seconds=2))    # or raise the limit
```

**CI behaves differently by default.** When the `CI` env var is set (most CI providers do), the built-in `ci` profile activates: `deadline=None`, `derandomize=True`, `database=None`, `print_blob=True`, `suppress_health_check=[HealthCheck.too_slow]`. A property can pass locally and fail in CI (or the reverse) purely through profile differences — know which profile is active before debugging.

**`max_examples` — default 100.** Hypothesis stops after this many satisfying test cases without finding a failure; inputs rejected by `assume()` / `.filter()` don't count, so heavy filtering silently shrinks your coverage (and eventually trips `HealthCheck.filter_too_much`). Raise it for statistical properties — e.g. `hypothesis.target()` becomes effective above 1000 examples.

**Profiles** for cheap-commit vs deep-run splits:

```python
from hypothesis import settings

settings.register_profile("ci", max_examples=1000)
settings.load_profile("ci")   # e.g. in conftest.py, chosen by env var
```

**Health checks** warn about performance problems (`too_slow`, `filter_too_much`, `data_too_large`, `large_base_example`) except two correctness ones: `function_scoped_fixture` and `differing_executors`. Suppress selectively via `settings(suppress_health_check=[HealthCheck.too_slow])`; never blanket-suppress in shared conftest code.

## Shrinking → Minimal Repro → Promoted Test

Source: https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html

On failure, Hypothesis shrinks the counterexample toward a minimal case and reports it (e.g. `Failing test case: test(f=nan,)`). The shrunk input IS your bug report — reduced without a debugger.

1. **Read the minimal counterexample** and fix the code — or decide the property was wrong (over-strong invariant, missing `assume()`).
2. **Reproduce:** the failure is auto-saved to the `.hypothesis/` example database and replayed on the next run. On CI (`print_blob=True`) the report contains an `@reproduce_failure(...)` blob — handy to replay a CI failure locally, but the blob is version-specific: never commit it.
3. **Promote:** pin the counterexample with `@example` so it becomes a permanent regression test:

```python
@example("")                     # the shrunk counterexample, pinned forever
@example("\x00\x00")             # a second edge case the shrinker missed
@given(st.text())
def test_decode_roundtrip(s):
    assert decode(encode(s)) == s
```

`@example` inputs run on every invocation before generated ones and do not shrink. Prefer `@example` over the database for correctness: the database is a cache that upgrades and source edits can invalidate.

## Pytest Fixture Interaction

Source: https://hypothesis.readthedocs.io/en/latest/reference/api.html#hypothesis.HealthCheck

`@given` re-runs the test body once per example — but a function-scoped pytest fixture runs once per test function, so its state is shared and dirty across examples. Hypothesis raises `HealthCheck.function_scoped_fixture` proactively.

Fixes, in order of preference:

```python
@pytest.fixture(scope="module")
def clean_db(): ...              # 1. widen the scope to match real semantics

@given(st.text())
def test_parsing(clean_db):
    with clean_state(clean_db):  # 2. or reset inside the test, per example
        assert parse_ok()
```

Suppress the health check only when the fixture genuinely needs no reset between examples.

## Closing Card: Properties as Mutation Killers

One property kills an entire class of mutants: `decode(encode(s)) == s` dies against every mutation of `encode` that corrupts any generated input — including mutants no hand-written example test notices. And a shrinking counterexample is a ready-made mutation oracle: pin it with `@example`, and the whole mutant class stays dead on every future run.

Pair with mutation testing (`mutmut`) to find behavior classes your properties still don't cover — see [mutation-testing.md](mutation-testing.md) in this directory.
