"""Ship tileset (S.S. Anne decks, cabins, kitchen)."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_lab import (BLACK, FLOOR, LIGHT, MAT, WHITE, door, edged, on, stairs_down,
                                      stairs_up, table_tiles)
from games.pokered.art.ts_overworld import PLANK, WATER

WALK = (0x04, 0x0D, 0x17, 0x1D, 0x1E, 0x23, 0x34, 0x37, 0x39, 0x4A)

SHADE = tex(lambda x, y: 2 if (x + y) % 2 == 0 else PLANK[y, x])        # deck in the shadow of a wall
RAIL = np.array([[0] * 16, [3] * 16, [1] * 16, [3] * 16] + [[2] * 16] * 3 + [[3] * 16], np.uint8)
RAIL[4:7, 7] = 3; RAIL[4:7, 15] = 3; RAIL[5, 2:5] = 1; RAIL[5, 10:13] = 1    # wainscot under the cabin wall


def outline(T):
    """The hull drawn as a thin light line on black."""
    T[0x01] = BLACK
    T[0x33] = edged(BLACK, t=[3, 1]); T[0x15] = edged(BLACK, l=[3, 1]); T[0x16] = edged(BLACK, r=[3, 1])
    T[0x05] = edged(edged(BLACK, t=[3, 1]), l=[3, 1]); T[0x05][0, 1] = 3
    T[0x06] = edged(edged(BLACK, t=[3, 1]), r=[3, 1]); T[0x06][0, 6] = 3
    c = C(8, 8, 3); c.vline(1, 0, 3, 1); T[0x25] = c.a
    c = C(8, 8, 3); c.vline(6, 0, 2, 1); c.px(7, 1, 1); T[0x26] = c.a
    T[0x11] = edged(BLACK, b=[2, 2])
    c = C(8, 8); c.a[:] = T[0x11]; c.vline(6, 0, 8, 1); T[0x22] = c.a
    c = C(8, 8); c.a[:] = T[0x11]; c.vline(1, 0, 8, 1); T[0x32] = c.a


def round_table():
    c = C(16, 16)
    c.frame(6, 8, 10, 14, 3, fill=2)
    c.ellipse(8, 14, 4.5, 1.8, 2, outline=3)
    c.ellipse(8, 5, 7.6, 4.8, 1, outline=3)
    c.hline(3, 4, 9, 0); c.hline(8, 5, 11, 2)
    return c


def seat():
    """High-backed seat: back on the wall row (16x8) and cushion (16x8); stands on the table foot."""
    c = C(16, 16)
    c.a[:8] = RAIL
    c.frame(2, 1, 14, 9, 3, fill=2); c.frame(4, 3, 12, 8, 3, fill=1)
    c.frame(1, 8, 15, 15, 3, fill=1); c.hline(9, 2, 14, 0); c.hline(13, 2, 14, 2)
    return c


def barrel():
    c = C(16, 16)
    y, x = c.grid()
    c.blob(c.emask(8, 8, 6.5, 7.8) & (y >= 1) & (y <= 14), 1.4, 1.1)
    c.hline(4, 2, 14, 3); c.hline(11, 2, 14, 3); c.hline(1, 5, 11, 3); c.hline(14, 5, 11, 3)
    c.vline(8, 5, 11, 2); c.px(5, 7, 0)
    return c


def hatch():
    """Raised deck locker along the bow, 16x16."""
    c = C(16, 16, 2)
    c.frame(0, 0, 16, 16, 3); c.hline(1, 1, 15, 1); c.vline(1, 1, 14, 1)
    c.frame(3, 3, 13, 12, 3, fill=1); c.hline(4, 4, 12, 0)
    c.line(4, 10, 11, 5, 2)
    for px in ((2, 13), (13, 13)):
        c.px(px[0], px[1], 0)
    return c


def stove():
    c = C(16, 8, 2)
    c.frame(0, 0, 16, 8, 3); c.hline(1, 1, 15, 1)
    c.frame(2, 3, 9, 7, 3, fill=0); c.hline(5, 3, 8, 2)
    c.px(11, 3, 0); c.px(13, 3, 0); c.hline(5, 11, 14, 3)
    return c


def build():
    T = {}
    outline(T)
    T[0x14] = WATER
    T[0x04] = PLANK; T[0x23] = SHADE
    T[0x1D] = FLOOR
    T[0x24] = edged(MAT, t=[0, 3]); T[0x34] = edged(MAT, b=[0, 3])
    T[0x4A] = tex(lambda x, y: 1 if (x % 4, y % 4) in ((1, 1), (3, 3)) else 2)
    # cabin wall: white upper part, wainscot, porthole, door
    T[0x12] = RAIL[:, :8].copy(); T[0x13] = RAIL[:, 8:].copy()
    T[0x20] = edged(WHITE, l=[3, 2]); T[0x21] = edged(WHITE, r=[3, 2])
    T[0x30] = edged(T[0x12], l=[3, 2]); T[0x31] = edged(T[0x13], r=[3, 2])
    c = C(16, 8)
    c.ellipse(8, 4, 4.3, 4.0, 1, outline=3); c.ellipse(8, 4, 2.4, 2.2, 2, outline=3); c.px(7, 3, 0)
    put(T, c, [[0x02, 0x03]])
    d = door(); d.a[8:, 0] = 3
    put(T, d, [[0x0E, 0x0F], [0x1E, 0x1F]])
    # stairs
    put(T, stairs_down(), [[0x27, 0x28], [0x37, 0x38]])
    put(T, stairs_up(PLANK), [[0x29, 0x2A], [0x39, 0x3A]])
    # tables, beds
    table_tiles(T, 0x09, 0x0A, 0x0C, 0x19, 0x2C, 0x1C)
    T[0x0B] = tex(lambda x, y: (3, 2, 2, 2, 3, 0, 0, 0)[y])
    c = C(16, 8)
    c.rect(0, 0, 16, 6, 2); c.frame(0, 0, 16, 6, 3); c.frame(4, 2, 12, 5, 3, fill=1); c.hline(3, 6, 10, 3)
    c.rect(0, 6, 3, 8, 3); c.rect(13, 6, 16, 8, 3)
    put(T, c, [[0x3B, 0x3C]])
    c = C(16, 16)
    c.frame(0, 0, 16, 18, 3, fill=0); c.rect(1, 1, 15, 3, 2); c.hline(3, 0, 16, 3)
    c.frame(3, 4, 13, 8, 3, fill=0); c.hline(6, 5, 11, 1)
    c.vline(1, 4, 16, 1); c.vline(14, 4, 16, 1)
    put(T, c, [[0x46, 0x47], [0x56, 0x57]])
    put(T, round_table(), [[0x07, 0x08], [0x17, 0x18]])
    put(T, seat(), [[0x54, 0x55], [0x42, 0x43]])
    # things on the tables
    c = C(8, 8, 1); c.frame(1, 2, 6, 8, 3, fill=0); c.hline(3, 2, 5, 2); c.px(6, 4, 3); c.px(7, 4, 3); c.px(7, 5, 3); c.px(6, 6, 3)
    T[0x1A] = c.a
    c = C(8, 8, 1); c.ellipse(4, 4, 3.6, 3.6, 0, outline=3); c.rect(3, 3, 6, 5, 2); c.px(3, 5, 2); c.px(2, 3, 1)
    T[0x35] = c.a
    c = C(16, 16, 1)
    c.ellipse(8, 8, 7.4, 7.0, 0, outline=3); c.ellipse(8, 8, 5.6, 5.2, 0, outline=1)
    c.ellipse(7, 8, 3.6, 2.2, 2, outline=3); c.poly([(10, 8), (13, 5.5), (13, 10.5)], 2, outline=3); c.px(5, 7, 0)
    put(T, c, [[0x40, 0x41], [0x50, 0x51]])
    c = C(16, 8, 1)
    c.frame(1, 1, 15, 7, 3, fill=0); c.vline(8, 1, 7, 3); c.vline(7, 2, 6, 1)
    c.hline(3, 3, 6, 2); c.hline(5, 3, 6, 2); c.hline(3, 10, 13, 2); c.hline(5, 10, 12, 2)
    put(T, c, [[0x44, 0x45]])
    # kitchen, cargo, deck fittings
    put(T, stove(), [[0x36, 0x2B]])
    put(T, barrel(), [[0x48, 0x49], [0x58, 0x59]])
    put(T, hatch(), [[0x2E, 0x2F], [0x3E, 0x3F]])
    c = on(SHADE, 8, 16)
    for y0 in (1, 9):
        c.vline(3, y0 + 4, y0 + 8, 3); c.vline(4, y0 + 4, y0 + 8, 1)
        c.ellipse(4, y0 + 2.5, 3.2, 2.6, 0, outline=3); c.px(4, y0 + 3, 2)
    put(T, c, [[0x2D], [0x3D]])
    # KITHBOUND additions: riveted void, white cabin floor, deck rope coil, deck ring bolt, shaded deck bucket
    T[0x00] = WHITE
    T[0x10] = tex(lambda x, y: 2 if (x, y) in ((1, 1), (5, 5)) else 3)
    T[0x0D] = tex(lambda x, y: 1 if (x, y) == (7, 7) else 0)
    c = C(8, 8).paste(PLANK, 0, 0); c.ellipse(4, 4, 3.6, 3.2, 1, outline=3); c.ellipse(4, 4, 1.6, 1.3, 2, outline=3); T[0x1B] = c.a
    c = C(8, 8).paste(PLANK, 0, 0); c.ellipse(4, 4, 2.4, 2.4, 0, outline=3); c.px(4, 4, 3); T[0x4B] = c.a
    c = C(8, 8).paste(SHADE, 0, 0); c.frame(2, 2, 7, 8, 3, fill=1); c.hline(3, 3, 6, 0); c.hline(1, 3, 6, 3); T[0x4C] = c.a
    return T


@drawer("tilesets/ship.png")
def ship(rel, a):
    return build_sheet(build(), a, WALK, "ship")
