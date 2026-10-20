"""KITHBOUND families, part 3 (national 29-60)."""
import math

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_fam import fam, spark
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, cog, fang, fin,
                                          flame, horn, leaf, rot, spikes, spiral, spots, star, stripes,
                                          tail_fin)


def feet2(f, x0, x1, y, r, s=1):
    for x in (x1, x0):
        f.ell(x, y, r * 1.2, r * 0.75, s, group="feet%d" % x)


def fuzzball(f, cx, cy, r, s=1, n=16, amp=3.0):
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n
        rr = r + (amp if i % 2 == 0 else 0)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return f.poly(pts, s)


def quills(f, cx, cy, rx, ry, a0, a1, n, ln, s=2, wd=None):
    """Quill fan: long triangles radiating from an ellipse arc."""
    ids = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / max(1, n - 1))
        x, y = cx + math.cos(a) * rx * 0.7, cy + math.sin(a) * ry * 0.7
        ids.append(horn(f, x, y, ln + rx * 0.3, wd or ln * 0.55, math.degrees(a), s=s))
    return ids


# =================================================================== 29 PRICKLA / 32 BRISTLO lines
def hedgehog(f, st, qs, horned):
    if st < 2:
        big = st == 1
        def pre(f, q):
            quills(f, 62, 66, 22 + 3 * big, 16 + 2 * big, -170, -10, 8 + 2 * big, 10 + 4 * big, s=qs)
        def head(f, q):
            if big and not horned:
                quills(f, q["hx"] + 2, q["hy"] - 6, 6, 6, -120, -40, 4, 7, s=qs)
            if horned:
                horn(f, q["hx"] - 6, q["hy"] - q["hr"] * 0.75, 7 + 6 * big, 5, -115, curve=-0.4, s=0)
        quad(f, bx=60, by=72 - 2 * big, brx=22 + 3 * big, bry=15 + 2 * big, hx=34, hy=62 - 4 * big, hr=12 + big, sn=6, snr=5,
             ears="round" if not horned else "point", er=7, ear_in=2, lr=3.6 + big, tail=None, eye="round" if not horned else "angry",
             eyer=2.8, belly=0, pre=pre, head=head, mouth="smile" if not horned else "line", fangs=int(horned and big))
    else:
        def pre(f, q):
            quills(f, 62, 48, 18, 20, -150, 30, 9, 14, s=qs)
            if horned:
                tail(f, "club", 66, 82, 26, 3.5, 1, -10)
        def back(f, q):
            for i in range(4):
                f.mark_stroke([(44, 52 + i * 7), (60, 52 + i * 7)], 1.0, s=2, clip=q["body"])
        def head(f, q):
            if horned:
                horn(f, q["hx"] - 7, q["hy"] - q["hr"] * 0.7, 14, 7, -110, curve=-0.4, s=0)
                horn(f, q["hx"] + 4, q["hy"] - q["hr"] * 0.85, 9, 5, -80, s=0)
            else:
                quills(f, q["hx"] + 1, q["hy"] - 9, 8, 6, -135, -45, 5, 9, s=0)
        biped(f, tx=54, ty=64, trx=17, tr_y=21, hx=44, hy=32, hr=13, sn=7, legr=7, legx=7, arm="guard" if horned else "hips",
              armr=4.5, hand=4, ears="point", er=6, eye="angry", eyer=2.8, belly=0, pre=pre, back=back, head=head,
              mouth="open" if horned else "line", fangs=2 if horned else 0)


@fam("PRICKLA", "QUILLESS", "SPIKEQUEEN")
def prickla_line(f, st):
    hedgehog(f, st, 1, False)


@fam("BRISTLO", "QUILLORD", "SPIKEKING")
def bristlo_line(f, st):
    hedgehog(f, st, 2, True)


