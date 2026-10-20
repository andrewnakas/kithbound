"""Plateau tileset (Route 23, Indigo Plateau): mountain rock, lawn, ponds and the
League building. Lawn, grass, water, trees, rock and signs are the overworld ones."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex
from games.pokered.art.ts_overworld import (FACE_L, FACE_R, LAWN, ROCK, SAND, TALL, WATER, on, sign,
                                            tree)
from games.pokered.art.ts_forest import shore

WALK = (0x1b, 0x23, 0x2c, 0x2d, 0x3b, 0x45)

FACE_D = tex(lambda x, y: 3 if (x % 4 == 1 and (y + (x // 4) * 3) % 8 < 5) else (1 if (x % 4 == 3 and (y + x) % 8 == 2) else 2))
ROOF = tex(lambda x, y: 2 if y % 4 == 3 else (2 if x == (2 if y < 4 else 6) else 1))
SIDING = tex(lambda x, y: 1 if y % 4 == 3 else 0)
LATTICE = tex(lambda x, y: 3 if (x % 4 == 1 and y % 4 == 1) else (2 if (x + y) % 4 == 0 else 1))


def boulder():
    c = on(LAWN, (16, 16))
    c.hline(14, 3, 13, 3)
    c.blob(c.emask(8, 8, 7.2, 6.4), 0.9, 1.3)
    c.px(5, 5, 0); c.px(6, 4, 0); c.line(9, 7, 11, 10, 2); c.px(6, 10, 2)
    return c


def cave_mouth():
    c = on(FACE_D, (16, 16))
    c.fill(c.emask(8, 10, 7.4, 9.2), 1, outline=3)
    c.fill(c.emask(8, 11, 5.6, 7.8), 3)
    c.rect(0, 15, 16, 16, 3)
    return c


def creature(bg):
    """Stone creature (head and body), 16x16; bg is an 8x8 pattern or None for plain."""
    c = on(bg, (16, 16)) if bg is not None else C(16, 16)
    body = c.emask(8, 12, 5.6, 5.0) | c.emask(8, 5.5, 4.4, 4.0) | c.pmask([(2, 0), (6, 3), (3, 6)]) \
        | c.pmask([(14, 0), (10, 3), (13, 6)])
    c.blob(body, 1.6, 1.1)
    c.px(6, 5, 0); c.px(10, 5, 0); c.px(6, 6, 3); c.px(10, 6, 3); c.hline(8, 7, 10, 3)
    c.px(5, 12, 1); c.px(6, 11, 1)
    return c


def tower():
    """White pillar, 2 tiles wide: cap row and a repeating shaft row."""
    c = C(16, 16)
    c.frame(0, 0, 16, 17, 3, fill=0)
    c.rect(11, 1, 15, 16, 1)
    c.hline(5, 1, 15, 3); c.hline(6, 1, 15, 2)
    for x in (3, 7, 11):
        c.rect(x, 2, x + 2, 4, 2)
    c.px(3, 11, 1); c.px(4, 11, 1); c.px(7, 14, 1); c.px(8, 14, 1)
    return c


def column():
    """Grey column: block row (cap/base), shaft row, plaque base row."""
    c = C(16, 24)
    c.frame(0, 1, 16, 7, 3, fill=1); c.hline(2, 1, 15, 0); c.hline(5, 1, 15, 2)
    c.frame(2, 8, 14, 16, 3, fill=1); c.rect(2, 8, 14, 9, 1); c.rect(2, 15, 14, 16, 1)
    c.vline(2, 8, 16, 3); c.vline(13, 8, 16, 3)
    c.rect(4, 8, 6, 16, 0); c.rect(10, 8, 13, 16, 2)
    c.frame(0, 16, 16, 24, 3, fill=2); c.frame(3, 18, 13, 22, 3, fill=0); c.hline(17, 1, 15, 1)
    return c


def big_door():
    c = C(16, 16, 2)
    c.frame(0, 0, 16, 17, 3); c.frame(2, 2, 14, 17, 3, fill=1)
    c.vline(7, 2, 16, 3); c.vline(8, 2, 16, 3)
    c.frame(3, 4, 7, 9, 2); c.frame(9, 4, 13, 9, 2)
    c.px(6, 11, 3); c.px(9, 11, 3)
    c.hline(15, 2, 14, 2)
    return c


def basin():
    c = C(16, 8)
    c.vline(3, 0, 7, 3); c.vline(4, 0, 7, 3); c.vline(11, 0, 7, 3); c.vline(12, 0, 7, 3)
    c.rect(5, 2, 11, 5, 1); c.hline(5, 3, 13, 3); c.hline(6, 3, 13, 3); c.hline(7, 4, 12, 1)
    return c


def build():
    T = {}
    blank = np.zeros((8, 8), np.uint8)
    T[0x00] = blank; T[0x23] = blank; T[0x2D] = SAND; T[0x2C] = LAWN; T[0x45] = TALL; T[0x14] = WATER
    T[0x33] = shore(top=True); T[0x32] = shore(left=True); T[0x1F] = shore(right=True)
    put(T, tree(), [[0x07, 0x08], [0x17, 0x18]])
    put(T, boulder(), [[0x2A, 0x2B], [0x22, 0x1D]])
    put(T, sign(), [[0x09, 0x0A], [0x19, 0x1A]])
    # mountain
    T[0x11] = ROCK; T[0x24] = FACE_R; T[0x27] = FACE_L; T[0x37] = FACE_D
    c = C(8, 8).paste(ROCK, 0, 0); c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 0); T[0x01] = c.a
    T[0x02] = tex(lambda x, y: 3 if x == y else (FACE_R[y, x] if x < y else 0))
    T[0x1E] = tex(lambda x, y: 3 if x + y == 7 else (FACE_L[y, x] if x + y > 7 else 0))
    T[0x13] = tex(lambda x, y: 3 if x == y else (ROCK[y, x] if x > y else FACE_D[y, x]))
    T[0x35] = tex(lambda x, y: 3 if x + y == 7 else (ROCK[y, x] if x + y < 7 else FACE_D[y, x]))
    T[0x36] = tex(lambda x, y: 3 if x == y else (FACE_D[y, x] if x > y else LAWN[y, x]))
    T[0x34] = tex(lambda x, y: 3 if x + y == 7 else (FACE_D[y, x] if x + y < 7 else LAWN[y, x]))
    put(T, cave_mouth(), [[0x39, 0x3A], [0x3B, 0x3C]])
    T[0x04] = tex(lambda x, y: 3 if (x + y) % 4 == 0 else 2)
    T[0x38] = tex(lambda x, y: 2 if (x * 3 + y * 5) % 8 < 2 else 1)
    # League building
    T[0x03] = ROOF; T[0x0F] = SIDING
    c = C(8, 8).paste(ROOF, 0, 0); c.rect(0, 4, 8, 7, 0); c.hline(3, 0, 8, 3); c.hline(7, 0, 8, 3); c.hline(6, 0, 8, 1)
    T[0x0D] = c.a
    c = C(8, 8).paste(SIDING, 0, 0); c.hline(3, 0, 8, 3); c.rect(0, 4, 8, 7, 2); c.hline(7, 0, 8, 3); T[0x0E] = c.a
    put(T, column(), [[0x15, 0x16], [0x05, 0x06], [0x30, 0x31]])
    put(T, big_door(), [[0x0B, 0x0C], [0x1B, 0x1C]])
    t = tower()
    put(T, t, [[0x20, 0x21], [0x2E, 0x2F]])
    put(T, creature(None), [[0x10, 0x12], [0x28, 0x29]])
    shaft = on(blank, (16, 8)); shaft.paste(t.a[8:16], 0, 0)
    c = creature(None)
    head = C(16, 8); head.paste(t.a[8:16], 0, 0)
    y, x = c.grid()
    m = c.emask(8, 12, 5.6, 5.0) | c.emask(8, 5.5, 4.4, 4.0) | c.pmask([(2, 0), (6, 3), (3, 6)]) \
        | c.pmask([(14, 0), (10, 3), (13, 6)])
    head.paste(c.a[0:8], 0, 0, mask=m[0:8])
    put(T, head, [[0x25, 0x26]])
    # paved court with rails (spare pieces 3F, 42, 43)
    T[0x3D] = LATTICE
    c = C(8, 8).paste(LATTICE, 0, 0); c.rect(0, 0, 8, 3, 0); c.hline(1, 0, 8, 3); c.hline(3, 0, 8, 3); T[0x3E] = c.a
    T[0x3F] = T[0x3E][::-1].copy()
    c = C(8, 8); c.rect(3, 0, 5, 8, 3); c.vline(5, 0, 8, 1); T[0x44] = c.a
    c = C(8, 8); c.rect(3, 2, 5, 8, 3); c.vline(5, 3, 8, 1); c.hline(1, 2, 6, 3); c.hline(3, 5, 8, 3); T[0x40] = c.a
    T[0x41] = T[0x40][:, ::-1].copy()
    put(T, basin(), [[0x42, 0x43]])
    return T


@drawer("tilesets/plateau.png")
def plateau(rel, a):
    return build_sheet(build(), a, WALK, "plateau")
