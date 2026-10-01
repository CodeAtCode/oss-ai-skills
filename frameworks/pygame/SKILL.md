---
name: pygame
description: Use when building 2D games in Python with pygame - game loop and delta time, sprites and groups, collision detection, drawing and surfaces, events and input, sound and fonts, camera, or performance optimization
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - game-development
    - 2d-games
    - pygame
    - graphics
    - game-engine
---

# Pygame

Python game development library.

## Quick Start

```bash
pip install pygame-ce  # Community Edition - actively maintained
```

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))
    # Draw game objects
    pygame.display.flip()
    
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
```

For full API reference, see https://www.pygame.org/docs/ref/

## Game Loop Architecture

### The Non-Negotiable Discipline

A game loop has three phases: **handle events** → **update simulation** → **render**. Never derive motion from raw frame counts—always use delta time (dt).

**Critical pattern:** `dt = clock.tick(FPS) / 1000` without clamping lets a stalled frame (e.g., system suspend, GC pause) teleport entities through walls. A 5-second stall at 60 FPS yields `dt = 5.0`, moving a 100 px/s entity 500 pixels in one update.

**Rule:** Always clamp `max_dt` to prevent tunneling.

### Fixed Timestep with Render Interpolation

The robust pattern: fixed physics steps, interpolated rendering for smoothness.

```python
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fixed timestep: physics always runs at 60 Hz
        self.fixed_dt = 1/60
        self.accumulator = 0.0
        self.max_dt = 1/10  # Clamp: ignore frames > 100ms (prevents tunneling)
    
    def run(self):
        while self.running:
            # Calculate delta time (seconds)
            dt = self.clock.tick(60) / 1000.0
            
            # Clamp to prevent spiral of death on stalled frames
            if dt > self.max_dt:
                dt = self.max_dt
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Fixed timestep update loop
            self.accumulator += dt
            while self.accumulator >= self.fixed_dt:
                self.update(self.fixed_dt)
                self.accumulator -= self.fixed_dt
            
            # Render with interpolation (smooths visual updates)
            interp = self.accumulator / self.fixed_dt
            self.render(interp)
        
        pygame.quit()
    
    def update(self, dt):
        """Physics and game logic at fixed 60 Hz"""
        # Movement: position += velocity * dt
        # Collision detection
        # AI decisions
        pass
    
    def render(self, interp):
        """Render with interpolation factor (0.0 to 1.0)"""
        self.screen.fill((0, 0, 0))
        
        # Interpolate positions for smooth rendering between physics steps
        for sprite in self.all_sprites:
            render_x = sprite.prev_x + (sprite.x - sprite.prev_x) * interp
            render_y = sprite.prev_y + (sprite.y - sprite.prev_y) * interp
            self.screen.blit(sprite.image, (render_x, render_y))
        
        pygame.display.flip()
```

**Why this matters:**
- Consistent physics regardless of framerate drops
- Deterministic simulation (network games, replays)
- No "spiral of death" when frame time exceeds update time
- Interpolation makes rendering smooth even when physics runs slower

**Variable delta alternative** (simpler, less precise):

```python
# Simpler: variable timestep (acceptable for non-critical physics)
dt = self.clock.tick(60) / 1000.0
if dt > 0.1:  # Clamp to 100ms max
    dt = 0.1
self.update(dt)
```

### Update/Draw/Collision Placement

```python
def update(self, dt):
    # 1. Handle input (keyboard/mouse state)
    # 2. Update positions: pos += vel * dt
    # 3. Update animations (frame += dt * fps)
    # 4. Collision detection (after positions change)
    # 5. Game logic (score, state transitions)

def render(self, interp):
    # 1. Clear screen (fill or restore background)
    # 2. Draw static background (once, cached)
    # 3. Draw sprites/groups (sorted by z-order if needed)
    # 4. Draw UI overlay (HUD, score, health)
    # 5. Flip display
```

## Sprite and Group Cost

### Why Groups Are the Bottleneck

`Group.update()` calls `.update()` on **every sprite** each frame. For 1000 sprites, that's 1000 function calls. The cost is not the group—it's the work each sprite does.

**Profile before optimizing:**

```python
import time

# Measure update cost
start = time.perf_counter()
all_sprites.update()
update_ms = (time.perf_counter() - start) * 1000

# Measure draw cost
start = time.perf_counter()
all_sprites.draw(screen)
draw_ms = (time.perf_counter() - start) * 1000

