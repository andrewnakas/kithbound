"""KITHBOUND families: one function per evolution family, stage 0/1/2 adds size and features."""
import math
import random

from games.pokered.art.k_kith_body import biped, bird, ears, eyes2, quad, serpent, tail
from games.pokered.art.k_kith_lib import (arc, bat_wing, bird_wing, blobpoly, bug_wing, cog, fang, fin,
                                          flame, horn, leaf, rot, spikes, spiral, spots, star, stripes,
                                          tail_fin)

REG = {}


def fam(*names, **opts):
    def reg(fn):
        for i, n in enumerate(names):
            o = opts.get(n, opts.get("all", {}))
            REG[n] = (fn, i, o)
        return fn
    return reg


_LOADED = False


def lookup(name):
    global _LOADED
    if not _LOADED:
        import importlib
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for fn in sorted(os.listdir(here)):
            if fn.startswith("k_kith_fam") and fn.endswith(".py") and fn != "k_kith_fam.py":
                importlib.import_module("games.pokered.art." + fn[:-3])
        _LOADED = True
    if name in REG:
        return REG[name]
    from games.pokered.world import ROSTER
    for r in ROSTER:
        if r[0] == name:
            return (lambda f, st, r=r: generic(f, r), 0, {})
    raise KeyError(name)


def generic(f, r):
    plan = r[3]
    if plan == "quad":
        quad(f, ears="point", tail="thin")
    elif plan == "biped":
        biped(f)
    elif plan == "bird":
        bird(f)
    else:
        f.ell(50, 60, 30, 30, 1)
        eyes2(f, 45, 55, 20)


def spark(f, x, y, r, s=3):
    f.line([(x - r, y - r), (x, y - r * 0.2), (x - r * 0.2, y + r * 0.2), (x + r, y + r)], s)


def R(name):
    return random.Random(sum(map(ord, name)) * 7919)


# =================================================================== 1 MOSSPUP line
def moss_saddle(f, x, y, rx, ry, seed, s=2, bumps=7):
    pts = blobpoly(x, y, rx, ry, n=bumps, amp=0.16, seed=seed)
    return f.poly(pts, s, sh=1)


@fam("MOSSPUP", "BRAMBLOX", "THORNHULK")
def moss_line(f, st):
    if st == 0:
        def back(f, q):
            sid = moss_saddle(f, 60, 56, 15, 7, 3)
            spots(f, sid, 60, 55, 11, 4, 5, 1.5, s=1, seed=4)
            f.stroke([(62, 50), (63, 44)], 1.2, 1.0, 2)
            b = f.ell(63, 39, 4.5, 6, 1)
            f.mark_ell(64, 35, 3, 2.5, 2, clip=b)
        quad(f, bx=60, by=72, brx=21, bry=13, hx=31, hy=52, hr=17, sn=5, snr=6, ears="fold", er=9,
             lr=4.6, tail="stub", trr=4, eye="round", eyer=3.4, back=back, belly=0)
    elif st == 1:
        def back(f, q):
            sid = moss_saddle(f, 60, 55, 22, 9, 5, bumps=9)
            for k, (x, y) in enumerate([(46, 50), (55, 46), (65, 46), (74, 50)]):
                horn(f, x, y, 6, 3.5, -100 + k * 8, s=0)
            f.line([(44, 58), (50, 54), (56, 58), (63, 53), (70, 57), (78, 53)], 3)
            leaf(f, 77, 49, 9, 3.5, -40, s=1)
        quad(f, bx=60, by=70, brx=25, bry=15, hx=29, hy=50, hr=14, sn=8, snr=6, ears="point", er=8, ear_in=2,
             lr=5.5, tail="thin", tl=14, trr=2.5, tang=-30, eye="dot", eyer=3, back=back, belly=0, fangs=1, brow=1)
    else:
        def back(f, q):
            sid = moss_saddle(f, 60, 50, 27, 13, 11, bumps=10)
            spikes(f, arc(60, 50, 27, 13, 190, 350, 9), 6, 5, s=0, side=1)
            f.line([(40, 56), (48, 50), (56, 55), (64, 48), (72, 54), (80, 49)], 3)
            f.stroke([(62, 40), (63, 26)], 1.8, 1.4, 2)
            leaf(f, 62, 33, 10, 3.6, 200, s=1)
            leaf(f, 63, 30, 10, 3.6, -25, s=1)
            f.poly(star(63, 18, 9, 5.5, n=9), 1)
            b = f.ell(63, 24, 5, 3.5, 2)
        def head(f, q):
            horn(f, 14, 63, 9, 4, -110, curve=0.6, s=0)
            horn(f, 21, 64, 8, 3.5, -100, curve=0.6, s=0)
        quad(f, bx=60, by=69, brx=30, bry=19, hx=27, hy=60, hr=14, sn=10, snr=7, snd=0.3, ears="point", er=6, ear_in=2,
             lr=7, tail="stub", trr=3, eye="angry", eyer=2.8, back=back, head=head, mouth="line", belly=None, neck=0)


