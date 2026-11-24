---
name: mgba
description: Use when scripting mGBA emulator automation in Lua - console API, ROM and save state operations, frame callbacks, input handling, memory reading for cheats and RAM watches, sockets, TAS and speedrunner tooling, headless parity testing against a reference emulator
metadata:
  author: mte90
  version: 2.1.0
  tags:
    - lua
    - emulator
    - gba
    - gameboy-advance
    - scripting
    - memory-hacking
---

# mGBA Scripting

Lua scripting for mGBA emulator (built-in since 0.10).

**GUI:** Tools → Scripting… opens the console where scripts load and run.
**Headless/CI:** scripting-related CLI flags vary by mGBA version — run `mgba --help` (or your frontend binary) on the target machine and verify the flags exist before relying on them; do not assume.

## Top-Level Objects

```lua
-- emu: CoreAdapter instance (available when game loaded)
-- C: Exported constants
-- callbacks: CallbackManager instance
-- console: Console instance
-- util: Basic utility library
-- socket: TCP socket library
```

```lua
console.log("Info"); console.warn("Warning"); console.error("Error")
buffer = console.createBuffer("My Buffer")
buffer:print("Text in buffer"); buffer:clear()

bits = util.expandBitmask(0xFF)      -- {0,1,2,3,4,5,6,7}
mask = util.makeBitmask({0, 3, 5})   -- 0x29
```

## Core API

### ROM Operations

```lua
success = emu.loadFile("path/to/rom.gba")
title  = emu.getGameTitle()  -- "POKEMON FIRE"
code   = emu.getGameCode()   -- "AGB-P-FE"
size   = emu.romSize()
platform = emu.platform()    -- 0=GBA, 1=GB
checksum = emu.checksum()    -- CRC32
emu.reset()
```

### Save States

```lua
emu.saveStateFile("path/to/state.state")   emu.loadStateFile("path/to/state.state")
emu.saveStateSlot(0)                       emu.loadStateSlot(0)
buffer = emu.saveStateBuffer()             emu.loadStateBuffer(buffer)
emu.autoloadSave()

-- Flags: SCREENSHOT=1, SAVEDATA=2, CHEATS=4, RTC=8, METADATA=16, ALL=31
emu.saveStateSlot(0, 31)
```

### Frame Control

```lua
emu.runFrame()      -- one frame
emu.step()          -- one instruction
emu.currentFrame()
emu.frameCycles()   -- cycles per frame
emu.frequency()      -- cycles per second
emu.screenshot("frame.png")
```

### Input

```lua
emu.setKeys(0x0000)                      -- all keys at once
emu.addKeys(C.GBA_KEY.A + C.GBA_KEY.R)    -- OR into current
emu.clearKeys(C.GBA_KEY.B)
emu.addKey(k); emu.clearKey(k)
if emu.getKey(C.GBA_KEY.UP) == 1 then end
keys = emu.getKeys()
```

```lua
-- GBA: A=0 B=1 SELECT=2 START=3 RIGHT=4 LEFT=5 UP=6 DOWN=7 R=8 L=9
-- GB:  same minus R/L (C.GB_KEY.*)
```

## Memory Access

```lua
v8  = emu.read8(addr); v16 = emu.read16(addr); v32 = emu.read32(addr)
emu.write8(addr, v);  emu.write16(addr, v);  emu.write32(addr, v)
data = emu.readRange(address, length)
rom = emu.memory["cart0"]; value = rom:read8(offset)   -- :read8/:read16/:read32/:readRange
emu.readRegister(name); emu.writeRegister(name, val)
```

### Memory Domains (GBA)

```lua
emu.memory["bios"]     -- 0x00000000   emu.memory["io"]       -- 0x04000000
emu.memory["wram"]     -- 0x02000000   emu.memory["palette"]  -- 0x05000000
emu.memory["iwram"]    -- 0x03000000   emu.memory["vram"]     -- 0x06000000
emu.memory["oam"]      -- 0x07000000   emu.memory["cart0"]    -- 0x08000000
```

GB: `cart0` (ROM), `vram` ($8000), `sram` ($a000), `wram` ($c000), `oam` ($fe00), `io` ($ff00), `hram` ($ff80).

## Callbacks

```lua
id = callbacks.add("frame", function() ... end)   callbacks.remove(id)
-- alarm · crashed · frame · keysRead · reset · savedataUpdated · sleep · shutdown · start · stop
```

## Agent Workflow — headless parity testing (the pattern that saves whole lanes)

Deterministic comparison against a reference run, **without ever dumping memory into context**:

1. **Anchor:** load ROM, reset to a fixed point, `emu.saveStateBuffer()` once — reuse it for every comparison (never re-run the intro to "get to" the same frame; that is not deterministic).
2. **Probe:** at frames of interest, read the regions that define behavior (`iwram` structs, `vram`, `oam`) — through `readRange`, but hash them in Lua, do not print them:

```lua
local function fnv1a(data)          -- 32-bit FNV-1a, pure Lua
  local h = 0x811c9dc5
  for i = 1, #data do
    h = (h ~ data:byte(i)) & 0xffffffff
    h = (h * 0x01000193) & 0xffffffff
  end
  return string.format("%08x", h)
end
local h = fnv1a(emu.memory["vram"]:readRange(0, 0x18000))  -- VRAM, hashed
console.log(string.format("frame=%d vram=%s oam=%s", emu.currentFrame(),
  h, fnv1a(emu.memory["oam"]:readRange(0, 0x400))))
```

3. **Compare:** emit "frame | region | hash" rows; a parity failure is a divergent hash, resolved by binary-searching the first frame where the hashes split — not by eyeballing buffers.
4. **Token economy:** VRAM alone is 96 KB — printing ranges is a context bomb. Hash always; dump a raw range only for the single first-divergence region, bounded (≤256 bytes).

Related skills: memory-forensics (savestate/RAM capture analysis), bpcore-engine (the on-device Lua engine), binary-analysis-patterns + ghidra (static side of the same question).

## Best Practices

1. **Always clear keys** after use in a frame callback — stale presses are the #1 input bug.
2. Input belongs in the `frame` callback.
3. Save state on `crashed` before doing anything else.
4. On script load: clear keys and remove old callbacks.

## Common Issues

- **Address not found:** games relocate RAM — find addresses with mGBA's cheat search or memory viewer, not by guessing.
- **Keys ignored:** some games poll oddly — prefer `addKeys` over `setKeys`.
- **Blocking sockets:** socket connect blocks the emulation thread — poll from callbacks.

## Deep Dives (references/ directory, load on demand)

- `references/classes-registers.md` — MemoryDomain, TextBuffer, GBA/GB registers
- `references/networking.md` — socket API and constants
- `references/examples.md` — complete scripts (cheats, TAS, networked)

## References

- https://mgba.io/docs/scripting.html
- https://github.com/mgba-emu/mgba
