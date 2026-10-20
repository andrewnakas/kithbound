"""KITHBOUND battle choreography: our own frame blocks, anchor points, frame sequences,
per-move scripts and per-move sound choices.

    python -m games.pokered.anims_gen <tree>                  rewrite the five tables
    python -m games.pokered.anims_gen --check <tree> <retail>  dirty-room check: share of
                                                               entries that differ

Rewrites, in <tree>:
    data/battle_anims/frame_blocks.asm   FrameBlockPointers + one block per slot
    data/battle_anims/base_coords.asm    FrameBlockBaseCoords
    data/battle_anims/subanimations.asm  SubanimationPointers + one sequence per id
    data/moves/animations.asm            AttackAnimationPointers + one script per label
    data/moves/sfx.asm                   MoveSoundTable

Labels, table lengths and constant names stay what the engine and constants expect.
Engine contracts honoured (engine/battle/animations.asm, engine/movie/trade.asm):
    - ball toss sequences have 11 frames (a sound plays at counter 11, the trainer/ghost
      code looks at the last three), the ball shake has exactly 4 frames drawn in place
      (the engine rewinds 4 frames per extra shake), the enemy poof has >= 5 frames;
    - trade ball: drop >= 6 frames (the mon is hidden at counter 6), shake and drop drawn in
      place in 4 sprites (the engine moves OAM entries 0-3), appear is one frame that is
      not cleared (the engine bounces it);
    - the snarl/cry move draws at most 4 sprites per frame (the engine copies 4);
    - set 0 tile $40 (rain) and $49 (orb) are drawn by engine effects; the falling-leaf
      effect draws tile $06 and the falling-petal effect tile $40 of the loaded set, so
      those moves load set 1 first;
    - the pic state effects are paired (slide off / squish / half off -> show pic, move
      horizontally -> reset position, palettes -> reset); the flying move's strike ends with
      show pic, the tunnel move's strike with slide up, and the blink move (also the flying
      move's charge turn) leaves the pic hidden;
    - no sequence ever holds more than 40 sprites.

Design frame: screen pixels, the player's turn (user bottom left, target top right).
Sequence types decide what the enemy's turn does: HFLIP (target effects: mirrored and moved
down 40 = exactly onto the player), ENEMY (user effects, drawn at the enemy and mirrored
onto the player on the player's turn), REVERSE (projectiles: the same path backwards),
HVFLIP (point mirror, tiles turned round: directional projectiles), NORMAL (fixed spots).
"""
import math
import os
import re
import sys
import zlib

T = (124, 30)        # target centre
TG = (124, 48)       # target's feet
TH = (124, 10)       # target's head
P = (36, 70)         # the user (player side) centre
S0 = (60, 62)        # projectile start, in front of the user
E0 = (110, 34)       # projectile end, in front of the target

NUM_FB = 122
NUM_BC = 177
SMALL_DISC_ID, LARGE_SPHERE_ID = 0x48, 0x49


# ------------------------------------------------------------------- shapes from tiles

def g(rows, anchor="c"):
    """rows of tokens: hex tile id with optional h (x flip) / v (y flip); '..' empty.
    Returns sprites (dx, dy, tile, flags) relative to the anchor (c centre, b bottom
    centre, bl bottom left)."""
    grid = [r.split() for r in rows]
    h, w = len(grid) * 8, max(len(r) for r in grid) * 8
    ax, ay = {"c": (w // 2, h // 2), "b": (w // 2, h), "bl": (0, h), "tl": (0, 0)}[anchor]
    out = []
    for y, row in enumerate(grid):
        for x, tok in enumerate(row):
            if tok == "..":
                continue
            m = re.fullmatch(r"([0-9A-Fa-f]{2})(h?)(v?)", tok)
            t, fl = int(m.group(1), 16), (1 if m.group(2) else 0) | (2 if m.group(3) else 0)
            out.append((x * 8 - ax, y * 8 - ay, t, fl))
    return out


def at(sprites, dx, dy):
    return [(x + dx, y + dy, t, f) for x, y, t, f in sprites]


def join(*parts):
    out = []
    for p in parts:
        out += p
    return out


def one(t, fl=0):
    return [(-4, -4, t, fl)]


def mirror(sprites):
    """the same shape seen in a mirror (x flip of every tile)"""
    return [(-x - 8, y, t, f ^ 1) for x, y, t, f in sprites]


def flipv(sprites):
    return [(x, -y - 8, t, f ^ 2) for x, y, t, f in sprites]


def ring_of(sprite, n, r, phase=0.0, ry=None):
    ry = r if ry is None else ry
    out = []
    for k in range(n):
        a = phase + 2 * math.pi * k / n
        out += at(sprite, round(r * math.cos(a)), round(ry * math.sin(a)))
    return out


SH = {}


def shape(name, sprites):
    SH[name] = sprites
    return name


# set 0 -------------------------------------------------------------------------------
shape("pow", g(["2C 2Ch", "2Cv 2Chv"]))                       # compact hit flash
shape("burst", g(["2C 2D 2Ch", "3C 3D 3Ch", "2Cv 2Dv 2Chv"]))   # full hit burst
shape("ring", g(["2E 2F 2Eh", "3E .. 3Eh", "2Ev 2Fv 2Ehv"]))    # ring (set 1: square)
shape("ringS", g(["2E 2Eh", "2Ev 2Ehv"]))                     # small ring
for d in (6, 12, 18, 26):
    shape(f"ring4_{d}", join(*(at(SH["ringS"], sx * d, sy * d) for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)))))
shape("puff", g(["20 21 21h 20h", "30 31 31h 30h", "30v 31v 31hv 30hv", "20v 21v 21hv 20hv"]))
shape("tight", g([".. 23 23h ..", "32 33 33h 32h", "32v 33v 33hv 32hv", ".. 23v 23hv .."]))
shape("smoke", g(["24 25 25h 24h", "34 .. .. 34h", "34v .. .. 34hv", "24v 25v 25hv 24hv"]))
shape("cluster", g(["20 20h", "20v 20hv"]))
shape("bird", g(["00 01", "10 11"]))
shape("birdL", mirror(SH["bird"]))
shape("heart", g(["08 09", "18 19"]))                           # set 1: music sign
shape("boulder", g(["0A 0B", "1A 1B"]))
shape("rocks2", join(at(SH["boulder"], -12, 4), at(SH["boulder"], 10, -6)))
shape("swirl", g(["2A 2B", "3A 3B"]))
shape("acorn", g(["02 02h", "12 12h"]))
shape("acornR", g(["06 07", "16 17"]))
shape("acornL", mirror(SH["acornR"]))
shape("egg", g(["48 48h", "12 12h"]))
shape("eggR", g(["4A 07", "16 17"]))
shape("eggL", mirror(SH["eggR"]))
shape("peak", g(["03 03h", "13 13h"]))
shape("peaks3", join(at(SH["peak"], -16, 6), SH["peak"], at(SH["peak"], 16, 2)))
shape("peakDown", flipv(SH["peak"]))
shape("crown", g(["04 04h", "14 14h"], "b"))
shape("crown2", g(["05 05h", "15 15h"], "b"))
for n in (1, 2, 3, 4):
    rows = [("41 41h" if k % 2 == 0 else "42 42h") for k in range(n)]
    shape(f"col{n}", g(rows, "b"))
    shape(f"geyser{n}", join(at(SH["crown" if n % 2 else "crown2"], 0, -8 * n), SH[f"col{n}"]))
shape("arcs", g(["0C 0D", "0Cv 0Dv"]))
shape("arcs2", join(at(SH["arcs"], -10, 0), at(one(0x0D), 10, -4), at(one(0x0D, 2), 10, 4)))
shape("poisonB", g(["0E 0Eh", "0F 0Fh"]))
shape("poison2", join(at(SH["poisonB"], -12, 6), at(SH["poisonB"], 12, -6)))
shape("silkcol", g(["1C 1D", "1C 1D", "1C 1D", "1C 1D"]))
for d in (8, 14, 22, 28):
    shape(f"bind{d}", join(at(SH["silkcol"], -d, 0), at(SH["silkcol"], d, 0)))
shape("silkseg", g(["26 27"]))
shape("horn", g(["1E 1F"]))
shape("bubble", g(["43 43h", "43v 43hv"]))
shape("bubbles", join(SH["bubble"], at(one(0x49), -14, 8), at(one(0x49), 12, -10)))
shape("beamseg", [(0, -8, 0x45, 0), (-8, 0, 0x46, 0)])
shape("beamend", g(["43 43h", "22 43hv"]))
shape("drop", g(["28 28h", "38 38h"]))
shape("dropcrown", g(["29 29h", "39 39h"], "b"))
shape("dropring", g(["36 36h", "36v 36hv"]))
for r in (10, 18, 26):
    shape(f"spray{r}", ring_of(one(0x37), 6, r, 0.3, r * 0.7))
shape("diamond", g(["35h 35", "35 35h"]))
shape("diamondsA", join(at(SH["diamond"], -18, -10), at(SH["diamond"], 16, 10)))
shape("diamondsB", join(at(SH["diamond"], 14, -14), at(SH["diamond"], -16, 12)))
shape("xslash", g(["44 44h", "44v 44hv"]))
for n in (1, 2, 3, 4):
    shape(f"stroke{n}", [(8 * i, -8 * (i + 1), 0x47, 0) for i in range(n)])      # up-right from anchor
    shape(f"strokeR{n}", [(8 * i, 8 * i - 8 * n, 0x47, 1) for i in range(n)])    # down-right to anchor row
shape("claws", join(at(SH["stroke3"], -14, 6), at(SH["stroke3"], -4, 10), at(SH["stroke3"], 6, 14)))
shape("coin", one(0x4B))
shape("coinE", one(0x4C))
shape("coins2", join(at(one(0x4B), -8, 0), at(one(0x4C), 8, -4)))
shape("coins2b", join(at(one(0x4C), -8, -4), at(one(0x4B), 8, 0)))
shape("pebble", one(0x4D))
shape("berry", one(0x4E))
shape("zz", join(one(0x3F), at(one(0x3F), 8, -8)))
shape("orb", one(0x49))
shape("dustA", [(-16, -6, 0x49, 0), (-4, -14, 0x49, 0), (6, -2, 0x49, 0), (14, -12, 0x49, 0), (-10, 6, 0x49, 0)])
shape("dustB", [(-14, -14, 0x49, 0), (-2, -4, 0x49, 0), (10, -14, 0x49, 0), (16, 2, 0x49, 0), (-18, 4, 0x49, 0)])
shape("splashpow", join(SH["pow"], at(one(0x37), -14, -10), at(one(0x37, 1), 10, -12)))