# =================================================================== 35 MOONDROP line
@fam("MOONDROP", "LUNAPUFF")
def moon_line(f, st):
    if st == 0:
        feet2(f, 38, 62, 94, 6, 0)
        ears(f, "moon", 36, 46, 12, 1, ang=-30)
        ears(f, "moon", 64, 44, 12, 1, ang=30)
        b = f.ell(50, 70, 24, 22, 0, group="body")
        f.mark_ell(50, 82, 8, 6, 1, clip=b)
        spiral(f, 50, 50, 4, turns=1.2, s=3)
        f.eye(42, 68, 3, "round", -1)
        f.eye(56, 68, 3, "round", -1)
        f.line([(46, 77), (49, 78), (52, 77)], 3, face=True)
        f.ell(36, 74, 2.5, 1.6, 1, sh=0, line=False)
    else:
        for sgn in (-1, 1):
            f.poly([(50 + sgn * 18, 50), (50 + sgn * 40, 28), (50 + sgn * 34, 44), (50 + sgn * 42, 52), (50 + sgn * 20, 64)], 1)
        feet2(f, 38, 62, 94, 7, 0)
        ears(f, "moon", 36, 30, 14, 1, ang=-30)
        ears(f, "moon", 64, 28, 14, 1, ang=30)
        b = f.ell(50, 64, 22, 30, 0, group="body")
        f.mark_ell(50, 78, 10, 10, 1, clip=b)
        spiral(f, 50, 36, 5, turns=1.3, s=3)
        f.eye(42, 56, 3, "round", -1)
        f.eye(57, 56, 3, "round", -1)
        f.line([(46, 66), (50, 68), (54, 66)], 3, face=True)
        for x, y in ((24, 74), (76, 74)):
            f.ell(x, y, 4, 6, 0)


# =================================================================== 37 CINDERKIT line
@fam("CINDERKIT", "PYRELYNX")
def cinder_line(f, st):
    if st == 0:
        def tl(f, q):
            x, y = q["tailinfo"]["tip"]
            f.ell(x, y, 4.5, 4.5, 2)
            flame(f, x, y - 3, 7, 10, n=2, s=1, inner=False)
        quad(f, bx=60, by=74, brx=20, bry=13, hx=35, hy=56, hr=15, sn=2, ears="point", er=10, ear_in=2,
             lr=3.5, tail="thin", tl=28, trr=2, tang=-60, eye="round", eyer=3.2, belly=0, back=tl, neck=0)
        f.line([(18, 62), (12, 60)], 3, face=True)
        f.line([(18, 64), (12, 66)], 3, face=True)
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            for x, y, a in ((hx - hr * 0.4, hy - hr * 1.3, -20), (hx + hr * 0.55, hy - hr * 1.4, 10)):
                flame(f, x, y, 7, 13, ang=a, n=2, s=1, inner=False)
            spikes(f, [(hx + hr * 0.2, hy + hr * 0.9), (hx - hr * 0.6, hy + hr * 1.05)], 5, 4, s=0, side=-1)
        quad(f, bx=60, by=68, brx=26, bry=15, hx=31, hy=46, hr=13, sn=4, snr=5, ears="point", er=10, ear_in=2,
             lr=5, tail="stub", trr=4, eye="slit", eyer=3, belly=0, head=head, brow=1)


# =================================================================== 39 TUNEPUFF line
def note(f, x, y, r=3):
    f.ell(x, y, r, r * 0.8, 3, sh=0, line=False)
    f.line([(x + r - 0.5, y), (x + r - 0.5, y - r * 3.5), (x + r * 2.2, y - r * 2.6)], 3)


