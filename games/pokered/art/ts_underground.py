"""Underground path tileset: paved tunnel floor, shaded lane, end wall with a pipe, stairs."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_gym import FACE, rim, stairs
from games.pokered.art.ts_pokecenter import BLACK, WALL, shade

WALK = (0x0b, 0x0c, 0x13, 0x15, 0x18)

PAVE_A = tex(lambda x, y: 1 if (x == 7 or y == 7) else 0)
PAVE_B = tex(lambda x, y: 1 if (x == 7 or y == 7 or (x, y) == (3, 3)) else 0)


def end_wall():
    """24x16: left end, repeating middle, right end; a pipe runs along it on brackets."""
    c = C(24, 16)
    c.a[:8] = np.tile(WALL, (1, 3)); c.a[8:] = np.tile(FACE, (1, 3))
    c.hline(0, 0, 24, 3)
    c.rect(0, 9, 24, 12, 0); c.hline(9, 0, 24, 3); c.hline(12, 0, 24, 3); c.hline(11, 0, 24, 1)
    c.vline(0, 0, 16, 3); c.vline(23, 0, 16, 3)
    for x in (3, 19):
        c.rect(x, 8, x + 2, 14, 3)
    return c


def build():
    T = {}
    T[0x00] = np.zeros((8, 8), np.uint8)
    T[0x10] = BLACK
    T[0x01] = tex(lambda x, y: 3 if (x + y) % 2 == 0 and (x // 2 + y // 2) % 2 == 0 else 2)
    T[0x0B] = PAVE_A; T[0x0C] = PAVE_B
    T[0x18] = shade(PAVE_A); T[0x15] = shade(PAVE_B)
    T[0x02] = rim(BLACK, "t"); T[0x11] = rim(BLACK, "tl"); T[0x12] = rim(BLACK, "tr")
    T[0x17] = rim(BLACK, "l"); T[0x16] = rim(BLACK, "r")
    put(T, end_wall(), [[0x05, 0x06, 0x07], [0x08, 0x09, 0x0A]])
    put(T, stairs(np.zeros((8, 8), np.uint8)), [[0x03, 0x04], [0x13, 0x14]])
    # KITHBOUND additions: brick ceiling fill, wall lamp, wall vent
    T[0x19] = tex(lambda x, y: 2 if (y in (3, 7) or (x == 1 and y < 3) or (x == 5 and 3 < y < 7)) else 3)
    c = C(8, 8).paste(T[0x06], 0, 0); c.rect(2, 2, 6, 7, 3); c.rect(3, 3, 5, 6, 0); c.hline(7, 1, 7, 3)
    T[0x1A] = c.a
    c = C(8, 8).paste(T[0x06], 0, 0); c.frame(1, 2, 7, 8, 3, fill=2)
    for y in (4, 6):
        c.hline(y, 2, 6, 3)
    T[0x1B] = c.a
    return T


@drawer("tilesets/underground.png")
def underground(rel, a):
    return build_sheet(build(), a, WALK, "underground")
