---
name: thunderbird-extension
description: Use when developing Thunderbird MailExtensions - Manifest V2/V3 configuration, messenger.* APIs for accounts, messages, folders and compose, UI actions, message display scripts, Experiment APIs, ATN submission, or migration from legacy extensions
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - thunderbird
    - mailextension
    - email-extension
    - mozilla
    - atn
    - messenger-api
---

> **Objective:** Use this skill to reduce manifest-schema rejections, messenger-API-typed errors, and ATN-review failures by enforcing manifest-version discipline, API-boundary rules, and permission-scoping patterns below.

# Thunderbird MailExtension Development

## Core Rules

**Do manifest_version discipline because MV2 deprecation will break extensions at Thunderbird 137+.** Set manifest_version: 3 for new extensions; migrate existing MV2 extensions now.

**Do declare messenger.* permissions explicitly because missing permissions fail silently at runtime.** Enumerate every API namespace in permissions before calling it.

**Do use Experiment APIs only when messenger.* cannot reach required functionality because reviewers reject unnecessary Experiment access.** Cite the missing built-in API in submission notes.

**Do validate message content before processing because untrusted email data causes XSS in display scripts.** Sanitize HTML, escape user input, verify MIME types.

**Do use vCard format for contacts in MV3 because legacy contacts API is removed.** Call messenger.addressBooks.contacts.create with vCard string, not name/email fields.

**Do implement onStartup/onShutdown in Experiment APIs because missing cleanup causes crashes on extension reload.** Unregister observers, clear caches, remove listeners.

**Do place extension ID in browser_specific_settings.gecko.id because ATN rejects extensions without stable IDs.** Generate UUID-formatted ID, do not use auto-generated values.

**Do set strict_min_version to "128.0" because older Thunderbird versions lack MV3 support.** Test on Thunderbird 128 ESR minimum.

## UI Actions

**Do attach listeners to action.onClicked because extensions with no popup need click handlers.** Register in background.js, not in popup script.

**Do update badge text asynchronously because setBadgeText returns a Promise.** Awaiting prevents race conditions with badge color updates.

**Do use compose_action for compose-window tools because message_display_action only works in message view.** Match button location to API scope.

## Message Display Scripts

**Do execute display scripts via messenger.scripting.messageDisplay.executeScript in MV3 because manifest declaration is removed.** Call dynamically after tab loads.

**Do limit display script APIs to runtime/storage/i18n because full messenger.* is unavailable.** Communicate with background via runtime.sendMessage for privileged operations.

**Do validate message DOM before manipulation because email content varies widely.** Check element existence, handle plain-text vs HTML, catch parsing errors.

## MV2 → MV3 Migration Decision Guide

**Do migrate now because Thunderbird 137 removes MV2 support.** Priority order:
1. Replace browser_action with action
2. Migrate background.scripts to background.service_worker
3. Convert composeScripts to scripting.compose
4. Update contacts API to messenger.addressBooks.contacts.*

**Do not use messenger.contacts.* in MV3 because it is removed.** Use messenger.addressBooks.contacts.quickSearch and contacts.create with vCard.

**Do test display scripts on both HTML and plain-text messages because rendering differs.** Verify script handles text/plain bodies gracefully.

## Deep Dives

See references for detailed API catalogs loaded on demand:

- **Messenger APIs** — Complete messenger.* reference (accounts, messages, folders, addressBooks, compose, mailTabs): `./references/messenger-apis.md`
- **Experiment APIs** — Custom Experiment API development: `./references/experiment-apis.md`
- **ATN Submission** — Publishing workflow and review criteria: `./references/atn-submission.md`
- **Testing & Migration** — Debugging, testing workflow, legacy migration: `./references/testing-migration.md`

**Do structure extensions with clear separation because monolithic files become unmaintainable.** Pattern:
```
my-extension/
├── manifest.json
├── background.js          # Event handlers, API orchestration
├── popup.html/js          # UI, user interaction
├── compose_popup.html/js  # Compose window UI
├── message_popup.html/js  # Message view UI
├── message_content.js     # Display script (limited API)
├── api/                   # Experiment APIs (if needed)
│   └── myapi/
│       ├── schema.json
│       └── implementation.js
├── icons/                 # 16, 32, 64 px
└── _locales/              # i18n strings
```