@fam("TUNEPUFF", "BALLADOON")
def tune_line(f, st):
    if st == 0:
        feet2(f, 40, 58, 94, 5, 2)
        b = f.ell(50, 68, 25, 24, 1, group="body", hl=True)
        bird_wing(f, 66, 66, 14, 9, 30, n=3, s=2)
        f.stroke([(52, 46), (48, 36), (56, 32), (58, 38), (53, 40)], 1.6, 1.0, 2)
        f.poly([(26, 66), (16, 70), (26, 73)], 0)
        f.eye(34, 62, 3.2, "round", -1)
        f.eye(46, 62, 2.8, "round", -1)
        note(f, 14, 48, 3)
    else:
        ears(f, "long", 66, 32, 18, 1, ang=30)
        feet2(f, 38, 62, 95, 7, 2)
        b = f.ell(50, 60, 34, 34, 1, group="body", hl=True)
        ears(f, "long", 40, 30, 20, 1, ang=-20, inner=2)
        f.stroke([(50, 26), (44, 16), (54, 12), (57, 18), (51, 20)], 2.0, 1.2, 2)
        f.eye(36, 52, 3.4, "closed", -1)
        f.eye(54, 52, 3.4, "closed", -1)
        f.ell(42, 70, 7, 8, 3, line=False, sh=0, face=True)
        f.ell(42, 74, 4, 3, 2, line=False, sh=0, face=True)
        note(f, 14, 40, 3.5)
        note(f, 86, 30, 3.5)


# =================================================================== 41 DUSKBIT line
@fam("DUSKBIT", "FANGWING")
def dusk_line(f, st):
    if st == 0:
        bat_wing(f, 56, 54, 38, 26, -20, n=3, s=2)
        bat_wing(f, 44, 54, 38, 26, 200, n=3, s=2)
        ears(f, "tall", 40, 44, 10, 1, ang=-20)
        ears(f, "tall", 60, 44, 10, 1, ang=20)
        f.ell(50, 58, 14, 15, 1, group="body")
        f.eye(44, 54, 3, "round", -1)
        f.eye(56, 54, 3, "round", -1)
        f.line([(45, 64), (55, 64)], 3, face=True)
        fang(f, 47, 64, 3.5, 2.5)
        fang(f, 53, 64, 3.5, 2.5)
        f.stroke([(46, 72), (45, 80)], 1.0, 1.0, 3)
        f.stroke([(54, 72), (55, 80)], 1.0, 1.0, 3)
    else:
        bat_wing(f, 58, 46, 46, 34, -25, n=4, s=2, torn=True)
        bat_wing(f, 42, 46, 46, 34, 205, n=4, s=2, torn=True)
        ears(f, "tall", 38, 30, 12, 1, ang=-25)
        ears(f, "tall", 62, 30, 12, 1, ang=25)
        b = f.ell(50, 54, 19, 24, 1, group="body")
        f.ell(50, 60, 12, 12, 3, line=False, sh=0, face=True)
        f.ell(50, 66, 7, 5, 2, line=False, sh=0, face=True)
        fang(f, 43, 49, 9, 5)
        fang(f, 57, 49, 9, 5)
        f.eye(43, 40, 3, "angry", -1)
        f.eye(57, 40, 3, "angry", 1)
        f.stroke([(44, 76), (42, 88)], 1.2, 1.0, 3)
        f.stroke([(56, 76), (58, 88)], 1.2, 1.0, 3)


# =================================================================== 43 ROOTLET line
def turnip(f, cx, cy, r, s=1, root=True):
    if root:
        f.stroke([(cx, cy + r), (cx + 2, cy + r * 1.6)], 1.2, 0.8, 3)
    b = f.poly(arc(cx, cy, r, r, 160, 380, 14) + [(cx, cy - r * 1.25)], s)
    return b


