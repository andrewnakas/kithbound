"""KITHBOUND families, pass 2 part B: creatures whose roster concept changed (national 86-151)."""
import math

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_fam import fam, spark
from games.pokered.art.k_kith_fam2 import insect
from games.pokered.art.k_kith_fam3 import feet2, note
from games.pokered.art.k_kith_fam4 import claw, rock
from games.pokered.art.k_kith_fam6 import antennae, bell, eyespot, frill, lantern_pod, moth, snail_shell
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, fang, fin, flame, horn,
                                          leaf, rot, spikes, spiral, spots, star, stripes, tail_fin)


# =================================================================== 86 FLOEPUP line (penguins)
@fam("FLOEPUP", "FROSTSEAL")
def penguin_line(f, st):
    big = st == 1
    if not big:
        feet2(f, 38, 58, 95, 6, 2)
        f.ell(76, 66, 6, 12, 2, ang=-25)
        b = f.ell(50, 66, 25, 28, 2, hl=True)
        f.mark_ell(46, 72, 16, 21, 0, clip=b)
        f.ell(24, 66, 6, 12, 2, ang=25)
        for k, a in enumerate((-120, -95, -70, -45)):
            horn(f, 50 + (k - 1.5) * 5, 40, 10 if k % 2 else 8, 4, a, s=0)
        f.poly([(36, 54), (26, 57), (36, 60)], 1)
        f.eye(40, 52, 3.2, "round", -1)
        f.eye(54, 51, 3.0, "round", -1)
    else:
        for x in (40, 58):
            f.ell(x, 96, 8, 3, 2)
        f.poly([(64, 80), (80, 94), (60, 92)], 2)
        b = f.poly(arc(50, 62, 22, 34, 180, 360, 12) + arc(50, 62, 22, 32, 0, 180, 10), 2, hl=True)
        f.mark_poly(arc(44, 64, 13, 26, 100, 260, 10) + arc(44, 64, 15, 28, 280, 440, 10), 0, clip=b)
        f.poly([(64, 46), (84, 70), (78, 74), (62, 60)], 2)
        f.poly([(38, 46), (24, 72), (30, 74), (42, 60)], 2)
        f.poly([(36, 30), (18, 34), (36, 38)], 1)
        horn(f, 30, 38, 14, 4, 100, curve=-0.3, s=0)
        horn(f, 38, 38, 12, 3.5, 95, curve=-0.3, s=0)
        spikes(f, arc(50, 30, 16, 12, 200, 320, 4), 7, 5, s=0, side=1)
        f.eye(42, 28, 2.8, "angry", -1)
        f.eye(52, 27, 2.6, "angry", -1)


# =================================================================== 88 MUCKLET line (snails)
@fam("MUCKLET", "SLOPMOUND")
def snail_line(f, st):
    if st == 0:
        b = f.poly([(14, 92), (16, 74), (26, 62), (34, 66), (36, 84), (80, 86), (86, 94)], 2)
        for x in (18, 26):
            f.stroke([(x + 4, 66), (x, 54)], 1.0, 1.0, 3)
            f.ell(x, 52, 2.5, 2.5, 2)
        s_ = snail_shell(f, 58, 66, 22, s=1)
        for x, ln in ((44, 10), (60, 14), (72, 8)):
            f.stroke([(x, 84), (x, 84 + ln * 0.6)], 1.6, 1.0, 2)
            f.ell(x, 85 + ln * 0.6, 2, 2.4, 2)
        f.eye(22, 70, 2.6, "round", -1)
        f.line([(18, 80), (24, 81)], 3, face=True)
    else:
        b = f.poly([(8, 94), (10, 70), (22, 56), (34, 60), (36, 82), (84, 84), (94, 95)], 2)
        for x in (12, 22):
            f.stroke([(x + 4, 60), (x, 46)], 1.2, 1.2, 3)
            f.ell(x, 44, 3, 3, 2)
        f.poly([(60, 30), (74, 30), (76, 8), (58, 8)], 1)
        f.poly([(56, 10), (78, 10), (78, 4), (56, 4)], 2)
        snail_shell(f, 60, 62, 28, s=1)
        for k, (x, y, r) in enumerate(((70, 0, 4), (80, -4, 5), (92, -6, 6))):
            f.ell(x, y, r, r * 0.8, 1, sh=0)
        for x in (40, 64, 80):
            f.stroke([(x, 84), (x, 92)], 1.8, 1.2, 2)
        f.eye(16, 64, 3, "angry", -1)
        f.eye(24, 63, 2.6, "angry", -1)
        f.ell(16, 76, 4, 2.5, 3, sh=0, face=True)


# =================================================================== 90 PEARLIP line (urchins)
def urchin(f, cx, cy, r, n, ln, s_body=2, s_sp=2, wd=None, seed=0):
    for i in range(n):
        a = -90 + i * 360 / n + (seed % 7)
        if 60 < (a % 360) < 120:
            continue
        horn(f, cx + math.cos(math.radians(a)) * r * 0.8, cy + math.sin(math.radians(a)) * r * 0.8, ln, wd or ln * 0.28, a, s=s_sp)
    return f.ell(cx, cy, r, r * 0.9, s_body, hl=True)


@fam("PEARLIP", "SPIKECLAM")
def urchin_line(f, st):
    if st == 0:
        urchin(f, 50, 62, 22, 18, 14, s_body=1, s_sp=2)
        for x in (40, 58):
            f.ell(x, 60, 6, 6, 0, hl=False)
            f.ell(x - 2, 58, 1.6, 1.6, 0, line=False, sh=0)
            f.ell(x + 1, 61, 2.4, 2.4, 1, line=False, sh=0)
        f.line([(46, 72), (49, 74), (52, 72)], 3, face=True)
        for x in (36, 50, 64):
            f.ell(x, 86, 2.5, 3, 1)
    else:
        b = urchin(f, 50, 58, 26, 14, 26, s_body=2, s_sp=3, wd=7, seed=3)
        for k in (-0.4, 0.4):
            f.mark_stroke([(24, 58 + k * 30), (76, 58 + k * 30)], 2.0, s=1, clip=b)
        for x in (38, 62):
            f.ell(x, 56, 6, 6, 0, hl=False)
            f.ell(x + 1, 57, 2.6, 2.6, 2, line=False, sh=0)
        f.line([(40, 70), (60, 70)], 3, face=True)


