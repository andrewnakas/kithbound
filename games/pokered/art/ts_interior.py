"""Interior tileset: Bill's house (the two pods), the fan club and the top office floor.
Floor, wall, mat, window and painting are the shared home drawings."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_house import picture
from games.pokered.art.ts_reds_house import BLACK, FLOOR, WALL, WHITE, cv, mat, window

WALK = (0x04, 0x0f, 0x15, 0x1f, 0x3b, 0x45, 0x47, 0x55, 0x56)

TOP = np.full((8, 8), 1, np.uint8)                       # table top / carpet
PALE = tex(lambda x, y: 1 if (x % 4 == 2 and y % 4 == 1) else 0)          # pale upper wall
SKIRT = tex(lambda x, y: (0, 0, 0, 3, 1, 2, 2, 3)[y] if y != 4 or x % 2 else 2)


def rows(bgs, wt):
    """Canvas wt tiles wide, one background tile per tile row."""
    c = C(wt * 8, len(bgs) * 8)
    for j, bg in enumerate(bgs):
        c.a[j * 8:j * 8 + 8] = np.tile(bg, (1, wt))
    return c


def face(wt=2, left=True, right=True):
    """Front board of a wall / desk / stand: grooved panel."""
    w = wt * 8
    c = C(w, 8, 1)
    c.hline(0, 0, w, 3); c.hline(1, 0, w, 0); c.hline(4, 0, w, 2); c.hline(6, 0, w, 3); c.hline(7, 0, w, 2)
    if left:
        c.vline(0, 0, 7, 3)
    if right:
        c.vline(w - 1, 0, 7, 3)
    return c


def walltop(kind):
    """Top of a partition wall seen from above. kind: tl, tr, t, l, r."""
    c = C(8, 8, 2)
    if kind in ("tl", "tr", "t"):
        c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 1)
    if kind in ("tl", "l"):
        c.vline(0, 0, 8, 3); c.vline(1, 1 if kind == "tl" else 0, 8, 1)
    if kind in ("tr", "r"):
        c.vline(7, 0, 8, 3); c.vline(6, 2 if kind == "tr" else 0, 8, 3)
    return c.a


def chair(top_bg=FLOOR, bottom_bg=FLOOR):
    c = rows([top_bg, bottom_bg], 2)
    c.frame(3, 1, 13, 9, 3, fill=1); c.hline(2, 4, 12, 0); c.vline(4, 2, 8, 0)
    c.frame(2, 8, 14, 13, 3, fill=0); c.hline(11, 3, 13, 1)
    c.rect(3, 13, 5, 16, 3); c.rect(11, 13, 13, 16, 3)
    return c


def desk(bg=FLOOR):
    """Work desk seen from above/front: screen and keyboard on the left, a box unit on the right."""
    c = cv(bg, 32, 16)
    c.frame(0, 1, 32, 16, 3, fill=1); c.hline(2, 1, 31, 0)
    c.frame(2, 3, 15, 11, 3, fill=2); c.frame(4, 5, 13, 9, 3, fill=0); c.hline(6, 5, 9, 1)
    c.frame(3, 12, 14, 15, 3, fill=0); c.pat(4, 13, 13, 14, lambda x, y: 2 if x % 2 == 0 else 0)
    c.frame(18, 3, 30, 14, 3, fill=0)
    c.rect(19, 4, 29, 7, 2); c.hline(9, 20, 28, 3); c.hline(11, 20, 25, 3); c.px(27, 11, 2)
    return c


def pods():
    """Bill's machine: a tall round pod (4 x 5 tiles) with pipe stubs either side. 6 x 5 tiles."""
    c = rows([WALL, FLOOR, FLOOR, FLOOR, FLOOR], 6)
    y, x = c.grid()
    for x0, x1 in ((0, 9), (39, 48)):
        c.rect(x0, 10, x1, 16, 1); c.hline(10, x0, x1, 3); c.hline(15, x0, x1, 3); c.hline(11, x0, x1, 0)
    for x0 in (1, 43):
        c.frame(x0, 9, x0 + 4, 17, 3, fill=2)
        c.rect(x0 + 1, 17, x0 + 3, 20, 3)
    body = ((abs(x - 23.5) <= 14.5) & (y >= 7) & (y <= 31)) | c.emask(24, 7, 15, 6) | c.emask(24, 31, 15, 5.4)
    c.hline(37, 12, 36, 1)
    c.blob(body, 1.5, 1.0)
    c.ellipse(24, 7, 13, 4.6, 0, outline=3)
    c.ellipse(24, 7, 8, 2.6, 1, outline=3)
    c.hline(6, 20, 28, 0)
    c.frame(18, 15, 30, 34, 3, fill=3); c.frame(20, 18, 28, 25, 1, fill=2); c.line(21, 22, 24, 19, 0)
    c.px(27, 29, 0)
    for xx in (12, 14, 33, 35):
        c.px(xx, 17, 0); c.px(xx, 19, 3); c.hline(27, xx - 1, xx + 1, 3)
    return c


