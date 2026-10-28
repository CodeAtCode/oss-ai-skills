> Loaded on demand from SKILL.md when the agent needs the complete BPCore Lua API function list.

# BPCore API Reference

Complete function catalog for the BPCore Engine Lua framework.

## Entity Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `ent()` | `ent()` | Create entity, returns handle |
| `entpos(e, x, y)` | `entpos(e, x, y)` | Set position, returns self |
| `entz(e, z)` | `entz(e, z)` | Set Z-order (0-255), returns self |
| `entspr(e, sprite, xflip, yflip)` | `entspr(e, sprite, xflip, yflip)` | Set sprite and flips, returns self |
| `entspd(e, x, y)` | `entspd(e, x, y)` | Set movement speed, returns self |
| `entslot(e, slot, value)` | `entslot(e, slot, value)` | Store in slot, returns self |
| `entslots(e, count)` | `entslots(e, count)` | Allocate slots, returns self |
| `entanim(e, start, len, rate)` | `entanim(e, start, len, rate)` | Set animation |
| `entag(e, tag)` | `entag(e, tag)` | Set collision tag, returns self |
| `enthb(e, ox, oy, w, h)` | `enthb(e, ox, oy, w, h)` | Set hitbox, returns self |
| `del(e, auto?)` | `del(e, [auto])` | Delete entity |
| `ents()` | `ents()` | Get all entities table |

## Sprite & Tile Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `txtr(layer_id, filename)` | `txtr(layer_id, filename)` | Load texture from file |
| `txtr(layer_id, ptr, len)` | `txtr(layer_id, ptr, len)` | Load from pointer/length |
| `file(filename)` | `file(filename)` | Get file pointer/length |
| `spr(sprite_id, x, y)` | `spr(sprite_id, x, y)` | Draw sprite |
| `spr(sprite_id, x, y, xflip, yflip)` | `spr(sprite_id, x, y, xflip, yflip)` | Draw with flips |
| `tile(layer_id, x, y, num?)` | `tile(layer_id, x, y, [num])` | Draw/read tile |
| `tilemap(f, layer, w, h, dx, dy, sx, sy)` | `tilemap(f, layer, w, h, dx, dy, sx, sy)` | Load CSV tilemap |
| `clear()` | `clear()` | Clear sprites, VSync |
| `display()` | `display()` | Send sprites to display |
| `fade(amount, color?, tl?, bg?)` | `fade(amount, [color], [tl], [bg])` | Fade layers |

## Camera & Scroll

| Function | Signature | Description |
|----------|-----------|-------------|
| `camera(x, y)` | `camera(x, y)` | Set camera center |
| `scroll(layer, x, y)` | `scroll(layer, x, y)` | Set layer scroll |
| `priority(s, bg, t0, t1)` | `priority(s, bg, t0, t1)` | Set render priority |

## Collision

| Function | Signature | Description |
|----------|-----------|-------------|
| `ecolle(e1, e2)` | `ecolle(e1, e2)` | Check collision (bool) |
| `ecoll(e, tag)` | `ecoll(e, tag)` | Find tag matches (array) |
| `enthb(e)` | `enthb(e)` | Get hitbox (getter) |

## Input

| Function | Signature | Description |
|----------|-----------|-------------|
| `btn(num)` | `btn(num)` | Button held? (bool) |
| `btnp(num)` | `btnp(num)` | Button pressed? (bool) |
| `btnnp(num)` | `btnnp(num)` | Button released? (bool) |

## Graphics

| Function | Signature | Description |
|----------|-----------|-------------|
| `print(text, x, y, fg?, bg?)` | `print(text, x, y, [fg], [bg])` | Print to overlay |

## Audio

| Function | Signature | Description |
|----------|-----------|-------------|
| `music(f, offset?)` | `music(f, [offset])` | Play background music |
| `sound(f, priority)` | `sound(f, priority)` | Play sound effect |

## Memory

| Function | Signature | Description |
|----------|-----------|-------------|
| `poke(addr, value)` | `poke(addr, value)` | Write byte |
| `poke4(addr, value)` | `poke4(addr, value)` | Write 32-bit word |
| `peek(addr)` | `peek(addr)` | Read byte |
| `peek4(addr)` | `peek4(addr)` | Read 32-bit word |
| `memput(addr, data)` | `memput(addr, data)` | Write to memory |
| `memget(addr, len?)` | `memget(addr, [len])` | Read from memory |

## System

| Function | Signature | Description |
|----------|-----------|-------------|
| `delta()` | `delta()` | Microseconds since last call |
| `sleep(frames)` | `sleep(frames)` | Sleep N frames |
| `startup_time()` | `startup_time()` | Get boot time |
| `fdog()` | `fdog()` | Feed watchdog timer |
| `log(msg)` | `log(msg)` | Debug log |
| `rline()` | `rline()` | Get raster line |
| `flimit(fps)` | `flimit(fps)` | Set frame rate limit |
| `next_script(filename)` | `next_script(filename)` | Switch Lua script |

## Multiplayer

| Function | Signature | Description |
|----------|-----------|-------------|
| `connect(timeout)` | `connect(timeout)` | Connect (blocking) |
| `disconnect()` | `disconnect()` | Disconnect |
| `send(data)` | `send(data)` | Send message (max 11 bytes) |
| `recv()` | `recv()` | Receive message |
| `send_iram(ptr)` | `send_iram(ptr)` | Send from IRAM |
| `recv_iram(ptr)` | `recv_iram(ptr)` | Receive to IRAM |

## Layer IDs

| ID | Layer | Size | Description |
|----|-------|------|-------------|
| 0 | Overlay | 32x32 tiles | Front, persistent |
| 1 | Tile Layer 1 | 64x64 tiles | Behind sprites, in front of tile_0 |
| 2 | Tile Layer 0 | 64x64 tiles | Main background |
| 3 | Background | 32x32 tiles | Back layer |
| 4 | Sprites | Dynamic | On-top sprites |
