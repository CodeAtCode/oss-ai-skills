---
name: tailwind
description: Use when styling with Tailwind CSS v4 - @theme syntax, design token architecture, dark mode strategy, bundle size optimization, component-layer discipline, or migrating from v3
metadata:
  author: mte90
  version: 3.0.0
  tags:
    - css
    - tailwind
    - v4
    - design-tokens
    - dark-mode
    - bundle-size
---

## Overview

Tailwind CSS v4 is a complete rewrite built on the Rust-based Oxide engine. Configuration moves from JavaScript to CSS via `@theme`.

**Key v4 shifts:**
- Config: `tailwind.config.js` → CSS `@theme` block
- Import: `@tailwind base/components/utilities` → `@import "tailwindcss"`
- Dark mode: automatic via `@media (prefers-color-scheme)`
- Content detection: automatic, no `content` array needed

**Browser support:** Safari 16.4+, Chrome 111+, Firefox 128+

## Installation

### Vite (Recommended)
```bash
npm install tailwindcss @tailwindcss/vite
```

```js
// vite.config.js
import tailwindcss from "@tailwindcss/vite";

export default {
  plugins: [tailwindcss()],
};
```

### PostCSS
```bash
npm install -D tailwindcss @tailwindcss/postcss
```

```js
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

### CLI
```bash
npm install -D @tailwindcss/cli
npx @tailwindcss/cli -i input.css -o output.css --watch
```

## Basic Setup

```css
/* input.css */
@import "tailwindcss";

/* Your custom styles and @theme block below */
```

That's it. No `@tailwind base/components/utilities` directives—they're gone.

## Design Token Architecture (v4)

**Single source of truth:** The `@theme` block in your main CSS file defines all design tokens. Every color, spacing value, and font becomes a CSS variable.

### Token Definition Pattern

```css
@import "tailwindcss";