# set 1 -------------------------------------------------------------------------------
shape("sword", g(["00 01", "10 11"]))
shape("swordL", mirror(SH["sword"]))
shape("dorb", g(["02 02h", "12 12h"]))
shape("star", g(["03 03h", "13 13h"]))
shape("glint", one(0x46))
shape("flame", g(["04 04h", "14 14h"], "b"))
shape("flame2", g(["05 05h", "15 15h"], "b"))
shape("flames2", join(at(SH["flame"], -10, 0), at(SH["flame2"], 10, -4)))
shape("flamerow", join(at(SH["flame"], -18, 0), at(SH["flame2"], 0, -3), at(SH["flame"], 18, 0)))
shape("flamerow2", join(at(SH["flame2"], -18, -2), at(SH["flame"], 0, 0), at(SH["flame2"], 18, -2)))
shape("fpair", g(["41", "42"]))
shape("finner", ring_of(one(0x41), 6, 12))
shape("fouter", ring_of(at(SH["flame"], 0, 8), 5, 20, -math.pi / 2))
shape("fouter2", ring_of(at(SH["flame2"], 0, 8), 5, 22, -math.pi / 2 + math.pi / 5))
shape("leaf2", join(at(one(0x06), -6, -4), at(one(0x06, 3), 6, 4)))
shape("leaf2b", join(at(one(0x06, 1), -6, 4), at(one(0x06, 2), 6, -4)))
shape("sprout", g(["06h 06", "16 17"], "b"))
shape("cloud", g(["0A 0B", "1A 1B"]))
shape("clouds", join(at(SH["cloud"], -10, 2), at(SH["cloud"], 8, -6)))
shape("bolt", g(["0C 0D", "1C 1D", "1Dhv 1Chv", "0Dhv 0Chv"]))
shape("sparks", g(["0E 0F 0Fh 0Eh", "1E 1F 1Fh 1Eh"], "b"))
shape("sun", g(["20 21 21h 20h", "30 31 31h 30h", "30v 31v 31hv 30hv", "20v 21v 21hv 20hv"]))
shape("sand", g(["2C 3C 3C 2Ch", "2Cv 3Cv 3Cv 2Chv"]))
shape("sandL", g(["2C 3C 3C 2Ch", "2Dh 31 31 2D", "2Cv 3Cv 3Cv 2Chv"]))
shape("sphere", g(["22 23 23h 22h", "32 43 43h 32h", "32v 43v 43hv 32hv", "22v 23v 23hv 22hv"]))
shape("sphereShine", g(["22 3B 23h 22h", "32 43 43h 32h", "32v 43v 43hv 32hv", "22v 23v 23hv 22hv"]))
shape("disc", g(["33 33h", "33v 33hv"]))
shape("blast", g(["24 25 25h 24h", "34 .. .. 34h", "34v .. .. 34hv", "24v 25v 25hv 24hv"]))
shape("twister", g(["26 27", "36 37", "28 29", "38 39"]))
shape("shout", g(["2A 2B", "3A ..", "3Av ..", "2Av 2Bv"]))
shape("tri", g(["4D 2F 4Dh", "4E 07 4Eh", ".. 3F .."]))
shape("triInv", flipv(SH["tri"]))
shape("seeds", [(-10, -2, 0x3D, 0), (0, -8, 0x3D, 1), (6, 2, 0x3D, 0)])
shape("goo", g(["44 44h", "44v 44hv"]))
shape("splat", join(SH["goo"], at(one(0x45), -14, 6), at(one(0x45), 12, 8), at(one(0x45, 2), -4, -16)))
shape("drips", [(-14, -6, 0x45, 0), (-2, 4, 0x45, 0), (10, -2, 0x45, 0)])
shape("charge1", join(SH["disc"], at(one(0x4A), -14, -12), at(one(0x4C), 10, 6), at(one(0x4A, 3), 8, -14)))
shape("charge2", join(SH["disc"], at(one(0x4B), 12, -12), at(one(0x4B), -16, 4), at(one(0x4C, 1), -10, -14)))
shape("twinkles", [(-12, 2, 0x35, 0), (2, -10, 0x46, 0), (8, 6, 0x35, 1)])
shape("hexA", [(0, y, 0x48, 0) for y in (-16, -8)] + [(-8, -12, 0x47, 0)])
shape("hexB", [(0, y, 0x48, 0) for y in (0, 8)] + [(-8, 4, 0x48, 0), (-8, -4, 0x47, 0)])
shape("hexGlint", [(-4, -18, 0x46, 0), (-10, 2, 0x46, 0), (2, 10, 0x35, 0)])
shape("hexWall", join(SH["hexA"], SH["hexB"]))

