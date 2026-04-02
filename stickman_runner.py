"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     ★  STICKMAN  RUNNER  ★                                   ║
║                                                                              ║
║   Author  : Utkarsh Mani Tripathi                                            ║
║   LinkedIn: https://www.linkedin.com/in/utkarsh-mani-tripathi/               ║
║                                                                              ║
║   Controls:                                                                  ║
║     SPACE / UP   — Jump                                                      ║
║     DOWN         — Duck / Slide                                              ║
║     ENTER/SPACE  — Restart after Game Over                                   ║
║     C            — Credits                                                   ║
║     ESC          — Quit                                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import pygame
import random
import sys
import math

# ─── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

SCREEN_W = 1000
SCREEN_H = 440
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("★ Stickman Runner — by Utkarsh Mani Tripathi ★")
clock = pygame.time.Clock()
FPS = 60

# ─── Palette ───────────────────────────────────────────────────────────────────
WHITE        = (255, 255, 255)
BLACK        = (0, 0, 0)
DARK_GRAY    = (50, 50, 55)
LIGHT_GRAY   = (155, 155, 160)
MID_GRAY     = (120, 120, 125)

# Sky
SKY_TOP_DAY  = (100, 180, 255)
SKY_BOT_DAY  = (200, 230, 255)
SKY_TOP_NIGHT= (8, 8, 30)
SKY_BOT_NIGHT= (20, 20, 55)

# Accent palette
CACTUS_GREEN = (30, 150, 30)
CACTUS_DARK  = (15, 100, 15)
STICKMAN_BODY= (20, 90, 210)
STICKMAN_HEAD= (45, 45, 50)
RED          = (230, 50, 40)
GOLD         = (255, 200, 30)
CYAN         = (0, 220, 245)
MAGENTA      = (220, 40, 180)
ORANGE       = (255, 130, 30)

# Aircraft
JET_BODY     = (90, 95, 110)
JET_DARK     = (60, 65, 80)
JET_RED      = (200, 35, 35)
JET_COCKPIT  = (160, 210, 255)
EXHAUST      = (255, 100, 20)
EXHAUST_GLOW = (255, 200, 60)

# Missile
MISSILE_BODY = (210, 210, 50)
MISSILE_TIP  = (255, 60, 20)
MISSILE_TRAIL= (255, 140, 40)

# Ground
GROUND_DAY   = (200, 185, 160)
GROUND_NIGHT = (40, 40, 65)

# ─── Physics ───────────────────────────────────────────────────────────────────
GROUND_Y       = 310
GRAVITY        = 0.75
JUMP_VEL       = -14.0
INIT_SPEED     = 6.5
MAX_SPEED      = 18
SPEED_INC      = 0.003

# ─── Fonts ─────────────────────────────────────────────────────────────────────
F_HUGE   = pygame.font.SysFont("Consolas", 44, bold=True)
F_LARGE  = pygame.font.SysFont("Consolas", 30, bold=True)
F_MED    = pygame.font.SysFont("Consolas", 20, bold=True)
F_SMALL  = pygame.font.SysFont("Consolas", 16)
F_TINY   = pygame.font.SysFont("Consolas", 12)
F_CREDIT = pygame.font.SysFont("Consolas", 15)
F_CRED_T = pygame.font.SysFont("Consolas", 24, bold=True)

AUTHOR  = "Utkarsh Mani Tripathi"
LINKED  = "https://www.linkedin.com/in/utkarsh-mani-tripathi/"


# ═══════════════════════════════════════════════════════════════════════════════
#  8-BIT  SOUND  ENGINE  (Mario-inspired)
# ═══════════════════════════════════════════════════════════════════════════════

def _syn(notes, sr=44100, vol=0.14, wave="square"):
    total = sum(int(sr * d / 1000) for _, d in notes)
    buf = bytearray(total * 2)
    off = 0
    for freq, dur in notes:
        n = int(sr * dur / 1000)
        for i in range(n):
            if freq == 0:
                v = 0
            else:
                t = i / sr
                ph = (freq * t) % 1.0
                if wave == "square":
                    raw = 1.0 if ph < 0.5 else -1.0
                elif wave == "saw":
                    raw = 2.0 * ph - 1.0
                elif wave == "noise":
                    raw = random.uniform(-1, 1)
                else:
                    raw = math.sin(2 * math.pi * freq * t)
                env = max(0.0, 1.0 - (i / n) * 0.4)
                v = int(vol * 32767 * raw * env)
            v = max(-32767, min(32767, v))
            buf[2 * off] = v & 0xFF
            buf[2 * off + 1] = (v >> 8) & 0xFF
            off += 1
    return pygame.mixer.Sound(buffer=bytes(buf))

try:
    SND_JUMP     = _syn([(350 + i * 75, 11) for i in range(10)], vol=0.12)
    SND_LAND     = _syn([(90, 25), (55, 35)], vol=0.09, wave="noise")
    SND_DUCK     = _syn([(280, 18), (220, 20), (160, 22)], vol=0.08, wave="noise")
    SND_COIN     = _syn([(988, 50), (1319, 100)], vol=0.10)
    SND_MILESTONE= _syn([(659,45),(784,45),(1047,45),(784,45),(1047,45),(1319,90)], vol=0.09)
    SND_DEATH    = _syn([(494,100),(466,100),(440,120),(0,40),(349,100),(330,100),(294,160),(262,250)], vol=0.14)
    SND_JET      = _syn([(150+i*35,18) for i in range(14)] + [(640-i*45,22) for i in range(10)], vol=0.10, wave="noise")
    SND_MISSILE  = _syn([(120,12),(250,12),(450,12),(700,15),(1000,18),(1300,20)], vol=0.11, wave="saw")
    SND_NEARMISS = _syn([(1000-i*100, 15) for i in range(8)], vol=0.08, wave="noise")
    SND_SPEEDUP  = _syn([(880, 35), (1100, 50)], vol=0.07, wave="saw")
    SND_EXPLODE  = _syn([(200, 20),(150, 25),(100, 30),(60, 40),(30, 50)], vol=0.13, wave="noise")
    SND_SIREN    = _syn([(600, 60),(800, 60),(600, 60),(800, 60)], vol=0.06, wave="square")
    SND_DODGE    = _syn([(1200, 30), (1500, 40)], vol=0.06)
