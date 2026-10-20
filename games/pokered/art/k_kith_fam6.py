"""KITHBOUND families, pass 2 part A: creatures whose roster concept changed (national 25-80)."""
import math

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_fam import drop, fam, spark
from games.pokered.art.k_kith_fam2 import insect, larva
from games.pokered.art.k_kith_fam3 import feet2, note
from games.pokered.art.k_kith_fam4 import claw, rock
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, fang, fin, flame, horn,
                                          leaf, rot, spikes, spiral, spots, star, stripes, tail_fin)


# ------------------------------------------------------------------ shared helpers
def frill(f, cx, cy, r, a0, a1, n=7, s=0, rib=2):
    """Fan frill around (cx, cy) from angle a0 to a1 with scalloped rim and ribs."""
    pts = [(cx, cy)]
    for i in range(n * 2 + 1):
        a = math.radians(a0 + (a1 - a0) * i / (n * 2))
        rr = r if i % 2 == 0 else r * 0.82
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    j = f.poly(pts, s)
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        f.line([(cx + math.cos(a) * r * 0.25, cy + math.sin(a) * r * 0.25), (cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9)], rib)
    return j


def bell(f, x, y, r, s=2, clapper=True):
    """Bell hanging from (x, y) (top), height about 2r."""
    pts = arc(x, y + r * 0.9, r * 0.75, r * 0.9, 180, 360, 9) + [(x + r * 0.8, y + r * 1.4), (x + r * 1.1, y + r * 1.85),
                                                              (x - r * 1.1, y + r * 1.85), (x - r * 0.8, y + r * 1.4)]
    j = f.poly(pts, s, hl=True)
    f.mark_stroke([(x - r * 1.0, y + r * 1.6), (x + r * 1.0, y + r * 1.6)], max(0.8, r * 0.12), s=1 if s == 2 else 2, clip=j)
    if clapper:
        f.ell(x, y + r * 1.95, r * 0.28, r * 0.25, 3, sh=0)
    return j


def moth(f, cx, cy, span, s_w=1, s_b=2, eyespot=None, low=0.6, ang_up=-35, ang_lo=25, body_l=None, pale=None):
    """Front-facing moth: four wings around a fuzzy body at (cx, cy)."""
    for sg in (-1, 1):
        for a, L, w in ((ang_up, span, span * 0.62), (ang_lo, span * low, span * 0.5 * low / 0.6)):
            aa = a if sg > 0 else 180 - a
            wx, wy = cx + math.cos(math.radians(aa)) * L * 0.5, cy + math.sin(math.radians(aa)) * L * 0.5
            j = f.ell(wx, wy, L * 0.55, w * 0.5, s_w, ang=aa)
            if eyespot and a == ang_up:
                ex, ey = cx + math.cos(math.radians(aa)) * L * 0.62, cy + math.sin(math.radians(aa)) * L * 0.62
                eyespot(f, j, ex, ey, w * 0.22)
            if pale is not None and a == ang_up:
                f.mark_ell(wx + sg * L * 0.12, wy - w * 0.12, L * 0.22, w * 0.14, pale, ang=aa, clip=j)
    bl = body_l or span * 0.55
    b = f.ell(cx, cy + bl * 0.25, span * 0.16, bl * 0.55, s_b)
    for k in range(3):
        f.mark_stroke([(cx - span * 0.2, cy + bl * (0.15 + k * 0.18)), (cx + span * 0.2, cy + bl * (0.15 + k * 0.18))], 0.9,
                      s=1 if s_b == 2 else 2, clip=b)
    return b


def eyespot(f, j, x, y, r):
    f.mark_ell(x, y, r * 1.3, r * 1.3, 3, clip=j)
    f.mark_ell(x, y, r * 0.7, r * 0.7, 0, clip=j)