# =================================================================== 92 WISPLET (candle flame) / 93 SHROUDLE (walking lantern)
@fam("WISPLET", "SHROUDLE")
def candle_line(f, st):
    if st == 0:
        f.ell(50, 92, 12, 3, 2)
        flame(f, 50, 84, 44, 70, n=3, s=1)
        f.ell(50, 66, 14, 13, 0, line=False, sh=0)
        f.ell(22, 66, 4, 4, 1)
        f.ell(78, 64, 4, 4, 1)
        f.eye(44, 64, 3.2, "round", -1)
        f.eye(56, 64, 3.2, "round", -1)
        f.line([(46, 74), (50, 76), (54, 74)], 3, face=True)
    else:
        for x in (40, 60):
            f.stroke([(x, 82), (x - 2, 96)], 2.6, 2.2, 2)
            f.ell(x - 4, 96, 5, 2.5, 2)
        box = f.poly([(28, 34), (72, 34), (76, 84), (24, 84)], 2)
        f.mark_poly([(34, 40), (66, 40), (68, 78), (32, 78)], 0, clip=box)
        flame(f, 50, 74, 22, 30, n=3, s=1, inner=False)
        f.eye(44, 58, 3, "angry", -1)
        f.eye(56, 58, 3, "angry", 1)
        for x in (36, 64):
            f.line([(x, 40), (x, 78)], 3)
        hood = f.poly([(20, 38), (36, 12), (50, 4), (64, 12), (80, 38), (64, 34), (36, 34)], 2)
        f.mark_poly([(36, 30), (50, 14), (64, 30)], 3, clip=hood)
        f.ell(50, 26, 2.5, 2.5, 0, line=False, sh=0)


# =================================================================== 94 NIGHTGRIN (shadow heron)
@fam("NIGHTGRIN")
def nightgrin(f, st):
    for dx in (4, -4):
        f.stroke([(58 + dx, 64), (60 + dx, 80), (56 + dx, 96)], 1.6, 1.4, 3)
        f.stroke([(50 + dx, 96), (62 + dx, 96)], 1.2, 1.2, 3)
    f.poly([(70, 50), (94, 70), (86, 72), (90, 80), (68, 64)], 2)
    b = f.ell(60, 52, 15, 14, 2, ang=-20, hl=True)
    for (a, b_, c) in (((56, 46), (36, 56), (20, 76)), ((64, 46), (78, 60), (84, 82))):
        f.stroke([a, b_, c], 2.6, 2.0, 2)
        for k in range(3):
            horn(f, c[0] - 2 + k * 2, c[1], 6, 1.8, 95 - k * 10, s=3)
    f.stroke([(52, 42), (44, 28), (40, 20)], 3.4, 3.0, 2)
    f.ell(40, 18, 9, 8, 2)
    f.poly([(34, 16), (6, 22), (34, 22)], 2)
    f.poly([(42, 10), (54, 2), (48, 12)], 2)
    f.eye(38, 15, 2.8, "glow", -1)
    f.poly(arc(30, 21, 8, 3.5, 0, 180, 8), 0, face=True)
    f.line([(22, 21), (38, 21)], 3, face=True)


# =================================================================== 95 SLATEWORM (slate mole dragon)
@fam("SLATEWORM")
def slateworm(f, st):
    def back(f, q):
        for k in range(5):
            x = 42 + k * 9
            f.poly([(x - 5, 58 + abs(k - 2)), (x + 5, 56 + abs(k - 2)), (x + 3, 46 + abs(k - 2) * 1.5), (x - 4, 48 + abs(k - 2) * 1.5)], 2 if k % 2 else 1)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.ell(hx - hr * 1.5, hy + hr * 0.25, 3, 2.4, 3, sh=0)
        for k in range(3):
            horn(f, 22 + k * 3, 94, 7, 2.2, 120 - k * 10, curve=0.4, s=0)
    quad(f, bx=58, by=74, brx=28, bry=13, hx=30, hy=68, hr=12, hry=10, sn=10, snr=5, snd=0.3, ears=None, lr=5.5,
         tail="thin", tl=26, trr=5, tang=-15, eye="sleepy", eyer=2.4, back=back, head=head, neck=5, mouth=None, belly=1)


# =================================================================== 96 YAWNTAPIR line (tapir moths)
def tapir_head(f, x, y, r, big=False, eye="sleepy"):
    f.stroke([(x - r * 0.6, y + r * 0.2), (x - r * 1.3, y + r * 0.6), (x - r * 1.5, y + r * 1.4)], r * 0.32, r * 0.26, 1, group="th")
    h = f.ell(x, y, r, r * 0.9, 1, group="th", hl=True)
    f.eye(x - r * 0.35, y - r * 0.15, max(2.2, r * 0.22), eye, -1)
    f.eye(x + r * 0.3, y - r * 0.15, max(2.2, r * 0.22), eye, -1)
    return h


@fam("YAWNTAPIR", "DREAMSNOUT")
def tapirmoth_line(f, st):
    if st == 0:
        moth(f, 54, 58, 34, s_w=1, s_b=2, low=0.65, body_l=26)
        antennae(f, 54, 38, 12, spread=8, feather=True)
        tapir_head(f, 52, 44, 10)
        for x, y, r in ((82, 22, 3), (90, 12, 4)):
            f.line([(x - r, y - r), (x + r, y - r), (x - r, y + r), (x + r, y + r)], 3)
    else:
        def spot(f, j, x, y, r):
            f.mark_ell(x, y, r * 1.5, r * 1.5, 0, clip=j)
            f.mark_ell(x, y, r * 0.7, r * 0.7, 3, clip=j)
            spiral(f, x, y, r * 1.3, turns=1.2, s=2)
        moth(f, 54, 54, 46, s_w=2, s_b=1, low=0.6, eyespot=spot, body_l=30)
        antennae(f, 54, 32, 16, spread=10, feather=True, s=2)
        tapir_head(f, 52, 38, 11, eye="closed")
        f.line([(30, 86), (36, 82), (34, 90), (40, 86)], 2)