# variety for the slots the sequences leave free: more of our arrangements
EXTRA = [
    ("orbs3", [(-10, 0, 0x49, 0), (0, -8, 0x49, 0), (8, 2, 0x49, 0)]),
    ("rainline", [(x, -x // 2, 0x40, 0) for x in range(-16, 17, 8)]),
    ("heartPair", join(at(SH["heart"], -10, 0), at(SH["heart"], 10, -8))),
    ("birdPair", join(at(SH["bird"], -12, 4), at(SH["birdL"], 12, -4))),
    ("swirl2", join(at(SH["swirl"], -10, 0), at(SH["swirl"], 12, -6))),
    ("acornRow", join(at(SH["acorn"], -12, 0), at(SH["acornR"], 12, 0))),
    ("drop2", join(at(SH["drop"], -10, 0), at(SH["drop"], 10, -6))),
    ("xslash2", join(at(SH["xslash"], -10, -4), at(SH["xslash"], 10, 6))),
    ("hornPair", join(at(SH["horn"], 0, -8), at(SH["horn"], -4, 6))),
    ("zz3", join(one(0x3F), at(one(0x3F), 8, -8), at(one(0x3F), 16, -14))),
    ("coins3", [(-12, 0, 0x4B, 0), (0, -10, 0x4C, 0), (10, 2, 0x4B, 0)]),
    ("bubblePair", join(at(SH["bubble"], -10, 4), at(SH["bubble"], 10, -6))),
    ("stars2", join(at(SH["star"], -10, 4), at(SH["star"], 10, -6))),
    ("swordsX", join(SH["sword"], SH["swordL"])),
    ("cloud3", join(at(SH["cloud"], -14, 4), at(SH["cloud"], 2, -6), at(SH["cloud"], 14, 6))),
    ("discs2", join(at(SH["disc"], -10, 4), at(SH["disc"], 10, -6))),
    ("hex3", [(-12, 0, 0x48, 0), (0, -6, 0x47, 0), (12, 0, 0x48, 0)]),
    ("leafRing", ring_of(one(0x06), 5, 14)),
    ("seedRow", [(x, 0, 0x3D, 0) for x in (-12, -4, 4)]),
    ("sparkle4", ring_of(one(0x4B), 4, 12, math.pi / 4)),
    ("dorb2", join(at(SH["dorb"], -10, 4), at(SH["dorb"], 10, -6))),
    ("tri2", join(at(SH["tri"], -12, 0), at(SH["triInv"], 12, 0))),
    ("gooPair", join(at(SH["goo"], -10, 0), at(SH["goo"], 10, -6))),
    ("musicPair", join(at(SH["heart"], -12, 4), at(SH["heart"], 12, -4))),
    ("peakPair", join(at(SH["peak"], -10, 0), at(SH["peak"], 10, -4))),
    ("arcs3", join(at(SH["arcs"], -12, 0), at(SH["arcs"], 4, 0))),
    ("pebbles", [(-8, 0, 0x4D, 0), (2, -6, 0x4D, 1), (8, 4, 0x4D, 2)]),
    ("berries", [(-6, 0, 0x4E, 0), (6, 0, 0x4E, 1)]),
    ("crackles", [(-8, -8, 0x4A, 0), (4, -8, 0x4C, 0), (-8, 4, 0x4C, 1), (4, 4, 0x4A, 3)]),
    ("squares3", [(-12, 0, 0x49, 0), (0, -10, 0x49, 0), (10, 4, 0x49, 0)]),
    ("ring2", join(at(SH["ringS"], -10, 4), at(SH["ringS"], 10, -6))),
    ("glints3", [(-12, 0, 0x46, 0), (0, -10, 0x46, 0), (10, 6, 0x46, 0)]),
    ("sproutPair", join(at(SH["sprout"], -10, 0), at(SH["sprout"], 10, 0))),
    ("flamePieces", [(-12, 0, 0x41, 0), (-4, -8, 0x42, 0), (4, 0, 0x41, 1), (12, -8, 0x42, 1)]),
    ("silk2", join(at(SH["silkseg"], -8, -6), at(SH["silkseg"], 8, 2))),
    ("dropringPair", join(at(SH["dropring"], -10, 0), at(SH["dropring"], 10, -6))),
    ("boulder3", join(at(SH["boulder"], -16, 4), at(SH["boulder"], 0, -6), at(SH["boulder"], 16, 4))),
    ("eggPair", join(at(SH["egg"], -10, 0), at(SH["eggR"], 10, 0))),
    ("powPair", join(at(SH["pow"], -12, 4), at(SH["pow"], 12, -4))),
]


# ------------------------------------------------------------------- paths

def lerp(a, b, n):
    if n == 1:
        return [b]
    return [(a[0] + (b[0] - a[0]) * i / (n - 1), a[1] + (b[1] - a[1]) * i / (n - 1)) for i in range(n)]


def arc(a, b, n, h):
    pts = lerp(a, b, n)
    return [(x, y - h * 4 * (i / (n - 1)) * (1 - i / (n - 1))) for i, (x, y) in enumerate(pts)]


def wave(a, b, n, amp, cycles=1.0):
    pts = lerp(a, b, n)
    return [(x, y + amp * math.sin(2 * math.pi * cycles * i / (n - 1))) for i, (x, y) in enumerate(pts)]


def orbit(c, rx, ry, n, a0=0.0, turns=1.0):
    return [(c[0] + rx * math.cos(a0 + 2 * math.pi * turns * k / n),
             c[1] + ry * math.sin(a0 + 2 * math.pi * turns * k / n)) for k in range(n)]


def off(c, dx, dy):
    return (c[0] + dx, c[1] + dy)


# ------------------------------------------------------------------- sequences

SUB = {}


def E(block, pt, mode=0):
    return (block, (round(pt[0]), round(pt[1])), mode)


def seq(blocks, pts, mode=0):
    if isinstance(blocks, str):
        blocks = [blocks]
    return [E(blocks[i % len(blocks)], p, mode) for i, p in enumerate(pts)]


def sub(name, typ, entries):
    SUB[name] = (typ, entries)


U = T  # user-centred effects are drawn at the enemy (type ENEMY)

sub("0_STAR", "HFLIP", [E("pow", off(T, -6, 2)), E("burst", off(T, -6, 2)), E("pow", off(T, -4, 0))])
sub("0_STAR_TWICE", "HFLIP", [E("pow", off(T, -14, -4)), E("burst", off(T, -14, -4)),
                              E("pow", off(T, 8, 8)), E("burst", off(T, 8, 8))])
sub("0_STAR_THRICE", "HFLIP", [E("pow", off(T, -12, 6), 3), E("pow", off(T, 4, -10), 3),
                               E("pow", off(T, 12, 10), 3), E("burst", off(T, 0, 2))])
sub("0_STAR_DESCENDING", "HFLIP", seq("pow", lerp(off(T, -10, -30), off(T, 0, 2), 4)) + [E("burst", off(T, 0, 4))])
sub("1_STAR_BIG_MOVING", "HFLIP", seq("sun", [off(T, -40, -18), off(T, -22, -8), T]) + [E("star", T)])
sub("1_STAR_BIG", "HFLIP", [E("glint", T), E("star", T), E("sun", T), E("star", off(T, 0, -2))])
for nm, h in (("HIGH", 54), ("MIDDLE", 38), ("LOW", 22)):
    pts = arc((26, 78), off(TG, 0, -4), 11, h)
    sub(f"0_BALL_TOSS_{nm}", "NORMAL", seq(["acorn", "acornR", "acorn", "acornL"], pts))
sub("0_BALL_SHAKE_ENEMY", "NORMAL", seq(["acorn", "acornR", "acorn", "acornL"], [off(TG, 0, -4)] * 4, 4))
sub("0_BALL_POOF_ENEMY", "HFLIP", seq(["cluster", "tight", "puff", "smoke", "smoke", "cluster"],
                                      [T, T, T, T, off(T, 0, -4), off(T, 0, -6)]))
sub("0_BALL_BLOCK", "NORMAL", [E("pow", (114, 40))] +
    seq(["acornL", "acorn", "acornR", "acorn", "acornL"], arc((110, 38), (58, 30), 5, 26)))
sub("1_FLAME_COLUMN_1", "HFLIP", seq(["flame", "flame2"], lerp(TG, off(TG, 0, -30), 5)))
sub("1_FLAME_COLUMN_2", "HFLIP", seq(["flames2", "flame2", "flames2"], lerp(TG, off(TG, 0, -24), 4)))
sub("1_FLAME_COLUMN_3", "HFLIP", seq(["flamerow", "flamerow2"], lerp(off(TG, 0, 6), off(TG, 0, -20), 4)))
sub("0_SCRATCHES", "HFLIP", [E("stroke3", off(T, -16, 10), 3), E("stroke3", off(T, -6, 14), 3),
                             E("stroke3", off(T, 4, 18), 0)])
sub("1_TORNADO", "HFLIP", seq("twister", wave(off(T, -26, 0), off(T, 22, 0), 6, 6, 1.5)))
sub("1_FLAMES", "HFLIP", [E("flame", off(T, -14, 18), 3), E("flame2", off(T, 10, 6), 3),
                          E("flame", off(T, -4, -2), 3), E("flame2", off(T, 16, 22), 3),
                          E("flame", off(T, 2, 14), 0)])
sub("0_HEART_1_MUSIC", "REVERSE", seq("heart", wave(S0, E0, 8, 8, 1.0)))
sub("1_BLOB_TOSS", "REVERSE", seq("goo", arc(S0, E0, 6, 24)) + [E("splat", T)])
sub("1_BLOB_DRIP_ENEMY", "HFLIP", seq("drips", lerp(off(T, 0, -26), off(T, 0, 18), 6)))
sub("1_SHOUT", "ENEMY", seq("shout", [off(U, -28, -4), off(U, -34, -4), off(U, -28, -4), off(U, -36, -4)]))
sub("0_SLICE", "HFLIP", [E(f"stroke{n}", off(T, -16, 16)) for n in (1, 2, 3, 4)] + [E("xslash", T)])
_b = orbit(TH, 18, 6, 8, 0)
sub("0_BIRDIES_CIRCLING_ENEMY", "HFLIP", [E("birdL" if math.sin(2 * math.pi * k / 8) >= 0 else "bird", p)
                                          for k, p in enumerate(_b)])
sub("1_SWORDS_CIRCLING", "ENEMY", seq("sword", orbit(U, 24, 14, 6, math.pi / 2), 3)[:-1] +
    [E("swordL", off(U, 0, -16), 0)])
sub("1_CLOUD_TOSS", "REVERSE", seq(["cloud", "clouds"], wave(S0, E0, 6, 5, 0.5)) + [E("clouds", T)])
sub("0_WATER_COLUMNS", "HFLIP", [E("geyser1", off(TG, -14, 8)), E("geyser2", off(TG, -14, 8)),
                                 E("geyser3", off(TG, -14, 8), 3), E("geyser1", off(TG, 14, 4), 4),
                                 E("geyser2", off(TG, 14, 4), 4), E("geyser3", off(TG, 14, 4))])
sub("1_SEED_TOSS", "REVERSE", seq("seeds", arc(S0, E0, 6, 30)))
sub("1_SEED_LAND", "HFLIP", [E("seeds", off(T, 0, 10)), E("sprout", off(TG, -14, 6), 3),
                             E("sprout", off(TG, 12, 2), 3), E("sprout", off(TG, 0, 10))])
sub("0_ROCKS_LIFT", "ENEMY", seq("rocks2", lerp(off(U, 0, 22), off(U, 0, -18), 5)))
sub("0_ROCKS_TOSS", "HVFLIP", seq("boulder", arc(S0, E0, 5, 30)) + [E("pow", T)])
sub("1_FLAME_BEAM", "REVERSE", seq("fpair", lerp(S0, E0, 8), 3) + [E("flame", off(T, 0, 12))])
sub("1_FLAME_STAR", "HFLIP", seq(["finner", "fouter", "fouter2", "finner"], [T] * 4))
sub("0_CIRCLES_1_SQUARES_CENTERING_ENEMY", "HFLIP", seq(["ring4_26", "ring4_18", "ring4_12", "ring4_6", "ring"], [T] * 5))
sub("0_CIRCLE_1_SQUARE_TOSS_BACK", "REVERSE", seq("ringS", lerp(off(T, -6, 2), off(P, 8, -6), 6)) +
    [E("ring", off(P, 4, -4))])
sub("0_BIND", "HFLIP", seq(["bind28", "bind22", "bind14", "bind8", "bind14", "bind8"], [T] * 6))
sub("0_STATUS_PARALYZED", "ENEMY", seq(["diamondsA", "diamondsB"], [U, U, off(U, 2, 0), U]))
sub("0_STATUS_CONFUSED", "NORMAL", seq("swirl", [(30, 44), (36, 41), (42, 44)]))
sub("0_STATUS_CONFUSED_ENEMY", "NORMAL", seq("swirl", [(118, 12), (124, 9), (130, 12)]))
sub("0_STATUS_POISONED", "ENEMY", seq("poison2", lerp(off(U, 0, 18), off(U, 0, -12), 4)))
sub("1_SAND", "REVERSE", seq(["sand", "sand", "sandL", "sandL", "sandL"], lerp(S0, off(T, -6, 0), 5)))
sub("1_LIGHTNING_BALL", "HFLIP", seq(["charge1", "charge2"], [T] * 4))
sub("0_SLICE_BOTH_SIDES", "HFLIP", [E("stroke4", off(T, -16, 16), 3), E("strokeR4", off(T, -16, 16), 0),
                                    E("xslash", T)])
sub("1_LIGHTNING", "HFLIP", [E("bolt", off(T, 0, -26)), E("bolt", off(T, 0, -6), 3), E("sparks", off(T, 0, 26))])
sub("0_WATER_DROPLETS", "HFLIP", [E("dropcrown", off(T, 0, 14)), E("spray10", T), E("spray18", T), E("spray26", T)])
sub("0_CIRCLES_CENTERING", "ENEMY", seq(["ring4_26", "ring4_18", "ring4_12", "ringS", "ring"], [U] * 5))
sub("0_BEAM", "HVFLIP", seq("beamseg", [(64, 82), (80, 66), (96, 50), (112, 34)], 3) + [E("beamend", (124, 22))])
sub("0_ICE_RISE", "HFLIP", seq("peaks3", lerp(off(T, 0, 26), off(T, 0, -2), 4)) + [E("xslash", T)])
_rk = []
for x0, dx in ((-14, 4), (12, -4), (0, 2)):
    _rk += seq("boulder", lerp(off(T, x0, -34), off(T, x0 + dx, 10), 4))
sub("0_ROCKS_FALL_ENEMY", "HFLIP", _rk + [E("rocks2", off(T, 0, 16))])
sub("0_SOUND_WAVE", "HVFLIP", seq("arcs", lerp(S0, E0, 6)))
sub("0_CIRCLE_1_SQUARE_HALF_TOSS", "HVFLIP", seq("horn", lerp(S0, E0, 5)) + [E("pow", off(T, -6, 2))])
sub("1_BARRIER", "ENEMY", [E("hexA", off(U, -30, 0), 3), E("hexB", off(U, -30, 0), 3),
                           E("hexGlint", off(U, -30, 0), 0), E("hexWall", off(U, -30, 0), 0)])
sub("1_SELFDESTRUCT", "ENEMY", seq(["star", "sun", "blast", "sun", "blast", "sun", "blast", "star"],
                                   [U, U, off(U, -8, -6), off(U, 6, 6), off(U, 8, -8), U, off(U, -6, 8), U]))
sub("0_WATER_BUBBLES", "REVERSE", seq("bubbles", wave(S0, E0, 6, 7, 1.0)))
sub("0_CIRCLES_FALLING", "HFLIP", seq(["dustA", "dustB"], lerp(off(T, 0, -26), off(T, 0, 12), 5)))
sub("0_STRING_SHOT", "HVFLIP", seq("silkseg", [(62, 66), (78, 58), (94, 50), (110, 42)], 3) + [E("bind8", T)])
_ic = []
for x0 in (-16, 14, 0):
    _ic += seq("peakDown", lerp(off(T, x0, -36), off(T, x0, 6), 4))
sub("0_ICE_FALL", "HFLIP", _ic + [E("burst", off(T, 0, 8))])
sub("0_CIRCLE_1_SQUARE_APPEARS", "HFLIP", seq(["ringS", "ring", "ring4_12", "ring4_18", "ring"], [T] * 5))
sub("0_STATUS_SLEEP", "NORMAL", seq("zz", [(46, 44), (52, 36), (58, 28)]))
sub("0_STATUS_SLEEP_ENEMY", "NORMAL", seq("zz", [(110, 22), (104, 16), (98, 12)]))
sub("0_WATER_1_FIRE_BARRIER", "ENEMY", seq(["fringA", "fringB"], [U] * 4))
sub("0_WATER_1_FIRE_GEYSER", "HFLIP", seq(["col1", "col2", "col3", "geyser4", "geyser3"], [off(TG, 0, 6)] * 5))
sub("1_STAR_BIG_TOSS", "REVERSE", seq("sun", lerp(S0, off(T, -4, 0), 5)))
sub("1_STARS_SMALL_TOSS", "REVERSE", seq("twinkles", wave(S0, E0, 6, 6, 1.5)))
sub("1_MUSIC_CIRCLING_ENEMY", "HFLIP", seq("heart", orbit(off(TH, 0, 2), 20, 7, 8, math.pi)))
sub("1_CIRCLE_BLACK_TOSS", "REVERSE", seq("dorb", wave(S0, off(T, -4, 0), 6, 9, 1.0)))
sub("1_EXPLOSION_SMALL_ENEMY", "HFLIP", [E("blast", off(T, -10, -6)), E("blast", off(T, 10, 8)), E("sun", T)])
sub("0_CIRCLE_1_SQUARE_CLOSING", "HFLIP", seq(["ring4_26", "ring4_18", "ring4_6", "ring", "ringS"], [T] * 5))
sub("1_LEAVES_TOSS", "REVERSE", seq(["leaf2", "leaf2b"], wave(S0, E0, 7, 10, 2.0)))
sub("0_HORN_JAB_TWICE", "HFLIP", seq("horn", [off(T, -36, 2), off(T, -22, 2), off(T, -36, 2), off(T, -20, 4)]) +
    [E("pow", off(T, -6, 4))])
sub("0_HORN_JAB_THRICE", "HFLIP", seq("horn", [off(T, -34, -8), off(T, -20, -8), off(T, -34, 8),
                                               off(T, -20, 8), off(T, -34, 0), off(T, -18, 0)]) +
    [E("pow", off(T, -6, 0))])
sub("0_BALL_POOF", "ENEMY", seq(["cluster", "tight", "smoke", "puff", "cluster"], [U, U, U, off(U, 0, -2), off(U, 0, -6)]))
TR = (84, 44)
sub("2_TRADE_BALL_DROP", "NORMAL", seq(["acorn", "acorn", "acorn", "acorn", "acornR", "acorn", "acornL", "acorn"],
                                       [off(TR, 0, -6), off(TR, 0, -9), off(TR, 0, -6), off(TR, 0, 2),
                                        off(TR, 0, 12), off(TR, 0, 22), off(TR, 0, 30), off(TR, 0, 36)], 4))
sub("2_TRADE_BALL_SHAKE", "NORMAL", seq(["acornR", "acorn", "acornL", "acorn"], [(96, 56)] * 4, 4))
sub("2_TRADE_BALL_APPEAR", "NORMAL", [E("acorn", (84, 20), 3)])
sub("2_TRADE_BALL_POOF", "NORMAL", seq(["cluster", "tight", "puff", "smoke", "cluster"],
                                       [TR, TR, TR, off(TR, 0, -2), off(TR, 0, -6)]))
sub("0_EGG_SHAKING", "ENEMY", seq(["egg", "eggR", "egg", "eggL", "egg"],
                                  [off(U, 0, 8), off(U, 2, 8), off(U, 0, 8), off(U, -2, 8), off(U, 0, 6)]))
sub("1_TRIANGLE_TOSS", "REVERSE", seq(["tri", "triInv"], lerp(S0, off(T, -4, 0), 6)))
sub("1_SPHERE_BIG", "HFLIP", seq(["disc", "sphere", "sphereShine", "sphere"], [T] * 4))
sub("1_SPHERE_BIG_RISE", "ENEMY", seq("sphere", lerp(U, off(U, 0, -66), 4)))
sub("1_SPHERE_BIG_FALL", "HFLIP", seq("sphere", lerp(off(T, 0, -58), T, 4)) + [E("sphereShine", T)])
sub("0_SHELL", "ENEMY", seq(["ring4_18", "ring", "ringS", "ring"], [U] * 4))
sub("0_COIN_BOUNCE", "HFLIP", seq(["coins2", "coins2b"], [off(T, 0, 0), off(T, 0, -12), off(T, 0, -18),
                                                       off(T, 0, -14), off(T, 0, -4), off(T, 0, 10)]))
sub("0_SAFARI_ROCK", "NORMAL", seq("pebble", arc((40, 64), (120, 28), 7, 26)) + [E("pow", (122, 26))])
sub("0_SAFARI_BAIT", "NORMAL", seq("berry", arc((40, 64), (112, 52), 7, 30)) + [E("berry", (112, 54))])
sub("0_STAR_HIGH", "HFLIP", [E("pow", off(T, 4, -12)), E("burst", off(T, 4, -12)), E("pow", off(T, 4, -14))])

shape("fringA", ring_of(one(0x41), 8, 24, 0, 16))
shape("fringB", ring_of(one(0x42), 8, 24, math.pi / 8, 16))


# ------------------------------------------------------------------- move scripts
# (sound move or None, subanimation suffix, tileset, delay) or (sound move or None, "SE_...")

def s(snd, sa, ts, d):
    return (snd, sa, ts, d)


def e(snd, se):
    return (snd, se)


MV = {
    "POUND": [s(1, "0_STAR_HIGH", 0, 5)],
    "KARATE_CHOP": [s(1, "0_SLICE", 0, 3), s(None, "0_STAR", 0, 4)],
    "DOUBLESLAP": [s(1, "0_STAR_TWICE", 0, 4)],
    "COMET_PUNCH": [s(1, "0_STAR_THRICE", 0, 3), s(1, "0_STAR_THRICE", 0, 2)],
    "MEGA_PUNCH": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "1_STAR_BIG", 1, 6)],
    "PAY_DAY": [s("POUND", "0_STAR", 0, 5), s(1, "0_COIN_BOUNCE", 0, 4)],
    "FIRE_PUNCH": [s(1, "0_STAR_HIGH", 0, 4), s("EMBER", "1_FLAMES", 1, 4)],
    "ICE_PUNCH": [s(1, "0_STAR", 0, 4), s("ICE_BEAM", "0_ICE_RISE", 0, 3)],
    "THUNDERPUNCH": [s(1, "0_STAR", 0, 4), e(None, "SE_DARK_SCREEN_PALETTE"), s("THUNDERSHOCK", "1_LIGHTNING_BALL", 1, 4),
                     e(None, "SE_RESET_SCREEN_PALETTE")],
    "SCRATCH": [s(1, "0_SCRATCHES", 0, 5)],
    "VICEGRIP": [s(1, "0_SLICE_BOTH_SIDES", 0, 4)],
    "GUILLOTINE": [e(None, "SE_DARK_SCREEN_FLASH"), s(1, "0_SLICE_BOTH_SIDES", 0, 3)],
    "RAZOR_WIND": [s(1, "1_TORNADO", 1, 3), s("CUT", "0_SLICE", 0, 3)],
    "SWORDS_DANCE": [s(1, "1_SWORDS_CIRCLING", 1, 4), s(1, "1_SWORDS_CIRCLING", 1, 3)],
    "CUT": [e(None, "SE_DARK_SCREEN_FLASH"), s(1, "0_SLICE", 0, 4)],
    "GUST": [s(1, "1_CLOUD_TOSS", 1, 4)],
    "WING_ATTACK": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "0_STAR_TWICE", 0, 4)],
    "WHIRLWIND": [s(1, "1_TORNADO", 1, 4), e(None, "SE_SLIDE_ENEMY_MON_OFF")],
    "FLY": [s(1, "1_STARS_SMALL_TOSS", 1, 3), s("PECK", "1_STAR_BIG", 1, 4), e(None, "SE_SHOW_MON_PIC")],
    "BIND": [s(1, "0_BIND", 0, 5)],
    "SLAM": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "0_STAR_DESCENDING", 0, 4)],
    "VINE_WHIP": [s(1, "0_SLICE", 0, 2), s(None, "0_STAR", 0, 3)],
    "STOMP": [s(1, "0_STAR_DESCENDING", 0, 4), e(None, "SE_SHAKE_SCREEN")],
    "DOUBLE_KICK": [s(1, "0_STAR_TWICE", 0, 3)],
    "MEGA_KICK": [s(1, "1_STAR_BIG_MOVING", 1, 5)],
    "JUMP_KICK": [e(1, "SE_SLIDE_MON_OFF"), s(None, "0_STAR_HIGH", 0, 5), e(None, "SE_SHOW_MON_PIC")],
    "ROLLING_KICK": [e(None, "SE_SHAKE_BACK_AND_FORTH"), s(1, "0_STAR_THRICE", 0, 3)],
    "SAND_ATTACK": [s(1, "1_SAND", 1, 4)],
    "HEADBUTT": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "0_STAR", 0, 6)],
    "HORN_ATTACK": [s(1, "0_HORN_JAB_TWICE", 0, 4)],
    "FURY_ATTACK": [s(1, "0_HORN_JAB_THRICE", 0, 3)],
    "HORN_DRILL": [s(1, "0_HORN_JAB_THRICE", 0, 2), s(1, "0_HORN_JAB_THRICE", 0, 2), e(None, "SE_DARK_SCREEN_FLASH")],
    "TACKLE": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "0_STAR", 0, 3)],
    "BODY_SLAM": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"),
                  s(1, "0_STAR_DESCENDING", 0, 4), e(None, "SE_SHAKE_SCREEN")],
    "WRAP": [s(1, "0_BIND", 0, 4), s(1, "0_BIND", 0, 3)],
    "TAKE_DOWN": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_DARK_SCREEN_FLASH"), e(None, "SE_RESET_MON_POSITION"),
                  s(1, "0_STAR_TWICE", 0, 4)],
    "THRASH": [s(1, "0_STAR_THRICE", 0, 3), e(None, "SE_SHAKE_SCREEN"), s(1, "0_STAR_TWICE", 0, 3)],
    "DOUBLE_EDGE": [e(None, "SE_LIGHT_SCREEN_PALETTE"), e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"),
                    e(None, "SE_RESET_SCREEN_PALETTE"), s(1, "1_STAR_BIG", 1, 5)],
    "TAIL_WHIP": [e(1, "SE_SHAKE_BACK_AND_FORTH"), e(None, "SE_DELAY_ANIMATION_10")],
    "POISON_STING": [s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 2)],
    "TWINEEDLE": [s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 2), s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 2)],
    "PIN_MISSILE": [s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 1), s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 1),
                    s(None, "0_STAR_THRICE", 0, 3)],
    "LEER": [e(None, "SE_DARKEN_MON_PALETTE"), s(1, "1_TRIANGLE_TOSS", 1, 3), e(None, "SE_RESET_SCREEN_PALETTE")],
    "BITE": [s(1, "0_SLICE_BOTH_SIDES", 0, 3), s(None, "0_STAR", 0, 3)],
    "GROWL": [s(1, "0_SOUND_WAVE", 0, 5), s(None, "0_SOUND_WAVE", 0, 4)],
    "ROAR": [s(1, "1_SHOUT", 1, 4), s(None, "1_SHOUT", 1, 3), s(None, "0_SOUND_WAVE", 0, 3)],
    "SING": [s(1, "0_HEART_1_MUSIC", 1, 6), s(None, "1_MUSIC_CIRCLING_ENEMY", 1, 5)],
    "SUPERSONIC": [s(1, "0_SOUND_WAVE", 0, 3), s(None, "0_SOUND_WAVE", 0, 2), s(None, "0_SOUND_WAVE", 0, 2)],
    "SONICBOOM": [s(1, "0_SOUND_WAVE", 0, 2), e(None, "SE_DARK_SCREEN_FLASH"), s(None, "0_STAR", 0, 3)],
    "DISABLE": [s(1, "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", 1, 4)],
    "ACID": [s(1, "1_BLOB_TOSS", 1, 3), s(None, "1_BLOB_DRIP_ENEMY", 1, 4)],
    "EMBER": [s(1, "1_FLAME_COLUMN_1", 1, 4)],
    "FLAMETHROWER": [s(1, "1_FLAME_BEAM", 1, 2), s(1, "1_FLAMES", 1, 4)],
    "MIST": [s(1, "0_WATER_1_FIRE_BARRIER", 0, 4), e(None, "SE_LIGHT_SCREEN_PALETTE"),
             e(None, "SE_WATER_DROPLETS_EVERYWHERE"), e(None, "SE_RESET_SCREEN_PALETTE")],
    "WATER_GUN": [s(1, "0_BEAM", 0, 2), s(None, "0_WATER_DROPLETS", 0, 3)],
    "HYDRO_PUMP": [s(1, "0_WATER_COLUMNS", 0, 3), s(1, "0_WATER_COLUMNS", 0, 3), e(None, "SE_SHAKE_SCREEN")],
    "SURF": [e(1, "SE_WATER_DROPLETS_EVERYWHERE"), s(None, "0_WATER_1_FIRE_GEYSER", 0, 3)],
    "ICE_BEAM": [s(1, "0_BEAM", 0, 2), s(None, "0_ICE_RISE", 0, 3)],
    "BLIZZARD": [s(1, "0_ICE_FALL", 0, 2), s(None, "0_ICE_RISE", 0, 3)],
    "PSYBEAM": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "0_CIRCLE_1_SQUARE_APPEARS", 1, 3), e(None, "SE_WAVY_SCREEN"),
                e(None, "SE_RESET_SCREEN_PALETTE")],
    "BUBBLEBEAM": [s(1, "0_WATER_BUBBLES", 0, 3)],
    "AURORA_BEAM": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_BEAM", 0, 2), s(None, "0_CIRCLES_FALLING", 0, 3),
                    e(None, "SE_RESET_SCREEN_PALETTE")],
    "HYPER_BEAM": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "0_BEAM", 0, 2), s(1, "1_EXPLOSION_SMALL_ENEMY", 1, 3),
                   e(None, "SE_RESET_SCREEN_PALETTE")],
    "PECK": [s(1, "0_STAR_THRICE", 0, 2)],
    "DRILL_PECK": [s(1, "0_HORN_JAB_THRICE", 0, 2), s(None, "0_STAR_HIGH", 0, 3)],
    "SUBMISSION": [e(1, "SE_SLIDE_MON_OFF"), s(None, "1_STAR_BIG_MOVING", 1, 4), e(None, "SE_SHAKE_SCREEN"),
                   e(None, "SE_SHOW_MON_PIC")],
    "LOW_KICK": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "0_STAR_TWICE", 0, 3)],
    "COUNTER": [s(1, "0_STAR", 0, 3), s(None, "0_STAR_HIGH", 0, 3), e(None, "SE_DARK_SCREEN_FLASH")],
    "SEISMIC_TOSS": [e(None, "SE_SLIDE_MON_OFF"), s(1, "1_SPHERE_BIG_FALL", 1, 2), e(None, "SE_SHAKE_SCREEN"),
                     e(None, "SE_SHOW_MON_PIC")],
    "STRENGTH": [s(1, "0_ROCKS_LIFT", 0, 4), s(None, "0_ROCKS_TOSS", 0, 3)],
    "ABSORB": [s(1, "0_CIRCLE_1_SQUARE_TOSS_BACK", 0, 3), e(None, "SE_BLINK_MON")],
    "MEGA_DRAIN": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "0_CIRCLE_1_SQUARE_TOSS_BACK", 0, 3),
                   s(None, "0_CIRCLE_1_SQUARE_TOSS_BACK", 0, 2), e(None, "SE_RESET_SCREEN_PALETTE"), e(None, "SE_BLINK_MON")],
    "LEECH_SEED": [s(1, "1_SEED_TOSS", 1, 3), s(None, "1_SEED_LAND", 1, 6)],
    "GROWTH": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_CIRCLES_CENTERING", 0, 3), e(None, "SE_RESET_SCREEN_PALETTE")],
    "RAZOR_LEAF": [s(1, "1_LEAVES_TOSS", 1, 2), e(None, "SE_LEAVES_FALLING"), s(None, "0_SLICE", 0, 2)],
    "SOLARBEAM": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "1_STAR_BIG_TOSS", 1, 3), s(None, "1_STAR_BIG", 1, 4),
                  e(None, "SE_RESET_SCREEN_PALETTE")],
    "POISONPOWDER": [e(None, "SE_DARKEN_MON_PALETTE"), s(1, "0_CIRCLES_FALLING", 0, 4), e(None, "SE_RESET_SCREEN_PALETTE")],
    "STUN_SPORE": [s(1, "0_CIRCLES_FALLING", 1, 4), s(None, "1_LIGHTNING_BALL", 1, 3)],
    "SLEEP_POWDER": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_CIRCLES_FALLING", 0, 6), e(None, "SE_RESET_SCREEN_PALETTE")],
    "PETAL_DANCE": [s(1, "1_TORNADO", 1, 3), e(None, "SE_PETALS_FALLING")],
    "STRING_SHOT": [s(1, "0_STRING_SHOT", 0, 2), s(None, "0_BIND", 0, 4)],
    "DRAGON_RAGE": [s(1, "1_FLAME_BEAM", 1, 2), s(None, "1_FLAME_STAR", 1, 3)],
    "FIRE_SPIN": [s(1, "1_FLAME_STAR", 1, 3), s(1, "1_FLAME_STAR", 1, 2)],
    "THUNDERSHOCK": [s(1, "1_LIGHTNING_BALL", 1, 3)],
    "THUNDERBOLT": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "1_LIGHTNING", 1, 3), s(None, "1_LIGHTNING_BALL", 1, 3),
                    e(None, "SE_RESET_SCREEN_PALETTE")],
    "THUNDER_WAVE": [s(1, "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", 1, 3), s(None, "1_LIGHTNING_BALL", 1, 3)],
    "THUNDER": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "1_LIGHTNING", 1, 2), s(1, "1_LIGHTNING", 1, 2),
                e(None, "SE_DARK_SCREEN_FLASH"), e(None, "SE_RESET_SCREEN_PALETTE")],
    "ROCK_THROW": [s(1, "0_ROCKS_TOSS", 0, 3)],
    "EARTHQUAKE": [e(1, "SE_SHAKE_SCREEN"), e(None, "SE_SHAKE_SCREEN")],
    "FISSURE": [e(None, "SE_DARK_SCREEN_FLASH"), e(1, "SE_SHAKE_SCREEN"), s(None, "0_ROCKS_FALL_ENEMY", 0, 2),
                e(None, "SE_SHAKE_SCREEN")],
    "DIG": [s(1, "0_ROCKS_TOSS", 0, 3), e(None, "SE_SLIDE_MON_UP")],
    "TOXIC": [s(1, "1_BLOB_DRIP_ENEMY", 1, 4), e(None, "SE_DARKEN_MON_PALETTE"), s(None, "1_BLOB_DRIP_ENEMY", 1, 3),
              e(None, "SE_RESET_SCREEN_PALETTE")],
    "CONFUSION": [e(1, "SE_WAVY_SCREEN"), s(None, "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", 0, 3)],
    "PSYCHIC_M": [e(1, "SE_FLASH_SCREEN_LONG"), e(None, "SE_WAVY_SCREEN"), s(None, "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", 1, 3)],
    "HYPNOSIS": [s(1, "0_CIRCLE_1_SQUARE_APPEARS", 0, 6), s(1, "0_CIRCLE_1_SQUARE_APPEARS", 0, 5)],
    "MEDITATE": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_CIRCLES_CENTERING", 0, 4), e(None, "SE_RESET_SCREEN_PALETTE")],
    "AGILITY": [e(1, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), e(1, "SE_MOVE_MON_HORIZONTALLY"),
                e(None, "SE_RESET_MON_POSITION")],
    "QUICK_ATTACK": [e(1, "SE_SLIDE_MON_OFF"), s(None, "0_STAR", 0, 2), e(None, "SE_SHOW_MON_PIC")],
    "RAGE": [s(1, "1_SHOUT", 1, 3), s(None, "0_STAR_TWICE", 0, 3)],
    "TELEPORT": [e(1, "SE_SQUISH_MON_PIC"), e(None, "SE_SHOOT_MANY_BALLS_UPWARD")],
    "NIGHT_SHADE": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "1_SPHERE_BIG", 1, 4), e(None, "SE_WAVY_SCREEN"),
                    e(None, "SE_RESET_SCREEN_PALETTE")],
    "MIMIC": [s(1, "0_CIRCLE_1_SQUARE_TOSS_BACK", 1, 4), e(None, "SE_BLINK_MON")],
    "SCREECH": [s(1, "0_SOUND_WAVE", 0, 2), s(None, "0_SOUND_WAVE", 0, 2), e(None, "SE_SHAKE_SCREEN")],
    "DOUBLE_TEAM": [e(1, "SE_SHAKE_BACK_AND_FORTH"), e(None, "SE_BLINK_MON")],
    "RECOVER": [e(None, "SE_LIGHT_SCREEN_PALETTE"), e(1, "SE_BLINK_MON"), s(None, "0_CIRCLES_CENTERING", 1, 3),
                e(None, "SE_RESET_SCREEN_PALETTE")],
    "HARDEN": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_SHELL", 0, 4), e(None, "SE_RESET_SCREEN_PALETTE")],
    "MINIMIZE": [e(1, "SE_LIGHT_SCREEN_PALETTE"), e(None, "SE_SPIRAL_BALLS_INWARD"), e(None, "SE_MINIMIZE_MON"),
                 e(None, "SE_RESET_SCREEN_PALETTE")],
    "SMOKESCREEN": [s(1, "1_CLOUD_TOSS", 1, 3), e(None, "SE_DARKEN_MON_PALETTE"), e(None, "SE_DELAY_ANIMATION_10"),
                    e(None, "SE_RESET_SCREEN_PALETTE")],
    "CONFUSE_RAY": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "1_CIRCLE_BLACK_TOSS", 1, 3),
                    s(None, "0_BIRDIES_CIRCLING_ENEMY", 0, 4), e(None, "SE_RESET_SCREEN_PALETTE")],
    "WITHDRAW": [e(1, "SE_SLIDE_MON_DOWN"), s(None, "0_SHELL", 0, 4), e(None, "SE_SLIDE_MON_UP")],
    "DEFENSE_CURL": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_SHELL", 0, 3), e(None, "SE_RESET_SCREEN_PALETTE")],
    "BARRIER": [s(1, "1_BARRIER", 1, 3)],
    "LIGHT_SCREEN": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "1_BARRIER", 1, 2), e(None, "SE_RESET_SCREEN_PALETTE")],
    "HAZE": [e(None, "SE_LIGHT_SCREEN_PALETTE"), e(1, "SE_WATER_DROPLETS_EVERYWHERE"), e(None, "SE_RESET_SCREEN_PALETTE")],
    "REFLECT": [s(1, "0_SHELL", 1, 4)],
    "FOCUS_ENERGY": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "0_CIRCLES_CENTERING", 0, 3), e(None, "SE_SPIRAL_BALLS_INWARD"),
                     e(None, "SE_RESET_SCREEN_PALETTE")],
    "BIDE": [e(None, "SE_DARKEN_MON_PALETTE"), s(1, "0_SHELL", 0, 5), e(None, "SE_RESET_SCREEN_PALETTE")],
    "METRONOME": [s(1, "1_STARS_SMALL_TOSS", 1, 4), e(None, "SE_BLINK_MON")],
    "MIRROR_MOVE": [e(None, "SE_BLINK_MON"), s(1, "0_CIRCLE_1_SQUARE_TOSS_BACK", 1, 3)],
    "SELFDESTRUCT": [s(1, "1_SELFDESTRUCT", 1, 3), e(None, "SE_SHAKE_SCREEN")],
    "EGG_BOMB": [s(1, "0_ROCKS_TOSS", 0, 3), s(None, "1_EXPLOSION_SMALL_ENEMY", 1, 4)],
    "LICK": [s(1, "1_BLOB_DRIP_ENEMY", 1, 3)],
    "SMOG": [s(1, "1_CLOUD_TOSS", 1, 3), e(None, "SE_DARKEN_MON_PALETTE"), s(None, "0_BALL_POOF_ENEMY", 0, 4),
             e(None, "SE_RESET_SCREEN_PALETTE")],
    "SLUDGE": [s(1, "1_BLOB_TOSS", 1, 3), s(None, "1_BLOB_DRIP_ENEMY", 1, 3)],
    "BONE_CLUB": [s(1, "0_STAR_DESCENDING", 0, 4), s(None, "0_STAR", 0, 3)],
    "FIRE_BLAST": [s(1, "1_FLAME_BEAM", 1, 2), s(None, "1_FLAME_STAR", 1, 3), s(1, "1_FLAMES", 1, 3)],
    "WATERFALL": [s(1, "0_WATER_1_FIRE_GEYSER", 0, 3), s(None, "0_WATER_COLUMNS", 0, 3)],
    "CLAMP": [s(1, "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", 0, 3), s(None, "0_SLICE_BOTH_SIDES", 0, 3)],
    "SWIFT": [s(1, "1_STARS_SMALL_TOSS", 1, 2), s(None, "1_STAR_BIG", 1, 3)],
    "SKULL_BASH": [e(None, "SE_MOVE_MON_HORIZONTALLY"), e(None, "SE_RESET_MON_POSITION"), s(1, "1_STAR_BIG_MOVING", 1, 4),
                   e(None, "SE_SHAKE_SCREEN")],
    "SPIKE_CANNON": [s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 1), s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 1),
                     s(None, "0_STAR_THRICE", 0, 2)],
    "CONSTRICT": [s(1, "0_BIND", 0, 3)],
    "AMNESIA": [s(1, "0_STATUS_CONFUSED", 0, 6), s(None, "0_STATUS_CONFUSED", 0, 6)],
    "KINESIS": [s(1, "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", 1, 4), e(None, "SE_FLASH_SCREEN_LONG")],
    "SOFTBOILED": [e(None, "SE_SLIDE_MON_HALF_OFF"), s(1, "0_EGG_SHAKING", 0, 5), e(None, "SE_SHOW_MON_PIC"),
                   e(None, "SE_BLINK_MON")],
    "HI_JUMP_KICK": [e(1, "SE_SLIDE_MON_OFF"), s(None, "1_STAR_BIG_MOVING", 1, 3), e(None, "SE_SHOW_MON_PIC")],
    "GLARE": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "1_TRIANGLE_TOSS", 1, 4), e(None, "SE_DARK_SCREEN_FLASH"),
              e(None, "SE_RESET_SCREEN_PALETTE")],
    "DREAM_EATER": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "0_CIRCLE_1_SQUARE_TOSS_BACK", 0, 4), e(None, "SE_BLINK_MON"),
                    e(None, "SE_RESET_SCREEN_PALETTE")],
    "POISON_GAS": [s(1, "1_CLOUD_TOSS", 1, 4), e(None, "SE_DARKEN_MON_PALETTE"), e(None, "SE_RESET_SCREEN_PALETTE")],
    "BARRAGE": [s(1, "0_ROCKS_TOSS", 0, 2), s(None, "0_STAR_TWICE", 0, 3)],
    "LEECH_LIFE": [s(1, "0_STAR", 0, 3), s(None, "0_CIRCLE_1_SQUARE_TOSS_BACK", 0, 3)],
    "LOVELY_KISS": [s(1, "0_HEART_1_MUSIC", 0, 5), s(None, "0_HEART_1_MUSIC", 0, 3)],
    "SKY_ATTACK": [e(None, "SE_LIGHT_SCREEN_PALETTE"), e(1, "SE_SLIDE_MON_OFF"), s(None, "1_STARS_SMALL_TOSS", 1, 2),
                   s(None, "1_STAR_BIG", 1, 3), e(None, "SE_SHOW_MON_PIC"), e(None, "SE_RESET_SCREEN_PALETTE")],
    "TRANSFORM": [s(1, "0_CIRCLE_1_SQUARE_APPEARS", 1, 4), s(None, "0_BALL_POOF", 0, 5), e(None, "SE_TRANSFORM_MON")],
    "BUBBLE": [s(1, "0_WATER_BUBBLES", 0, 4)],
    "DIZZY_PUNCH": [s(1, "0_STAR", 0, 4), s(None, "0_BIRDIES_CIRCLING_ENEMY", 0, 4)],
    "SPORE": [s(1, "0_CIRCLES_FALLING", 1, 5)],
    "FLASH": [e(None, "SE_LIGHT_SCREEN_PALETTE"), e(1, "SE_FLASH_SCREEN_LONG"), e(None, "SE_RESET_SCREEN_PALETTE")],
    "PSYWAVE": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "1_CIRCLE_BLACK_TOSS", 1, 3), e(None, "SE_WAVY_SCREEN"),
                e(None, "SE_RESET_SCREEN_PALETTE")],
    "SPLASH": [e(1, "SE_BOUNCE_UP_AND_DOWN"), s(None, "0_WATER_1_FIRE_BARRIER", 0, 3)],
    "ACID_ARMOR": [s(None, "0_SHELL", 1, 3), e(1, "SE_SLIDE_MON_DOWN_AND_HIDE")],
    "CRABHAMMER": [s(1, "0_STAR_DESCENDING", 0, 3), s(None, "0_WATER_DROPLETS", 0, 3)],
    "EXPLOSION": [s(1, "1_SELFDESTRUCT", 1, 2), s(None, "1_EXPLOSION_SMALL_ENEMY", 1, 3), e(None, "SE_SHAKE_SCREEN")],
    "FURY_SWIPES": [s(1, "0_SCRATCHES", 0, 3), s(1, "0_SCRATCHES", 0, 2)],
    "BONEMERANG": [s(1, "0_CIRCLE_1_SQUARE_HALF_TOSS", 0, 2), s(None, "0_CIRCLE_1_SQUARE_TOSS_BACK", 0, 2)],
    "REST": [s(1, "0_STATUS_SLEEP", 0, 10), e(None, "SE_BLINK_MON")],
    "ROCK_SLIDE": [s(1, "0_ROCKS_FALL_ENEMY", 0, 2), e(None, "SE_SHAKE_SCREEN")],
    "HYPER_FANG": [s(1, "0_SLICE_BOTH_SIDES", 0, 3), s(None, "0_STAR_HIGH", 0, 3)],
    "SHARPEN": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(1, "1_SWORDS_CIRCLING", 1, 3), e(None, "SE_RESET_SCREEN_PALETTE")],
    "CONVERSION": [e(None, "SE_DARK_SCREEN_FLASH"), s(1, "0_CIRCLE_1_SQUARE_APPEARS", 1, 4), e(None, "SE_DARK_SCREEN_FLASH")],
    "TRI_ATTACK": [s(1, "1_TRIANGLE_TOSS", 1, 3), e(None, "SE_DARK_SCREEN_FLASH"), s(None, "1_LIGHTNING_BALL", 1, 3)],
    "SUPER_FANG": [e(None, "SE_DARK_SCREEN_PALETTE"), s(1, "0_SLICE_BOTH_SIDES", 0, 3), e(None, "SE_RESET_SCREEN_PALETTE"),
                   s(None, "0_STAR", 0, 3)],
    "SLASH": [e(None, "SE_DARK_SCREEN_FLASH"), s(1, "0_SLICE", 0, 3)],
    "SUBSTITUTE": [e(None, "SE_BLINK_MON"), e(1, "SE_SLIDE_MON_OFF"), s(None, "0_BALL_POOF", 0, 6), e(None, "SE_SUBSTITUTE_MON")],
    "STRUGGLE": [e(None, "SE_SHAKE_BACK_AND_FORTH"), s(1, "0_STAR", 0, 4)],
}