except Exception:
    SND_JUMP = SND_LAND = SND_DUCK = SND_COIN = SND_MILESTONE = SND_DEATH = None
    SND_JET = SND_MISSILE = SND_NEARMISS = SND_SPEEDUP = SND_EXPLODE = SND_SIREN = SND_DODGE = None


# ═══════════════════════════════════════════════════════════════════════════════
#  SCREEN  SHAKE
# ═══════════════════════════════════════════════════════════════════════════════
shake_amount = 0
shake_decay  = 0.85

def trigger_shake(intensity=8):
    global shake_amount
    shake_amount = max(shake_amount, intensity)

def get_shake_offset():
    global shake_amount
    if shake_amount < 0.5:
        shake_amount = 0
        return 0, 0
    ox = random.randint(int(-shake_amount), int(shake_amount))
    oy = random.randint(int(-shake_amount), int(shake_amount))
    shake_amount *= shake_decay
    return ox, oy


# ═══════════════════════════════════════════════════════════════════════════════
#  PARTICLE  SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class Particle:
    __slots__ = ("x","y","vx","vy","life","ml","col","sz")
    def __init__(self, x, y, vx, vy, life, col, sz=3):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.life=life; self.ml=life; self.col=col; self.sz=sz
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.06; self.life-=1
    def draw(self, surf):
        a = max(0, int(255*self.life/self.ml))
        s = max(1, int(self.sz * self.life / self.ml))
        ps = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
        pygame.draw.circle(ps, (*self.col[:3], a), (s,s), s)
        surf.blit(ps, (int(self.x)-s, int(self.y)-s))

particles: list[Particle] = []

def emit(x, y, col, n=6, spd=2.5, life=18, sz=3):
    for _ in range(n):
        particles.append(Particle(x, y,
            random.uniform(-spd, spd), random.uniform(-spd, 0.5),
            life + random.randint(-3, 3), col, sz))

def emit_explosion(x, y, n=20, sz=5):
    """Big colourful explosion."""
    colours = [RED, ORANGE, GOLD, EXHAUST, WHITE]
    for _ in range(n):
        c = random.choice(colours)
        s = random.uniform(1, spd := 5)
        a = random.uniform(0, 2 * math.pi)
        particles.append(Particle(x, y,
            math.cos(a)*s, math.sin(a)*s,
            random.randint(15, 30), c, random.randint(2, sz)))

def emit_sparks(x, y, n=8):
    for _ in range(n):
        particles.append(Particle(x, y,
            random.uniform(-3, 3), random.uniform(-4, -1),
            random.randint(8, 16), GOLD, 2))


# ═══════════════════════════════════════════════════════════════════════════════
#  STICKMAN  SPRITES
# ═══════════════════════════════════════════════════════════════════════════════

def _stick_run():
    frames = []
    W, H, LW = 44, 60, 3
    legs = [
        ((-5,10),(-9,20)), ((6,10),(11,18)),
        ((-2,10),(-3,20)), ((2,10),(3,20)),
        ((6,10),(11,18)), ((-5,10),(-9,20)),
        ((2,10),(3,20)), ((-2,10),(-3,20)),
    ]
    arms = [((9,11),(-7,13)),((3,13),(-3,13)),((-7,13),(9,11)),((-3,13),(3,13))]
    for fi in range(4):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        cx = W//2
        pygame.draw.circle(s, STICKMAN_HEAD, (cx,8), 7, LW)
        pygame.draw.circle(s, WHITE, (cx+3,7), 2)
        pygame.draw.line(s, STICKMAN_BODY, (cx,15), (cx,34), LW)
        for ax,ay in arms[fi]:
            pygame.draw.line(s, STICKMAN_BODY, (cx,20), (cx+ax,20+ay), LW)
        for ki in range(2):
            kn, ft = legs[fi*2+ki]
            pygame.draw.line(s, STICKMAN_BODY, (cx,34), (cx+kn[0],34+kn[1]), LW)
            pygame.draw.line(s, STICKMAN_BODY, (cx+kn[0],34+kn[1]), (cx+ft[0],34+ft[1]), LW)
        frames.append(s)
    return frames

def _stick_jump():
    W,H,LW = 44,54,3
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    cx = W//2
    pygame.draw.circle(s, STICKMAN_HEAD, (cx,8), 7, LW)
    pygame.draw.circle(s, WHITE, (cx+3,6), 2)
    pygame.draw.line(s, STICKMAN_BODY, (cx,15), (cx,34), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,20), (cx-11,9), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,20), (cx+11,9), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,34), (cx-8,42), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx-8,42), (cx-4,50), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,34), (cx+8,42), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx+8,42), (cx+4,50), LW)
    return s