# =================================================================== 98 PINCHLET (hermit snail) / 99 CLAWMAJOR (hermit in a bell)
@fam("PINCHLET", "CLAWMAJOR")
def hermit_line(f, st):
    if st == 0:
        b = f.poly([(18, 94), (20, 78), (32, 70), (40, 84), (70, 88), (72, 95)], 1)
        cone = f.poly([(34, 86), (44, 50), (60, 30), (74, 52), (78, 86)], 2, hl=True)
        for k in range(3):
            f.line([(38 + k * 4, 80 - k * 14), (76 - k * 2, 72 - k * 14)], 3)
        f.stroke([(22, 80), (12, 74)], 1.6, 1.6, 1)
        claw(f, 8, 70, 6, ang=-30, s=0)
        f.eye(26, 76, 2.8, "round", -1)
        f.stroke([(28, 72), (26, 64)], 0.9, 0.9, 3)
    else:
        for i in range(3):
            x = 54 + i * 10
            f.stroke([(x, 82), (x + 6, 90), (x + 8, 97)], 1.8, 1.3, 3)
        bl = f.poly(arc(58, 46, 24, 26, 180, 360, 12) + [(84, 62), (92, 86), (24, 86), (32, 62)], 2, hl=True)
        f.mark_stroke([(24, 78), (92, 78)], 2, s=3, clip=bl)
        for x in (36, 50, 64, 78):
            f.mark_ell(x, 72, 1.6, 1.6, 0, clip=bl)
        f.ell(58, 18, 4, 3, 2)
        f.ell(30, 82, 12, 8, 3, sh=0)
        f.stroke([(30, 80), (18, 72)], 3, 3, 1)
        f.ell(14, 60, 14, 11, 1, ang=-30, hl=True)
        f.line([(6, 54), (18, 66)], 3)
        for x in (26, 34):
            f.eye(x, 80, 2.8, "glow", -1)


# =================================================================== 100 FUSEBALL line (lantern bugs)
def glow_rays(f, x, y, r, n=6):
    for i in range(n):
        a = math.radians(i * 360 / n + 15)
        f.line([(x + math.cos(a) * r, y + math.sin(a) * r), (x + math.cos(a) * (r + 5), y + math.sin(a) * (r + 5))], 2)


@fam("FUSEBALL", "FUSEBOMB")
def lanternbug_line(f, st):
    big = st == 1
    r = 22 + big * 6
    cx, cy = 62, 62
    glow_rays(f, cx + 2, cy, r + 2, n=7)
    for i in range(3):
        x = 34 + i * 9
        f.stroke([(x, 66), (x - 4, 80), (x - 1, 94)], 1.5, 1.2, 3)
    ab = f.ell(cx, cy, r, r * 0.85, 0, sh=2)
    for k in (-0.45, 0.0, 0.45):
        f.mark_stroke([(cx + k * r, cy - r), (cx + k * r + 2, cy + r)], 1.2, s=1, clip=ab)
    f.ell(cx, cy - r * 0.9, r * 0.55, r * 0.22, 2)
    th = f.ell(36, 56, 11 + big * 2, 10 + big * 2, 2 if big else 1, hl=True)
    h = f.ell(22, 52, 10 + big, 9 + big, 2 if big else 1)
    f.stroke([(22, 44), (18, 28), (28, 16), (40, 14)], 1.2, 1.2, 2)
    f.poly(star(42, 12, 6 + big * 2, 2.5, n=6), 0)
    if big:
        spark(f, 56, 8, 4)
        spark(f, 30, 4, 4)
    f.eye(18, 51, 3, "round" if not big else "angry", -1)
    f.eye(26, 50, 2.6, "round" if not big else "angry", -1)


# =================================================================== 102 PODCLUSTER (bean pods) / 103 PALMHEADS (mangrove)
def bean(f, x, y, ln, s=1, eye="dot"):
    j = f.ell(x, y + ln * 0.5, ln * 0.3, ln * 0.55, s, hl=True)
    for k in (0.3, 0.6):
        f.mark_ell(x, y + ln * (0.2 + k * 0.8), ln * 0.2, ln * 0.13, 2 if s == 1 else 1, clip=j)
    f.eye(x - ln * 0.12, y + ln * 0.42, 2.0, eye, -1)
    f.eye(x + ln * 0.12, y + ln * 0.42, 2.0, eye, -1)
    return j


@fam("PODCLUSTER", "PALMHEADS")
def bean_line(f, st):
    if st == 0:
        ring = f.ell(50, 26, 36, 12, 2)
        f.cut_ell(50, 26, 28, 7)
        for a in range(0, 360, 60):
            leaf(f, 50 + math.cos(math.radians(a)) * 34, 26 + math.sin(math.radians(a)) * 11, 10, 3.5, a - 60, s=1, vein=False)
        for k, x in enumerate((24, 38, 52, 66, 80)):
            y0 = 32 + (k % 2) * 4
            f.line([(x, y0), (x, y0 + 6)], 3)
            bean(f, x, y0 + 6, 26 + (k % 2) * 6, eye="dot" if k % 2 else "round")
    else:
        for x0, x1 in ((40, 18), (46, 36), (54, 62), (60, 82)):
            f.stroke([(x0, 70), ((x0 + x1) / 2, 74), (x1, 97)], 2.6, 2.0, 2)
        trunk = f.stroke([(50, 74), (50, 34)], 9, 7, 2)
        for k in range(3):
            f.mark_stroke([(42, 44 + k * 10), (58, 46 + k * 10)], 0.9, s=1, clip=trunk)
        canopy = f.poly(blobpoly(50, 22, 42, 16, n=8, amp=0.18, seed=103), 1, hl=True)
        spots(f, canopy, 50, 20, 30, 10, 7, 2.2, s=2, seed=4)
        for x, y in ((18, 42), (34, 46), (66, 46), (82, 42)):
            f.line([(x, 30), (x, y - 6)], 3)
            lantern_pod(f, x, y, 5.5, face=None)
        f.eye(45, 52, 3, "round", -1)
        f.eye(56, 52, 3, "round", -1)
        f.line([(46, 61), (50, 63), (55, 61)], 3, face=True)


# =================================================================== 104 SKULLWAIF line (gourd-helm armadillos)
def gourd(f, x, y, r, s=1, big=False):
    j = f.poly(arc(x, y, r * 1.1, r, -30, 210, 14) + [(x - r * 0.35, y - r * 1.15), (x + r * 0.35, y - r * 1.15)], s, hl=True)
    f.stroke([(x, y - r * 1.1), (x + 2, y - r * 1.5)], 1.2, 1.0, 2)
    leaf(f, x + 2, y - r * 1.4, r * 0.6, r * 0.22, -20, s=2, vein=False)
    for dx in (-0.5, 0.15):
        f.ell(x + r * dx, y + r * 0.05, r * 0.24, r * 0.26, 3, sh=0, line=False)
    if big:
        f.mark_stroke([(x - r, y - r * 0.5), (x + r, y - r * 0.55)], 1.0, s=2, clip=j)
        f.mark_stroke([(x - r, y + r * 0.6), (x + r, y + r * 0.55)], 1.0, s=2, clip=j)
    return j


