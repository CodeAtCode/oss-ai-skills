---
name: mgba
description: Use when scripting mGBA emulator automation in Lua - console API, ROM and save state operations, frame callbacks, input handling, memory reading for cheats and RAM watches, sockets, or TAS and speedrunner tooling
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - lua
    - emulator
    - gba
    - gameboy-advance
    - scripting
    - memory-hacking
---

# mGBA Scripting

Lua scripting for mGBA emulator.

> **Objective:** Use this skill to reduce [desynced-TAS runs, memory-read misalignment bugs, frame-callback race incidents, save-state-corruption losses] by enforcing [frame-accurate discipline, address-validation rules, callback-ordering patterns below].

## Overview

Starting with version 0.10, mGBA has built-in scripting capabilities. To use scripting, click "Scripting..." from the Tools menu. Currently, only Lua scripting is supported.

**Key Features:**
- Full memory access (ROM, RAM, MMIO)
- Input manipulation (button presses)
- Save state management
- Callbacks for frame/events
- TCP socket networking
- Console output
- Screenshot capture

### Opening Scripting Console

```
Tools → Scripting...
```

This opens a console where you can load and run Lua scripts.

## Top-Level Objects

### Available Objects

```lua
-- emu: CoreAdapter instance (available when game loaded)
-- C: Exported constants
-- callbacks: CallbackManager instance
-- console: Console instance
-- util: Basic utility library
-- socket: TCP socket library
```

### Console Output

Do use `console.log/warn/error` for debugging because script errors don't crash the emulator.

```lua
console.log("Info message")
console.warn("Warning message")
console.error("Error message")

-- Create text buffer for persistent display
buffer = console.createBuffer("My Buffer")
buffer:print("Text in buffer")
buffer:clear()
```

See `references/classes-registers.md` for TextBuffer class details.

### Utility Functions

```lua
-- Expand bitmask to list
bits = util.expandBitmask(0xFF)  -- {0,1,2,3,4,5,6,7}

-- Make bitmask from list
mask = util.makeBitmask({0, 3, 5})  -- 0x29
```

## Core API

### ROM Operations

Do validate ROM loaded before operations because calling API on unloaded game returns nil.

```lua
-- Load ROM file
success = emu.loadFile("path/to/rom.gba")

-- Get game info
title = emu.getGameTitle()  -- "POKEMON FIRE"
code = emu.getGameCode()   -- "AGB-P-FE"
size = emu.romSize()       -- ROM size in bytes
platform = emu.platform()  -- 0=GBA, 1=GB
checksum = emu.checksum()  -- CRC32
```

### Save States

Do save state before risky operations because crashes lose progress. Do use slots (0-9) for quick saves because file I/O is slow.

```lua
-- Save to file
emu.saveStateFile("path/to/state.state")

-- Load from file
emu.loadStateFile("path/to/state.state")

-- Save to slot (0-9)
emu.saveStateSlot(0)
emu.loadStateSlot(0)

-- Save/load buffer (faster for frequent saves)
buffer = emu.saveStateBuffer()
emu.loadStateBuffer(buffer)

-- Flags: SCREENSHOT=1, SAVEDATA=2, CHEATS=4, RTC=8, METADATA=16
-- ALL = 31
emu.saveStateSlot(0, 31)  -- Save everything
```

See `references/networking.md` for save state flag constants.

### Frame Control

Do run frames in callbacks because manual stepping desyncs TAS runs.

```lua
-- Run one frame
emu.runFrame()

-- Run one instruction
emu.step()

-- Get current frame number
frame = emu.currentFrame()

-- Get cycle info
cycles = emu.frameCycles()    -- Cycles per frame
freq = emu.frequency()         -- Cycles per second
```

### Input Handling

Do clear keys every frame because held keys accumulate and break TAS precision. Do handle input in frame callbacks because timing matters for frame-perfect inputs.

```lua
-- Set all keys at once
emu.setKeys(0x0000)  -- No keys

-- Add keys (OR with existing)
emu.addKeys(C.GBA_KEY.A + C.GBA_KEY.R)

-- Clear keys
emu.clearKeys(C.GBA_KEY.B)

-- Check key state
if emu.getKey(C.GBA_KEY.UP) == 1 then
    print("UP is pressed")
end

-- Get all pressed keys
keys = emu.getKeys()
```

See `references/examples.md` for input patterns (button masher, auto-farmer, TAS helper).

## Memory Access

### Reading Memory

Do validate addresses against ROM map before reading because wrong offsets read garbage and desync the TAS.

```lua
-- Read 8/16/32 bit values
value8 = emu.read8(address)
value16 = emu.read16(address)
value32 = emu.read32(address)

-- Read range
data = emu.readRange(address, length)

-- Read from memory domain
rom = emu.memory["cart0"]
value = rom:read8(offset)
data = rom:readRange(offset, length)
```

### Writing Memory

Do write to RAM domains only because ROM writes corrupt the cartridge image.

```lua
-- Write 8/16/32 bit values
emu.write8(address, value)
emu.write16(address, value)
emu.write32(address, value)
```

### Memory Domains (GBA)

Do use named domains because raw addresses are error-prone.

