"""Lobby tileset (department store floors and roof, game corner, diner, elevators):
counters, shop shelves, slot machines, vending machines, stairwells, lift doors."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_gate import TOP, edge, stool
from games.pokered.art.ts_gym import FACE
from games.pokered.art.ts_pokecenter import BLACK, WALL, counter_front, mat, on, pc, shelf

WALK = (0x14, 0x17, 0x1a, 0x1c, 0x20, 0x38, 0x45)

TILE = tex(lambda x, y: 1 if (x == 7 or y == 7) else 0)             # small floor tiles
WHITE = tex(lambda x, y: 1 if (x == 7 and y == 7) else 0)
GREY = np.full((8, 8), 1, np.uint8)
DARK = np.full((8, 8), 2, np.uint8)


def stairwell(up=True):
    """16x16 stair opening set into the back wall."""
    c = C(16, 16, 3)
    if up:
        c.rect(1, 1, 15, 16, 0)
        for k in range(5):
            c.hline(3 + k * 3, 1 + (4 - k), 15 - (4 - k), 3); c.hline(4 + k * 3, 1 + (4 - k), 15 - (4 - k), 1)
        c.line(1, 14, 5, 2, 3); c.line(14, 14, 10, 2, 3)
    else:
        c.rect(1, 1, 15, 8, 2)
        for k in range(3):
            c.hline(2 + k * 2, 3, 13, 3)
        c.rect(1, 8, 15, 16, 0); c.rect(1, 8, 15, 10, 1)
        c.poly([(1, 10), (8, 10), (1, 16)], 2)
    return c


def slot_machine():
    c = C(16, 16, 2)
    c.frame(0, 0, 16, 16, 3); c.hline(1, 1, 15, 1)
    c.rect(2, 3, 14, 9, 3)
    for i, x in enumerate((3, 7, 11)):
        c.rect(x, 4, x + 2, 8, 0); c.px(x + (i % 2), 5 + i % 2, 3)
    c.px(3, 11, 0); c.px(6, 11, 0); c.px(9, 11, 0); c.rect(12, 10, 14, 12, 1)
    c.frame(4, 12, 12, 15, 3, fill=1)
    return c


def vending():
    c = C(16, 16, 1)
    c.frame(0, 0, 16, 16, 3); c.hline(1, 1, 15, 0)
    c.frame(2, 3, 10, 12, 3, fill=0)
    c.rect(5, 5, 7, 11, 2); c.rect(5, 4, 7, 5, 3); c.hline(8, 5, 7, 0)
    for y in (4, 6, 8, 10):
        c.rect(12, y, 14, y + 1, 3)
    c.rect(3, 13, 13, 15, 3)
    return c


def till():
    """16x16 cash register and call bell on a counter top."""
    c = C(16, 16, 1)
    c.frame(1, 5, 10, 15, 3, fill=0); c.frame(3, 1, 9, 6, 3, fill=2); c.hline(3, 5, 7, 0)
    c.pat(3, 8, 9, 13, lambda x, y: 3 if (x % 2 == 1 and y % 2 == 0) else None)
    c.ellipse(13, 12, 2.6, 2.6, 0, outline=3); c.px(12, 9, 3); c.px(13, 9, 3)
    return c


def shelf32():
    s = shelf().a
    c = C(32, 32)
    c.a[:, :8] = s[:, :8]; c.a[:, 8:16] = s[:, 8:16]; c.a[:, 16:24] = s[:, 8:16]; c.a[:, 24:] = s[:, 16:]
    c.a[8:16, 16:24] = c.a[8:16, 16:24][:, ::-1]
    c.rect(17, 2, 23, 6, 2); c.hline(3, 18, 22, 0)
    return c


def big_table():
    """32x32 eight-sided table on a foot (the plain middle tiles are not cut from here)."""
    c = C(32, 32, 0)
    pts = [(8, 0), (24, 0), (32, 8), (32, 15), (26, 21), (21, 30), (11, 30), (6, 21), (0, 15), (0, 8)]
    c.poly(pts, 1, outline=3)
    c.line(8, 1, 1, 8, 0); c.hline(1, 8, 24, 0); c.vline(1, 8, 17, 0)
    c.line(24, 23, 20, 28, 2); c.line(30, 9, 30, 16, 2); c.line(24, 2, 30, 8, 2)
    c.rect(13, 26, 19, 29, 2)
    return c


def painting(bg=WALL):
    c = on(bg, 16, 16)
    c.frame(0, 0, 16, 15, 3, fill=0)
    c.poly([(2, 10), (6, 4), (9, 8), (11, 6), (14, 10)], 2); c.px(12, 3, 3); c.px(13, 3, 3)
    c.rect(1, 10, 15, 14, 1); c.hline(12, 3, 13, 0)
    return c


def build():
    T = {}
    T[0x00] = np.zeros((8, 8), np.uint8); T[0x5A] = T[0x00]; T[0x5E] = T[0x00]; T[0x5F] = T[0x00]
    T[0x10] = BLACK
    T[0x01] = WALL; T[0x21] = FACE
    T[0x20] = TILE; T[0x45] = WHITE; T[0x55] = WHITE; T[0x37] = GREY
    T[0x5B] = tex(lambda x, y: 1 if y == 0 else WHITE[y, x])
    put(T, mat(), [[0x04], [0x14]])
    # counters
    T[0x27] = TOP; T[0x26] = edge(TOP, "l", True); T[0x29] = edge(TOP, "r", True)
    T[0x36] = edge(GREY, "l"); T[0x39] = edge(GREY, "r")
    f = counter_front()
    T[0x15] = f.tile(0, 0); T[0x05] = f.tile(1, 0)
    c = C(8, 8).paste(T[0x15], 0, 0); c.vline(1, 0, 8, 3); T[0x30] = c.a
    c = C(8, 8).paste(T[0x15], 0, 0); c.vline(7, 0, 8, 3); c.vline(6, 0, 8, 3); T[0x31] = c.a
    put(T, till(), [[0x24, 0x25], [0x34, 0x35]])
    m = pc(GREY)
    put(T, m, [[0x0E, 0x0F], [0x1E, 0x1F]])
    # stairs and lift
    put(T, stairwell(True), [[0x0C, 0x0D], [0x1C, 0x1D]])
    put(T, stairwell(False), [[0x0A, 0x0B], [0x1A, 0x1B]])
    c = C(8, 16, 2); c.frame(0, 0, 8, 17, 3); c.vline(1, 1, 16, 1); c.rect(3, 6, 5, 9, 3); c.hline(15, 1, 7, 1)
    put(T, c, [[0x28], [0x38]])
    c = on(WALL, 8, 16); c.a[8:] = FACE
    c.frame(1, 2, 7, 12, 3, fill=0); c.rect(3, 4, 5, 6, 3); c.rect(3, 8, 5, 10, 2)
    put(T, c, [[0x06], [0x16]])
    # seats and tables
    put(T, stool(np.block([[TILE, TILE], [TILE, TILE]])), [[0x07, 0x08], [0x17, 0x18]])
    c = C(8, 8, 0); c.rect(1, 1, 7, 4, 1); c.frame(0, 0, 8, 4, 3); c.rect(1, 4, 3, 8, 3); c.rect(5, 4, 7, 8, 3); T[0x11] = c.a
    t = big_table()
    put(T, t, [[0x09, None, None, 0x19], [None] * 4, [0x46, None, None, 0x47], [None, 0x56, 0x57, None]])
    # machines and goods
    put(T, slot_machine(), [[0x22, 0x23], [0x32, 0x33]])
    put(T, vending(), [[0x02, 0x03], [0x12, 0x13]])
    put(T, shelf32(), [[0x2A, 0x2B, 0x2C, 0x2D], [0x3A, 0x3B, 0x3C, 0x3D], [0x40, 0x41, 0x42, 0x43], [0x50, 0x51, 0x52, 0x53]])
    # wall things
    c = on(WALL, 16, 8); c.frame(0, 0, 16, 8, 3, fill=0); c.hline(2, 2, 9, 3); c.hline(4, 2, 13, 2); c.rect(11, 2, 14, 3, 3)
    put(T, c, [[0x2E, 0x2F]])
    c = on(WALL, 8, 16); c.a[8:] = FACE
    c.frame(1, 1, 7, 12, 3, fill=0); c.ellipse(4, 4.5, 2, 2, 2); c.hline(8, 2, 6, 3); c.hline(10, 2, 5, 1)
    put(T, c, [[0x3E], [0x3F]])
    put(T, painting(), [[0x48, 0x49], [0x58, 0x59]])
    T[0x44] = tex(lambda x, y: 3 if y == 0 else (0 if y == 1 else (2 if (y == 5 and x % 4 == 1) else 1)))
    T[0x54] = tex(lambda x, y: 3 if y == 7 else (1 if (x % 4 == 1 and y % 4 == 1) else 2))
    T[0x4A] = tex(lambda x, y: 3 if (x + y) % 2 == 0 and (x // 2 + y // 2) % 2 == 0 else 2)
    # roof: parapet rails and the drop beyond
    T[0x4F] = DARK
    r = C(16, 8, 2); r.vline(2, 0, 8, 3); r.rect(3, 0, 5, 8, 0); r.vline(5, 0, 8, 1); r.rect(6, 0, 16, 8, 2)
    r.vline(6, 0, 8, 3); r.vline(12, 0, 8, 3); r.vline(13, 0, 8, 1); r.vline(14, 0, 8, 3)
    put(T, r, [[0x4B, 0x4C]])
    r2 = C(16, 8); r2.a[:] = r.a; r2.rect(0, 5, 16, 8, 2); r2.hline(5, 2, 15, 3)
    put(T, r2, [[0x4D, 0x4E]])
    T[0x5C] = tex(lambda x, y: (2, 2, 3, 0, 0, 1, 3, 2)[y])
    T[0x5D] = tex(lambda x, y: (2, 2, 2, 3, 1, 3, 2, 2)[y])
    return T


@drawer("tilesets/lobby.png")
def lobby(rel, a):
    return build_sheet(build(), a, WALK, "lobby")