print(f"Update: {update_ms:.2f}ms, Draw: {draw_ms:.2f}ms")
# Budget: < 8ms update, < 8ms draw for 60 FPS headroom
```

### Group Types and Their Costs

| Group Type | Cost | Use When |
|------------|------|----------|
| `Group` | O(n) update, O(n) draw | Most cases, sprites with `.update()` |
| `GroupSingle` | O(1) access | Single entity (player, boss) |
| `LayeredUpdates` | O(n) + layer sorting | Z-order rendering, depth sorting |
| `Sprite` (manual) | O(1) | Single sprite, no group overhead |

```python
# GroupSingle: single entity, faster access
player = pygame.sprite.GroupSingle()
player.add(PlayerSprite())
player.update()  # Updates only the single sprite
player.draw(screen)

# LayeredUpdates: control draw order by layer
layers = pygame.sprite.LayeredUpdates()
layers.add(background, layers=[0])  # Draw first
layers.add(player, layers=[1])
layers.add(enemies, layers=[2])
layers.add(particles, layers=[3])  # Draw last (on top)
layers.change_layer(player, 5)  # Move player to top
```

### When to Draw Manually

Skip groups when:
- Sprites don't need `.update()` (static background tiles)
- You need custom draw order per frame
- You're using dirty rect optimization

```python
# Manual draw: skip group overhead for static tiles
for tile in background_tiles:
    screen.blit(tile.image, tile.rect)  # No update() call

# Custom z-order: sort before draw
sprites_to_draw = sorted(all_sprites, key=lambda s: s.z_index)
for sprite in sprites_to_draw:
    screen.blit(sprite.image, sprite.rect)
```

### GroupCollide vs Manual Collision

`GroupCollide` returns a dict keyed by sprite—expensive if you only need "did anything hit?"

```python
# Expensive: groupcollide builds full dict
hits = pygame.sprite.groupcollide(bullets, enemies, False, False)
# hits = {bullet1: [enemy1, enemy2], bullet2: [enemy3], ...}

# Cheaper: spritecollide, short-circuit on first hit
for bullet in bullets:
    if pygame.sprite.spritecollideany(bullet, enemies):
        bullet.kill()
        break  # Stop checking
```

## Collision Detection Decision Guide

### Collision Strategies by Cost

| Strategy | Cost | Use When |
|----------|------|----------|
| AABB (`rect.colliderect`) | O(1), fast | Most games, initial filter |
| `spritecollide` (rect) | O(n) per sprite | Small sprite counts (< 100) |
| `groupcollide` (dict) | O(n×m) | Need full collision map |
| Mask (`collide_mask`) | O(pixels) | Pixel-perfect needed |
| Circle (`collide_circle`) | O(1), approximate | Round sprites, medium precision |

### The Failure Modes

**Tunneling at high velocity:** A bullet moving 200 px/frame skips a 32-pixel enemy entirely.

**Fix:** Use continuous collision (swept AABB) or subdivide high-velocity updates.

```python
# Subdivide to prevent tunneling
def update_high_velocity(bullet, dt, subdivisions=4):
    sub_dt = dt / subdivisions
    for _ in range(subdivisions):
        bullet.x += bullet.vx * sub_dt
        bullet.y += bullet.vy * sub_dt
        if pygame.sprite.spritecollideany(bullet, enemies):
            return True  # Collision detected
    return False
```

**O(n²) broad-phase:** 500 bullets × 500 enemies = 250,000 checks per frame.

**Fix:** AABB pre-filter with spatial partitioning.

```python
# AABB pre-filter: reject distant sprites first
def collide_with_filter(bullet, enemies):
    # Fast bounding box check
    for enemy in enemies:
        if not bullet.rect.colliderect(enemy.rect):
            continue  # Skip expensive mask check
        
        # Only now do the expensive check
        if bullet.mask and enemy.mask:
            offset = (enemy.rect.x - bullet.rect.x, 
                     enemy.rect.y - bullet.rect.y)
            if bullet.mask.overlap(enemy.mask, offset):
                return True
    return False

# For large counts: use a quadtree or grid
# (See references/performance.md for spatial partitioning)
```

### Mask vs Colorkey vs Rect

```python
# Rect collision (fastest, least precise)
if player.rect.colliderect(enemy.rect):
    handle_collision()

# Colorkey: simple transparency, no pixel-perfect
image = pygame.image.load("sprite.png").convert()
image.set_colorkey((0, 0, 0))  # Black is transparent

# Mask: pixel-perfect (slow, use as second filter)
mask = pygame.mask.from_surface(image)  # Expensive, do once at load
# Store mask on sprite
sprite.mask = mask

# Collision: rect first (AABB), then mask
if sprite1.rect.colliderect(sprite2.rect):
    offset = (sprite2.rect.x - sprite1.rect.x, 
              sprite2.rect.y - sprite1.rect.y)
    if sprite1.mask.overlap(sprite2.mask, offset):
        handle_pixel_perfect_collision()
