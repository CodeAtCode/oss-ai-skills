---
name: rust-core
description: >
  Use when writing, reviewing, or refactoring Rust code. Covers ownership,
  borrowing, error handling, async patterns, API design, memory optimization,
  performance, testing, and common anti-patterns. Targets Rust 1.80+ and
  Edition 2024. Invoke with /rust-core.
metadata:
  author: mte90
  version: "2.0.0"
  tags:
    - rust
    - core
    - ownership
    - error-handling
    - async
    - performance
    - testing
---

> **Objective:** Use this skill to reduce borrow-checker rejections, unwrap panics in production, and data-race incidents by enforcing ownership discipline, error-handling patterns, and concurrency rules below.

# Rust Core

Guide for writing high-quality, idiomatic, and optimized Rust code. Targets Rust 1.80+ and Edition 2024.

**File globs:** `**/*.rs`  
**License:** MIT  
**Sources:** Rust API Guidelines, Rust Performance Book, Rust Design Patterns, ripgrep/tokio/serde/polars codebases

See `references/when-to-apply.md` for usage context.

## Edition 2024 Changes (Rust 1.85+)

| Change | Impact | Action |
|--------|--------|--------|
| `unsafe` blocks required for `extern` blocks | `extern "C" { ... }` now needs `unsafe { extern "C" { ... } }` | Wrap extern blocks in `unsafe` |
| `unsafe_op_in_unsafe_fn` lint | `unsafe fn` body requires explicit `unsafe` blocks for unsafe ops | Add `unsafe { ... }` inside unsafe fns |
| `if let` temporary scope | Temporaries dropped at end of `if let` block | May extend borrow lifetimes |
| `gen` keyword reserved | `gen { ... }` blocks for iterators | Use `gen` for lazy iterators |
| `#[diagnostic::on_unimplemented]` | Better error messages for trait failures | Add to library traits |
| Nested or-patterns | `Some(1 \| 2)` stabilized | Use in match arms |

Run `cargo fix --edition` to apply most changes automatically.

## Rule Categories by Priority

| Priority | Category | Prefix | Rules |
|----------|----------|--------|-------|
| 1 | Ownership & Borrowing | `own-` | 12 |
| 2 | Error Handling | `err-` | 12 |
| 3 | Memory Optimization | `mem-` | 15 |
| 4 | API Design | `api-` | 15 |
| 5 | Async/Await | `async-` | 15 |
| 6 | Compiler Optimization | `opt-` | 12 |
| 7 | Naming Conventions | `name-` | 16 |
| 8 | Type Safety | `type-` | 10 |
| 9 | Testing | `test-` | 13 |
| 10 | Documentation | `doc-` | 11 |
| 11 | Performance Patterns | `perf-` | 11 |
| 12 | Project Structure | `proj-` | 11 |
| 13 | Clippy & Linting | `lint-` | 11 |
| 14 | Anti-patterns | `anti-` | 15 |

Detailed rules live in `rules/` — 14 files, one per prefix group (`ownership.md` covers `own-`, `error-handling.md` covers `err-`, …). Each `## <rule-id>` section inside a category file is one rule, so a grep for a rule id lands directly on it.

See `references/rule-index.md` for the full 179-rule catalog.

## Ownership & Borrowing

**Prefer `&T` borrowing over `.clone()`** because cloning allocates and copies memory unnecessarily when a reference suffices, wasting CPU and memory in hot paths.

**Accept `&[T]` not `&Vec<T>`, `&str` not `&String`** because slice/string references accept any borrowed sequence (including subslices), making functions more flexible without sacrificing safety.

**Use `Cow<'a, T>` for conditional ownership** because some callers can provide borrowed data while others need owned data, avoiding unnecessary clones in the common case.

**Use `Arc<T>` for thread-safe shared ownership, `Rc<T>` for single-threaded** because reference counting enables multiple owners without data races (`Arc` uses atomic ops, `Rc` does not).

**Use `RefCell<T>` (single-thread) or `Mutex<T>`/`RwLock<T>` (multi-thread) for interior mutability** because these types enforce borrowing rules at runtime when compile-time checks cannot verify them.

**Derive `Copy` for small, trivial types** because copy types avoid heap allocation and indirection, but only for types fitting in a few registers (typically ≤16 bytes).

