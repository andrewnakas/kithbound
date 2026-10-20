"""Gym / Dojo tileset (also Oak's lab, the Elite Four rooms and the Hall of Fame):
board floor, partition walls seen from above, statues, boulders, pool, bins,
spinner arrows, lab tables and bookshelves."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_overworld import FLOWER, LAWN, WATER, bush, tree
from games.pokered.art.ts_pokecenter import BLACK, WALL, ball, counter_top, mat, on

WALK = (0x11, 0x16, 0x19, 0x2b, 0x3c, 0x3d, 0x3f, 0x4a, 0x4c, 0x4d, 0x03)

BOARDS = tex(lambda x, y: 1 if y in (3, 7) else 0)                  # gym floor boards
FACE = tex(lambda x, y: 3 if y == 7 else (2 if y in (3, 5, 6) else 1))   # wall foot with skirting
RAIL = tex(lambda x, y: (1, 1, 1, 3, 0, 1, 2, 3)[y])               # wall foot with a dado rail


def rim(a, sides):
    """Black/light/dark rim of a partition top on the given sides ('l', 'r', 't')."""
    c = C(8, 8).paste(a, 0, 0)
    for s in sides:
        for k, v in enumerate((3, 1, 2)):
            if s == "t":
                c.hline(k, 0, 8, v)
            elif s == "l":
                c.vline(k, 0, 8, v)
            else:
                c.vline(7 - k, 0, 8, v)
    if "t" in sides and "l" in sides:
        c.rect(0, 0, 1, 8, 3); c.rect(0, 0, 8, 1, 3); c.vline(1, 1, 8, 1); c.hline(1, 1, 8, 1); c.rect(2, 2, 8, 3, 2); c.rect(2, 2, 3, 8, 2)
    if "t" in sides and "r" in sides:
        c.rect(7, 0, 8, 8, 3); c.rect(0, 0, 8, 1, 3); c.vline(6, 1, 8, 1); c.hline(1, 0, 7, 1); c.rect(0, 2, 6, 3, 2); c.rect(5, 2, 6, 8, 2)
    return c.a


def statue(bg=BOARDS):
    """16x32: stone creature on a pedestal with a name plate."""
    c = on(bg, 16, 32)
    c.poly([(3, 18), (13, 18), (14, 31), (2, 31)], 1, outline=3)
    c.hline(31, 2, 14, 3)
    c.frame(2, 16, 14, 20, 3, fill=0)
    c.frame(5, 23, 11, 28, 3, fill=0); c.hline(25, 7, 9, 2)
    m = (c.emask(8, 12, 5.5, 4.5) | c.emask(8, 6, 4.5, 4)
         | c.pmask([(3, 0), (6, 4), (3, 6)]) | c.pmask([(13, 0), (10, 4), (13, 6)]))
    c.blob(m, 1.4, 1.2)
    c.px(6, 6, 3); c.px(10, 6, 3); c.hline(8, 7, 10, 3)
    c.vline(8, 11, 15, 3)
    return c


def boulder(bg=BOARDS):
    c = on(bg, 16, 16)
    c.blob(c.emask(8, 8.5, 7.6, 7.2), 1.3, 1.3)
    c.line(9, 4, 11, 7, 3); c.line(11, 7, 10, 10, 3); c.px(5, 10, 3); c.px(6, 11, 3)
    return c


def slab():
    """16x16 stepping slab."""
    c = C(16, 16, 0)
    c.frame(0, 0, 16, 16, 3); c.frame(1, 1, 15, 15, 1)
    c.hline(14, 1, 15, 2); c.vline(14, 1, 15, 2)
    return c


def bin_(bg=BOARDS):
    """16x16 waste bin."""
    c = on(bg, 16, 16)
    c.poly([(2, 5), (14, 5), (12, 15), (4, 15)], 1, outline=3)
    c.hline(15, 4, 12, 3)
    c.ellipse(8, 5, 6.5, 3.2, 2, outline=3)
    c.ellipse(8, 5, 3.5, 1.4, 3)
    c.vline(6, 9, 14, 2); c.vline(9, 9, 14, 2); c.vline(11, 9, 13, 0)
    return c


def bookcase():
    """16x24: one repeating row of books over a row of doors."""
    c = C(16, 16, 0)
    c.rect(0, 0, 16, 8, 3)
    for i, (x, s) in enumerate(((1, 1), (3, 0), (5, 2), (7, 1), (10, 0), (12, 2), (13, 1))):
        c.rect(x, 1 + (i % 2), x + 2, 7, s)
    c.rect(9, 5, 10, 7, 1)
    c.frame(0, 8, 16, 16, 3, fill=2)
    c.vline(7, 8, 15, 3); c.vline(8, 8, 15, 3); c.px(5, 11, 0); c.px(10, 11, 0); c.hline(9, 1, 7, 1); c.hline(9, 9, 15, 1)
    return c


def table_top(w=24):
    c = C(w, 16, 1)
    c.hline(0, 0, w, 3); c.vline(0, 0, 16, 3); c.vline(w - 1, 0, 16, 3)
    c.hline(1, 1, w - 1, 0); c.vline(1, 1, 16, 0); c.vline(w - 2, 2, 16, 2)
    return c


def table_front(bg=BOARDS):
    c = on(bg, 24, 8)
    c.rect(0, 0, 24, 4, 2); c.hline(0, 0, 24, 3); c.hline(4, 0, 24, 3); c.vline(0, 0, 5, 3); c.vline(23, 0, 5, 3)
    c.rect(2, 4, 5, 8, 3); c.rect(19, 4, 22, 8, 3)
    return c


def terminal():
    """16x16 computer on a table top."""
    c = C(16, 16, 1)
    c.hline(0, 0, 16, 3); c.vline(0, 0, 16, 3); c.vline(1, 1, 16, 0)
    c.frame(3, 1, 14, 10, 3, fill=0); c.frame(5, 3, 12, 8, 3, fill=2); c.line(6, 6, 8, 4, 0)
    c.frame(2, 11, 15, 16, 3, fill=0)
    c.pat(4, 12, 13, 15, lambda x, y: 3 if (x % 2 == 0 and y % 2 == 1) else None)
    return c


def console():
    """16x16 instrument box on a table top."""
    c = C(16, 16, 1)
    c.hline(0, 0, 16, 3); c.vline(15, 0, 16, 3); c.vline(14, 1, 16, 2)
    c.frame(1, 3, 13, 15, 3, fill=0)
    c.frame(3, 5, 8, 10, 3, fill=2); c.px(4, 6, 0)
    c.ellipse(10.5, 7.5, 1.6, 1.6, 3); c.px(10, 12, 3); c.px(4, 12, 3); c.px(6, 12, 3); c.px(8, 12, 2)
    return c


def chart(bg=WALL):
    """16x16 framed wall chart."""
    c = on(bg, 16, 16)
    c.frame(1, 0, 15, 15, 3, fill=0)
    c.hline(1, 2, 14, 2); c.hline(15, 3, 13, 2)
    c.line(3, 10, 6, 6, 3); c.line(6, 6, 9, 9, 3); c.line(9, 9, 12, 4, 3)
    c.hline(12, 3, 13, 1); c.vline(4, 11, 13, 2); c.vline(8, 11, 13, 2); c.vline(11, 11, 13, 2)
    return c


def double_door():
    c = C(16, 16, 2)
    c.frame(0, 0, 16, 16, 3); c.vline(7, 0, 16, 3); c.vline(8, 0, 16, 3)
    for x0 in (2, 10):
        c.frame(x0, 2, x0 + 4, 7, 3, fill=1); c.frame(x0, 9, x0 + 4, 14, 3, fill=1)
    c.px(6, 8, 0); c.px(9, 8, 0)
    return c


def stairs(bg=BOARDS):
    """16x16 flight going up to the right."""
    c = on(bg, 16, 16)
    for k in range(4):
        x, y = 1 + k * 4, 12 - k * 3
        c.rect(x, y, 16, 16, 3); c.rect(x + 1, y + 1, 16, y + 3, 0); c.rect(x + 1, y + 3, x + 4, 16, 2)
    c.vline(15, 3, 16, 3); c.hline(15, 1, 16, 3)
    return c


def arrow_pad():
    """16x16 spinner pad; its quarters pair up into left/right/up/down chevrons."""
    c = C(16, 16, 0)
    c.frame(0, 0, 16, 16, 1)
    c.poly([(8, 1), (15, 8), (8, 15), (1, 8)], 3)
    c.poly([(8, 4), (12, 8), (8, 12), (4, 8)], 0)
    c.poly([(8, 6), (10, 8), (8, 10), (6, 8)], 2)
    return c


def build():
    T = {}
    T[0x00] = np.zeros((8, 8), np.uint8)
    T[0x0F] = BLACK
    T[0x11] = BOARDS
    T[0x15] = tex(lambda x, y: 2 if y in (3, 7) else 1)
    c = C(8, 8).paste(BOARDS, 0, 0); c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 1); T[0x01] = c.a
    c = C(8, 8).paste(BOARDS, 0, 0); c.hline(6, 0, 8, 2); c.hline(7, 0, 8, 3); T[0x28] = c.a
    T[0x1F] = tex(lambda x, y: 2 if (y == 3 and x in (1, 2, 5, 6)) else BOARDS[y, x])
    # walls
    T[0x05] = WALL; T[0x10] = FACE; T[0x56] = RAIL
    T[0x24] = rim(BLACK, "tl"); T[0x26] = rim(BLACK, "t"); T[0x27] = rim(BLACK, "tr")
    T[0x25] = rim(BLACK, "l"); T[0x35] = rim(BLACK, "r")
    T[0x42] = rim(FACE, "l"); T[0x3E] = rim(FACE, "r")
    T[0x44] = rim(WALL, "l"); T[0x47] = rim(WALL, "r")
    T[0x54] = rim(RAIL, "l"); T[0x57] = rim(RAIL, "r")
    c = on(WALL, 16, 8); ball(c, 8, 4, 3.4)
    put(T, c, [[0x45, 0x46]])
    T[0x3A] = counter_top()
    # water, pool edge, slabs
    T[0x14] = WATER
    T[0x04] = tex(lambda x, y: 3 if y in (0, 3) else (0 if y < 3 else (3 if x % 4 == 3 else 2)))
    put(T, slab(), [[0x09, 0x0A], [0x19, 0x1A]])
    put(T, mat(), [[0x06], [0x16]])
    # things on the floor
    put(T, statue(), [[0x02, 0x38], [0x12, 0x13], [0x22, 0x23], [0x32, 0x33]])
    put(T, boulder(), [[0x07, 0x08], [0x17, 0x18]])
    put(T, bin_(), [[0x0B, 0x0C], [0x1B, 0x1C]])
    put(T, stairs(), [[0x48, 0x49], [0x4A, 0x4B]])
    put(T, double_door(), [[0x20, 0x21], [0x30, 0x31]])
    put(T, arrow_pad(), [[0x3C, 0x3D], [0x4C, 0x4D]])
    c = C(8, 8, 0); c.frame(0, 0, 8, 8, 1); c.frame(2, 2, 6, 6, 3, fill=2); T[0x3F] = c.a
    # indoor garden
    T[0x2B] = LAWN
    T[0x03] = C(8, 8).paste(LAWN, 0, 0).put(FLOWER[0].replace(".", " "), 0, 0).a
    put(T, tree(), [[0x2C, 0x2D], [0x2E, 0x2F]])
    put(T, bush(), [[0x40, 0x41], [0x50, 0x51]])
    # lab furniture
    put(T, table_top(), [[0x29, 0x3B, 0x2A], [0x4E, 0x39, 0x4F]])
    T[0x39] = np.full((8, 8), 1, np.uint8)
    put(T, table_front(), [[0x58, 0x59, 0x5A]])
    b = bookcase()
    put(T, b, [[0x0D, 0x0E], [0x1D, 0x1E]])
    put(T, terminal(), [[0x5B, 0x5C], [0x36, 0x37]])
    put(T, console(), [[0x5D, 0x5E], [0x55, 0x5F]])
    put(T, chart(), [[0x34, 0x43], [0x52, 0x53]])
    return T


@drawer("tilesets/gym.png")
def gym(rel, a):
    return build_sheet(build(), a, WALK, "gym")
