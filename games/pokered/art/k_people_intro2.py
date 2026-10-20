"""KITHBOUND intro creatures, second pass: TUNEPUFF (songbird chick hatched from a tiny
bell), NIGHTGRIN (long-armed shadow heron with a grin), and OLD HOLT's back view.
Our own designs from world.py concepts only.
"""
from collections import Counter

import numpy as np

from cleanroom.gb import gfx
from games.pokered.art.k_people_kit import Fig, _edge


# ------------------------------------------------------------------ OLD HOLT from behind
def holt_back(w=32, h=32):
    """Hunched old man: small bald head sunk between round shoulders, white fringe,
    striped shawl, a walking stick handle at his side."""
    f = Fig(w, h)
    f.part(f.cap([(28, 9), (28.5, 33)], 1.1), 1)                              # stick
    f.part(f.cap([(28, 9), (25, 7.5), (23, 9)], 1.1), 1)
    f.part(f.cap([(5, 22), (2, 33)], 3.4), 2)
    f.part(f.cap([(25, 22), (28, 27)], 3.2), 2)
    f.part(f.E(28, 27, 2.4, 2.2), 0)                                          # hand on the stick
    body = f.P([(5, 17), (25, 17), (30, 24), (31, 33), (1, 33), (1, 24)]) | f.E(15, 21, 13, 7)
    f.part(body, 2)
    shawl = f.P([(3, 18), (27, 18), (28, 23), (15, 29), (2, 23)]) | f.E(15, 19, 12.5, 4)
    f.part(shawl, 1)
    f.stripes(shawl & ~_edge(shawl), 2, gap=3, dirn=(0, 1))
    f.part(f.E(8.8, 13.5, 1.6, 2.3) | f.E(21.2, 13.5, 1.6, 2.3), 0, shadow=False)
    head = f.E(15, 12, 6.4, 6.8)
    f.part(head, 0)
    f.flat(f.E(17, 14, 3.6, 3.8) & ~_edge(head), 1)
    f.px(13, 8, 1)
    fringe = f.E(15, 12, 7.0, 7.2) & ~f.E(15, 10, 6.2, 6.0) & (f.Y > 11)
    f.part(fringe, 1)
    f.dither(fringe & ~_edge(fringe), 0)
    f.part(f.E(15, 5.2, 1.8, 1.5), 1)                                         # little topknot
    f.outline_all()
    return f.a


# ------------------------------------------------------------------ TUNEPUFF: chick in its bell shell
def tunepuff(pose):
    """Facing right. The bell it hatched from: the crown worn as a cap (with its loop),
    the flared mouth of the bell still around its middle like a skirt."""
    f = Fig(48, 48, open_bottom=False)
    if pose == 1:
        f.pose(0)
    elif pose == 2:
        f.pose(0, sx=1.12, sy=0.84, px=24, py=45)
    else:
        f.pose(-8, px=24, py=30, ty=-6)
    hop = pose == 3
    # legs
    for x0, x1 in ((20, 18 if not hop else 15), (27, 29 if not hop else 31)):
        f.part(f.cap([(x0, 37), (x1, 44 if not hop else 42)], 1.2), 2)
        y = 44.5 if not hop else 42.5
        f.line([(x1 - 2, y), (x1 + 2, y)], 3); f.px(x1 + 2, y - 1, 3)
    # wings behind / tail tuft
    f.part(f.cap([(12, 26), (6, 23)], 2.0, 1.0) | f.cap([(12, 28), (5, 29)], 1.8, 0.9), 2)
    # fluffy chick body
    body = f.E(24, 24, 11, 10.5)
    for a in range(0, 360, 40):
        t = np.radians(a)
        body |= f.E(24 + np.cos(t) * 10, 24 + np.sin(t) * 9.5, 2.4, 2.4)
    f.part(body, 0)
    f.flat(body & ~_edge(body) & f.E(17, 21, 6, 6) & ~f.E(19, 19, 4, 3), 1)
    # the bell skirt: flared rim, a band, a slot
    skirt = f.P([(13, 27), (35, 27), (40, 38), (8, 38)])
    f.part(skirt, 1)
    f.part(f.E(24, 38, 16.5, 2.4), 2)
    f.part(f.R(11, 29, 37, 31.5) & skirt, 2, line=None, shadow=False)
    f.line([(24, 33), (24, 36)], 3)
    for x in (16, 32):
        f.px(x, 34, 0)
    # bell crown cap with its hanging loop
    cap = f.E(23.5, 15, 7.5, 4.5) & (f.Y < 16)
    f.part(cap, 1)
    f.part(f.ring(23.5, 8.2, 2.6, 1.3), 2, line=None, shadow=False)
    f.a[_edge(f.ring(23.5, 8.2, 2.6, 1.3))] = 3
    f.line([(17, 14), (30, 14)], 2)
    # face
    if hop:
        f.part(f.P([(33, 19), (40, 16), (34, 21)]), 2)                        # beak open, singing
        f.part(f.P([(33, 22), (39, 24), (33, 24)]), 2)
        for k, (x, y) in enumerate(((42, 8), (45, 13), (41, 30))):            # ringing marks
            f.line([(x, y), (x + 3, y - 1 if k < 2 else y + 1)], 3)
        f.part(f.P([(13, 22), (5, 12), (17, 19)]) | f.E(14, 21, 3, 2.5), 1)   # wing up
    else:
        f.part(f.P([(33, 20), (39, 22), (33, 24)]), 2)
        f.part(f.E(16, 24, 4, 3.4) | f.P([(13, 25), (11, 30), (19, 26)]), 1)  # folded wing
    if pose == 2:
        f.line([(26, 19), (28, 20), (30, 19)], 3)
    else:
        f.stamp(".#/##/##", 29.5, 19.5)
    f.dither(f.E(30, 23.5, 2.2, 1.4), 1)
    f.outline_all()
    return f.a