**Move large data instead of cloning** because moving transfers ownership with zero cost, while cloning always allocates and copies.

**Rely on lifetime elision when possible** because explicit lifetimes add verbosity; the compiler infers common patterns correctly in most cases.

See `rules/ownership.md` for detailed rules with failure modes and examples.

## Error Handling

**Use `thiserror` for library error types, `anyhow` for application error handling** because libraries need stable, documented error types (thiserror), while applications prioritize ergonomic propagation (anyhow).

**Return `Result`, don't panic on expected errors** because panics crash the entire program while `Result` lets callers recover or propagate gracefully.

**Add context with `.context()` or `.with_context()`** because error chains show what operation failed and why, making debugging production incidents feasible.

**Never use `.unwrap()` in production code** because `.unwrap()` panics when the value is `None` or `Err`, turning recoverable errors into crashes.

**Use `.expect()` only for programming errors** because `.expect("invariant violated")` documents invariants that should never fail if the code is correct.

**Use `?` operator for clean propagation** because `?` propagates errors without boilerplate, keeping error paths readable.

**Use `#[from]` for automatic error conversion** because `#[from]` generates `From` implementations, reducing glue code for common error types.

**Use `#[source]` to chain underlying errors** because `#[source]` preserves the error chain for debugging, enabling `error.source()` traversal.

**Error messages: lowercase, no trailing punctuation** because Rust convention uses lowercase for error messages (like `std`), and punctuation adds noise.

**Document errors with `# Errors` section** because users need to know what failures to expect and how to handle them.

**Create custom error types, not `Box<dyn Error>`** because custom types enable pattern matching, better diagnostics, and stable APIs.

See `rules/error-handling.md` for detailed rules with failure modes and examples.

## Memory Optimization

**Use `with_capacity()` when size is known** because pre-allocating avoids repeated reallocations as the collection grows.

**Use `SmallVec` for usually-small collections, `ArrayVec` for bounded-size** because stack allocation avoids heap overhead for small sizes, with fallback to heap when needed.

**Box large enum variants to reduce type size** because boxing the largest variant makes the enum size predictable and often smaller overall.

**Use `Box<[T]>` instead of `Vec<T>` when fixed size** because `Box<[T]>` cannot grow/shrink, communicating intent and avoiding capacity overhead.

**Use `clone_from()` to reuse allocations** because `clone_from()` can reuse existing buffers instead of allocating fresh memory.

**Reuse collections with `clear()` in loops** because `clear()` keeps capacity, avoiding repeated allocations in hot loops.

**Avoid `format!()` when string literals work; use `write!()` instead** because `format!()` always allocates, while `write!()` can write to existing buffers.

**Use smallest integer type that fits** because smaller types reduce memory footprint and can improve cache locality.

**Assert hot type sizes to prevent regressions** because `assert!(std::mem::size_of::<T>() <= N)` catches accidental bloat in performance-critical types.

See `rules/memory.md` for detailed rules with failure modes and examples.

## API Design

**Use Builder pattern for complex construction; add `#[must_use]` to builder types** because builders make optional parameters ergonomic, and `#[must_use]` prevents silently dropping configured builders.

**Use newtypes for type-safe distinctions (`UserId(u64)`, `Email`, `Url`)** because newtypes prevent mixing semantically different values that share the same underlying type.

**Use typestate for compile-time state machines** because typestate encodes valid state transitions in the type system, making illegal states unrepresentable.

**Seal traits to prevent external implementations when appropriate** because sealed traits let you add methods later without breaking downstream code.

**Use extension traits to add methods to foreign types** because extension traits add functionality without modifying the original type or requiring ownership.

**Parse into validated types at boundaries** because parsing once at the boundary and using validated types internally prevents invalid data from propagating.

**Accept `impl Into<T>` for flexible string inputs, `impl AsRef<T>` for borrowed inputs** because these patterns accept multiple input types without overloading.

**Add `#[must_use]` to `Result`-returning functions** because `#[must_use]` forces callers to handle errors instead of silently ignoring them.

**Use `#[non_exhaustive]` for future-proof enums/structs** because `#[non_exhaustive]` lets you add fields/variants later without breaking semver.