def _stick_duck():
    frames = []
    W,H,LW = 60,30,3
    for fi in range(2):
        s = pygame.Surface((W,H), pygame.SRCALPHA)
        pygame.draw.circle(s, STICKMAN_HEAD, (48,8), 6, LW)
        pygame.draw.circle(s, WHITE, (51,7), 2)
        pygame.draw.line(s, STICKMAN_BODY, (14,13), (42,11), LW)
        pygame.draw.line(s, STICKMAN_BODY, (20,13), (8, 6 if fi==0 else 9), LW)
        pygame.draw.line(s, STICKMAN_BODY, (14,13), (6, 24 if fi==0 else 27), LW)
        pygame.draw.line(s, STICKMAN_BODY, (14,13), (18, 25 if fi==0 else 21), LW)
        frames.append(s)
    return frames

def _stick_dead():
    W,H,LW = 48,56,3
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    cx = W//2
    pygame.draw.circle(s, RED, (cx,8), 7, LW)
    for dx in [-3,3]:
        pygame.draw.line(s, RED, (cx+dx-2,5),(cx+dx+2,9), 2)
        pygame.draw.line(s, RED, (cx+dx+2,5),(cx+dx-2,9), 2)
    pygame.draw.line(s, STICKMAN_BODY, (cx,15),(cx,34), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,20),(cx-13,32), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,20),(cx+13,32), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,34),(cx-11,52), LW)
    pygame.draw.line(s, STICKMAN_BODY, (cx,34),(cx+11,52), LW)
    return s

SRUN  = _stick_run()
SJUMP = _stick_jump()
SDUCK = _stick_duck()
SDEAD = _stick_dead()


# ═══════════════════════════════════════════════════════════════════════════════
#  COLOURED  CACTI
# ═══════════════════════════════════════════════════════════════════════════════

def _mk_cactus(v):
    flower_cols = [(255,220,60),(255,100,150),(255,80,80),(180,100,255)]
    if v == 0:
        s = pygame.Surface((18,38), pygame.SRCALPHA)
        pygame.draw.rect(s, CACTUS_GREEN, (5,0,8,38))
        pygame.draw.rect(s, CACTUS_DARK, (0,8,5,14))
        pygame.draw.rect(s, CACTUS_DARK, (13,14,5,12))
        pygame.draw.circle(s, flower_cols[0], (9,3), 4)
    elif v == 1:
        s = pygame.Surface((20,50), pygame.SRCALPHA)
        pygame.draw.rect(s, CACTUS_GREEN, (6,0,8,50))
        pygame.draw.rect(s, CACTUS_DARK, (0,8,6,16))
        pygame.draw.rect(s, CACTUS_DARK, (14,14,6,14))
        pygame.draw.circle(s, flower_cols[1], (10,3), 4)
    elif v == 2:
        s = pygame.Surface((36,38), pygame.SRCALPHA)
        pygame.draw.rect(s, CACTUS_GREEN, (4,4,8,34)); pygame.draw.rect(s, CACTUS_DARK, (0,10,4,12))
        pygame.draw.rect(s, CACTUS_GREEN, (22,0,8,38)); pygame.draw.rect(s, CACTUS_DARK, (18,8,4,12))
        pygame.draw.rect(s, CACTUS_DARK, (30,14,4,10))
        pygame.draw.circle(s, flower_cols[2], (26,3), 3)
    else:
        s = pygame.Surface((52,42), pygame.SRCALPHA)
        for xo in [0,18,34]:
            h = random.randint(30,42); ys = 42-h
            pygame.draw.rect(s, CACTUS_GREEN, (xo+4,ys,8,h))
            pygame.draw.rect(s, CACTUS_DARK, (xo,ys+6,4,12))
            pygame.draw.rect(s, CACTUS_DARK, (xo+12,ys+10,4,10))
        pygame.draw.circle(s, flower_cols[3], (8,2), 3)
    return s

CACTI = [_mk_cactus(i) for i in range(4)]


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGHTER  JET  (facing LEFT → towards the player)
# ═══════════════════════════════════════════════════════════════════════════════

def _mk_jet():
    frames = []
    W, H = 60, 26
    for fi in range(2):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        # Fuselage  (nose on LEFT)
        pygame.draw.rect(s, JET_BODY, (14, 9, 38, 8))
        # Nose cone pointing LEFT
        pygame.draw.polygon(s, JET_RED, [(14,9), (0,13), (14,17)])
        # Cockpit canopy
        pygame.draw.rect(s, JET_COCKPIT, (16, 10, 8, 6))
        pygame.draw.rect(s, (120,180,230), (16, 10, 8, 3))  # glass glint
        # Top wing (swept)
        pygame.draw.polygon(s, JET_DARK, [(30,9), (44,9), (48,0), (34,0)])
        # Bottom wing
        pygame.draw.polygon(s, JET_DARK, [(30,17), (44,17), (48,26), (34,26)])
        # Tail fins
        pygame.draw.polygon(s, JET_RED, [(50,7), (52,9), (50,9)])
        pygame.draw.polygon(s, JET_RED, [(50,17), (52,17), (50,19)])
        # Vertical stabiliser
        pygame.draw.polygon(s, JET_RED, [(46,9), (52,9), (54,4)])
        # Exhaust flame on RIGHT side (rear of jet)
        if fi == 0:
            pygame.draw.polygon(s, EXHAUST, [(52,11), (60,13), (52,15)])
            pygame.draw.polygon(s, EXHAUST_GLOW, [(52,12), (57,13), (52,14)])
        else:
            pygame.draw.polygon(s, EXHAUST, [(52,10), (62,13), (52,16)])
            pygame.draw.polygon(s, EXHAUST_GLOW, [(52,11), (59,13), (52,15)])
        # Missile hardpoints under wings
        pygame.draw.rect(s, MISSILE_BODY, (34, 4, 6, 2))
        pygame.draw.rect(s, MISSILE_BODY, (34, 20, 6, 2))
        frames.append(s)
    return frames