def antennae(f, x, y, ln, spread=7, s=3, feather=False, curl=True):
    for sg in (-1, 1):
        pts = [(x + sg * 2, y), (x + sg * spread * 0.6, y - ln * 0.6), (x + sg * spread, y - ln)]
        if curl:
            pts.append((x + sg * spread * 1.35, y - ln * 0.9))
        if feather:
            f.stroke(pts, 1.8, 1.2, s)
            spikes(f, pts[:3], 2.5, 2, s=s, side=sg)
        else:
            f.line(pts, s)


def snail_shell(f, cx, cy, r, s=2, ang0=200):
    j = f.ell(cx, cy, r, r * 0.95, s, hl=True)
    spiral(f, cx + r * 0.05, cy, r * 0.85, turns=1.7, s=3, ang0=ang0)
    return j


# =================================================================== 25 ZAPPET line (kite-lizards)
@fam("ZAPPET", "VOLTRIX")
def zap_line(f, st):
    if st == 0:
        def pre(f, q):
            frill(f, q["hx"] + 6, q["hy"] + 2, 27, 150, 340, n=6, s=0)
            for x, y in ((16, 30), (60, 18)):
                spark(f, x, y, 3.5)
        biped(f, tx=58, ty=74, trx=13, tr_y=13, hx=44, hy=52, hr=13, sn=6, snr=5, legr=3.6, legx=5, footl=1.4,
              arm="fwd", armr=2.4, tail="thin", tl=34, trr=2.4, tang=-10, eye="round", eyer=3.2, belly=0, pre=pre, mouth="smile")
    else:
        def pre(f, q):
            frill(f, q["hx"] + 4, q["hy"] + 3, 28, 130, 345, n=8, s=0)
            spark(f, 10, 20, 5)
            spark(f, 70, 6, 5)
        def back(f, q):
            x, y = q["tailinfo"]["tip"]
            for a in (-70, 10):
                f.poly(rot([(0, -2), (7, -5), (5, -1), (12, -2), (4, 4), (5, 1)], a, x, y), 1)
        biped(f, tx=56, ty=64, trx=13, tr_y=20, hx=42, hy=36, hr=11, sn=9, snr=5, legr=4.5, legx=6, footl=1.5,
              arm="guard", armr=3, hand=2.6, tail="thin", tl=34, trr=3, tang=-25, eye="angry", eyer=2.8, belly=0, pre=pre, back=back,
              mouth="open", fangs=1)


# =================================================================== 27 DUSTBALL line (beetle, scorpion)
@fam("DUSTBALL", "SANDSPUR")
def dust_line(f, st):
    if st == 0:
        pel = f.ell(24, 74, 20, 20, 1, hl=True)
        spots(f, pel, 24, 74, 14, 14, 9, 1.4, s=2, seed=27)
        for i in range(3):
            x = 54 + i * 9
            f.stroke([(x, 80), (x + 5, 88), (x + 3, 96)], 1.5, 1.2, 3)
        f.stroke([(48, 78), (40, 76), (38, 70)], 1.5, 1.2, 3)
        sh_ = f.ell(64, 72, 22, 17, 2, hl=True)
        f.line([(52, 60), (76, 86)], 3)
        f.ell(44, 72, 8, 7, 2)
        horn(f, 40, 66, 8, 4, -120, s=2)
        f.eye(42, 71, 2.6, "round", -1)
    else:
        def tailpath():
            return [(74, 76), (90, 66), (92, 44), (80, 28), (64, 26)]
        f.stroke(tailpath(), 5, 3, 1)
        for (x, y) in tailpath()[1:4]:
            f.mark_ell(x, y, 5, 2, 2, clip=len(f.parts) - 1)
        horn(f, 64, 26, 12, 6, 160, curve=-0.6, s=0)
        for i in range(4):
            x = 44 + i * 9
            f.stroke([(x, 78), (x - 4, 88), (x - 2, 96)], 1.4, 1.1, 3)
        b = f.ell(56, 76, 24, 10, 1)
        for k in range(4):
            f.mark_poly([(40 + k * 9, 68), (47 + k * 9, 68), (48 + k * 9, 84), (39 + k * 9, 84)], 2, clip=b)
        spikes(f, [(40, 67), (76, 70)], 4, 4, s=1, side=-1)
        for y0, (cx, cy) in ((78, (14, 70)), (72, (18, 58))):
            f.stroke([(36, y0), (26, y0 - 2), (cx + 6, cy)], 2.5, 2.2, 1)
            claw(f, cx, cy, 9, ang=-20, s=1)
        f.ell(32, 74, 7, 6, 1)
        f.eye(30, 72, 2.4, "angry", -1)
        f.eye(36, 72, 2.2, "angry", -1)