**Implement `From`, not `Into` (auto-derived)** because `From` is the source; `Into` is automatically implemented for free.

**Implement `Default` for sensible defaults** because `Default` enables `..Default::default()` struct update syntax and builder patterns.

**Implement `Debug`, `Clone`, `PartialEq` eagerly** because these traits are so commonly needed that deriving them early saves friction.

**Gate `Serialize`/`Deserialize` behind feature flag** because serialization dependencies (serde) are heavy; let users opt in only when needed.

See `rules/api-design.md` for detailed rules with failure modes and examples.

## Async/Await

**Use Tokio for production async runtime** because Tokio is the most mature, well-tested async runtime with comprehensive ecosystem support.

**Never hold `Mutex`/`RwLock` across `.await`** because holding a lock across an await point can cause deadlocks if the task yields while another task waits for the lock.

**Use `spawn_blocking` for CPU-intensive work** because `spawn_blocking` runs CPU-bound tasks on a separate thread pool, preventing blocking the async runtime.

**Use `tokio::fs` not `std::fs` in async code** because `tokio::fs` offloads blocking I/O to the thread pool, keeping the async runtime responsive.

**Use `CancellationToken` for graceful shutdown** because cancellation tokens propagate shutdown signals cleanly through async task hierarchies.

**Use `tokio::join!` for parallel operations, `tokio::try_join!` for fallible** because `join!` runs tasks concurrently and `try_join!` short-circuits on first error.

**Use `tokio::select!` for racing/timeouts** because `select!` waits on multiple futures and cancels losers, enabling timeouts and race patterns.

**Use bounded channels for backpressure** because bounded channels prevent producers from overwhelming consumers with unbounded buffering.

**Use `JoinSet` for dynamic task groups** because `JoinSet` manages a collection of tasks with uniform lifecycle management.

**Clone data before await, release locks** because holding data across await points while keeping locks causes deadlocks; clone to break the dependency.

See `rules/async.md` for detailed rules with failure modes and examples.

## Testing

**Use `#[cfg(test)] mod tests { }` with `use super::*;`** because test modules compile only with `cargo test`, keeping test code out of production builds.

**Put integration tests in `tests/` directory** because integration tests exercise the public API from outside the crate, catching breaking changes.

**Structure tests as arrange/act/assert** because this pattern makes test intent clear: setup, exercise, verify.

**Use `#[tokio::test]` for async tests** because `#[tokio::test]` provides the async runtime needed to execute async test code.

**Use `proptest` for property-based testing** because property tests generate many inputs automatically, finding edge cases manual tests miss.

**Use `mockall` for trait mocking; design dependencies as traits** because traits enable dependency injection, making code testable with mocks.

**Use RAII pattern (Drop) for test cleanup** because `Drop` ensures cleanup runs even if tests panic.

**Use `criterion` for benchmarking** because Criterion provides statistically sound benchmarks with regression detection.

**Keep doc examples as executable tests** because `cargo test --doc` runs doc examples, ensuring they stay synchronized with implementation.

**Use `#[should_panic]` for panic tests** because `#[should_panic]` verifies that expected panics actually occur.

**Aim for 80%+ coverage; test edge cases and error paths** because coverage metrics reveal untested code, and error paths are where bugs hide.

See `rules/testing.md` for detailed rules with failure modes and examples.

## Anti-Patterns

The 15 `anti-*` rules are indexed in `references/rule-index.md` with full rationale and ❌/✅ examples in [`rules/anti-patterns.md`](rules/anti-patterns.md).

Common anti-patterns (see detailed rules at the cited line numbers):

- **Don't use `.unwrap()` in production code** → see Error Handling rule at :100
- **Don't clone when borrowing works** → see Ownership rule at :74
- **Don't hold locks across `.await`** → see Async rule at :174
- **Don't accept `&String` when `&str` works** → see Ownership rule at :76
- **Don't use `format!()` in hot paths** → see Memory rule at :132

## Deep Dives

See these reference files for detailed catalogs:

- `references/rule-index.md` — Full 179-rule catalog across all categories
- `references/compiler-errors.md` — Common compiler errors (E0382, E0502, E0716) and quick fixes
- `references/commands.md` — Essential Cargo commands for build/test/lint
- `references/release-profile.md` — Optimized release profile configuration
