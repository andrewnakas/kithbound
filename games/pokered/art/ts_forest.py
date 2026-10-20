"""Forest tileset (Viridian Forest, Safari Zone): lawn, tall grass, trees, a raised
terrace, ponds, rest house. Same lawn / grass / water / tree as the overworld."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex
from games.pokered.art.ts_overworld import (FACE_R, LAWN, SAND, TALL, WATER, board, door, on, sign,
                                            tree)

WALK = (0x1e, 0x20, 0x2e, 0x30, 0x34, 0x37, 0x39, 0x3a, 0x40, 0x51, 0x52, 0x5a, 0x5c, 0x5e, 0x5f)

# raised ground: light with white flecks
PLAT = np.where(LAWN == 1, 0, 1).astype(np.uint8)
ARROW = T8("""
........
...++...
..++++..
.++++++.
...++...
...++...
...++...
........""")


def terrace(top=False, left=False, right=False, bottom=False, ground=PLAT, low=0):
    """Edge piece of a raised terrace: rims on top/left, shaded faces right/bottom."""
    c = C(8, 8).paste(ground, 0, 0)
    y0 = 1 if top else 0
    if top:
        c.hline(0, 0, 8, low); c.hline(1, 0, 8, 3)
    if bottom:
        c.paste(FACE_R[3:7], 0, 3); c.hline(2, 0, 8, 3); c.hline(7, 0, 8, 3)
    if right:
        c.rect(4, y0 + 1, 7, 8, 2); c.vline(3, y0, 3 if bottom else 8, 3); c.vline(7, y0, 8, 3)
        if bottom:
            c.px(7, 7, low)
    if left:
        c.vline(0, 0, 8, low); c.vline(1, y0, 8, 3)
        if bottom:
            c.px(1, 7, low)
    return c.a


def diagonal(ground=PLAT, low=None):
    """Terrace above/right, lower ground below/left, a slanted face between."""
    low = LAWN if low is None else low

    def f(x, y):
        d = y - x
        if d < 2:
            return ground[y, x]
        if d == 2 or d == 6:
            return 3
        return 2 if d < 6 else low[y, x]
    return tex(f)


def steps():
    c = C(16, 8, 1)
    for y in (1, 4, 7):
        c.hline(y, 0, 16, 3); c.hline((y + 1) % 8, 0, 16, 0)
    c.vline(0, 0, 8, 3); c.vline(15, 0, 8, 3); c.vline(1, 0, 8, 2); c.vline(14, 0, 8, 2)
    return c


def shore(top=False, left=False, right=False, land=0):
    c = C(8, 8).paste(WATER, 0, 0)
    if top:
        c.rect(0, 0, 8, 2, land); c.hline(2, 0, 8, 3); c.hline(3, 0, 8, 1)
    if left:
        c.rect(0, 0, 2, 8, land); c.vline(2, 2 if top else 0, 8, 3); c.vline(3, 3 if top else 0, 8, 1)
    if right:
        c.rect(6, 0, 8, 8, land); c.vline(5, 2 if top else 0, 8, 3); c.vline(4, 3 if top else 0, 8, 1)
    return c.a


def big_tree():
    c = on(LAWN, (32, 32))
    c.rect(13, 22, 19, 30, 1); c.vline(13, 22, 30, 3); c.vline(18, 22, 30, 3); c.vline(16, 23, 29, 2)
    c.hline(30, 9, 23, 3); c.hline(29, 10, 13, 3); c.hline(29, 19, 22, 3)
    crown = c.emask(16, 12.5, 15.4, 11.6) | c.emask(8, 17, 7, 6) | c.emask(24, 17, 7, 6)
    c.blob(crown, 1.9, 1.3)
    for x, y in ((8, 6), (12, 4), (6, 11), (11, 9), (15, 7), (9, 14), (14, 13)):
        c.px(x, y, 1); c.px(x + 1, y, 1)
    for x, y in ((20, 10), (24, 13), (18, 16), (22, 18), (26, 16), (12, 19), (16, 20)):
        c.px(x, y, 3); c.px(x + 1, y + 1, 3)
    return c


def shrub():
    c = on(LAWN, (16, 16))
    c.hline(14, 3, 13, 3)
    c.blob(c.emask(8, 8.5, 7.4, 5.6), 2.0, 1.2)
    for x, y in ((4, 7), (7, 5), (6, 9)):
        c.px(x, y, 1)
    for x, y in ((10, 10), (12, 8), (8, 11)):
        c.px(x, y, 3)
    return c


def water_rock():
    c = on(WATER, (16, 16))
    c.blob(c.emask(8, 8, 6.6, 5.6), 0.9, 1.3)
    c.px(5, 5, 0); c.px(6, 5, 0); c.px(9, 10, 2); c.hline(14, 4, 12, 1)
    return c


def statue():
    """Stone creature on a plinth, 2 tiles wide and 3 high."""
    c = on(LAWN, (16, 24))
    y, x = c.grid()
    c.frame(1, 16, 15, 23, 3, fill=1); c.frame(3, 18, 13, 21, 3, fill=0); c.hline(23, 0, 16, 3)
    body = c.emask(8, 11, 5.2, 5.4) | c.emask(8, 5, 3.8, 3.6) | c.pmask([(3, 0), (6, 3), (3, 5)]) \
        | c.pmask([(13, 0), (10, 3), (13, 5)])
    c.blob(body, 1.5, 1.1)
    c.px(6, 5, 3); c.px(9, 5, 3); c.hline(7, 7, 9, 3)
    return c


def fence():
    c = on(LAWN, (8, 16))
    c.rect(0, 5, 8, 8, 1); c.hline(4, 0, 8, 3); c.hline(8, 0, 8, 3)
    for x in (1, 5):
        c.rect(x, 9, x + 2, 14, 1); c.vline(x - 1, 9, 15, 3); c.vline(x + 2, 9, 15, 3)
    c.hline(14, 0, 8, 3); c.hline(15, 0, 8, 2)
    return c


def house_roof():
    c = C(24, 16, 2)
    for y in (3, 7, 11):
        c.hline(y, 0, 24, 3); c.hline(y + 1, 0, 24, 1)
    c.hline(0, 0, 24, 3); c.hline(15, 0, 24, 3); c.hline(14, 0, 24, 1)
    c.vline(1, 0, 16, 3); c.vline(22, 0, 16, 3); c.vline(0, 0, 16, 0); c.vline(23, 0, 16, 0)
    return c


def siding(left=False, right=False, base=False):
    c = C(8, 8, 0)
    for y in (3, 7):
        c.hline(y, 0, 8, 1)
    if left:
        c.vline(0, 0, 8, 0); c.vline(1, 0, 8, 3); c.vline(2, 0, 8, 2)
    if right:
        c.vline(7, 0, 8, 0); c.vline(6, 0, 8, 3); c.vline(5, 0, 8, 2)
    if base:
        c.hline(7, 1 if left else 0, 7 if right else 8, 3); c.hline(6, 2 if left else 0, 6 if right else 8, 2)
    return c.a


def shutter():
    c = C(8, 8, 0)
    c.frame(0, 1, 8, 7, 3, fill=1); c.hline(3, 1, 7, 3); c.hline(5, 1, 7, 2)
    return c.a


def ladder_up(bg=LAWN):
    c = on(bg, (16, 16))
    c.rect(4, 0, 12, 15, 0)
    c.vline(4, 0, 15, 3); c.vline(5, 0, 15, 2); c.vline(11, 0, 15, 3); c.vline(10, 0, 15, 2)
    for y in (2, 6, 10, 14):
        c.hline(y, 4, 12, 3)
    return c


def ladder_down(bg=LAWN):
    c = on(bg, (16, 16))
    c.ellipse(8, 9, 7.2, 6.2, 3)
    c.ellipse(8, 9.6, 5.6, 4.4, 2)
    c.vline(5, 2, 12, 0); c.vline(10, 2, 12, 0)
    for y in (4, 7, 10):
        c.hline(y, 5, 11, 0)
    return c


def build():
    T = {}
    T[0x00] = LAWN; T[0x30] = LAWN; T[0x20] = TALL; T[0x14] = WATER; T[0x5E] = SAND
    T[0x33] = np.full((8, 8), 3, np.uint8)
    T[0x34] = C(8, 8).paste(TALL, 0, 0).put(" ## /#..#/#..#/ ## ", 2, 0).a
    T[0x37] = C(8, 8).paste(LAWN, 0, 0).put(" ++ /+--+/ ++ ", 2, 3).a
    T[0x39] = C(8, 8).paste(LAWN, 0, 0).put("+   +  +/ + + + / +++ ++/  ++++ ", 0, 3).a
    T[0x5F] = T[0x39][:, ::-1]
    # trees and shrubs
    put(T, tree(), [[0x02, 0x03], [0x12, 0x13]])
    put(T, big_tree(), [[0x04, 0x05, 0x06, 0x07], [0x23, 0x15, 0x16, 0x17], [0x24, 0x25, 0x26, 0x27],
                        [None, 0x35, 0x36, None]])
    put(T, shrub(), [[0x54, 0x55], [0x56, 0x57]])
    # terrace
    T[0x2E] = PLAT
    T[0x1D] = terrace(top=True, left=True); T[0x1E] = terrace(top=True); T[0x1F] = terrace(top=True, right=True)
    T[0x2D] = terrace(left=True); T[0x2F] = terrace(right=True)
    T[0x3D] = terrace(left=True, bottom=True); T[0x3E] = terrace(bottom=True)
    T[0x3F] = terrace(right=True, bottom=True)
    T[0x0E] = diagonal(); T[0x0F] = diagonal(PLAT[:, ::-1], LAWN[:, ::-1])[:, ::-1]
    put(T, steps(), [[0x40, 0x41]])
    # ponds
    T[0x49] = shore(top=True); T[0x48] = shore(left=True); T[0x4A] = shore(right=True)
    T[0x4D] = shore(top=True, left=True); T[0x4E] = shore(top=True, right=True)
    put(T, water_rock(), [[0x44, 0x45], [0x46, 0x47]])
    # rest house
    put(T, house_roof(), [[0x08, 0x09, 0x0C], [0x18, 0x19, 0x1C]])
    T[0x28] = siding(left=True); T[0x29] = siding(); T[0x2C] = siding(right=True)
    T[0x38] = siding(left=True, base=True); T[0x3C] = siding(right=True, base=True)
    put(T, door(), [[0x2A, 0x2B], [0x3A, 0x3B]])
    put(T, board("POKE"), [[0x10, 0x11]])
    T[0x01] = shutter()
    # things
    put(T, sign(), [[0x21, 0x22], [0x31, 0x32]])
    put(T, statue(), [[0x0A, 0x0B], [0x1A, 0x1B], [0x4B, 0x4C]])
    put(T, fence(), [[0x42], [0x43]])
    put(T, ladder_up(), [[0x0D, 0x4F], [0x5C, 0x5D]])
    put(T, ladder_down(), [[0x58, 0x59], [0x5A, 0x5B]])
    a = ARROW
    T[0x50] = a; T[0x51] = a[::-1]; T[0x52] = a.T.copy(); T[0x53] = a.T[:, ::-1].copy()
    return T


@drawer("tilesets/forest.png")
def forest(rel, a):
    return build_sheet(build(), a, WALK, "forest")