@fam("ROOTLET", "REEKBLOOM", "ROTBLOSSOM")
def root_line(f, st):
    if st == 0:
        for a in (-120, -90, -60):
            leaf(f, 50, 44, 22, 6, a, s=2)
        for x in (40, 58):
            f.stroke([(x, 80), (x - 3, 96)], 2.0, 1.4, 2, group="legs")
        b = f.ell(50, 64, 22, 20, 1, group="body", hl=True)
        f.mark_poly([(30, 70), (70, 70), (64, 84), (36, 84)], 0, clip=b)
        f.eye(42, 60, 3, "round", -1)
        f.eye(56, 60, 3, "round", -1)
        f.line([(46, 70), (50, 72), (54, 70)], 3, face=True)
    elif st == 1:
        for a in (-150, -30):
            leaf(f, 50, 44, 24, 7, a, s=2)
        f.stroke([(50, 44), (56, 26), (66, 24)], 2.2, 1.6, 2)
        bell = f.poly([(58, 20), (78, 22), (84, 42), (76, 38), (70, 44), (64, 38), (56, 42)], 1)
        spots(f, bell, 70, 32, 7, 5, 3, 1.8, s=2, seed=4)
        for x in (78, 86):
            f.line([(x, 50), (x + 2, 54), (x, 58), (x + 2, 62)], 2)
        for x in (38, 60):
            f.stroke([(x, 80), (x - 3, 96)], 2.4, 1.6, 2, group="legs")
        b = f.ell(48, 64, 24, 21, 1, group="body", hl=True)
        f.mark_poly([(26, 70), (70, 70), (64, 86), (32, 86)], 0, clip=b)
        f.eye(38, 60, 3, "sleepy", -1)
        f.eye(54, 60, 3, "sleepy", -1)
        f.line([(40, 72), (44, 70), (48, 72)], 3, face=True)
    else:
        for x in (36, 62):
            f.stroke([(x, 82), (x - 3, 97)], 3, 2, 2, group="legs")
        b = f.ell(50, 74, 22, 18, 1, group="body")
        pet = []
        for i in range(5):
            a = -90 + i * 72 + 36
            px, py = 50 + math.cos(math.radians(a)) * 24, 40 + math.sin(math.radians(a)) * 16
            pid = f.ell(px, py, 18, 11, 1, ang=a)
            pet.append(pid)
            spots(f, pid, px, py, 8, 4, 3, 2.2, s=2, seed=i + 3)
        f.ell(50, 40, 12, 8, 3, sh=0)
        spikes(f, arc(50, 40, 11, 7, 190, 350, 5), 5, 3, s=2, side=1)
        f.eye(42, 74, 3, "angry", -1)
        f.eye(58, 74, 3, "angry", 1)
        f.line([(44, 84), (56, 84)], 3, face=True)


# =================================================================== 46 MOLDCRAB line
def mushroom(f, x, y, r, stem=6, s=2, spot_s=0, ang=0):
    f.stroke([(x, y), (x, y - stem)], r * 0.32, r * 0.32, 0)
    cid = f.poly(rot(arc(0, 0, r, r * 0.75, 180, 360, 12) + [(r, 0), (-r, 0)], ang, x, y - stem), s)
    for dx in (-0.45, 0.15, 0.6):
        f.mark_ell(*rot([(r * dx, -r * 0.4)], ang, x, y - stem)[0], r * 0.16, r * 0.14, spot_s, clip=cid)
    return cid


@fam("MOLDCRAB", "FUNGIPEDE")
def mold_line(f, st):
    if st == 0:
        for i in range(3):
            x = 52 + i * 9
            f.stroke([(x, 78), (x + 6, 86), (x + 9, 96)], 1.4, 1.1, 3)
        b = f.ell(56, 76, 24, 12, 1, group="body")
        for x, y in ((24, 74), (32, 82)):
            f.stroke([(40, 80), (x + 4, y)], 2.0, 2.0, 1)
            f.ell(x, y, 5, 4, 1)
            f.cut_poly([(x - 7, y - 1), (x - 1, y + 0.5), (x - 7, y + 2)])
        mushroom(f, 48, 66, 11, 6, 2, 0, ang=-12)
        mushroom(f, 68, 66, 13, 7, 2, 0, ang=10)
        f.eye(38, 72, 2.6, "dot", -1)
        f.eye(44, 71, 2.4, "dot", -1)
    else:
        for i in range(6):
            x = 30 + i * 9
            f.stroke([(x, 76), (x - 2, 86), (x + 1, 97)], 1.5, 1.2, 3)
        f.ell(50, 74, 32, 12, 2, group="body")
        cid = f.poly(arc(50, 62, 46, 38, 180, 360, 18) + [(96, 64), (4, 64)], 1, hl=True)
        spots(f, cid, 50, 44, 30, 12, 6, 3.6, s=0, seed=9)
        f.ell(22, 72, 8, 6, 2, group="head")
        f.eye(20, 71, 2.8, "round", -1)
        f.eye(27, 71, 2.6, "round", -1)
        f.stroke([(18, 76), (14, 82)], 1.0, 1.0, 3)