# =================================================================== 4 KINDLET line
@fam("KINDLET", "SCORCHET", "BLAZEWYRM")
def kindlet_line(f, st):
    if st == 0:
        def head(f, q):
            flame(f, 50, 26, 12, 16, ang=10, n=3, s=1)
        biped(f, tx=56, ty=72, trx=14, tr_y=15, hx=46, hy=44, hr=15, sn=3, legr=4.5, legx=5,
              arm="side", armr=3.2, tail="flame", tl=20, trr=3.0, tang=-20, ttip=1, belly=0,
              eye="round", eyer=3.5, head=head, mouth="smile")
    elif st == 1:
        def back(f, q):
            spikes(f, [(56, 40), (66, 50), (70, 64), (68, 76)], 7, 6, s=2, side=-1)
            for x, y, r in ((74, 38, 2.5), (78, 30, 3.2)):
                f.ell(x, y, r, r, 1, sh=0)
        def head(f, q):
            flame(f, 46, 20, 10, 14, ang=25, n=3, s=1)
        biped(f, tx=55, ty=64, trx=13, tr_y=20, hx=42, hy=32, hr=12, sn=8, legr=5, legx=5.5,
              arm="fwd", armr=3.3, tail="flame", tl=28, trr=3.5, tang=-35, belly=0, pre=back,
              eye="angry", eyer=2.8, head=head, mouth="open", fangs=1, neck=5)
    else:
        def pre(f, q):
            bat_wing(f, 62, 44, 36, 24, -40, n=3, s=2)
            bat_wing(f, 58, 46, 30, 18, -75, n=3, s=2)
        def head(f, q):
            for a, (x, y) in zip((-60, -20, 20, 50), ((44, 20), (52, 17), (59, 22), (62, 30))):
                flame(f, x, y, 8, 11, ang=a, n=2, s=1, inner=False)
            horn(f, 40, 20, 8, 3.5, -120, curve=-0.5, s=0)
        biped(f, tx=54, ty=62, trx=16, tr_y=22, hx=40, hy=31, hr=12, sn=10, legr=6.5, legx=6,
              arm="guard", armr=4, hand=3.5, tail="flame", tl=30, trr=4, tang=-15, belly=0, pre=pre,
              eye="angry", eyer=2.6, head=head, mouth="open", fangs=2, neck=6)


# =================================================================== 7 DRIPLET line
def drop(f, x, y, h, s=0):
    pts = [(x, y - h)] + arc(x, y - h * 0.3, h * 0.38, h * 0.38, -10, 190, 9)
    return f.poly(pts, s)


@fam("DRIPLET", "BRINESHELL", "HYDROCLAD")
def driplet_line(f, st):
    if st == 0:
        from games.pokered.art.k_kith_fam4 import claw
        for x in (36, 62):
            f.ell(x, 94, 7, 3.5, 1, group="feet")
        f.stroke([(30, 74), (18, 68)], 3, 3, 1)
        f.stroke([(70, 74), (82, 68)], 3, 3, 1)
        claw(f, 14, 62, 10, ang=-30, s=1)
        claw(f, 86, 62, 10, ang=210, s=1)
        b = f.ell(50, 72, 28, 21, 1, group="body", hl=True)
        f.mark_ell(50, 82, 18, 10, 0, clip=b)
        for x, y in ((37, 52), (61, 51)):
            f.ell(x, y, 7, 7, 1, group="body")
        f.eye(37, 52, 4, "round", -1)
        f.eye(61, 51, 4, "round", -1)
        drop(f, 49, 46, 20, 0)
        f.line([(38, 66), (44, 70), (54, 70), (60, 66)], 3, face=True)
    elif st == 1:
        def pre(f, q):
            sid = f.ell(64, 58, 20, 22, 2)
            spiral(f, 64, 58, 15, turns=1.8, s=3)
        def head(f, q):
            f.ell(32, 22, 4.5, 4.5, 1, group="head")
            f.ell(46, 21, 4.5, 4.5, 1, group="head")
            f.eye(32, 22, 2.6, "angry", -1)
            f.eye(46, 21, 2.4, "angry", -1)
        def front(f, q):
            x, y = q["handpos"]
            f.ell(x - 3, y, 7, 5, 1)
            f.cut_poly([(x - 11, y - 1), (x - 3, y + 1), (x - 11, y + 4)])
        biped(f, tx=48, ty=64, trx=17, tr_y=21, hx=40, hy=35, hr=13, legr=5.5, legx=7, eye=None,
              arm="fwd", armr=3.5, belly=0, pre=pre, head=head, front=front, mouth="line")
    else:
        def pre(f, q):
            f.ell(66, 54, 22, 26, 2)
            spiral(f, 66, 54, 18, turns=1.9, s=3)
        def head(f, q):
            f.ell(36, 16, 4, 4, 1, group="head")
            f.ell(48, 15, 4, 4, 1, group="head")
            f.eye(36, 16, 2.4, "angry", -1)
            f.eye(48, 15, 2.2, "angry", -1)
            f.mark_poly([(30, 24), (56, 22), (56, 27), (30, 29)], 2, clip=q["headid"])
        def front(f, q):
            for (x, y), s in ((q["handpos"], 1), ):
                f.ell(x, y, 6, 6, 1)
                f.poly([(x - 4, y - 4), (x - 14, y - 6), (x - 14, y + 2), (x - 4, y + 2)], 2)
                f.ell(x - 14, y - 2, 2, 4, 3, sh=0)
            x, y = q["farhand"]
        def back(f, q):
            x, y = 78, 38
            f.poly([(x - 2, y - 2), (x + 8, y - 12), (x + 13, y - 8), (x + 4, y + 2)], 2)
        biped(f, tx=50, ty=58, trx=18, tr_y=24, hx=43, hy=27, hr=12, legr=7, legx=8, eye=None,
              arm="fwd", armr=5, belly=0, pre=pre, head=head, front=front, back=back, mouth="line")