# non-move animations (labels after the move part of the pointer table)
XA = {
    "ZigZagScreenAnim": [e(None, "SE_WAVY_SCREEN")],
    "ShowPicAnim": [e(None, "SE_SHOW_ENEMY_MON_PIC")],
    "HidePicAnim": [e(None, "SE_HIDE_ENEMY_MON_PIC")],
    "EnemyFlashAnim": [e(None, "SE_SHOW_MON_PIC")],
    "PlayerFlashAnim": [e(None, "SE_FLASH_MON_PIC")],
    "EnemyHUDShakeAnim": [e(None, "SE_SHAKE_ENEMY_HUD")],
    "TradeBallDropAnim": [s(None, "2_TRADE_BALL_DROP", 2, 5)],
    "TradeBallAppear1Anim": [s(None, "2_TRADE_BALL_SHAKE", 2, 5)],
    "TradeBallAppear2Anim": [s(None, "2_TRADE_BALL_APPEAR", 2, 8)],
    "TradeBallPoofAnim": [s(None, "2_TRADE_BALL_POOF", 2, 5)],
    "XStatItemAnim": [e(None, "SE_LIGHT_SCREEN_PALETTE"), s(None, "0_CIRCLES_CENTERING", 0, 3), e(None, "SE_RESET_SCREEN_PALETTE")],
    "ShrinkingSquareAnim": [s(None, "0_CIRCLE_1_SQUARE_CLOSING", 0, 4), e(None, "SE_DARK_SCREEN_FLASH")],
    "XStatItemBlackAnim": [e(None, "SE_DARKEN_MON_PALETTE"), s(None, "0_CIRCLES_CENTERING", 1, 3),
                           e(None, "SE_RESET_SCREEN_PALETTE")],
    "ShrinkingSquareBlackAnim": [e(None, "SE_DARKEN_MON_PALETTE"), s(None, "0_CIRCLE_1_SQUARE_CLOSING", 1, 4),
                                 e(None, "SE_RESET_SCREEN_PALETTE")],
    "UnusedAnim": [e(None, "SE_SHOOT_MANY_BALLS_UPWARD")],
    "ParalyzeAnim": [s("THUNDER_WAVE", "0_STATUS_PARALYZED", 0, 3), s(None, "0_STATUS_PARALYZED", 0, 3)],
    "PoisonAnim": [s("POISON_GAS", "0_STATUS_POISONED", 0, 6)],
    "SleepPlayerAnim": [s("SING", "0_STATUS_SLEEP", 0, 12), s(None, "0_STATUS_SLEEP", 0, 10)],
    "SleepEnemyAnim": [s("SING", "0_STATUS_SLEEP_ENEMY", 0, 12), s(None, "0_STATUS_SLEEP_ENEMY", 0, 10)],
    "ConfusedPlayerAnim": [s("CONFUSE_RAY", "0_STATUS_CONFUSED", 0, 6), s(None, "0_STATUS_CONFUSED", 0, 5)],
    "ConfusedEnemyAnim": [s("CONFUSE_RAY", "0_STATUS_CONFUSED_ENEMY", 0, 6), s(None, "0_STATUS_CONFUSED_ENEMY", 0, 5)],
    "SlideDownAnim": [e("EARTHQUAKE", "SE_SLIDE_MON_DOWN")],
    "BallTossAnim": [s(None, "0_BALL_TOSS_HIGH", 0, 2)],
    "GreatTossAnim": [s(None, "0_BALL_TOSS_MIDDLE", 0, 2)],
    "UltraTossAnim": [s(None, "0_BALL_TOSS_LOW", 0, 3)],
    "BallShakeAnim": [s(None, "0_BALL_SHAKE_ENEMY", 0, 5)],
    "BallPoofAnim": [s(None, "0_BALL_POOF_ENEMY", 0, 5)],
    "BallBlockAnim": [s(None, "0_BALL_BLOCK", 0, 4)],
    "ShakeScreenAnim": [e(None, "SE_SHAKE_SCREEN")],
    "ThrowRockAnim": [s("ROCK_THROW", "0_SAFARI_ROCK", 0, 2)],
    "ThrowBaitAnim": [s("LOVELY_KISS", "0_SAFARI_BAIT", 0, 3)],
}