@fam("SKULLWAIF", "BONEWARDEN")
def gourd_line(f, st):
    def back(f, q):
        for k in range(3):
            f.mark_stroke([(q["tx"] - 20, q["ty"] - 6 + k * 7), (q["tx"] + 20, q["ty"] - 6 + k * 7)], 1.0, s=2, clip=q["body"])
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        gourd(f, hx, hy - hr * 0.2, hr, s=1, big=st == 1)
        f.eye(hx - hr * 0.5, hy - hr * 0.15, max(2.0, hr * 0.13), "dot", -1)
        f.eye(hx + hr * 0.15, hy - hr * 0.15, max(2.0, hr * 0.13), "dot", -1)
    def flail(f, q):
        x, y = q["handpos"]
        f.stroke([(x, y + 4), (x - 2, y - 14)], 1.6, 1.6, 2)
        f.line([(x - 2, y - 14), (x - 8, y - 20), (x - 14, y - 18)], 3)
        rock(f, x - 18, y - 16, 6, 6, 3, s=1, cracks=0)
        spikes(f, arc(x - 18, y - 16, 6, 6, 0, 360, 7), 3, 2.4, s=0, side=1)
        f.ell(x, y, 3.5, 3.5, q["bs"])
    if st == 0:
        biped(f, tx=54, ty=72, trx=15, tr_y=14, hx=48, hy=46, hr=15, sn=3, legr=4, legx=5, arm="side", armr=3, eye=None,
              mouth=None, head=head, back=back, tail="thin", tl=14, trr=3, tang=10, bs=2)
    else:
        biped(f, tx=54, ty=62, trx=16, tr_y=21, hx=46, hy=32, hr=13, sn=3, legr=5, legx=6, arm="fwd", armr=3.6, eye=None,
              mouth=None, head=head, back=back, front=flail, tail="thin", tl=20, trr=3.5, tang=10, bs=2)


# =================================================================== 108 SLURPOX (pangolin)
@fam("SLURPOX")
def slurpox(f, st):
    def back(f, q):
        for r_ in range(3):
            for k in range(5):
                x = 42 + k * 9 + (r_ % 2) * 4
                y = 58 + r_ * 7
                f.mark_poly(arc(x, y, 5, 4, 0, 180, 6), 2, clip=q["body"])
                f.line(arc(x, y, 5, 4, 0, 180, 6), 3)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        x = hx - hr * 1.5
        f.stroke([(x, hy + hr * 0.4), (x - 8, hy + hr * 1.4), (x - 2, hy + hr * 2.4), (x - 10, hy + hr * 3.2)], 1.4, 1.2, 0, face=True)
    quad(f, bx=60, by=72, brx=27, bry=14, hx=30, hy=70, hr=10, hry=8, sn=12, snr=4, snd=0.3, ears=None, lr=4, tail="thin",
         tl=26, trr=6, tang=20, eye="round", eyer=2.4, back=back, head=head, neck=4, mouth=None, belly=0)


# =================================================================== 109 FUMEPUFF line (chimney toads)
@fam("FUMEPUFF", "TWINFUME")
def chimney_line(f, st):
    def pre(f, q):
        xs = (62,) if st == 0 else (54, 72)
        for k, x in enumerate(xs):
            top = 30 - k * 4
            f.poly([(x - 6, 60), (x + 6, 60), (x + 6, top), (x - 6, top)], 2)
            f.poly([(x - 8, top + 2), (x + 8, top + 2), (x + 8, top - 3), (x - 8, top - 3)], 3)
            for j, (dx, dy, r) in enumerate(((2, -8, 4), (8, -15, 5), (16, -20, 6))):
                f.ell(x + dx, top + dy, r, r * 0.8, 1, sh=0)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        for dx in (-0.5, 0.3):
            f.ell(hx + hr * dx, hy - hr * 0.7, hr * 0.32, hr * 0.32, 1, group="head")
            f.eye(hx + hr * dx, hy - hr * 0.72, hr * 0.22, "sleepy" if st == 0 else "angry", -1)
        f.line([(hx - hr * 1.0, hy + hr * 0.25), (hx + hr * 0.4, hy + hr * 0.4)], 3, face=True)
    biped(f, tx=54, ty=74, trx=24, tr_y=16, hx=36, hy=60, hr=13, hry=9, legr=5, legx=12, footl=1.6, arm="side", armr=3.5, hand=3.5,
          eye=None, mouth=None, head=head, pre=pre, belly=0, bs=1 if st == 0 else 2)


# =================================================================== 113 MEDIEGG (herbal bird in a shell helm)
@fam("MEDIEGG")
def mediegg(f, st):
    feet2(f, 40, 60, 95, 6, 2)
    f.ell(80, 66, 7, 12, 1, ang=-30)
    b = f.ell(50, 64, 28, 27, 1, hl=True)
    f.mark_ell(46, 74, 18, 15, 0, clip=b)
    zig = [(78, 54)]
    for i in range(9):
        zig.append((78 - (i + 1) * 56 / 9, 50 + (5 if i % 2 == 0 else 0)))
    f.poly(arc(50, 50, 29, 30, 180, 360, 12) + zig, 0, sh=2)
    f.line([(40, 30), (44, 38), (40, 44)], 2)
    f.poly([(24, 58), (12, 62), (24, 66)], 2)
    f.eye(34, 58, 3, "happy", -1)
    f.eye(48, 58, 3, "happy", -1)
    f.stroke([(30, 80), (14, 70)], 2.4, 2, 1)
    f.stroke([(14, 70), (8, 56)], 0.9, 0.9, 2)
    for k in range(3):
        leaf(f, 10 - k, 64 - k * 4, 8, 2.6, -150 + k * 40, s=2, vein=False)


# =================================================================== 114 VINEWAD (reed scarecrow)
@fam("VINEWAD")
def vinewad(f, st):
    f.stroke([(50, 40), (50, 97)], 2.2, 2.2, 2)
    f.stroke([(12, 46), (88, 46)], 2.6, 2.6, 2)
    for x in (12, 88):
        for k in range(3):
            f.stroke([(x, 46), (x + (-6 if x < 50 else 6), 40 + k * 6)], 1.0, 0.7, 1)
    body = f.poly([(34, 42), (66, 42), (70, 80), (30, 80)], 1)
    for k in range(6):
        f.mark_stroke([(30 + k * 7, 42), (40 + k * 7, 80)], 0.8, s=2, clip=body)
        f.mark_stroke([(40 + k * 7, 42), (30 + k * 7, 80)], 0.8, s=2, clip=body)
    spikes(f, [(30, 80), (70, 80)], 6, 5, s=1, side=1, n=6)
    h = f.ell(50, 26, 13, 13, 0, hl=False, sh=2)
    f.poly([(32, 18), (68, 18), (60, 6), (40, 6)], 2)
    f.stroke([(28, 18), (72, 18)], 1.6, 1.6, 2)
    f.eye(44, 26, 2.6, "dot", -1)
    f.eye(56, 26, 2.6, "dot", -1)
    f.line([(42, 33), (46, 31), (50, 33), (54, 31), (58, 33)], 3, face=True)


