> Loaded on demand from SKILL.md when the agent needs the complete manifest key enumeration.

# Manifest Keys Reference

## Required Keys

- `manifest_version` - Must be 2 or 3
- `name` - Extension name (max 45 characters for AMO)
- `version` - Version string (semver recommended)

## Metadata Keys

- `description` - Short description (max 140 characters for AMO)
- `author` - Author name
- `homepage_url` - Extension homepage (required for data collection disclosure)
- `icons` - Extension icons object (`16`, `32`, `48`, `96`, `128`)

## Firefox-Specific Keys

### browser_specific_settings

- `gecko.id` - **Required for AMO** (unique email or UUID)
- `gecko.strict_min_version` - Minimum Firefox version (e.g., "78.0", "109.0")
- `gecko.strict_max_version` - Maximum Firefox version (optional)
- `gecko_android` - Android-specific settings

### Firefox-Only Features

- `userScripts` - Register user scripts (Firefox desktop only)
- `sidebar_action` - Sidebar panel configuration
- `protocol_handlers` - Custom protocol handlers
- `chrome_settings_overrides` - Override homepage/search engine
- `chrome_url_overrides` - Override newtab/bookmarks/history pages

## Background & Scripts

- `background` - Background configuration
  - MV3: `{ service_worker: "background.js", type: "module" }`
  - MV2: `{ scripts: ["background.js"], persistent: false }`
- `content_scripts` - Scripts injected into web pages
- `content_scripts.matches` - URL patterns for injection
- `content_scripts.js` - JavaScript files to inject
- `content_scripts.css` - CSS files to inject
- `content_scripts.run_at` - `document_start`, `document_end`, `document_idle`

## UI Components

- `action` (MV3) / `browser_action` (MV2) - Toolbar button
- `page_action` - Address bar button (shows conditionally)
- `sidebar_action` - Sidebar panel (Firefox-only)
- `options_ui` - Options page configuration
- `devtools_page` - DevTools extension page
- `omnibox` - Address bar integration

## Permissions

- `permissions` - API permissions
- `host_permissions` (MV3) - Host access patterns
- `optional_permissions` - Runtime-requested permissions
- `optional_host_permissions` (MV3) - Runtime-requested host access

## MV3-Only Keys

- `declarative_net_request` - Rule-based request modification
- `host_permissions` - Separated from permissions
- `background.service_worker` - Service worker instead of scripts

## Other Keys

- `commands` - Keyboard shortcuts
- `web_accessible_resources` - Resources accessible from web pages
- `minimum_chrome_version` - Chrome compatibility (ignored by Firefox)
- `incognito` - `split`, `not_allowed`, or `spanning`
