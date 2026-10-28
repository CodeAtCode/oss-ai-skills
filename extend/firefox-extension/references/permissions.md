> Loaded on demand from SKILL.md when the agent needs the permissions reference with AMO review triggers.

# Permissions Reference

## API Permissions

| Permission | What It Grants | AMO Review Level |
|------------|---------------|------------------|
| `alarms` | Schedule code execution | Automatic |
| `bookmarks` | Read/modify bookmarks | Human |
| `browsingData` | Clear browsing data | Human |
| `clipboardRead` / `clipboardWrite` | Clipboard access | Automatic |
| `cookies` | Read/write cookies | Human |
| `debugger` | Attach debugger | Human (high scrutiny) |
| `declarativeNetRequest` | Rule-based blocking | Automatic |
| `devtools` | DevTools integration | Automatic |
| `downloads` | Download management | Human |
| `find` | Find text in pages | Automatic |
| `history` | Read browsing history | Human (high scrutiny) |
| `identity` | OAuth2 authentication | Automatic |
| `management` | Installed add-ons info | Human |
| `menus` / `contextMenus` | Context menu items | Automatic |
| `notifications` | System notifications | Automatic |
| `permissions` | Runtime permissions | Automatic |
| `privacy` | Privacy settings | Human |
| `proxy` | Request proxying | Human |
| `scripting` | Inject scripts/CSS (MV3) | Automatic |
| `sessions` | Closed tabs/windows | Automatic |
| `storage` | Local/managed storage | Automatic |
| `tabGroups` | Tab groups | Automatic |
| `tabs` | Tab management | Human |
| `theme` | Theme API | Automatic |
| `topSites` | Frequently visited sites | Automatic |
| `webNavigation` | Navigation events | Automatic |
| `webRequest` | Request interception | Human (MV2 only) |
| `windows` | Window management | Automatic |

## Host Permissions

| Pattern | What It Grants | AMO Review Level |
|---------|---------------|------------------|
| `<all_urls>` | All websites | Human (high scrutiny) |
| `https://*/*` | All HTTPS sites | Human |
| `https://*.example.com/*` | Specific domain | Automatic |
| `file:///*` | Local files | Human |

## Narrower Alternatives

| High-Risk Permission | Narrower Alternative |
|---------------------|---------------------|
| `<all_urls>` | Specific host patterns (`https://*.example.com/*`) |
| `tabs` | `activeTab` for on-demand access |
| `webRequest` | `declarativeNetRequest` for static rules |
| `cookies` | `host_permissions` for specific domains |
| `debugger` | `devtools` API for inspection |

## AMO Justification Requirements

**Must justify in AMO notes:**
- `bookmarks` - Explain how bookmarks are used
- `history` - Explain why history access is necessary
- `cookies` - Explain cookie usage and data flow
- `<all_urls>` - Explain why specific hosts are insufficient
- `debugger` - Rarely approved; provide alternative

**Automatic approval (no justification needed):**
- `storage`, `activeTab`, `alarms`, `i18n`, `runtime`, `webNavigation`
