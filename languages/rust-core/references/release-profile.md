> Loaded on demand from `SKILL.md` when the agent needs release configuration.

# Cargo.toml Release Profile

```toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true

[profile.dev.package."*"]
opt-level = 3
```
