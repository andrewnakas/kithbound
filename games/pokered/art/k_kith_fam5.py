"""KITHBOUND families, part 5 (national 102-151) and the fossil displays."""
import math

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_fam import fam, spark
from games.pokered.art.k_kith_fam3 import feet2, fuzzball, note, quills, mushroom
from games.pokered.art.k_kith_fam4 import claw, rock
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, cog, fang, fin,
                                          flame, horn, leaf, rot, spikes, spiral, spots, star, stripes,
                                          tail_fin)


# =================================================================== 102 PODCLUSTER line
def pod(f, x, y, r, eye="dot", s=1, crack=True):
    p = f.poly([(x, y - r * 1.25)] + arc(x, y, r, r, -40, 220, 12), s, hl=True)
    if crack:
        f.line([(x - r * 0.6, y - r * 0.5), (x - r * 0.2, y - r * 0.2), (x + r * 0.2, y - r * 0.6)], 2)
    f.eye(x - r * 0.35, y + r * 0.1, max(2.0, r * 0.22), eye, -1)
    f.eye(x + r * 0.3, y + r * 0.1, max(2.0, r * 0.22), eye, -1)
    return p


@fam("PODCLUSTER", "PALMHEADS")
def pod_line(f, st):
    if st == 0:
        for k, (x, y, r) in enumerate(((22, 80, 12), (48, 84, 12), (74, 80, 12), (34, 60, 12), (62, 60, 12), (48, 38, 12))):
            pod(f, x, y, r, eye="dot" if k % 2 else "round")
    else:
        for x in (40, 60):
            f.stroke([(x, 76), (x - 4, 96)], 4, 4, 2)
            f.ell(x - 7, 96, 7, 3, 2)
        trunk = f.poly([(36, 40), (64, 40), (66, 80), (34, 80)], 1)
        for k in range(4):
            f.mark_stroke([(34, 48 + k * 9), (66, 46 + k * 9)], 1.0, s=2, clip=trunk)
        for a in (-170, -135, -100, -70, -40, -5):
            leaf(f, 50, 26, 34, 8, a, s=2)
        for x, y in ((30, 30), (50, 22), (70, 30)):
            pod(f, x, y, 10, eye="angry", s=1, crack=False)


# =================================================================== 104 SKULLWAIF line
def skull_helm(f, hx, hy, hr, big=False):
    h = f.poly(arc(hx, hy - hr * 0.1, hr * 1.1, hr * 1.05, 160, 380, 14) + [(hx + hr * 0.9, hy + hr * 0.3), (hx - hr * 1.15, hy + hr * 0.3)], 0)
    f.ell(hx - hr * 0.55, hy - hr * 0.1, hr * 0.3, hr * 0.3, 3, sh=0, line=False)
    f.ell(hx + hr * 0.2, hy - hr * 0.1, hr * 0.28, hr * 0.3, 3, sh=0, line=False)
    if big:
        horn(f, hx + hr * 0.4, hy - hr * 0.9, hr * 0.9, hr * 0.5, -60, curve=-0.5, s=0)
    return h