# =================================================================== 48 GNATBALL line
@fam("GNATBALL", "DUSTMOTH")
def gnat_line(f, st):
    if st == 0:
        for x in (40, 58):
            f.stroke([(x, 80), (x - 2, 96)], 1.0, 1.0, 3)
        for d in (-1, 1):
            f.stroke([(50 + d * 6, 46), (50 + d * 12, 32), (50 + d * 18, 30)], 0.9, 0.9, 3)
        b = fuzzball(f, 50, 66, 24, 1, n=18, amp=4)
        f.eye(41, 64, 6, "round", -1)
        f.eye(59, 64, 6, "round", -1)
        f.line([(46, 80), (50, 82), (54, 80)], 3, face=True)
    else:
        for side, ang in ((1, -30), (1, 20), (-1, 210), (-1, 160)):
            big = ang in (-30, 210)
            L = 40 if big else 30
            wid = f.ell(50 + math.cos(math.radians(ang)) * L * 0.5, 54 + math.sin(math.radians(ang)) * L * 0.5, L * 0.55, 15 if big else 11, 1, ang=ang)
            cx, cy = 50 + math.cos(math.radians(ang)) * L * 0.6, 54 + math.sin(math.radians(ang)) * L * 0.6
            f.mark_ell(cx, cy, 6, 6, 3, clip=wid)
            f.mark_ell(cx, cy, 3, 3, 0, clip=wid)
            spots(f, wid, cx, cy, L * 0.4, 6, 4, 1.0, s=2, seed=int(ang + 400))
        f.ell(50, 62, 7, 18, 2, group="body")
        for d in (-1, 1):
            f.stroke([(50 + d * 3, 38), (50 + d * 12, 24), (50 + d * 18, 20)], 1.6, 1.0, 2)
            spikes(f, [(50 + d * 3, 38), (50 + d * 12, 24)], 3, 2.5, s=2, side=d)
        f.ell(50, 40, 8, 7, 1, group="head")
        f.eye(46, 40, 3, "round", -1)
        f.eye(54, 40, 3, "round", 1)


# =================================================================== 50 BURROWN line
def mole(f, x, y, r, eye="dot"):
    hid = f.poly(arc(x, y, r, r * 1.3, 180, 360, 12) + [(x + r, y + r * 0.8), (x - r, y + r * 0.8)], 1)
    f.ell(x - r * 0.1, y - r * 0.25, r * 0.42, r * 0.32, 2, sh=0)
    f.eye(x - r * 0.45, y - r * 0.75, max(2.2, r * 0.22), eye, -1)
    f.eye(x + r * 0.3, y - r * 0.75, max(2.0, r * 0.2), eye, -1)
    return hid


def mound(f, cx, cy, rx, ry, seed):
    m = f.poly(blobpoly(cx, cy, rx, ry, n=7, amp=0.12, seed=seed), 2)
    for i in range(5):
        f.mark_ell(cx - rx * 0.6 + i * rx * 0.3, cy - ry * 0.2 + (i % 2) * ry * 0.3, 2.2, 1.6, 3, clip=m)
    return m


@fam("BURROWN", "TRIBURROW")
def burrow_line(f, st):
    if st == 0:
        mole(f, 50, 74, 15)
        f.ell(50, 90, 36, 12, 2, group="mound")
        spots(f, len(f.parts) - 1, 50, 92, 26, 6, 6, 2, s=3, seed=2)
    else:
        for x, y, r in ((30, 76, 12), (70, 75, 12), (50, 66, 14)):
            mole(f, x, y, r)
        f.ell(50, 88, 44, 14, 2, group="mound")
        spots(f, len(f.parts) - 1, 50, 90, 34, 7, 8, 2, s=3, seed=3)


# =================================================================== 52 COINCAT line
def coin(f, x, y, r):
    f.ell(x, y, r, r, 0, hl=False)
    f.line([(x, y - r * 0.5), (x, y + r * 0.5)], 2)