# sequences drawn only from tiles that mean something in both sets (rings / squares,
# orbs / small squares, hearts / music signs, column pieces / flame pieces)
BOTH = {"0_HEART_1_MUSIC", "0_CIRCLES_1_SQUARES_CENTERING_ENEMY", "0_CIRCLE_1_SQUARE_TOSS_BACK",
        "0_CIRCLE_1_SQUARE_APPEARS", "0_CIRCLE_1_SQUARE_CLOSING", "0_WATER_1_FIRE_BARRIER",
        "0_WATER_1_FIRE_GEYSER", "0_CIRCLES_FALLING", "0_SHELL", "0_CIRCLES_CENTERING"}

# move ids whose animation id makes the engine run extra code per frame block
FLASH_EACH_BLOCK = {"MEGA_PUNCH", "GUILLOTINE", "MEGA_KICK", "HEADBUTT", "DISABLE", "BUBBLEBEAM", "REFLECT", "SPORE"}


# ------------------------------------------------------------------- tree helpers

def rd(tree, rel):
    return open(os.path.join(tree, rel), encoding="utf-8").read()


def wr(tree, rel, text):
    open(os.path.join(tree, rel), "w", encoding="utf-8", newline="\n").write(text)


def consts(text, start_marker=None, stop=None):
    """names of `const X` lines, in order, from the const_def that follows start_marker"""
    out, on = [], start_marker is None
    for line in text.splitlines():
        if not on:
            on = start_marker in line
            continue
        m = re.match(r"\s*const\s+(\w+)", line)
        if m:
            out.append(m.group(1))
        elif stop and re.search(stop, line):
            break
    return out