# ------------------------------------------------------------------ NIGHTGRIN: long-armed shadow heron
# per pose, in panel pixels (56 wide): head, beak tip(s), crest plumes, body, long arms, legs, tail
POSES = [
    dict(  # stalking low, beak spearing forward, arms trailing to the ground
        head=(32, 20), beak=[(2, 20)], eye=(31, 18), crest=[(44, 9), (38, 15)],
        body=((30, 40), 15, 11), neck=[(30, 33), (33, 26)],
        arms=[[(22, 33), (12, 34), (4, 40), (3, 53)], [(36, 36), (26, 44), (16, 50), (9, 55)]],
        legs=[[(28, 48), (26, 56)], [(34, 48), (36, 56)]], tail=[(44, 42), (54, 47)]),
    dict(  # rearing up, beak thrown open in a grin, arms spread wide
        head=(33, 12), beak=[(16, 12), (25, 2)], eye=(34, 10), crest=[(44, 2), (53, 11)],
        body=((30, 41), 16, 16), neck=[(28, 26), (32, 17)], bulk=((40, 31), 7, 8),
        arms=[[(18, 28), (8, 24), (3, 17), (4, 21)], [(16, 36), (6, 44), (3, 54)]],
        legs=[[(24, 52), (22, 56)]], tail=[(40, 44), (45, 54)]),
    dict(  # lunging: beak spearing back over its shoulder, arms reaching far left
        head=(24, 15), beak=[(54, 21)], eye=(23, 13), crest=[(18, 9), (27, 8)],
        body=((31, 43), 16, 13), neck=[(28, 30), (25, 22)],
        arms=[[(22, 30), (12, 28), (3, 30), (2, 36)], [(24, 38), (12, 42), (3, 46), (2, 54)]],
        legs=[[(34, 50), (30, 56)], [(40, 48), (46, 56)]], tail=[(46, 38), (54, 43)]),
]


