"""Battle effect tiles (move_anim_0 / move_anim_1), all our own drawing.

Each tile keeps the role the animation code gives it (data/battle_anims: which frame
blocks place it where, with which flips).  Multi-tile shapes are drawn whole on one
canvas, made exactly symmetric where the frame blocks mirror them, and cut into tiles.
Sprites: shade 0 is see-through, so light parts use shade 1.
"""
import math

import numpy as np

from games.pokered.art import DRAWERS, sheet
from games.pokered.art.tilekit import C


def front(pattern):
    def reg(fn):
        DRAWERS.insert(0, (pattern, fn))
        return fn
    return reg


def symh(a):
    w = a.shape[1]
    a[:, w - w // 2:] = a[:, :w // 2][:, ::-1]
    return a


def symv(a):
    h = a.shape[0]
    a[h - h // 2:] = a[:h // 2][::-1]
    return a


def tile(a, tx, ty):
    return a[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8].copy()


def rot(a, deg):
    h, w = a.shape
    out = np.zeros_like(a)
    t = math.radians(deg)
    cy, cx = (h - 1) / 2, (w - 1) / 2
    for y in range(h):
        for x in range(w):
            sx = math.cos(t) * (x - cx) + math.sin(t) * (y - cy) + cx
            sy = -math.sin(t) * (x - cx) + math.cos(t) * (y - cy) + cy
            ix, iy = int(round(sx)), int(round(sy))
            if 0 <= ix < w and 0 <= iy < h:
                out[y, x] = a[iy, ix]
    return out


def dist(c, cx, cy):
    y, x = c.grid()
    return np.hypot(x + 0.5 - cx, y + 0.5 - cy)


def thick(c, x0, y0, x1, y1, core=1, edge=3):
    """A two-tone stroke: dark rim around a light core."""
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        c.line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, edge)
    c.line(x0, y0, x1, y1, core)


def spark(c, x, y, r=2, s=1, mid=3):
    for d in range(1, r + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            c.px(x + dx, y + dy, s)
    c.px(x, y, mid)


def grain(x, y):
    return 2 if (x % 8 * 3 + y % 8 * 5) % 7 == 0 else 1


# ---- shared shapes ------------------------------------------------------------------------

def acorn():
    """The catch capsule: an acorn with a hatched cap and a short stalk (16x16)."""
    c = C(16, 16)
    c.fill(c.emask(8, 9.5, 6.2, 5.8) | c.pmask([(6.5, 14), (9.5, 14), (8, 16)]), 1, outline=3)
    y, x = c.grid()
    xm = np.where(x < 8, x, 15 - x)
    cap = c.emask(8, 6.5, 7.4, 4.2) & (y < 8 + (xm % 2))
    c.fill(cap, 2, outline=3)
    inner = cap & ((xm + y) % 3 == 0) & (y > 3) & (y < 8)
    c.a[inner & (c.a == 2)] = 3
    c.rect(7, 0, 9, 3, 3)
    c.px(6, 10, 2).px(9, 10, 2)        # two grain marks, mirrored
    return symh(c.a)


def egg():
    e = C(16, 16)
    e.fill(e.emask(8, 9.5, 6.2, 8.5), 1, outline=3)
    for x, y in ((5, 4), (10, 4), (7, 6), (3, 6)):
        e.px(x, y, 2)
    a = acorn()
    a[:8] = e.a[:8]
    return symh(a)


def ring_puffs(n, radius, r, clear=None, jag=False):
    c = C(32, 32)
    m = np.zeros((32, 32), bool)
    for k in range(n):
        t = 2 * math.pi * (k + 0.5) / n
        cx, cy = 16 + radius * math.cos(t), 16 + radius * math.sin(t)
        if jag:
            pts = []
            for j in range(10):
                rr = r * (1.0 if j % 2 == 0 else 0.5)
                u = 2 * math.pi * j / 10 + t
                pts.append((cx + rr * math.cos(u), cy + rr * math.sin(u)))
            m |= c.pmask(pts)
        else:
            m |= c.emask(cx, cy, r, r)
    if clear:
        x0, y0, x1, y1 = clear
        m[y0:y1, x0:x1] = False
        m[32 - y1:32 - y0, x0:x1] = False
        m[y0:y1, 32 - x1:32 - x0] = False
        m[32 - y1:32 - y0, 32 - x1:32 - x0] = False
    c.fill(m, 2 if jag else 1, outline=3)
    if jag:
        d = dist(c, 16, 16)
        c.a[m & (c.a == 2) & (np.abs(d - radius) < r * 0.3)] = 1
    else:
        c.a[m & (c.a == 1) & (dist(c, 16, 16) > radius + r * 0.35)] = 2
    a = symh(c.a)
    return symv(a)


def bubble16():
    c = C(16, 16)
    c.fill(c.emask(8, 8, 7.4, 7.4), 1, outline=3)
    c.a[(dist(c, 8, 8) > 5.2) & (c.a == 1)] = 2
    c.px(4, 4, 0).px(5, 3, 0).px(3, 5, 0)
    return symv(symh(c.a))


def square_ring():
    c = C(24, 24)
    c.frame(1, 1, 23, 23, 3).frame(2, 2, 22, 22, 1).frame(3, 3, 21, 21, 3)
    for x, y in ((1, 1), (2, 2)):
        c.px(x, y, 2)
    return symv(symh(c.a))


# ---- tileset 0 ----------------------------------------------------------------------------

def set0():
    T = {}
    # 00 01 10 11: a little bird (dizzy birds)
    b = C(16, 16)
    b.fill(b.pmask([(3, 10), (0, 7), (0, 13)]), 2, outline=3)
    b.fill(b.emask(8, 10.5, 5.5, 3.8), 1, outline=3)
    b.fill(b.emask(12, 7, 2.8, 2.8), 1, outline=3)
    b.fill(b.pmask([(3, 10), (10, 10), (4, 1)]), 2, outline=3)
    b.px(12, 6, 3).rect(15, 7, 16, 9, 3).px(14, 8, 3)
    T[0x00], T[0x01], T[0x10], T[0x11] = tile(b.a, 0, 0), tile(b.a, 1, 0), tile(b.a, 0, 1), tile(b.a, 1, 1)
    # 02 12: the acorn capsule; 06 07 16 17 the same tipped over; 48 / 4A egg tops
    a = acorn()
    T[0x02], T[0x12] = tile(a, 0, 0), tile(a, 0, 1)
    t = rot(a, 24)
    T[0x06], T[0x07], T[0x16], T[0x17] = tile(t, 0, 0), tile(t, 1, 0), tile(t, 0, 1), tile(t, 1, 1)
    e = egg()
    T[0x48] = tile(e, 0, 0)
    T[0x4A] = tile(rot(e, 24), 0, 0)
    # 03 13: an ice shard, tip at the top right (pairs make peaks)
    s = C(8, 16)
    s.fill(s.pmask([(0, 16), (0, 8), (7, 0), (8, 0), (8, 16)]), 1, outline=3)
    s.line(6, 3, 2, 15, 2).line(5, 9, 7, 12, 2)
    T[0x03], T[0x13] = tile(s.a, 0, 0), tile(s.a, 0, 1)
    # 04 14 / 05 15: water splash crowns; 41 42 water column pieces
    for top, bot, lift in ((0x04, 0x14, 0), (0x05, 0x15, 3)):
        w = C(16, 16)
        w.fill(w.emask(8, 15, 7.5, 3.5), 1, outline=3)
        w.fill(w.pmask([(5, 14), (8, 3 + lift), (11, 14)]), 1, outline=3)
        for cx, cy, r in ((2.5, 8 - lift, 1.8), (5, 4 - lift / 2, 1.5), (1.5, 2 + lift, 1.2)):
            w.fill(w.emask(cx, cy, r, r), 1, outline=3)
        w.vline(8, 8, 14, 2)
        a2 = symh(w.a)
        T[top], T[bot] = tile(a2, 0, 0), tile(a2, 0, 1)
    for n, ph in ((0x41, 0), (0x42, 2)):
        w = C(8, 8)
        for y in range(8):
            o = round(math.sin((y + ph) * math.pi / 4))
            w.hline(y, 1 + o, 7 + o, 1)
            w.px(1 + o, y, 3).px(6 + o, y, 3)
            if (y + ph) % 4 == 0:
                w.px(3 + o, y, 2).px(4 + o, y + 1, 2)
        T[n] = w.a
    # 08 09 18 19: heart
    h = C(16, 16)
    h.fill(h.emask(5, 5.5, 4.5, 4.5) | h.emask(11, 5.5, 4.5, 4.5) | h.pmask([(0.8, 7), (15.2, 7), (8, 15.5)]), 2, outline=3)
    h.rect(3, 3, 5, 5, 1).px(5, 3, 1).px(3, 5, 1).px(12, 10, 1)
    T[0x08], T[0x09], T[0x18], T[0x19] = tile(h.a, 0, 0), tile(h.a, 1, 0), tile(h.a, 0, 1), tile(h.a, 1, 1)
    # 0A 0B 1A 1B: boulder
    r = C(16, 16)
    m = r.pmask([(1, 8), (4, 2), (10, 1), (15, 5), (15, 12), (9, 15), (2, 14)])
    r.fill(m, 1, outline=3)
    y, x = r.grid()
    r.a[m & (r.a == 1) & (x + y > 17)] = 2
    r.line(4, 3, 7, 8, 3).line(7, 8, 13, 6, 3).line(7, 8, 6, 13, 2)
    T[0x0A], T[0x0B], T[0x1A], T[0x1B] = tile(r.a, 0, 0), tile(r.a, 1, 0), tile(r.a, 0, 1), tile(r.a, 1, 1)
    # 0C 0D: sound arcs (block mirrors them downwards)
    sw = C(16, 16)
    d = dist(sw, -3, 8)
    for rr in (6, 10, 14):
        sw.a[(d >= rr - 1.2) & (d < rr + 0.2)] = 3
        sw.a[(d >= rr + 0.2) & (d < rr + 1.0)] = 2
    sw.a = symv(sw.a)
    T[0x0C], T[0x0D] = tile(sw.a, 0, 0), tile(sw.a, 1, 0)
    # 0E 0F: poison bubbles (mirrored sideways)
    p = C(16, 16)
    for cx, cy, rr in ((4, 11.5, 3.4), (7.5, 4.5, 2.4), (2, 4, 1.5), (8, 14, 1.6)):
        p.fill(p.emask(cx, cy, rr, rr), 2, outline=3)
        p.px(int(cx - rr / 2), int(cy - rr / 2), 1)
    a2 = symh(p.a)
    T[0x0E], T[0x0F] = tile(a2, 0, 0), tile(a2, 0, 1)
    # 1C 1D: silk column (repeats downwards); 26 27: silk thread rising
    st = C(16, 8)
    for y in range(8):
        o = round(2.5 * math.sin(y * math.pi / 4))
        st.px(7 + o, y, 3).px(8 - o, y, 3).px(3, y, 1).px(12, y, 1)
    st.px(3, 2, 3).px(12, 6, 3)
    T[0x1C], T[0x1D] = tile(st.a, 0, 0), tile(st.a, 1, 0)
    sd = C(16, 8)
    sd.line(0, 7, 15, 0, 3).line(1, 7, 15, 1, 1)
    sd.rect(6, 3, 8, 5, 3)
    T[0x26], T[0x27] = tile(sd.a, 0, 0), tile(sd.a, 1, 0)
    # 1E 1F: horn pointing right
    hn = C(16, 8)
    m = hn.pmask([(0, 0.5), (16, 4), (0, 7.5)])
    hn.fill(m, 1, outline=3)
    for gx in (3, 6, 9):
        hn.a[m & (hn.a == 1) & (hn.grid()[1] == gx)] = 2
    T[0x1E], T[0x1F] = tile(hn.a, 0, 0), tile(hn.a, 1, 0)
    # 20 21 30 31: big puff ring; 23 32 33: tight puff; 24 25 34: open smoke ring
    pf = ring_puffs(8, 9.5, 5.2)
    T[0x20], T[0x21], T[0x30], T[0x31] = tile(pf, 0, 0), tile(pf, 1, 0), tile(pf, 0, 1), tile(pf, 1, 1)
    c = C(32, 32)
    m = c.emask(16, 16, 7, 7)
    for k in range(8):
        tt = 2 * math.pi * k / 8
        rr = 4.6 if k % 2 == 0 else 3.4
        m |= c.emask(16 + 7.5 * math.cos(tt), 16 + 7.5 * math.sin(tt), rr, rr)
    m[0:8, 0:8] = m[0:8, 24:32] = m[24:32, 0:8] = m[24:32, 24:32] = False
    c.fill(m, 1, outline=3)
    c.a[m & (c.a == 1) & (dist(c, 16, 16) < 4)] = 2
    tp = symv(symh(c.a))
    T[0x23], T[0x32], T[0x33] = tile(tp, 1, 0), tile(tp, 0, 1), tile(tp, 1, 1)
    sr = ring_puffs(12, 12.6, 3.3, clear=(8, 8, 16, 16))
    T[0x24], T[0x25], T[0x34] = tile(sr, 0, 0), tile(sr, 1, 0), tile(sr, 0, 1)
    # 43: bubble quarter; 22: that quarter (lower left) with the beam running in;
    # 45 46: beam pieces rising to the right
    bb = bubble16()
    T[0x43] = tile(bb, 0, 0)
    q = tile(bb, 0, 1)
    for yy in range(8):
        for xx in range(8):
            dd = xx + yy - 7
            if abs(dd) <= 1:
                q[yy, xx] = 1
            elif abs(dd) == 2 and q[yy, xx] == 0:
                q[yy, xx] = 3
    T[0x22] = q
    for n, wig in ((0x45, 0), (0x46, 1)):
        bm = np.zeros((8, 8), np.uint8)
        for yy in range(8):
            for xx in range(8):
                dd = xx + yy - 7 + (wig if (xx // 2) % 2 else 0)
                if abs(dd) <= 1:
                    bm[yy, xx] = 1
                elif abs(dd) == 2:
                    bm[yy, xx] = 3
                elif abs(dd) == 3 and (xx + 2 * yy) % 3 == 0:
                    bm[yy, xx] = 2
        T[n] = bm
    # 28 38 / 29 39: water drops (mirrored sideways); 36: drop ring; 37 one drop; 40 rain
    dp = C(16, 16)
    dp.fill(dp.emask(8, 10.5, 5.5, 5.5) | dp.pmask([(3, 9), (8, 0), (13, 9)]), 1, outline=3)
    dp.a[(dist(dp, 8, 10.5) > 3.8) & (dp.a == 1) & (dp.grid()[0] > 10)] = 2
    dp.px(6, 9, 0).px(6, 10, 0)
    a2 = symh(dp.a)
    T[0x28], T[0x38] = tile(a2, 0, 0), tile(a2, 0, 1)
    cr = C(16, 16)
    cr.fill(cr.emask(8, 14, 7.5, 2.5), 2, outline=3)
    for px_, top in ((2, 4), (5, 1), (8, 6)):
        cr.fill(cr.pmask([(px_ - 1.5, 13), (px_, top), (px_ + 1.5, 13)]), 1, outline=3)
    cr.fill(cr.emask(1.5, 1.5, 1.3, 1.3), 1, outline=3)
    a2 = symh(cr.a)
    T[0x29], T[0x39] = tile(a2, 0, 0), tile(a2, 0, 1)
    rg = C(16, 16)
    for k in range(4):
        tt = math.pi / 4 + k * math.pi / 2
        cx, cy = 8 + 4.5 * math.cos(tt), 8 + 4.5 * math.sin(tt)
        rg.fill(rg.emask(cx, cy, 2.2, 2.2), 1, outline=3)
    rg.fill(rg.emask(8, 8, 1.5, 1.5), 2, outline=3)
    a2 = symv(symh(rg.a))
    T[0x36] = tile(a2, 0, 0)
    one = C(8, 8)
    one.fill(one.emask(4, 5, 2.6, 2.6) | one.pmask([(1.8, 4.5), (4, 0), (6.2, 4.5)]), 1, outline=3)
    T[0x37] = one.a
    T[0x40] = C(8, 8).put("   #/  #-#/  #-#/   #", 1, 2).a
    # 2A 2B 3A 3B: dizzy swirl with two twinkles
    sp = C(16, 16)
    for i in range(140):
        th = i * 0.09
        rr = 1.0 + th * 0.95
        x_, y_ = 8 + rr * math.cos(th), 8 + rr * math.sin(th)
        sp.px(int(x_), int(y_), 3)
        sp.px(int(x_) + 1, int(y_), 2 if sp.a[int(y_) % 16, (int(x_) + 1) % 16] == 0 else sp.a[int(y_) % 16, (int(x_) + 1) % 16])
    spark(sp, 2, 2, 2, 1, 3)
    spark(sp, 13, 13, 1, 1, 3)
    T[0x2A], T[0x2B], T[0x3A], T[0x3B] = tile(sp.a, 0, 0), tile(sp.a, 1, 0), tile(sp.a, 0, 1), tile(sp.a, 1, 1)
    # 2C 2D 3C 3D: hit burst, 24x24, eight spikes
    hb = C(24, 24)
    pts = []
    for j in range(16):
        tt = 2 * math.pi * j / 16 - math.pi / 2
        rr = (12 if j % 4 == 0 else 8.6) if j % 2 == 0 else 4.2
        pts.append((12 + rr * math.cos(tt), 12 + rr * math.sin(tt)))
    m = hb.pmask(pts)
    hb.fill(m, 1, outline=3)
    hb.a[m & (np.abs(hb.grid()[1] + 0.5 - 12) + np.abs(hb.grid()[0] + 0.5 - 12) < 3.6)] = 2
    a2 = symv(symh(hb.a))
    T[0x2C], T[0x2D], T[0x3C], T[0x3D] = tile(a2, 0, 0), tile(a2, 1, 0), tile(a2, 0, 1), tile(a2, 1, 1)
    # 2E 2F 3E: hollow ring 24x24
    rn = C(24, 24)
    d = dist(rn, 12, 12)
    rn.a[(d >= 8.6) & (d < 11.8)] = 1
    rn.a[(d >= 10.8) & (d < 11.8)] = 3
    rn.a[(d >= 8.6) & (d < 9.6)] = 3
    rn.a[(d >= 9.6) & (d < 10.8) & ((rn.grid()[0] + rn.grid()[1]) % 4 == 0)] = 2
    a2 = symv(symh(rn.a))
    T[0x2E], T[0x2F], T[0x3E] = tile(a2, 0, 0), tile(a2, 1, 0), tile(a2, 0, 1)
    # 35: crackle stroke corner to corner (four make a diamond)
    z = C(8, 8)
    for (x0, y0, x1, y1) in ((0, 0, 3, 1), (3, 1, 2, 4), (2, 4, 6, 5), (6, 5, 7, 7)):
        z.line(x0, y0, x1, y1, 3)
    for x_, y_ in ((1, 1), (4, 2), (3, 5), (6, 6)):
        z.px(x_, y_, 1)
    T[0x35] = z.a
    # 3F: sleep: a crescent with a dot
    sl = C(8, 8)
    m = sl.emask(4, 4, 3.4, 3.4) & ~sl.emask(5.8, 2.8, 2.8, 2.8)
    sl.fill(m, 2, outline=3)
    sl.px(6, 6, 3)
    T[0x3F] = sl.a
    # 44: slash flash quarter (four make an X); 47: one slash stroke
    sx = np.zeros((8, 8), np.uint8)
    for i in range(8):
        sx[i, i] = 1
        if i > 0:
            sx[i, i - 1] = 3
        if i < 7:
            sx[i, i + 1] = 3
    sx[6:8, 6:8] = 1
    sx[5, 7] = sx[7, 5] = 3
    T[0x44] = sx
    sl2 = np.zeros((8, 8), np.uint8)
    for i in range(8):
        sl2[7 - i, i] = 1
        if 1 < i < 7:
            sl2[7 - i + 1, i] = 3
            sl2[7 - i, i - 1] = 3 if sl2[7 - i, i - 1] == 0 else sl2[7 - i, i - 1]
    T[0x47] = sl2
    # 49: small orb; 4B 4C: coin face / coin edge; 4D pebble; 4E bait berry
    o = C(8, 8)
    o.fill(o.emask(4, 4, 3.6, 3.6), 1, outline=3)
    o.px(4, 5, 2).px(5, 4, 2).px(5, 5, 2)
    T[0x49] = o.a
    cn = C(8, 8)
    cn.fill(cn.emask(4, 4, 3.6, 3.6), 1, outline=3)
    cn.put(" + /+ +/ + ", 2, 2)
    T[0x4B] = cn.a
    ce = C(8, 8)
    ce.fill(ce.emask(4, 4, 1.8, 3.6), 2, outline=3)
    T[0x4C] = ce.a
    pb = C(8, 8)
    pb.fill(pb.pmask([(0.5, 5), (2, 1.5), (6, 1), (7.5, 4), (6, 7.5), (2, 7.5)]), 2, outline=3)
    pb.px(3, 3, 1).px(2, 4, 1)
    T[0x4D] = pb.a
    br = C(8, 8)
    br.fill(br.emask(4, 5, 3.2, 3), 2, outline=3)
    br.put("+/ -#", 3, 0)
    br.px(3, 4, 1)
    T[0x4E] = br.a
    return T


# ---- tileset 1 ----------------------------------------------------------------------------

def set1():
    T = {}
    # 00 01 10 11: sword, hilt low left, tip high right; a glint in the empty corner
    s = C(16, 16)
    s.line(5, 9, 13, 1, 3).line(6, 11, 15, 2, 3).line(5, 10, 14, 1, 1).line(6, 10, 14, 2, 1)
    s.px(15, 0, 3).px(14, 0, 3).px(15, 1, 3)
    s.line(2, 8, 7, 13, 3).line(3, 8, 8, 13, 3)
    s.line(1, 14, 4, 11, 2).line(2, 14, 5, 11, 3)
    s.rect(0, 14, 2, 16, 3)
    spark(s, 3, 3, 2, 1, 3)
    T[0x00], T[0x01], T[0x10], T[0x11] = tile(s.a, 0, 0), tile(s.a, 1, 0), tile(s.a, 0, 1), tile(s.a, 1, 1)
    # 02 12: dark orb
    k = C(16, 16)
    k.fill(k.emask(8, 8, 7.4, 7.4), 3)
    k.a[(dist(k, 8, 8) > 4.6) & (dist(k, 8, 8) < 5.8) & (k.grid()[0] < 6)] = 2
    a2 = symh(k.a)
    T[0x02], T[0x12] = tile(a2, 0, 0), tile(a2, 0, 1)
    # 03 13: four-point twinkle star (also the splash's shooting star)
    st = C(16, 16)
    y, x = st.grid()
    dx, dy = np.abs(x + 0.5 - 8) / 7.8, np.abs(y + 0.5 - 8) / 7.8
    m = dx ** 0.6 + dy ** 0.6 <= 1
    st.fill(m, 1, outline=3)
    st.a[m & (np.abs(x + 0.5 - 8) + np.abs(y + 0.5 - 8) < 2.6)] = 2
    a2 = symv(symh(st.a))
    T[0x03], T[0x13] = tile(a2, 0, 0), tile(a2, 0, 1)
    # 04 14 / 05 15: flames; 41 42: flame column pieces / single fireballs
    for top, bot, var in ((0x04, 0x14, 0), (0x05, 0x15, 1)):
        f = C(16, 16)
        if var == 0:
            tongues = [[(3, 11), (8, 0), (13, 11)], [(1, 12), (2.5, 3), (7, 10)]]
        else:
            tongues = [[(4, 11), (7, 2), (10, 9)], [(1, 12), (3.5, 5), (8, 10)], [(5, 8), (8, 4.5), (11, 8)]]
        m = f.emask(8, 11.5, 6.6, 4.4)
        for tg in tongues:
            m |= f.pmask(tg)
        f.fill(m, 2, outline=3)
        inner = f.emask(8, 12.5, 3.4, 2.6) | f.pmask([(5.5, 12), (8, 5 + var * 2), (10.5, 12)])
        f.a[inner & m] = 1
        a2 = symh(f.a)
        T[top], T[bot] = tile(a2, 0, 0), tile(a2, 0, 1)
    for n, ph in ((0x41, 0), (0x42, 4)):
        f = C(8, 8)
        for yy in range(8):
            o = round(1.3 * math.sin((yy + ph) * math.pi / 4))
            hw = 2.5 + 0.8 * math.cos((yy + ph) * math.pi / 2)
            x0, x1 = int(round(4 + o - hw)), int(round(4 + o + hw))
            f.hline(yy, x0, x1, 2)
            f.px(x0, yy, 3).px(x1 - 1, yy, 3)
            if x1 - x0 > 3:
                f.px(x0 + 2, yy, 1)
        T[n] = f.a
    # 06: leaf (stem lower right); 16 17: sprout stem and soil under a leaf pair
    lf = C(8, 8)
    lf.fill(lf.pmask([(7.5, 7.5), (2.5, 6.5), (0, 0), (6.5, 2.5)]), 1, outline=3)
    lf.line(2, 2, 7, 7, 2)
    T[0x06] = lf.a
    sp = C(16, 8)
    sp.fill(sp.emask(8, 9, 7.5, 3.6), 2, outline=3)
    sp.rect(7, 0, 9, 6, 3)
    sp.px(4, 7, 1).px(11, 6, 1)
    T[0x16], T[0x17] = tile(sp.a, 0, 0), tile(sp.a, 1, 0)
    # 08 09 18 19: two-note music sign
    mu = C(16, 16)
    mu.fill(mu.emask(4.5, 12.5, 3.4, 2.5), 3)
    mu.fill(mu.emask(12, 10.5, 3.4, 2.5), 3)
    mu.rect(7, 2, 8, 12, 3).rect(14, 0, 15, 10, 3)
    mu.poly([(7, 1), (15, -1), (15, 3), (7, 5)], 3)
    mu.px(3, 12, 1).px(11, 10, 1)
    T[0x08], T[0x09], T[0x18], T[0x19] = tile(mu.a, 0, 0), tile(mu.a, 1, 0), tile(mu.a, 0, 1), tile(mu.a, 1, 1)
    # 0A 0B 1A 1B: cloud
    cl = C(16, 16)
    m = (cl.emask(5, 9.5, 4.4, 4.4) | cl.emask(10, 7, 5, 5) | cl.emask(13, 11, 3, 3)) & (cl.grid()[0] < 14)
    cl.fill(m, 1, outline=3)
    cl.a[m & (cl.a == 1) & (cl.grid()[0] > 10)] = 2
    T[0x0A], T[0x0B], T[0x1A], T[0x1B] = tile(cl.a, 0, 0), tile(cl.a, 1, 0), tile(cl.a, 0, 1), tile(cl.a, 1, 1)
    # 0C 0D 1C 1D: upper half of a bolt (the block turns it round for the lower half)
    bo = C(16, 16)
    bo.fill(bo.pmask([(9, 0), (15, 0), (11, 6), (14, 6), (9.5, 16), (6.5, 16), (8, 10), (4.5, 10)]), 1, outline=3)
    T[0x0C], T[0x0D], T[0x1C], T[0x1D] = tile(bo.a, 0, 0), tile(bo.a, 1, 0), tile(bo.a, 0, 1), tile(bo.a, 1, 1)
    # 0E 0F 1E 1F: strike sparks fanning up from the ground (32x16, mirrored)
    gs = C(32, 16)
    for tdeg, ln in ((200, 15), (225, 13), (250, 15), (270, 12)):
        t = math.radians(tdeg)
        x1, y1 = 16 + ln * math.cos(t), 16 + ln * math.sin(t)
        xm, ym = 16 + ln * 0.55 * math.cos(t) + 2, 16 + ln * 0.55 * math.sin(t)
        thick(gs, 15, 15, int(xm), int(ym))
        thick(gs, int(xm), int(ym), int(x1), int(y1))
    for x_, y_ in ((3, 3), (9, 1), (5, 9)):
        spark(gs, x_, y_, 1, 1, 3)
    a2 = symh(gs.a)
    T[0x0E], T[0x0F], T[0x1E], T[0x1F] = tile(a2, 0, 0), tile(a2, 1, 0), tile(a2, 0, 1), tile(a2, 1, 1)
    # 20 21 30 31: big sunburst star; its grainy core doubles as sand (31)
    bs = C(32, 32)
    pts = []
    for j in range(16):
        t = 2 * math.pi * j / 16 - math.pi / 2
        rr = 16 if j % 2 == 0 else 12.6
        pts.append((16 + rr * math.cos(t), 16 + rr * math.sin(t)))
    m = bs.pmask(pts) | bs.emask(16, 16, 12.6, 12.6)
    bs.a[m] = 1
    bs.pat(0, 0, 32, 32, lambda x_, y_: grain(x_, y_) if m[y_, x_] else None)
    from games.pokered import drawn
    dm = drawn.depth_map(m, edge_inside=False)
    bs.a[m & (dm == 1)] = 3
    a2 = symv(symh(bs.a))
    T[0x20], T[0x21], T[0x30], T[0x31] = tile(a2, 0, 0), tile(a2, 1, 0), tile(a2, 0, 1), tile(a2, 1, 1)
    # 2C 3C 2D (+31): sand cloud edges
    for n, kind in ((0x2C, "tl"), (0x3C, "t"), (0x2D, "r")):
        sd = C(8, 8)
        mm = np.ones((8, 8), bool)
        for yy in range(8):
            for xx in range(8):
                if kind in ("tl", "t") and yy < 2 + (1 if (xx // 2) % 2 else 0):
                    mm[yy, xx] = False
                if kind == "tl" and xx < 2 + (1 if (yy // 2) % 2 else 0):
                    mm[yy, xx] = False
                if kind == "r" and xx > 4 + round(math.sin(yy * math.pi / 4)):
                    mm[yy, xx] = False
        sd.pat(0, 0, 8, 8, lambda x_, y_: grain(x_, y_) if mm[y_, x_] else None)
        dm = drawn.depth_map(mm, edge_inside=True)
        edge = mm & (dm == 1)
        sd.a[edge] = 3
        T[n] = sd.a
    # 22 23 32 43 (+3B shine): big dark sphere; 33: small dark disc quarter
    ks = C(32, 32)
    d = dist(ks, 16, 16)
    ks.a[d < 15.6] = 3
    ks.a[(d > 13.4) & (d < 14.4)] = 2
    a2 = symv(symh(ks.a))
    T[0x22], T[0x23], T[0x32], T[0x43] = tile(a2, 0, 0), tile(a2, 1, 0), tile(a2, 0, 1), tile(a2, 1, 1)
    sh = T[0x23].copy()
    sh[4:6, 2:6] = 1
    sh[3, 3:5] = 1
    sh[6, 2:4] = 2
    T[0x3B] = sh
    kd = C(16, 16)
    d = dist(kd, 8, 8)
    kd.a[d < 7.6] = 3
    kd.a[(d > 5.6) & (d < 6.5)] = 2
    T[0x33] = tile(symv(symh(kd.a)), 0, 0)
    # 24 25 34: blast ring
    br = ring_puffs(10, 12.4, 3.8, clear=(8, 8, 16, 16), jag=True)
    T[0x24], T[0x25], T[0x34] = tile(br, 0, 0), tile(br, 1, 0), tile(br, 0, 1)
    # 26 27 / 36 37 / 28 29 / 38 39: twister 16x32
    tw = C(16, 32)
    for yy in range(32):
        hw = 7.6 - yy * 0.17
        cx = 8 + 1.6 * math.sin(yy / 4.5)
        for xx in range(16):
            u = xx + 0.5 - cx
            if abs(u) <= hw:
                band = int((u / hw * 2.2 + yy * 0.35)) % 2
                tw.a[yy, xx] = 1 if band else 2
                if abs(u) > hw - 1:
                    tw.a[yy, xx] = 3
    for yy in range(0, 32, 5):
        tw.px(int(8 + 1.6 * math.sin(yy / 4.5)), yy, 3)
    rows = [(0x26, 0x27), (0x36, 0x37), (0x28, 0x29), (0x38, 0x39)]
    for ty, (l, r) in enumerate(rows):
        T[l], T[r] = tile(tw.a, 0, ty), tile(tw.a, 1, ty)
    # 2A 2B 3A: shout lines (16x32, mirrored downwards; the middle right stays empty)
    so = C(16, 32)
    for (x0, y0, x1, y1) in ((7, 6, 2, 1), (12, 6, 11, 0), (7, 12, 1, 11), (6, 9, 0, 6)):
        thick(so, x0, y0, x1, y1, 1, 3)
    so.rect(8, 8, 16, 16, 0)
    a2 = symv(so.a)
    T[0x2A], T[0x2B], T[0x3A] = tile(a2, 0, 0), tile(a2, 1, 0), tile(a2, 0, 1)
    # 2E 2F 3E: square ring; 4D 4E 07 3F (+2F): triangle with an eye
    sq = square_ring()
    T[0x2E], T[0x2F], T[0x3E] = tile(sq, 0, 0), tile(sq, 1, 0), tile(sq, 0, 1)
    tr = C(24, 24)
    for k, sh_ in ((0, 3), (1, 1), (2, 3), (3, 0)):
        tr.a[tr.pmask([(1 + 2.3 * k, 1 + k), (23 - 2.3 * k, 1 + k), (12, 23.5 - 2.3 * k)])] = sh_
    tr.a[0:8, 8:16] = sq[0:8, 8:16]
    tr.put(" + /+#+/ + ", 11, 9)
    a2 = symh(tr.a)
    T[0x4D], T[0x4E], T[0x07], T[0x3F] = tile(a2, 0, 0), tile(a2, 0, 1), tile(a2, 1, 1), tile(a2, 1, 2)
    # 3D: seed
    sdd = C(8, 8)
    sdd.fill(sdd.pmask([(1, 6), (3, 1.5), (7, 1), (5.5, 5.5)]), 2, outline=3)
    sdd.px(4, 3, 1)
    T[0x3D] = sdd.a
    # 44: goo blob quarter; 45: goo drip
    gb = C(16, 16)
    m = gb.emask(8, 8, 7, 6.6) | gb.emask(8, 13, 2, 3)
    gb.fill(m, 2, outline=3)
    gb.px(4, 4, 1).px(5, 4, 1).px(4, 5, 1)
    T[0x44] = tile(symv(symh(gb.a)), 0, 0)
    dr = C(8, 8)
    dr.fill(dr.emask(4, 5, 2.8, 2.6) | dr.pmask([(1.5, 4.5), (4, 0), (6.5, 4.5)]), 2, outline=3)
    dr.px(3, 4, 1)
    T[0x45] = dr.a
    # 46 47 48: barrier: a glint, a glinting cell, a plain hex cell
    def hexcell(glint):
        hc = C(8, 8)
        hc.fill(hc.pmask([(2, 0.5), (6, 0.5), (8, 4), (6, 7.5), (2, 7.5), (0, 4)]), 1, outline=3)
        hc.line(2, 5, 5, 2, 2)
        if glint:
            hc.px(5, 2, 0).px(6, 3, 0).px(4, 1, 0)
        return hc.a
    gl = C(8, 8)
    spark(gl, 3, 3, 3, 1, 3)
    gl.px(2, 2, 2).px(4, 4, 2).px(2, 4, 2).px(4, 2, 2)
    T[0x46], T[0x47], T[0x48] = gl.a, hexcell(True), hexcell(False)
    # 49: small square
    T[0x49] = C(8, 8).frame(0, 0, 8, 8, 3, fill=1).rect(2, 2, 6, 6, 2).px(2, 2, 3).a
    # 4A 4B 4C: crackles around a charged ball
    T[0x4A] = C(8, 8).put("##/ #/ ##/  #/  ##/   #", 1, 1).a
    k4 = C(8, 8)
    spark(k4, 3, 3, 3, 1, 3)
    T[0x4B] = k4.a
    T[0x4C] = C(8, 8).put("#/-#/ -#/  ##/   -#/    #", 1, 1).a
    # 35: spare twinkle; 40: a petal (the falling-petals effect draws tile $40 of whichever
    # set is loaded, and the petal moves load set 1 first)
    t35 = C(8, 8)
    spark(t35, 3, 4, 2, 2, 3)
    T[0x35] = t35.a
    t40 = C(8, 8)
    t40.fill(t40.emask(3.6, 4.4, 2.6, 3.4) | t40.pmask([(1.5, 2), (6.5, 0.5), (5.5, 5)]), 1, outline=3)
    t40.line(2, 6, 5, 2, 2)
    T[0x40] = t40.a
    return T


def build(T, a):
    n = (a["w"] // 8) * (a["h"] // 8)
    missing = [i for i in range(n) if i not in T and i not in a.get("blank", [])]
    if missing:
        print("  move_anim: not drawn: " + " ".join(f"{m:02X}" for m in missing))
    return sheet([T.get(i) for i in range(n)], a["w"], a["h"])


@front("battle/move_anim_0.png")
def move_anim_0(rel, a):
    return build(set0(), a)


@front("battle/move_anim_1.png")
def move_anim_1(rel, a):
    return build(set1(), a)