def hx(v):
    return f"${v & 0xFF:02x}"


FL = {0: "0", 1: "OAM_XFLIP", 2: "OAM_YFLIP", 3: "OAM_XFLIP | OAM_YFLIP"}


# ------------------------------------------------------------------- building

def build(tree):
    mac = rd(tree, "constants/move_animation_constants.asm")
    sub_consts = [c for c in consts(mac, "; subanimations that are part", r"^DEF NUM_SUBANIMS") if c.startswith("SUBANIM_")]
    fb_consts = [c for c in consts(mac, "; frame blocks that are part", r"^DEF NUM_FRAMEBLOCKS")]
    bc_consts = [c for c in consts(mac, "; base coordinates that are part", r"^DEF NUM_BASECOORDS")]
    assert len(fb_consts) == NUM_FB and len(bc_consts) == NUM_BC, (len(fb_consts), len(bc_consts))
    assert fb_consts[SMALL_DISC_ID] == "FRAMEBLOCK_SMALL_BLACK_CIRCLE"
    missing = [c for c in sub_consts if c[len("SUBANIM_"):] not in SUB]
    assert not missing, missing
    assert len(SUB) == len(sub_consts)

    # frame block ids: in order of first use; the two named slots hold the discs
    fb_of = {"disc": SMALL_DISC_ID, "sphere": LARGE_SPHERE_ID}
    free = [i for i in range(NUM_FB) if i not in fb_of.values()]
    for c in sub_consts:
        for blk, _, _ in SUB[c[8:]][1]:
            if blk not in fb_of:
                fb_of[blk] = free.pop(0)
    used = len(fb_of)
    for name, sp in EXTRA:
        if not free:
            break
        SH[name] = sp
        fb_of[name] = free.pop(0)
    assert not free, f"{len(free)} frame block slots left empty"
    blocks = {i: n for n, i in fb_of.items()}

    # base coordinates: block centres in OAM space (y + 16, x + 8), merged until they fit
    want = []
    for c in sub_consts:
        for blk, (x, y), _ in SUB[c[8:]][1]:
            want.append(((y + 16) & 0xFF, (x + 8) & 0xFF))
    for q in range(1, 9):
        snap = lambda v: (round(v[0] / q) * q & 0xFF, round(v[1] / q) * q & 0xFF)
        uniq = list(dict.fromkeys(snap(v) for v in want))
        if len(uniq) <= NUM_BC:
            break
    pool = uniq[:]
    k = 0
    while len(pool) < NUM_BC:      # the rest: a lattice over the battle field
        y, x = 24 + (k * 37) % 96, 16 + (k * 53) % 152
        k += 1
        if (y, x) not in pool:
            pool.append((y, x))
    bc_of = {v: i for i, v in enumerate(pool)}

    # ---- frame_blocks.asm (it also includes the base coordinates)
    incl = re.findall(r"^INCLUDE [^\n]*", rd(tree, "data/battle_anims/frame_blocks.asm"), re.M)
    assert incl, "frame_blocks.asm has no INCLUDE of the base coordinates"
    out = ["FrameBlockPointers:", "\ttable_width 2"]
    labels = []
    for i, c in enumerate(fb_consts):
        lab = {SMALL_DISC_ID: "SmallBlackCircleFrameBlock", LARGE_SPHERE_ID: "LargeBlackCircleFrameBlock"}.get(i, f"FrameBlock{i:02x}")
        labels.append(lab)
        out.append(f"\tdw {lab}")
    out += ["\tassert_table_length NUM_FRAMEBLOCKS", "",
            "; KITHBOUND arrangements: sprites are placed around the block's anchor (the base",
            "; coordinate is the anchor), so offsets wrap below zero.", ""]
    for i, lab in enumerate(labels):
        sp = SH[blocks[i]]
        assert 0 < len(sp) <= 40, (blocks[i], len(sp))
        out += [f"{lab}: ; {blocks[i]}", f"\tdb {len(sp)} ; #"]
        for (dx, dy, t, f) in sp:
            ox, oy = dx & 0xFF, dy & 0xFF
            out.append(f"\tdbsprite {ox // 8:2d}, {oy // 8:2d}, {ox % 8}, {oy % 8}, ${t:02x}, {FL[f]}")
        out.append("")
    out += incl + [""]
    wr(tree, "data/battle_anims/frame_blocks.asm", "\n".join(out))

    # ---- base_coords.asm
    out = ["FrameBlockBaseCoords:", "\ttable_width 2"]
    for i, (y, x) in enumerate(pool):
        out.append(f"\tdb ${y:02X}, ${x:02X} ; {bc_consts[i]}")
    out += ["\tassert_table_length NUM_BASECOORDS", ""]
    wr(tree, "data/battle_anims/base_coords.asm", "\n".join(out))

    # ---- subanimations.asm
    old = rd(tree, "data/battle_anims/subanimations.asm")
    sub_labels = re.findall(r"^\s*dw (Subanim_\w+)", old, re.M)
    assert len(sub_labels) == len(sub_consts)
    out = ["SubanimationPointers:", "\ttable_width 2"]
    for lab in sub_labels:
        out.append(f"\tdw {lab}")
    out += ["\tassert_table_length NUM_SUBANIMS", "",
            "; format:", "; subanim type, count", "; REPT count",
            ";     db frame block id, base coordinate id, frame block mode", "; ENDR", "",
            "MACRO subanim", "\tdb (\\1 << 5) | \\2", "ENDM", ""]
    for lab, c in zip(sub_labels, sub_consts):
        typ, ents = SUB[c[8:]]
        assert 1 <= len(ents) <= 31, (c, len(ents))
        oam = 0
        for blk, _, mode in ents:
            n = len(SH[blk])
            assert oam + n <= 40, (c, "OAM overflow")
            oam = oam + n if mode in (2, 3) else (oam if mode == 4 else 0)
        out += [f"{lab}:", f"\tsubanim SUBANIMTYPE_{typ}, {len(ents)}"]
        for blk, (x, y), mode in ents:
            v = snap(((y + 16) & 0xFF, (x + 8) & 0xFF))
            if v not in bc_of:
                v = min(pool, key=lambda p: (p[0] - v[0]) ** 2 + (p[1] - v[1]) ** 2)
            out.append(f"\tdb {fb_consts[fb_of[blk]]}, {bc_consts[bc_of[v]]}, FRAMEBLOCKMODE_{mode:02X}")
        out.append("")
    wr(tree, "data/battle_anims/subanimations.asm", "\n".join(out))

    # ---- animations.asm
    move_consts = consts(rd(tree, "constants/move_constants.asm"), "const_def", r"NUM_ATTACKS")
    move_consts = [m for m in move_consts if m != "NO_MOVE"]
    old = rd(tree, "data/moves/animations.asm")
    head = old[:old.index("; each animation is a list")]
    ptr_labels = re.findall(r"^\s*dw (\w+)", head, re.M)
    label_move = {}
    for i, lab in enumerate(ptr_labels[:len(move_consts)]):
        label_move[lab] = move_consts[i]
    body_labels = list(dict.fromkeys(ptr_labels))
    # moves that shared one label get their own label only when the pointer table names it
    out = [head.rstrip("\n"), "",
           "; each animation is a list of subanimations",
           "; and/or special effects, terminated by -1", "",
           ";\\1: sound_id", ";\\2: special_effect_id or subanimation_id",
           "; if \\2 is a subanimation_id:", ";\\3: tileset_id", ";\\4: delay",
           "MACRO battle_anim", "\tIF _NARG == 4", "\t\tdb (\\3 << 6) | \\4", "\t\tdb \\1 - 1", "\t\tdb \\2",
           "\tELSE", "\t\tdb \\2", "\t\tdb \\1 - 1", "\tENDC", "ENDM", ""]
    nmoves = 0
    for lab in body_labels:
        if lab in label_move:
            mv = label_move[lab]
            script = MV[mv]
            nmoves += 1
        else:
            script = XA[lab]
            mv = None
        out.append(f"{lab}:")
        for cmd in script:
            snd = cmd[0]
            snd = "NO_MOVE" if snd is None else (mv if snd == 1 else snd)
            if len(cmd) == 2:
                out.append(f"\tbattle_anim {snd}, {cmd[1]}")
            else:
                _, sa, ts, d = cmd
                assert 0 < d < 64 and ts in (0, 1, 2)
                assert sa[0] == str(ts) or (ts < 2 and sa in BOTH), (lab, sa, ts)
                if mv in FLASH_EACH_BLOCK:
                    assert len(SUB[sa][1]) <= 6, (lab, sa)
                if mv == "GROWL":
                    assert all(len(SH[b]) <= 4 for b, _, _ in SUB[sa][1]), sa
                out.append(f"\tbattle_anim {snd}, SUBANIM_{sa}, {ts}, {d}")
        out.append("\tdb -1 ; end")
        out.append("")
    assert set(MV) == set(move_consts), set(move_consts) ^ set(MV)
    wr(tree, "data/moves/animations.asm", "\n".join(out))

    # ---- sfx.asm
    write_sfx(tree, move_consts)
    return dict(blocks_used=used, coords_used=len(uniq), coord_snap=q, subanims=len(sub_consts), anims=len(body_labels))


