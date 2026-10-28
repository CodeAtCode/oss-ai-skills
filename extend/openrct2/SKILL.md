---
name: openrct2
description: Use when developing OpenRCT2 plugins in TypeScript - plugin registration and game actions, window and widget UI, event hooks, park, map, ride and entity access, network API, storage, or ES5 runtime constraints
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - openrct2
    - plugin
    - javascript
    - typescript
    - game-modding
    - rollercoaster-tycoon
    - scripting
---

> **Objective:** Use this skill to reduce desynced multiplayer actions, ES5-transpilation failures, event-hook leak incidents, and game-action rejection bugs by enforcing action-validation discipline, ES5-compatible patterns, and hook-cleanup rules below.

# OpenRCT2 Plugin Development

Develop plugins (scripts) for OpenRCT2 using JavaScript/TypeScript to extend the game with custom windows, game actions, event hooks, and multiplayer features.

## Overview

OpenRCT2 plugins run in Duktape (ES5 runtime). Key capabilities:

- **JavaScript/TypeScript** - ES5 compatible, use transpilers for ES6+
- **Game Actions** - Multiplayer-synchronized state mutations
- **UI Windows** - Custom windows with widgets
- **Hooks** - Subscribe to game events
- **Network API** - TCP sockets for localhost communication
- **Hot Reload** - Real-time plugin development

### Plugin Directory

Place `.js` files in the `plugin` directory:

- **Windows**: `C:\Users\YourName\Documents\OpenRCT2\plugin\`
- **Mac**: `/Users/YourName/Library/Application Support/OpenRCT2/plugin/`
- **Linux**: `$XDG_CONFIG_HOME/OpenRCT2/plugin/` or `$HOME/.config/OpenRCT2/plugin/`

Access via game: **Red toolbox button → Open custom content folder**

## Plugin Types

Do **do not mutate game state in local plugins because the server rejects direct mutations in multiplayer**. Use game actions instead.

```javascript
// Local plugin - info windows only
registerPlugin({
    name: 'Local Info Plugin',
    version: '1.0',
    type: 'local',  // Available to all players in multiplayer
    main: function() {
        // Can only use game actions, not direct mutations
        // Good for: info windows, tools, dashboards
    }
});
```

Remote plugins load only on server and distribute to clients. **Mutate game state only in the execute context of custom game actions because that is the only server-side entry point**.

```javascript
// Remote plugin - server-side state mutation
registerPlugin({
    name: 'Remote Game Plugin',
    version: '1.0',
    type: 'remote',  // Server-side, synced to clients
    main: function() {
        // Can mutate game state in custom game action execute()
    }
});
```

Intransient plugins stay loaded across park changes and in title screen. **Use `context.sharedStorage` for persistence because park storage clears on park load**.

```javascript
// Intransient plugin - persistent across parks
registerPlugin({
    name: 'Global Plugin',
    version: '1.0',
    type: 'intransient',  // Never unloaded
    main: function() {
        // Active in title screen and across parks
        // Use context.sharedStorage for persistence
    }
});
```

## Game Actions

Game actions are the **recommended way** to mutate game state, ensuring multiplayer synchronization.

### Validate Game Action Args Before Execute Because the Server Rejects Invalid Actions and Desyncs Multiplayer

Custom game actions must implement both `query` (validation) and `execute` (mutation). The `query` phase runs client-side to check permissions and args; `execute` runs server-side to mutate state.

```javascript
context.registerAction({
    id: 'myplugin.award_cash',
    query: function(args) {
        // Validation - return error object if invalid
        if (args.amount < 0) {
            return { error: 'Amount must be positive' };
        }
        if (args.amount > 100000) {
            return { error: 'Amount too large' };
        }
        // Check permissions in multiplayer
        if (network.mode !== 'none') {
            var player = network.getPlayer(args.playerId);
            if (!player || !player.hasPermission('modify_park')) {
                return { error: 'No permission' };
            }
        }
        return {};  // Success
    },
    execute: function(args) {
        // Actual game state mutation - only runs on server
        park.cash += args.amount;
        return {};  // Success
    }
});
```

See `references/game-actions.md` for built-in action type tables and argument schemas.

## Best Practices

### Check UI Availability Because Headless Servers Lack the UI API

Do check `typeof ui !== 'undefined'` before using UI APIs because headless servers crash on undefined API access.

### Use Game Actions for Mutations Because Direct State Changes Fail in Multiplayer

Do use `context.executeAction()` for all state mutations because direct property assignments like `park.cash =` are rejected by the server in multiplayer.

### Namespace Your Data Because Unnamespaced Keys Conflict Across Plugins

Do use namespaced keys like `MyPlugin.Settings.Enabled` instead of `Settings.Enabled` because multiple plugins writing to the same key will overwrite each other's data.

### Handle Errors Because Action Failures Must Be Logged

Do check `result.error` in every action callback because failed actions silent without error handling make debugging impossible.

### Clean Up On Unload Because Event Hooks Leak Memory

Do track all `context.setInterval()` IDs and call `clearInterval()` on the `plugin.unloaded` event because unsubscribed hooks continue running after plugin reload, causing memory leaks and duplicate executions.

## ES5 Limitations

OpenRCT2 uses Duktape (ES5). ES6+ features require transpilation. **Avoid arrow functions because the ES5 runtime transpilation fails on them**.

### Not Supported

```javascript
// Arrow functions - transpilation fails
var func = () => {};

// Classes - transpilation fails
class MyClass {}

// let/const - transpilation fails
let x = 1;

// Template literals - transpilation fails
`Hello ${name}`

// Spread operator - transpilation fails
[...arr]

// Destructuring - transpilation fails
var { x } = obj;

// find/includes - transpilation fails
arr.find(x => x > 0);
arr.includes(5);
```

### ES5 Alternatives

```javascript
// Function expressions - works
var func = function() {};

// Constructor functions - works
function MyClass() {}

// var - works
var x = 1;

// String concatenation - works
'Hello ' + name

// Array methods - works
arr.filter(function(x) { return x > 0; })[0];
arr.indexOf(5) !== -1;
```

## Distribution

### Publishing

1. **GitHub Releases** - Recommended, attach compiled `.js`
2. **openrct2plugins.org** - Community plugin repository

### Versioning

```javascript
registerPlugin({
    name: 'My Plugin',
    version: '1.2.3',  // Semantic versioning
    minApiVersion: 34,  // Minimum OpenRCT2 API version
    targetApiVersion: 34,  // Target API for behavior
});
```

## Deep Dives

Load these reference files on demand for detailed API information:

- **Window and Widget UI** - Window creation, widgets (ListView, GroupBox, tabs), events → `references/ui.md`
- **Hooks and Map Access** - Event subscriptions, park info, map tiles, rides, entities → `references/hooks-map.md`
- **Network, Storage, Hot Reload, Debugging** - TCP sockets, storage APIs, development workflow → `references/network-storage.md`
- **Game Actions Reference** - Built-in action types, argument schemas, custom action patterns → `references/game-actions.md`

## References

- **OpenRCT2 Scripting Docs**: https://github.com/OpenRCT2/OpenRCT2/blob/develop/distribution/scripting.md
- **API Types**: https://github.com/OpenRCT2/OpenRCT2/blob/develop/distribution/openrct2.d.ts
- **Plugin Samples**: https://github.com/OpenRCT2/plugin-samples
- **Community Plugins**: https://openrct2plugins.org/
- **Duktape Engine**: https://duktape.org/
