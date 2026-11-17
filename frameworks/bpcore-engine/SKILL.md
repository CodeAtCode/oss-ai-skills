---
name: bpcore-engine
description: Use when building GBA games with the BPCore Lua engine - entity, sprite and tilemap functions, SRAM save and load, link cable multiplayer protocol, camera and scrolling, or optimization patterns
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - lua
    - gba
    - game-engine
    - gameboy-advance
---

> **Objective:** Use this skill to reduce SRAM-corruption incidents, sprite-flicker bugs, link-cable desync, and tilemap-tearing crashes by enforcing save-format discipline, VRAM-budget rules, and sync-protocol patterns below.

# BPCore Engine Skill

Comprehensive guide for building Gameboy Advance games using the BPCore Engine Lua framework.

## Overview

BPCore Engine (Blind jumP Core Engine) is a Lua game framework for GBA that combines C++ with embedded Lua, letting developers create games without C++ or compilers. Inspired by Pico-8 and Tic80, it's suited for small minigames given the GBA's limited resources: 240x160 screen, 16.78 MHz ARM7TDMI, and 256KB RAM for Lua/data.

The engine provides sprite rendering, tile-based graphics, entity management with collision, button input, UTF-8 text, audio, save/load via SRAM, and multiplayer through the link cable. The build system uses Lua to package resources into ROM.

## Deep Dives

Complex topics are split into reference files loaded on demand from `SKILL.md`:

- **API Reference** — All 60+ engine functions with signatures → [`references/api-reference.md`](references/api-reference.md)
- **Save/Load to SRAM** — Persistent storage patterns, checksums, marker bytes → [`references/save-load.md`](references/save-load.md)
- **Multiplayer Link Cable Protocol** — Packet formats, binary I/O, client-server sync → [`references/multiplayer.md`](references/multiplayer.md)
- **Optimization & Camera** — Sprite batching, entity pools, parallax scrolling → [`references/optimization.md`](references/optimization.md)
- **Error Handling** — Bounds checking, validation patterns → [`references/error-handling.md`](references/error-handling.md)

## Critical Rules (do X because Y)

### Memory & VRAM Discipline

- **Pre-allocate entity pools before runtime because** runtime allocation during gameplay causes frame stalls and can exhaust the 128-entity limit mid-level.
- **Batch stationary sprites into a single draw loop because** scattered spr() calls across update logic increase CPU overhead and risk missing vblank deadlines.
- **Keep tile updates under 10 per frame because** each tile() call writes to VRAM during active display, causing visible tearing if it hits vblank.
- **Distribute sprites vertically across scanlines because** GBA can only render ~10 sprites per scanline; exceeding this causes flickering on crowded rows.

### SRAM Save/Load Discipline

- **Validate save data size before SRAM write because** oversized data corrupts adjacent save slots and can overwrite the marker byte.
- **Write checksums after every save because** SRAM bit-flips during power loss leave corrupted data that loads silently without validation.
- **Verify marker byte (0x42) before loading because** loading uninitialized SRAM returns garbage that crashes game logic expecting valid state.
- **Use atomic writes (temp buffer then commit) because** power loss mid-write leaves partial data that passes checksum but contains torn state.

### Link Cable Multiplayer Discipline

- **Keep packets under 11 bytes because** the hardware queue rejects longer messages, causing silent send failures and desync.
- **Drain recv() in a loop each frame because** unprocessed packets overflow the 64-packet receive queue, losing critical state updates.
- **Handle disconnects by resetting game state because** stale connections send garbage after cable removal, corrupting opponent position tracking.
- **Use client-server authority model because** dual-authority games desync when both players predict differently; one peer validates all inputs.

### Camera & Scrolling Discipline

- **Clamp camera coordinates to world bounds because** unbounded camera(x, y) exposes blank VRAM edges when player reaches level limits.
- **Update scroll() after camera() because** scroll offsets are relative to camera position; reversing the order causes parallax misalignment.
- **Use fixed-point math for scroll interpolation because** GBA lacks FPU; floating-point emulation is slow and causes jittery camera movement.