# =================================================================== 35 MOONDROP line (sprites)
@fam("MOONDROP", "LUNAPUFF")
def moon_line(f, st):
    if st == 0:
        leaf(f, 40, 58, 30, 9, 200, s=1)
        leaf(f, 60, 58, 30, 9, -20, s=1)
        for x in (42, 58):
            f.stroke([(x, 86), (x, 94)], 1.4, 1.4, 3)
        b = f.poly([(50, 24)] + arc(50, 66, 22, 24, -30, 210, 14), 0, hl=False, sh=3)
        f.mark_ell(44, 56, 4, 6, 1, clip=b)
        f.eye(43, 66, 3.2, "round", -1)
        f.eye(57, 66, 3.2, "round", -1)
        f.line([(47, 75), (50, 77), (53, 75)], 3, face=True)
    else:
        moth(f, 50, 56, 44, s_w=2, s_b=1, pale=0, body_l=26)
        h = f.ell(50, 40, 12, 11, 1, hl=True)
        for sg in (-1, 1):
            f.stroke([(50 + sg * 4, 31), (50 + sg * 10, 18), (50 + sg * 18, 14)], 1.4, 1.0, 0)
            f.poly(arc(50 + sg * 20, 12, 5, 5, 0, 360, 10), 0)
            f.mark_ell(50 + sg * 21.5, 11, 3.5, 3.5, 2 if sg > 0 else 1)
        f.eye(45, 40, 3, "closed", -1)
        f.eye(55, 40, 3, "closed", -1)
        for x, y in ((14, 86), (86, 84)):
            f.poly(star(x, y, 4, 1.6, n=4), 0)


# =================================================================== 39 TUNEPUFF line (bell birds)
@fam("TUNEPUFF", "BALLADOON")
def tune_line(f, st):
    if st == 0:
        b = f.ell(50, 48, 18, 17, 1, hl=True)
        f.poly([(34, 46), (22, 49), (34, 52)], 0)
        f.stroke([(56, 32), (54, 24), (60, 20)], 1.4, 1.0, 2)
        f.eye(40, 44, 3.2, "round", -1)
        f.eye(52, 44, 2.8, "round", -1)
        bl = f.poly([(20, 60), (80, 60), (86, 92), (14, 92)], 2, hl=True)
        f.poly([(20, 60), (28, 54), (36, 60), (44, 54), (52, 60), (60, 54), (68, 60), (76, 54), (80, 60)], 2)
        f.mark_stroke([(16, 84), (84, 84)], 1.6, s=1, clip=bl)
        note(f, 86, 30, 3)
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            for k, (dx, dy) in enumerate(((4, -26), (14, -20), (22, -10))):
                f.stroke([(hx + 2, hy - hr * 0.6), (hx + dx, hy + dy)], 1.0, 1.0, 2)
                bell(f, hx + dx, hy + dy, 4.2, s=0 if k % 2 else 1)
        bird(f, bx=58, by=64, brx=24, bry=19, tilt=-10, hx=34, hy=42, hr=13, beak=8, beakw=6, wing="fold", wl=26, ww=15,
             tailk="fan", tl=20, tw=12, legl=8, belly=0, eye="closed", eyer=3, head=head)
        note(f, 10, 20, 3)
        note(f, 90, 30, 3)


