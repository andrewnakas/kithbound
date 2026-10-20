"""KITHBOUND branding, all our own drawing: title logo, DAWN / DUSK tags, credit lines,
studio splash, Super Game Boy frame words and the KITHLOG screen parts.

Tile placement facts used (engine code, no picture):
  title logo  16x7 tiles shown as one block (rows 1..7 of the screen)
  version tag DAWN: tiles 0 1 _ 5 6 7 8 9 shown, DUSK: tiles 0..7 shown
  credit line tiles 0..4 repeat as 0 1 2 1 3 1 4 in front of every line,
              5..10 and 11..18 are lines one and two, gamefreak_inc is line three and
              also follows the 7-tile prefix on the title screen
  splash      presents tiles 0 1 2 3 _ 4 5 3 1 6 form the studio name row under the
              2x3 emblem; tiles 7..12 are never shown
Drawers here are put at the front of the list so they win over misc.py.
"""
import numpy as np

from games.pokered.art import DRAWERS, sheet
from games.pokered.art.font import G
from games.pokered.art.text import ptext, width
from games.pokered.art.tilekit import C


def front(pattern):
    def reg(fn):
        DRAWERS.insert(0, (pattern, fn))
        return fn
    return reg


def tiles_of(a):
    a = a.a if isinstance(a, C) else a
    return [a[y:y + 8, x:x + 8].copy() for y in range(0, a.shape[0], 8) for x in range(0, a.shape[1], 8)]


def dilate(m, n=1):
    out = m.copy()
    for _ in range(n):
        p = np.pad(out, 1)
        o = np.zeros_like(m)
        for dy in range(3):
            for dx in range(3):
                o |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
        out = o
    return out


def shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    out[dy:, dx:] = m[:h - dy, :w - dx]
    return out


def glyph_rows(ch):
    return G[ch].split("/")


def bold_text(c, s, x, y, shade=3, gap=2):
    """5x7 font with every stroke doubled sideways (6 px wide letters)."""
    for ch in s:
        if ch == " ":
            x += 4
            continue
        for j, r in enumerate(glyph_rows(ch)):
            for i, v in enumerate(r):
                if v == "1":
                    c.px(x + i, y + j, shade); c.px(x + i + 1, y + j, shade)
        x += 6 + gap
    return x


def bold_width(s, gap=2):
    return sum(4 if ch == " " else 6 + gap for ch in s) - gap


def sun(c, cx, cy, r, s=3):
    """A rising sun: half disc on a line with short rays."""
    m = c.emask(cx, cy, r, r) & (c.grid()[0] < cy)
    c.a[m] = s
    for dx, dy in ((-r - 2, -1), (r + 1, -1), (-r + 0, -r - 1), (r - 1, -r - 1), (0, -r - 2)):
        c.px(int(cx + dx), int(cy + dy), s)
    c.hline(int(cy), int(cx - r - 2), int(cx + r + 2), s)


def moon(c, cx, cy, r, s=3):
    m = c.emask(cx, cy, r, r) & ~c.emask(cx + r * 0.55, cy - r * 0.35, r * 0.8, r * 0.8)
    c.a[m] = s


# ---- title logo -----------------------------------------------------------------------

def kith_mask(w, h, x0, y0):
    """Chunky slab letters K I T H, 20x28 each, drawn as polygons (our own lettering)."""
    c = C(w, h)
    m = np.zeros((h, w), bool)
    x = x0
    # K
    m |= c.pmask([(x, y0), (x + 7, y0), (x + 7, y0 + 28), (x, y0 + 28)])
    m |= c.pmask([(x + 7, y0 + 11), (x + 13, y0), (x + 21, y0), (x + 11, y0 + 16), (x + 7, y0 + 18)])
    m |= c.pmask([(x + 10, y0 + 12), (x + 21, y0 + 28), (x + 13, y0 + 28), (x + 6, y0 + 17)])
    x += 25
    # I with slab serifs
    m |= c.pmask([(x + 2, y0), (x + 14, y0), (x + 14, y0 + 5), (x + 11, y0 + 5), (x + 11, y0 + 23),
                  (x + 14, y0 + 23), (x + 14, y0 + 28), (x + 2, y0 + 28), (x + 2, y0 + 23), (x + 5, y0 + 23),
                  (x + 5, y0 + 5), (x + 2, y0 + 5)])
    x += 19
    # T
    m |= c.pmask([(x, y0), (x + 21, y0), (x + 21, y0 + 6), (x + 14, y0 + 6), (x + 14, y0 + 28),
                  (x + 7, y0 + 28), (x + 7, y0 + 6), (x, y0 + 6)])
    x += 25
    # H
    m |= c.pmask([(x, y0), (x + 7, y0), (x + 7, y0 + 11), (x + 14, y0 + 11), (x + 14, y0), (x + 21, y0),
                  (x + 21, y0 + 28), (x + 14, y0 + 28), (x + 14, y0 + 17), (x + 7, y0 + 17), (x + 7, y0 + 28),
                  (x, y0 + 28)])
    return m


