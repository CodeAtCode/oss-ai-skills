<!-- Loaded on demand from ../SKILL.md — Language Server Integration deep dive -->

## Language Server (LSP) Integration

### Configuration in extension.toml

```toml
[language_servers.my-language-server]
name = "My Language LSP"
languages = ["My Language"]
```

### Implementation

```rust
use zed_extension_api as zed;

struct MyExtension {
    cached_binary_path: Option<String>,
}

impl zed::Extension for MyExtension {
    fn new() -> Self {
        Self { cached_binary_path: None }
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<zed::Command> {
        // Option 1: Use binary from PATH
        let path = worktree
            .which("my-language-server")
            .ok_or_else(|| "my-language-server not found in PATH".to_string())?;

        Ok(zed::Command {
            command: path,
            args: vec!["--stdio".to_string()],
            env: worktree.shell_env(),
        })
    }
}
```

### Downloading Language Server from GitHub

```rust
fn language_server_command(
    &mut self,
    _language_server_id: &zed::LanguageServerId,
    worktree: &zed::Worktree,
) -> zed::Result<zed::Command> {
    let binary_path = format!(
        "{}/my-language-server-{}",
        worktree.root_path(),
        std::env::consts::OS
    );

    if !std::path::Path::new(&binary_path).exists() {
        let release = zed::latest_github_release(
            "owner/my-language-server",
            zed::GithubReleaseOptions { require_assets: true },
        )?;

        let (os, arch) = zed::current_platform();
        let asset_name = format!("server-{}-{}.tar.gz", os, arch);

        let asset = release.assets
            .iter()
            .find(|a| a.name.contains(&asset_name))
            .ok_or_else(|| format!("No release asset matching '{}'", asset_name))?;

        zed::download_file(&asset.browser_download_url, &binary_path)?;
        zed::make_file_executable(&binary_path)?;
    }

    Ok(zed::Command {
        command: binary_path,
        args: vec!["--stdio".to_string()],
        env: worktree.shell_env(),
    })
}
```

### Using npm Packages

```rust
fn language_server_command(
    &mut self,
    _language_server_id: &zed::LanguageServerId,
    worktree: &zed::Worktree,
) -> zed::Result<zed::Command> {
    if zed::npm_package_installed_version("my-language-server").is_none() {
        zed::npm_install_package("my-language-server")?;
    }

    Ok(zed::Command {
        command: format!("{}/node_modules/.bin/my-language-server",
            zed::node_binary_path()),
        args: vec!["--stdio".to_string()],
        env: worktree.shell_env(),
    })
}
```

### LSP Initialization Options

```rust
fn language_server_initialization_options(
    &mut self,
    _language_server_id: &zed::LanguageServerId,
    _worktree: &zed::Worktree,
) -> zed::Result<Option<serde_json::Value>> {
    Ok(Some(serde_json::json!({
        "settings": {
            "enableFormatting": true,
            "lint": { "enable": true }
        }
    })))
}
```

### Custom Completion Labels

```rust
fn label_for_completion(
    &self,
    _language_server_id: &zed::LanguageServerId,
    completion: zed::lsp::Completion,
) -> Option<zed::CodeLabel> {
    Some(zed::CodeLabel {
        text: completion.label.clone(),
        filter_range: 0..completion.label.len(),
        display_range: 0..completion.label.len(),
        syntax_highlights: vec![],
    })
}
```