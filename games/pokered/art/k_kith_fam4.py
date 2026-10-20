"""KITHBOUND families, part 4 (national 61-100)."""
import math

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_fam import fam, spark
from games.pokered.art.k_kith_fam3 import feet2, fuzzball, note, quills
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, cog, fang, fin,
                                          flame, horn, leaf, rot, spikes, spiral, spots, star, stripes,
                                          tail_fin)


# =================================================================== 61 EDDYFROG line
@fam("EDDYFROG", "VORTEXTOAD")
def eddy_line(f, st):
    big = st == 1
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        for dx in (-0.5, 0.35):
            f.ell(hx + hr * dx, hy - hr * 0.75, hr * 0.38, hr * 0.38, 1, group="head")
            f.eye(hx + hr * dx, hy - hr * 0.78, hr * 0.26, "angry" if big else "round", -1)
        f.line([(hx - hr * 0.9, hy + hr * 0.25), (hx + hr * 0.5, hy + hr * 0.35)], 3, face=True)
    def back(f, q):
        b = q["body"]
        f.mark_ell(q["tx"] - q["trx"] * 0.15, q["ty"] + 1, q["trx"] * 0.62, q["tr_y"] * 0.6, 0, clip=b)
        spiral(f, q["tx"] - q["trx"] * 0.15, q["ty"] + 1, q["trx"] * 0.55, turns=2.0)
    if not big:
        biped(f, tx=50, ty=68, trx=24, tr_y=22, hx=44, hy=40, hr=14, hry=10, legr=6, legx=12, footl=1.5, arm="side", armr=4,
              hand=4, eye=None, mouth=None, head=head, back=back, bs=1)
    else:
        def front(f, q):
            for x, y in (q["farhand"], q["handpos"]):
                f.ell(x, y, 7, 6, 0)
        biped(f, tx=50, ty=62, trx=24, tr_y=24, hx=44, hy=30, hr=13, hry=9, legr=8, legx=12, footl=1.5, arm="guard", armr=6,
              hand=None, eye=None, mouth=None, head=head, back=back, front=front, bs=1)