## Error Handling

**Do wrap async calls with explicit error logging because silent failures hide bugs.** Log error message plus context (message ID, folder, operation).

**Do check messenger.runtime.lastError after promises because unresolved errors accumulate.** Clear lastError before next operation.

**Do return structured error objects because callers need to distinguish failure modes.** Include error type, offending values, suggested fix.

## Performance

**Do use messages.query with filters because server-side filtering is faster than client-side.** Avoid list() + filter manually for large folders.

**Do debounce rapid events because user actions fire multiple times.** Throttle onMessage, onMessageDisplayed handlers.

**Do paginate large message lists because loading all messages blocks the UI.** Use limit/offset in queries.

## Security

**Do validate all user input before storage because unvalidated data corrupts state.** Schema-validate permissions, folder IDs, message IDs.

**Do sanitize HTML before injection because email content may contain scripts.** Use DOMParser, strip dangerous elements.

**Do use minimal permissions because excessive permissions trigger ATN review rejection.** Request only what the extension needs.

**Do not store sensitive data unencrypted because storage.local is readable.** Encrypt passwords, tokens before storage.

## Differences from Firefox WebExtensions

**Do use messenger.* for mail APIs because browser.* lacks email functionality.** messenger.accounts, messenger.messages, messenger.compose are Thunderbird-specific.

**Do expect content scripts to work only in web tabs because email content is sandboxed.** Use message_display_scripts for email body access.

**Do implement Experiment APIs for XPCOM access because WebExtensions cannot reach internals.** Experiments bridge the gap but require justification.
## Quick Reference

### Essential Permissions

```json
{
  "permissions": [
    "storage",           // Data persistence
    "messagesRead",      // Read message content
    "messagesMove",      // Move/copy/delete
    "addressBooks",      // Contact access
    "compose",           // Compose windows
    "accountsRead",      // Account listing
    "accountsFolders"    // Folder access
  ]
}
```

### Essential APIs

```javascript
// Messages — list, get, query, update, move, delete
messenger.messages.list(folderId)
messenger.messages.get(messageId)
messenger.messages.query({ from, unread, limit })
messenger.messages.update(messageId, { read: true })
messenger.messages.move([messageId], destinationFolderId)

// Folders — get, create, rename, delete
messenger.folders.get(folderId)
messenger.folders.getSubFolders(account)
messenger.folders.create(accountId, name)

// Compose — open, modify, send
messenger.compose.beginNew({ to, subject, body })
messenger.compose.getComposeDetails(tabId)
messenger.compose.onBeforeSend.addListener(handler)
messenger.compose.beginNew({ to, subject, body })
messenger.compose.getComposeDetails(tabId)
messenger.compose.onBeforeSend.addListener(handler)

// Address Books — vCard-only in MV3
messenger.addressBooks.list()
messenger.addressBooks.contacts.create(addressBookId, { vCard })
messenger.addressBooks.contacts.quickSearch(query)

// Display — event-driven
messenger.messageDisplay.onMessageDisplayed.addListener(handler)
messenger.messageDisplay.getDisplayedMessage(tabId)
```

### Workflow

1. **Develop:** Load temporarily via Debug Add-ons
2. **Debug:** Inspect background/popup via DevTools
3. **Test:** Verify on HTML and plain-text messages
4. **Build:** Create .zip with manifest and all scripts
5. **Submit:** Upload to ATN with inline privacy policy
6. **Review:** Respond within 10 days
7. **Publish:** Extension goes live after approval

## References

- [Thunderbird Developer Hub](https://developer.thunderbird.net/add-ons/)
- [Supported APIs](https://developer.thunderbird.net/add-ons/mailextensions/supported-webextension-api)
- [MV3 Migration Guide](https://github.com/thunderbird/webext-docs/blob/beta-mv2/guides/manifestV3.rst)
- [Example Extensions](https://github.com/thunderbird/webext-examples)
- [Experiment Support](https://github.com/thunderbird/thunderbird/webext-support)
- [ATN Developer Hub](https://addons.thunderbird.net/developers/)
- [ATN Review Policy](https://thunderbird.github.io/atn-review-policy/)