def pipe():
    c = rows([FLOOR, FLOOR], 1)
    c.rect(0, 2, 8, 8, 1); c.hline(2, 0, 8, 3); c.hline(7, 0, 8, 3); c.hline(3, 0, 8, 0)
    c.hline(8, 0, 8, 1)
    return c


def octagon():
    """The big eight-sided table, 8 x 7 tiles (only the edge tiles are cut out; the middle is TOP)."""
    c = cv(FLOOR, 64, 56)
    top = c.pmask([(16, 0), (48, 0), (64, 16), (64, 32), (48, 48), (16, 48), (0, 32), (0, 16)])
    side = c.pmask([(0, 32), (16, 48), (48, 48), (64, 32), (64, 40), (48, 56), (16, 56), (0, 40)])
    c.fill(side, 2, outline=3)
    c.fill(top, 1, outline=3)
    y, x = c.grid()
    c.a[top & (y == 1)] = 0
    inner = c.pmask([(18, 4), (46, 4), (60, 18), (60, 30), (46, 44), (18, 44), (4, 30), (4, 18)])
    c.fill(inner, 1, outline=2)                       # inlaid rim on the table top
    for xx in (20, 28, 36, 44):
        c.vline(xx, 49, 55, 3)
    c.rect(18, 55, 21, 56, 3); c.rect(43, 55, 46, 56, 3)
    return c


def centrepiece():
    """Bonsai in a bowl, the table's centrepiece (on the table top)."""
    c = cv(TOP, 16, 16)
    c.poly([(3, 11), (13, 11), (11, 16), (5, 16)], 0, outline=3)
    c.vline(8, 7, 11, 3); c.vline(7, 8, 11, 3)
    crown = c.emask(5.5, 5, 4.2, 3.4) | c.emask(10.5, 4.5, 4, 3.6) | c.emask(8, 7, 4, 2.5)
    c.blob(crown, 2.0, 1.2)
    c.px(4, 4, 0); c.px(9, 3, 0); c.px(7, 6, 0)
    return c


def sofa():
    c = rows([SKIRT, FLOOR], 4)
    y, x = c.grid()
    body = ((x >= 3) & (x <= 28) & (y >= 1) & (y <= 13)) | ((x >= 1) & (x <= 30) & (y >= 4) & (y <= 12))
    c.fill(body, 1, outline=3)
    c.hline(2, 4, 28, 0); c.hline(7, 3, 29, 3); c.hline(8, 3, 29, 0)
    c.vline(3, 5, 12, 3); c.vline(28, 5, 12, 3)
    c.rect(3, 13, 6, 15, 3); c.rect(26, 13, 29, 15, 3)
    return c


