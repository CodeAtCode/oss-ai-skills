> Loaded on demand from SKILL.md when the agent needs game action type tables and argument schemas.

# Game Actions Reference

## Built-in Action Types

### Park Actions

```javascript
// Set park cash
context.executeAction({
    type: 'parksetcash',
    args: { cash: 100000 }
}, callback);

// Set guest generation rate
context.executeAction({
    type: 'parksetguestgenerationrate',
    args: { generationRate: 100 }
}, callback);

// Set park entrance price
context.executeAction({
    type: 'parksetentrancefee',
    args: { price: 500 }
}, callback);

// Open/close park
context.executeAction({
    type: 'parksetopen',
    args: { isOpen: true }
}, callback);
```

### Land Actions

```javascript
// Change land height
context.executeAction({
    type: 'landsetheight',
    args: { 
        x: 32 * 10, 
        y: 32 * 10, 
        height: 10 
    }
}, callback);

// Set land ownership
context.executeAction({
    type: 'landsetrights',
    args: {
        x: 32 * 10,
        y: 32 * 10,
        setRights: true
    }
}, callback);
```

### Scenery Actions

```javascript
// Place small scenery
context.executeAction({
    type: 'smallsceneryplace',
    args: {
        object: 0,           // Scenery object ID
        x: 32 * 10,          // X coordinate in map units
        y: 32 * 10,          // Y coordinate in map units
        z: 0,                // Z height
        direction: 0,        // Rotation (0-3)
        quadrant: 0,         // Quadrant for quarter tile scenery
        primaryColour: 0,    // Primary color
        secondaryColour: 0   // Secondary color
    }
}, callback);

// Remove scenery
context.executeAction({
    type: 'smallsceneryremove',
    args: {
        x: 32 * 10,
        y: 32 * 10,
        z: 0,
        sceneryType: 0
    }
}, callback);
```

### Ride Actions

```javascript
// Build ride
context.executeAction({
    type: 'trackplace',
    args: { 
        ride: 0, 
        trackType: 1, 
        x: 32 * 10, 
        y: 32 * 10, 
        z: 0, 
        direction: 0 
    }
}, callback);

// Set ride status
context.executeAction({
    type: 'ridesetstatus',
    args: {
        ride: 0,
        status: 1  // 0=closed, 1=open, 2=closing, 3=opening
    }
}, callback);

// Set ride price
context.executeAction({
    type: 'ridesetprice',
    args: {
        ride: 0,
        price: 500
    }
}, callback);

// Remove ride
context.executeAction({
    type: 'rideremove',
    args: {
        ride: 0
    }
}, callback);
```

### Guest Actions

```javascript
// Set guest name
context.executeAction({
    type: 'guestsetname',
    args: {
        guest: 0,
        name: 'John Doe'
    }
}, callback);

// Set guest parameters
context.executeAction({
    type: 'guestsetparameters',
    args: {
        guest: 0,
        parameter: 1,  // Happiness, energy, etc.
        value: 200
    }
}, callback);
```

## Custom Game Action Pattern

```javascript
context.registerAction({
    id: 'myplugin.action_id',
    query: function(args) {
        // Validate args - return error object if invalid
        if (!args || args.value < 0) {
            return { error: 'Invalid arguments' };
        }
        
        // Check permissions in multiplayer
        if (network.mode !== 'none') {
            var player = network.getPlayer(args.playerId);
            if (!player || !player.hasPermission('custom_action')) {
                return { error: 'Permission denied' };
            }
        }
        
        return {};  // Success - action can proceed
    },
    execute: function(args) {
        // Mutate game state - only runs on server
        // This is where the actual game state change happens
        
        return {};  // Success
    }
});
```

## Common Error Patterns

```javascript
// Error: Missing validation
context.registerAction({
    id: 'myplugin.bad_action',
    execute: function(args) {
        // This will fail - no query validation!
        park.cash += args.amount;  // args.amount might be undefined
    }
});

// Error: Direct mutation without game action
// park.cash = 100000;  // Fails in multiplayer!

// Error: Using arrow functions (ES5 incompatibility)
context.registerAction({
    id: 'myplugin.arrow_action',
    query: (args) => { return {}; },  // Transpilation fails!
    execute: (args) => { return {}; }
});
```
