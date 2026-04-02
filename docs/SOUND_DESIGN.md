# 🎵 Sound Design Documentation

Technical documentation for the **8-bit Sound Engine** used in Stickman Runner.

---

## Overview

All sounds in Stickman Runner are **synthesized at runtime** — no audio files are loaded from disk. The engine generates waveforms as raw PCM byte buffers and wraps them in `pygame.mixer.Sound` objects.

This approach means:
- **Zero external audio dependencies**
- **Instant loading** (no file I/O)
- **Consistent behavior** across platforms
- **Tiny footprint** (no audio files in the repo)

---

## Synthesizer: `_syn()`

### Function Signature

```python
def _syn(notes, sr=44100, vol=0.14, wave="square"):
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `notes` | `list[tuple]` | — | List of `(frequency_hz, duration_ms)` pairs |
| `sr` | `int` | `44100` | Sample rate in Hz |
| `vol` | `float` | `0.14` | Volume multiplier (0.0 → 1.0) |
| `wave` | `str` | `"square"` | Waveform type |

### Waveform Types

| Type | Formula | Character | Best For |
|---|---|---|---|
| `square` | `1.0 if phase < 0.5 else -1.0` | Sharp, classic 8-bit | Melodic tones, jingles |
| `saw` | `2.0 * phase - 1.0` | Buzzy, harmonic-rich | Mechanical sounds, alarms |
| `noise` | `random(-1, 1)` | Static, unpitched | Impacts, wind, explosions |
| `sine` | `sin(2π * freq * t)` | Pure, smooth | Subtle tones (fallback) |

### Envelope

Each note uses a **linear decay envelope**:
```
envelope = max(0.0, 1.0 - (sample_index / total_samples) * 0.4)
```
This creates a natural fade from full volume to 60% over each note's duration.

---

## Sound Effect Catalog

### Player Sounds

| Sound | Notes | Wave | Vol | Description |
|---|---|---|---|---|
| `SND_JUMP` | 10 ascending tones (350–1025 Hz) | square | 0.12 | Rising chirp on jump |
| `SND_LAND` | 90 Hz → 55 Hz | noise | 0.09 | Thud on ground contact |
| `SND_DUCK` | 280 → 220 → 160 Hz | noise | 0.08 | Whoosh on ducking |

### Scoring Sounds

| Sound | Notes | Wave | Vol | Description |
|---|---|---|---|---|
| `SND_COIN` | B5 → E6 | square | 0.10 | Every 50 points (not at 100s) |
| `SND_MILESTONE` | E5→G5→C6→G5→C6→E6 | square | 0.09 | Every 100 points — fanfare |

### Enemy Sounds

| Sound | Notes | Wave | Vol | Description |
|---|---|---|---|---|
| `SND_JET` | 14 ascending + 10 descending | noise | 0.10 | Jet flyby on spawn |
| `SND_MISSILE` | 6 rising tones (120→1300) | saw | 0.11 | Missile launch |
| `SND_NEARMISS` | 8 descending (1000→200) | noise | 0.08 | Close call warning |
| `SND_SIREN` | 600↔800 Hz alternating ×2 | square | 0.06 | Formation attack warning |

### Impact Sounds

| Sound | Notes | Wave | Vol | Description |
|---|---|---|---|---|
| `SND_DEATH` | B4→A#4→A4→(rest)→F4→E4→D4→C4 | square | 0.14 | Descending death melody |
| `SND_EXPLODE` | 200→150→100→60→30 Hz | noise | 0.13 | Explosion rumble |

### Feedback Sounds

| Sound | Notes | Wave | Vol | Description |
|---|---|---|---|---|
| `SND_SPEEDUP` | A5 → C#6 | saw | 0.07 | Speed milestone |
| `SND_DODGE` | C6 → G6 | square | 0.06 | Successful dodge confirmation |

---

## Audio Configuration

```python
pygame.mixer.init(
    frequency=44100,  # CD-quality sample rate
    size=-16,         # 16-bit signed samples
    channels=2,       # Stereo (though sounds are mono)
    buffer=512        # Low latency buffer
)
```

### Buffer Size

The `512` sample buffer provides ~11.6ms latency at 44.1kHz, ensuring responsive sound playback that feels synchronized with gameplay actions.

---

## Design Philosophy

The sound design follows **Mario-era 8-bit conventions**:

1. **Ascending tones** = positive actions (jump, coin, milestone)
2. **Descending tones** = negative events (death, near-miss)
3. **Noise waves** = physical impacts (landing, explosions, jets)
4. **Saw waves** = mechanical/technological sounds (missiles, speed-up)
5. **Square waves** = melodic/musical elements (jingles, sirens)

Each sound's volume is carefully balanced relative to others, with gameplay-critical sounds (death, missiles) louder than ambient feedback (dodge, speed-up).