@theme {
  /* Replace, don't extend, the default palette */
  --color-brand: oklch(65% 0.25 250);
  --color-brand-dark: oklch(55% 0.25 250);
  --color-bg: oklch(98% 0.01 250);
  --color-surface: oklch(100% 0 250);
  --color-text: oklch(20% 0.02 250);
  --color-text-muted: oklch(50% 0.02 250);

  /* Spacing scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-display: "Clash Display", sans-serif;
  --font-body: "Satoshi", system-ui, sans-serif;
}
```

### Why Replace Instead of Extend

The default Tailwind palette is generic. Replacing it with your semantic tokens:
- Prevents `bg-blue-500` from leaking into a design that uses `bg-brand-500`
- Makes theme changes a **token edit**, not a class sweep
- Keeps the design system coherent

**Failure mode:** Hardcoding a hex in a component class:

```css
/* BAD: This breaks the theme system */
.card {
  background-color: #3b82f6; /* Can't change via @theme */
}
```

**Correct:**

```css
/* GOOD: Theme change is one token edit */
@theme {
  --color-card-bg: var(--color-surface);
}

.card {
  background-color: var(--color-card-bg);
}
```

### Token-to-Component Mapping

Component styles reference tokens, not raw values:

```css
@layer components {
  .btn {
    background-color: var(--color-brand);
    color: var(--color-surface);
    padding: var(--spacing-sm) var(--spacing-md);
    font-family: var(--font-display);
  }

  .btn:hover {
    background-color: var(--color-brand-dark);
  }
}
```

**Result:** Changing `--color-brand` in `@theme` updates every button site-wide. No search-and-replace.

### The `--color-*` Namespace Rule

Any `--color-*` variable in `@theme` automatically generates utility classes:

```css
@theme {
  --color-primary: oklch(60% 0.18 250);
}
```

Now `bg-primary`, `text-primary`, `border-primary` all work. The engine maps:
- `--color-{name}` → `{prop}-{name}` utilities

## Dark Mode Decision Guide

v4 defaults to `@media (prefers-color-scheme)`—no config needed. But product requirements dictate the right strategy.

### Three Strategies

| Strategy | Mechanism | Best For |
|----------|-----------|----------|
| **Media query** | `@media (prefers-color-scheme: dark)` | Static sites, blogs, no user preference |
| **Manual toggle** | `.dark` class on `<html>` | Apps with user theme preference |
| **Data attribute** | `[data-theme="dark"]` on `<html>` | Multiple themes (light/dark/sepia) |

### Decision Logic

```
Does the product need user-chosen theme that survives reload?
├─ Yes → Use `.dark` class or `data-theme` attribute
│        Persist choice in localStorage
│        Sync with `<html class="dark">` or `<html data-theme="dark">`
│
└─ No → Media query is enough. Do nothing.
```

### Manual Toggle Implementation

```html
<!-- HTML -->
<html class="dark">
  <div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    Content
  </div>
</html>
```

```javascript
// JavaScript toggle
function toggleDark() {
  const html = document.documentElement;
  const isDark = html.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

// Restore on load
const saved = localStorage.getItem("theme");
if (saved === "dark") {
  document.documentElement.classList.add("dark");
}
```

### Avoiding Flash-of-Wrong-Theme

On first paint, before JS runs, the page may flash the wrong theme. Fix:

```html
<!-- Inline script before any CSS/JS -->
<script>
  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (saved === "dark" || (!saved && prefersDark)) {
    document.documentElement.classList.add("dark");
  }
</script>
```

Place this in `<head>` before any stylesheets.

### Why Not `dark:` on Every Color

Adding `dark:` to every utility duplicates tokens:

```html
<!-- BAD: Duplicates token definitions -->
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 border-gray-200 dark:border-gray-800">
```

**Better:** Define semantic tokens that invert automatically:

```css
@theme {
  --color-bg: oklch(100% 0 250);
  --color-bg-dark: oklch(15% 0.02 250);
  --color-text: oklch(20% 0.02 250);
  --color-text-dark: oklch(90% 0.02 250);
}
```

```html
<!-- Use semantic tokens, fewer dark: prefixes -->
<div class="bg-bg text-text">
```

Or use CSS `color-scheme` with automatic contrast:

```css
@layer base {
  :root {
    color-scheme: light dark;
  }
}
```

## Bundle Size and Content Detection

### Content Detection in v4 (`@source`)

v4 automatically scans your project. No `content` array needed. But you can explicitly add sources:

```css
@import "tailwindcss";

@source "../components/**/*.{js,ts,jsx,tsx,vue,svelte}";
@source "../pages/**/*.{js,ts,jsx,tsx}";
```

**Rule:** Content scanning must cover **all template files**, not just JS. If you use Blade, EJS, Handlebars, or PHP templates, add them:

```css
@source "../views/**/*.blade.php";
@source "../templates/**/*.html";
```

### Why Unused Utilities Are Tree-Shaken

The Oxide engine generates only the utilities you actually use. Unused classes are never emitted.

**What inflates output:**
- **Arbitrary values:** `bg-[#3b82f6]` prevents some optimizations because each arbitrary value is unique
- **Icon libraries:** SVG icons in HTML add bulk
- **Plugin CSS:** Custom plugins that emit raw CSS (not utilities)
- **Preflight:** The base reset (~15KB)

### Measuring Bundle Size

```bash
# Build and measure
npx @tailwindcss/cli -i input.css -o output.css
wc -c output.css  # Byte count

# Compare with and without @source directives
```

**Target:** A typical v4 build is 10–30KB gzipped for a medium app.

### Reducing Bundle Size

1. **Use semantic tokens instead of arbitrary values:**
   ```html
   <!-- BAD: Arbitrary value -->
   <div class="bg-[#3b82f6]">

   <!-- GOOD: Token -->
   <div class="bg-brand">
   ```

2. **Exclude unused plugin CSS:**
   ```css
   /* Don't import full plugins if you only need one utility */
   @plugin "@tailwindcss/typography"; /* Only if you need prose */
   ```

3. **Use `@reference` for component styles:**
   ```vue
   <style>
   @reference "../app.css";
   /* Only what you @apply here */
   </style>
   ```

## Component-Layer Discipline

When a utility pattern repeats, decide between three approaches:

### 1. Plain Class (Default)

```css
@layer components {
  .btn {
    display: inline-flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: 0.5rem;
    font-weight: 600;
  }
}
```

**Use when:** The pattern is used in 3+ places and has no variants.

### 2. `@utility` Directive (v4)

```css
@utility btn {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: 0.5rem;
  font-weight: 600;
}
```

**Use when:** You want the pattern to work with variants (`hover:btn`, `dark:btn`).

**Failure in JSX-heavy codebases:** `@apply` re-opens the specificity fight utilities were meant to end:

```css
/* BAD: @apply in a component library */
.btn {
  @apply bg-blue-500 text-white px-4 py-2;
}
```

**Why it fails:**
- The component CSS may load after Tailwind, overriding your utilities
- Specificity becomes unpredictable
- You're back to fighting CSS cascade instead of avoiding it

**Correct:** Define the component in `@layer components` with raw CSS, or use `@utility` if you need variant support.

### 3. Variant with `@variant`

```css
@variant elevated {
  box-shadow: var(--shadow-card);
  background-color: var(--color-surface);
}
```

**Use when:** A state (like "elevated", "pressed", "selected") applies across multiple utilities.

## Migration to v4 Checklist

| Symptom | v3 | v4 | Fix |
|---------|----|----|-----|
| Build fails, unknown directive | `@tailwind base` | `@import "tailwindcss"` | Replace all `@tailwind` directives |
| Config changes ignored | `tailwind.config.js` | `@theme` in CSS | Move config to CSS `@theme` block |
| `extend` not working | `theme.extend` in JS | CSS variables | Define variables directly in `@theme` |
| Custom utilities missing | `@layer utilities` | `@utility` | Rewrite with `@utility` directive |
| Old config needed | N/A | `@config` | Add `@config "../../tailwind.config.js"` (legacy only) |
| Plugin not loading | `plugins: []` in JS | `@plugin` | Use `@plugin "@tailwindcss/typography"` |
| `corePlugins` error | `corePlugins: []` | Not supported | Remove from config, use `@theme` flags |
| `separator` error | `separator: "_"` | Not supported | Use new arbitrary value syntax |

**One-line summary:**
- `@tailwind base/components/utilities` → `@import "tailwindcss"`
- `tailwind.config.js` → CSS `@theme` block
- `extend` → CSS variables in `@theme`
- `@apply` → `@utility` (for variant support)
- Plugins → `@plugin` directive

## Framework Integration

### Vue / Svelte Component Styles

In v4, styles in separate files don't see theme variables by default. Use `@reference`:

```vue
<template>
  <h1>Hello</h1>
</template>

<style>
@reference "../app.css";

h1 {
  @apply text-2xl font-bold text-red-500;
}
</style>
```

### Next.js / Vite

No special config needed if using the official plugin:

```js
// next.config.js or vite.config.js
import tailwindcss from "@tailwindcss/vite";

export default {
  plugins: [tailwindcss()],
};
```

## Common Issues

### Missing Classes After Build
- Ensure `@source` directives cover all template files
- Check that the CSS file with `@theme` is imported by your entry point

### Dark Mode Not Applying
- For manual toggle: add `class="dark"` to `<html>`, not `<body>`
- For media: no config needed, just use `dark:` utilities

### Custom Utilities Not Working
- Use `@utility` directive, not `@layer utilities`
- Ensure the CSS file with `@theme` is imported

### Arbitrary Values Not Parsing
- v3: `bg-[--my-var]`
- v4: `bg-(--my-var)` (parentheses, not brackets)

## Best Practices

### Do:
- Replace the default color palette with semantic tokens in `@theme`
- Use `@utility` for reusable patterns that need variants
- Let dark mode be automatic unless user preference is required
- Use `@source` to explicitly scan non-JS templates
- Define tokens once, reference everywhere via CSS variables

### Don't:
- Hardcode hex values in component CSS
- Use `@apply` in JSX-heavy component libraries
- Add `dark:` to every color utility
- Create a `tailwind.config.js` for new projects
- Use Sass/Less/Stylus—they don't work with v4

## Deep Dives

Load these reference files for detailed information:

- **Theme Configuration** — `@theme` directive syntax, design tokens, colors, spacing, breakpoints, animations — `references/theme.md`
- **Custom Utilities & Variants** — `@utility`, `@variant` directives, utility classes reference — `references/utilities-variants.md`
- **Migration from v3** — Breaking changes, upgrade tool, new features, Preflight changes — `references/migration-v4.md`

## References

- [Tailwind CSS v4 Official Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS v4: Everything You Need to Know](https://tailwindcss.com/blog/tailwindcss-v4)
- [Oxide Engine Announcement](https://tailwindcss.com/blog/oxcide)
- [Migration Guide: v3 to v4](https://tailwindcss.com/docs/upgrade-guide)
- [Tailwind CSS on GitHub](https://github.com/tailwindlabs/tailwindcss)