@front("title/pokemon_logo.png")
def kith_logo(rel, a):
    h, w = a["h"], a["w"]
    c = C(w, h)
    x0, y0 = 15, 2
    m = kith_mask(w, h, x0, y0)
    o = dilate(m)
    ext = np.zeros_like(m)
    for k in range(1, 4):                                   # deep extrusion down-right
        ext |= shift(o, k, k)
    c.a[ext] = 2
    c.a[o] = 3
    yy = c.grid()[0]
    c.a[m] = 1
    c.a[m & (yy < y0 + 9)] = 0                               # dawn-lit top, dusk-dark foot
    c.a[m & (yy >= y0 + 21)] = 2
    c.a[m & (yy == y0 + 9)] = 1
    for x in range(w):                                       # light seam between the bands
        for y in (y0 + 20,):
            if m[y, x] and (x % 2 == 0):
                c.a[y, x] = 2
    # a four-point sparkle off the H
    sx, sy = 117, 6
    for d in range(-5, 6):
        c.px(sx + d, sy, 3 if abs(d) < 5 else 2); c.px(sx, sy + d, 3 if abs(d) < 5 else 2)
    c.px(sx - 1, sy - 1, 2).px(sx + 1, sy - 1, 2).px(sx - 1, sy + 1, 2).px(sx + 1, sy + 1, 2)
    # BOUND on a ribbon
    ry0, ry1 = 38, 54
    rx0, rx1 = 22, 106
    for side in (0, 1):                                      # forked tails, folded behind
        tx = rx0 - 14 if side == 0 else rx1 + 14
        bx = rx0 + 4 if side == 0 else rx1 - 4
        pts = [(bx, ry0 + 4), (tx, ry0 + 4), (tx + (5 if side == 0 else -5), ry0 + 11), (tx, ry1 + 2), (bx, ry1 + 2)]
        c.poly(pts, 2, outline=3)
        fold = [(rx0, ry1), (rx0 + 4, ry1 + 2), (rx0 + 4, ry1 - 2)] if side == 0 else \
               [(rx1, ry1), (rx1 - 4, ry1 + 2), (rx1 - 4, ry1 - 2)]
        c.poly(fold, 3)
    c.rect(rx0, ry0, rx1, ry1, 3)
    c.hline(ry0, rx0, rx1, 2).hline(ry1 - 1, rx0, rx1, 2)
    word = "BOUND"
    gw = [np.kron(np.array([[v == "1" for v in r] for r in glyph_rows(ch)]), np.ones((1, 2), bool)) for ch in word]
    tw = sum(g.shape[1] for g in gw) + 3 * (len(gw) - 1)
    x = (rx0 + rx1 - tw) // 2
    for g in gw:                                            # 10x7 letters doubled down: 10x13
        for j in range(7):
            for i in range(g.shape[1]):
                if g[j, i]:
                    yy0 = ry0 + 1 + j * 2
                    c.px(x + i, yy0, 0); c.px(x + i, yy0 + 1, 0)
        x += g.shape[1] + 3
    return c.a


# ---- DAWN / DUSK tags (1bpp) ------------------------------------------------------------