def _feathers(f, m):
    """Grey chevron feather marks on the black body."""
    yy, xx = np.mgrid[0:f.h, 0:f.w]
    inner = m & ~_edge(m, True)
    v = (xx + np.abs(((yy * 2) % 10) - 5) + (yy // 5) * 3) % 6
    f.a[inner & (v == 0) & (yy % 5 != 0)] = 2


def nightgrin(a):
    """Three poses side by side. The build de-duplicates this picture's tiles (spec
    'classes'): blank-class tiles stay white, the solid-black class stays black, the intro
    uses tile 1 (second tile of the first column) as letterbox black, equal classes copy."""
    h, w = a["h"], a["w"]
    cls = a["classes"]
    W = w // 8
    cnt = Counter(cls)
    blank_c, black_c = cls[0], cls[W]
    out = np.zeros((h, w), np.uint8)
    for k, P in enumerate(POSES):
        x0 = k * 56
        al = np.zeros((h, 56), bool)
        bl = np.zeros((h, 56), bool)
        for i, c in enumerate(cls):
            ty, tx = (i // W) * 8, (i % W) * 8 - x0
            if 0 <= tx < 56:
                if c != blank_c and i != W:
                    al[ty:ty + 8, tx:tx + 8] = True
                if c == black_c and i != W:
                    bl[ty:ty + 8, tx:tx + 8] = True
        f = Fig(56, h, open_bottom=True)
        # the folded wing-cloak behind: the drawn tile area, rounded, with a ragged feather hem
        from games.pokered.art.k_people_intro import _open
        cloak = _open(al, 4) & al
        yy, xx = np.mgrid[0:h, 0:56]
        rag = ((xx * 5 + (yy // 3) * 7) % 9 < 3)
        hem = cloak & ~_open(cloak, 2)
        cloak &= ~(_edge(cloak, True) & rag & (yy > 20))
        f.a[cloak] = 1
        v = (xx + np.abs(((yy * 2) % 8) - 4) + (yy // 4) * 3) % 5
        f.a[cloak & (v == 0)] = 2
        f.a[_edge(cloak, True)] = 3
        # body, neck, head, legs, tail plumes (all black)
        (bx, by), brx, bry = P["body"]
        m = f.E(bx, by, brx, bry) | (f.E(*P["bulk"][0], P["bulk"][1], P["bulk"][2]) if "bulk" in P else False) | f.cap(P["neck"], 3.4, 2.6) | f.E(P["head"][0], P["head"][1], 5.5, 4.6)
        m |= f.P([(P["tail"][0][0] - 4, P["tail"][0][1] - 4), P["tail"][1], (P["tail"][0][0] - 2, P["tail"][0][1] + 6)])
        for leg in P["legs"]:
            m |= f.cap(leg, 1.4)
        for c_ in P["crest"]:
            hx, hy = P["head"]
            m |= f.P([(hx - 2, hy - 2), c_, (hx + 3, hy)])
        m |= bl
        m &= al
        f.a[m] = 3
        _feathers(f, m)
        # long arms with long white-tipped fingers
        arms = np.zeros_like(m)
        for arm in P["arms"]:
            arms |= f.cap(arm, 2.0, 1.2)
        arms &= al
        f.a[arms] = 3
        f.a[_edge(arms, True) & ~m] = 3
        for arm in P["arms"]:
            hx, hy = arm[-1]
            px, py = arm[-2]
            dx, dy = hx - px, hy - py
            n = max(abs(dx), abs(dy), 1)
            dx, dy = dx / n, dy / n
            for s_ in (-1, 0, 1):
                ex, ey = hx + dx * 3 + dy * s_ * 2, hy + dy * 3 - dx * s_ * 2
                f.line([(hx, hy), (ex, ey)], 3)
                f.px(ex, ey, 0)
        mm = m | arms | cloak
        # the beak: long, light, with a grin of teeth along the jaw line
        hx, hy = P["head"]
        for tip in P["beak"]:
            ang = np.arctan2(tip[1] - hy, tip[0] - hx)
            nx, ny = -np.sin(ang), np.cos(ang)
            base1 = (hx + nx * 3, hy + ny * 3)
            base2 = (hx - nx * 3, hy - ny * 3)
            beak = f.P([base1, tip, base2]) & al
            f.a[beak] = 0
            f.a[_edge(beak, True)] = 3
            mm |= beak
            L = int(np.hypot(tip[0] - hx, tip[1] - hy))
            for t in range(5, L - 3, 3):                       # zigzag teeth along the middle
                px_, py_ = hx + np.cos(ang) * t, hy + np.sin(ang) * t
                f.px(px_ + nx * ((t // 3) % 2), py_ + ny * ((t // 3) % 2), 3)
        # grin corner and eye
        ex, ey = P["eye"]
        eye = f.E(ex, ey, 2.4, 1.8)
        f.a[eye & al] = 0
        f.px(ex - 0.5, ey, 3)
        f.line([(hx - 1, hy + 2), (hx + 3, hy + 3)], 0)
        p = f.a.copy()
        p[~al] = 0
        p[bl] = 3
        # every drawn tile must hold something: fill any near-empty one with a wisp plume
        for i, c in enumerate(cls):
            ty, tx = (i // W) * 8, (i % W) * 8 - x0
            if not (0 <= tx < 56) or c in (blank_c, black_c) or i == W:
                continue
            if (p[ty:ty + 8, tx:tx + 8] > 0).sum() < 6:
                yy2, xx2 = np.mgrid[0:8, 0:8]
                wisp = np.abs(xx2 - (4 + (yy2 - 4) * 0.5)) <= (yy2 + 1) * 0.35
                p[ty:ty + 8, tx:tx + 8][wisp] = 3
                p[ty:ty + 8, tx:tx + 8][wisp & ((xx2 + yy2) % 3 == 0)] = 2
        out[:, x0:x0 + 56] = p
    out[8:16, 0:8] = 3
    t = gfx.tiles(out).copy()
    first = {}
    for i, c in enumerate(cls):
        if c in (blank_c, black_c):
            continue
        if c in first and cnt[c] > 1:
            t[i] = t[first[c]]
        first.setdefault(c, i)
    return gfx.untile(t, w)[:h]