@fam("SKULLWAIF", "BONEWARDEN")
def skull_line(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        skull_helm(f, hx, hy - hr * 0.25, hr, big=st == 1)
        f.eye(hx - hr * 0.55, hy - hr * 0.3, max(2.0, hr * 0.15), "dot", -1)
        f.eye(hx + hr * 0.2, hy - hr * 0.3, max(2.0, hr * 0.15), "dot", -1)
    def bone(f, q):
        x, y = q["handpos"]
        ln = 20 if st == 0 else 34
        f.stroke([(x - 2, y + ln * 0.4), (x + 2, y - ln * 0.6)], 1.8, 1.8, 0)
        for (bx, by) in ((x - 2, y + ln * 0.4), (x + 2, y - ln * 0.6)):
            f.ell(bx - 2, by, 2.4, 2.4, 0)
            f.ell(bx + 2, by, 2.4, 2.4, 0)
        f.ell(x, y, 3.5, 3.5, q["bs"])
    if st == 0:
        biped(f, tx=54, ty=72, trx=14, tr_y=15, hx=48, hy=46, hr=15, sn=2, legr=4, legx=5, arm="fwd", armr=3, eye=None,
              mouth=None, head=head, front=bone, belly=0, tail="stub", trr=3, bs=1)
    else:
        biped(f, tx=54, ty=62, trx=15, tr_y=21, hx=46, hy=32, hr=13, sn=3, legr=5, legx=6, arm="fwd", armr=3.6, eye=None,
              mouth=None, head=head, front=bone, belly=0, tail="thin", tl=20, trr=3, tang=10, bs=2)


# =================================================================== 106 KICKSTER / 107 JABBERFIST
@fam("KICKSTER")
def kickster(f, st):
    f.stroke([(56, 64), (66, 80), (62, 96)], 4, 3.5, 2)
    f.ell(58, 96, 7, 3, 2)
    f.stroke([(48, 64), (30, 66), (10, 58)], 4.5, 4, 1)
    f.ell(8, 56, 5, 7, 1, ang=-20)
    t = f.ell(52, 50, 14, 18, 1, hl=True)
    f.mark_stroke([(38, 58), (66, 58)], 2, s=3, clip=t)
    f.stroke([(56, 40), (68, 52), (74, 44)], 2.6, 2.4, 1)
    f.ell(48, 26, 11, 10, 1)
    f.eye(44, 26, 2.8, "angry", -1)
    f.eye(51, 25, 2.6, "angry", -1)
    f.mark_stroke([(36, 20), (60, 18)], 2.2, s=2)
    f.stroke([(58, 18), (70, 16), (78, 22)], 1.5, 1.0, 2)
    f.stroke([(44, 40), (34, 44), (30, 36)], 2.6, 2.4, 1)


@fam("JABBERFIST")
def jabber(f, st):
    def front(f, q):
        for (x, y) in (q["farhand"], q["handpos"]):
            g = f.ell(x - 2, y - 2, 9, 8, 0, hl=False)
            f.line([(x - 6, y + 2), (x + 2, y + 4)], 2)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.mark_poly([(hx - hr, hy - hr * 0.5), (hx + hr, hy - hr * 0.7), (hx + hr, hy - hr * 0.2), (hx - hr, hy - hr * 0.1)], 2, clip=q["headid"])
    biped(f, tx=56, ty=62, trx=14, tr_y=20, hx=50, hy=30, hr=12, legr=5, legx=6, arm="guard", armr=3.5, eye="angry", eyer=2.8,
          mouth="line", head=head, front=front, belly=None, bs=1, fs=2)


# =================================================================== 108 SLURPOX
@fam("SLURPOX")
def slurpox(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.stroke([(hx - hr * 0.6, hy + hr * 0.5), (hx - hr * 1.4, hy + hr * 1.3), (hx - hr * 1.2, hy + hr * 2.6), (hx - hr * 0.4, hy + hr * 3.0)],
                 hr * 0.32, hr * 0.38, 0, face=True)
        f.line([(hx - hr * 1.2, hy + hr * 1.4), (hx - hr * 1.1, hy + hr * 2.4)], 2, face=True)
    biped(f, tx=54, ty=64, trx=22, tr_y=24, hx=48, hy=32, hr=14, legr=6.5, legx=9, arm="side", armr=4, hand=4, eye="round",
          eyer=3, mouth=None, head=head, belly=0, tail="thin", tl=22, trr=3.5, tang=0, bs=1)


# =================================================================== 109 FUMEPUFF line
def smokeball(f, cx, cy, r, s=2, eye="round", grin=False, seed=1):
    b = f.poly(blobpoly(cx, cy, r, r, n=8, amp=0.08, seed=seed), s, hl=True)
    for a in (-60, 30, 160):
        x, y = cx + math.cos(math.radians(a)) * r * 0.75, cy + math.sin(math.radians(a)) * r * 0.75
        f.ell(x, y, r * 0.16, r * 0.12, 3, sh=0, line=False)
        f.ell(x + math.cos(math.radians(a)) * r * 0.45, y + math.sin(math.radians(a)) * r * 0.45 - 2, r * 0.18, r * 0.14, 1, sh=0)
    f.eye(cx - r * 0.35, cy - r * 0.15, r * 0.18, eye, -1)
    f.eye(cx + r * 0.2, cy - r * 0.15, r * 0.18, eye, -1)
    if grin:
        f.line([(cx - r * 0.45, cy + r * 0.3), (cx - r * 0.1, cy + r * 0.45), (cx + r * 0.3, cy + r * 0.3)], 3, face=True)
    else:
        f.ell(cx - r * 0.1, cy + r * 0.38, r * 0.14, r * 0.1, 3, sh=0, line=False, face=True)
    return b


@fam("FUMEPUFF", "TWINFUME")
def fume_line(f, st):
    if st == 0:
        smokeball(f, 50, 58, 34, s=2)
    else:
        f.stroke([(68, 34), (40, 66)], 6, 6, 2)
        smokeball(f, 70, 34, 24, s=2, eye="angry", grin=True, seed=2)
        smokeball(f, 38, 66, 30, s=2, eye="angry", grin=True, seed=3)


# =================================================================== 111 HORNBUCK line
@fam("HORNBUCK", "DRILLBUCK")
def buck_line(f, st):
    if st == 0:
        def back(f, q):
            for k in range(3):
                x = 46 + k * 12
                f.mark_poly([(x, 56), (x + 11, 56), (x + 10, 70), (x + 1, 70)], 2, clip=q["body"])
            spikes(f, [(42, 57), (82, 60)], 6, 6, s=2, side=-1)
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            horn(f, hx - hr * 1.3, hy - hr * 0.2, 14, 6, -110, curve=-0.3, s=0)
            f.mark_poly([(hx - hr, hy - hr * 0.9), (hx + hr, hy - hr * 0.9), (hx + hr, hy - hr * 0.3), (hx - hr, hy - hr * 0.2)], 2, clip=q["headid"])
        quad(f, bx=62, by=70, brx=24, bry=14, hx=32, hy=64, hr=12, sn=9, snr=6, ears="point", er=6, lr=6, tail="thin", tl=10, trr=2,
             tang=-10, eye="angry", eyer=2.6, back=back, head=head, neck=6, mouth="line")
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            x, y = hx - hr * 1.5, hy - hr * 0.2
            d = horn(f, x, y, 20, 10, -115, s=0)
            for k in range(3):
                t = 0.2 + k * 0.25
                f.line([(x + math.cos(math.radians(-115)) * 20 * t - 4 * (1 - t), y + math.sin(math.radians(-115)) * 20 * t + 1),
                        (x + math.cos(math.radians(-115)) * 20 * t + 4 * (1 - t), y + math.sin(math.radians(-115)) * 20 * t - 2)], 2)
        def back(f, q):
            for k in range(3):
                f.mark_stroke([(q["tx"] - 14, q["ty"] - 8 + k * 8), (q["tx"] + 14, q["ty"] - 8 + k * 8)], 1.0, s=2, clip=q["body"])
        biped(f, tx=56, ty=62, trx=19, tr_y=22, hx=42, hy=32, hr=12, sn=8, snr=6, legr=7, legx=8, arm="guard", armr=4.5, hand=4.5,
              ears="point", er=6, tail="thin", tl=24, trr=4, tang=20, eye="angry", eyer=2.6, head=head, back=back, mouth="line", bs=2, belly=1)


# =================================================================== 113 MEDIEGG
@fam("MEDIEGG")
def mediegg(f, st):
    feet2(f, 36, 62, 95, 7, 1)
    for x, a in ((18, -30), (82, 30)):
        f.ell(x, 60, 7, 10, 1, ang=a)
    b = f.poly(arc(50, 64, 32, 32, -10, 190, 14) + [(18, 50), (30, 22), (50, 12), (70, 22), (82, 50)], 1, hl=True)
    f.mark_poly([(18, 64), (82, 64), (80, 80), (20, 80)], 0, clip=b)
    f.poly([(42, 70), (58, 70), (58, 66), (62, 70), (58, 74), (58, 78), (42, 78), (42, 74), (38, 70), (42, 66)], 2)
    h = f.poly([(40, 12), (60, 12), (58, 4), (42, 4)], 0)
    f.line([(48, 6), (52, 6)], 2)
    f.line([(50, 4), (50, 9)], 2)
    f.eye(40, 40, 3, "happy", -1)
    f.eye(58, 40, 3, "happy", -1)
    f.line([(45, 52), (50, 55), (55, 52)], 3, face=True)


# =================================================================== 114 VINEWAD
@fam("VINEWAD")
def vinewad(f, st):
    for x in (36, 64):
        f.ell(x, 94, 8, 4, 2)
    b = f.ell(50, 58, 36, 34, 2)
    import random
    rng = random.Random(114)
    for k in range(14):
        a = rng.uniform(0, math.tau)
        x, y = 50 + math.cos(a) * 26, 58 + math.sin(a) * 24
        f.line([(x, y), (x + rng.uniform(-14, 14), y + rng.uniform(-10, 10)), (50 + rng.uniform(-20, 20), 58 + rng.uniform(-20, 20))], 1)
    for a in range(0, 360, 40):
        leaf(f, 50 + math.cos(math.radians(a)) * 34, 58 + math.sin(math.radians(a)) * 32, 9, 3, a, s=1, vein=False)
    f.ell(42, 48, 14, 8, 3, sh=0, line=False)
    f.eye(37, 48, 3.2, "round", -1)
    f.eye(49, 48, 3.2, "round", -1)


# =================================================================== 115 MARSUPRIME
@fam("MARSUPRIME")
def marsu(f, st):
    def back(f, q):
        p = f.ell(q["tx"] - 4, q["ty"] + 8, 12, 9, 0)
        f.line([(q["tx"] - 16, q["ty"] + 4), (q["tx"] + 8, q["ty"] + 4)], 3)
        f.ell(q["tx"] - 8, q["ty"] + 0, 5, 4.5, 1)
        f.eye(q["tx"] - 9, q["ty"] - 0.5, 1.8, "dot", -1)
        f.ell(q["tx"] - 13, q["ty"] - 5, 1.6, 3, 1)
    biped(f, tx=54, ty=64, trx=20, tr_y=24, hx=44, hy=30, hr=13, sn=8, snr=5, legr=6, legx=8, footl=1.6, arm="side", armr=4,
          ears="long", er=10, ear_in=2, tail="bushy", tl=30, trr=7, tang=20, eye="dot", eyer=2.8, back=back, mouth="smile", bs=2, hs=2, as_=2, fs=2)


# =================================================================== 116 REEFPONY line
def seahorse(f, st):
    spiny = st == 1
    f.stroke([(58, 72), (62, 86), (72, 93), (80, 86), (74, 79), (69, 84)], 5 + spiny, 1.8, 1)
    fin(f, 68, 52, 10 + spiny * 4, 12, 75, s=0, n=3)
    body = [(48, 30), (62, 34), (69, 48), (67, 64), (58, 78), (46, 76), (38, 64), (40, 46)]
    b = f.poly(body, 1, hl=True)
    f.mark_poly([(38, 64), (40, 46), (46, 44), (50, 74), (46, 76)], 0, clip=b)
    for k in range(4):
        y = 50 + k * 6
        f.line([(40, y), (47, y + 1)], 2)
    if spiny:
        spikes(f, [(62, 34), (69, 48), (67, 64), (58, 78)], 6, 5, s=0, side=-1)
    f.stroke([(40, 30), (24, 33)], 3.2, 2.8, 1, group="head")
    f.ell(46, 26, 10, 8, 1, group="head")
    if spiny:
        for a_ in (-120, -90, -60, -30):
            horn(f, 50, 20, 11, 4, a_, s=0)
    else:
        fin(f, 52, 20, 7, 8, 20, s=0, n=2)
    f.eye(44, 25, 3, "angry" if spiny else "round", -1)
    f.dot(22, 33, 3, face=True)


@fam("REEFPONY", "SPINDRIFT")
def reef_line(f, st):
    seahorse(f, st)


# =================================================================== 118 FRILLFIN line
@fam("FRILLFIN", "REGALFIN")
def frill_line(f, st):
    big = st == 1
    tail_fin(f, 70, 60, 26 + big * 4, 34 + big * 6, ang=0, s=1, fork=0.5)
    fin(f, 54, 40, 14 + big * 4, 22, -10, s=2 if big else 1, n=4)
    f.poly([(52, 76), (62, 92), (66, 74)], 2)
    b = f.ell(48, 58, 28, 20, 1 if not big else 2, hl=True)
    if big:
        f.mark_ell(44, 66, 20, 9, 0, clip=b)
        f.poly([(26, 42), (28, 30), (34, 38), (40, 28), (44, 38), (50, 30), (50, 44)], 0)
    else:
        stripes(f, b, 40, 58, 64, 58, 3, 2.4, s=2, ang=90, ln=40)
    horn(f, 22, 50, 16 + big * 6, 5, 200, s=0)
    f.poly([(36, 62), (40, 72), (48, 66)], 0)
    f.eye(30, 54, 3.4, "round" if not big else "angry", -1)
    f.line([(21, 60), (26, 62)], 3, face=True)


# =================================================================== 120 SHOALSTAR line
@fam("SHOALSTAR", "PRISMSTAR")
def star_line(f, st):
    if st == 0:
        s_ = f.poly(star(50, 58, 40, 15, n=5, ang=-90), 1, hl=True)
        f.ell(50, 58, 9, 9, 0)
        f.poly(star(50, 58, 6, 3, n=4, ang=-90), 2, line=False)
        spots(f, s_, 50, 58, 30, 30, 8, 1.6, s=2, seed=12)
    else:
        f.poly(star(50, 54, 44, 16, n=5, ang=-54), 2)
        s_ = f.poly(star(50, 54, 40, 15, n=5, ang=-90), 1, hl=True)
        f.poly([(50, 40), (62, 54), (50, 68), (38, 54)], 0)
        f.line([(50, 40), (50, 68)], 2)
        f.line([(38, 54), (62, 54)], 2)


# =================================================================== 122 PANTOMIX
@fam("PANTOMIX")
def pantomix(f, st):
    def front(f, q):
        for x, y in ((14, 50), (28, 20)):
            f.poly([(x - 9, y - 9), (x + 9, y - 9), (x + 9, y + 9), (x - 9, y + 9)], 0, line=True, sh=0)
        f.ell(22, 44, 5, 5, 0)
        f.ell(32, 26, 5, 5, 0)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        for dx in (-0.6, 0.6):
            f.ell(hx + hr * dx, hy - hr * 0.95, 4, 4, 2)
        f.mark_ell(hx - hr * 0.3, hy + hr * 0.4, 3.5, 2.2, 2, clip=q["headid"])
    biped(f, tx=54, ty=62, trx=14, tr_y=18, hx=50, hy=32, hr=13, legr=4, legx=6, footl=1.4, arm="up", armr=3, eye="dot", eyer=2.8,
          mouth="smile", head=head, front=front, belly=2, bs=1, fs=2)


# =================================================================== 123 RAZORMANT
@fam("RAZORMANT")
def razormant(f, st):
    bug_wing(f, 60, 46, 34, 12, -30, s=0, veins=2)
    for k in range(2):
        x = 58 + k * 10
        f.stroke([(x, 62), (x + 6, 80), (x + 2, 96)], 1.8, 1.4, 1)
    ab = f.ell(74, 60, 16, 9, 1, ang=20)
    stripes(f, ab, 66, 56, 84, 64, 3, 1.2, s=2, ang=110, ln=24)
    th = f.ell(52, 50, 8, 14, 1)
    f.stroke([(48, 36), (40, 24)], 4, 3.5, 1)
    f.ell(38, 20, 10, 8, 1)
    for d in (0, 5):
        f.line([(36 + d, 13), (32 + d, 4), (24 + d, 2)], 3)
    for y0 in (44, 52):
        f.stroke([(48, y0), (34, y0 + 4)], 2.5, 2.2, 1)
        f.poly(arc(34, y0 - 8, 18, 14, 100, 200, 8) + [(20, y0 - 6), (33, y0 + 2)], 0)
    f.eye(34, 18, 3.4, "angry", -1)


# =================================================================== 124 FROSTDIVA
@fam("FROSTDIVA")
def frostdiva(f, st):
    gown = f.poly([(40, 44), (60, 44), (76, 96), (24, 96)], 1)
    f.mark_poly([(40, 44), (60, 44), (62, 58), (38, 58)], 2, clip=gown)
    spikes(f, [(24, 96), (76, 96)], 6, 6, s=1, side=1, n=6)
    for k in range(3):
        f.poly(star(36 + k * 14, 78, 4, 1.5, n=6, ang=0), 0)
    for sg in (-1, 1):
        f.stroke([(50 + sg * 8, 48), (50 + sg * 22, 58), (50 + sg * 28, 44)], 2.6, 2.2, 1)
    h = f.ell(50, 30, 13, 13, 1)
    f.poly([(34, 30), (40, 12), (50, 8), (62, 12), (68, 30), (64, 40), (60, 26), (40, 26), (36, 40)], 0)
    f.eye(44, 32, 3, "closed", -1)
    f.eye(56, 32, 3, "closed", -1)
    f.ell(50, 38, 3, 2, 3, line=False, sh=0, face=True)
    note(f, 80, 24, 3)


# =================================================================== 125 VOLTBRUTE / 126 LAVABRUTE
@fam("VOLTBRUTE")
def voltbrute(f, st):
    def back(f, q):
        for k in range(4):
            y = q["ty"] - 14 + k * 8
            f.mark_poly([(q["tx"] - 22, y), (q["tx"] + 22, y - 3), (q["tx"] + 22, y), (q["tx"] - 22, y + 3)], 3, clip=q["body"])
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        for dx in (-0.5, 0.4):
            f.poly([(hx + hr * dx - 2, hy - hr * 0.8), (hx + hr * dx + 3, hy - hr * 1.7), (hx + hr * dx + 1, hy - hr * 1.1), (hx + hr * dx + 5, hy - hr * 1.5), (hx + hr * dx + 3, hy - hr * 0.6)], 1)
    def front(f, q):
        spark(f, q["handpos"][0] - 6, q["handpos"][1] - 6, 5)
    biped(f, tx=54, ty=62, trx=21, tr_y=23, hx=46, hy=30, hr=12, legr=6.5, legx=8, arm="guard", armr=5, hand=5, eye="angry", eyer=2.6,
          mouth="open", fangs=1, back=back, head=head, front=front, bs=1, tail="bolt", tl=18, trr=3, tang=-10, ttip=1)


@fam("LAVABRUTE")
def lavabrute(f, st):
    def back(f, q):
        spots(f, q["body"], q["tx"], q["ty"], q["trx"] * 0.7, q["tr_y"] * 0.7, 7, 3.2, s=0, seed=126)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        flame(f, hx + 2, hy - hr * 0.7, 16, 18, ang=10, n=3, s=0)
    def pre(f, q):
        pass
    biped(f, tx=54, ty=62, trx=20, tr_y=22, hx=46, hy=32, hr=12, sn=5, legr=6.5, legx=8, arm="fwd", armr=5, hand=5, eye="angry", eyer=2.6,
          mouth="line", back=back, head=head, bs=2, hs=2, as_=2, fs=2, tail="flame", tl=20, trr=3.5, tang=10, ttip=0)


# =================================================================== 127 VICEHORN
@fam("VICEHORN")
def vicehorn(f, st):
    for sg in (-1, 1):
        f.poly([(44 + sg * 8, 34), (50 + sg * 20, 18), (50 + sg * 24, 2), (50 + sg * 14, 8), (50 + sg * 10, 22), (50 + sg * 2, 34)], 1)
        spikes(f, [(50 + sg * 10, 22), (50 + sg * 14, 8)], 3, 3, s=1, side=-sg)
    for sg in (-1, 1):
        f.stroke([(50 + sg * 10, 70), (50 + sg * 18, 82), (50 + sg * 16, 96)], 2.5, 2, 2)
        f.stroke([(50 + sg * 12, 56), (50 + sg * 26, 64), (50 + sg * 28, 76)], 2.5, 2, 2)
    b = f.ell(50, 64, 18, 26, 1, hl=True)
    f.line([(50, 50), (50, 90)], 2)
    h = f.ell(50, 40, 14, 9, 2)
    f.eye(43, 40, 3, "angry", -1)
    f.eye(57, 40, 3, "angry", 1)
    f.line([(44, 46), (56, 46)], 0, face=True)


# =================================================================== 128 RAGEBULL
@fam("RAGEBULL")
def ragebull(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        for sg, s_ in ((1, 0), (-1, 0)):
            horn(f, hx + sg * hr * 0.5, hy - hr * 0.7, 16, 6, -90 - sg * 50, curve=sg * 0.7, s=s_)
        f.poly(blobpoly(hx + 10, hy + 2, hr * 1.2, hr * 1.1, n=7, amp=0.25, seed=128), 2)
    quad(f, bx=62, by=66, brx=27, bry=17, hx=32, hy=50, hr=12, sn=7, snr=6, ears=None, lr=5.5, tail="three", tl=20, trr=1.6, tang=-30,
         eye="angry", eyer=2.6, pre=head, mouth="line", neck=8)
    f.ell(18, 56, 2, 2, 3, sh=0, face=True)


# =================================================================== 129 SPLASHLING
@fam("SPLASHLING")
def splashling(f, st):
    tail_fin(f, 70, 52, 24, 30, ang=-30, s=1, fork=0.6)
    fin(f, 50, 34, 10, 20, 10, s=1, n=3)
    b = f.ell(46, 54, 26, 18, 2, ang=-15, hl=True)
    f.mark_ell(42, 62, 18, 7, 1, ang=-15, clip=b)
    spots(f, b, 52, 48, 12, 6, 5, 1.6, s=1, seed=129)
    f.poly([(40, 60), (42, 74), (50, 64)], 1)
    f.eye(30, 50, 4, "round", 1)
    f.ell(19, 60, 3, 4, 3, sh=0, face=True)
    for x, y in ((14, 84), (30, 90), (70, 88), (84, 80)):
        f.ell(x, y, 3, 3, 0)


# =================================================================== 130 TEMPESTEEL
@fam("TEMPESTEEL")
def tempesteel(f, st):
    path = [(94, 94), (80, 96), (66, 86), (72, 72), (86, 62), (84, 46), (68, 38), (52, 42), (40, 36)]
    b, h = serpent(f, path, 9, 5, bs=2, hr=10, hry=9, bands=0, eye=None, sn=8)
    spikes(f, path[2:-1], 6, 6, s=1, side=-1)
    for x, y, a in ((44, 26, -100), (52, 26, -70)):
        horn(f, x, y, 10, 3.5, a, s=0)
    f.poly([(22, 40), (40, 42), (40, 50), (26, 52)], 3, face=True)
    fang(f, 30, 42, 4, 3)
    fang(f, 36, 42, 4, 3)
    f.eye(44, 34, 3, "angry", -1)
    spark(f, 12, 18, 5)
    f.stroke([(36, 46), (24, 56), (16, 54)], 1.4, 0.8, 1)


# =================================================================== 131 SEAFERRY
@fam("SEAFERRY")
def seaferry(f, st):
    f.poly([(62, 90), (82, 96), (72, 84)], 2)
    f.poly([(30, 82), (14, 92), (40, 92)], 1)
    b = f.ell(56, 76, 30, 16, 1)
    sh_ = f.poly(arc(58, 74, 30, 24, 180, 360, 14) + [(88, 76), (28, 76)], 2, hl=True)
    spikes(f, arc(58, 74, 30, 24, 200, 340, 5), 6, 6, s=1, side=1)
    for k in range(3):
        f.mark_ell(46 + k * 12, 64, 4, 3, 1, clip=sh_)
    f.stroke([(36, 72), (26, 54), (24, 36)], 6, 5, 1)
    h = f.ell(22, 30, 11, 9, 1)
    horn(f, 26, 22, 10, 5, -70, s=0)
    f.eye(18, 28, 3, "round", -1)
    f.line([(12, 34), (18, 35)], 3, face=True)


# =================================================================== 132 COPYGOO
@fam("COPYGOO")
def copygoo(f, st):
    f.stroke([(26, 74), (14, 62), (10, 50)], 4, 2.5, 1)
    f.ell(9, 48, 3.5, 3.5, 1)
    b = f.poly(blobpoly(50, 72, 38, 22, n=6, amp=0.2, seed=132), 1, hl=True)
    ears(f, "point", 66, 56, 9, 1, ang=20)
    f.ell(50, 94, 42, 3, 1, group="puddle")
    f.eye(40, 68, 2.4, "dot", -1)
    f.eye(54, 67, 3.2, "round", -1)
    f.line([(40, 78), (44, 80), (50, 78)], 3, face=True)


# =================================================================== 133 MORPHKIT family
def fox(f, st, mane=None):
    def pre(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        if mane == "ruff":
            f.poly(blobpoly(hx + 6, hy + hr * 0.9, hr * 1.0, hr * 0.7, n=6, amp=0.25, seed=7), 0)
        elif mane == "fin":
            fin(f, hx + 6, hy - hr * 0.4, 18, 22, 40, s=0, n=3)
            fin(f, hx + 14, hy + 4, 14, 18, 70, s=0, n=3)
        elif mane == "spiky":
            spikes(f, arc(q["bx"], q["by"], q["brx"], q["bry"], 180, 360, 8), 10, 8, s=1, side=1)
            spikes(f, arc(hx, hy, hr, hr, 300, 420, 5), 8, 7, s=1, side=1)
        elif mane == "fire":
            f.poly(blobpoly(hx + 8, hy + hr * 0.9, hr * 1.3, hr * 1.0, n=7, amp=0.3, seed=9), 0)
            for a, x, y in ((-60, hx, hy - hr * 0.9), (-30, hx + hr * 0.7, hy - hr * 0.7)):
                flame(f, x, y, 8, 12, ang=a + 50, n=2, s=0, inner=False)
    tails = {None: ("fox", 28, 9, 0), "ruff": ("fox", 28, 9, 0), "fin": ("leaf", 20, 2.5, None), "spiky": ("bolt", 22, 2.5, 1),
             "fire": ("fox", 34, 11, 0)}
    tk, tl, tr, tip = tails[mane]
    kit = mane in (None, "ruff")
    quad(f, bx=60, by=72 if kit else 68, brx=20 if kit else 25, bry=12 if kit else 14, hx=34, hy=52 if kit else 46, hr=14 if kit else 12,
         sn=5 if kit else 8, snr=5, ears="tall" if mane != "fin" else "fin", er=11 if kit else 10, ear_in=2 if mane != "fin" else None,
         lr=3.5 if kit else 4, tail=tk, tl=tl, trr=tr, tang=-55, ttip=tip, eye="round" if kit else "dot", eyer=3.2 if kit else 3,
         pre=pre, neck=0 if kit else None, bs=1 if mane != "spiky" else 1, belly=0 if mane in ("fin",) else None, mouth="smile")


@fam("MORPHKIT")
def morphkit(f, st):
    fox(f, st, "ruff")


@fam("TIDEMANE")
def tidemane(f, st):
    fox(f, st, "fin")


@fam("SPARKMANE")
def sparkmane(f, st):
    fox(f, st, "spiky")


@fam("FLAREMANE")
def flaremane(f, st):
    fox(f, st, "fire")


# =================================================================== 137 POLYGRID
@fam("POLYGRID")
def polygrid(f, st):
    f.poly([(70, 56), (94, 44), (90, 60), (96, 70), (72, 70)], 2)
    for x in (46, 60):
        f.stroke([(x, 76), (x, 94)], 1.4, 1.4, 3)
        f.stroke([(x - 6, 95), (x + 3, 95)], 1.2, 1.2, 3)
    b = f.poly([(30, 52), (56, 40), (76, 54), (64, 80), (38, 80)], 1)
    f.mark_poly([(38, 80), (64, 80), (60, 66), (36, 64)], 0, clip=b)
    f.poly([(48, 52), (78, 26), (74, 48), (84, 50), (66, 64)], 2)
    f.poly([(14, 26), (36, 16), (46, 32), (34, 46), (16, 40)], 1)
    f.poly([(14, 28), (2, 34), (14, 38)], 0)
    f.line([(24, 22), (34, 40)], 2)
    f.eye(26, 30, 2.6, "dot", -1)


# =================================================================== 138 AMMONIX line
@fam("AMMONIX", "AMMOLORD")
def ammo_line(f, st):
    if st == 0:
        for k in range(4):
            f.stroke([(36, 74), (26 + k * 6, 90), (24 + k * 7, 96)], 2.2, 1.4, 1)
        sh_ = f.ell(54, 56, 30, 30, 1, hl=True)
        spiral(f, 56, 54, 26, turns=2.2, s=3, ang0=180)
        f.ell(32, 70, 12, 11, 0)
        f.eye(28, 68, 3, "round", -1)
    else:
        for k in range(6):
            f.stroke([(36, 70), (18 + k * 6, 86), (14 + k * 7, 96)], 2.6, 1.4, 1 if k % 2 else 2)
        sh_ = f.ell(56, 50, 36, 36, 2, hl=True)
        spikes(f, arc(56, 50, 36, 36, 220, 360, 6), 10, 8, s=1, side=1)
        spiral(f, 58, 48, 30, turns=2.3, s=3, ang0=180)
        f.ell(30, 66, 15, 13, 1)
        fang(f, 22, 74, 5, 4)
        f.eye(24, 62, 3, "angry", -1)


# =================================================================== 140 TRILOBYTE / 141 SICKLOBYTE
@fam("TRILOBYTE")
def trilobyte(f, st):
    for k in range(3):
        x = 32 + k * 18
        f.stroke([(x, 80), (x - 4, 96)], 1.6, 1.2, 3)
    d = f.poly(arc(50, 82, 40, 44, 180, 360, 16) + [(90, 84), (10, 84)], 2, hl=True)
    for k in range(3):
        f.mark_stroke([(14 + k * 4, 70 - k * 12), (86 - k * 4, 70 - k * 12)], 0.9, s=1, clip=d)
    f.ell(50, 82, 26, 8, 3, sh=0)
    f.eye(42, 80, 3.2, "glow", -1)
    f.eye(58, 80, 3.2, "glow", -1)


def sicklo_body(f, s=1, eye=True):
    for x in (54, 64):
        f.stroke([(x, 70), (x + 4, 84), (x, 96)], 2.6, 2, 2)
    tail(f, "thin", 70, 64, 24, 3.5, s, 10)
    t = f.ell(56, 54, 12, 20, s)
    f.poly(arc(58, 50, 16, 22, 200, 340, 8) + [(72, 54), (44, 54)], 2)
    for k in range(3):
        f.mark_stroke([(44, 60 + k * 7), (68, 60 + k * 7)], 1.0, s=2, clip=t)
    h = f.poly([(36, 26), (54, 22), (60, 32), (52, 40), (36, 38)], s)
    if eye:
        f.eye(44, 30, 3, "angry", -1)
    for y0 in (48, 58):
        f.stroke([(50, y0), (36, y0 - 2)], 2.6, 2.4, s)
        f.poly(arc(36, y0 - 14, 22, 18, 100, 210, 9) + [(15, y0 - 12), (36, y0 + 1)], 0)


@fam("SICKLOBYTE")
def sicklobyte(f, st):
    sicklo_body(f)


# =================================================================== 142 PTEROFANG
def ptero(f, s=2, eyes=True):
    bat_wing(f, 60, 46, 44, 26, -30, n=3, s=s)
    f.stroke([(60, 58), (84, 68), (96, 64)], 3, 1.2, s)
    f.poly([(92, 60), (100, 62), (94, 68)], s)
    for x in (54, 62):
        f.stroke([(x, 62), (x, 76), (x - 3, 84)], 1.6, 1.3, 3)
    f.ell(57, 54, 12, 9, s)
    f.stroke([(48, 50), (38, 36)], 4.5, 4, s)
    f.poly([(12, 34), (30, 26), (46, 28), (48, 36), (38, 40), (12, 40)], s)
    horn(f, 44, 30, 14, 6, -15, s=s)
    fang(f, 20, 39, 5, 3)
    fang(f, 27, 39, 4, 3)
    f.line([(13, 38), (40, 38)], 3, face=True)
    if eyes:
        f.eye(34, 31, 3, "angry", -1)
    bat_wing(f, 50, 50, 44, 24, -125, n=3, s=1 if s == 2 else 2)


@fam("PTEROFANG")
def pterofang(f, st):
    ptero(f)


# =================================================================== 143 SLUMBERUS
@fam("SLUMBERUS")
def slumberus(f, st):
    feet2(f, 22, 78, 94, 9, 1)
    b = f.ell(50, 66, 42, 30, 2, hl=True)
    f.mark_ell(50, 74, 28, 20, 1, clip=b)
    ears(f, "round", 30, 26, 10, 2, inner=1)
    ears(f, "round", 70, 26, 10, 2, inner=1)
    h = f.ell(50, 34, 22, 16, 2)
    f.mark_ell(50, 40, 10, 7, 1, clip=h)
    f.ell(50, 37, 3, 2, 3, sh=0, face=True)
    f.eye(40, 32, 3.4, "closed", -1)
    f.eye(60, 32, 3.4, "closed", -1)
    f.line([(46, 44), (50, 45), (54, 44)], 3, face=True)
    for x, y, r in ((80, 18, 4), (88, 8, 5)):
        f.line([(x - r, y - r), (x + r, y - r), (x - r, y + r), (x + r, y + r)], 3)


# =================================================================== 144-146 the legendary birds
@fam("GLACIRAVEN")
def glaciraven(f, st):
    def back(f, q):
        for k in range(4):
            horn(f, 70 + k * 6, 30 - k * 3, 12, 4, -60 - k * 8, s=0)
    bird(f, bx=58, by=60, brx=22, bry=14, tilt=-20, bs=1, hx=32, hy=34, hr=11, beak=12, beakw=6, hook=2, wing="up", wl=40, ww=18,
         tailk="long", tl=26, tw=12, legl=12, eye="angry", eyer=2.6, crest="spike", cl=12, fly=True, belly=0, back=back)


@fam("VOLTHAWK")
def volthawk(f, st):
    def head(f, q):
        spark(f, 18, 18, 5)
        spark(f, 88, 86, 5)
    bird(f, bx=58, by=60, brx=22, bry=14, tilt=-20, bs=2, hs=2, hx=32, hy=34, hr=11, beak=10, beakw=6, hook=3, wing="up", wl=40, ww=18,
         ws=1, tailk="banner", tl=26, tw=14, legl=12, eye="angry", eyer=2.6, crest="spike", cl=14, fly=True, head=head)


@fam("FLAREKITE")
def flarekite(f, st):
    def pre(f, q):
        for a, x, y in ((-30, 74, 40), (0, 82, 46), (30, 88, 54)):
            flame(f, x, y, 12, 18, ang=a + 40, n=3, s=0, inner=False)
    def head(f, q):
        flame(f, q["hx"] + 4, q["hy"] - q["hr"] * 0.7, 10, 16, ang=30, n=3, s=0, inner=False)
    bird(f, bx=58, by=60, brx=22, bry=13, tilt=-20, bs=1, hx=32, hy=34, hr=11, beak=10, beakw=6, hook=1, wing="up", wl=40, ww=18,
         ws=1, tailk="long", tl=26, tw=10, legl=12, eye="angry", eyer=2.6, fly=True, pre=pre, head=head)


# =================================================================== 147 WYRMLET line
@fam("WYRMLET", "CLOUDWYRM", "STORMWYRM")
def wyrm_line(f, st):
    if st == 0:
        path = [(90, 90), (70, 96), (50, 92), (44, 80), (56, 70), (60, 56), (50, 44), (36, 40)]
        b, h = serpent(f, path, 7, 3, bs=1, hr=9, bands=0, eye="round", eyer=3.2, sn=4)
        f.mark_stroke(path[:-1], 2.2, 1.2, s=0, clip=b)
        fin(f, 44, 30, 8, 8, 20, s=0, n=2)
        fin(f, 52, 31, 8, 8, 40, s=0, n=2)
    elif st == 1:
        path = [(96, 96), (74, 94), (60, 84), (70, 70), (82, 56), (72, 40), (54, 34), (38, 30)]
        b, h = serpent(f, path, 7, 3, bs=1, hr=9, bands=0, eye="dot", eyer=3, sn=5)
        f.mark_stroke(path[:-1], 2.4, 1.2, s=0, clip=b)
        horn(f, 46, 22, 9, 4, -80, s=0)
        fin(f, 48, 24, 10, 10, 30, s=0, n=2)
        for x, y in ((18, 60), (40, 70)):
            f.ell(x, y, 6, 6, 0, hl=False)
            f.ell(x, y, 2.5, 2.5, 2, line=False, sh=0)
        f.poly(blobpoly(80, 92, 14, 6, n=5, amp=0.2, seed=3), 0)
    else:
        def pre(f, q):
            bat_wing(f, 64, 46, 34, 22, -50, n=3, s=2)
            bat_wing(f, 60, 48, 30, 18, -80, n=3, s=2)
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            f.stroke([(hx - 2, hy - hr * 0.8), (hx - 6, hy - hr * 1.7)], 0.9, 0.9, 3)
            f.stroke([(hx + 4, hy - hr * 0.8), (hx + 2, hy - hr * 1.7)], 0.9, 0.9, 3)
        biped(f, tx=54, ty=62, trx=19, tr_y=23, hx=42, hy=30, hr=12, sn=8, snr=5, legr=7, legx=7, arm="side", armr=4.5, hand=4,
              ears="point", er=6, tail="thin", tl=26, trr=5, tang=10, eye="dot", eyer=2.8, belly=0, pre=pre, head=head, mouth="smile", bs=1)


# =================================================================== 150 OMNIGENE / 151 PRIMORA
@fam("OMNIGENE")
def omnigene(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.poly([(hx - hr * 0.4, hy - hr * 0.9), (hx + hr * 0.6, hy - hr * 1.6), (hx + hr * 0.8, hy - hr * 0.6)], q["bs"])
        f.mark_ell(hx + hr * 0.1, hy - hr * 0.45, hr * 0.5, hr * 0.25, 0, clip=q["headid"])
        f.line([(q["tx"] - 4, q["ty"] - 12), (q["tx"] - 2, q["ty"] + 10)], 2)
    def back(f, q):
        for k in range(3):
            f.mark_ell(q["tx"] - 2, q["ty"] - 10 + k * 9, 6, 2.2, 2, clip=q["body"])
    def pre(f, q):
        for x, y in ((14, 30), (86, 22)):
            f.ell(x, y, 7, 7, 0, hl=False)
            f.ell(x, y, 3.5, 3.5, 2, line=False, sh=0)
    biped(f, tx=54, ty=58, trx=14, tr_y=24, hx=46, hy=26, hr=11, legr=5.5, legx=6, arm="up", armr=3, hand=4, eye="angry", eyer=2.6,
          mouth="line", tail="thin", tl=34, trr=4, tang=30, head=head, back=back, pre=pre, belly=1, bs=0, hs=0, as_=0, fs=0)


@fam("PRIMORA")
def primora(f, st):
    f.stroke([(64, 70), (84, 74), (92, 60), (86, 52)], 2.2, 1.0, 1)
    f.ell(86, 51, 3, 3, 1)
    for a in (-50, -15):
        bug_wing(f, 56, 56, 30, 14, a, s=0, veins=1)
    for x in (44, 56):
        f.stroke([(x, 70), (x - 2, 86)], 2.4, 2, 1)
    b = f.ell(50, 62, 12, 12, 1, hl=True)
    h = f.ell(48, 40, 16, 15, 1, hl=True)
    f.eye(42, 40, 4, "round", -1)
    f.eye(54, 40, 3.6, "round", -1)
    f.line([(44, 49), (48, 50)], 3, face=True)


# =================================================================== fossil displays
def fossil(stem, W, H):
    from games.pokered.art.k_kith_draw import Fig
    f = Fig(W, H, sc=W / 100.0, ox=W / 2.0, oy=H)
    f.poly([(6, 92), (4, 30), (18, 10), (60, 4), (90, 16), (96, 60), (92, 94)], 2)
    s = f.poly([(10, 88), (8, 32), (20, 14), (58, 8), (86, 20), (92, 60), (88, 90)], 1)
    for (x, y) in ((16, 72), (80, 30), (70, 82)):
        f.line([(x, y), (x + 5, y + 4), (x + 3, y + 9)], 2)
    if stem == "fossilkabutops":
        bones = [[(50, 30), (50, 76)], [(46, 24), (40, 14), (34, 12)], [(54, 24), (60, 14), (66, 12)]]
        for sg in (-1, 1):
            bones += [[(50, 40), (50 + sg * 34, 20), (50 + sg * 30, 40), (50 + sg * 32, 50), (50, 52)],
                      [(50 + sg * 6, 42), (50 + sg * 24, 32)],
                      [(50, 56), (50 + sg * 22, 66), (50 + sg * 16, 80), (50 + sg * 4, 70)]]
        for y in (58, 64, 70):
            bones.append([(46, y), (54, y)])
    else:
        bones = [[(18, 34), (32, 28), (44, 30), (40, 38), (18, 40), (18, 34)], [(42, 34), (54, 48)], [(54, 48), (70, 56), (86, 54)],
                 [(54, 46), (62, 30), (74, 22), (88, 28)], [(62, 30), (72, 40)], [(70, 24), (78, 40)], [(56, 52), (54, 70)], [(62, 54), (64, 72)]]
        for x in (58, 64, 70, 76):
            bones.append([(x, 52), (x + 1, 60)])
    for b in bones:
        f.stroke(b, 1.6, 1.6, 0, group="bone", sh=0)
    if stem == "fossilkabutops":
        f.ell(50, 28, 4, 3.5, 0, group="bone", sh=0)
        f.eye(50, 28, 1.6, "dot", -1)
    else:
        f.eye(26, 32, 2.2, "dot", -1)
    return f.render()