## Installation & Project Structure

### Getting BPCoreEngine.gba

**Important**: BPCore Engine requires `BPCoreEngine.gba` base ROM with compiled C++ code and Lua interpreter. This is **not** a custom ROM you create.

#### Where to Obtain

1. **Official Repository**: Clone from [GitHub](https://github.com/evanbowman/BPCore-Engine)
   ```bash
   git clone https://github.com/evanbowman/BPCore-Engine.git
   cd BPCore-Engine
   ```

2. **Required Files**: Repository contains:
   - `BPCoreEngine.gba` - Engine base ROM (~3.5 MB)
   - `build.lua` - Build script (Lua 5.3)
   - `test/` - Example projects

3. **Alternatives**:
   - GitHub Releases may have pre-built GBA files
   - mGBA emulator includes BPCore version in some distributions

#### File Placement

```
your-project/
├── BPCoreEngine.gba          # Base ROM (required)
├── build.lua                  # Build script
├── manifest.lua               # Your manifest
├── overlay.bmp                # Text/UI tiles
├── tile0.bmp                  # Main background (64x64 tiles)
├── tile1.bmp                  # Foreground (64x64 tiles)
├── spritesheet.bmp           # Sprites (16x16)
├── music.raw                  # Music (mono 16kHz PCM)
├── sfx.wav                    # Sound effects
├── main.lua                   # Entry point
└── data.txt                   # Resources
```

### Building Your ROM

**Step 1**: Create `manifest.lua`
### Building Your ROM

**Step 1**: Create `manifest.lua`

```lua
local app = {
    name = "My Adventure",
    gamecode = "ABCD",
    makercode = "BC",
    tilesets = { "overlay.bmp", "tile0.bmp", "tile1.bmp" },
    spritesheets = { "spritesheet.bmp" },
    audio = { "music.raw", "jump.wav", "coin.wav" },
    scripts = { "main.lua", "game.lua", "menu.lua" },
    misc = { "level1.csv" }
}

return app
```

**Step 2**: Run build script

```bash
lua build.lua manifest.lua BPCoreEngine.gba output.gba
```

**Step 3**: Verify

Build checks manifest files exist, formats are valid, scripts readable, output ROM created (~3.5-4 MB).

**Step 4**: Test with mGBA

```bash
mGBA output.gba --log --memview
```

`--log` shows engine log() output, `--memview` opens memory viewer for debugging.

### File Formats

**BMP Tilesets**: Indexed color (256 colors), tiles are 8x8 pixels. Overlay: 16x16 tiles, Tile_0/1: 32x32 tiles, Sprites: 8x8 sprites.

**Audio**: Mono 16kHz signed 8-bit PCM. Convert with FFmpeg:
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 -f s8 output.raw
```

**Tilemap CSV**: Comma-separated tile indices, each row is one tile row. Tile indices start at 1 (0 = empty).

## Troubleshooting

- **Emulator vs hardware differences**: Test on real hardware because mGBA timing differs from actual GBA clock rates, causing race conditions in fast games.
- **Sprite flickering (too many sprites per scanline)**: Redistribute sprites vertically because GBA hardware limits ~10 sprites per scanline; excess sprites blink on/off.
- **Audio channel conflicts**: Prioritize player-hurt sounds at priority 95+ because only 3 SFX channels exist; lower-priority sounds drop silently.
- **Save data corruption**: Write to temp offset then commit because power loss mid-write leaves partial data; atomic writes prevent torn state.
- **Link cable desync**: Implement sequence numbers in packets because recv() queue reordering causes state rollback when packets arrive out of order.

## References

- [BPCore Engine GitHub Repository](https://github.com/evanbowman/BPCore-Engine)
- [GBA Hardware Specifications](https://problemkaputt.de/gbatek.htm)
- [Tonc GBA Tutorial](https://www.coranac.com/tonc/text/)
- [GBA Programming Wiki](https://gbadev.net/)
- [mGBA Emulator](https://mgba.io/)