```

**Rule:** Always use AABB as first filter. Mask collision is 10-100× slower than rect.

## Surface and Blit Pitfalls

### Per-Frame Allocation

**Never** allocate Surfaces inside the game loop.

```python
# Bad: Allocates new surface every frame (triggers GC, causes stutter)
while running:
    text = font.render(score_text, True, WHITE)
    screen.blit(text, (10, 10))

# Good: Cache the surface, update only when score changes
class HUD:
    def __init__(self):
        self.score_font = pygame.font.Font(None, 36)
        self.score_surface = None
        self.score = 0
    
    def set_score(self, value):
        if value != self.score:
            self.score = value
            self.score_surface = self.score_font.render(
                str(value), True, WHITE
            )
    
    def draw(self, screen):
        if self.score_surface:
            screen.blit(self.score_surface, (10, 10))
```

### convert() and convert_alpha() at Load Time

```python
# Bad: Converts on every load (or worse, every frame)
image = pygame.image.load("sprite.png").convert()

# Good: Load once at startup, convert immediately
class AssetManager:
    def __init__(self):
        self.player = pygame.image.load("player.png").convert_alpha()
        self.tile = pygame.image.load("tile.png").convert()
        # Opaque → convert(), transparent → convert_alpha()
```

**Rule of thumb:**
- `convert()`: Opaque images, no transparency (20-30% faster blit)
- `convert_alpha()`: Images with alpha channels or colorkeys
- Never call `convert()` inside the game loop

### set_alpha vs Alpha Channel

```python
# Bad: set_alpha on many sprites (slow, recomputes every blit)
for sprite in hundreds_of_sprites:
    sprite.image.set_alpha(128)

# Good: Use alpha channel in the image itself (precomputed)
# Load with transparency already baked in
sprite = pygame.image.load("fading.png").convert_alpha()
```

**Rule:** `set_alpha()` on a Surface is slower than having the alpha channel in the image data. Pre-render semi-transparent surfaces once.

### blit vs blits Batching

```python
# Bad: Multiple individual blit calls
for sprite in sprites:
    screen.blit(sprite.image, sprite.rect)

# Good: Batched blits (single call, faster)
screen.blits([(s.image, s.rect) for s in sprites])

# Even better: pre-compute the list
blit_list = [(s.image, s.rect) for s in sprites]
screen.blits(blit_list)
```

**Rule:** `blits()` is 10-30% faster than individual `blit()` calls for large sprite counts.

## When Not to Use Pygame

### Browser-Targeted Games

**Problem:** Pygbag (pygame-to-WebAssembly) has limitations:
- Large binary size (~10MB+ initial load)
- Input latency in browser
- No access to native APIs (file system, notifications)
- Mobile browser performance issues

**Alternative:** Native JS/TypeScript game engines (Phaser, Babylon.js) or Unity/Godot export to WebGL.

### Hardware-Accelerated 3D or Heavy 2D Sprite Counts

**Problem:** Pygame uses software rendering (SDL2 software renderer by default). Even with `HWSURFACE`, it's not a full 3D pipeline.

**Symptoms:**
- > 1000 moving sprites at 60 FPS
- Need for 3D transformations (rotation in 3D space, perspective)
- Shader effects (bloom, depth of field)

**Alternative:**
- 2D: Godot (GDScript, built-in sprite batching)
- 3D: Panda3D, Ursina, or OpenGL/DirectX directly
- High-performance 2D: Pyglet (OpenGL-backed)

### Projects Needing a Retained-Mode Scene Graph

**Problem:** Pygame is immediate-mode. You redraw everything every frame. No scene graph, no object retention.

**Symptoms:**
- Complex UI with nested widgets
- Need for editor-time scene composition
- Undo/redo history of scene changes

**Alternative:** Godot (built-in scene system), Unity, or a retained-mode UI library (Dear PyGui for tools).

### Games That Must Ship on Mobile

**Problem:** Pygame has no official mobile support. Pygbag targets web, not native mobile.

**Symptoms:**
- Need iOS/Android app store distribution
- Need native mobile features (push notifications, in-app purchases)
- Need touch-optimized input handling

**Alternative:** Godot, Unity, or Flutter with game plugins.

## Deep Dives

Load these reference files on demand for detailed implementations:

- **Drawing & Surfaces**: `references/drawing-surfaces.md` — Colors, shapes, surface operations, transforms
- **Performance Optimization**: `references/performance.md` — Image conversion, RLEACCEL, batched blits, dirty rects, pre-rendered surfaces
- **Sprites, Camera & UI**: `references/sprites-camera-ui.md` — Sprite classes, groups, camera implementation, button UI elements

## References

- **Official Documentation**: https://www.pygame.org/docs/
- **Pygame Wiki**: https://www.pygame.org/wiki/
- **KidsCanCode Pygame Tutorials**: https://kidscancode.org/pygame_tutorials/