# ------------------------------------------------------------------- sounds

def sfx_features(tree):
    """battle sound effects of the clean tree: which channels, how long"""
    mc = rd(tree, "constants/music_constants.asm")
    names = re.findall(r"music_const\s+(SFX_\w+),\s*(\w+)", mc)
    order = [n for n, _ in names]
    lab_of = dict(names)
    i0, i1 = order.index("SFX_PECK"), order.index("SFX_BATTLE_36")
    battle = order[i0:i1 + 1]
    hdr = rd(tree, "audio/headers/sfxheaders2.asm")
    src = "".join(open(os.path.join(tree, "audio/sfx", f), encoding="utf-8").read()
                  for f in sorted(os.listdir(os.path.join(tree, "audio/sfx"))))
    feats = {}
    for c in battle:
        m = re.search(rf"^{lab_of[c]}::\n(.*?)(?=^\S|\Z)", hdr, re.M | re.S)
        chans = re.findall(r"channel (\d), (\w+)", m.group(1)) if m else []
        sq = nz = 0
        for ch, cl in chans:
            mm = re.search(rf"^{cl}:\n(.*?)sound_ret", src, re.M | re.S)
            body = mm.group(1) if mm else ""
            ln = sum(int(a) for a in re.findall(r"(?:square|noise)_note (\d+)", body))
            if ch == "8":
                nz += ln
            else:
                sq += ln
        feats[c] = (sq, nz)
    return feats