@fam("COINCAT", "SLYPANTHER")
def coincat_line(f, st):
    if st == 0:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            f.mark_poly([(hx - hr, hy + hr * 0.7), (hx + hr, hy + hr * 0.75), (hx + hr, hy + hr), (hx - hr, hy + hr)], 2, clip=q["headid"])
            coin(f, hx - hr * 0.2, hy + hr * 1.15, 4)
            f.cut_poly([(hx + hr * 0.5, hy - hr * 1.9), (hx + hr * 0.4, hy - hr * 1.35), (hx + hr * 0.75, hy - hr * 1.5)])
            f.line([(hx - hr * 1.0, hy + hr * 0.25), (hx - hr * 1.6, hy + hr * 0.1)], 3, face=True)
        quad(f, bx=62, by=74, brx=19, bry=13, hx=38, hy=56, hr=14, sn=2, ears="point", er=10, ear_in=2,
             lr=3.6, tail="thin", tl=30, trr=2, tang=-80, eye="slit", eyer=3.2, belly=0, head=head, neck=0, mouth="smile")
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            coin(f, hx + 2, hy + hr * 1.25, 3.5)
        quad(f, bx=60, by=68, brx=30, bry=12, bs=2, hx=24, hy=52, hr=11, sn=3, ears="point", er=8, ear_in=1,
             lr=3.6, ll=None, tail="ring", tl=34, trr=2.2, tang=-35, eye="slit", eyer=2.8, head=head, brow=1, belly=1)


# =================================================================== 54 BEWILDUCK line
@fam("BEWILDUCK", "BRAINWADER")
def duck_line(f, st):
    if st == 0:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            f.poly([(hx - hr * 0.7, hy + 1), (hx - hr * 1.6, hy + 4), (hx - hr * 1.5, hy + 8), (hx - hr * 0.6, hy + 7)], 0)
            f.line([(hx + 1, hy - hr * 0.95), (hx + 3, hy - hr * 1.4), (hx + 6, hy - hr * 1.2)], 3)
            f.line([(hx + hr * 1.3, hy - hr * 1.5), (hx + hr * 1.5, hy - hr * 1.8), (hx + hr * 1.8, hy - hr * 1.6), (hx + hr * 1.6, hy - hr * 1.2), (hx + hr * 1.6, hy - hr * 1.0)], 3)
            f.dot(hx + hr * 1.6, hy - hr * 0.7)
        def pre(f, q):
            f.stroke([(62, 62), (70, 50), (62, 40)], 3.2, 3.0, 2)
            f.ell(61, 39, 4, 4, 2)
        def front(f, q):
            f.stroke([(42, 62), (28, 52), (33, 40)], 3.4, 3.0, 1)
            f.ell(34, 39, 4.5, 4.5, 1)
        biped(f, tx=52, ty=72, trx=16, tr_y=16, hx=48, hy=42, hr=14, legr=4, legx=5, footl=1.5, fs=0, arm=None,
              eye="round", eyer=3.2, belly=0, head=head, front=front, pre=pre, mouth=None, bs=1)
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            f.poly([(hx - hr * 0.7, hy), (hx - hr * 2.6, hy + 3), (hx - hr * 2.5, hy + 6), (hx - hr * 0.6, hy + 6)], 0)
            f.ell(hx - hr * 0.1, hy - hr * 0.8, 3.5, 3.5, 0, hl=False)
            for a in (-150, -90, -30):
                f.line([(hx - hr * 0.1 + math.cos(math.radians(a)) * 5, hy - hr * 0.8 + math.sin(math.radians(a)) * 5),
                        (hx - hr * 0.1 + math.cos(math.radians(a)) * 8, hy - hr * 0.8 + math.sin(math.radians(a)) * 8)], 3)
        biped(f, tx=56, ty=56, trx=14, tr_y=18, hx=44, hy=22, hr=10, legr=2.6, legx=4, footl=1.8, fs=0, legy=68,
              arm="side", armr=3, eye="angry", eyer=2.6, belly=0, head=head, neck=4, mouth=None, tail="stub", trr=4)


