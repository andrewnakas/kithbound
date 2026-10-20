"""Cavern tileset (Mt. Moon, Rock Tunnel, Seafoam, Victory Road, Cerulean Cave ...).
Two floor levels, both light (lower white, upper light grey); rock faces, mounds and
pits are dark so walkable ground reads at a glance."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex
from games.pokered.art.ts_overworld import WATER, on
from games.pokered.art.ts_forest import steps

WALK = (0x05, 0x15, 0x18, 0x1a, 0x20, 0x21, 0x22, 0x2a, 0x2d, 0x30)

LO = T8("""
........
.....-..
.--.....
........
........
....--..
-.......
........""")
HI = T8("""
--------
--+-----
--------
------.-
--------
-.------
-----+--
--------""")
GRAVEL = T8("""
.-...-..
...-....
-.....-.
..-.-...
.....-.-
-.-.....
...-..-.
.-....-.""")
DARKER = T8("""
.+......
........
......+.
..+.....
.....-..
+.......
...+....
......-.""")
ROCKW = T8("""
########
-+++#-++
++++#+++
++++#+++
########
+#-+++++
+#++++++
########""")
BLACK = np.full((8, 8), 3, np.uint8)
ROCK_A = T8("""
########
++-+++#+
++++++#+
-+++++#+
########
+++#++-+
++-#++++
########""")
ROCK_B = T8("""
########
+#+++-++
+#++++++
+#+-++++
########
++++-+#+
+-++++#+
########""")


def corner(flip_x=False, flip_y=False):
    """Rock corner piece; the outer corner is cut off and shows the lower floor."""
    def f(x, y):
        d = x + y
        return LO[y, x] if d < 3 else (3 if d == 3 else ROCKW[y, x])
    a = tex(f)
    if flip_x:
        a = a[:, ::-1]
    if flip_y:
        a = a[::-1]
    return a.copy()


def diag():
    """Upper floor above/right of a slanted rock edge."""
    return tex(lambda x, y: HI[y, x] if x > y else (3 if x == y else ROCKW[y, x]))


def mound():
    c = on(LO, (16, 16))
    c.blob(c.emask(8, 8.5, 7.6, 7.0), 2.0, 1.3)
    for x, y in ((4, 5), (6, 4), (5, 8)):
        c.px(x, y, 1)
    c.line(9, 6, 11, 9, 3); c.line(6, 11, 8, 12, 3); c.px(12, 11, 3)
    return c


