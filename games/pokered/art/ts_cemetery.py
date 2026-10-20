"""Cemetery tileset (Pokemon Tower, Agatha's room, a few houses). Same sheet layout as
the facility for walls, tables, stairs, beds and statues; graves and floor are its own."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_facility import base, bed
from games.pokered.art.ts_lab import BLACK, edged, on, shelf_row, stairs_up, table_tiles

WALK = (0x01, 0x10, 0x13, 0x1B, 0x22, 0x42, 0x52)

FLOOR = tex(lambda x, y: 1 if (x, y) in ((0, 0), (4, 4), (5, 4), (1, 0)) else 0)     # pale stone, sparse flecks


def gravestone(bg):
    """Round-topped headstone on a plinth, 16x16."""
    c = on(bg, 16, 16)
    y, x = c.grid()
    m = (c.emask(8, 6, 6.2, 5.6) | ((abs(x - 7.5) <= 6) & (y >= 6))) & (y < 13)
    c.blob(m, 0.9, 1.2)
    c.hline(5, 6, 10, 2); c.hline(7, 5, 11, 2); c.hline(9, 6, 10, 2)
    c.frame(0, 12, 16, 16, 3, fill=2); c.hline(13, 1, 15, 1)
    return c


def marker(bg):
    """Small pointed grave marker with offerings, 16x16."""
    c = on(bg, 16, 16)
    c.poly([(8, 0), (12, 4), (12, 12), (4, 12), (4, 4)], 1, outline=3)
    c.vline(6, 4, 11, 0); c.hline(6, 7, 10, 2); c.hline(8, 7, 10, 2)
    c.frame(2, 11, 14, 15, 3, fill=2); c.hline(15, 1, 15, 3)
    c.px(1, 13, 3); c.px(1, 12, 0); c.px(14, 13, 3); c.px(14, 12, 0)
    return c


def bookcase():
    c = C(16, 16, 3)
    c.a[1:9] = shelf_row().a; c.a[8:16] = shelf_row().a[:, ::-1]
    c.hline(0, 0, 16, 3); c.hline(1, 1, 15, 2)
    return c


def altar():
    """Front of the big altar, 32x16 (the two middle columns are the same tile)."""
    c = C(32, 16, 0)
    c.frame(0, 0, 32, 16, 3)
    c.rect(1, 1, 31, 3, 2); c.hline(3, 0, 32, 3)
    c.rect(1, 12, 31, 15, 2); c.hline(11, 0, 32, 3)
    for x0 in (2, 24):
        c.frame(x0, 5, x0 + 6, 10, 3, fill=1); c.px(x0 + 2, 7, 0)
    c.vline(8, 3, 12, 3); c.vline(23, 3, 12, 3)
    return c


def build():
    T = base(FLOOR)
    T[0x47] = BLACK
    T[0x10] = edged(FLOOR, t=[2, 1, 1])
    put(T, stairs_up(FLOOR), [[0x03, 0x04], [0x13, 0x14]])
    put(T, gravestone(FLOOR), [[0x09, 0x0A], [0x19, 0x1A]])
    put(T, marker(FLOOR), [[0x05, 0x06], [0x15, 0x16]])
    put(T, bookcase(), [[0x07, 0x08], [0x17, 0x18]])
    put(T, bed(1), [[0x28, 0x29], [0x38, 0x39], [0x48, 0x49]])
    table_tiles(T, None, None, None, None, None, None, 0x44, 0x45, 0x46, bg=FLOOR)
    put(T, altar(), [[0x21, 0x20, None, 0x23], [0x31, 0x30, None, 0x33]])
    # sunken dark floor behind a kerb
    T[0x1F] = tex(lambda x, y: 3 if (x % 4, y % 4) in ((0, 0), (2, 2)) else 2)
    T[0x0F] = tex(lambda x, y: (0, 3, 1, 1, 3, 2, 2, 3)[y])
    c = on(FLOOR, 8, 8); c.frame(0, 0, 8, 8, 1); c.frame(2, 2, 6, 6, 2, fill=0); T[0x22] = c.a
    # rubble (spare tiles)
    T[0x4E] = tex(lambda x, y: 2 if (x * 3 + y * 5) % 7 < 2 else (1 if (x + y * 3) % 5 == 0 else 0))
    T[0x4F] = tex(lambda x, y: 3 if (x * 5 + y * 3) % 7 < 2 else (1 if (x * 3 + y) % 5 == 0 else 2))
    # KITHBOUND additions: cracked flagstone, fallen petals, ivy on dark ground, candles on the counter
    c = on(FLOOR, 8, 8); c.line(0, 2, 3, 4, 2); c.line(3, 4, 7, 3, 2); c.line(3, 4, 4, 7, 1); T[0x5C] = c.a
    c = on(FLOOR, 8, 8)
    for (x, y) in ((1, 1), (5, 2), (3, 5), (6, 6)):
        c.px(x, y, 2); c.px(x + 1, y, 1)
    T[0x5D] = c.a
    c = C(8, 8).paste(T[0x11], 0, 0)
    for (x, y) in ((1, 1), (2, 2), (5, 1), (6, 3), (2, 5), (4, 6)):
        c.px(x, y, 1)
    c.line(1, 1, 2, 5, 3); c.line(5, 1, 4, 6, 3); T[0x5E] = c.a
    c = C(8, 8).paste(T[0x02], 0, 0); c.rect(3, 2, 5, 7, 0); c.vline(3, 2, 7, 3); c.px(4, 1, 1); c.px(4, 0, 2); T[0x5F] = c.a
    return T


@drawer("tilesets/cemetery.png")
def cemetery(rel, a):
    return build_sheet(build(), a, WALK, "cemetery")