def tag(a, icon, word, word_tile):
    c = C(a["w"], 8)
    icon(c)
    bold_text(c, word, word_tile * 8 + (40 - bold_width(word)) // 2, 0)
    return c.a


@front("title/red_version.png")
def dawn_tag(rel, a):
    def icon(c):
        sun(c, 8, 6, 4)
        c.hline(7, 1, 15, 3)
    return tag(a, icon, "DAWN", 5)


@front("title/blue_version.png")
def dusk_tag(rel, a):
    def icon(c):
        moon(c, 6, 4, 3.6)
        c.px(12, 1, 3).px(13, 4, 3).px(11, 6, 3).px(14, 2, 3)
    return tag(a, icon, "DUSK", 3)


# ---- credit lines -----------------------------------------------------------------------

def cell_digit(ch):
    c = C(8, 8)
    bold_text(c, ch, 1, 0)
    return c.a


@front("splash/copyright.png")
def kith_credits(rel, a):
    dot = C(8, 8).rect(3, 3, 5, 5, 2).a                      # 2 . 0 . 2 . 6
    pre = [cell_digit("2"), dot, cell_digit("0"), cell_digit("2"), cell_digit("6")]
    l1 = C(48, 8)
    s = "KITH CREW"
    ptext(l1, s, (48 - width(s)) // 2, 0)
    l2 = C(64, 8)
    s = "DAWN-DUSK"
    ptext(l2, s, (64 - width(s)) // 2, 0)
    return sheet(pre + tiles_of(l1) + tiles_of(l2), a["w"], a["h"])


@front("title/gamefreak_inc.png")
def kith_name_line(rel, a):
    c = C(a["w"], 8)
    s = "KITHBOUND"
    ptext(c, s, 4, 0)
    return c.a


# ---- studio splash (sprites: shade 0 shows through) --------------------------------------

@front("splash/gamefreak_presents.png")
def studio_row(rel, a):
    ts = []
    for ch in "TEAMGAS":                                     # T E A M _ G A M E S
        t = C(8, 8)
        bold_text(t, ch, 1, 0)
        ts.append(t.a)
    c = C(48, 8)
    s = "BRINGS"
    ptext(c, s, (48 - width(s)) // 2, 0)
    return sheet(ts + tiles_of(c), a["w"], a["h"])


@front("splash/gamefreak_logo.png")
def studio_emblem(rel, a):
    """A shield crest with a K monogram under a small star."""
    c = C(16, 24)
    shield = c.pmask([(1, 5), (15, 5), (15, 15), (8, 23), (1, 15)])
    c.a[shield] = 3
    inner = c.pmask([(3, 7), (13, 7), (13, 14.5), (8, 20.5), (3, 14.5)])
    c.a[inner] = 0
    c.rect(5, 8, 7, 17, 3)                                   # K
    c.line(7, 12, 11, 8, 3).line(8, 12, 12, 8, 3)
    c.line(7, 12, 11, 16, 3).line(8, 12, 11, 15, 3)
    c.px(8, 0, 1).rect(7, 1, 10, 2, 1).rect(6, 2, 11, 3, 1).px(8, 3, 1)      # star
    c.px(5, 2, 1).px(11, 1, 1)
    return c.a


# (Super Game Boy frames and the slot screen live in a_brand_screens.py)


# ---- KITHLOG screen parts ($60..$71) ----------------------------------------------------
# 60 feet mark, 61 inches mark, 62 decimal dot, 63 UL, 64 top, 65 UR, 66 left, 67 right,
# 68 divider meets left side, 69 divider stud, 6A divider meets right side, 6B divider,
# 6C LL, 6D spare bottom piece, 6E LR, 6F bottom, 70 stud on the upright, 71 upright.

def band_h(c, x0, x1, y):
    """The frame rail: black edge, a dark channel with light links, black edge."""
    c.hline(y, x0, x1, 3)
    c.rect(x0, y + 1, x1, y + 4, 2)
    for x in range(x0, x1):
        if x % 4 in (1, 2):
            c.px(x, y + 2, 1)
    c.hline(y + 4, x0, x1, 3)


def band_v(c, x, y0, y1):
    c.vline(x, y0, y1, 3)
    c.rect(x + 1, y0, x + 4, y1, 2)
    for y in range(y0, y1):
        if y % 4 in (1, 2):
            c.px(x + 2, y, 1)
    c.vline(x + 4, y0, y1, 3)


def rivet(c, x, y):
    """5x5 diamond stud."""
    c.put("  #  / #-# /#-+-#/ #-# /  #  ", x, y)


@front("pokedex/pokedex.png")
def kithlog(rel, a):
    t = {}
    f = C(24, 24)                                           # the frame as a 3x3 box
    band_h(f, 0, 24, 0)
    band_h(f, 0, 24, 19)
    band_v(f, 0, 0, 24)
    band_v(f, 19, 0, 24)
    for x, y in ((0, 0), (19, 0), (0, 19), (19, 19)):
        f.rect(x, y, x + 5, y + 5, 3)
        rivet(f, x, y)
    ft = tiles_of(f)
    t[0x63], t[0x64], t[0x65], t[0x66], t[0x67] = ft[0], ft[1], ft[2], ft[3], ft[5]
    t[0x6C], t[0x6F], t[0x6E] = ft[6], ft[7], ft[8]
    notch = ft[7].copy()                                    # bottom rail with a hanging tab
    notch[1:3, 2:6] = 3
    t[0x6D] = notch
    d = C(8, 8)                                             # divider rail across
    d.hline(2, 0, 8, 3).rect(0, 3, 8, 5, 1).hline(5, 0, 8, 3)
    d.px(1, 4, 2).px(5, 4, 2)
    t[0x6B] = d.a
    stud = d.a.copy()
    sc = C(8, 8); sc.a = stud
    sc.rect(2, 1, 6, 7, 3).rect(3, 2, 5, 6, 1).px(3, 2, 0)
    t[0x69] = sc.a
    l = C(8, 8); l.a = ft[3].copy()
    l.hline(2, 4, 8, 3).rect(4, 3, 8, 5, 1).hline(5, 4, 8, 3)
    t[0x68] = l.a
    r = C(8, 8); r.a = ft[5].copy()
    r.hline(2, 0, 4, 3).rect(0, 3, 4, 5, 1).hline(5, 0, 4, 3)
    t[0x6A] = r.a
    v = C(8, 8)
    v.vline(2, 0, 8, 3).rect(3, 0, 5, 8, 1).vline(5, 0, 8, 3)
    v.px(4, 1, 2).px(4, 5, 2)
    t[0x71] = v.a
    vs = C(8, 8); vs.a = v.a.copy()
    vs.rect(1, 2, 7, 6, 3).rect(2, 3, 6, 5, 1).px(2, 3, 0)
    t[0x70] = vs.a
    t[0x60] = C(8, 8).put("...#/..#./..#.", 2, 0).a          # feet: one slanted tick
    t[0x61] = C(8, 8).put("..#..#/.#..#./.#..#.", 0, 0).a     # inches: two ticks
    t[0x62] = C(8, 8).rect(3, 5, 5, 7, 3).a
    return sheet([t[0x60 + i] for i in range(18)], a["w"], a["h"])
