"""KITHBOUND families, part 2 (bugs, birds, rodents, snakes)."""
import math

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_fam import fam, spark
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, cog, fang, fin,
                                          flame, horn, leaf, rot, spikes, spiral, spots, star, stripes,
                                          tail_fin)


# =================================================================== bug helpers
def larva(f, x0, y0, n, r0, r1, dx, dy=0.0, s=1, bands=None, wave=3.0, feet=True):
    """Chain of segments from the tail (x0, y0) toward the head (step dx, dy)."""
    ids = []
    for i in range(n):
        t = i / max(1, n - 1)
        r = r1 + (r0 - r1) * t
        x = x0 + dx * i
        y = y0 + dy * i - math.sin(t * math.pi) * wave
        if feet:
            f.ell(x - 1, y + r * 0.95, r * 0.3, r * 0.32, 3, group="feet", sh=0)
        sid = f.ell(x, y, r, r * 0.95, (bands if (bands is not None and i % 2) else s))
        ids.append((sid, x, y, r))
    return ids


def insect(f, hx, hy, hr, thx, thy, thr, ab, abr, abang=20, s=1, abs_=None, stripes_n=0,
           legs=6, legs_s=3, ant=0, antc=0.0, stinger=0):
    """Head, thorax and abdomen facing left; ab = abdomen length."""
    a = math.radians(abang)
    ax, ay = thx + math.cos(a) * (thr + ab * 0.45), thy + math.sin(a) * (thr + ab * 0.45)
    if stinger:
        ex, ey = thx + math.cos(a) * (thr + ab * 0.95), thy + math.sin(a) * (thr + ab * 0.95)
        horn(f, ex - math.cos(a) * 2, ey - math.sin(a) * 2, stinger, stinger * 0.45, abang, s=0)
    for i in range(legs // 2):
        lx = thx - thr * 0.5 + i * thr * 0.6
        f.stroke([(lx, thy), (lx - 4 + i * 3, thy + thr + 5), (lx - 7 + i * 5, thy + thr + 11)], 1.2, 1.0, legs_s, group="legs")
    abid = f.ell(ax, ay, ab * 0.55, abr, abs_ if abs_ is not None else s, ang=abang, group="ab")
    if stripes_n:
        for i in range(stripes_n):
            t = (i + 0.8) / (stripes_n + 0.6) - 0.5
            cx, cy = ax + math.cos(a) * ab * t, ay + math.sin(a) * ab * t
            f.mark_ell(cx, cy, 1.8, abr * 1.2, 3 if s < 2 else 0, ang=abang, clip=abid)
    th = f.ell(thx, thy, thr, thr * 0.9, s, group="th")
    if ant:
        for d in (0, 5):
            f.stroke([(hx + d * 0.6, hy - hr * 0.7), (hx - ant * 0.4 + d, hy - hr - ant * 0.6 - antc),
                      (hx - ant * 0.7 + d * 1.2, hy - hr - ant)], 0.8, 0.8, 3, group="ant")
    hd = f.ell(hx, hy, hr, hr * 0.95, s, group="head")
    return dict(ab=abid, th=th, head=hd, ax=ax, ay=ay)


# =================================================================== 10 SILKLING line
@fam("SILKLING", "COCOONIX", "GOSSAMIRE")
def silk_line(f, st):
    if st == 0:
        larva(f, 84, 82, 5, 10, 6.5, -10, wave=6, bands=2)
        f.stroke([(26, 76), (18, 84), (26, 90), (12, 94), (6, 86)], 1.0, 1.0, 2)
        f.ell(32, 66, 14, 13, 1, group="head")
        for x, y in ((26, 53), (34, 52), (42, 55)):
            horn(f, x, y + 2, 6, 3.5, -100, s=0)
        f.eye(27, 64, 3.2, "round", -1)
        f.eye(37, 63, 2.8, "round", -1)
        f.line([(24, 73), (28, 75), (32, 73)], 3, face=True)
    elif st == 1:
        f.stroke([(50, 0), (50, 14)], 1.0, 1.0, 3)
        pid = f.ell(50, 54, 20, 40, 1)
        for i in range(6):
            y = 22 + i * 11
            f.mark_stroke([(30, y + 6), (70, y - 4)], 1.1, s=2, clip=pid)
        f.mark_ell(50, 52, 10, 7, 0, clip=pid)
        f.eye(50, 53, 4, "sleepy", -1)
        f.poly([(42, 12), (58, 12), (54, 18), (46, 18)], 2)
    else:
        bug_wing(f, 52, 46, 44, 18, -60, s=0, veins=3)
        bug_wing(f, 54, 50, 40, 15, -15, s=0, veins=3)
        insect(f, 34, 48, 10, 50, 54, 8, 26, 5.5, abang=35, s=1, legs=6, ant=16, antc=2)
        bug_wing(f, 50, 48, 46, 19, -105, s=0, veins=3)
        f.eye(31, 47, 4, "round", -1)
        f.eye(39, 46, 3.4, "round", -1)
        f.line([(27, 54), (31, 56)], 3, face=True)


# =================================================================== 13 STINGLET line
@fam("STINGLET", "HUSKPOD", "SPIKEWASP")
def sting_line(f, st):
    if st == 0:
        horn(f, 84, 72, 16, 7, -60, s=0)
        larva(f, 82, 82, 5, 10, 7, -11, wave=4, bands=2)
        f.ell(28, 70, 13, 12, 1, group="head")
        horn(f, 30, 60, 11, 5, -100, curve=-0.4, s=0)
        f.eye(24, 69, 3, "angry", -1)
        f.eye(34, 68, 2.6, "angry", -1)
        f.line([(20, 76), (26, 77)], 3, face=True)
    elif st == 1:
        pts = [(50, 6), (70, 22), (74, 54), (62, 90), (38, 90), (26, 56), (30, 22)]
        pid = f.poly(pts, 1)
        f.mark_poly([(50, 6), (60, 22), (62, 54), (50, 90), (38, 90), (40, 54), (42, 22)], 0, clip=pid)
        f.line([(30, 22), (50, 30), (70, 22)], 3)
        f.line([(26, 56), (50, 62), (74, 54)], 3)
        f.line([(50, 30), (50, 62)], 3)
        f.eye(42, 44, 3, "angry", -1)
        f.eye(57, 44, 3, "angry", -1)
        f.stroke([(50, 0), (50, 8)], 1.0, 1.0, 3)
    else:
        bug_wing(f, 56, 40, 34, 13, -70, s=0, veins=2)
        insect(f, 30, 38, 9, 48, 46, 9, 30, 9, abang=50, s=1, stripes_n=3, legs=4, ant=10, stinger=10)
        bug_wing(f, 52, 40, 36, 14, -40, s=0, veins=2)
        for y0, ln in ((50, 26), (56, 22)):
            f.stroke([(42, y0), (34, y0 + 6)], 2.2, 2.0, 1)
            horn(f, 33, y0 + 6, ln, 5, 195, s=0)
        f.eye(26, 36, 3.6, "angry", -1)
        f.eye(34, 35, 3.0, "angry", -1)


# =================================================================== 16 PIPWING line
@fam("PIPWING", "GUSTJAY", "SKYMARSHAL")
def pip_line(f, st):
    if st == 0:
        bird(f, bx=56, by=70, brx=22, bry=19, tilt=-5, hx=36, hy=50, hr=14, beak=6, beakw=6, wing="fold", wl=20, ww=13,
             tailk="fan", tl=10, tw=8, legl=6, belly=0, eye="round", eyer=3.2, neck=0, crest="plume", cl=8)
    elif st == 1:
        bird(f, bx=58, by=62, brx=22, bry=14, tilt=-20, hx=34, hy=38, hr=11, beak=8, beakw=5, wing="up", wl=28, ww=15,
             tailk="long", tl=22, tw=8, legl=10, belly=0, eye="dot", eyer=3, crest="tuft", cl=14)
    else:
        bird(f, bx=58, by=60, brx=24, bry=15, tilt=-22, hx=32, hy=33, hr=11, beak=9, beakw=6, hook=3, wing="up", wl=36, ww=18,
             tailk="banner", tl=30, tw=16, legl=12, belly=0, eye="angry", eyer=2.8, crest="plume", cl=20, fly=True)


# =================================================================== 19 NIBBIT line
@fam("NIBBIT", "GNAWLORD")
def nib_line(f, st):
    def teeth(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        x = hx - hr * 0.75 - q["sn"] * 0.85
        f.poly([(x, hy + hr * 0.55), (x + 4.5, hy + hr * 0.55), (x + 4, hy + hr * 0.55 + 6), (x + 0.5, hy + hr * 0.55 + 6)], 0, sh=0)
        f.line([(x - 4, hy + hr * 0.2), (x - 12, hy + hr * 0.05)], 3, face=True)
        f.line([(x - 4, hy + hr * 0.35), (x - 12, hy + hr * 0.45)], 3, face=True)
    if st == 0:
        quad(f, bx=58, by=74, brx=22, bry=15, hx=34, hy=58, hr=15, sn=5, snr=6, ears="round", er=10, ear_in=2,
             lr=3.5, tail="thin", tl=30, trr=1.5, tang=-10, eye="round", eyer=3, belly=0, head=teeth, mouth=None, neck=0)
    else:
        def mane(f, q):
            spikes(f, arc(36, 50, 14, 15, 60, 330, 10), 7, 6, s=2, side=1)
        quad(f, bx=60, by=70, brx=26, bry=17, hx=32, hy=50, hr=14, sn=7, snr=6, ears="round", er=8, ear_in=2,
             lr=4.5, tail="thin", tl=30, trr=2.2, tang=-20, eye="angry", eyer=2.8, belly=0, pre=mane, head=teeth, mouth=None)


# =================================================================== 21 BEAKLET line
@fam("BEAKLET", "RAPTORAX")
def beak_line(f, st):
    def mask(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.mark_poly([(hx - hr, hy - 4), (hx + hr, hy - 2), (hx + hr, hy + 3), (hx - hr, hy + 2)], 2, clip=q["headid"])
    if st == 0:
        bird(f, bx=56, by=68, brx=20, bry=16, tilt=-10, hx=36, hy=46, hr=14, beak=7, beakw=6, hook=2, wing="fold", wl=22, ww=13,
             tailk="fan", tl=14, tw=8, legl=7, belly=0, eye="angry", eyer=3, crest="spike", cl=10, head=mask)
    else:
        bird(f, bx=60, by=58, brx=22, bry=13, tilt=-25, hx=30, hy=28, hr=10, beak=20, beakw=5, hook=3, wing="up", wl=36, ww=16,
             wang=-50, tailk="long", tl=24, tw=10, legl=12, belly=0, eye="angry", eyer=2.6, crest="spike", cl=10, neck=6, head=mask, fly=True)


# =================================================================== 23 COILET line
@fam("COILET", "COBRAXIS")
def coil_line(f, st):
    if st == 0:
        path = [(78, 86), (66, 92), (46, 92), (32, 86), (38, 76), (58, 76), (66, 70), (60, 60), (44, 56), (34, 50)]
        serpent(f, path, 6.5, 3.0, bs=1, hr=8, bands=6, bandw=2.4, eye="round", eyer=3, tongue=True, sn=3)
    else:
        path = [(86, 92), (66, 94), (40, 92), (30, 84), (44, 78), (62, 76), (66, 64), (58, 48)]
        f.stroke(path, 7, 4, 1, group="body")
        hid = f.ell(52, 34, 18, 22, 1, group="hood")
        f.mark_ell(52, 40, 9, 16, 0, clip=hid)
        for x in (40, 63):
            f.mark_ell(x, 34, 4.5, 5, 3, clip=hid)
            f.mark_ell(x, 34, 2.2, 2.6, 0, clip=hid)
        f.stroke([(56, 52), (52, 40)], 6, 6, 1, group="neck")
        f.ell(48, 22, 10, 7.5, 1, group="head")
        f.eye(44, 20, 2.8, "angry", -1)
        f.eye(52, 20, 2.4, "angry", -1)
        f.line([(40, 26), (52, 27)], 3, face=True)
        f.line([(39, 25), (33, 27), (30, 24)], 3, face=True)
        f.line([(33, 27), (30, 30)], 3, face=True)


# =================================================================== 25 ZAPPET line
@fam("ZAPPET", "VOLTRIX")
def zap_line(f, st):
    def head(f, q):
        hx, hy, hr = q["hx"], q["hy"], q["hr"]
        f.mark_ell(hx - hr * 0.55, hy + hr * 0.38, 3.5, 3.2, 2, clip=q["headid"])
        spark(f, hx - hr * 1.3, hy + hr * 0.3, 3.5)
    if st == 0:
        def pre(f, q):
            f.stroke([(70, 82), (78, 94), (66, 96)], 6, 5, 1, group="far")
        quad(f, bx=62, by=78, brx=18, bry=14, hx=38, hy=58, hr=15, sn=2, ears="round", er=15, ear_in=2,
             lr=3, tail="ring", tl=36, trr=1.5, tang=-30, eye="round", eyer=3.2, belly=0, head=head, pre=pre, neck=0)
    else:
        biped(f, tx=55, ty=64, trx=13, tr_y=19, hx=46, hy=34, hr=12, sn=3, ears="tall", er=12, ear_in=2,
              legr=4.5, legx=5, footl=1.6, arm="side", armr=2.5, tail="bolt", tl=30, trr=1.6, tang=-60, ttip=1,
              eye="angry", eyer=2.8, belly=0, head=head)


# =================================================================== 27 DUSTBALL line
@fam("DUSTBALL", "SANDSPUR")
def dust_line(f, st):
    if st == 0:
        def back(f, q):
            sid = f.ell(60, 66, 22, 18, 2, group="shell")
            for i in range(4):
                x = 48 + i * 8
                f.mark_stroke([(x, 48), (x + 2, 84)], 0.9, s=1, clip=sid)
        quad(f, bx=60, by=74, brx=20, bry=14, hx=34, hy=72, hr=11, hry=9, sn=9, snr=4, snd=0.4, ears="point", er=7, ear_in=2,
             lr=3.5, tail="stub", trr=3, eye="dot", eyer=2.6, back=back, neck=0, mouth=None)
    else:
        def back(f, q):
            sid = f.ell(60, 62, 26, 21, 2, group="shell")
            for i in range(5):
                x = 44 + i * 8
                f.mark_stroke([(x, 42), (x + 2, 82)], 0.9, s=1, clip=sid)
            spikes(f, arc(60, 62, 26, 21, 195, 345, 8), 9, 6, s=0, side=1)
        quad(f, bx=60, by=72, brx=24, bry=15, hx=31, hy=68, hr=11, hry=9, sn=10, snr=4, snd=0.4, ears="point", er=8, ear_in=2,
             lr=4.5, tail="thin", tl=14, trr=3, tang=10, eye="angry", eyer=2.6, back=back, neck=0, mouth=None)