# =================================================================== 115 MARSUPRIME (wombat with backpack nest)
@fam("MARSUPRIME")
def marsuprime(f, st):
    def back(f, q):
        n = f.poly(arc(62, 52, 18, 10, 0, 180, 10) + [(80, 46), (44, 46)], 2)
        for k in range(4):
            f.mark_stroke([(44, 50 + k * 3), (80, 48 + k * 3)], 0.8, s=1, clip=n)
        f.ell(60, 42, 7, 6, 1)
        ears(f, "round", 63, 37, 4, 1)
        f.eye(57, 42, 2, "dot", -1)
        f.line([(44, 46), (34, 58)], 3)
        f.line([(80, 46), (82, 60)], 3)
    quad(f, bx=60, by=74, brx=28, bry=17, bs=2, hx=30, hy=66, hr=14, hry=12, sn=4, snr=6, ears="round", er=6, ear_in=1,
         lr=5.5, tail=None, eye="dot", eyer=2.6, back=back, neck=0, mouth="smile", belly=1)


# =================================================================== 116 REEFPONY line (sea goats)
def coral_horn(f, x, y, ln, s=0):
    f.stroke([(x, y), (x + 2, y - ln * 0.5), (x - 1, y - ln)], 1.6, 1.0, s)
    f.stroke([(x + 1.5, y - ln * 0.45), (x + ln * 0.4, y - ln * 0.75)], 1.2, 0.8, s)
    f.stroke([(x + 0.5, y - ln * 0.7), (x - ln * 0.3, y - ln * 0.95)], 1.0, 0.7, s)


def wave_horn(f, x, y, r, s=0):
    pts = [(x, y), (x + r * 0.6, y - r * 1.2), (x + r * 1.5, y - r * 1.4), (x + r * 1.9, y - r * 0.8), (x + r * 1.4, y - r * 0.4), (x + r * 1.0, y - r * 0.8)]
    f.stroke(pts, r * 0.32, r * 0.14, s)


@fam("REEFPONY", "SPINDRIFT")
def seagoat_line(f, st):
    big = st == 1
    tail_fin(f, 86, 70 - big * 4, 16 + big * 4, 22 + big * 6, ang=-40, s=1)
    f.stroke([(56, 74), (72, 82), (84, 72)], 9 + big * 2, 4, 1, group="tail")
    for k in range(3):
        f.mark_ell(66 + k * 6, 79 - k * 2, 2.2, 3, 2, clip=len(f.parts) - 1)
    for x in (36, 46):
        f.stroke([(x, 72), (x - 2, 92)], 2.8, 2.4, 1)
        f.ell(x - 3, 93, 3.4, 2.4, 3, sh=0)
    b = f.ell(50, 66, 18 + big * 3, 12, 1, hl=True)
    f.mark_ell(48, 72, 12, 5, 0, clip=b)
    f.stroke([(40, 60), (32, 46)], 6, 5, 1)
    h = f.ell(28, 40, 10, 8, 1, hl=True)
    f.ell(19, 44, 5, 4.5, 1)
    f.poly([(22, 47), (20, 56), (26, 48)], 2)
    ears(f, "point", 34, 36, 5, 1, ang=60)
    if big:
        wave_horn(f, 30, 33, 9, s=0)
        fin(f, 46, 56, 8, 18, -10, s=0, n=3)
    else:
        coral_horn(f, 30, 33, 14, s=0)
    f.eye(26, 38, 2.8, "round" if not big else "angry", -1)


# =================================================================== 118 FRILLFIN line (ribbon eels)
@fam("FRILLFIN", "REGALFIN")
def eel_line(f, st):
    big = st == 1
    path = [(96, 76), (82, 88), (66, 78), (54, 60), (40, 52), (24, 54)] if not big else \
        [(98, 90), (84, 96), (68, 86), (62, 66), (68, 48), (54, 32), (34, 30)]
    r0, r1 = (6, 2.5) if not big else (7.5, 3)
    for k in range(len(path) - 2):
        a, b = path[k], path[k + 1]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ang = math.degrees(math.atan2(dy, dx))
        for sg in (-1, 1):
            fin(f, mx + (-dy / L) * sg * r0 * 0.6, my + (dx / L) * sg * r0 * 0.6, 7 + big * 3, L * 0.9, ang + (0 if sg < 0 else 180), s=0, n=3)
    b, h = serpent(f, path, r0, r1, bs=1 if not big else 2, hr=r0 * 1.2, bands=0, eye="round" if not big else "angry", eyer=2.8, sn=3)
    if big:
        hx, hy = path[-1]
        f.poly([(hx - 6, hy - 6), (hx - 7, hy - 16), (hx - 2, hy - 10), (hx + 2, hy - 18), (hx + 4, hy - 10), (hx + 9, hy - 15), (hx + 8, hy - 5)], 0)


# =================================================================== 120 SHOALSTAR line (wheels)
@fam("SHOALSTAR", "PRISMSTAR")
def wheel_line(f, st):
    if st == 0:
        d = f.ell(52, 52, 38, 38, 1, hl=True)
        f.mark_ell(52, 52, 30, 30, 0, clip=d)
        for i in range(5):
            a = math.radians(-90 + i * 72)
            f.mark_ell(52 + math.cos(a) * 16, 52 + math.sin(a) * 16, 4, 9, 2, ang=math.degrees(a) + 90, clip=d)
        f.eye(44, 52, 3, "round", -1)
        f.eye(60, 52, 3, "round", -1)
        for y in (30, 52, 74):
            f.line([(96, y), (99, y)], 2)
    else:
        for i in range(8):
            a = math.radians(i * 45 + 10)
            x, y = 50 + math.cos(a) * 34, 50 + math.sin(a) * 34
            f.poly(rot(arc(0, 0, 10, 9, 180, 360, 8) + [(0, 8)], math.degrees(a) + 90, x, y), 1 if i % 2 else 0)
        f.ell(50, 50, 28, 28, 2)
        f.ell(50, 50, 22, 22, 3, sh=0)
        bell(f, 50, 32, 11, s=1)
        f.eye(44, 46, 2.6, "glow", -1)
        f.eye(56, 46, 2.6, "glow", -1)