# =================================================================== 50 BURROWN (periscope worm) / 51 TRIBURROW (drill turtle)
@fam("BURROWN")
def burrown(f, st):
    f.ell(50, 90, 38, 9, 2, group="ground")
    f.ell(50, 90, 18, 5, 3, sh=0)
    b = f.stroke([(50, 92), (52, 70), (50, 46), (44, 32)], 7, 9, 1)
    for y in (82, 72, 62, 52):
        f.mark_stroke([(40, y), (62, y - 1)], 1.0, s=2, clip=b)
    h = f.ell(38, 28, 13, 10, 1, hl=True)
    f.ell(28, 28, 7, 8, 2)
    f.ell(27, 28, 4.5, 5.5, 0)
    f.eye(26, 28, 3.6, "round", -1)
    for x, y in ((14, 82), (86, 80), (20, 92)):
        f.ell(x, y, 3, 2.4, 2)


@fam("TRIBURROW")
def triburrow(f, st):
    def back(f, q):
        sh_ = f.poly(arc(60, 66, 27, 22, 180, 360, 14) + [(87, 68), (33, 68)], 2, hl=True)
        for x, y in ((48, 54), (60, 50), (72, 54), (54, 62), (66, 62)):
            f.mark_poly([(x - 5, y), (x - 2, y - 4), (x + 2, y - 4), (x + 5, y), (x + 2, y + 4), (x - 2, y + 4)], 1, clip=sh_)
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        x = hx - hr * 0.8
        d = horn(f, x, hy + 1, 18, 11, 180, s=0)
        for k in range(3):
            xx = x - 4 - k * 4.5
            f.line([(xx, hy - 4 + k * 1.2), (xx - 2, hy + 5 - k * 1.2)], 2)
    quad(f, bx=60, by=74, brx=27, bry=12, hx=32, hy=72, hr=10, hry=8, sn=0, ears=None, lr=4.5, paws=True,
         tail="stub", trr=3, eye="angry", eyer=2.4, back=back, head=head, neck=5, mouth=None)


# =================================================================== 72 DRIFTJELL line (lanterns)
def lantern_pod(f, x, y, r, s=1, glow=True, face="round"):
    j = f.ell(x, y, r * 0.85, r, s, hl=True)
    for dx in (-0.45, 0, 0.45):
        f.mark_stroke([(x + dx * r, y - r * 0.9), (x + dx * r * 1.2, y + r * 0.9)], max(0.7, r * 0.06), s=2, clip=j)
    if glow:
        f.mark_ell(x, y + r * 0.15, r * 0.45, r * 0.4, 0, clip=j)
    if face:
        f.eye(x - r * 0.22, y + r * 0.1, max(2.0, r * 0.16), face, -1)
        f.eye(x + r * 0.22, y + r * 0.1, max(2.0, r * 0.16), face, -1)
    return j


@fam("DRIFTJELL", "STINGMIRE")
def drift_line(f, st):
    if st == 0:
        for a in range(-160, -10, 25):
            f.line([(50, 30), (50 + math.cos(math.radians(a)) * 26, 30 + math.sin(math.radians(a)) * 20)], 2)
            f.ell(50 + math.cos(math.radians(a)) * 28, 30 + math.sin(math.radians(a)) * 22, 2.5, 2.5, 0)
        f.stroke([(50, 30), (50, 40)], 1.2, 1.2, 2)
        lantern_pod(f, 50, 60, 20)
        for x in (44, 50, 56):
            f.line([(x, 80), (x + (x - 50) * 0.4, 90), (x - 2, 96)], 2)
    else:
        for x, k in ((30, 0), (44, 1), (58, 2), (72, 3)):
            f.stroke([(50, 74), (x, 86), (x - 6 + k * 4, 97)], 2.4, 1.2, 2)
        trunk = f.stroke([(50, 80), (50, 40)], 9, 7, 1)
        for (a, b, c) in (((50, 50), (34, 36), (20, 24)), ((50, 44), (66, 30), (82, 22)), ((50, 40), (46, 22), (52, 8))):
            f.stroke([a, b, c], 3.2, 1.8, 1)
            spikes(f, [a, b, c], 3, 3, s=1, side=1, n=3)
        for x, y in ((18, 36), (84, 34), (34, 20), (64, 14)):
            f.line([(x, y - 8), (x, y - 4)], 3)
            lantern_pod(f, x, y, 6.5, face=None)
        f.eye(45, 60, 3, "angry", -1)
        f.eye(56, 60, 3, "angry", -1)
        f.line([(46, 68), (55, 68)], 3, face=True)


