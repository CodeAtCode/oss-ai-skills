> Loaded on demand from SKILL.md when the agent needs the full MV3 manifest schema reference.

# Manifest V3 Schema Reference

## Complete MV3 Manifest Structure

```json
{
  "manifest_version": 3,
  "name": "Extension Name",
  "version": "1.0.0",
  "description": "Brief description",
  "author": "Author Name",
  "homepage_url": "https://example.com",
  "icons": {
    "16": "icons/icon-16.png",
    "48": "icons/icon-48.png",
    "96": "icons/icon-96.png"
  },

  "browser_specific_settings": {
    "gecko": {
      "id": "extension@example.com",
      "strict_min_version": "109.0"
    },
    "gecko_android": {
      "strict_min_version": "109.0"
    }
  },

  "background": {
    "service_worker": "background.js",
    "type": "module"
  },

  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon-16.png",
      "48": "icons/icon-48.png",
      "96": "icons/icon-96.png"
    },
    "default_title": "Extension Title"
  },

  "content_scripts": [
    {
      "matches": ["https://*/*"],
      "js": ["content.js"],
      "css": ["styles.css"],
      "run_at": "document_idle",
      "all_frames": false
    }
  ],

  "permissions": ["storage", "activeTab"],
  "host_permissions": ["https://api.example.com/*"],

  "optional_permissions": ["bookmarks"],

  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self';"
  },

  "web_accessible_resources": [
    {
      "resources": ["images/*"],
      "matches": ["https://*/*"]
    }
  ],

  "commands": {
    "open-options": {
      "suggested_key": {
        "default": "Ctrl+Shift+O"
      },
      "description": "Open options page"
    }
  },

  "options_ui": {
    "page": "options.html",
    "open_in_tab": false
  },

  "sidebar_action": {
    "default_panel": "sidebar.html",
    "default_title": "Sidebar"
  },

  "devtools_page": "devtools.html"
}
```

## Key MV3 Changes from MV2

| MV2 Key | MV3 Equivalent | Notes |
|---------|---------------|-------|
| `browser_action` | `action` | Unified API since Firefox 109+ |
| `background.scripts` | `background.service_worker` | Event-driven, ephemeral |
| `permissions` (with hosts) | `host_permissions` | Separated in MV3 |
| N/A | `declarative_net_request` | Replaces blocking `webRequest` |