# =================================================================== 122 PANTOMIX (puppeteer moth)
@fam("PANTOMIX")
def pantomix(f, st):
    moth(f, 56, 40, 34, s_w=1, s_b=2, low=0.6, body_l=22)
    antennae(f, 56, 24, 10, spread=7)
    f.ell(56, 28, 9, 8, 1)
    f.eye(53, 28, 2.6, "dot", -1)
    f.eye(60, 28, 2.4, "dot", -1)
    f.stroke([(50, 44), (30, 48)], 1.6, 1.4, 2)
    f.stroke([(18, 48), (44, 48)], 1.6, 1.6, 2)
    f.stroke([(30, 42), (30, 56)], 1.6, 1.6, 2)
    for x in (18, 30, 44):
        f.line([(x, 49), (x, 74)], 2)
    p = f.ell(30, 80, 6, 7, 0)
    f.ell(30, 70, 4.5, 4.5, 0)
    f.stroke([(26, 86), (24, 96)], 1.4, 1.2, 0)
    f.stroke([(34, 86), (36, 96)], 1.4, 1.2, 0)


# =================================================================== 123 RAZORMANT (sickle swift) / 124 FROSTDIVA (icicle heron)
@fam("RAZORMANT")
def razormant(f, st):
    f.poly([(44, 54), (56, 36), (74, 22), (96, 10), (78, 30), (62, 46), (54, 58)], 2)
    f.poly([(58, 56), (86, 48), (72, 57), (88, 66), (58, 62)], 2)
    b = f.ell(40, 57, 22, 8, 1, hl=True)
    f.mark_ell(38, 61, 15, 3.5, 0, clip=b)
    f.ell(20, 53, 8, 7, 1)
    f.poly([(13, 53), (5, 55), (13, 57)], 0)
    f.poly([(42, 58), (56, 70), (74, 82), (98, 90), (74, 74), (58, 62)], 1)
    f.eye(18, 51, 2.6, "angry", -1)


@fam("FROSTDIVA")
def frostdiva(f, st):
    for dx in (3, -3):
        f.stroke([(56 + dx, 70), (58 + dx, 84), (55 + dx, 97)], 1.4, 1.2, 3)
    cape = f.poly([(48, 30), (64, 30), (82, 86), (40, 80)], 1)
    spikes(f, [(40, 80), (82, 86)], 10, 6, s=0, side=1, n=6)
    f.mark_poly([(48, 30), (64, 30), (66, 40), (48, 40)], 0, clip=cape)
    b = f.ell(54, 54, 12, 17, 0, sh=2)
    f.stroke([(50, 40), (44, 26)], 3.2, 3, 0)
    f.ell(44, 22, 7, 6, 0, sh=2)
    f.poly([(38, 20), (10, 24), (38, 25)], 1)
    for a in (-100, -75, -50):
        horn(f, 46, 17, 10, 3, a, s=1)
    f.eye(42, 21, 2.4, "closed", -1)
    for x in (16, 84):
        f.poly(star(x, 50, 4, 1.5, n=6, ang=0), 0)


# =================================================================== 128 RAGEBULL (ram)
@fam("RAGEBULL")
def ragebull(f, st):
    def pre(f, q):
        q["wool"] = f.poly(blobpoly(62, 64, 30, 18, n=12, amp=0.12, seed=128), 0, sh=2)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        pts = []
        for i in range(16):
            t = i / 15
            a = math.radians(-150 + t * 380)
            rr = hr * 1.05 * (1 - 0.6 * t)
            pts.append((hx + 4 + math.cos(a) * rr, hy - 1 + math.sin(a) * rr))
        f.stroke(pts, 4.5, 1.6, 2)
        for p in pts[1:-2:2]:
            f.dot(p[0], p[1], 3)
    quad(f, bx=62, by=64, brx=26, bry=15, hx=30, hy=52, hr=11, sn=7, snr=5, ears=None, lr=4.5, tail="stub", trr=3,
         eye="angry", eyer=2.6, pre=pre, head=head, mouth="line", neck=7, bs=1, fs=2)


# =================================================================== 129 SPLASHLING (raindrop sprite)
@fam("SPLASHLING")
def splashling(f, st):
    for sg in (-1, 1):
        f.stroke([(50 + sg * 18, 66), (50 + sg * 28, 54), (50 + sg * 32, 44)], 2.2, 1.6, 1)
    for x in (42, 58):
        f.stroke([(x, 86), (x + (x - 50) * 0.3, 96)], 1.8, 1.6, 1)
    b = f.poly([(50, 14)] + arc(50, 66, 22, 24, -40, 220, 14), 1, hl=True)
    f.mark_ell(50, 74, 12, 10, 0, clip=b)
    for sg in (-1, 1):
        f.line([(50 + sg * 8, 66), (50 + sg * 24, 62), (50 + sg * 30, 66)], 3, face=True)
    f.eye(43, 60, 3.2, "round", -1)
    f.eye(57, 60, 3.2, "round", 1)
    f.ell(50, 70, 3.5, 3, 3, sh=0, face=True)
    for x, y in ((18, 28), (84, 24), (88, 40)):
        f.poly([(x, y - 5)] + arc(x, y, 2.6, 2.6, -30, 210, 6), 0)


# =================================================================== 130 TEMPESTEEL (thundercloud ray) / 131 SEAFERRY (garden manatee)
@fam("TEMPESTEEL")
def tempesteel(f, st):
    pts = [(60, 66), (76, 80), (80, 86), (88, 84), (84, 94), (94, 96)]
    f.stroke(pts[:2], 2.4, 2.0, 2)
    f.poly([(74, 76), (86, 80), (80, 84), (92, 90), (78, 88), (82, 84)], 1)
    ray = f.poly([(10, 54), (40, 36), (56, 38), (92, 48), (60, 62), (44, 70), (30, 66)], 2, hl=True)
    for x, y, r in ((34, 38, 7), (46, 32, 8), (58, 34, 7), (70, 40, 6)):
        f.ell(x, y, r, r * 0.8, 1, sh=0)
    f.eye(34, 52, 3, "angry", -1)
    f.eye(46, 51, 2.8, "angry", -1)
    f.line([(30, 58), (40, 60)], 3, face=True)
    spark(f, 14, 26, 5)
    spark(f, 88, 24, 5)


