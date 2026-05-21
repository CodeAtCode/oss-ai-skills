#BQ|---
#RB|name: zed-editor
#SN|description: "Zed Editor extensions - Rust/Wasm plugins, LSP servers, Tree-sitter grammars, themes, MCP servers, slash commands, debug adapters"
#PN|metadata:
#VW|  author: mte90
#RP|  version: 1.0.0
#QJ|  tags:
#MS|    - zed
#HR|    - editor
#PB|    - extension
#WQ|    - rust
#MX|    - wasm
#VX|    - tree-sitter
#RW|    - lsp
#BZ|    - plugin
#ZY|---
#HX|
#BB|## Overview
#YT|
#MP|Build extensions for the [Zed](https://zed.dev) editor — high-performance, multiplayer code editor built in Rust.
#RJ|
#ZS|Extensions are **Rust crates compiled to WebAssembly** that run in a sandboxed Wasmtime environment. They can provide languages, themes, debuggers, snippets, MCP servers, and AI slash commands.
#NV|
#RZ|
#BB|## Top-Level Metadata
#YT|
#RB|**What**: This skill covers creating Zed Editor extensions — Rust/Wasm plugins for language support, themes, debuggers, MCP servers, slash commands, and more. Includes extension manifest structure, language server integration, tree-sitter grammar development, and publishing workflows.
#MP|
#RB|**Why**: Extend Zed to add custom language support, debugging capabilities, AI-powered features, and personalization through themes and snippets. Zed's sandboxed architecture allows safe extension development without compromising core editor stability.
#MP|
#RB|**When**: Use this skill when developing extensions for Zed, whether for production use, personal productivity tools, or contributing to the Zed ecosystem. Ideal for language developers, editor enthusiasts, and Rust developers building Wasm-based extensions.
#MP|
#RB|**Requirements**:
#MP|- Rust 1.75+ with rustup installed
#MP|- Zed Dev edition (installed locally or via [AppImage](https://zed.dev/download))
#MP|- `cargo install zed_extension_api` (latest version from crates.io)
#MP|- Tree-sitter CLI (for grammar compilation)
#MP|- Node.js 18+ (for npm-based language server installations)
#MP|- GitHub account (for publishing extensions)
#MP|
#RB|**See also**:
#MP|- [Zed Extension API Documentation](https://zed.dev/docs/extensions)
#MP|- [Publishing Extensions to Marketplace](https://github.com/zed-industries/extensions#publishing-your-extension)
#MP|- [Zed Extension API Schema](https://github.com/zed-industries/zed/blob/main/crates/zed_extension_api/src/extension.toml.md)
#MP|- [Zed GitHub Repository](https://github.com/zed-industries/zed)
#MP|- [crates.io: zed_extension_api](https://crates.io/crates/zed_extension_api)
#MP|
#YT|
#HH|---
#JT|
#BP|## Directory Structure
#XW|
#BZ|```
#NQ|my-extension/
#HS|├── extension.toml          # Required manifest
#BN|├── Cargo.toml              # Required for Rust extensions (cdylib)
#XN|├── src/
#XB|│   └── lib.rs              # Extension implementation
#VK|├── languages/
#WZ|│   └── my-language/
#ZR|│       ├── config.toml     # Language metadata
#TM|│       ├── highlights.scm  # Syntax highlighting
#TB|│       ├── brackets.scm    # Bracket matching
#XY|│       ├── outline.scm     # Code outline
#WR|│       ├── indents.scm     # Auto-indentation
#XK|│       ├── injections.scm  # Language injections
#BV|│       ├── overrides.scm   # Editor behavior overrides
#YP|│       ├── textobjects.scm # Text objects (Vim)
#ZP|│       ├── redactions.scm  # Screen share redaction
#SY|│       ├── runnables.scm   # Runnable code detection
#SJ|│       └── semantic_token_rules.json  # LSP semantic tokens
#NI|├── themes/
#NP|│   └── my-theme.json       # Theme definitions
#KS|├── icon-themes/
#YT|│   └── my-icons.json       # Icon theme definitions
#MQ|└── snippets/
#KQ|    └── snippets.json        # Snippet definitions
#PT|```
#RS|
#NP|---
#QS|
#NP|## Extension Manifest (extension.toml)
#VN|
#JM|```toml
#RP|id = "my-extension"
#XN|name = "My Extension"
#BY|version = "0.1.0"
#VZ|schema_version = 1
#JM|authors = ["Your Name <you@example.com>"]
#TS|description = "Provides support for My Language"
#VV|repository = "https://github.com/you/my-zed-extension"
#VV|
#XR|# Tree-sitter grammars
#WZ|[grammars.my-language]
#XJ|repository = "https://github.com/tree-sitter/tree-sitter-my-language"
#KT|rev = "abc123def456"
#S|
#TX|# For local development, use file:// URL
#BS|# [grammars.my-language]
#TS|# repository = "file:///path/to/tree-sitter-my-language"
#N|
#VM|# Language servers
#VW|[language_servers.my-lsp]
#PM|name = "My Language Server"
#NY|languages = ["My Language"]
#HV|
#GR|# Multi-language server with LSP ID mapping
#WZ|# [language_servers.my-lsp]
#RZ|# name = "Whatever LSP"
#XJ|# languages = ["JavaScript", "HTML", "CSS"]
#MK|#
#PM|# [language_servers.my-lsp.language_ids]
#JT|# "JavaScript" = "javascript"
#ST|# "TSX" = "typescriptreact"
#XX|# "HTML" = "html"
#WQ|
#WR|# Debug adapters
#WP|[debug_adapters.my-dap]
#ZS|schema_path = "debug_adapter_schemas/my-dap.json"
#RK|
#WX|# MCP context servers
#PV|[context_servers.my-mcp]
#Y|
#VX|# Agent servers
#PV|[agent_servers.my-agent]
#BR|name = "My AI Agent"
#BV|icon = "icon/agent.svg"
#X|
#BM|[agent_servers.my-agent.env]
#XJ|AGENT_LOG_LEVEL = "info"
#TS|
#TM|[agent_servers.my-agent.targets.darwin-aarch64]
#PK|archive = "https://github.com/owner/repo/releases/download/v1.0.0/agent-darwin-arm64.tar.gz"
#VS|cmd = "./agent"
#PQ|args = ["--serve"]
#QZ|sha256 = "abc123..."
#S|
#QW|[agent_servers.my-agent.targets.linux-x86_64]
#MU|archive = "https://github.com/owner/repo/releases/download/v1.0.0/agent-linux-x64.tar.gz"
#VS|cmd = "./agent"
#PQ|args = ["--serve"]
#HV|```
#KZ|
#YQ|---
#HS|
#NP|## Rust Extension Setup
#O|
#HM|### Cargo.toml
#WX|
#JM|```toml
#JZ|[package]
#VK|name = "my-extension"
#NQ|version = "0.1.0"
#ZQ|edition = "2021"
#PT|
#TK|[lib]
#XH|crate-type = ["cdylib"]
#PY|
#YN|[dependencies]
#VR|zed_extension_api = "0.1.0"  # Use latest from crates.io
#HQ|serde = "1.0"
#RZ|serde_json = "1.0"
#TH|```
#TT|
#RR|> **Important**: Use the latest `zed_extension_api` version from [crates.io](https://crates.io/crates/zed_extension_api). Check [compatible Zed versions](https://github.com/zed-industries/zed/blob/main/crates/extension_api#compatible-zed-versions).
#TV|
#SR|### src/lib.rs — Basic Extension
#ZB|
#QR|```rust
#ZM|use zed_extension_api as zed;
#VQ|
#WS|struct MyExtension;
#NX|
#MK|impl zed::Extension for MyExtension {
#RW|    fn new() -> Self {
#QJ|        Self
#KB|    }
#BW|}
#NV|
#BH|zed::register_extension!(MyExtension);
#MR|```
#RT|
#MM|---
#QN|
#SS|## Language Server (LSP) Integration
#VY|
#WK|### Configuration in extension.toml
#QS|
#JM|```toml
#NP|[language_servers.my-language-server]
#VQ|name = "My Language LSP"
#RX|languages = ["My Language"]
#HB|```
#HN|
#ZH|### Implementation
#XH|
#QR|```rust
#ZM|use zed_extension_api as zed;
#BH|
#WW|struct MyExtension {
#SH|    cached_binary_path: Option<String>,
#TZ|}
#JZ|
#MK|impl zed::Extension for MyExtension {
#RW|    fn new() -> Self {
#SK|        Self { cached_binary_path: None }
#PR|    }
#MV|
#MX|    fn language_server_command(
#NT|        &mut self,
#HY|        _language_server_id: &zed::LanguageServerId,
#TT|        worktree: &zed::Worktree,
#PB|    ) -> zed::Result<zed::Command> {
#PY|        // Option 1: Use binary from PATH
#NS|        let path = worktree
#XT|            .which("my-language-server")
#KV|            .ok_or_else(|| "my-language-server not found in PATH".to_string())?;
#ZX|
#QH|        Ok(zed::Command {
#ZJ|            command: path,
#JX|            args: vec!["--stdio".to_string()],
#JP|            env: worktree.shell_env(),
#TV|        })
#ZW|    }
#ZK|}
#YN|```
#MH|
#VV|### Downloading Language Server from GitHub
#HT|
#QR|```rust
#BZ|fn language_server_command(
#JH|    &mut self,
#PV|    _language_server_id: &zed::LanguageServerId,
#BJ|    worktree: &zed::Worktree,
#TP|) -> zed::Result<zed::Command> {
#PM|    let binary_path = format!(
#TR|        "{}/my-language-server-{}",
#QZ|        worktree.root_path(),
#HV|        std::env::consts::OS
#NP|    );
#YZ|
#YB|    if !std::path::Path::new(&binary_path).exists() {
#SM|        let release = zed::latest_github_release(
#YB|            "owner/my-language-server",
#WR|            zed::GithubReleaseOptions { require_assets: true },
#TW|        )?;
#HS|
#YP|        let (os, arch) = zed::current_platform();
#YR|        let asset_name = format!("server-{}-{}.tar.gz", os, arch);
#TK|
#TH|        let asset = release.assets
#TP|            .iter()
#QQ|            .find(|a| a.name.contains(&asset_name))
#PH|            .ok_or_else(|| format!("No release asset matching '{}'", asset_name))?;
#KJ|
#TV|        zed::download_file(&asset.browser_download_url, &binary_path)?;
#SB|        zed::make_file_executable(&binary_path)?;
#XP|    }
#TM|
#BV|    Ok(zed::Command {
#RV|        command: binary_path,
#BM|        args: vec!["--stdio".to_string()],
#MQ|        env: worktree.shell_env(),
#HW|    })
#BP|}
#ZY|```
#WQ|
#XH|### Using npm Packages
#YM|
#QR|```rust
#BZ|fn language_server_command(
#JH|    &mut self,
#PV|    _language_server_id: &zed::LanguageServerId,
#BJ|    worktree: &zed::Worktree,
#TP|) -> zed::Result<zed::Command> {
#NM|    if zed::npm_package_installed_version("my-language-server").is_none() {
#RP|        zed::npm_install_package("my-language-server")?;
#YV|    }
#YZ|
#BV|    Ok(zed::Command {
#PY|        command: format!("{}/node_modules/.bin/my-language-server",
#BM|            zed::node_binary_path()),
#BM|        args: vec!["--stdio".to_string()],
#MQ|        env: worktree.shell_env(),
#NH|    })
#JX|}
#HN|```
#WY|
#YN|### LSP Initialization Options
#QT|
#QR|```rust
#TK|fn language_server_initialization_options(
#JH|    &mut self,
#PV|    _language_server_id: &zed::LanguageServerId,
#ZK|    _worktree: &zed::Worktree,
#RH|) -> zed::Result<Option<serde_json::Value>> {
#MJ|    Ok(Some(serde_json::json!({
#QQ|        "settings": {
#MS|            "enableFormatting": true,
#JK|            "lint": { "enable": true }
#SQ|        }
#NH|    })))
#QX|}
#TH|```
#QN|
#QB|### Custom Completion Labels
#XN|
#QR|```rust
#XN|fn label_for_completion(
#SZ|    &self,
#PV|    _language_server_id: &zed::LanguageServerId,
#VQ|    completion: zed::lsp::Completion,
#YN|) -> Option<zed::CodeLabel> {
#VM|    Some(zed::CodeLabel {
#XX|        text: completion.label.clone(),
#WJ|        filter_range: 0..completion.label.len(),
#YK|        display_range: 0..completion.label.len(),
#HZ|        syntax_highlights: vec![],
#RS|    })
#NB|}
#XP|```
#RN|
#YY|---
#JS|
#JT|## Language Support (Tree-sitter)
#BV|
#WN|### Language config.toml
#TW|
#QZ|Place in `languages/my-language/config.toml`:
#PS|
#JM|```toml
#TN|name = "My Language"
#MW|grammar = "my-language"               # Must match grammar name in extension.toml
#VJ|path_suffixes = ["myl", "mylang"]     # File extensions
#WV|line_comments = ["// ", "# "]          # Line comment prefixes
#QK|block_comments = [{ start = "/*", end = "*/" }]
#TZ|tab_size = 4
#YN|hard_tabs = false
#WZ|first_line_pattern = "^#!.*myl"       # Shebang detection
#PH|word_characters = ["#", "$", "-"]     # Non-alpha chars that are part of words
#QV|
#HS|# Bracket auto-closing configuration
#JV|brackets = [
#ZR|    { start = "{", end = "}", close = true, newline = true },
#MV|    { start = "(", end = ")", close = true, newline = true },
#MY|    { start = "[", end = "]", close = true, newline = true },
#TV|    { start = "\"", end = "\"", close = true, newline = false, not_in = ["string"] },
#RR|]
#PS|
#MN|# Scope-specific overrides
#VT|[overrides.string]
#XJ|completion_query_characters = ["-", "."]
#VZ|```
#PV|
#VX|### Tree-sitter Query Files
#BQ|
#ZK|All `.scm` files go in `languages/my-language/`.
#XK|
#YN|#### highlights.scm — Syntax Highlighting
#NX|
#TR|```scheme
#TR|(string) @string
#PX|(comment) @comment
#SW|(number) @number
#HW|(keyword) @keyword
#KR|(function name: (identifier) @function)
#NB|(type_identifier) @type
#VQ|(identifier) @variable
#HB|(property_identifier) @property
#PQ|(operator) @operator
#WM|(constant) @constant
#MW|(boolean) @boolean
#BY|```
#MB|
#PY|**Supported captures:**
#RY|| Capture | Description |
#QB||---------|-------------|
#SM|| `@string` | String literals |
#NV|| `@string.escape` | Escaped characters |
#ZB|| `@string.regex` | Regular expressions |
#TR|| `@string.special` | Special strings |
#RW|| `@comment` | Comments |
#XR|| `@comment.doc` | Doc comments |
#WM|| `@keyword` | Keywords |
#XT|| `@number` | Numeric values |
#XP|| `@boolean` | Boolean values |
#MP|| `@function` | Functions |
#ZB|| `@type` | Types |
#JB|| `@type.builtin` | Built-in types |
#VK|| `@variable` | Variables |
#XS|| `@variable.special` | Special variables |
#SV|| `@variable.parameter` | Parameters |
#QN|| `@property` | Properties |
#PM|| `@operator` | Operators |
#KR|| `@constant` | Constants |
#XW|| `@constant.builtin` | Built-in constants |
#VZ|| `@constructor` | Constructors |
#ZW|| `@attribute` | Attributes |
#PT|| `@tag` | Tags |
#NJ|| `@label` | Labels |
#MH|| `@punctuation` | Punctuation |
#JY|| `@punctuation.bracket` | Brackets |
#QW|| `@punctuation.delimiter` | Delimiters |
#RN|| `@preproc` | Preprocessor directives |
#RV|| `@embedded` | Embedded content |
#RW|| `@enum` | Enumerations |
#RZ|| `@variant` | Variants |
#RN|
#KJ|**Fallback captures:** Multiple captures on same node define fallback highlights:
#TR|```scheme
#JK|(type_identifier) @type @variable
#HT|```
#RP|Zed resolves right-to-left: tries `@variable` first, falls back to `@type`.
#XT|
#XK|#### brackets.scm — Bracket Matching
#YY|
#TR|```scheme
#TP|("{" @open "}" @close)
#RJ|("[" @open "]" @close)
#ZS|("(" @open ")" @close)
#XV|("\"" @open "\"" @close) (#set! rainbow.exclude)  ; Exclude from rainbow brackets
#KW|```
#QW|
#HK|#### outline.scm — Code Outline
#ZQ|
#TR|```scheme
#SJ|(function_definition name: (identifier) @name) @item
#VM|(class_definition name: (identifier) @name) @item
#RH|(method_definition name: (identifier) @name) @item
#ZT|```
#HJ|
#TM|Captures: `@name` (item name), `@item` (entire item), `@context` (context info), `@annotation` (decorators, doc comments).
#KS|
#SW|#### indents.scm — Auto-Indentation
#XK|
#TR|```scheme
#ZB|(array "]" @end) @indent
#BQ|(object "}" @end) @indent
#BH|(function_definition body: (block "{" @indent))
#VK|```
#SW|
#VT|#### injections.scm — Language Injections
#MS|
#TR|```scheme
#HJ|(fenced_code_block
#SZ|    (info_string (language) @injection.language)
#XZ|    (code_fence_content) @injection.content)
#QR|
#JQ|((string_content) @injection.content
#RT|    (#set! injection.language "sql"))
#MT|```
#MQ|
#VV|#### textobjects.scm — Vim Text Objects
#XM|
#TR|```scheme
#ZX|(method_definition
#TX|    body: (_
#KY|        "{"
#YJ|        (_)* @function.inside
#TN|        "}")) @function.around
#NX|
#TW|(class_definition
#TX|    body: (_
#VP|        "{"
#WJ|        (_)* @class.inside
#VX|        "}")) @class.around
#SZ|
#TX|(comment)+ @comment.around
#KT|```
#HM|
#ZS|Captures: `@function.around`, `@function.inside`, `@class.around`, `@class.inside`, `@comment.around`, `@comment.inside`.
#QS|
#JZ|#### redactions.scm — Screen Share Privacy
#JX|
#TR|```scheme
#JQ|(pair value: (string) @redact)
#QS|(pair value: (number) @redact)
#BQ|(password_field) @redact
#NP|```
#RJ|
#XW|#### runnables.scm — Runnable Code Detection
#XV|
#TR|```scheme
#XH|(
#SW|    (document
#PT|        (object
#TX|            (pair
#QZ|                key: (string (string_content) @_name
#VZ|                    (#eq? @_name "scripts"))
#SV|                value: (object
#MN|                    (pair
#JS|                        key: (string (string_content) @run))
#VV|                    )
#NP|                )
#RS|            )
#MW|        )
#BR|    )
#XM|)
#BZ|```
#HK|
#ZK|Extra captures (except `_` prefixed) become `ZED_CUSTOM_<capture_name>` env vars.
#SM|
#BT|---
#MZ|
#VY|## MCP Server Extensions
#NT|
#YX|### Registration
#WW|
#JM|```toml
#XW|[context_servers.my-mcp]
#SW|```
#MW|
#ZH|### Implementation
#YS|
#QR|```rust
#KY|fn context_server_command(
#JH|    &mut self,
#KB|    _context_server_id: &zed::ContextServerId,
#ZX|    _project: &zed::Project,
#TP|) -> zed::Result<zed::Command> {
#BV|    Ok(zed::Command {
#TK|        command: "my-mcp-server".to_string(),
#BM|        args: vec!["--stdio".to_string()],
#VQ|        env: std::env::vars().collect(),
#BP|    })
#XB|}
#VW|```
#BM|
#PJ|---
#TH|
#MP|## Slash Commands (AI Assistant)
#MZ|
#QV|### Registration in extension.toml
#BM|
#JM|```toml
#MS|[[slash_commands.my-command]]
#VK|description = "Does something useful"
#MP|requires_argument = true
#PB|```
#JR|
#ZH|### Implementation
#YH|
#QR|```rust
#BB|fn run_slash_command(
#SZ|    &self,
#XW|    command: zed::SlashCommand,
#KV|    args: Vec<String>,
#VB|    worktree: Option<&zed::Worktree>,
#TR|) -> zed::Result<zed::SlashCommandOutput, String> {
#PY|    match command.name.as_str() {
#SB|        "my-command" => {
#WT|            let result = do_something(&args)?;
#RQ|            Ok(zed::SlashCommandOutput {
#SB|                text: result,
#TR|                sections: vec![],
#PT|                attachments: vec![],
#ZY|            })
#BY|        }
#RK|        _ => Err(format!("Unknown command: {}", command.name)),
#TZ|    }
#XK|}
#JX|
#HX|fn complete_slash_command_argument(
#SZ|    &self,
#XW|    command: zed::SlashCommand,
#NR|    _args: Vec<String>,
#RX|) -> zed::Result<Vec<zed::SlashCommandArgumentCompletion>> {
#HP|    Ok(vec![
#TT|        zed::SlashCommandArgumentCompletion {
#VS|            label: "option-1".to_string(),
#BN|            new_text: "option-1".to_string(),
#TQ|            run_command_in_query: false,
#ST|        },
#PY|    ])
#VK|}
#TP|```
#HQ|
#QY|---
#PM|
#BZ|## Debugger Extensions (DAP)
#VN|
#YX|### Registration
#YS|
#JM|```toml
#XQ|[debug_adapters.my-dap]
#KS|schema_path = "debug_adapter_schemas/my-dap.json"
#QT|
#XQ|[debug_locators.my-locator]
#HW|```
#ZT|
#ZH|### Implementation
#RR|
#QR|```rust
#HV|fn get_dap_binary(
#JH|    &mut self,
#ZY|    adapter_name: String,
#XV|    _config: zed::DebugTaskDefinition,
#QJ|    _user_provided_debug_adapter_path: Option<String>,
#BJ|    worktree: &zed::Worktree,
#QX|) -> zed::Result<zed::DebugAdapterBinary, String> {
#YS|    let path = worktree
#BH|        .which(&adapter_name)
#WW|        .ok_or_else(|| format!("{} not found", adapter_name))?;
#XN|
#ZV|    Ok(zed::DebugAdapterBinary {
#JZ|        command: Some(path),
#QR|        args: vec![],
#MQ|        env: worktree.shell_env(),
#ZJ|        connection: None,
#SY|        use_tcp: false,
#BZ|    })
#QK|}
#ZV|```
#PX|
#VP|---
#KX|
#WX|## Theme Extensions
#XP|
#WB|### Theme JSON Structure
#ZH|
#BK|Place in `themes/my-theme.json`. Follow schema: https://zed.dev/schema/themes/v0.2.0.json
#JH|
#YP|```json
#TV|{
#VM|    "name": "My Theme Family",
#PR|    "author": "Your Name",
#NW|    "themes": [
#NK|        {
#VP|            "name": "My Dark Theme",
#XS|            "appearance": "dark",
#TM|            "style": {
#HZ|                "background": "#1a1b26",
#RR|                "foreground": "#a9b1d6",
#MB|                "accent": "#7aa2f7",
#PT|                "border": "#292e42",
#PQ|                "border.variant": "#1f2335",
#HQ|                "surface.background": "#1a1b26",
#PB|                "title_bar.background": "#1a1b26",
#RP|                "toolbar.background": "#1a1b26",
#SP|                "editor.background": "#1a1b26",
#XP|                "editor.foreground": "#a9b1d6",
#NR|                "editor.gutter.background": "#1a1b26",
#NJ|                "editor.active_line.background": "#292e42",
#MQ|                "editor.line_number": "#3b4261",
#TB|                "editor.active_line_number": "#a9b1d6",
#HH|                "terminal.background": "#1a1b26",
#QH|                "terminal.foreground": "#a9b1d6",
#SH|                "terminal.ansi.black": "#24283b",
#ZP|                "terminal.ansi.red": "#f7768e",
#KP|                "terminal.ansi.green": "#9ece6a",
#MR|                "terminal.ansi.yellow": "#e0af68",
#QX|                "terminal.ansi.blue": "#7aa2f7",
#QV|                "terminal.ansi.magenta": "#ad8ee6",
#TR|                "terminal.ansi.cyan": "#7dcfff",
#JT|                "terminal.ansi.white": "#a9b1d6",
#PM|                "syntax": {
#KQ|                    "keyword": { "color": "#bb9af7" },
#NM|                    "keyword.control": { "color": "#bb9af7" },
#KP|                    "string": { "color": "#9ece6a" },
#KM|                    "function": { "color": "#7aa2f7" },
#TR|                    "type": { "color": "#7dcfff" },
#WY|                    "comment": { "color": "#565f89", "font_style": "italic" },
#ZX|                    "variable": { "color": "#a9b1d6" },
#NB|                    "number": { "color": "#ff9e64" },
#PH|                    "operator": { "color": "#89ddff" },
#KN|                    "property": { "color": "#73daca" },
#BV|                    "constant": { "color": "#ff9e64" },
#ZH|                    "tag": { "color": "#f7768e" }
#ZM|                },
#WM|                "players": [
#NT|                    { "cursor": "#7aa2f7", "selection": "#283457" }
#HB|                ]
#YY|            }
#NY|        },
#MP|        {
#NR|            "name": "My Light Theme",
#PS|            "appearance": "light",
#TM|            "style": {
#MB|                "background": "#e1e2e7",
#QV|                "foreground": "#3760bf",
#HZ|                "editor.background": "#e1e2e7",
#VM|                "editor.foreground": "#3760bf"
#HM|            }
#PB|        }
#XP|    ]
#HX|}
#RK|```
#NQ|
#KS|> Use the [Theme Builder](https://zed.dev/theme-builder) to visually design themes.
#ZK|
#ZY|---
#XX|
#KZ|## Snippet Extensions
#QB|
#SQ|### Snippet JSON Format
#VW|
#WJ|Place in `snippets/my-language.json`:
#VS|
#YP|```json
#TB|{
#PP|    "function": {
#PH|        "prefix": "fn",
#ZV|        "body": [
#YZ|            "fn ${1:function_name}(${2:args}) -> ${3:ReturnType} {",
#KM|            "    ${4:// TODO: implement}",
#HX|            "}",
#BP|            "$0"
#QJ|        ],
#VP|        "description": "Create a new function"
#TH|    },
#VZ|    "test": {
#ZY|        "prefix": "test",
#ZV|        "body": [
#ST|            "#[test]",
#WX|            "fn ${1:test_name}() {",
#KV|            "    ${2:// TODO: write test}",
#KV|            "}"
#BM|        ],
#JV|        "description": "Create a test function"
#HH|    },
#ZH|    "struct": {
#VQ|        "prefix": "struct",
#ZV|        "body": [
#TM|            "struct ${1:Name} {",
#XY|            "    ${2:field}: ${3:Type},",
#RM|            "}"
#ZW|        ],
#QM|        "description": "Create a struct"
#PP|    }
#BP|}
#PY|```
#TV|
#ZV|**Tabstop syntax**: `$0` (final cursor), `${1:placeholder}`, `${2:default_value}`.
#WM|
#VK|---
#TT|
#HV|## Extension Capabilities (Security)
#VN|
#WV|Extensions run sandboxed. Users grant capabilities in settings:
#NJ|
#YP|```json
#VR|{
#TZ|    "granted_extension_capabilities": [
#VM|        { "kind": "process:exec", "command": "*", "args": ["**"] },
#WZ|        { "kind": "download_file", "host": "github.com", "path": ["**"] },
#MJ|        { "kind": "npm:install", "package": "*" }
#KJ|    ]
#HW|}
#RJ|```
#NN|
#JV|### Restricting Capabilities
#YR|
#YP|```json
#VS|{
#TZ|    "granted_extension_capabilities": [
#WH|        { "kind": "process:exec", "command": "cargo", "args": ["**"] },
#VV|        { "kind": "download_file", "host": "github.com", "path": ["owner", "repo", "**"] }
#BY|    ]
#BY|}
#NR|```
#RS|
#WS|### Capability Kinds
#RN|
#TT|| Capability | Controls |
#KY||------------|----------|
#HT|| `process:exec` | Execute external commands |
#ZK|| `download_file` | Download files from URLs |
#RP|| `npm:install` | Install npm packages |
#TY|
#ZN|To disable all capabilities: `"granted_extension_capabilities": []`
#HZ|
#JJ|---
#QR|
#BP|## Development Workflow
#VJ|
#YW|### Prerequisites
#SN|
#SR|- **Rust** installed via [rustup](https://www.rust-lang.org/tools/install) (not Homebrew or system packages)
#NZ|- Node.js (for some extensions using npm packages)
#VM|
#HK|### Install Dev Extension
#NV|
#NX|1. Open Zed → Extensions page → **Install Dev Extension**
#XM|2. Select your extension directory
#SK|3. Dev extension overrides any published version
#MT|
#TJ|### Debugging
#YB|
#BV|```bash
#SX|# Run Zed in foreground for verbose logs
#VH|zed --foreground
#NH|
#JV|# View logs in Zed: open command palette → "zed: open log"
#KV|# Log file locations:
#PQ|#   Linux: ~/.config/zed/zed.log
#XH|#   macOS: ~/Library/Application Support/zed/zed.log
#KJ|
#JY|# stdout/stderr from extensions is forwarded to Zed process
#YZ|# Use println!/dbg! in Rust code, visible with --foreground
#JR|```
#XK|
#SR|### Test Workflow
#HR|
#BV|```bash
#XH|# 1. Make changes to extension code
#RN|# 2. In Zed: Extensions → click "Install Dev Extension" again to rebuild
#KB|# 3. Check Zed.log for errors
#ST|# 4. Test language features, LSP, themes, etc.
#NJ|```
#RZ|
#QB|---
#SX|
#PW|## Publishing to Zed Marketplace
#ZX|
#ZT|### License Requirements
#JN|
#XY|Extension repositories **must** include a license file at the root. Accepted:
#XB|- Apache 2.0, MIT, BSD 2-Clause, BSD 3-Clause
#VM|- CC BY 4.0, GPLv3, LGPLv3, Unlicense, zlib
#WR|
#VK|### Naming Rules
#RJ|
#RS|- Extension IDs must be unique
#XW|- Cannot contain "zed", "Zed", or "extension"
#KZ|- Theme extensions: suffix with `-theme`
#KS|- Snippet extensions: suffix with `-snippets`
#KT|- Language extensions: use the language name (e.g., `rust`, `python`)
#TK|
#HS|### Publishing Process
#MV|
#TP|1. **Fork** [zed-industries/extensions](https://github.com/zed-industries/extensions)
#NW|   > Fork to a personal account (not org) so Zed staff can push changes to your PR.
#XX|
#ZN|2. **Add submodule**:
#BV|```bash
#MP|git submodule add https://github.com/you/my-zed-extension.git extensions/my-extension
#TM|git add extensions/my-extension
#MQ|```
#NZ|
#TK|3. **Add to extensions.toml**:
#JM|```toml
#WN|[my-extension]
#QM|submodule = "extensions/my-extension"
#NQ|version = "0.1.0"
#VM|
#WB|# If extension is in a subdirectory:
#XB|# [my-extension]
#SY|# submodule = "extensions-my-extension"
#TY|# path = "packages/zed"
#HP|# version = "0.1.0"
#MZ|```
#NZ|
#WY|4. **Sort entries**:
#BV|```bash
#SP|pnpm sort-extensions
#RV|```
#BN|
#VX|5. **Open PR** to `zed-industries/extensions`
#HP|
#KK|### Updating an Extension
#RH|
#BV|```bash
#BJ|# Update submodule to latest commit
#MN|git submodule update --remote extensions/my-extension
#ST|
#NV|# Update version in extensions.toml to match extension.toml
#YS|# Open PR with the changes
#JX|```
#TK|
#YJ|### Additional Publishing Rules
#JW|
#NW|- Language/debugger extensions must NOT ship binaries — they should download or detect them
#QX|- Theme and icon theme extensions must be published separately from language extensions
#RV|- If an existing extension has issues, fix it upstream first before creating a new one
#ZY|
#HH|---
#PQ|
#WP|## Extension API Reference
#JT|
#XR|### Key Types
#PV|
#ZM|| Type | Description |
#VP||------|-------------|
#PR|| `Command` | Process command with args and env |
#SM|| `Worktree` | Project workspace (read files, find binaries, get env) |
#SX|| `Project` | Zed project context |
#NZ|| `LanguageServerId` | LSP server identifier |
#YW|| `ContextServerId` | MCP server identifier |
#TT|| `CodeLabel` | Syntax-highlighted text label |
#TB|| `SlashCommand` | AI assistant slash command definition |
#QJ|| `SlashCommandOutput` | Command response with text, sections, attachments |
#YQ|| `DebugAdapterBinary` | Debug adapter process configuration |
#WJ|| `DebugTaskDefinition` | Debug launch configuration |
#QY|| `KeyValueStore` | Persistent key-value storage |
#ZB|
#YT|### Key Global Functions
#KY|
#PJ|| Function | Description |
#XX||----------|-------------|
#TX|| `download_file(url, path)` | Download file (requires capability) |
#WM|| `latest_github_release(repo, opts)` | Get latest GitHub release |
#KP|| `github_release_by_tag_name(repo, tag)` | Get specific release by tag |
#HZ|| `npm_install_package(pkg)` | Install npm package |
#BW|| `npm_package_latest_version(pkg)` | Get latest npm version |
#YR|| `npm_package_installed_version(pkg)` | Check installed version |
#XH|| `node_binary_path()` | Get Node.js binary path |
#SS|| `make_file_executable(path)` | Set executable permission |
#TX|| `current_platform()` | Get (OS, Architecture) tuple |
#ZX|
#QW|### Worktree Methods
#RJ|
#YH|| Method | Description |
#RK||--------|-------------|
#RV|| `id()` | Worktree identifier |
#ZX|| `root_path()` | Project root path |
#KS|| `read_text_file(path)` | Read file content |
#TH|| `which(binary_name)` | Find binary in PATH |
#VZ|| `shell_env()` | Get shell environment variables |
#KP|
#SX|---
#QR|
#MP|## Common Patterns
#XM|
#KV|### Download + Cache Language Server
#WJ|
#QR|```rust
#ZM|use zed_extension_api as zed;
#SM|use std::path::Path;
#ZQ|
#WW|struct MyExtension {
#XX|    cached_path: Option<String>,
#HN|}
#QR|
#MK|impl zed::Extension for MyExtension {
#RW|    fn new() -> Self {
#RV|        Self { cached_path: None }
#BR|    }
#RK|
#MX|    fn language_server_command(
#NT|        &mut self,
#VK|        _id: &zed::LanguageServerId,
#TT|        worktree: &zed::Worktree,
#PB|    ) -> zed::Result<zed::Command> {
#SP|        if self.cached_path.is_none() {
#SW|            let path = self.ensure_server_binary(worktree)?;
#QV|            self.cached_path = Some(path);
#BM|        }
#TX|
#HK|        let path = self.cached_path.as_ref().unwrap().clone();
#QH|        Ok(zed::Command {
#ZJ|            command: path,
#JX|            args: vec!["--stdio".to_string()],
#JP|            env: worktree.shell_env(),
#TS|        })
#HN|    }
#YR|}
#MV|
#MV|impl MyExtension {
#KM|    fn ensure_server_binary(&self, worktree: &zed::Worktree) -> zed::Result<String> {
#YP|        let (os, arch) = zed::current_platform();
#KX|        let binary_name = format!("my-lsp-{}-{}", os, arch);
#ZJ|        let binary_path = format!("{}/.cache/{}", worktree.root_path(), binary_name);
#SX|
#JT|        if Path::new(&binary_path).exists() {
#MS|            return Ok(binary_path);
#JZ|        }
#SV|
#SM|        let release = zed::latest_github_release(
#ZK|            "owner/my-lsp",
#WR|            zed::GithubReleaseOptions { require_assets: true },
#KY|        )?;
#NY|
#YB|        let asset = release.assets.iter()
#WN|            .find(|a| a.name.contains(&binary_name))
#QW|            .ok_or_else(|| "No matching release asset".to_string())?;
#HK|
#TV|        zed::download_file(&asset.browser_download_url, &binary_path)?;
#SB|        zed::make_file_executable(&binary_path)?;
#MK|
#VJ|        Ok(binary_path)
#PV|    }
#QP|}
#ZX|```
#HR|
#KQ|### Check External Tool Availability
#RM|
#QR|```rust
#BZ|fn language_server_command(
#JH|    &mut self,
#SM|    _id: &zed::LanguageServerId,
#BJ|    worktree: &zed::Worktree,
#TP|) -> zed::Result<zed::Command> {
#XB|    // Prefer local install, fall back to global
#QZ|    let local_path = format!("{}/node_modules/.bin/typescript-language-server",
#ZM|        worktree.root_path());
#SX|
#WZ|    let command = if Path::new(&local_path).exists() {
#NW|        local_path
#KR|    } else {
#RK|        worktree.which("typescript-language-server")
#HZ|            .ok_or_else(|| "typescript-language-server not found. Install with: npm i -g typescript-language-server typescript".to_string())?
#HJ|    };
#QR|
#BV|    Ok(zed::Command {
#QZ|        command,
#BM|        args: vec!["--stdio".to_string()],
#MQ|        env: worktree.shell_env(),
#NS|    })
#KJ|}
#QP|```
#BZ|
#QH|## Best Practices
#NR|
#SK|### Extension Structure
#HW|
#QR|```rust
#RS|// ✅ GOOD: Clear module organization
#KP|src/
#XZ|├── lib.rs          // Main entry, register languages/themes
#SQ|├── language.rs     // Language server implementation
#HP|├── theme.rs        // Color definitions
#JH|└── snippets.rs     // Snippet collections
#ZS|
#YQ|// ❌ BAD: Everything in one file
#BT|```
#WQ|
#PK|### Performance
#PM|
#QR|```rust
#HY|// Cache expensive operations
#WK|fn expensive_computation(&self) -> Result<Value> {
#WP|    if let Some(cached) = &self.cached {
#RX|        return Ok(cached.clone());
#WJ|    }
#HP|    // ... compute ...
#QK|}
#PV|
#XS|// Lazy initialization
#YQ|fn get_language(&self) -> &Language {
#WH|    self.language.get_or_init(|| /* ... */)
#SR|}
#VW|```
#RZ|
#YZ|### Testing
#MP|
#QR|```rust
#ZM|// Test extension loads correctly
#PP|#[test]
#JK|fn test_extension_loads() {
#TV|    let ext = MyExtension::new();
#VH|    assert!(ext.activate().is_ok());
#VV|}
#WV|```
#XN|
#JP|### Do:
#SZ|- Keep extension size under 1MB
#SQ|- Use async for I/O operations
#BZ|- Test on multiple Zed versions
#XN|
#XZ|- **Always verify crate versions on [crates.io](https://crates.io)** before adding dependencies — Rust's strict semver means a wrong version can cascade into hundreds of compile errors. Check `zed_extension_api` and any third-party crate versions explicitly
#VZ|- **Inform the user when including libraries from third-party repositories** and let them check versions. Highlight files and lines where you include such dependencies so the user can double-check
#TS|- When generating `Cargo.toml` dependencies, mark version numbers as approximate and advise the user to run `cargo check` immediately to verify compatibility
#MS|
#VW|- **Verify language server binary compatibility** — ensure LSP supports `--stdio` protocol for seamless integration
#RJ|
#KQ|### Don't:
#WQ|- Block the main thread
#XZ|- Use heavy dependencies
#VS|- Hardcode paths (use API methods)
#MP|- Assume a crate version compiles without verifying — always recommend the user runs `cargo check` after dependency changes
#PQ|
#HH|---
#PQ|
#BB|## Known Issues / Pitfalls
#YT|
#RB|### No `cargo binstall` — Zed requires native `cargo install`
#MP|- Zed's extension API does not support `cargo binstall` for package installation
#MP|- Must use standard `cargo install` command for installing language servers and dependencies
#MP|- Pre-built binaries from binstall packages may not work correctly
#MP|
#RB|### Binary download errors — LSP servers not supporting `--stdio` will fail
#MP|- Language servers must support the `--stdio` (stdin/stdout) protocol
#MP|- Some LSP servers require TCP socket connection instead
#MP|- Binary downloads from GitHub may fail if asset naming doesn't match expected patterns
#MP|- Always verify LSP documentation before implementing download logic
#MP|
#RB|### Cache invalidation — binary cache at `~/.cache/` needs manual clearing
#MP|- Cached LSP binaries stored at `{worktree_root}/.cache/` persist across Zed sessions
#MP|- Old/broken cached binaries cause silent failures
#MP|- Manual cache clearing required: `rm -rf ~/.cache/zed/{extension_name}/`
#MP|- Consider implementing cache age checks in production code
#MP|
#RB|### No GUI access — extensions cannot create custom panels or modify Zed's UI
#MP|- Extensions run in sandboxed Wasmtime environment without GUI context
#MP|- Cannot create custom panels, dialogs, or windows
#MP|- Cannot access or modify Zed's internal UI components
#MP|- All output must be text-based or passed through LSP/Slash Command channels
#MP|
#BB|---
#YT|
#BB|## References
#YT|
#RM|
#BQ|**Core Resources:**
#MJ|
#MS|- **Zed Editor Website**: https://zed.dev
#HY|- **Zed Extension API Docs**: https://zed.dev/docs/extensions
#RZ|- **Extension Manifest Schema**: https://github.com/zed-industries/zed/blob/main/crates/zed_extension_api/src/extension.toml.md
#WZ|- **Publishing Guide**: https://github.com/zed-industries/extensions
#RZ|- **Zed GitHub Repository**: https://github.com/zed-industries/zed
#PY|- **crates.io: zed_extension_api**: https://crates.io/crates/zed_extension_api
#RP|
#NX|**Protocols & Standards:**
#XV|
#UP|- **Language Server Protocol (LSP)**: https://microsoft.github.io/language-server-protocol/
#TX|- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io/
#VZ|- **Debug Adapter Protocol (DAP)**: https://microsoft.github.io/debug-adapter-protocol/
#KX|
#TS|**Tools & Utilities:**
#NY|
#VH|- **Tree-sitter CLI**: https://tree-sitter.github.io/tree-sitter/
#QZ|- **cargo install**: https://doc.rust-lang.org/cargo/commands/cargo-install.html
#MS|- **npm CLI**: https://docs.npmjs.com/cli
#HY|- **GitHub Releases API**: https://docs.github.com/en/rest/releases/releases
#RP|
#PJ|**Additional Documentation:**
#RK|
#QK|- **Zed Theme Builder**: https://zed.dev/theme-builder
#MK|- **Zed Extension API Rust Docs**: https://docs.rs/zed_extension_api/latest/zed_extension_api/
#TM|- **Extension Naming Guide**: https://github.com/zed-industries/extensions#naming
#BB|
#PJ|
#VW|---
#TV|
#VW|**End of Document**
