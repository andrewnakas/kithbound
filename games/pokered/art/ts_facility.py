"""Facility tileset (Silph Co, Rocket Hideout, Power Plant, Pokemon Mansion, Saffron and
Cinnabar gyms). The cemetery tileset shares most tile numbers and builds on base()."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_lab import (BLACK, DARK, LIGHT, WHITE, edged, machine, on, plant,
                                      stairs_down, stairs_up, table_tiles)
from games.pokered.art.ts_overworld import WATER

WALK = (0x01, 0x10, 0x11, 0x13, 0x1B, 0x20, 0x21, 0x22, 0x30, 0x31, 0x32, 0x42, 0x43, 0x48, 0x52,
        0x55, 0x58, 0x5E)

FLOOR = tex(lambda x, y: 1 if (x == 7 or y == 7) else 0)                 # white tiles, light joints
STUD = tex(lambda x, y: 1 if (x == 7 or y == 7 or (x, y) in ((3, 3), (4, 4))) else 0)   # studded floor
CARPET = tex(lambda x, y: 1 if (x % 4, y % 4) in ((1, 1), (3, 3)) else 2)
CAP = DARK                                                                # top of a wall seen from above
FACE = tex(lambda x, y: 3 if y == 7 else (2 if (y == 0 or y == 6 or x % 4 == 3) else 1))   # boarded wall face


def boulder(bg):
    c = on(bg, 16, 16)
    y, x = c.grid()
    m = c.pmask([(4, 1), (10, 0), (14, 4), (16, 10), (13, 15), (4, 15), (0, 11), (1, 5)])
    c.blob(m, 1.2, 1.4)
    c.line(4, 2, 7, 6, 2); c.line(7, 6, 13, 5, 2); c.line(7, 6, 6, 13, 2); c.line(10, 10, 13, 13, 2)
    c.px(5, 4, 0); c.px(9, 3, 0); c.px(3, 8, 0)
    return c


def cabinet():
    """Equipment cabinet, 16x16: lit top with a display, dark front."""
    c = C(16, 16, 1)
    c.frame(0, 0, 16, 16, 3)
    c.hline(1, 1, 15, 0); c.vline(1, 1, 9, 0)
    c.frame(3, 3, 13, 8, 3, fill=2); c.line(4, 6, 6, 4, 0); c.px(11, 6, 1); c.px(9, 6, 1)
    c.rect(1, 9, 15, 15, 2); c.hline(9, 0, 16, 3)
    c.hline(11, 3, 13, 3); c.hline(13, 3, 13, 3); c.px(2, 11, 0); c.px(13, 13, 1)
    return c


def bed(rows=2):
    """Bed, 16 wide: head (8), sheet (8 x rows), foot (8)."""
    h = 16 + 8 * rows
    c = C(16, h, 0)
    c.frame(0, 0, 16, h, 3)
    c.rect(1, 1, 15, 3, 2); c.hline(3, 0, 16, 3)
    c.frame(3, 4, 13, 9, 3, fill=0); c.hline(7, 4, 12, 1)
    c.vline(1, 4, h - 8, 1); c.vline(14, 4, h - 8, 1)
    c.hline(11, 2, 14, 1)
    c.rect(1, h - 8, 15, h - 1, 2); c.hline(h - 8, 0, 16, 3); c.hline(h - 6, 1, 15, 1)
    c.rect(1, h - 2, 4, h, 3); c.rect(12, h - 2, 15, h, 3)
    return c


def statue(bg):
    """Pokemon statue on a plinth with a plate, 16x24."""
    c = on(bg, 16, 24)
    y, x = c.grid()
    m = c.emask(8, 6, 4.6, 4.2) | c.emask(8, 12.5, 5.6, 4.5)
    m |= c.pmask([(3, 0), (6, 3), (4, 5)]) | c.pmask([(13, 0), (10, 3), (12, 5)])      # ears
    m |= c.pmask([(12, 13), (16, 10), (15, 15)])                                        # tail
    m &= y < 17
    c.blob(m, 1.4, 1.2)
    c.px(6, 6, 3); c.px(10, 6, 3); c.hline(8, 7, 9, 3)
    c.frame(0, 16, 16, 24, 3, fill=2); c.hline(17, 1, 15, 1)
    c.frame(3, 19, 13, 22, 3, fill=0); c.hline(20, 5, 11, 2)
    return c


def arrows(T):
    """Spinner / warp pad tiles: 21 31 over 20 30 make a diamond; pairs make arrow heads."""
    def t(fn):
        return tex(lambda x, y: 3 if fn(x, y) in (0, 1) else (2 if fn(x, y) == 2 else (1 if fn(x, y) > 2 else 0)))
    T[0x21] = t(lambda x, y: x + y - 6)          # top left:  /  inside is below right
    T[0x31] = t(lambda x, y: y - x + 1)          # top right: \  inside is below left
    T[0x20] = t(lambda x, y: x - y + 1)          # bottom left:  \  inside is above right
    T[0x30] = t(lambda x, y: 8 - x - y)          # bottom right: /  inside is above left


def walls(T):
    T[0x2A] = edged(CAP, t=[3, 1], b=[3])
    T[0x3A] = FACE
    T[0x2B] = edged(CAP, l=[3, 1]); T[0x2C] = edged(CAP, r=[3])
    T[0x2D] = edged(edged(CAP, t=[3, 1]), l=[3, 1]); T[0x2E] = edged(edged(CAP, t=[3, 1]), r=[3])
    T[0x3B] = edged(FACE, l=[3]); T[0x3C] = edged(FACE, r=[3])
    T[0x57] = tex(lambda x, y: 3 if y == 0 else (2 if (y == 1 or x % 4 == 3) else 1))
    T[0x59] = tex(lambda x, y: 3 if y == 7 else (2 if (y >= 5 or x % 4 == 3) else 1))


def base(floor=FLOOR):
    """Everything the facility and cemetery sheets have in common."""
    T = {}
    T[0x01] = floor
    T[0x11] = DARK.copy(); T[0x33] = BLACK; T[0x35] = LIGHT.copy()
    walls(T)
    # counter, tables
    T[0x02] = edged(LIGHT, t=[3, 0])
    T[0x12] = tex(lambda x, y: (1, 1, 3, 2, 2, 2, 3, 3)[y] if x % 8 != 3 or y not in (3, 4, 5) else 3)
    table_tiles(T, 0x0D, None, 0x0E, 0x1D, None, 0x1E, None, None, None)
    c = on(floor, 8, 8); c.rect(0, 0, 8, 4, 2); c.hline(0, 0, 8, 3); c.hline(4, 0, 8, 3)
    c.frame(2, 4, 6, 8, 3, fill=2); T[0x44] = c.a
    c = on(floor, 8, 8); c.rect(0, 0, 8, 4, 2); c.hline(0, 0, 8, 3); c.hline(4, 0, 8, 3); c.hline(2, 2, 6, 3); T[0x45] = c.a
    put(T, stairs_down(), [[0x0B, 0x0C], [0x1B, 0x1C]])
    put(T, boulder(floor), [[0x53, 0x54], [0x36, 0x26]])
    put(T, statue(floor), [[0x27, 0x2F], [0x37, 0x3F], [0x3D, 0x3E]])
    put(T, bed(1), [[0x28, 0x29], [0x38, 0x39], [None, None]])
    put(T, machine(2), [[0x4A, 0x4B], [0x4C, 0x4D]])
    # pillar
    c = on(floor, 16, 8)
    c.rect(5, 0, 15, 8, 1); c.vline(4, 0, 8, 3); c.vline(15, 0, 8, 3); c.vline(6, 0, 8, 0); c.rect(12, 0, 15, 8, 2)
    put(T, c, [[0x24, 0x25]])
    T[0x32] = tex(lambda x, y: 2 if (x % 4 == 3 and y % 4 == 3) else (1 if (x % 4 == 3 or y % 4 == 3) else 0))
    # carpet
    T[0x52] = CARPET
    band = tex(lambda x, y: (2, 3, 1, 1, 1, 1, 3, 2)[y] if not (y in (3, 4) and x % 4 < 2) else 2)
    T[0x42] = band.T.copy()
    # rail over a drop
    T[0x40] = tex(lambda x, y: (0, 0, 3, 1, 1, 3, 2, 2)[y])
    T[0x50] = tex(lambda x, y: 3 if y in (0, 6) or x % 4 == 0 else (2 if y == 7 else (0 if y < 3 else 1)))
    T[0x41] = tex(lambda x, y: (3, 0, 1, 1, 1, 3, 2, 2)[x])
    c = C(8, 8); c.a[:] = T[0x41]; c.frame(0, 2, 6, 7, 3, fill=0); c.rect(0, 7, 8, 8, 2); c.px(2, 4, 2); T[0x51] = c.a
    # doors in the top wall: stairwell (5A 5B / 43 34) and lift doors (56 / 58)
    c = C(16, 16, 3)
    c.rect(1, 1, 15, 16, 2); c.rect(1, 1, 15, 3, 1)
    for i in range(4):
        c.rect(2 + i * 3, 12 - i * 3, 14, 14 - i * 3, 0)
        c.hline(14 - i * 3, 2 + i * 3, 14, 3)
    c.rect(1, 14, 15, 16, 0)
    put(T, c, [[0x5A, 0x5B], [0x43, 0x34]])
    c = C(8, 16, 3)
    c.rect(1, 1, 7, 16, 1); c.vline(1, 1, 16, 0)
    c.frame(2, 3, 6, 8, 3, fill=2); c.px(3, 4, 0)
    c.px(5, 10, 3); c.px(5, 11, 3); c.rect(1, 14, 7, 16, 0)
    put(T, c, [[0x56], [0x58]])
    T[0x55] = edged(floor, b=[2, 2, 1])
    return T


def build():
    T = base()
    T[0x14] = WATER
    T[0x4F] = tex(lambda x, y: 3 if (y % 4 == 3 or x == (1 if y // 4 == 0 else 5)) else (1 if (x + y) % 5 == 0 else 2))
    put(T, stairs_up(FLOOR), [[0x03, 0x04], [0x13, 0x4E]])
    put(T, plant(FLOOR, FLOOR), [[0x05, 0x06], [0x15, 0x16], [0x07, 0x0F], [0x17, 0x1F]])
    put(T, cabinet(), [[0x09, 0x0A], [0x19, 0x1A]])
    # low lockers
    T[0x08] = edged(edged(LIGHT, t=[3, 0]), l=[3], r=[3])
    c = C(8, 8, 2); c.frame(0, 0, 8, 8, 3); c.hline(3, 2, 6, 0); c.hline(7, 0, 8, 3); T[0x18] = c.a
    arrows(T)
    band = tex(lambda x, y: (2, 3, 1, 1, 1, 1, 3, 2)[y] if not (y in (3, 4) and x % 4 < 2) else 2)
    T[0x22] = band
    # floor pad with a lamp (2x2) and single floor switch
    c = on(FLOOR, 16, 16)
    c.poly([(5, 1), (11, 1), (15, 5), (15, 11), (11, 15), (5, 15), (1, 11), (1, 5)], 1, outline=3)
    c.ellipse(8, 8, 4.2, 4.2, 2, outline=3); c.ellipse(8, 8, 2, 2, 0)
    put(T, c, [[0x23, 0x46], [0x48, 0x49]])
    c = on(FLOOR, 8, 8); c.frame(0, 0, 7, 7, 2, fill=1); c.frame(2, 2, 5, 5, 3, fill=0); T[0x5E] = c.a
    # round vent on the wall
    c = C(16, 16)
    c.a[:8] = np.tile(T[0x2A], (1, 2)); c.a[8:] = np.tile(T[0x3A], (1, 2))
    c.ellipse(8, 8, 6.5, 6.5, 1, outline=3); c.ellipse(8, 8, 4.5, 4.5, 2, outline=3)
    c.hline(8, 4, 12, 3); c.vline(8, 4, 12, 3); c.px(5, 5, 0); c.px(6, 4, 0)
    put(T, c, [[0x47, 0x5F], [0x5C, 0x5D]])
    # KITHBOUND additions: studded floor tile (10, walkable) and its twin with a cover plate (00)
    T[0x10] = STUD
    c = C(8, 8).paste(STUD, 0, 0); c.frame(1, 1, 6, 6, 2, fill=1); c.px(3, 3, 3); T[0x00] = c.a
    return T


@drawer("tilesets/facility.png")
def facility(rel, a):
    return build_sheet(build(), a, WALK, "facility")