JET_FRAMES = _mk_jet()


# ═══════════════════════════════════════════════════════════════════════════════
#  MISSILE  (pointing LEFT → towards player)
# ═══════════════════════════════════════════════════════════════════════════════

def _mk_missile():
    W, H = 22, 8
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(s, MISSILE_BODY, (6, 2, 12, 4))
    # Tip pointing LEFT
    pygame.draw.polygon(s, MISSILE_TIP, [(6,2), (0,4), (6,6)])
    # Tail fins on RIGHT
    pygame.draw.polygon(s, (180,180,50), [(18,0), (18,2), (22,1)])
    pygame.draw.polygon(s, (180,180,50), [(18,6), (18,8), (22,7)])
    # Exhaust glow on right
    pygame.draw.circle(s, EXHAUST, (20, 4), 3)
    pygame.draw.circle(s, EXHAUST_GLOW, (20, 4), 2)
    return s

MISSILE_IMG = _mk_missile()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════

def _mk_cloud():
    s = pygame.Surface((50,20), pygame.SRCALPHA)
    c = (225,235,250)
    pygame.draw.ellipse(s, c, (10,4,30,14))
    pygame.draw.ellipse(s, c, (0,6,22,12))
    pygame.draw.ellipse(s, c, (28,6,22,12))
    pygame.draw.ellipse(s, c, (14,0,20,14))
    return s

def _mk_star():
    s = pygame.Surface((6,6), pygame.SRCALPHA)
    c = (220,220,255)
    pygame.draw.line(s, c, (3,0),(3,5),1)
    pygame.draw.line(s, c, (0,3),(5,3),1)
    return s

def _mk_moon():
    s = pygame.Surface((30,30), pygame.SRCALPHA)
    pygame.draw.circle(s, (235,235,255), (15,15), 14)
    pygame.draw.circle(s, (0,0,0,0), (22,10), 12)
    pygame.draw.circle(s, (215,215,235), (11,13), 3)
    pygame.draw.circle(s, (215,215,235), (9,22), 2)
    return s

CLOUD_IMG = _mk_cloud()
STAR_IMG  = _mk_star()
MOON_IMG  = _mk_moon()


# ═══════════════════════════════════════════════════════════════════════════════
#  GAME  CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class Player:
    def __init__(self):
        self.x = 70; self.y = GROUND_Y
        self.vy = 0; self.jumping = False; self.ducking = False
        self.dead = False; self.fi = 0; self.at = 0
        self.was_air = False; self.dodges = 0

    @property
    def img(self):
        if self.dead:    return SDEAD
        if self.jumping: return SJUMP
        if self.ducking: return SDUCK[self.fi % 2]
        return SRUN[self.fi % 4]

    @property
    def rect(self):
        i = self.img
        if self.ducking:
            return pygame.Rect(self.x+8, self.y+30, i.get_width()-16, i.get_height()-4)
        return pygame.Rect(self.x+12, self.y+4, i.get_width()-24, i.get_height()-10)

    def jump(self):
        if not self.jumping and not self.dead:
            self.vy = JUMP_VEL; self.jumping = True; self.ducking = False
            if SND_JUMP: SND_JUMP.play()
            emit(self.x+22, GROUND_Y+58, (180,180,200), 4, 1.2, 10, 2)

    def duck(self, d):
        if self.dead: return
        if self.jumping and d: self.vy += 1.5; return
        was = self.ducking
        self.ducking = d and not self.jumping
        if self.ducking and not was and SND_DUCK: SND_DUCK.play()

    def update(self):
        self.was_air = self.jumping
        if self.jumping:
            self.vy += GRAVITY; self.y += self.vy
            if self.y >= GROUND_Y:
                self.y = GROUND_Y; self.vy = 0; self.jumping = False
                if self.was_air:
                    if SND_LAND: SND_LAND.play()
                    emit(self.x+22, GROUND_Y+58, (160,140,110), 5, 1.8, 12, 2)
                    trigger_shake(3)
        self.at += 1
        if self.at >= 4: self.at = 0; self.fi = (self.fi+1) % 4

    def draw(self, surf):
        if self.ducking: surf.blit(self.img, (self.x, self.y+30))
        else: surf.blit(self.img, (self.x, self.y))


class Missile:
    def __init__(self, x, y, vx, vy):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.tt=0; self.warned=False; self.dodged=False
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x)+1, int(self.y)+1, 18, 6)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.tt += 1
        if self.tt % 2 == 0:
            emit(self.x+18, self.y+4, MISSILE_TRAIL, 1, 0.6, 8, 2)

    def draw(self, surf):
        surf.blit(MISSILE_IMG, (int(self.x), int(self.y)))

    def off(self):
        return self.x < -30 or self.y > SCREEN_H + 20 or self.x > SCREEN_W + 30


