---
name: zed-editor
description: Use when developing Zed editor extensions in Rust - extension.toml manifest, LSP server integration, tree-sitter grammars and query files, MCP servers, slash commands, DAP debuggers, themes, snippets, or publishing to the Zed marketplace
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - zed
    - editor
    - extension
    - rust
    - wasm
    - tree-sitter
    - lsp
    - plugin
---

## Overview

Build extensions for the [Zed](https://zed.dev) editor — high-performance, multiplayer code editor built in Rust.

Extensions are **Rust crates compiled to WebAssembly** that run in a sandboxed Wasmtime environment. They can provide languages, themes, debuggers, snippets, MCP servers, and AI slash commands.

---

## Top-Level Metadata

**What**: Creating Zed Editor extensions — Rust/Wasm plugins for language support, themes, debuggers, MCP servers, slash commands, and more. Includes extension manifest structure, language server integration, tree-sitter grammar development, and publishing workflows.

**Why**: Extend Zed to add custom language support, debugging capabilities, AI-powered features, and personalization through themes and snippets. Zed's sandboxed architecture allows safe extension development without compromising core editor stability.

**When**: Use this skill when developing extensions for Zed, whether for production use, personal productivity tools, or contributing to the Zed ecosystem. Ideal for language developers, editor enthusiasts, and Rust developers building Wasm-based extensions.

**Requirements**:
- Rust 1.75+ with rustup installed
- Zed Dev edition (installed locally or via [AppImage](https://zed.dev/download))
- `cargo install zed_extension_api` (latest version from crates.io)
- Tree-sitter CLI (for grammar compilation)
- Node.js 18+ (for npm-based language server installations)
- GitHub account (for publishing extensions)

**See also**:
- [Zed Extension API Documentation](https://zed.dev/docs/extensions)
- [Publishing Extensions to Marketplace](https://github.com/zed-industries/extensions#publishing-your-extension)
- [Zed Extension API Schema](https://github.com/zed-industries/zed/blob/main/crates/zed_extension_api/src/extension.toml.md)
- [Zed GitHub Repository](https://github.com/zed-industries/zed)
- [crates.io: zed_extension_api](https://crates.io/crates/zed_extension_api)

---

## Directory Structure

```
my-extension/
├── extension.toml          # Required manifest
├── Cargo.toml              # Required for Rust extensions (cdylib)
├── src/
│   └── lib.rs              # Extension implementation
├── languages/
│   └── my-language/
│       ├── config.toml     # Language metadata
│       ├── highlights.scm  # Syntax highlighting
│       ├── brackets.scm    # Bracket matching
│       ├── outline.scm     # Code outline
│       ├── indents.scm     # Auto-indentation
│       ├── injections.scm  # Language injections
│       ├── overrides.scm   # Editor behavior overrides
│       ├── textobjects.scm # Text objects (Vim)
│       ├── redactions.scm  # Screen share redaction
│       ├── runnables.scm   # Runnable code detection
│       └── semantic_token_rules.json  # LSP semantic tokens
├── themes/
│   └── my-theme.json       # Theme definitions
├── icon-themes/
│   └── my-icons.json       # Icon theme definitions
└── snippets/
    └── snippets.json        # Snippet definitions
```

---

## Extension Manifest (extension.toml)

```toml
id = "my-extension"
name = "My Extension"
version = "0.1.0"
schema_version = 1
authors = ["Your Name <you@example.com>"]
description = "Provides support for My Language"
repository = "https://github.com/you/my-zed-extension"

# Tree-sitter grammars
[grammars.my-language]
repository = "https://github.com/tree-sitter/tree-sitter-my-language"
rev = "abc123def456"

# Language servers
[language_servers.my-lsp]
name = "My Language Server"
languages = ["My Language"]

# Multi-language server with LSP ID mapping
# [language_servers.my-lsp]
# name = "Whatever LSP"
# languages = ["JavaScript", "HTML", "CSS"]
#
# [language_servers.my-lsp.language_ids]
# "JavaScript" = "javascript"
# "TSX" = "typescriptreact"
# "HTML" = "html"

# Debug adapters
[debug_adapters.my-dap]
schema_path = "debug_adapter_schemas/my-dap.json"

# MCP context servers
[context_servers.my-mcp]

# Agent servers
[agent_servers.my-agent]
name = "My AI Agent"
icon = "icon/agent.svg"

[agent_servers.my-agent.env]
AGENT_LOG_LEVEL = "info"

[agent_servers.my-agent.targets.darwin-aarch64]
archive = "https://github.com/owner/repo/releases/download/v1.0.0/agent-darwin-arm64.tar.gz"
cmd = "./agent"
args = ["--serve"]
sha256 = "abc123..."

[agent_servers.my-agent.targets.linux-x86_64]
archive = "https://github.com/owner/repo/releases/download/v1.0.0/agent-linux-x64.tar.gz"
cmd = "./agent"
args = ["--serve"]
```

---

## Rust Extension Setup

### Cargo.toml

```toml
[package]
name = "my-extension"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
zed_extension_api = "0.1.0"  # Use latest from crates.io
serde = "1.0"
serde_json = "1.0"
```

> **Important**: Use the latest `zed_extension_api` version from [crates.io](https://crates.io/crates/zed_extension_api). Check [compatible Zed versions](https://github.com/zed-industries/zed/blob/main/crates/extension_api#compatible-zed-versions).

### src/lib.rs — Basic Extension

```rust
use zed_extension_api as zed;

struct MyExtension;

impl zed::Extension for MyExtension {
    fn new() -> Self {
        Self
    }
}

zed::register_extension!(MyExtension);
```

---

## Extension Capabilities (Security)

Extensions run sandboxed. Users grant capabilities in settings:

```json
{
    "granted_extension_capabilities": [
        { "kind": "process:exec", "command": "*", "args": ["**"] },
        { "kind": "download_file", "host": "github.com", "path": ["**"] },
        { "kind": "npm:install", "package": "*" }
    ]
}
```

### Restricting Capabilities

```json
{
    "granted_extension_capabilities": [
        { "kind": "process:exec", "command": "cargo", "args": ["**"] },
        { "kind": "download_file", "host": "github.com", "path": ["owner", "repo", "**"] }
    ]
}
```

### Capability Kinds

| Capability | Controls |
|------------|----------|
| `process:exec` | Execute external commands |
| `download_file` | Download files from URLs |
| `npm:install` | Install npm packages |

To disable all capabilities: `"granted_extension_capabilities": []`

---

## Development Workflow

### Prerequisites

- **Rust** installed via [rustup](https://www.rust-lang.org/tools/install) (not Homebrew or system packages)
- Node.js (for some extensions using npm packages)

### Install Dev Extension

1. Open Zed → Extensions page → **Install Dev Extension**
2. Select your extension directory
3. Dev extension overrides any published version

### Debugging

```bash
# Run Zed in foreground for verbose logs
zed --foreground

# View logs in Zed: open command palette → "zed: open log"
# Log file locations:
#   Linux: ~/.config/zed/zed.log
#   macOS: ~/Library/Application Support/zed/zed.log

# stdout/stderr from extensions is forwarded to Zed process
# Use println!/dbg! in Rust code, visible with --foreground
```

### Test Workflow

```bash
# 1. Make changes to extension code
# 2. In Zed: Extensions → click "Install Dev Extension" again to rebuild
# 3. Check Zed.log for errors
# 4. Test language features, LSP, themes, etc.
```

---

## Best Practices

### Extension Structure

```rust
// ✅ GOOD: Clear module organization
src/
├── lib.rs          // Main entry, register languages/themes
├── language.rs     // Language server implementation
├── theme.rs        // Color definitions
└── snippets.rs     // Snippet collections

// ❌ BAD: Everything in one file
```

### Performance

```rust
// Cache expensive operations
fn expensive_computation(&self) -> Result<Value> {
    if let Some(cached) = &self.cached {
        return Ok(cached.clone());
    }
    // ... compute ...
}

// Lazy initialization
fn get_language(&self) -> &Language {
    self.language.get_or_init(|| /* ... */)
}
```

### Testing

```rust
// Test extension loads correctly
#[test]
fn test_extension_loads() {
    let ext = MyExtension::new();
    assert!(ext.activate().is_ok());
}
```

### Do:
- Keep extension size under 1MB
- Use async for I/O operations
- Test on multiple Zed versions
- Always verify crate versions on [crates.io](https://crates.io) before adding dependencies
- Verify language server binary compatibility — ensure LSP supports `--stdio` protocol

### Don't:
- Block the main thread
- Use heavy dependencies
- Hardcode paths (use API methods)
- Assume a crate version compiles without verifying — always recommend the user runs `cargo check` after dependency changes

---

## Known Issues / Pitfalls

### No `cargo binstall` — Zed requires native `cargo install`
- Zed's extension API does not support `cargo binstall` for package installation
- Must use standard `cargo install` command for installing language servers and dependencies
- Pre-built binaries from binstall packages may not work correctly

### Binary download errors — LSP servers not supporting `--stdio` will fail
- Language servers must support the `--stdio` (stdin/stdout) protocol
- Some LSP servers require TCP socket connection instead
- Binary downloads from GitHub may fail if asset naming doesn't match expected patterns
- Always verify LSP documentation before implementing download logic

### Cache invalidation — binary cache at `~/.cache/` needs manual clearing
- Cached LSP binaries stored at `{worktree_root}/.cache/` persist across Zed sessions
- Old/broken cached binaries cause silent failures
- Manual cache clearing required: `rm -rf ~/.cache/zed/{extension_name}/`
- Consider implementing cache age checks in production code

### No GUI access — extensions cannot create custom panels or modify Zed's UI
- Extensions run in sandboxed Wasmtime environment without GUI context
- Cannot create custom panels, dialogs, or windows
- Cannot access or modify Zed's internal UI components
- All output must be text-based or passed through LSP/Slash Command channels

---

## References

**Core Resources:**

- **Zed Editor Website**: https://zed.dev
- **Zed Extension API Docs**: https://zed.dev/docs/extensions
- **Extension Manifest Schema**: https://github.com/zed-industries/zed/blob/main/crates/zed_extension_api/src/extension.toml.md
- **Publishing Guide**: https://github.com/zed-industries/extensions
- **Zed GitHub Repository**: https://github.com/zed-industries/zed
- **crates.io: zed_extension_api**: https://crates.io/crates/zed_extension_api

**Protocols & Standards:**

- **Language Server Protocol (LSP)**: https://microsoft.github.io/language-server-protocol/
- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io/
- **Debug Adapter Protocol (DAP)**: https://microsoft.github.io/debug-adapter-protocol/

**Tools & Utilities:**

- **Tree-sitter CLI**: https://tree-sitter.github.io/tree-sitter/
- **cargo install**: https://doc.rust-lang.org/cargo/commands/cargo-install.html
- **npm CLI**: https://docs.npmjs.com/cli
- **GitHub Releases API**: https://docs.github.com/en/rest/releases/releases

**Additional Documentation:**

- **Zed Theme Builder**: https://zed.dev/theme-builder
- **Zed Extension API Rust Docs**: https://docs.rs/zed_extension_api/latest/zed_extension_api/
- **Extension Naming Guide**: https://github.com/zed-industries/extensions#naming

---

## Deep Dives

Load these reference files on demand for detailed information:

- **LSP Integration** — Language server implementation patterns, binary downloads, npm integration, initialization options: `references/lsp.md`
- **Tree-sitter Language Support** — Grammar configuration, all `.scm` query file types, syntax highlighting captures: `references/tree-sitter.md`
- **Other Extensions** — MCP servers, slash commands, debug adapters, themes, snippets: `references/other-extensions.md`
- **Patterns & Publishing** — Common code patterns, API reference, marketplace publishing workflow: `references/patterns-publishing.md`