def write_sfx(tree, move_consts):
    feats = sfx_features(tree)
    mvtxt = rd(tree, "data/moves/moves.asm")
    info = {m.group(1): (m.group(2), int(m.group(3)), m.group(4))
            for m in re.finditer(r"^\s*move (\w+),\s*(\w+),\s*(\d+),\s*(\w+)", mvtxt, re.M)}
    noise = sorted((c for c, (sq, nz) in feats.items() if nz and not sq), key=lambda c: feats[c][1])
    tone = sorted((c for c, (sq, nz) in feats.items() if sq and not nz), key=lambda c: feats[c][0])
    mixed = sorted((c for c, (sq, nz) in feats.items() if sq and nz), key=lambda c: sum(feats[c]))
    half = len(noise) // 2
    pools = {"tap": noise[:half] or noise, "thud": noise[half:] or noise, "tone": tone or mixed,
             "mixed": mixed or tone}
    cut = {"KARATE_CHOP", "SCRATCH", "VICEGRIP", "GUILLOTINE", "RAZOR_WIND", "CUT", "SLASH", "FURY_SWIPES",
           "CRABHAMMER", "BITE", "HYPER_FANG", "SUPER_FANG", "CLAMP", "RAZOR_LEAF", "VINE_WHIP", "PECK", "DRILL_PECK"}
    voice = {"GROWL", "ROAR", "SING", "SUPERSONIC", "SCREECH", "LOVELY_KISS"}
    fast = {"QUICK_ATTACK", "AGILITY", "COMET_PUNCH", "DOUBLESLAP", "FURY_ATTACK", "FURY_SWIPES", "PIN_MISSILE",
            "TWINEEDLE", "SPIKE_CANNON", "SWIFT", "DOUBLE_KICK", "BARRAGE", "PECK", "THUNDERSHOCK", "EMBER"}
    pitch_of = {"ICE": 0x58, "ELECTRIC": 0x48, "PSYCHIC_TYPE": 0x38, "FIRE": 0x20, "WATER": 0x18, "GRASS": 0x28,
                "POISON": 0x10, "BUG": 0x30, "BIRD": 0x40, "FLYING": 0x40, "GHOST": 0x08, "DRAGON": 0x04,
                "ROCK": 0x00, "GROUND": 0x00, "FIGHTING": 0x0c, "NORMAL": 0x14}
    rows = []
    for mv in move_consts:
        eff, pw, typ = info.get(mv, ("", 0, "NORMAL"))
        h = zlib.crc32(("kith-sfx-" + mv).encode())
        if mv in voice:
            pool = pools["tone"]
        elif mv in cut:
            pool = pools["tap"]
        elif typ in ("FIRE", "WATER", "ELECTRIC", "ICE", "GRASS", "POISON", "DRAGON"):
            pool = pools["mixed"]
        elif typ in ("PSYCHIC_TYPE", "GHOST") or pw == 0:
            pool = pools["tone"]
        elif pw >= 80 or typ in ("ROCK", "GROUND"):
            pool = pools["thud"]
        else:
            pool = pools["tap"] if h & 1 else pools["thud"]
        sfx = pool[h % len(pool)]
        pitch = (pitch_of.get(typ, 0x10) + (h >> 8) % 0x18) & 0xFF
        if mv in fast:
            tempo = 0x28 + (h >> 16) % 0x28
        elif pw >= 90:
            tempo = 0xb8 + (h >> 16) % 0x40
        else:
            tempo = 0x68 + (h >> 16) % 0x38
        if mv in ("GROWL", "ROAR"):            # added to the cry's own pitch/tempo
            pitch, tempo = (0x0c, 0x18) if mv == "GROWL" else (0xf4, 0x30)
        rows.append((sfx, pitch, tempo, mv))
    extra = (pools["tap"][0], 0x08, 0x70, None)
    out = ["MoveSoundTable:", "\ttable_width 3", "\t; ID, pitch mod, tempo mod"]
    for sfx, p, t, mv in rows:
        out.append(f"\tdb {sfx + ',':23s} ${p:02x}, ${t:02x} ; {mv}")
    out.append("\tassert_table_length NUM_ATTACKS")
    out.append(f"\tdb {extra[0] + ',':23s} ${extra[1]:02x}, ${extra[2]:02x}")
    out.append("")
    wr(tree, "data/moves/sfx.asm", "\n".join(out))


# ------------------------------------------------------------------- dirty-room check

def parse_tables(tree):
    """{table: {key: normalised content}} for the five tables"""
    res = {}
    fb = rd(tree, "data/battle_anims/frame_blocks.asm")
    ptr = re.findall(r"^\s*dw (\w+)", fb, re.M)
    bodies = {}
    for m in re.finditer(r"^(\w+):[^\n]*\n\tdb (\d+) ; #\n((?:\tdbsprite[^\n]*\n?)*)", fb, re.M):
        sp = []
        for a in re.findall(r"dbsprite\s+(-?\d+),\s*(-?\d+),\s*(\d+),\s*(\d+),\s*\$([0-9a-fA-F]+),\s*([^\n;]*)", m.group(3)):
            xt, yt, xp, yp, t, f = a
            fl = (1 if "XFLIP" in f else 0) | (2 if "YFLIP" in f else 0)
            sp.append((((int(yt) * 8) % 256 + int(yp)) % 256, ((int(xt) * 8) % 256 + int(xp)) % 256, int(t, 16), fl))
        bodies[m.group(1)] = sp
    res["frame_blocks"] = [tuple(bodies.get(l, [])) for l in ptr]
    bc = rd(tree, "data/battle_anims/base_coords.asm")
    res["base_coords"] = re.findall(r"db \$([0-9A-Fa-f]+), \$([0-9A-Fa-f]+)", bc)
    res["base_coords"] = [(int(a, 16), int(b, 16)) for a, b in res["base_coords"]]
    sa = rd(tree, "data/battle_anims/subanimations.asm")
    sptr = re.findall(r"^\s*dw (Subanim_\w+)", sa, re.M)
    sb = {}
    for m in re.finditer(r"^(Subanim_\w+):\n((?:Subanim_\w+:\n)*)\tsubanim (\w+), (\d+)\n((?:\tdb [^\n]*\n?)*)", sa, re.M):
        ents = tuple(re.findall(r"db (\w+), (\w+), (\w+)", m.group(5)))
        val = (m.group(3), ents)
        for lab in [m.group(1)] + re.findall(r"(Subanim_\w+):", m.group(2)):
            sb[lab] = val
    res["subanimations"] = [sb.get(l) for l in sptr]
    an = rd(tree, "data/moves/animations.asm")
    aptr = re.findall(r"^\s*dw (\w+)", an[:an.index("; each animation")], re.M)
    ab = {}
    for m in re.finditer(r"^(\w+Anim):\n((?:\w+Anim:\n)*)((?:\tbattle_anim [^\n]*\n)*)\tdb -1", an, re.M):
        cmds = tuple(re.sub(r"\s+", "", c) for c in re.findall(r"battle_anim ([^\n;]*)", m.group(3)))
        for lab in [m.group(1)] + re.findall(r"(\w+Anim):", m.group(2)):
            ab[lab] = cmds
    res["animations"] = [ab.get(l) for l in aptr]
    sx = rd(tree, "data/moves/sfx.asm")
    res["sfx"] = re.findall(r"^\s*db (SFX_\w+),\s*\$([0-9a-fA-F]+),\s*\$([0-9a-fA-F]+)", sx, re.M)
    res["sfx"] = [(a, int(b, 16), int(c, 16)) for a, b, c in res["sfx"]]
    return res


def norm_block(sp):
    """sprite set translated so its top-left sprite sits at 0,0 (signed offsets)"""
    if not sp:
        return frozenset()
    s = [((y + 128) % 256 - 128, (x + 128) % 256 - 128, t, f) for y, x, t, f in sp]
    my, mx = min(v[0] for v in s), min(v[1] for v in s)
    return frozenset((y - my, x - mx, t, f) for y, x, t, f in s)


def check(tree, retail):
    a, b = parse_tables(tree), parse_tables(retail)
    ok = True
    print(f"{'table':15s} entries  differ  share")
    for k in ("frame_blocks", "base_coords", "subanimations", "animations", "sfx"):
        new, old = a[k], b[k]
        n = min(len(new), len(old))
        diff = sum(1 for i in range(n) if new[i] != old[i])
        share = diff / n if n else 0
        ok &= share >= 0.9 and len(new) == len(old)
        print(f"{k:15s} {n:7d} {diff:7d}  {share:6.1%}" + ("" if len(new) == len(old) else f"  LENGTH {len(new)} vs {len(old)}"))
    # content check beyond index order: arrangements / anchor points reused anywhere
    oldb = {norm_block(x) for x in b["frame_blocks"] if x}
    same = sum(1 for x in a["frame_blocks"] if norm_block(x) in oldb)
    oldc = set(b["base_coords"])
    samec = sum(1 for x in a["base_coords"] if x in oldc)
    olds = {x[1] for x in b["subanimations"] if x}
    sames = sum(1 for x in a["subanimations"] if x and x[1] in olds)
    olda = {x for x in b["animations"] if x}
    samea = [i for i, x in enumerate(a["animations"]) if x in olda]
    print(f"anywhere-match: blocks {same}/{len(a['frame_blocks'])}, coords {samec}/{len(a['base_coords'])}, "
          f"sequences {sames}/{len(a['subanimations'])}, scripts {len(samea)}/{len(a['animations'])}")
    print("PASS" if ok else "FAIL")
    return ok


def main(tree):
    st = build(tree)
    print(f"anims_gen: {st['subanims']} sequences, {st['anims']} scripts, {st['blocks_used']} designed blocks "
          f"(+{NUM_FB - st['blocks_used']} variety), {st['coords_used']} anchor points (snap {st['coord_snap']} px)")


if __name__ == "__main__":
    if sys.argv[1] == "--check":
        sys.exit(0 if check(sys.argv[2], sys.argv[3]) else 1)
    main(sys.argv[1])