class Jet:
    def __init__(self, x, y, speed, wave_type="straight"):
        self.x=x; self.y=y; self.speed=speed
        self.fi=0; self.at=0
        self.mfired=0; self.mcd=random.randint(15,35)
        self.wave = wave_type
        self.base_y = y
        self.t = 0
        # Aggressive: more missiles at higher speeds
        self.max_m = random.randint(2, 4) if speed > 10 else random.randint(1, 3)
        if SND_JET: SND_JET.play()

    @property
    def rect(self):
        return pygame.Rect(int(self.x)+4, int(self.y)+5, 48, 16)

    def update(self, speed, ml):
        self.t += 1
        # Movement patterns
        if self.wave == "dive":
            self.x -= speed * 0.6 + 2
            if self.t > 30:
                self.y += 1.5  # dive down
        elif self.wave == "sine":
            self.x -= speed * 0.5 + 1.5
            self.y = self.base_y + math.sin(self.t * 0.08) * 30
        elif self.wave == "fast":
            self.x -= speed * 0.9 + 3
        else:  # straight
            self.x -= speed * 0.6 + 1

        self.at += 1
        if self.at >= 5: self.at = 0; self.fi = (self.fi+1) % 2

        # Exhaust particles
        if random.random() < 0.4:
            emit(self.x+55, self.y+13, EXHAUST, 1, 1.2, 7, 2)

        # Fire missiles
        self.mcd -= 1
        if self.mfired < self.max_m and self.mcd <= 0 and self.x < SCREEN_W - 40:
            # Missiles aimed generally at player area (left + down)
            mvx = -3.5 - speed * 0.25 + random.uniform(-0.5, 0.5)
            mvy = random.uniform(1.5, 3.5)
            ml.append(Missile(self.x + 10, self.y + 18, mvx, mvy))
            self.mfired += 1
            self.mcd = random.randint(18, 40)
            if SND_MISSILE: SND_MISSILE.play()
            trigger_shake(2)
            emit(self.x+10, self.y+18, EXHAUST, 4, 1.5, 8, 2)

    def draw(self, surf):
        surf.blit(JET_FRAMES[self.fi], (int(self.x), int(self.y)))

    def off(self):
        return self.x < -80 or self.y > SCREEN_H + 30


