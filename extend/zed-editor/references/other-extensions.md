<!-- Loaded on demand from ../SKILL.md — Other extension types deep dive (MCP, slash commands, DAP, themes, snippets) -->

## MCP Server Extensions

### Registration

```toml
[context_servers.my-mcp]
```

### Implementation

```rust
fn context_server_command(
    &mut self,
    _context_server_id: &zed::ContextServerId,
    _project: &zed::Project,
) -> zed::Result<zed::Command> {
    Ok(zed::Command {
        command: "my-mcp-server".to_string(),
        args: vec!["--stdio".to_string()],
        env: std::env::vars().collect(),
    })
}
```

---

## Slash Commands (AI Assistant)

### Registration in extension.toml

```toml
[[slash_commands.my-command]]
description = "Does something useful"
requires_argument = true
```

### Implementation

```rust
fn run_slash_command(
    &self,
    command: zed::SlashCommand,
    args: Vec<String>,
    worktree: Option<&zed::Worktree>,
) -> zed::Result<zed::SlashCommandOutput, String> {
    match command.name.as_str() {
        "my-command" => {
            let result = do_something(&args)?;
            Ok(zed::SlashCommandOutput {
                text: result,
                sections: vec![],
                attachments: vec![],
            })
        }
        _ => Err(format!("Unknown command: {}", command.name)),
    }
}

fn complete_slash_command_argument(
    &self,
    command: zed::SlashCommand,
    _args: Vec<String>,
) -> zed::Result<Vec<zed::SlashCommandArgumentCompletion>> {
    Ok(vec![
        zed::SlashCommandArgumentCompletion {
            label: "option-1".to_string(),
            new_text: "option-1".to_string(),
            run_command_in_query: false,
        },
    ])
}
```

---

## Debugger Extensions (DAP)

### Registration

```toml
[debug_adapters.my-dap]
schema_path = "debug_adapter_schemas/my-dap.json"

[debug_locators.my-locator]
```

### Implementation

```rust
fn get_dap_binary(
    &mut self,
    adapter_name: String,
    _config: zed::DebugTaskDefinition,
    _user_provided_debug_adapter_path: Option<String>,
    worktree: &zed::Worktree,
) -> zed::Result<zed::DebugAdapterBinary, String> {
    let path = worktree
        .which(&adapter_name)
        .ok_or_else(|| format!("{} not found", adapter_name))?;

    Ok(zed::DebugAdapterBinary {
        command: Some(path),
        args: vec![],
        env: worktree.shell_env(),
        connection: None,
        use_tcp: false,
    })
}
```

---

## Theme Extensions

### Theme JSON Structure

Place in `themes/my-theme.json`. Follow schema: https://zed.dev/schema/themes/v0.2.0.json

```json
{
    "name": "My Theme Family",
    "author": "Your Name",
    "themes": [
        {
            "name": "My Dark Theme",
            "appearance": "dark",
            "style": {
                "background": "#1a1b26",
                "foreground": "#a9b1d6",
                "accent": "#7aa2f7",
                "border": "#292e42",
                "border.variant": "#1f2335",
                "surface.background": "#1a1b26",
                "title_bar.background": "#1a1b26",
                "toolbar.background": "#1a1b26",
                "editor.background": "#1a1b26",
                "editor.foreground": "#a9b1d6",
                "editor.gutter.background": "#1a1b26",
                "editor.active_line.background": "#292e42",
                "editor.line_number": "#3b4261",
                "editor.active_line_number": "#a9b1d6",
                "terminal.background": "#1a1b26",
                "terminal.foreground": "#a9b1d6",
                "terminal.ansi.black": "#24283b",
                "terminal.ansi.red": "#f7768e",
                "terminal.ansi.green": "#9ece6a",
                "terminal.ansi.yellow": "#e0af68",
                "terminal.ansi.blue": "#7aa2f7",
                "terminal.ansi.magenta": "#ad8ee6",
                "terminal.ansi.cyan": "#7dcfff",
                "terminal.ansi.white": "#a9b1d6",
                "syntax": {
                    "keyword": { "color": "#bb9af7" },
                    "keyword.control": { "color": "#bb9af7" },
                    "string": { "color": "#9ece6a" },
                    "function": { "color": "#7aa2f7" },
                    "type": { "color": "#7dcfff" },
                    "comment": { "color": "#565f89", "font_style": "italic" },
                    "variable": { "color": "#a9b1d6" },
                    "number": { "color": "#ff9e64" },
                    "operator": { "color": "#89ddff" },
                    "property": { "color": "#73daca" },
                    "constant": { "color": "#ff9e64" },
                    "tag": { "color": "#f7768e" }
                },
                "players": [
                    { "cursor": "#7aa2f7", "selection": "#283457" }
                ]
            }
        },
        {
            "name": "My Light Theme",
            "appearance": "light",
            "style": {
                "background": "#e1e2e7",
                "foreground": "#3760bf",
                "editor.background": "#e1e2e7",
                "editor.foreground": "#3760bf"
            }
        }
    ]
}
```

> Use the [Theme Builder](https://zed.dev/theme-builder) to visually design themes.

---

## Snippet Extensions

### Snippet JSON Format

Place in `snippets/my-language.json`:

```json
{
    "function": {
        "prefix": "fn",
        "body": [
            "fn ${1:function_name}(${2:args}) -> ${3:ReturnType} {",
            "    ${4:// TODO: implement}",
            "}",
            "$0"
        ],
        "description": "Create a new function"
    },
    "test": {
        "prefix": "test",
        "body": [
            "#[test]",
            "fn ${1:test_name}() {",
            "    ${2:// TODO: write test}",
            "}"
        ],
        "description": "Create a test function"
    },
    "struct": {
        "prefix": "struct",
        "body": [
            "struct ${1:Name} {",
            "    ${2:field}: ${3:Type},",
            "}"
        ],
        "description": "Create a struct"
    }
}
```

**Tabstop syntax**: `$0` (final cursor), `${1:placeholder}`, `${2:default_value}`.