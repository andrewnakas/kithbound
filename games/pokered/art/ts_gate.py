"""Gate / Museum / Forest Gate tileset: chequered floor, counters and desks, carpet
lane, lookout windows and telescopes, museum booth and exhibits."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_gym import FACE, bookcase, stairs
from games.pokered.art.ts_pokecenter import BLACK, WALL, counter_front, mat, on, plant

WALK = (0x01, 0x12, 0x14, 0x1a, 0x1c, 0x37, 0x38, 0x3b, 0x3c, 0x5e)

F_W = tex(lambda x, y: 1 if (x == 7 and y == 7) else 0)
F_G = tex(lambda x, y: 0 if (x in (0, 7) or y in (0, 7)) else 1)
FLOOR = np.block([[F_W, F_G], [F_G, F_W]])                          # 16x16: 11 01 / 01 11
GLASS = np.full((8, 8), 1, np.uint8)
CARPET = tex(lambda x, y: 2 if (x + 2 * y) % 8 == 0 else 1)
FRINGE = tex(lambda x, y: (0, 3, 1, 2, 2, 1, 3, 0)[x])
TOP = tex(lambda x, y: 3 if y == 0 else (0 if y == 1 else 1))        # counter surface, far edge


def edge(a, sides, top=False):
    c = C(8, 8).paste(a, 0, 0)
    if top:
        c.hline(0, 0, 8, 3)
    if "l" in sides:
        c.vline(0, 0, 8, 3); c.vline(1, 1 if top else 0, 8, 0)
    if "r" in sides:
        c.vline(7, 0, 8, 3); c.vline(6, 1 if top else 0, 8, 2)
    return c.a


def stool(bg=FLOOR):
    c = on(bg, 16, 16)
    c.rect(3, 9, 5, 15, 3); c.rect(11, 9, 13, 15, 3); c.hline(12, 5, 11, 3)
    c.ellipse(8, 6, 6.5, 4, 1, outline=3)
    c.hline(4, 5, 10, 0)
    return c


def desk_top():
    """16x8 small table top with a mat on it."""
    c = C(16, 8, 1)
    c.hline(0, 0, 16, 3); c.vline(0, 0, 8, 3); c.vline(15, 0, 8, 3); c.hline(1, 1, 15, 0)
    c.frame(3, 3, 13, 7, 2, fill=0)
    return c


def scope():
    """8x24 lookout telescope on a stand."""
    c = C(8, 24, 0)
    c.frame(1, 2, 7, 15, 3, fill=1)
    c.rect(2, 0, 6, 3, 3); c.rect(3, 1, 5, 2, 0)
    c.vline(2, 4, 13, 0); c.hline(9, 1, 7, 3)
    c.rect(3, 15, 5, 20, 3)
    c.ellipse(4, 20.5, 3.6, 2, 2, outline=3)
    return c


def doorway():
    c = C(16, 16, 3)
    c.rect(2, 2, 14, 8, 2); c.hline(4, 4, 12, 3); c.hline(6, 3, 13, 3)
    c.rect(2, 8, 14, 16, 0); c.rect(2, 8, 14, 10, 1)
    return c


def potted_bush():
    """16x16 flowering bush in a bowl on a desk."""
    c = C(16, 16, 0)
    c.poly([(3, 11), (13, 11), (11, 16), (5, 16)], 1, outline=3)
    c.blob(c.emask(8, 6, 7.4, 5.6), 1.9, 1.2)
    for x, y in ((4, 5), (8, 3), (11, 6), (7, 8)):
        c.px(x, y, 0); c.px(x + 1, y, 0); c.px(x, y + 1, 0)
    return c


def fossil_case():
    """48x16 glass case with a skeleton of our own invention."""
    c = C(48, 16, 0)
    c.frame(0, 0, 48, 16, 3); c.rect(1, 13, 47, 15, 1); c.hline(12, 1, 47, 2)
    c.ellipse(8, 5.5, 5, 3.6, 0, outline=3); c.px(7, 5, 3); c.hline(7, 4, 9, 3)
    c.line(3, 8, 6, 10, 3); c.px(4, 6, 0)
    c.hline(4, 12, 40, 3)                                   # spine
    for x in range(15, 31, 3):
        c.vline(x, 5, 8, 3)                                 # ribs
    c.line(40, 4, 45, 9, 3)                                 # tail
    c.line(12, 5, 13, 11, 3); c.line(36, 5, 38, 11, 3)      # limbs
    c.hline(11, 11, 15, 3); c.hline(11, 36, 41, 3)
    c.line(20, 3, 26, 1, 3); c.line(26, 1, 33, 3, 3)        # wing bone
    return c


def shuttle():
    """32x8 model rocket plane lying on a display counter."""
    c = on(TOP, 32, 8)
    c.poly([(2, 5), (7, 2.2), (26, 2.2), (26, 7), (7, 7)], 0, outline=3)
    c.poly([(24, 0), (29, 0), (29, 7), (26, 7)], 2, outline=3)
    c.hline(5, 8, 24, 2); c.px(8, 4, 3); c.px(10, 4, 3); c.rect(29, 3, 31, 6, 3)
    return c


def build():
    T = {}
    T[0x11] = F_W; T[0x01] = F_G
    T[0x00] = WALL; T[0x10] = BLACK; T[0x5F] = np.zeros((8, 8), np.uint8)
    put(T, mat(), [[0x04], [0x14]])
    # counters, desks, shelves
    T[0x09] = TOP; T[0x07] = edge(TOP, "l", True); T[0x08] = edge(TOP, "r", True)
    T[0x17] = edge(GLASS, "l"); T[0x18] = edge(GLASS, "r")
    put(T, counter_front(), [[0x32, 0x33]])
    put(T, desk_top(), [[0x20, 0x21]])
    b = bookcase(); T[0x22] = b.tile(0, 0); T[0x23] = b.tile(1, 0)
    # stairs up (left) and down (right-handed, darker)
    put(T, stairs(np.zeros((8, 8), np.uint8)), [[0x0A, 0x0B], [0x1A, 0x1B]])
    c = stairs(np.zeros((8, 8), np.uint8)); c.a = c.a[:, ::-1].copy(); c.a[c.a == 0] = 1; c.rect(0, 0, 4, 3, 0)
    put(T, c, [[0x0C, 0x0D], [0x1C, 0x1D]])
    put(T, stool(), [[0x02, 0x03], [0x12, 0x13]])
    put(T, plant(FLOOR), [[0x05, 0x06], [0x15, 0x16], [0x25, 0x26], [0x35, 0x36]])
    put(T, potted_bush(), [[0x0E, 0x0F], [0x1E, 0x1F]])
    put(T, doorway(), [[0x2B, 0x29], [0x3B, 0x2A]])
    # carpet lane
    T[0x38] = CARPET; T[0x37] = FRINGE; T[0x5E] = FRINGE.T.copy()
    # lookout: windows and telescopes
    T[0x3A] = GLASS
    T[0x2D] = tex(lambda x, y: 0 if x + y in (6, 7, 8) else 1)
    T[0x3D] = tex(lambda x, y: 0 if x + y == 7 else 1)
    T[0x3E] = tex(lambda x, y: (1, 1, 3, 0, 2, 3, 1, 1)[x])
    put(T, scope(), [[0x24], [0x34], [0x39]])
    # museum booth
    c = C(8, 8, 2); c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 1); c.hline(7, 0, 8, 3); T[0x28] = c.a
    T[0x27] = edge(T[0x28], "l"); T[0x19] = edge(T[0x28], "r")
    T[0x30] = edge(GLASS, "l"); T[0x30][:, 1] = 2
    T[0x3C] = TOP.copy(); T[0x3C][7, :] = 2
    T[0x31] = edge(T[0x3C], "l"); T[0x2C] = edge(GLASS, "r"); T[0x2F] = edge(GLASS, "r"); T[0x2F][:, 5] = 2
    c = C(16, 8, 1); c.frame(3, 0, 13, 7, 3, fill=2); c.vline(6, 1, 6, 1); c.vline(9, 1, 6, 1); c.rect(6, 7, 10, 8, 3)
    put(T, c, [[0x46, 0x47]])
    c = C(8, 8, 1); c.ellipse(4, 4, 3.6, 3.2, 0, outline=3); c.px(3, 3, 1); T[0x2E] = c.a
    c = on(TOP, 16, 8); c.frame(2, 1, 15, 8, 3, fill=0)
    c.pat(4, 3, 13, 7, lambda x, y: 3 if (x % 2 == 0 and y % 2 == 1) else None)
    put(T, c, [[0x53, 0x3F]])
    # museum walls and exhibits
    T[0x48] = tex(lambda x, y: 0 if (abs(x - 3) + abs(y - 3) == 1) else 1)
    T[0x4A] = FACE
    c = on(T[0x48], 16, 8); c.frame(1, 0, 15, 8, 3, fill=0); c.poly([(3, 7), (8, 2), (11, 5), (13, 4), (14, 7)], 2); c.px(4, 2, 3)
    put(T, c, [[0x4E, 0x4F]])
    put(T, fossil_case(), [[0x40, 0x41, 0x42, 0x43, 0x44, 0x45], [0x50, 0x51, 0x52, 0x52, 0x54, 0x55]])
    put(T, shuttle(), [[0x56, 0x57, 0x58, 0x59]])
    c = on(TOP, 16, 8); c.blob(c.emask(8, 4.5, 5.5, 3.4), 1.6, 1.2); c.px(6, 3, 0); c.px(10, 5, 3)
    put(T, c, [[0x5A, 0x5B]])
    c = on(FLOOR, 16, 16); c.ellipse(8, 8, 7.8, 7.4, 1, outline=3); c.ellipse(8, 7, 5.4, 4.6, 0)
    c.poly([(8, 3), (11, 7), (8, 11), (5, 7)], 2, outline=3); c.px(7, 6, 0)
    put(T, c, [[0x4C, 0x4D], [0x5C, 0x5D]])
    T[0x49] = tex(lambda x, y: (3, 0, 0, 0, 0, 1, 1, 3)[x])
    c = C(8, 8, 1); c.frame(0, 0, 8, 8, 3); c.hline(1, 1, 7, 0); c.rect(1, 5, 7, 7, 2); T[0x4B] = c.a
    return T


@drawer("tilesets/gate.png")
def gate(rel, a):
    return build_sheet(build(), a, WALK, "gate")