# =================================================================== 74 PEBBLIT (geode crab) / 75 RUBBLEMAN (rubble ape)
def shard(f, x, y, ln, wd, ang, s=0):
    return f.poly(rot([(0, -wd / 2), (ln * 0.75, -wd / 2), (ln, 0), (ln * 0.75, wd / 2), (0, wd / 2)], ang, x, y), s)


@fam("PEBBLIT")
def pebblit(f, st):
    for i in range(3):
        x = 52 + i * 9
        f.stroke([(x, 76), (x + 5, 86), (x + 8, 96)], 1.5, 1.1, 3)
    for k, a in enumerate((-125, -95, -65, -40)):
        shard(f, 50 + k * 8, 64, 22 if k % 2 else 16, 9, a, s=0 if k % 2 else 1)
    g = f.poly(arc(56, 72, 26, 16, 180, 360, 12) + [(82, 76), (30, 76)], 2, hl=True)
    f.mark_poly(arc(56, 72, 18, 9, 180, 360, 10), 1, clip=g)
    f.stroke([(36, 74), (24, 70)], 2.6, 2.6, 2)
    shard(f, 22, 70, 18, 7, 200, s=0)
    shard(f, 22, 72, 14, 6, 165, s=1)
    for x in (48, 60):
        f.stroke([(x, 62), (x, 52)], 1.0, 1.0, 3)
        f.eye(x, 50, 3, "round", -1)


@fam("RUBBLEMAN")
def rubbleman(f, st):
    def pre(f, q):
        f.stroke([(64, 48), (80, 64), (82, 84)], 6, 5, 2)
        rock(f, 82, 88, 8, 7, 5, s=2, cracks=0)
    def back(f, q):
        for x, y in ((50, 50), (62, 62), (46, 70)):
            rock(f, x, y, 5, 4, int(x + y), s=2, cracks=0)
    def front(f, q):
        f.stroke([(42, 50), (26, 64), (22, 84)], 6.5, 5.5, 1)
        rock(f, 20, 88, 10, 8, 11, s=1, cracks=1)
    biped(f, tx=56, ty=60, trx=20, tr_y=20, hx=40, hy=36, hr=12, sn=4, legr=6, legx=7, arm=None, eye="angry", eyer=2.8,
          mouth="line", pre=pre, back=back, front=front, bs=1)
    spikes(f, arc(40, 36, 12, 11, 220, 320, 4), 4, 4, s=2, side=1)


# =================================================================== 77 EMBERCOLT line (ibex)
def curl_horn(f, x, y, r, s=0, big=False):
    pts = []
    n = 14
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(-100 + t * (330 if big else 260))
        rr = r * (1 - 0.55 * t)
        pts.append((x + r * 0.2 + math.cos(a) * rr, y - r * 0.2 + math.sin(a) * rr))
    f.stroke(pts, r * 0.32, r * 0.12, s)
    for p in pts[2:-2:2]:
        f.dot(p[0], p[1], 2)


@fam("EMBERCOLT", "BLAZESTEED")
def ibex_line(f, st):
    big = st == 1
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        curl_horn(f, hx + 3, hy - hr * 0.6, 9 + big * 6, s=0, big=big)
        f.poly([(hx - hr * 0.9, hy + hr * 0.6), (hx - hr * 0.7, hy + hr * 1.6), (hx - hr * 0.3, hy + hr * 0.7)], 2)
        for k, (a, dx, dy) in enumerate(((-20, 4, -0.2), (10, 10, 0.4), (30, 14, 1.2))):
            flame(f, hx + dx, hy + hr * dy, 9 + big * 3, 13 + big * 5, ang=a + 40, n=2 + big, s=1 if not big else 0, inner=False)
    quad(f, bx=60, by=64 if not big else 60, brx=19 + big * 6, bry=12 + big, hx=34 if not big else 30, hy=40 if not big else 34,
         hr=11 if not big else 10, sn=6, snr=5, ears="point", er=5, lr=2.8 + big * 0.6, tail="stub", trr=3,
         eye="round" if not big else "angry", eyer=2.8, head=head, neck=5, mouth="line", belly=0)