@fam("SEAFERRY")
def seaferry(f, st):
    f.poly([(80, 76), (98, 66), (96, 88)], 1)
    b = f.ell(54, 76, 34, 15, 1, hl=True)
    f.mark_ell(50, 84, 24, 6, 0, clip=b)
    f.poly([(28, 80), (20, 94), (34, 88)], 1)
    raft = f.poly([(30, 62), (80, 62), (82, 54), (28, 54)], 2)
    for x in (38, 48, 58, 68, 78):
        f.line([(x, 54), (x, 62)], 3)
    for x, k in ((36, 0), (50, 1), (66, 2), (76, 3)):
        f.stroke([(x, 54), (x, 44)], 0.9, 0.9, 2)
        if k % 2:
            f.poly(star(x, 40, 5, 2.4, n=5), 0)
            f.ell(x, 40, 1.6, 1.6, 2, line=False, sh=0)
        else:
            leaf(f, x, 46, 9, 3, -60, s=1, vein=False)
            leaf(f, x, 48, 8, 3, 220, s=1, vein=False)
    h = f.ell(20, 72, 12, 10, 1)
    f.ell(11, 76, 5, 4, 1)
    f.eye(17, 69, 2.6, "sleepy", -1)
    for k in range(3):
        f.dot(9 + k * 2, 77, 3, face=True)


# =================================================================== 132 COPYGOO (mirror beetle)
@fam("COPYGOO")
def copygoo(f, st):
    for i in range(3):
        x = 44 + i * 12
        f.stroke([(x, 80), (x - 4, 88), (x - 2, 96)], 1.5, 1.2, 3)
    sh_ = f.ell(56, 64, 30, 22, 0, sh=2)
    for k in range(3):
        f.mark_stroke([(38 + k * 9, 76), (54 + k * 9, 48)], 1.4 if k != 1 else 2.4, s=1, clip=sh_)
    f.line([(56, 42), (56, 86)], 3)
    f.ell(24, 72, 10, 9, 1)
    antennae(f, 22, 64, 10, spread=6, curl=False)
    f.eye(20, 70, 2.6, "round", -1)
    f.eye(28, 70, 2.4, "round", -1)
    f.poly(star(66, 52, 5, 1.8, n=4), 0)


# =================================================================== 133 MORPHKIT family (otters)
def otter(f, kind):
    kit = kind == "kit"
    def pre(f, q):
        if kind == "fin":
            fin(f, 62, 56, 12, 26, -5, s=0, n=4)
        elif kind == "ash":
            spots(f, q["body"], q["bx"], q["by"], q["brx"] * 0.7, q["bry"] * 0.6, 6, 2.0, s=1, seed=136) if "body" in q else None
    def back(f, q):
        if kind == "ash":
            spots(f, q["body"], q["bx"], q["by"], q["brx"] * 0.7, q["bry"] * 0.6, 6, 2.2, s=1, seed=136)
        if kind == "static":
            spikes(f, arc(q["bx"], q["by"], q["brx"], q["bry"], 200, 340, 6), 6, 5, s=q["bs"], side=1)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        wx = hx - hr * 1.2
        if kind == "static":
            for dy, a in ((-1, -150), (2, -170)):
                f.line([(wx, hy + hr * 0.3 + dy), (wx - 8, hy + hr * 0.3 + dy - 8 * (1 if a == -150 else 0.3)), (wx - 10, hy - 4 + dy * 3)], 3)
            spark(f, wx - 12, hy - 8, 3)
        else:
            f.line([(wx, hy + hr * 0.3), (wx - 6, hy + hr * 0.15)], 3, face=True)
            f.line([(wx, hy + hr * 0.45), (wx - 6, hy + hr * 0.6)], 3, face=True)
        if kind == "fin":
            fin(f, hx + 2, hy - hr * 0.6, 8, 10, 10, s=0, n=2)
        f.mark_ell(hx - hr * 0.5, hy + hr * 0.45, hr * 0.55, hr * 0.4, 0, clip=q["headid"])
    tails = {"kit": ("thin", 22, 4.5, None), "fin": ("thin", 24, 5.5, None), "static": ("bolt", 22, 4, 1), "ash": ("flame", 22, 4.5, 0)}
    tk, tl, tr, tip = tails[kind]
    quad(f, bx=58, by=76 if kit else 72, brx=24 if kit else 30, bry=11 if kit else 12, hx=28 if kit else 22, hy=64 if kit else 58,
         hr=12 if kit else 11, hry=10 if kit else 9, sn=4, snr=5, ears="round", er=5, ear_in=None, lr=3.2 if kit else 3.8,
         tail=tk, tl=tl, trr=tr, tang=-5, ttip=tip, eye="round" if kit else "dot", eyer=2.8, pre=pre, back=back, head=head,
         neck=6, bs=2 if kind == "ash" else 1, belly=0 if kind != "ash" else None, mouth="smile")


@fam("MORPHKIT")
def morphkit(f, st):
    otter(f, "kit")


@fam("TIDEMANE")
def tidemane(f, st):
    otter(f, "fin")


@fam("SPARKMANE")
def sparkmane(f, st):
    otter(f, "static")


@fam("FLAREMANE")
def flaremane(f, st):
    otter(f, "ash")


# =================================================================== 137 POLYGRID (paper crane)
@fam("POLYGRID")
def polygrid(f, st):
    f.ell(50, 94, 26, 3, 2)
    f.poly([(68, 62), (96, 48), (84, 68)], 2)
    f.poly([(50, 60), (82, 10), (72, 62)], 2)
    f.poly([(24, 64), (50, 54), (78, 62), (52, 76)], 1)
    f.line([(50, 54), (52, 76)], 2)
    f.stroke([(30, 62), (22, 44), (18, 34)], 3.2, 2.6, 1)
    f.poly([(14, 30), (2, 38), (22, 38)], 1)
    f.poly([(38, 62), (44, 14), (64, 60)], 0, sh=2)
    f.line([(44, 16), (52, 60)], 2)
    f.eye(15, 34, 1.8, "dot", -1)


# =================================================================== 138 AMMONIX line (pinecone armadillos)
def cone_scales(f, q, rows=3, cols=5):
    bx, by, brx, bry = q["bx"], q["by"], q["brx"], q["bry"]
    for r_ in range(rows):
        for k in range(cols):
            x = bx - brx * 0.7 + k * brx * 1.4 / (cols - 1) + (r_ % 2) * 3
            y = by - bry * 0.6 + r_ * bry * 0.5
            f.poly([(x - 4, y), (x, y - 5), (x + 4, y), (x, y + 2)], 2 if (r_ + k) % 2 else 1)


@fam("AMMONIX", "AMMOLORD")
def pinecone_line(f, st):
    big = st == 1
    def back(f, q):
        cone_scales(f, q, rows=3 + big, cols=5 + big)
    quad(f, bx=60, by=72 if not big else 66, brx=24 if not big else 28, bry=16 if not big else 19, hx=32 if not big else 28,
         hy=72 if not big else 64, hr=10 if not big else 11, hry=8 if not big else 9, sn=8, snr=4, snd=0.4, ears="point", er=5,
         lr=4 if not big else 5.5, tail="club" if big else "stub", tl=22, trr=3, tang=-20, eye="round" if not big else "angry",
         eyer=2.4, back=back, neck=5, mouth=None, bs=1)