# =================================================================== 56 SCRAPPET line
@fam("SCRAPPET", "FURYBOON")
def monkey_line(f, st):
    if st == 0:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            spikes(f, arc(hx, hy, hr, hr, 210, 330, 4), 8, 6, s=2, side=1)
            f.mark_ell(hx - hr * 0.3, hy + hr * 0.25, hr * 0.6, hr * 0.5, 0, clip=q["headid"])
        b = biped(f, tx=54, ty=70, trx=20, tr_y=18, hx=46, hy=44, hr=16, legr=4.5, legx=8, arm="guard", armr=3.2, hand=4,
                  ears="round", er=7, ear_in=0, tail="coil", tl=20, trr=1.6, tang=-20, eye="angry", eyer=3, head=head, mouth="open", belly=None)
    else:
        def head(f, q):
            hx, hy, hr = q["hx"], q["hy"], q["hr"]
            f.poly(blobpoly(hx + 4, hy + 4, hr * 1.5, hr * 1.4, n=9, amp=0.2, seed=5), 2)
        def front(f, q):
            for x, y in (q["farhand"], q["handpos"]):
                h = f.ell(x, y, 6, 6, 0)
                f.line([(x - 5, y - 2), (x + 5, y - 3)], 2)
                f.line([(x - 5, y + 2), (x + 5, y + 1)], 2)
        biped(f, tx=54, ty=64, trx=20, tr_y=21, hx=40, hy=34, hr=12, sn=5, legr=5.5, legx=8, arm="guard", armr=4.2, hand=None,
              ears="round", er=6, tail="thin", tl=22, trr=2, tang=-60, eye="angry", eyer=2.8, pre=head, front=front, mouth="open", fangs=2, belly=1, bs=1)


# =================================================================== 58 PYREPUP line
@fam("PYREPUP", "BLAZEHOUND")
def pyre_line(f, st):
    if st == 0:
        def back(f, q):
            spots(f, q["body"], 62, 70, 14, 7, 5, 2.4, s=2, seed=8)
            hx, hy = q["hx"], q["hy"]
            r = f.poly(blobpoly(hx + 10, hy + 12, 12, 9, n=6, amp=0.22, seed=3), 0)
        quad(f, bx=60, by=72, brx=21, bry=14, hx=34, hy=54, hr=14, sn=6, snr=5, ears="fold", er=9,
             lr=4, tail="bushy", tl=16, trr=5, tang=-50, eye="round", eyer=3, back=back, neck=0)
    else:
        def pre(f, q):
            for a, (x, y) in zip((-80, -50, -20, 10, 40), ((36, 30), (46, 30), (54, 36), (58, 46), (58, 58))):
                flame(f, x, y, 12, 18, ang=a + 20, n=3, s=0, inner=False)
        def back(f, q):
            spots(f, q["body"], 62, 64, 18, 8, 6, 2.6, s=2, seed=8)
        quad(f, bx=60, by=66, brx=27, bry=16, hx=30, hy=44, hr=13, sn=9, snr=6, ears="point", er=9, ear_in=2,
             lr=5.5, tail="flame", tl=22, trr=3, tang=-40, ttip=0, eye="angry", eyer=2.8, pre=pre, back=back, mouth="open", fangs=1)


# =================================================================== 60 SWIRLTAD line (tadpole)
@fam("SWIRLTAD")
def swirltad(f, st):
    tail_fin(f, 62, 66, 30, 22, ang=-15, s=1, fork=0.2)
    f.ell(30, 92, 4, 3, 1)
    b = f.ell(44, 66, 24, 22, 1, group="body", hl=True)
    f.mark_ell(46, 74, 12, 10, 0, clip=b)
    spiral(f, 46, 74, 9, turns=1.8, s=3)
    f.eye(34, 56, 3.4, "round", -1)
    f.eye(48, 54, 3.0, "round", -1)
    f.line([(24, 68), (28, 70)], 3, face=True)