```lua
-- Available memory domains
emu.memory["bios"]    -- BIOS (0x00000000)
emu.memory["wram"]     -- EWRAM (0x02000000)
emu.memory["iwram"]    -- IWRAM (0x03000000)
emu.memory["io"]       -- MMIO (0x04000000)
emu.memory["palette"]  -- Palette (0x05000000)
emu.memory["vram"]     -- VRAM (0x06000000)
emu.memory["oam"]      -- OAM (0x07000000)
emu.memory["cart0"]    -- ROM (0x08000000)
emu.memory["cart1"]    -- ROM WS1 (0x0a000000)
emu.memory["cart2"]    -- ROM WS2 (0x0c000000)
```

### Memory Domains (GB)

```lua
emu.memory["cart0"]  -- ROM Bank ($0000)
emu.memory["vram"]   -- VRAM ($8000)
emu.memory["sram"]   -- SRAM ($a000)
emu.memory["wram"]   -- WRAM ($c000)
emu.memory["oam"]    -- OAM ($fe00)
emu.memory["io"]     -- MMIO ($ff00)
emu.memory["hram"]   -- HRAM ($ff80)
```

See `references/classes-registers.md` for MemoryDomain class methods and ROM analysis examples.

## Callbacks

### Adding Callbacks

Do register frame callbacks before emulation starts because late registration misses the first vblank and desyncs frame counters. Do store callback IDs because you need them to remove callbacks later.

```lua
-- Add callback (returns callback ID)
id = callbacks.add("frame", function()
    -- Called every frame
end)

id = callbacks.add("start", function()
    -- Called when emulation starts
end)

id = callbacks.add("reset", function()
    -- Called when emulation resets
end)

id = callbacks.add("shutdown", function()
    -- Called when emulation stops
end)

-- Remove callback
callbacks.remove(id)
```

### Available Callbacks

```lua
-- alarm     - In-game alarm went off
-- crashed   - Emulation crashed
-- frame     - Frame finished
-- keysRead  - About to read key input
-- reset     - Emulation reset
-- savedataUpdated - Save data modified
-- sleep     - Entered low-power mode
-- shutdown  - Powered off
-- start     - Started
-- stop      - Voluntarily shut down
```

### Frame Callback Example

Do clear keys after adding because held keys persist across frames.

```lua
-- Auto-press A every 10 frames
local counter = 0
callbacks.add("frame", function()
    counter = counter + 1
    if counter >= 10 then
        emu.addKeys(C.GBA_KEY.A)
    else
        emu.clearKeys(C.GBA_KEY.A)
    end
end)
```

See `references/examples.md` for complete callback patterns (RAM watch, save state timer, speedrunner splits, TAS record/playback).

## Deep Dives

Detailed reference material is available in the `references/` directory. Load these on demand for specific topics:

- **Classes & Registers** — MemoryDomain class, TextBuffer class, GBA/GB register details
  - `references/classes-registers.md`
- **Networking** — Socket API details and constants
  - `references/networking.md`
- **Examples** — Complete working scripts (cheats, TAS tools, networked scripts)
  - `references/examples.md`

## Best Practices

### 1. Always Clear Keys

Do clear keys every frame because held keys accumulate and cause unintended input.

```lua
-- Bad: Keys stay pressed
callbacks.add("frame", function()
    emu.addKeys(C.GBA_KEY.A)
end)

-- Good: Clear after use
callbacks.add("frame", function()
    emu.addKeys(C.GBA_KEY.A)
    emu.clearKeys(C.GBA_KEY.A)
end)
```

### 2. Use Frame Callback for Input

Do handle input in frame callbacks because input timing must align with emulation cycle.

```lua
-- Input should be handled in frame callback
callbacks.add("frame", function()
    if emu.getKey(6) == 1 then  -- UP pressed
        -- Handle input
    end
end)
```

### 3. Watch for Crashes

Do register crash handler because unhandled crashes lose unsaved state.

```lua
callbacks.add("crashed", function()
    console.error("Emulation crashed!")
    -- Save state before exit
    emu.saveStateFile("crash.state")
end)
```

### 4. Reset State on Script Load

Do clear previous state when loading script because stale callbacks and keys persist.

```lua
-- Clear any previous state when loading
emu.clearKeys(0xFFFF)
callbacks.remove(cbid)  -- Remove old callbacks
```

### 5. Validate Memory Addresses

Do verify addresses before reading because wrong addresses return garbage data.

```lua
-- Check address is in valid range
local wram = emu.memory["wram"]
local base = wram:base()
local bound = wram:bound()

if addr >= base and addr < bound then
    value = emu.read16(addr)
else
    console.error("Invalid address!")
end
```

See `references/classes-registers.md` for MemoryDomain base/bound methods.

## Common Issues

### Address Not Found

Some games use different RAM locations because memory layout varies by title. Use mGBA's cheat search or memory viewer to find correct addresses.

### Keys Not Working

Some games poll keys differently because input handling varies. Try using addKeys instead of setKeys.

```lua
emu.addKeys(C.GBA_KEY.A)  -- OR with existing
```

### Socket Connection Timeout

Socket connect is blocking because it waits for server response. Use connect with timeout or run in separate thread. For async, use callbacks and poll().

See `references/networking.md` for socket patterns.

## References

- **Official Documentation**: https://mgba.io/docs/scripting.html
- **mGBA GitHub**: https://github.com/mgba-emu/mgba
- **Forums**: https://forums.mgba.io/
- **Discord**: https://discord.gg/em2M2sG
- **Scripting API Reference**: https://mgba.io/docs/scripting.html