def night_window():
    """Tall window with the city at night behind it."""
    c = cv(WALL, 16, 16)
    c.frame(0, 0, 16, 15, 3, fill=3)
    for x0, h, s in ((2, 6, 1), (5, 10, 2), (9, 4, 1), (12, 8, 2)):
        c.rect(x0, 14 - h, x0 + 2, 14, s)
        c.px(x0, 15 - h, 0)
    c.px(8, 3, 0); c.px(13, 2, 0); c.px(3, 4, 0)
    c.hline(15, 0, 16, 1)
    return c


def pad():
    """Teleport pad on the floor."""
    c = cv(FLOOR, 16, 16)
    c.frame(1, 1, 15, 15, 2, fill=0)
    c.ellipse(8, 8, 5.2, 5.2, 1, outline=3)
    c.ellipse(8, 8, 2.4, 2.4, 0, outline=2)
    for x, y in ((2, 2), (13, 2), (2, 13), (13, 13)):
        c.px(x, y, 3)
    return c


def build():
    T = {}
    T[0x00] = WHITE; T[0x1F] = FLOOR; T[0x10] = WALL; T[0x2F] = BLACK
    T[0x34] = PALE; T[0x44] = SKIRT; T[0x40] = TOP; T[0x45] = FLOOR
    T[0x46], T[0x47] = mat()
    put(T, window(1), [[0x03], [0x04]])
    put(T, night_window(), [[0x05, 0x06], [0x15, 0x16]])
    put(T, pods(), [[None, 0x07, 0x08, 0x09, 0x0A, None], [0x20, 0x17, 0x18, 0x19, 0x1A, 0x25], [0x30, 0x27, 0x28, 0x29, 0x2A, 0x35],
                    [None, 0x37, 0x38, 0x39, 0x3A, None], [None, 0x50, 0x01, 0x02, 0x0F, None]])
    put(T, pipe(), [[0x26], [0x36]])
    put(T, desk(), [[0x0B, 0x0C, 0x0D, 0x0E], [0x1B, 0x1C, 0x1D, 0x1E]])
    f = face(2)
    put(T, f, [[0x5B, 0x5C]])
    T[0x58] = face(1, False, False).a
    put(T, chair(f.a[:, :8], FLOOR), [[0x2B, 0x2C], [0x3B, 0x3C]])
    put(T, chair(), [[0x3D, 0x3E], [None, None]])
    put(T, picture(c=rows([PALE, SKIRT], 2)), [[0x13, 0x14], [0x23, 0x24]])
    put(T, sofa(), [[0x31, 0x32, None, 0x33], [0x41, 0x42, None, 0x43]])
    put(T, octagon(), [[None, 0x48, 0x4A, None, None, None, 0x49, None],
                       [None] * 8,
                       [0x4D, None, None, None, None, None, None, 0x4E],
                       [None] * 8,
                       [0x3F, None, None, None, None, None, None, 0x51],
                       [0x4F, None, None, None, None, None, None, None],
                       [None, None, 0x4B, 0x4C, None, None, 0x52, None]])
    put(T, centrepiece(), [[0x11, 0x12], [0x21, 0x22]])
    T[0x2D] = walltop("tl"); T[0x2E] = walltop("tr"); T[0x57] = walltop("t")
    T[0x59] = walltop("l"); T[0x5A] = walltop("r")
    put(T, pad(), [[0x53, 0x54], [0x55, 0x56]])
    c = cv(FLOOR, 8, 16)                                   # low rail
    c.hline(2, 0, 8, 3); c.rect(0, 3, 8, 5, 1); c.hline(5, 0, 8, 3)
    c.rect(3, 0, 5, 12, 3); c.px(3, 1, 1); c.hline(12, 1, 7, 2)
    put(T, c, [[0x5D], [0x5E]])
    return T


@drawer("tilesets/interior.png")
def interior(rel, a):
    return build_sheet(build(), a, WALK, "interior")