# =================================================================== 140 TRILOBYTE / 141 SICKLOBYTE (stone moths)
def stone_larva(f):
    for i in range(5):
        x = 82 - i * 12
        f.poly([(x - 7, 92), (x - 6, 72 - i), (x + 6, 70 - i), (x + 7, 92)], 1 if i % 2 else 2)
        f.line([(x - 6, 80), (x + 6, 79)], 2)
    f.ell(22, 78, 12, 13, 1, hl=True)
    for x in (18, 26):
        f.eye(x, 76, 2.8, "glow", -1)
    for x in (30, 50, 70):
        f.stroke([(x, 92), (x - 2, 97)], 1.4, 1.2, 3)


def slate_moth(f, eyes=True):
    for sg in (-1, 1):
        f.poly([(50, 48), (50 + sg * 46, 22), (50 + sg * 40, 46), (50 + sg * 44, 58), (50 + sg * 8, 58)], 2)
        f.line([(50 + sg * 10, 50), (50 + sg * 36, 32), (50 + sg * 38, 44)], 3)
        f.poly([(50, 58), (50 + sg * 30, 70), (50 + sg * 22, 86), (50 + sg * 6, 74)], 1)
    b = f.ell(50, 64, 7, 20, 1)
    for k in range(3):
        f.mark_stroke([(42, 60 + k * 7), (58, 60 + k * 7)], 0.9, s=2, clip=b)
    f.ell(50, 42, 8, 7, 1)
    antennae(f, 50, 36, 12, spread=8, feather=True)
    for sg in (-1, 1):
        f.poly(arc(50 + sg * 14, 40, 12, 10, 90 - sg * 90 - 40, 90 - sg * 90 + 40, 6) + [(50 + sg * 6, 46)], 0)
    if eyes:
        f.eye(46, 42, 2.6, "angry", -1)
        f.eye(54, 42, 2.6, "angry", 1)


@fam("TRILOBYTE")
def trilobyte(f, st):
    stone_larva(f)


@fam("SICKLOBYTE")
def sicklobyte(f, st):
    slate_moth(f)


# =================================================================== 142 PTEROFANG (better wings)
def ptero(f, s=2, eyes=True):
    far = [(56, 46), (66, 20), (80, 6), (92, 4), (88, 18), (90, 28), (82, 30), (82, 40), (72, 42), (64, 52)]
    f.poly(far, 2 if s == 2 else 1)
    f.stroke([(62, 58), (84, 68), (96, 64)], 2.6, 1.2, s)
    f.poly([(92, 60), (100, 62), (94, 68)], s)
    for x in (54, 62):
        f.stroke([(x, 62), (x, 76), (x - 3, 84)], 1.6, 1.3, 3)
    f.ell(58, 54, 11, 8, s)
    f.stroke([(50, 50), (40, 38)], 4.2, 3.8, s)
    f.poly([(12, 36), (30, 28), (46, 30), (48, 38), (38, 42), (12, 42)], s)
    horn(f, 44, 32, 14, 6, -15, s=s)
    fang(f, 20, 41, 5, 3)
    fang(f, 27, 41, 4, 3)
    f.line([(13, 40), (40, 40)], 3, face=True)
    if eyes:
        f.eye(34, 33, 3, "angry", -1)
    near = [(52, 50), (40, 30), (24, 14), (12, 10), (16, 20), (10, 26), (20, 30), (16, 38), (30, 40), (46, 58)]
    f.poly(near, 1 if s == 2 else 2)
    f.line([(50, 50), (24, 16)], 3)
    f.line([(46, 48), (18, 26)], 2)


@fam("PTEROFANG")
def pterofang(f, st):
    ptero(f)


# =================================================================== 143 SLUMBERUS (mossy hill-tortoise)
@fam("SLUMBERUS")
def slumberus(f, st):
    for x in (22, 46, 72):
        f.stroke([(x, 82), (x - 2, 95)], 6, 6, 1)
        f.ell(x - 4, 95, 8, 3, 1)
    sh_ = f.poly(arc(54, 82, 42, 46, 180, 360, 18) + [(96, 84), (12, 84)], 2, hl=True)
    for x, y in ((40, 54), (56, 46), (70, 58), (52, 68), (30, 70), (78, 74)):
        f.mark_poly([(x - 7, y), (x - 3, y - 6), (x + 4, y - 6), (x + 7, y), (x + 4, y + 6), (x - 3, y + 6)], 1, clip=sh_)
    for x, y, r in ((40, 40, 9), (58, 34, 11), (74, 44, 8)):
        f.stroke([(x, y + r), (x, y + r + 4)], 1.2, 1.2, 2)
        b = f.poly(blobpoly(x, y, r, r * 0.8, n=6, amp=0.2, seed=x), 1)
        spots(f, b, x, y, r * 0.5, r * 0.4, 3, 1.4, s=0, seed=y)
    f.stroke([(18, 80), (8, 70)], 6, 6, 1)
    f.ell(6, 64, 10, 8, 1, hl=True)
    f.eye(3, 62, 2.6, "closed", -1)
    for x, y, r in ((18, 40, 3), (24, 30, 4)):
        f.line([(x - r, y - r), (x + r, y - r), (x - r, y + r), (x + r, y + r)], 3)


# =================================================================== 150 OMNIGENE (three-eyed lab crystal)
@fam("OMNIGENE")
def omnigene(f, st):
    f.ell(50, 96, 20, 3, 2)
    c = f.poly([(50, 4), (70, 26), (66, 76), (50, 90), (34, 76), (30, 26)], 1)
    f.mark_poly([(50, 4), (50, 90), (34, 76), (30, 26)], 0, clip=c)
    f.mark_poly([(50, 4), (70, 26), (58, 30), (50, 22)], 2, clip=c)
    f.line([(30, 26), (50, 22), (70, 26)], 2)
    f.line([(50, 22), (50, 90)], 2)
    for y in (40, 62):
        r = f.poly([(22, y - 3), (78, y - 3), (78, y + 3), (22, y + 3)], 2)
        for x in (24, 76):
            f.ell(x, y, 3, 3, 1)
    for x, y in ((42, 32), (58, 32), (50, 52)):
        f.eye(x, y, 3, "slit", -1)
    for x, y in ((14, 20), (86, 30), (12, 76)):
        spark(f, x, y, 3.5)