# =================================================================== 79 DAWDLUG line (sloths)
def sloth_face(f, hx, hy, hr, eye):
    f.mark_ell(hx - hr * 0.3, hy + hr * 0.1, hr * 0.7, hr * 0.55, 0, clip=None)
    for dx in (-0.6, 0.0):
        f.mark_ell(hx + hr * dx, hy, hr * 0.26, hr * 0.17, 2, ang=15)
    f.eye(hx - hr * 0.6, hy, max(2.0, hr * 0.15), eye, -1)
    f.eye(hx, hy, max(2.0, hr * 0.15), eye, -1)
    f.ell(hx - hr * 0.3, hy + hr * 0.35, 1.8, 1.3, 3, sh=0, face=True)
    f.line([(hx - hr * 0.55, hy + hr * 0.55), (hx - hr * 0.3, hy + hr * 0.65), (hx - hr * 0.05, hy + hr * 0.55)], 3, face=True)


@fam("DAWDLUG", "DAWDLORD")
def sloth_line(f, st):
    if st == 0:
        f.stroke([(2, 14), (98, 20)], 3.5, 3.5, 2, group="branch")
        leaf(f, 86, 19, 12, 4, 60, s=1)
        for (a, b) in (((44, 50), (36, 18)), ((62, 52), (66, 20))):
            f.stroke([a, b], 3.6, 3.2, 1)
            for k in range(3):
                f.stroke([(b[0] - 2 + k * 2, b[1] + 2), (b[0] - 3 + k * 2, b[1] - 5)], 0.8, 0.8, 3)
        for (a, b) in (((44, 72), (40, 90)), ((60, 72), (66, 88))):
            f.stroke([a, b], 3.4, 3, 1)
        b = f.ell(52, 64, 16, 18, 1, hl=True)
        h = f.ell(50, 44, 13, 11, 1)
        f.mark_ell(47, 45, 9, 7, 0, clip=h)
        sloth_face(f, 50, 44, 12, "sleepy")
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            c = f.poly(arc(hx, hy - hr * 0.7, hr * 0.95, hr * 0.7, 180, 360, 10) + [(hx + hr * 0.95, hy - hr * 0.6), (hx - hr * 0.95, hy - hr * 0.6)], 0)
            for k in range(4):
                f.line([(hx - hr * 0.6 + k * hr * 0.4, hy - hr * 0.62), (hx - hr * 0.5 + k * hr * 0.33, hy - hr * 1.25)], 2)
            spikes(f, arc(hx, hy - hr * 0.7, hr * 0.95, hr * 0.7, 190, 350, 5), 3, 2.5, s=0, side=1)
            f.mark_ell(hx - hr * 0.3, hy + hr * 0.1, hr * 0.7, hr * 0.55, 0, clip=q["headid"])
            sloth_face(f, hx, hy, hr, "sleepy")
        def front(f, q):
            x, y = q["handpos"]
            for k in range(3):
                horn(f, x - 2 + k * 2.5, y + 2, 8, 2.2, 100 - k * 8, curve=0.6, s=0)
        def pre(f, q):
            x, y = 80, 80
            for k in range(3):
                horn(f, x - 2 + k * 2.5, y + 2, 7, 2, 100 - k * 8, curve=0.6, s=2)
        biped(f, tx=54, ty=62, trx=18, tr_y=22, hx=46, hy=34, hr=13, legr=5, legx=6, arm="side", armr=3.6, ears=None,
              eye=None, mouth=None, head=head, front=front, belly=None, bs=1)