class Cactus:
    def __init__(self, x, score):
        self.x = x
        v = random.randint(0, min(3, 1 + score // 180))
        self.img = CACTI[v]
        self.w = self.img.get_width(); self.h = self.img.get_height()
        self.y = GROUND_Y + 60 - self.h

    @property
    def rect(self):
        return pygame.Rect(self.x+4, self.y+4, self.w-8, self.h-8)

    def update(self, spd): self.x -= spd
    def draw(self, surf): surf.blit(self.img, (int(self.x), int(self.y)))
    def off(self): return self.x < -60


class CloudObj:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else SCREEN_W + random.randint(20, 200)
        self.y = y if y is not None else random.randint(15, 90)
        self.spd = random.uniform(0.3, 1.0)
    def update(self): self.x -= self.spd
    def draw(self, surf, night):
        if night:
            t = CLOUD_IMG.copy(); t.fill((70,70,110), special_flags=pygame.BLEND_RGB_MIN)
            surf.blit(t, (int(self.x), self.y))
        else:
            surf.blit(CLOUD_IMG, (int(self.x), self.y))
    def off(self): return self.x < -55

class StarObj:
    def __init__(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(5, 110)
        self.t = random.randint(0, 60)
    def update(self): self.t = (self.t+1) % 60
    def draw(self, surf):
        if self.t < 42: surf.blit(STAR_IMG, (self.x, self.y))

class Ground:
    def __init__(self):
        self.segs = []
        x = 0
        while x < SCREEN_W + 200:
            l = random.randint(10, 60); yo = random.choice([0,1,2])
            self.segs.append([x, l, yo]); x += l + random.randint(5, 30)
    def update(self, spd):
        for s in self.segs: s[0] -= spd
        self.segs = [s for s in self.segs if s[0]+s[1] > -10]
        r = max((s[0]+s[1] for s in self.segs), default=0)
        while r < SCREEN_W + 200:
            l = random.randint(10,60); yo = random.choice([0,1,2])
            g = random.randint(5,30); self.segs.append([r+g, l, yo]); r += g+l
    def draw(self, surf, night):
        gy = GROUND_Y + 60
        col = GROUND_NIGHT if night else DARK_GRAY
        pygame.draw.line(surf, col, (0,gy), (SCREEN_W,gy), 2)
        for x,l,yo in self.segs:
            pygame.draw.rect(surf, col, (x, gy+4+yo, l, 1))


# ═══════════════════════════════════════════════════════════════════════════════
#  DANGER  HUD  ELEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_warning_bar(surf, tick, jet_count, missile_count):
    """Pulsing danger bar when enemies are active."""
    if jet_count == 0 and missile_count == 0:
        return
    pulse = abs(math.sin(tick * 0.1))
    # Red border pulse
    alpha = int(40 + 60 * pulse)
    border = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    for i in range(3):
        pygame.draw.rect(border, (255, 0, 0, alpha // (i+1)),
                         (i, i, SCREEN_W - i*2, SCREEN_H - i*2), 2)
    surf.blit(border, (0, 0))

    # Warning text
    if tick % 30 < 22:
        if missile_count > 3:
            wt = F_SMALL.render("⚠ MISSILE BARRAGE!", True, RED)
        elif jet_count > 1:
            wt = F_SMALL.render(f"⚠ {jet_count} JETS INCOMING!", True, RED)
        elif jet_count == 1:
            wt = F_SMALL.render("⚠ JET INCOMING!", True, ORANGE)
        else:
            wt = F_SMALL.render(f"⚠ {missile_count} MISSILES!", True, ORANGE)
        surf.blit(wt, (SCREEN_W - wt.get_width() - 14, 50))

def draw_dodge_counter(surf, dodges):
    if dodges > 0:
        col = GOLD if dodges < 10 else CYAN if dodges < 25 else MAGENTA
        dt = F_SMALL.render(f"DODGES: {dodges}", True, col)
        surf.blit(dt, (14, 34))


# ═══════════════════════════════════════════════════════════════════════════════
#  CREDITS
# ═══════════════════════════════════════════════════════════════════════════════

def show_credits():
    run = True; t = 0
    while run:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_c, pygame.K_RETURN, pygame.K_SPACE):
                    run = False
        t += 1
        screen.fill((10, 10, 24))

        # Animated accent bars
        bc = tuple(max(0,min(255, int(c*(0.5+0.5*math.sin(t*0.025))))) for c in GOLD)
        pygame.draw.line(screen, bc, (50,32),(SCREEN_W-50,32), 2)

        ti = F_CRED_T.render("—  C R E D I T S  —", True, GOLD)
        screen.blit(ti, (SCREEN_W//2 - ti.get_width()//2, 45))

        entries = [
            ("Game", "Stickman Runner"),
            None,
            ("Created by", AUTHOR),
            None,
            ("LinkedIn", "linkedin.com/in/utkarsh-mani-tripathi/"),
            ("Full URL", LINKED),
            None,
            ("Engine", "Python + Pygame"),
            ("Sound Design", "Mario-inspired 8-bit audio"),
            ("Art Style", "Pixel-art & stickman characters"),
            ("Enemies", "Fighter jets with missile barrages"),
            ("Features", "Screen shake, particles, day/night cycle"),
            None,
            None,
            ("", "Thank you for playing!"),
        ]

        y = 88
        for e in entries:
            if e is None: y += 12; continue
            lb, vl = e
            if lb:
                ls = F_CREDIT.render(f"{lb}:", True, LIGHT_GRAY)
                screen.blit(ls, (SCREEN_W//2 - 230, y))
                vs = F_CREDIT.render(vl, True, WHITE)
                screen.blit(vs, (SCREEN_W//2 - 50, y))
            else:
                vs = F_CREDIT.render(vl, True, GOLD)
                screen.blit(vs, (SCREEN_W//2 - vs.get_width()//2, y))
            y += 22

        pygame.draw.line(screen, bc, (50, y+12), (SCREEN_W-50, y+12), 2)
        p = F_TINY.render("Press ESC / C / SPACE to return", True, LIGHT_GRAY)
        screen.blit(p, (SCREEN_W//2 - p.get_width()//2, SCREEN_H-22))
        pygame.display.flip(); clock.tick(FPS)


# ═══════════════════════════════════════════════════════════════════════════════
#  SKY  GRADIENT  RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

sky_cache_day = None
sky_cache_night = None

def build_sky_caches():
    global sky_cache_day, sky_cache_night
    h = GROUND_Y + 60
    sky_cache_day = pygame.Surface((1, h))
    sky_cache_night = pygame.Surface((1, h))
    for row in range(h):
        ratio = row / h
        # Day gradient
        r = int(SKY_TOP_DAY[0] + (SKY_BOT_DAY[0] - SKY_TOP_DAY[0]) * ratio)
        g = int(SKY_TOP_DAY[1] + (SKY_BOT_DAY[1] - SKY_TOP_DAY[1]) * ratio)
        b = int(SKY_TOP_DAY[2] + (SKY_BOT_DAY[2] - SKY_TOP_DAY[2]) * ratio)
        sky_cache_day.set_at((0, row), (r, g, b))
        # Night gradient
        r = int(SKY_TOP_NIGHT[0] + (SKY_BOT_NIGHT[0] - SKY_TOP_NIGHT[0]) * ratio)
        g = int(SKY_TOP_NIGHT[1] + (SKY_BOT_NIGHT[1] - SKY_TOP_NIGHT[1]) * ratio)
        b = int(SKY_TOP_NIGHT[2] + (SKY_BOT_NIGHT[2] - SKY_TOP_NIGHT[2]) * ratio)
        sky_cache_night.set_at((0, row), (r, g, b))

build_sky_caches()

def draw_sky(surf, night_alpha):
    h = GROUND_Y + 60
    if night_alpha <= 0:
        scaled = pygame.transform.scale(sky_cache_day, (SCREEN_W, h))
        surf.blit(scaled, (0, 0))
    elif night_alpha >= 255:
        scaled = pygame.transform.scale(sky_cache_night, (SCREEN_W, h))
        surf.blit(scaled, (0, 0))
    else:
        day_s = pygame.transform.scale(sky_cache_day, (SCREEN_W, h))
        night_s = pygame.transform.scale(sky_cache_night, (SCREEN_W, h))
        night_s.set_alpha(night_alpha)
        surf.blit(day_s, (0, 0))
        surf.blit(night_s, (0, 0))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN  GAME
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    global particles, shake_amount
    hi_score = 0

    while True:
        # ── Reset ──
        player = Player()
        cacti: list[Cactus] = []
        jets: list[Jet] = []
        missiles: list[Missile] = []
        clouds = [CloudObj(random.randint(0,SCREEN_W), random.randint(15,90)) for _ in range(5)]
        stars = [StarObj() for _ in range(30)]
        ground = Ground()
        particles = []
        shake_amount = 0
        speed = INIT_SPEED
        score = 0
        game_over = False
        sp_timer = 0; jet_timer = 0
        night = False; night_a = 0
        flash = 0; warn = 0; spd_ms = 1; tick = 0
        danger_level = 0  # increases over time
        wave_active = False; wave_jets = 0

        # ── Start Screen ──
        wait = True; blink = 0
        while wait:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_SPACE, pygame.K_UP): wait = False
                    if ev.key == pygame.K_c: show_credits()
                    if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

            blink = (blink + 1) % 80

            # Gradient BG
            draw_sky(screen, 0)
            pygame.draw.rect(screen, GROUND_DAY, (0, GROUND_Y+60, SCREEN_W, SCREEN_H-GROUND_Y-60))

            # Title
            t1 = F_HUGE.render("STICKMAN", True, DARK_GRAY)
            t2 = F_HUGE.render("RUNNER", True, RED)
            tw = t1.get_width() + 16 + t2.get_width()
            tx = SCREEN_W//2 - tw//2
            screen.blit(t1, (tx, 28)); screen.blit(t2, (tx+t1.get_width()+16, 28))

            by = F_CREDIT.render(f"by {AUTHOR}", True, STICKMAN_BODY)
            screen.blit(by, (SCREEN_W//2 - by.get_width()//2, 78))

            # Animated stickman
            pf = (blink // 6) % 4
            screen.blit(SRUN[pf], (SCREEN_W//2 - 22, 105))

            # Animated jet flying across
            jf = (blink // 8) % 2
            jx = SCREEN_W - ((blink * 4) % (SCREEN_W + 100))
            screen.blit(JET_FRAMES[jf], (jx, 160))

            if blink < 55:
                pr = F_SMALL.render("Press SPACE or UP to start", True, DARK_GRAY)
                screen.blit(pr, (SCREEN_W//2 - pr.get_width()//2, 200))

            ct = F_TINY.render("SPACE/UP = Jump  |  DOWN = Duck  |  C = Credits  |  ESC = Quit", True, LIGHT_GRAY)
            screen.blit(ct, (SCREEN_W//2 - ct.get_width()//2, 232))

            if hi_score > 0:
                hs = F_MED.render(f"★ HI {hi_score:05d} ★", True, GOLD)
                screen.blit(hs, (SCREEN_W//2 - hs.get_width()//2, 262))

            # Footer
            pygame.draw.rect(screen, (230,230,240), (0, SCREEN_H-28, SCREEN_W, 28))
            ft = F_TINY.render(f"{AUTHOR}  ·  linkedin.com/in/utkarsh-mani-tripathi", True, LIGHT_GRAY)
            screen.blit(ft, (SCREEN_W//2 - ft.get_width()//2, SCREEN_H-20))

            ground.draw(screen, False)
            pygame.display.flip(); clock.tick(FPS)

        player.jump()

        # ── Gameplay ──
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    if game_over and ev.key in (pygame.K_RETURN, pygame.K_SPACE): break
                    if game_over and ev.key == pygame.K_c: show_credits()
                    if not game_over:
                        if ev.key in (pygame.K_SPACE, pygame.K_UP): player.jump()
                        if ev.key == pygame.K_DOWN: player.duck(True)
                if ev.type == pygame.KEYUP:
                    if ev.key == pygame.K_DOWN: player.duck(False)
            else:
                tick += 1
                if not game_over:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_DOWN]: player.duck(True)
                    player.update()
                    speed = min(MAX_SPEED, speed + SPEED_INC)
                    danger_level = score / 150  # ramps up continuously

                    # Speed milestone
                    if int(speed) >= spd_ms + 2:
                        spd_ms = int(speed)
                        if SND_SPEEDUP: SND_SPEEDUP.play()

                    # ── Spawn cacti ──
                    sp_timer += 1
                    mg = max(30, 65 - int(speed * 2))
                    if sp_timer > mg and random.random() < 0.03 + speed * 0.004:
                        cacti.append(Cactus(SCREEN_W + random.randint(0, 70), score))
                        sp_timer = 0

                    for c in cacti: c.update(speed)
                    cacti = [c for c in cacti if not c.off()]

                    # ── Spawn jets  (INTENSE!) ──
                    jet_timer += 1
                    # Jet spawn rate increases with danger
                    jet_threshold = max(60, int(250 - danger_level * 8))
                    jet_chance = min(0.15, 0.02 + danger_level * 0.005)

                    if score > 150 and jet_timer > jet_threshold and random.random() < jet_chance:
                        # Pick a wave type based on danger
                        if danger_level > 8 and random.random() < 0.3:
                            # FORMATION ATTACK — multiple jets at once!
                            n = random.randint(2, min(4, int(danger_level // 3)))
                            wave_types = ["straight", "dive", "sine", "fast"]
                            if SND_SIREN: SND_SIREN.play()
                            for i in range(n):
                                jy = 30 + i * 40 + random.randint(-5, 5)
                                wt = random.choice(wave_types)
                                jets.append(Jet(SCREEN_W + 30 + i * 50, jy, speed, wt))
                            warn = 60
                        else:
                            jy = random.choice([30, 60, 90, 130, 170])
                            wt = random.choice(["straight", "dive", "sine", "fast"])
                            jets.append(Jet(SCREEN_W + 20, jy, speed, wt))
                            warn = 40
                        jet_timer = 0

                    for j in jets: j.update(speed, missiles)
                    jets = [j for j in jets if not j.off()]

                    # ── Update missiles ──
                    for m in missiles:
                        m.update()
                        # Near-miss detection (close call but didn't hit)
                        pr = player.rect
                        mx, my = m.x, m.y
                        if not m.warned and not m.dodged:
                            if abs(mx - pr.x) < 35 and abs(my - pr.centery) < 35:
                                m.warned = True
                                if SND_NEARMISS: SND_NEARMISS.play()
                        # Track successful dodges
                        if m.warned and not m.dodged and m.x < player.x - 20:
                            m.dodged = True
                            player.dodges += 1
                            if SND_DODGE: SND_DODGE.play()
                            emit_sparks(player.x + 20, player.y + 20, 5)
                    missiles = [m for m in missiles if not m.off()]

                    # ── Collision ──
                    pr = player.rect
                    hit = False
                    for c in cacti:
                        if pr.colliderect(c.rect):
                            hit = True
                            emit_explosion(c.x + c.w//2, c.y + c.h//2, 18)
                            break
                    if not hit:
                        for m in missiles:
                            if m.alive and pr.colliderect(m.rect):
                                hit = True; m.alive = False
                                emit_explosion(m.x, m.y, 22)
                                trigger_shake(12)
                                break
                    if not hit:
                        for j in jets:
                            if pr.colliderect(j.rect):
                                hit = True
                                emit_explosion(player.x+22, player.y+15, 30, 7)
                                trigger_shake(15)
                                break
                    if hit:
                        game_over = True; player.dead = True
                        if SND_DEATH: SND_DEATH.play()
                        if SND_EXPLODE: SND_EXPLODE.play()
                        trigger_shake(20)
                        emit_explosion(player.x+22, player.y+25, 25, 6)
                        if score > hi_score: hi_score = score

                    # ── Score ──
                    score += 1
                    if score % 50 == 0 and score % 100 != 0 and SND_COIN:
                        SND_COIN.play(); emit_sparks(SCREEN_W-100, 14, 4)
                    if score % 100 == 0 and SND_MILESTONE:
                        SND_MILESTONE.play(); flash = 25

                    # Day/Night
                    cyc = (score // 600) % 2
                    tgt = 255 if cyc == 1 else 0
                    if night_a < tgt: night_a = min(255, night_a+3)
                    elif night_a > tgt: night_a = max(0, night_a-3)
                    night = night_a > 127

                    if random.random() < 0.007: clouds.append(CloudObj())
                    for c in clouds: c.update()
                    clouds = [c for c in clouds if not c.off()]
                    for s in stars: s.update()
                    ground.update(speed)
                    if flash > 0: flash -= 1
                    if warn > 0: warn -= 1

                # ── Particles ──
                for p in particles: p.update()
                particles = [p for p in particles if p.life > 0]

                # ════════════ DRAW ════════════
                sx, sy = get_shake_offset()

                # Sky
                draw_sky(screen, night_a)

                # Ground fill
                gf = GROUND_NIGHT if night else GROUND_DAY
                pygame.draw.rect(screen, gf, (0, GROUND_Y+60, SCREEN_W, SCREEN_H-GROUND_Y-60))

                # Create offset surface for shake
                frame = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

                # Stars & moon
                if night_a > 50:
                    for s in stars: s.draw(frame)
                    frame.blit(MOON_IMG, (SCREEN_W - 100, 20))

                for c in clouds: c.draw(frame, night)
                ground.draw(frame, night)

                # Cacti
                for c in cacti: c.draw(frame)

                # Jets
                for j in jets: j.draw(frame)

                # Missiles
                for m in missiles:
                    if m.alive: m.draw(frame)

                # Player
                player.draw(frame)

                # Particles
                for p in particles: p.draw(frame)

                # Apply shake
                screen.blit(frame, (sx, sy))

                # HUD (no shake)
                # Danger HUD
                draw_warning_bar(screen, tick, len(jets), len(missiles))
                draw_dodge_counter(screen, player.dodges)

                # Score
                sc = WHITE if night else DARK_GRAY
                if flash > 0 and flash % 4 < 2: sc = GOLD
                st = F_SMALL.render(f"{score:05d}", True, sc)
                screen.blit(st, (SCREEN_W - 110, 14))
                if hi_score > 0:
                    ht = F_SMALL.render(f"HI {hi_score:05d}", True, LIGHT_GRAY)
                    screen.blit(ht, (SCREEN_W - 245, 14))

                # Speed
                spc = RED if speed > 13 else ORANGE if speed > 10 else CYAN
                spd_t = F_TINY.render(f"SPD {speed:.1f}", True, spc)
                screen.blit(spd_t, (14, 16))

                # Danger level indicator
                dl_col = RED if danger_level > 10 else ORANGE if danger_level > 5 else GOLD
                dl_t = F_TINY.render(f"DANGER LV {int(danger_level)}", True, dl_col)
                screen.blit(dl_t, (14, 52))

                # Author
                wm_c = (120,120,150) if night else (180,180,190)
                wm = F_TINY.render(f"by {AUTHOR}", True, wm_c)
                screen.blit(wm, (8, SCREEN_H - 15))

                # ── Game Over ──
                if game_over:
                    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                    ov.fill((0, 0, 0, 130))
                    screen.blit(ov, (0,0))

                    go = F_LARGE.render("G A M E   O V E R", True, RED)
                    screen.blit(go, (SCREEN_W//2 - go.get_width()//2, SCREEN_H//2 - 70))

                    fs = F_MED.render(f"Score: {score:05d}   Dodges: {player.dodges}", True, WHITE)
                    screen.blit(fs, (SCREEN_W//2 - fs.get_width()//2, SCREEN_H//2 - 25))

                    if score >= hi_score and score > 0:
                        nb = F_MED.render("★  NEW BEST!  ★", True, GOLD)
                        screen.blit(nb, (SCREEN_W//2 - nb.get_width()//2, SCREEN_H//2 + 10))

                    rx, ry = SCREEN_W//2, SCREEN_H//2 + 50
                    pygame.draw.rect(screen, WHITE, (rx-16, ry-13, 32, 26), 2, border_radius=5)
                    pygame.draw.polygon(screen, WHITE, [(rx-3,ry-5),(rx+7,ry),(rx-3,ry+5)])

                    rt = F_TINY.render("ENTER / SPACE to restart  |  C = Credits  |  ESC = Quit", True, LIGHT_GRAY)
                    screen.blit(rt, (SCREEN_W//2 - rt.get_width()//2, SCREEN_H//2 + 80))

                pygame.display.flip()
                clock.tick(FPS)
                continue
            break


if __name__ == "__main__":
    main()
