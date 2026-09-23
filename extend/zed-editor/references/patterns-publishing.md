<!-- Loaded on demand from ../SKILL.md — Common patterns, API reference, and publishing deep dive -->

## Common Patterns

### Download + Cache Language Server

```rust
use zed_extension_api as zed;
use std::path::Path;

struct MyExtension {
    cached_path: Option<String>,
}

impl zed::Extension for MyExtension {
    fn new() -> Self {
        Self { cached_path: None }
    }

    fn language_server_command(
        &mut self,
        _id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<zed::Command> {
        if self.cached_path.is_none() {
            let path = self.ensure_server_binary(worktree)?;
            self.cached_path = Some(path);
        }

        let path = self.cached_path.as_ref().unwrap().clone();
        Ok(zed::Command {
            command: path,
            args: vec!["--stdio".to_string()],
            env: worktree.shell_env(),
        })
    }
}

impl MyExtension {
    fn ensure_server_binary(&self, worktree: &zed::Worktree) -> zed::Result<String> {
        let (os, arch) = zed::current_platform();
        let binary_name = format!("my-lsp-{}-{}", os, arch);
        let binary_path = format!("{}/.cache/{}", worktree.root_path(), binary_name);

        if Path::new(&binary_path).exists() {
            return Ok(binary_path);
        }

        let release = zed::latest_github_release(
            "owner/my-lsp",
            zed::GithubReleaseOptions { require_assets: true },
        )?;

        let asset = release.assets.iter()
            .find(|a| a.name.contains(&binary_name))
            .ok_or_else(|| "No matching release asset".to_string())?;

        zed::download_file(&asset.browser_download_url, &binary_path)?;
        zed::make_file_executable(&binary_path)?;

        Ok(binary_path)
    }
}
```

### Check External Tool Availability

```rust
fn language_server_command(
    &mut self,
    _id: &zed::LanguageServerId,
    worktree: &zed::Worktree,
) -> zed::Result<zed::Command> {
    // Prefer local install, fall back to global
    let local_path = format!("{}/node_modules/.bin/typescript-language-server",
        worktree.root_path());

    let command = if Path::new(&local_path).exists() {
        local_path
    } else {
        worktree.which("typescript-language-server")
            .ok_or_else(|| "typescript-language-server not found. Install with: npm i -g typescript-language-server typescript".to_string())?
    };

    Ok(zed::Command {
        command,
        args: vec!["--stdio".to_string()],
        env: worktree.shell_env(),
    })
}
```

---

## Extension API Reference

### Key Types

| Type | Description |
|------|-------------|
| `Command` | Process command with args and env |
| `Worktree` | Project workspace (read files, find binaries, get env) |
| `Project` | Zed project context |
| `LanguageServerId` | LSP server identifier |
| `ContextServerId` | MCP server identifier |
| `CodeLabel` | Syntax-highlighted text label |
| `SlashCommand` | AI assistant slash command definition |
| `SlashCommandOutput` | Command response with text, sections, attachments |
| `DebugAdapterBinary` | Debug adapter process configuration |
| `DebugTaskDefinition` | Debug launch configuration |
| `KeyValueStore` | Persistent key-value storage |

### Key Global Functions

| Function | Description |
|----------|-------------|
| `download_file(url, path)` | Download file (requires capability) |
| `latest_github_release(repo, opts)` | Get latest GitHub release |
| `github_release_by_tag_name(repo, tag)` | Get specific release by tag |
| `npm_install_package(pkg)` | Install npm package |
| `npm_package_latest_version(pkg)` | Get latest npm version |
| `npm_package_installed_version(pkg)` | Check installed version |
| `node_binary_path()` | Get Node.js binary path |
| `make_file_executable(path)` | Set executable permission |
| `current_platform()` | Get (OS, Architecture) tuple |

### Worktree Methods

| Method | Description |
|--------|-------------|
| `id()` | Worktree identifier |
| `root_path()` | Project root path |
| `read_text_file(path)` | Read file content |
| `which(binary_name)` | Find binary in PATH |
| `shell_env()` | Get shell environment variables |

---

## Publishing to Zed Marketplace

### License Requirements

Extension repositories **must** include a license file at the root. Accepted:
- Apache 2.0, MIT, BSD 2-Clause, BSD 3-Clause
- CC BY 4.0, GPLv3, LGPLv3, Unlicense, zlib

### Naming Rules

- Extension IDs must be unique
- Cannot contain "zed", "Zed", or "extension"
- Theme extensions: suffix with `-theme`
- Snippet extensions: suffix with `-snippets`
- Language extensions: use the language name (e.g., `rust`, `python`)

### Publishing Process

1. **Fork** [zed-industries/extensions](https://github.com/zed-industries/extensions)
   > Fork to a personal account (not org) so Zed staff can push changes to your PR.

2. **Add submodule**:
```bash
git submodule add https://github.com/you/my-zed-extension.git extensions/my-extension
git add extensions/my-extension
```

3. **Add to extensions.toml**:
```toml
[my-extension]
submodule = "extensions/my-extension"
version = "0.1.0"

# If extension is in a subdirectory:
# [my-extension]
# submodule = "extensions-my-extension"
# path = "packages/zed"
# version = "0.1.0"
```

4. **Sort entries**:
```bash
pnpm sort-extensions
```

5. **Open PR** to `zed-industries/extensions`

### Updating an Extension

```bash
# Update submodule to latest commit
git submodule update --remote extensions/my-extension

# Update version in extensions.toml to match extension.toml
# Open PR with the changes
```

### Additional Publishing Rules

- Language/debugger extensions must NOT ship binaries — they should download or detect them
- Theme and icon theme extensions must be published separately from language extensions
- If an existing extensions has issues, fix it upstream first before creating a new one