# =================================================================== 63 SOMNIX line
@fam("SOMNIX", "DREAMWEAVE", "PSYMONARCH")
def somnix_line(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.mark_poly([(hx - hr * 1.2, hy + hr * 0.1), (hx - hr * 0.2, hy - hr * 0.1), (hx + hr * 0.1, hy + hr), (hx - hr, hy + hr)], 0, clip=q["headid"])
        if st == 2:
            f.poly([(hx - hr * 0.6, hy - hr * 0.8), (hx - hr * 0.7, hy - hr * 1.6), (hx - hr * 0.25, hy - hr * 1.15), (hx, hy - hr * 1.75),
                    (hx + hr * 0.25, hy - hr * 1.15), (hx + hr * 0.7, hy - hr * 1.6), (hx + hr * 0.6, hy - hr * 0.8)], 0)
    if st == 0:
        biped(f, tx=56, ty=72, trx=14, tr_y=15, hx=46, hy=46, hr=16, sn=6, snr=5, legr=4, legx=5, arm="side", armr=2.8,
              ears="fold", er=11, ear_ang=20, tail="fox", tl=26, trr=8, tang=-60, eye="closed", eyer=3.2, head=head, belly=0, mouth=None)
        f.line([(62, 30), (66, 28), (62, 24), (66, 22)], 3)
    elif st == 1:
        def front(f, q):
            x, y = q["handpos"]
            f.line([(x, y), (x - 6, y - 8), (x + 2, y - 16), (x - 4, y - 26), (x + 4, y - 32)], 2)
            f.ell(x + 4, y - 34, 3, 3, 0)
        biped(f, tx=55, ty=64, trx=14, tr_y=20, hx=44, hy=32, hr=13, sn=8, snr=5, legr=4.5, legx=5, arm="fwd", armr=3,
              ears="fold", er=12, ear_ang=20, tail="fox", tl=30, trr=8, tang=-50, eye="sleepy", eyer=3, head=head, belly=0, front=front, mouth=None)
    else:
        def pre(f, q):
            for x, y in ((18, 40), (86, 30), (84, 66)):
                o = f.ell(x, y, 6, 6, 1, hl=True)
        biped(f, tx=54, ty=62, trx=16, tr_y=22, hx=44, hy=30, hr=13, sn=9, snr=5, legr=5, legx=5.5, arm="up", armr=3.2, hand=3,
              ears="point", er=10, ear_in=2, tail="fox", tl=34, trr=9, tang=-40, eye="slit", eyer=3, head=head, belly=0, pre=pre, mouth="line")


# =================================================================== 66 GRAPPLET line
@fam("GRAPPLET", "HEFTGRIP", "TITANFIST")
def grapple_line(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.poly([(hx - hr * 0.6, hy - hr * 0.7), (hx - hr * 0.1, hy - hr * 1.5), (hx + hr * 0.2, hy - hr * 0.8)], 1)
    def belt(f, q):
        y = q["ty"] + q["tr_y"] * 0.55
        f.mark_stroke([(q["tx"] - 30, y), (q["tx"] + 30, y)], 2.5 + st * 0.5, s=3, clip=q["body"])
        f.ell(q["tx"] - q["trx"] * 0.3, y, 4 + st, 3 + st * 0.6, 0)
    if st == 0:
        biped(f, tx=52, ty=68, trx=17, tr_y=18, hx=46, hy=40, hr=13, legr=6, legx=7, arm="hips", armr=4.5, hand=4,
              eye="angry", eyer=2.8, mouth="line", head=head, back=belt, bs=1)
    elif st == 1:
        biped(f, tx=52, ty=62, trx=19, tr_y=22, hx=44, hy=30, hr=11, legr=7, legx=8, arm="guard", armr=7, hand=6,
              eye="angry", eyer=2.6, mouth="line", head=head, back=belt, bs=1)
    else:
        def pre(f, q):
            f.stroke([(62, 46), (82, 34), (88, 18)], 6, 5, 2)
            f.ell(88, 16, 7, 7, 2)
            f.stroke([(64, 56), (86, 60), (92, 48)], 6, 5, 2)
            f.ell(92, 46, 7, 7, 2)
        def front(f, q):
            f.stroke([(42, 54), (24, 62), (16, 52)], 6.5, 6, 1)
            f.ell(15, 50, 7.5, 7.5, 1)
        biped(f, tx=54, ty=60, trx=21, tr_y=24, hx=46, hy=28, hr=11, legr=8, legx=9, arm="up", armr=7, hand=7,
              eye="angry", eyer=2.6, mouth="open", head=head, back=belt, pre=pre, front=front, bs=1)


# =================================================================== 69 STEMSNAP line
def snapbulb(f, x, y, r, ang=0, s=1, teeth=True):
    top = rot(arc(0, 0, r, r * 0.8, 180, 360, 10) + [(r * 0.2, 0)], ang, x, y)
    bot = rot(arc(0, r * 0.25, r * 0.9, r * 0.6, 0, 180, 10), ang, x, y)
    f.poly(bot, s)
    t = f.poly(top, s)
    f.ell(*rot([(r * 0.1, r * 0.1)], ang, x, y)[0], r * 0.7, r * 0.12, 3, sh=0, line=False, ang=ang)
    if teeth:
        spikes(f, rot([(-r * 0.8, r * 0.02), (r * 0.6, r * 0.02)], ang, x, y), r * 0.25, r * 0.2, s=0, side=1)
    return t


@fam("STEMSNAP", "SNAPVINE", "PITCHERMAW")
def snap_line(f, st):
    if st == 0:
        f.stroke([(50, 96), (54, 76), (48, 56), (52, 44)], 2.2, 1.6, 2)
        leaf(f, 52, 78, 16, 5, -20, s=1)
        leaf(f, 50, 66, 14, 5, 200, s=1)
        snapbulb(f, 46, 34, 16, ang=-15, s=1)
        f.eye(40, 26, 3, "angry", -1)
        f.eye(50, 25, 2.6, "angry", -1)
        f.ell(42, 96, 12, 3, 2)
    elif st == 1:
        f.stroke([(56, 96), (64, 80), (58, 62), (62, 50)], 2.5, 1.8, 2)
        leaf(f, 62, 80, 20, 6, -20, s=1)
        leaf(f, 60, 70, 18, 6, 200, s=1)
        bell = f.poly([(62, 50), (40, 24), (24, 26), (16, 42), (28, 56), (44, 60)], 1)
        f.poly([(20, 40), (36, 52), (24, 54)], 3, line=False)
        spikes(f, [(18, 40), (34, 52)], 4, 3, s=0, side=-1)
        f.eye(32, 32, 3, "angry", -1)
        f.eye(42, 34, 2.6, "angry", -1)
    else:
        f.stroke([(60, 90), (78, 76), (86, 60)], 2.5, 1.8, 2)
        leaf(f, 70, 82, 20, 7, -30, s=1)
        leaf(f, 40, 84, 20, 7, 200, s=1)
        pid = f.poly([(28, 22), (72, 22), (70, 50), (64, 82), (50, 92), (36, 82), (30, 50)], 1, hl=True)
        f.mark_poly([(28, 22), (72, 22), (71, 32), (29, 32)], 2, clip=pid)
        spots(f, pid, 50, 66, 12, 12, 5, 2.4, s=2, seed=4)
        f.ell(50, 22, 22, 5, 3, sh=0)
        lid = f.poly([(26, 18), (50, 6), (76, 14), (66, 20), (40, 20)], 2)
        f.stroke([(76, 14), (84, 18)], 1.5, 1.0, 2)
        f.eye(42, 44, 3.2, "angry", -1)
        f.eye(58, 44, 3.2, "angry", 1)
        f.line([(40, 54), (60, 54)], 3, face=True)


# =================================================================== 72 DRIFTJELL line
@fam("DRIFTJELL", "STINGMIRE")
def jelly_line(f, st):
    if st == 0:
        for x in (36, 46, 56, 66):
            f.stroke([(x, 56), (x - 3, 70), (x + 2, 82), (x - 1, 94)], 1.4, 0.9, 2)
        b = f.poly(arc(50, 56, 26, 34, 180, 360, 16) + [(76, 58), (24, 58)], 0, hl=False)
        f.mark_ell(50, 50, 18, 18, 1, clip=b)
        for x in (40, 60):
            f.ell(x, 40, 5, 6, 2, hl=True)
        f.eye(42, 54, 2.4, "dot", -1)
        f.eye(58, 54, 2.4, "dot", -1)
    else:
        for i in range(9):
            x = 22 + i * 7
            f.stroke([(x, 50), (x + (i % 3 - 1) * 4, 68), (x - (i % 2) * 4, 84), (x + 2, 96)], 1.6, 0.8, 2 if i % 2 else 1)
            horn(f, x + 2, 94, 5, 3, 90, s=0)
        b = f.poly(arc(50, 50, 34, 40, 180, 360, 18) + [(84, 52), (16, 52)], 0)
        f.mark_ell(50, 42, 24, 24, 1, clip=b)
        for x, y in ((36, 30), (64, 30), (50, 22)):
            f.ell(x, y, 5, 6, 2, hl=True)
        f.eye(40, 44, 3, "angry", -1)
        f.eye(60, 44, 3, "angry", 1)


# =================================================================== 74 PEBBLIT line
def rock(f, cx, cy, rx, ry, seed, s=1, n=7, cracks=2):
    pts = []
    import random
    rng = random.Random(seed)
    for i in range(n):
        a = i * math.tau / n + rng.uniform(-0.2, 0.2)
        r = rng.uniform(0.85, 1.05)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    rid = f.poly(pts, s, hl=True)
    for k in range(cracks):
        a = rng.uniform(0, math.tau)
        x, y = cx + math.cos(a) * rx * 0.5, cy + math.sin(a) * ry * 0.5
        f.line([(x, y), (x + rng.uniform(-5, 5), y + rng.uniform(3, 6)), (x + rng.uniform(-6, 6), y + rng.uniform(6, 10))], 3)
    return rid


@fam("PEBBLIT", "RUBBLEMAN", "QUARRYHULK")
def pebble_line(f, st):
    if st == 0:
        f.stroke([(64, 64), (82, 72), (88, 86)], 4, 3.5, 2)
        f.ell(88, 88, 6, 5, 2)
        rock(f, 50, 66, 26, 24, 3)
        f.stroke([(34, 66), (18, 74), (12, 88)], 4.5, 4, 1)
        f.ell(12, 90, 6.5, 5.5, 1)
        f.eye(40, 60, 3, "angry", -1)
        f.eye(52, 60, 3, "angry", -1)
        f.line([(40, 72), (50, 72)], 3, face=True)
    elif st == 1:
        for (a, b, c) in (((62, 48), (84, 36), (92, 22)), ((64, 62), (86, 66), (94, 54))):
            f.stroke([a, b, c], 4.5, 4, 2)
            rock(f, c[0], c[1], 6, 6, int(c[0]), s=2, cracks=0)
        for k, (x, y, r) in enumerate(((36, 82, 12), (62, 84, 13), (50, 70, 14), (38, 58, 10), (62, 56, 12))):
            rock(f, x, y, r, r * 0.9, k + 2, cracks=1)
        f.ell(48, 48, 15, 13, 1, group="head", hl=True)
        for (a, b, c) in (((36, 56), (18, 50), (10, 36)), ((38, 66), (18, 72), (10, 62))):
            f.stroke([a, b, c], 5, 4.5, 1)
            rock(f, c[0], c[1], 7, 7, int(c[1]), s=1, cracks=0)
        f.eye(42, 46, 2.8, "angry", -1)
        f.eye(52, 45, 2.6, "angry", -1)
        f.line([(40, 54), (48, 54)], 3, face=True)
    else:
        for x in (36, 66):
            f.stroke([(x, 80), (x - 2, 95)], 6, 6, 2)
            f.ell(x - 4, 95, 8, 4, 2)
        sid = rock(f, 52, 58, 40, 34, 9, s=2, n=9, cracks=4)
        for k, (x, y) in enumerate(((30, 36), (52, 28), (72, 40), (78, 62), (24, 62))):
            rock(f, x, y, 7, 6, k + 30, s=1, cracks=0)
        f.ell(30, 60, 14, 12, 1, group="head", hl=True)
        f.stroke([(36, 78), (18, 86), (12, 76)], 6, 5.5, 1)
        f.ell(11, 74, 7, 7, 1)
        f.eye(24, 57, 2.8, "angry", -1)
        f.eye(34, 56, 2.6, "angry", -1)
        f.line([(22, 66), (32, 66)], 3, face=True)


# =================================================================== 77 EMBERCOLT line
@fam("EMBERCOLT", "BLAZESTEED")
def colt_line(f, st):
    def hooves(f, q):
        pass
    if st == 0:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            for a, x, y in ((-30, hx + 2, hy - hr * 0.9), (0, hx + 9, hy - hr * 0.5), (20, hx + 14, hy + 4)):
                flame(f, x, y, 9, 13, ang=a + 30, n=2, s=1, inner=False)
        quad(f, bx=60, by=64, brx=20, bry=12, hx=34, hy=38, hr=11, sn=8, snr=5, ears="point", er=7, ear_in=2,
             lr=2.6, tail="flame", tl=16, trr=2.5, tang=-30, ttip=1, eye="round", eyer=3, head=head, neck=5, mouth="smile", fs=1)
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            horn(f, hx - hr * 0.45, hy - hr * 0.75, 16, 4, -125, s=0)
            for a, x, y in ((-20, hx + 4, hy - hr), (10, hx + 11, hy - hr * 0.5), (30, hx + 16, hy + 3), (50, hx + 20, hy + 10)):
                flame(f, x, y, 11, 17, ang=a + 30, n=3, s=0, inner=False)
        quad(f, bx=60, by=60, brx=24, bry=13, hx=30, hy=32, hr=10, sn=11, snr=5, ears="point", er=7, ear_in=2,
             lr=3, tail="flame", tl=24, trr=3, tang=-20, ttip=0, eye="angry", eyer=2.6, head=head, neck=6, mouth="line")


# =================================================================== 79 DAWDLUG line
@fam("DAWDLUG", "DAWDLORD")
def dawd_line(f, st):
    if st == 0:
        quad(f, bx=60, by=76, brx=26, bry=13, hx=30, hy=62, hr=15, hry=12, sn=8, snr=7, ears="round", er=7,
             lr=4, tail="thin", tl=26, trr=3, tang=-5, eye="sleepy", eyer=3, belly=0, neck=0, mouth="smile")
        f.ell(14, 76, 2.2, 3, 0, sh=0)
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            c = f.poly(arc(hx + 2, hy - hr * 0.6, hr * 0.9, hr * 0.7, 180, 360, 10) + [(hx + 2 + hr * 0.9, hy - hr * 0.5), (hx + 2 - hr * 0.9, hy - hr * 0.5)], 0)
            for k in range(4):
                f.line([(hx + 2 - hr * 0.6 + k * hr * 0.4, hy - hr * 0.55), (hx + 2 - hr * 0.5 + k * hr * 0.33, hy - hr * 1.15)], 2)
            spikes(f, arc(hx + 2, hy - hr * 0.6, hr * 0.9, hr * 0.7, 190, 350, 5), 3, 2.5, s=0, side=1)
        biped(f, tx=54, ty=66, trx=17, tr_y=20, hx=42, hy=40, hr=14, hry=11, sn=7, snr=7, legr=5, legx=6, arm="side", armr=3.5,
              ears="round", er=6, tail="thin", tl=24, trr=3, tang=10, eye="sleepy", eyer=2.8, belly=0, head=head, mouth="smile")


# =================================================================== 81 COGSPARK line
def cogeye(f, cx, cy, r, s=1, ang=0, eye="round"):
    c = f.poly(cog(cx, cy, r, teeth=8, ang=ang), s, hl=True)
    f.ell(cx, cy, r * 0.5, r * 0.5, 0)
    f.eye(cx, cy, r * 0.32, eye, -1)
    return c


@fam("COGSPARK", "GEARSTORM")
def cog_line(f, st):
    if st == 0:
        cogeye(f, 50, 54, 26, 1)
        spark(f, 18, 30, 5)
        spark(f, 84, 76, 5)
        f.ell(50, 96, 14, 2, 2)
    else:
        f.stroke([(30, 60), (50, 34), (70, 62)], 3, 3, 2)
        cogeye(f, 50, 32, 20, 1, ang=10, eye="angry")
        cogeye(f, 28, 66, 20, 1, ang=5, eye="angry")
        cogeye(f, 72, 66, 20, 1, ang=15, eye="angry")
        spark(f, 12, 30, 5)
        spark(f, 88, 26, 5)


# =================================================================== 83 REEDBILL
@fam("REEDBILL")
def reedbill(f, st):
    def head(f, q):
        x, y = q["hx"] - q["hr"] * 1.4, q["hy"] + 2
        f.stroke([(x + 4, y - 16), (x - 2, y + 30)], 1.3, 1.3, 2)
        leaf(f, x + 4, y - 16, 10, 2.5, -70, s=1, vein=False)
        f.ell(x + 5, y - 22, 2.5, 6, 2)
    bird(f, bx=58, by=62, brx=20, bry=15, tilt=-12, hx=36, hy=40, hr=12, beak=9, beakw=5, wing="fold", wl=24, ww=13,
         tailk="fan", tl=14, tw=9, legl=10, belly=0, eye="dot", eyer=3, head=head, crest="tuft", cl=8)
    f.line([(30, 44), (33, 46)], 3, face=True)


# =================================================================== 84 BIRUNNER line
@fam("BIRUNNER", "TRIRUNNER")
def runner_line(f, st):
    n = 2 + st
    heads = [(30, 24), (52, 18), (44, 30)][:n] if n == 3 else [(34, 30), (52, 24)]
    for k, (x, y) in enumerate(heads[::-1]):
        f.stroke([(56, 58), (x + 3, y + 6)], 2.4, 2.2, 1, group="neck%d" % k)
    for dx in (6, -4):
        f.stroke([(56 + dx, 66), (54 + dx, 82), (58 + dx, 96)], 1.7, 1.4, 3)
        f.stroke([(50 + dx, 96), (62 + dx, 96)], 1.2, 1.2, 3)
    b = f.ell(60, 60, 22, 14, 1 if st == 0 else 2, ang=-8)
    f.poly([(78, 54), (96, 46), (90, 58), (98, 64), (78, 66)], 2 if st == 0 else 1)
    bird_wing(f, 52, 56, 22, 12, 15, n=3, s=2 if st == 0 else 1)
    for k, (x, y) in enumerate(heads[::-1]):
        f.ell(x, y, 8, 7.5, 1, group="h%d" % k)
        f.poly([(x - 6, y - 2), (x - 18, y + 1), (x - 6, y + 3)], 0, group="h%d" % k)
        f.eye(x - 2, y - 2, 2.6, "angry" if k % 2 else "dot", -1)
        if st == 1:
            f.poly([(x, y - 7), (x + 3, y - 14), (x + 4, y - 7)], 2)


# =================================================================== 86 FLOEPUP line (seals)
@fam("FLOEPUP", "FROSTSEAL")
def seal_line(f, st):
    if st == 0:
        tail_fin(f, 74, 84, 18, 14, ang=-10, s=1)
        b = f.poly([(20, 70), (36, 58), (60, 64), (80, 82), (70, 92), (30, 92), (18, 84)], 1, hl=True)
        f.ell(32, 62, 16, 14, 1, group="body")
        horn(f, 30, 50, 10, 5, -100, s=0)
        f.ell(42, 88, 8, 4, 1)
        f.eye(26, 58, 3, "round", -1)
        f.eye(36, 58, 2.6, "round", -1)
        f.ell(20, 66, 3, 2, 3, sh=0, face=True)
        f.line([(17, 70), (12, 70)], 3, face=True)
    else:
        tail_fin(f, 76, 76, 22, 18, ang=-30, s=0)
        b = f.poly([(16, 56), (34, 44), (60, 56), (84, 76), (76, 92), (30, 94), (14, 78)], 0, sh=3, group="body")
        f.ell(28, 46, 15, 13, 0, group="body", sh=2)
        horn(f, 24, 34, 18, 6, -100, s=1)
        spikes(f, [(60, 58), (80, 76)], 5, 5, s=1, side=-1)
        f.ell(40, 90, 10, 4, 1)
        f.eye(22, 42, 3, "dot", -1)
        f.eye(31, 42, 2.6, "dot", -1)
        f.ell(14, 50, 3, 2, 3, sh=0, face=True)


# =================================================================== 88 MUCKLET line
@fam("MUCKLET", "SLOPMOUND")
def muck_line(f, st):
    if st == 0:
        b = f.poly(blobpoly(50, 70, 32, 26, n=8, amp=0.18, seed=4), 2, hl=True)
        f.ell(50, 94, 38, 4, 2, group="puddle")
        for x, y in ((28, 54), (70, 50)):
            f.ell(x, y, 2.5, 2.5, 0, line=False, sh=0)
        f.eye(40, 66, 3.2, "round", -1)
        f.eye(56, 66, 3.2, "round", -1)
        f.ell(48, 78, 5, 3, 3, line=False, sh=0, face=True)
    else:
        f.stroke([(70, 56), (88, 46), (94, 32)], 6, 4, 2)
        b = f.poly(blobpoly(50, 64, 40, 34, n=9, amp=0.2, seed=8), 2, hl=True)
        f.ell(50, 95, 46, 4, 2, group="puddle")
        f.stroke([(28, 60), (12, 50), (8, 38)], 7, 4, 2)
        for i in range(3):
            f.ell(8 + i * 2.5 - 2, 36 - i * 1.5, 1.6, 4, 2)
        f.eye(36, 50, 3.4, "angry", -1)
        f.eye(56, 50, 3.4, "angry", 1)
        f.ell(46, 68, 12, 6, 3, line=False, sh=0, face=True)
        f.ell(46, 72, 7, 2.5, 1, line=False, sh=0, face=True)


# =================================================================== 90 PEARLIP line
@fam("PEARLIP", "SPIKECLAM")
def clam_line(f, st):
    if st == 0:
        bot = f.poly(arc(50, 70, 36, 24, 0, 180, 14), 1)
        f.ell(50, 70, 18, 6, 3, sh=0)
        f.ell(46, 66, 9, 9, 0, hl=False)
        f.ell(43, 63, 2.5, 2.5, 0, line=False, sh=0)
        top = f.poly(arc(50, 62, 36, 28, 180, 360, 14) + [(86, 64), (14, 64)], 1)
        for k in range(5):
            f.line([(50, 62), (24 + k * 13, 40 + abs(k - 2) * 4)], 2)
        f.eye(38, 52, 3, "round", -1)
        f.eye(54, 50, 3, "round", -1)
    else:
        spikes(f, arc(50, 56, 40, 38, 160, 380, 10), 12, 8, s=1, side=1)
        sh_ = f.ell(50, 56, 40, 38, 1, hl=True)
        for k in range(6):
            f.line([(50, 92), (22 + k * 11, 22 + abs(k - 2.5) * 6)], 2)
        f.ell(50, 60, 20, 18, 3, sh=0)
        core = f.ell(50, 60, 12, 12, 2)
        f.eye(45, 58, 3.0, "glow", -1)
        f.eye(56, 58, 3.0, "glow", -1)


# =================================================================== 92 WISPLET line
@fam("WISPLET", "SHROUDLE", "NIGHTGRIN")
def wisp_line(f, st):
    if st == 0:
        ring = f.poly(blobpoly(50, 56, 46, 40, n=9, amp=0.16, seed=6), 0)
        f.mark_ell(50, 56, 30, 26, 1, clip=ring)
        f.ell(50, 56, 22, 21, 3)
        f.eye(42, 52, 3.4, "glow", -1)
        f.eye(58, 52, 3.4, "glow", -1)
        f.line([(42, 64), (46, 66), (50, 64), (54, 66), (58, 64)], 0, face=True)
    elif st == 1:
        tailp = [(56, 66), (70, 80), (60, 90), (74, 96)]
        f.stroke(tailp, 12, 2, 2)
        h = f.ell(50, 46, 26, 26, 2, hl=True)
        spikes(f, arc(50, 46, 26, 26, 200, 340, 4), 8, 8, s=2, side=1)
        for x, y, sg in ((14, 56, -1), (86, 50, 1)):
            f.ell(x, y, 7, 6, 2)
            for k in range(3):
                horn(f, x + sg * 4, y - 4 + k * 4, 7, 2.5, sg * 0 + (180 if sg < 0 else 0) + (k - 1) * 18, s=2)
        f.eye(40, 42, 4, "angry", -1)
        f.eye(60, 42, 4, "angry", 1)
        f.poly([(36, 56), (64, 56), (58, 64), (42, 64)], 0, face=True)
        f.line([(44, 56), (44, 63)], 3, face=True)
        f.line([(50, 56), (50, 64)], 3, face=True)
        f.line([(56, 56), (56, 63)], 3, face=True)
    else:
        b = f.poly([(14, 96), (12, 60), (20, 30), (30, 14), (40, 30), (50, 20), (60, 30), (70, 14), (80, 30), (88, 60), (86, 96),
                    (74, 88), (64, 96), (50, 88), (36, 96), (26, 88)], 2, hl=True)
        for x, y in ((8, 60), (92, 60)):
            f.ell(x, y, 6, 8, 2)
        f.eye(36, 44, 4.5, "angry", -1)
        f.eye(64, 44, 4.5, "angry", 1)
        f.poly(arc(50, 58, 28, 14, 0, 180, 12), 0, face=True)
        for k in range(7):
            x = 26 + k * 8
            f.line([(x, 58), (x, 58 + 10 * math.sin(math.pi * (k + 0.5) / 7))], 3, face=True)
        f.line([(22, 58), (78, 58)], 3, face=True)


# =================================================================== 95 SLATEWORM
@fam("SLATEWORM")
def slateworm(f, st):
    path = [(92, 92), (76, 96), (58, 90), (50, 76), (58, 62), (66, 48), (60, 34), (46, 26)]
    for i, (x, y) in enumerate(path[:-1]):
        r = 8 + i * 0.9
        f.poly([(x - r, y - r * 0.6), (x + r, y - r * 0.7), (x + r * 1.05, y + r * 0.6), (x - r * 0.9, y + r * 0.7)], 1 if i % 2 else 2)
    x, y = path[-1]
    f.poly([(x - 16, y - 8), (x + 10, y - 12), (x + 14, y + 8), (x - 14, y + 10), (x - 20, y + 2)], 1, hl=True)
    horn(f, x + 4, y - 10, 10, 6, -70, s=0)
    f.eye(x - 10, y - 2, 3, "angry", -1)
    f.eye(x - 1, y - 3, 2.8, "angry", -1)
    f.line([(x - 18, y + 4), (x - 4, y + 6)], 3, face=True)


# =================================================================== 96 YAWNTAPIR line
@fam("YAWNTAPIR", "DREAMSNOUT")
def tapir_line(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.stroke([(hx - hr * 0.7, hy), (hx - hr * 1.5, hy + 2), (hx - hr * 1.8, hy + 8)], hr * 0.32, hr * 0.25, q["bs"], group="head")
        f.ell(hx - hr * 0.6, hy + hr * 0.55, hr * 0.35, hr * 0.3, 3, sh=0, line=False, face=True)
    if st == 0:
        def back(f, q):
            f.mark_poly([(30, 76), (80, 72), (80, 96), (30, 96)], 2, clip=q["body"])
        biped(f, tx=54, ty=68, trx=17, tr_y=20, hx=50, hy=38, hr=14, legr=5, legx=6, arm="side", armr=3.5, ears="round", er=6,
              eye="closed", eyer=3, head=head, back=back, mouth=None, bs=1)
    else:
        def front(f, q):
            x, y = q["handpos"]
            f.line([(x - 2, y), (x - 2, y + 16)], 3)
            f.ell(x - 2, y + 20, 4, 4, 0)
        def back(f, q):
            f.mark_ell(q["tx"], q["ty"] - q["tr_y"] * 0.7, q["trx"] * 1.2, 6, 0, clip=q["body"])
        biped(f, tx=54, ty=62, trx=19, tr_y=24, hx=48, hy=28, hr=13, legr=6, legx=7, arm="fwd", armr=4, ears="round", er=6,
              eye="sleepy", eyer=3, head=head, back=back, front=front, mouth=None, bs=2)


# =================================================================== 98 PINCHLET line
def claw(f, x, y, r, ang=0, s=1):
    c = f.ell(x, y, r, r * 0.75, s, ang=ang)
    f.cut_poly(rot([(-r * 1.2, -r * 0.08), (-r * 0.1, r * 0.08), (-r * 1.2, r * 0.38)], ang, x, y))
    return c


@fam("PINCHLET", "CLAWMAJOR")
def crab_line(f, st):
    if st == 0:
        for i in range(3):
            x = 50 + i * 9
            f.stroke([(x, 74), (x + 6, 84), (x + 10, 96)], 1.5, 1.1, 3)
        b = f.ell(56, 72, 22, 13, 1)
        for x in (48, 60):
            f.stroke([(x, 62), (x, 52)], 1.0, 1.0, 3)
            f.eye(x, 50, 3.2, "round", -1)
        f.stroke([(38, 76), (28, 72)], 3, 3, 1)
        claw(f, 20, 66, 15, ang=-20, s=1)
        f.line([(48, 80), (58, 80)], 3, face=True)
    else:
        for i in range(3):
            x = 50 + i * 9
            f.stroke([(x, 72), (x + 6, 84), (x + 10, 96)], 1.8, 1.3, 3)
        f.stroke([(64, 64), (82, 52)], 3.5, 3.5, 2)
        f.ell(86, 44, 13, 10, 2, ang=-30)
        b = f.ell(54, 70, 26, 15, 1)
        spikes(f, arc(54, 70, 26, 15, 200, 340, 6), 4, 4, s=1, side=1)
        for x in (46, 58):
            f.stroke([(x, 58), (x, 48)], 1.0, 1.0, 3)
            f.eye(x, 46, 3.0, "angry", -1)
        f.stroke([(34, 74), (24, 66)], 4, 4, 1)
        f.ell(18, 58, 14, 11, 1, ang=-30, hl=True)
        f.line([(10, 52), (22, 64)], 3)
        f.line([(44, 80), (56, 80)], 3, face=True)


# =================================================================== 100 FUSEBALL line
@fam("FUSEBALL", "FUSEBOMB")
def fuse_line(f, st):
    r = 30 if st == 0 else 36
    cy = 96 - r
    f.stroke([(56, cy - r + 2), (60, cy - r - 10), (68, cy - r - 14)], 1.4, 1.4, 2)
    f.poly(star(70, cy - r - 16, 6, 3, n=5), 0)
    f.poly([(42, cy - r + 6), (58, cy - r + 6), (58, cy - r - 2), (42, cy - r - 2)], 2)
    b = f.ell(50, cy, r, r, 1 if st == 0 else 2, hl=True)
    if st == 0:
        f.eye(40, cy - 2, 3.4, "round", -1)
        f.eye(56, cy - 2, 3.4, "round", -1)
        f.line([(42, cy + 10), (50, cy + 12)], 3, face=True)
    else:
        f.eye(38, cy - 6, 3.6, "angry", -1)
        f.eye(60, cy - 6, 3.6, "angry", 1)
        f.poly(arc(49, cy + 8, 20, 12, 0, 180, 12), 0, face=True)
        for k in range(5):
            x = 34 + k * 7.5
            f.line([(x, cy + 8), (x, cy + 8 + 10 * math.sin(math.pi * (k + 0.5) / 5))], 3, face=True)
        f.line([(29, cy + 8), (69, cy + 8)], 3, face=True)
