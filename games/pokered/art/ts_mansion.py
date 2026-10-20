"""Mansion tileset (the Celadon flats, their roof and the chief's house). Furniture is shared
with the homes; the white-topped partition walls, roof rail and roof-house front are drawn here."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_interior import chair, desk, face
from games.pokered.art.ts_reds_house import (BLACK, FLOOR, WALL, WHITE, bed, cv, mat, panel, plant, shelf_books,
                                             shelf_doors, stairs_down, stairs_up, table)

WALK = (0x01, 0x05, 0x11, 0x12, 0x14, 0x1a, 0x1c, 0x2c, 0x53)

CARPET = tex(lambda x, y: 1 if (x + 2 * y) % 4 == 0 else 0)
FACE = tex(lambda x, y: 3 if y == 7 else (1 if (x % 4 == 1 and y % 4 == 2) else 2))     # front of a partition wall


def top(l=False, r=False, t=False, b=False, dots=()):
    """Partition wall seen from above: white, black lines on the given sides, a soft inner line."""
    c = C(8, 8, 0)
    if t:
        c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 1)
    if l:
        c.vline(0, 0, 8, 3); c.vline(1, 1 if t else 0, 8, 1)
    if b:
        c.hline(7, 0, 8, 3)
    if r:
        c.vline(7, 0, 8, 3)
    for x, y in dots:
        c.px(x, y, 3)
    return c.a


def wall_foot(left):
    """Lower end of an upright wall: a little top, then its front."""
    c = C(8, 8, 0)
    c.rect(0, 2, 8, 8, 2); c.hline(2, 0, 8, 3); c.hline(7, 0, 8, 3)
    if left:
        c.vline(0, 0, 8, 3); c.vline(1, 0, 2, 1)
    else:
        c.vline(7, 0, 8, 3)
    return c.a


def rail():
    """Roof balustrade, one tile wide (repeats), two high."""
    c = cv(FLOOR, 8, 16)
    c.rect(0, 1, 8, 5, 0); c.hline(1, 0, 8, 3); c.hline(4, 0, 8, 3); c.hline(2, 0, 8, 1)
    for x in (1, 5):
        c.rect(x, 5, x + 2, 13, 3); c.px(x, 8, 1); c.px(x, 9, 1)
    c.rect(0, 13, 8, 15, 2); c.hline(12, 0, 8, 3); c.hline(15, 0, 8, 3)
    return c


def rail_post(left):
    c = rail()
    x0 = 0 if left else 3
    c.frame(x0, 0, x0 + 5, 16, 3, fill=1)
    c.vline(x0 + 1, 1, 15, 0)
    return c


def plate():
    """Name plate fixed to a wall front."""
    c = cv(FACE, 16, 8)
    c.frame(1, 0, 15, 7, 3, fill=0)
    c.hline(2, 3, 13, 2); c.hline(4, 3, 10, 2)
    return c


def door():
    """Front door set in the dark wall front."""
    c = cv(FACE, 16, 16)
    c.frame(1, 0, 15, 17, 3, fill=1)
    c.hline(1, 2, 14, 0); c.vline(2, 1, 16, 0)
    c.frame(4, 3, 12, 8, 3, fill=2); c.line(5, 6, 7, 4, 0)
    c.rect(11, 10, 13, 12, 3); c.px(11, 10, 0)
    c.hline(15, 2, 14, 2)
    return c


def trophy():
    """Shelf compartment with a small statue on a base."""
    c = C(16, 16, 3)
    c.rect(4, 12, 12, 15, 1); c.hline(12, 4, 12, 0)
    c.rect(6, 8, 10, 12, 0); c.px(5, 9, 0); c.px(10, 9, 0)
    c.ellipse(8, 5.5, 2.6, 2.6, 0); c.px(7, 5, 3); c.px(9, 5, 3)
    c.px(6, 2, 0); c.px(9, 2, 0)
    c.hline(15, 0, 16, 1); c.vline(0, 0, 16, 3); c.vline(15, 0, 16, 3)
    return c


def build():
    T = {}
    T[0x00] = WHITE; T[0x01] = FLOOR; T[0x11] = CARPET; T[0x10] = BLACK; T[0x50] = WALL
    T[0x20] = FACE; T[0x1E] = FACE; T[0x0E] = panel()
    c = C(8, 8); c.a[:] = FACE; c.vline(0, 0, 8, 3); T[0x30] = c.a
    c = C(8, 8); c.a[:] = FACE; c.vline(7, 0, 8, 3); T[0x5D] = c.a
    c = C(8, 8); c.a[:] = CARPET; c.hline(4, 0, 8, 3); c.rect(0, 5, 8, 7, 2); c.hline(7, 0, 8, 3); T[0x05] = c.a
    T[0x04], T[0x14] = mat()
    # furniture
    f = face(2)
    put(T, f, [[0x55, 0x56]])
    put(T, chair(f.a[:, :8], CARPET), [[0x02, 0x03], [0x12, 0x13]])
    put(T, desk(CARPET), [[0x24, 0x25, 0x34, 0x35], [0x40, 0x41, 0x42, 0x43]])
    put(T, plate(), [[0x06, 0x07]]); put(T, plate(), [[0x16, 0x17]])
    put(T, plant(), [[0x44, 0x45], [0x08, 0x09], [0x46, 0x47], [0x18, 0x19]])
    put(T, stairs_down(), [[0x0A, 0x0B], [0x1A, 0x1B]])
    put(T, stairs_up(), [[0x0C, 0x0D], [0x1C, 0x1D]])
    put(T, shelf_books(0), [[0x22, 0x23]])
    put(T, shelf_doors(), [[0x32, 0x33]])
    put(T, trophy(), [[0x28, 0x15], [0x38, 0x57]])
    put(T, table(3, 3, CARPET), [[0x26, 0x27, 0x29], [0x36, 0x37, 0x39], [0x3C, 0x3A, 0x3B]])
    put(T, bed(CARPET), [[0x2D, 0x2E], [0x3D, 0x3E], [0x3F, 0x2F]])
    put(T, door(), [[0x51, 0x52], [0x53, 0x54]])
    # roof rail
    put(T, rail(), [[0x0F], [0x1F]])
    put(T, rail_post(True), [[0x2A], [0x2B]])
    put(T, rail_post(False), [[0x21], [0x31]])
    # partition walls from above
    T[0x4C] = top(t=True, b=True)
    T[0x4D] = top(t=True, b=True, r=True)
    T[0x4A] = top(l=True); T[0x4B] = top(r=True)
    T[0x58] = T[0x4A]; T[0x59] = T[0x4B]
    T[0x48] = top(dots=((0, 0), (0, 7))); T[0x49] = T[0x4B]
    T[0x4E] = top(l=True, t=True); T[0x4F] = top(t=True, dots=((7, 7),))
    T[0x2C] = top(t=True, dots=((0, 7),)); T[0x5C] = top(t=True, r=True)
    T[0x5A] = wall_foot(True); T[0x5B] = wall_foot(False)
    # KITHBOUND addition: framed landscape hung on a wall front (5E 5F)
    c = cv(FACE, 16, 8)
    c.frame(1, 0, 15, 7, 3, fill=1)
    c.rect(2, 1, 14, 3, 0); c.line(2, 5, 6, 2, 2); c.line(6, 2, 9, 4, 2); c.line(9, 4, 13, 1, 2)
    c.rect(2, 5, 14, 6, 2)
    put(T, c, [[0x5E, 0x5F]])
    return T


@drawer("tilesets/mansion.png")
def mansion(rel, a):
    return build_sheet(build(), a, WALK, "mansion")
