---
name: firefox-extension
description: Use when developing Firefox WebExtensions - Manifest V2/V3 configuration, WebExtension APIs, content security policy, web-ext CLI, cross-browser support with the polyfill, AMO submission, or debugging extensions
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - firefox
    - webextension
    - browser-extension
    - mozilla
    - amo
    - manifest-v3
---

> **Objective:** Use this skill to reduce CSP-violation rejections, manifest-schema breakages, AMO-review failures, and cross-browser compat bugs by enforcing manifest-version discipline, CSP-safe patterns, and web-ext-verification rules below.

# Firefox WebExtension Development

## Core Rules (do X because Y)

- **Use `browser` namespace because** it is Promise-based natively in Firefox, avoiding callback boilerplate.
- **Pin `manifest_version: 3` for new extensions because** MV2 is sunsetting and AMO warns on new MV2 submissions.
- **Always include `browser_specific_settings.gecko.id` because** AMO rejects extensions without a unique ID.
- **Set `strict_min_version: "109.0"` for MV3 because** service workers and the `action` API require Firefox 109+.
- **Use `web-ext run --profile-create-new` for testing because** stale profile state causes false positives.

See `references/apis.md` for the complete WebExtension API namespace list (51 APIs) and usage patterns.

## Manifest V3 Rules

See `references/manifest-v3.md` for the full MV3 manifest schema reference.

### MV2 vs MV3 Migration Rules

- **Use `action` instead of `browser_action` because** MV3 requires the unified `action` key (Firefox 109+).
- **Use `background.service_worker` instead of `background.scripts` because** MV3 enforces event-driven, ephemeral background logic.
- **Move `permissions` with host URLs to `host_permissions` because** MV3 separates API permissions from host access.
- **Replace `webRequest` blocking with `declarativeNetRequest` because** MV3 makes `webRequest` non-blocking only (max 30,000 static rules, 5,000 dynamic).
- **Remove all `eval()`, `new Function()`, and dynamic imports because** MV3 CSP forbids remote code and AMO rejects it immediately.
- **Use `addEventListener` instead of inline `onclick=""` because** MV3 CSP blocks inline scripts.

See `references/manifest-keys.md` for the complete manifest key enumeration with Firefox-specific keys.

## Permissions Discipline

See `references/permissions.md` for the full permissions reference with AMO review triggers.

### High-Risk Permissions (AMO Scrutiny)

- **Avoid `<all_urls>` because** it triggers automatic reviewer scrutiny; use specific host patterns instead.
- **Justify `cookies`, `history`, `bookmarks` in AMO notes because** reviewers reject vague justifications.
- **Prefer `activeTab` over `tabs` because** it requests access only when the user interacts with your extension.
- **Use `declarativeNetRequest` instead of `webRequest` for static rules because** it is MV3-compliant and AMO-favored.

## web-ext CLI Rules

### Development Workflow Rules

- **Run `web-ext lint` before every build because** it catches manifest errors and AMO policy violations early.
- **Use `web-ext run --verbose` for debugging because** it shows injection failures and CSP violations in real-time.
- **Test with `--profile-create-new` because** stale cookies/cache mask real-world failures.
- **Run `web-ext build` to create the submission artifact because** it validates the zip structure AMO expects.
- **Sign with `--channel listed` for AMO submission because** unlisted bypasses human review.

See `references/web-ext.md` for the complete web-ext command reference with all flags.

## CSP & Security Rules

See `references/security-crossbrowser.md` for the full CSP reference and cross-browser polyfill patterns.

### CSP-Safe Patterns (do X because Y)

- **Never use `eval()`, `new Function()`, or `Function("...")` because** AMO rejects remote code execution immediately.
- **Escape all dynamic content into DOM nodes instead of `innerHTML` because** CSP blocks inline scripts and XSS.
- **Use `'wasm-unsafe-eval'` only for WebAssembly because** the broader `'unsafe-eval'` triggers AMO rejection.
- **Remove `http://localhost:<port>` from CSP before submission because** it allows remote scripts in production.
- **Bundle all dependencies locally instead of CDN scripts because** CSP forbids remote script sources.

### Cross-Browser Polyfill Rules

- **Use `webextension-polyfill` because** Firefox's `browser` API is Promise-based while Chrome uses callbacks.
- **Feature-detect Firefox-only APIs (`sidebarAction`, `userScripts`) because** they crash in Chrome without guards.
- **Use `browser.action || browser.browserAction` fallback because** MV2/MV3 have different key names.

## AMO Submission Rules

### Pre-Submission Checklist (do X because Y)

- **Verify `web-ext lint` passes with no errors because** AMO's automated gate rejects manifest/schema errors.
- **Ensure `browser_specific_settings.gecko.id` is set because** AMO rejects extensions without a unique ID.
- **Provide 48x48 and 96x96 PNG icons because** AMO's size rules cause automatic rejection.
- **Add a privacy policy URL if collecting data because** AMO requires data collection disclosure.
- **Write a natural description (no keyword stuffing) because** reviewers flag spammy listings.
- **Document permission usage in AMO notes because** vague justifications lead to rejection.

### Rejection Response Rules

- **Read reviewer notes in Developer Hub before resubmitting because** fixes must address the specific issue.
- **Resubmit within 30 days because** the review queue position expires.
- **Add clarifying notes for misunderstandings because** reviewers may approve with explanation.

See `references/testing-amo.md` for the full AMO checklist, debugging commands, and troubleshooting table.

## Deep Dives

Load these reference files on demand for detailed information:

- **WebExtension APIs** (51 namespaces, core patterns, Firefox-specific APIs): `references/apis.md`
- **Manifest V3 Schema** (complete MV3 manifest reference): `references/manifest-v3.md`
- **Manifest Keys** (all keys with Firefox-specific extensions): `references/manifest-keys.md`
- **Permissions** (AMO review triggers, narrower alternatives): `references/permissions.md`
- **web-ext CLI** (complete command reference): `references/web-ext.md`
- **Security & Cross-Browser** (CSP rules, polyfill patterns): `references/security-crossbrowser.md`
- **Testing & AMO** (debugging, troubleshooting, submission checklist): `references/testing-amo.md`

## External References

- [MDN WebExtensions](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions)
- [Extension Workshop](https://extensionworkshop.com/)
- [Manifest V3 Migration Guide](https://extensionworkshop.com/documentation/develop/manifest-v3-migration-guide/)
- [web-ext CLI Reference](https://extensionworkshop.com/documentation/develop/web-ext-command-reference/)
- [AMO Developer Hub](https://addons.mozilla.org/developers/)
- [webextension-polyfill](https://github.com/mozilla/webextension-polyfill)
