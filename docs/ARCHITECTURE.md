# 🏗️ Architecture Overview

Technical documentation for the **Stickman Runner** game engine.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        MAIN LOOP                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Input    │→ │  Update  │→ │ Collision│→ │  Render  │    │
│  │  Handler  │  │  Phase   │  │ Detection│  │  Phase   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────┴────┐   ┌─────┴─────┐  ┌────┴────┐  ┌─────┴─────┐
    │Keyboard │   │  Player   │  │  AABB   │  │  Sky      │
    │ Events  │   │  Cacti    │  │  Rect   │  │  Ground   │
    │         │   │  Jets     │  │  Tests  │  │  Entities │
    │         │   │  Missiles │  │         │  │  Particles│
    │         │   │  Particles│  │         │  │  HUD      │
    └─────────┘   └───────────┘  └─────────┘  └───────────┘
```

---

## Core Systems

### 1. Game Loop (`main()`)

- Runs at **60 FPS** via `pygame.time.Clock`
- Standard game loop: **Input → Update → Render**
- Two nested loops:
  - Outer loop: Game session (reset on restart)
  - Inner loop: Frame-by-frame gameplay

### 2. Entity System

| Class | Role | Properties |
|---|---|---|
| `Player` | Stickman character | Position, velocity, state (run/jump/duck/dead), animation frame |
| `Cactus` | Ground obstacle | Position, variant (4 types), hitbox |
| `Jet` | Flying enemy | Position, speed, flight pattern, missile cooldown |
| `Missile` | Projectile | Position, velocity, trail particles, near-miss tracking |
| `CloudObj` | Decorative cloud | Position, parallax speed |
| `StarObj` | Night sky star | Position, twinkle timer |
| `Ground` | Scrolling ground | Segment array with procedural regeneration |
| `Particle` | Visual effect | Position, velocity, lifetime, color, size |

### 3. Physics

- **Gravity:** `0.75 px/frame²`
- **Jump velocity:** `-14.0 px/frame`
- **Speed range:** `6.5` → `18.0` (increments by `0.003/frame`)
- **Ground plane:** `Y = 310`
- **Collision:** Axis-Aligned Bounding Box (AABB) with inset margins

### 4. Rendering Pipeline

1. **Sky gradient** — Cached 1px-wide strip, scaled to screen width
2. **Ground fill** — Solid rect below ground line
3. **Background** — Stars, moon (night only), clouds
4. **Entities** — Ground segments, cacti, jets, missiles, player
5. **Particles** — Alpha-blended circles with lifetime decay
6. **Screen shake** — Offset applied to the entire frame surface
7. **HUD** — Score, speed, danger level, warnings (drawn without shake)
8. **Game over overlay** — Semi-transparent black overlay with UI

### 5. Sound Engine (`_syn()`)

Synthesizes waveforms in real-time:

| Wave Type | Description | Used For |
|---|---|---|
| `square` | Classic 8-bit tone | Jump, coin, milestone, siren |
| `saw` | Buzzy, harmonic-rich | Missile launch, speed-up |
| `noise` | White noise | Landing, ducking, jet flyby, near-miss |
| `sine` | Pure tone | Fallback wave type |

**Envelope:** Linear decay (`1.0 → 0.6` over note duration).

### 6. Difficulty Scaling

```
danger_level = score / 150

Jet spawn threshold:  max(60, 250 - danger_level * 8) frames
Jet spawn chance:     min(0.15, 0.02 + danger_level * 0.005)
Formation attacks:    Enabled when danger_level > 8
Cactus gap:           max(30, 65 - speed * 2) frames
```

---

## Performance Optimizations

- **Sky gradient caching** — Pre-computed 1px strips instead of per-frame gradients
- **Particle `__slots__`** — Reduced memory footprint for particle objects
- **Conditional rendering** — Stars/moon only drawn when `night_alpha > 50`
- **Efficient collision** — AABB checks with inset rects (fewer false positives)
- **Frame surface** — Single off-screen surface for shake offset, blitted once

---

## State Machine

```
┌────────────┐    SPACE/UP    ┌────────────┐
│   TITLE    │ ──────────── → │  GAMEPLAY  │
│   SCREEN   │                │            │
└────────────┘                └─────┬──────┘
      ↑                             │
      │         Collision           ▼
      │                       ┌────────────┐
      │    ENTER/SPACE        │  GAME OVER │
      └────────────────────── │            │
                              └────────────┘
                                    │
                               C    ▼
                              ┌────────────┐
                              │  CREDITS   │
                              │  SCREEN    │
                              └────────────┘
```