def spikes():
    c = on(LO, (16, 16))
    for pts in ([(1, 14), (4, 3), (7, 14)], [(8, 14), (12, 1), (15, 14)], [(4, 15), (8, 7), (11, 15)]):
        c.poly(pts, 1, outline=3)
        (x0, y0), (x1, y1), _ = pts
        c.line(x1, y1 + 2, (x0 + x1) // 2 + 1, y0 - 2, 0)
    c.hline(15, 1, 15, 3)
    return c


def slab():
    c = on(HI, (16, 16))
    c.frame(1, 1, 15, 15, 3, fill=1)
    c.rect(2, 2, 14, 11, 0); c.hline(11, 2, 14, 2); c.rect(2, 12, 14, 14, 2)
    c.px(4, 4, 1); c.px(5, 4, 1); c.px(10, 7, 1); c.px(11, 7, 1)
    c.px(1, 1, 0); c.px(14, 1, 0)
    return c


def ladder_up():
    c = on(LO, (16, 16))
    c.frame(1, 0, 15, 16, 3, fill=2)
    c.vline(4, 1, 15, 0); c.vline(5, 1, 15, 0); c.vline(10, 1, 15, 0); c.vline(11, 1, 15, 0)
    for y in (3, 7, 11):
        c.rect(4, y, 12, y + 2, 0)
    return c


def ladder_down():
    c = on(LO, (16, 16))
    c.ellipse(8, 8.5, 7.6, 7.2, 3)
    c.ellipse(8, 3.2, 5.6, 1.6, 2)
    c.vline(5, 1, 11, 0); c.vline(10, 1, 11, 0)
    for y in (3, 6, 9):
        c.hline(y, 5, 11, 0)
    return c


def cave_sign():
    c = on(LO, (16, 16))
    c.rect(3, 11, 5, 16, 3); c.rect(11, 11, 13, 16, 3)
    c.frame(1, 1, 15, 12, 3, fill=0)
    c.hline(4, 3, 13, 2); c.hline(6, 3, 10, 2); c.hline(8, 3, 12, 2)
    return c


def plate():
    c = on(LO, (16, 16))
    c.ellipse(8, 8, 6.6, 6.6, 0, outline=3)
    c.ellipse(8, 8, 4.0, 4.0, 1, outline=3)
    return c


def build():
    T = {}
    T[0x00] = np.zeros((8, 8), np.uint8)
    T[0x05] = HI; T[0x20] = LO; T[0x21] = GRAVEL; T[0x2A] = DARKER; T[0x14] = WATER
    T[0x3C] = BLACK; T[0x22] = BLACK; T[0x30] = BLACK
    T[0x40] = DARKER[::-1].copy(); T[0x41] = HI[:, ::-1].copy()
    # rock faces around the upper floor
    T[0x10] = ROCKW
    c = C(8, 8).paste(HI, 0, 0); c.hline(0, 0, 8, 0); c.hline(1, 0, 8, 3); T[0x29] = c.a
    c = C(8, 8).paste(ROCKW, 0, 0); c.vline(7, 0, 8, 3); T[0x31] = c.a
    c = C(8, 8).paste(ROCKW, 0, 0); c.vline(0, 0, 8, 3); T[0x17] = c.a
    T[0x04] = corner(); T[0x07] = corner(flip_x=True)
    T[0x28] = corner(flip_y=True); T[0x11] = corner(flip_x=True, flip_y=True)
    T[0x26] = diag(); T[0x25] = diag()[:, ::-1].copy()
    put(T, steps(), [[0x15, 0x16]])
    # things on the floor
    put(T, mound(), [[0x02, 0x03], [0x12, 0x13]])
    put(T, spikes(), [[0x0C, 0x0D], [0x1C, 0x1D]])
    put(T, slab(), [[0x06, 0x27], [0x24, 0x01]])
    put(T, ladder_down(), [[0x08, 0x09], [0x18, 0x19]])
    put(T, ladder_up(), [[0x0A, 0x0B], [0x1A, 0x1B]])
    put(T, cave_sign(), [[0x0E, 0x0F], [0x1E, 0x1F]])
    put(T, plate(), [[0x2B, 0x2C], [0x2D, 0x2E]])
    c = C(8, 8).paste(LO, 0, 0); c.hline(3, 0, 8, 3); c.hline(4, 0, 8, 2); c.rect(0, 5, 8, 8, 3); T[0x2F] = c.a
    # spare pieces (no block uses them): pebble, slopes, a pit rim, a boulder top, rubble
    c = C(8, 8).paste(LO, 0, 0); c.blob(c.emask(4, 4.5, 3.2, 2.8), 1.8, 1.2); T[0x23] = c.a
    T[0x32] = tex(lambda x, y: LO[y, x] if x + y < 7 else (3 if x + y == 7 else ROCKW[y, x]))
    T[0x33] = tex(lambda x, y: HI[y, x] if x + y > 7 else (3 if x + y == 7 else ROCKW[y, x]))
    T[0x34] = tex(lambda x, y: 3 if x == y else 2)
    c = C(24, 8, 2); c.ellipse(12, -1, 11.5, 8, 0, outline=3); put(T, c, [[0x35, 0x36, 0x37]])
    T[0x38] = tex(lambda x, y: 1 if x + y > 7 else 0)
    T[0x39] = tex(lambda x, y: 1 if x > y else (3 if x == y else 0))
    T[0x3A] = tex(lambda x, y: 3 if x + y == 7 else 2)
    T[0x3B] = tex(lambda x, y: 1 if (x * 3 + y * 5) % 11 == 0 else 2)
    c = on(LO, (16, 8)); c.blob(c.emask(8, 9, 7.4, 7.6), 1.4, 1.2); put(T, c, [[0x3D, 0x3E]])
    c = C(8, 8, 2); c.blob(c.emask(2.5, 5, 2.4, 2.2), 1.4, 1.0); c.blob(c.emask(5.5, 2.5, 2.2, 2.0), 1.4, 1.0)
    T[0x3F] = c.a
    # KITHBOUND additions: our own rock face (two fill tiles that tile with each other, edge pieces
    # with a black line where the floor meets them), cracked / pebbled upper floor
    T[0x44] = ROCK_A; T[0x45] = ROCK_B
    c = C(8, 8).paste(ROCK_A, 0, 0); c.vline(0, 0, 8, 3); c.vline(1, 1, 8, 2); T[0x46] = c.a
    c = C(8, 8).paste(ROCK_B, 0, 0); c.vline(7, 0, 8, 3); c.vline(6, 1, 8, 2); T[0x47] = c.a
    c = C(8, 8).paste(ROCK_A, 0, 0); c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 1); T[0x48] = c.a
    c = C(8, 8).paste(HI, 0, 0); c.line(0, 3, 3, 5, 2); c.line(3, 5, 7, 4, 2); c.px(3, 6, 2); T[0x49] = c.a
    c = C(8, 8).paste(HI, 0, 0)
    for x, y in ((1, 1), (5, 2), (2, 5), (6, 6)):
        c.px(x, y, 3); c.px(x + 1, y, 0)
    T[0x4A] = c.a
    c = C(8, 8).paste(T[0x29], 0, 0); c.px(2, 4, 2); c.px(6, 5, 3); c.px(4, 6, 2); T[0x4B] = c.a
    return T


@drawer("tilesets/cavern.png")
def cavern(rel, a):
    return build_sheet(build(), a, WALK, "cavern")
