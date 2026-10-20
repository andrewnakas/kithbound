"""Red's house tileset, and the shared home furniture (floor, wall, stool, mat, TV, plant, stairs,
table, shelf, window, bed, PC) that the other indoor tilesets import. Every piece is drawn from
what it is, in our own design."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex

WALK = (0x01, 0x02, 0x03, 0x11, 0x12, 0x13, 0x14, 0x1c, 0x1a)

FLOOR = T8("""
........
........
........
....-...
........
........
........
-...-...""")
WALL = tex(lambda x, y: 3 if y == 7 else (1 if y == 6 else (1 if x % 4 == 1 else 2)))
BLACK = np.full((8, 8), 3, np.uint8)
WHITE = np.zeros((8, 8), np.uint8)
WOOD = 1                                               # table / desk surface shade


def cv(bg, w, h):
    """Canvas w x h tiled with the 8x8 background."""
    c = C(w, h)
    c.a[:] = np.tile(bg, (h // 8, w // 8))
    return c


def stool(bg=FLOOR):
    c = cv(bg, 16, 16)
    c.rect(3, 8, 13, 13, 2)
    c.vline(2, 7, 15, 3); c.vline(13, 7, 15, 3); c.hline(12, 3, 13, 3)
    c.rect(3, 13, 5, 15, 3); c.rect(11, 13, 13, 15, 3)
    c.hline(15, 4, 12, 1)
    c.ellipse(8, 6, 6.6, 4.4, 1, outline=3)
    c.hline(4, 5, 9, 0); c.px(4, 5, 0)
    return c


def mat():
    """Door mat, two tiles high; each tile repeats sideways."""
    def top(x, y):
        if y == 0:
            return 3 if x % 2 == 0 else 0
        if y == 1:
            return 3
        if y == 2:
            return 1
        return 1 if abs((x % 8) - 3.5) + abs(y - 7.5) < 3 else 2
    t = tex(top)
    return t, t[::-1].copy()


def tv(bg=FLOOR):
    c = cv(bg, 16, 16)
    c.frame(1, 1, 15, 14, 3, fill=2)
    c.hline(2, 2, 14, 1)
    c.frame(3, 4, 11, 12, 3, fill=1)
    c.line(4, 8, 7, 5, 0); c.px(8, 9, 0)
    c.px(12, 5, 0); c.px(12, 7, 0); c.hline(9, 12, 14, 3); c.hline(11, 12, 14, 3)
    c.rect(2, 14, 5, 16, 3); c.rect(11, 14, 14, 16, 3)
    return c


def console(bg=FLOOR):
    """Game console with its pad on the floor."""
    c = cv(bg, 16, 16)
    c.frame(1, 2, 12, 9, 3, fill=1)
    c.hline(3, 2, 11, 0); c.rect(4, 5, 9, 6, 3); c.px(3, 7, 2); c.px(9, 7, 2); c.px(10, 7, 3)
    c.line(6, 9, 9, 12, 3)
    c.frame(8, 11, 16, 16, 3, fill=0)
    c.px(10, 13, 3); c.px(13, 12, 2); c.px(13, 14, 2)
    return c


def plant(bg=FLOOR):
    """Tall house plant, 2 tiles wide and 4 high."""
    c = cv(bg, 16, 32)
    c.vline(7, 14, 24, 3); c.vline(8, 14, 24, 2)
    c.line(7, 20, 3, 17, 3); c.line(8, 19, 12, 16, 3)
    c.ellipse(3, 17, 2.4, 1.6, 2, outline=3); c.ellipse(12.5, 16, 2.4, 1.6, 2, outline=3)
    c.poly([(3, 24), (13, 24), (11, 32), (5, 32)], 2, outline=3)
    c.frame(2, 22, 14, 25, 3, fill=1)
    c.vline(6, 26, 30, 1)
    crown = c.emask(4.6, 6, 4.4, 5) | c.emask(11.4, 6, 4.4, 5) | c.emask(8, 11, 5.6, 4.6) | c.emask(8, 3.5, 3.4, 3.4)
    c.blob(crown, 1.9, 1.2)
    for x, y in ((4, 4), (7, 2), (10, 5), (6, 10)):
        c.px(x, y, 0)
    c.line(8, 6, 8, 12, 3); c.line(8, 9, 5, 7, 3); c.line(8, 10, 11, 8, 3)
    return c


def stairs_up(bg=FLOOR):
    """Light steps climbing to a dark opening at the top."""
    c = cv(bg, 16, 16)
    c.rect(1, 0, 15, 16, 0)
    c.rect(1, 0, 15, 3, 3)
    for i, y in enumerate((3, 6, 9, 12)):
        c.hline(y, 1, 15, 3); c.hline(y + 1, 1, 15, 0); c.hline(y + 2, 1, 15, 1 if i < 3 else 0)
    c.hline(15, 1, 15, 1)
    c.vline(0, 0, 16, 3); c.vline(15, 0, 16, 3); c.vline(1, 0, 16, 2); c.vline(14, 0, 16, 2)
    return c


def stairs_down(bg=FLOOR):
    """Dark stairwell: steps fading into the floor below."""
    c = cv(bg, 16, 16)
    c.rect(0, 0, 16, 16, 3)
    c.hline(0, 0, 16, 1)
    for y, s, inset in ((12, 1, 1), (9, 2, 2), (6, 2, 3)):
        c.rect(inset, y, 16 - inset, y + 2, s)
    c.rect(4, 3, 12, 4, 2)
    c.vline(0, 1, 16, 1); c.vline(15, 1, 16, 1)
    c.hline(15, 0, 16, 0)
    return c


def table(wt, ht, bg=FLOOR):
    """Table seen from the front: top surface, then (last tile row) the front board and legs."""
    w, h = wt * 8, ht * 8
    c = cv(bg, w, h)
    y0 = h - 8
    c.rect(0, 0, w, y0 + 3, WOOD)
    c.hline(0, 0, w, 3); c.vline(0, 0, y0 + 3, 3); c.vline(w - 1, 0, y0 + 3, 3)
    c.hline(1, 1, w - 1, 0); c.vline(1, 1, y0 + 2, 0); c.vline(w - 2, 2, y0 + 2, 2)
    c.hline(y0 + 2, 0, w, 3)
    c.rect(0, y0 + 3, w, y0 + 5, 2); c.vline(0, y0 + 3, y0 + 6, 3); c.vline(w - 1, y0 + 3, y0 + 6, 3)
    c.hline(y0 + 5, 0, w, 3)
    c.rect(1, y0 + 6, 3, y0 + 8, 3); c.rect(w - 3, y0 + 6, w - 1, y0 + 8, 3)
    return c


def vase(c, x, y):
    """Small vase of flowers, about 10 x 13, top left at (x, y)."""
    for fx, fy in ((x + 5, y + 2), (x + 8, y + 7), (x + 2, y + 7)):
        c.line(fx, fy + 2, x + 5, y + 8, 2)
        c.ellipse(fx + 0.5, fy + 0.5, 2.1, 2.1, 0, outline=3); c.px(fx, fy, 2)
    c.poly([(x + 3, y + 9), (x + 8, y + 9), (x + 9, y + 14), (x + 2, y + 14)], 0, outline=3)
    c.px(x + 4, y + 11, 1); c.px(x + 4, y + 12, 1)
    return c


def shelf_books(seed=0):
    """One shelf of standing books, 2 tiles wide."""
    c = C(16, 8, 3)
    hs = ((5, 0), (6, 1), (4, 0), (6, 2), (5, 0), (3, 1)) if seed == 0 else ((4, 1), (6, 0), (6, 0), (5, 2), (6, 0), (4, 0))
    for i, (h, s) in enumerate(hs):
        c.rect(2 + i * 2, 7 - h, 4 + i * 2, 7, s)
        if s == 0:
            c.px(2 + i * 2, 8 - h, 2)
    c.hline(7, 0, 16, 1); c.vline(0, 0, 8, 3); c.vline(15, 0, 8, 3)
    return c


def shelf_items():
    """Shelf with a cup, a box and a small figure."""
    c = C(16, 8, 3)
    c.rect(2, 3, 5, 7, 0); c.px(5, 4, 1); c.px(5, 5, 1)
    c.rect(7, 2, 9, 7, 1); c.rect(6, 4, 10, 7, 1); c.px(7, 1, 0); c.px(8, 1, 0)
    c.rect(11, 4, 14, 7, 2); c.hline(4, 11, 14, 0)
    c.hline(7, 0, 16, 1); c.vline(0, 0, 8, 3); c.vline(15, 0, 8, 3)
    return c


def shelf_doors():
    """Cupboard doors at the foot of a shelf, 2 tiles wide."""
    c = C(16, 8, 2)
    c.frame(0, 0, 16, 8, 3)
    c.frame(2, 1, 8, 6, 3, fill=1); c.frame(8, 1, 14, 6, 3, fill=1)
    c.px(6, 3, 3); c.px(9, 3, 3); c.hline(2, 3, 6, 0); c.hline(2, 10, 13, 0)
    return c


def window(wt=2, bg=WALL):
    """Window on the wall, 2 tiles high, 1 or 2 wide."""
    w = wt * 8
    c = cv(bg, w, 16)
    c.frame(1, 1, w - 1, 13, 3, fill=1)
    if wt == 2:
        c.vline(7, 1, 13, 3); c.vline(8, 1, 13, 3)
        c.line(3, 6, 5, 3, 0); c.line(10, 10, 13, 6, 0); c.line(10, 6, 11, 4, 0)
    else:
        c.line(3, 6, 4, 3, 0); c.line(3, 10, 4, 9, 0)
    c.hline(7, 1, w - 1, 3)
    c.rect(0, 13, w, 15, 0); c.hline(12, 0, w, 3); c.hline(15, 0, w, 3)
    c.px(0, 13, 3); c.px(0, 14, 3); c.px(w - 1, 13, 3); c.px(w - 1, 14, 3)
    return c


def bed(bg=FLOOR):
    """Bed, 2 tiles wide: head with pillow, a blanket tile that repeats, foot."""
    c = cv(bg, 16, 24)
    c.frame(0, 0, 16, 24, 3, fill=1)
    c.rect(1, 1, 15, 3, 2); c.hline(3, 1, 15, 3)
    c.frame(3, 4, 13, 8, 3, fill=0); c.px(3, 4, 1); c.px(12, 4, 1); c.px(3, 7, 1); c.px(12, 7, 1)
    c.pat(1, 8, 15, 20, lambda x, y: 0 if (x % 4 == 2 and y % 4 == 1) else (2 if (x % 4 == 0 and y % 4 == 3) else None))
    c.hline(8, 1, 15, 2)
    c.hline(19, 0, 16, 3); c.rect(1, 20, 15, 23, 2); c.hline(20, 1, 15, 1)
    c.rect(1, 23, 3, 24, 3); c.rect(13, 23, 15, 24, 3)
    return c


def pc(desk=True, wall=WALL):
    """Desktop computer: monitor against the wall, keyboard on the desk below. 2 x 3 tiles."""
    c = cv(wall, 16, 24)
    if desk:
        c.rect(0, 12, 16, 24, WOOD); c.vline(0, 12, 24, 3); c.vline(15, 12, 24, 3); c.hline(23, 0, 16, 3)
    c.frame(1, 2, 15, 14, 3, fill=1)
    c.frame(3, 4, 13, 11, 3, fill=2)
    c.hline(6, 5, 9, 0); c.hline(8, 5, 11, 0); c.px(13, 12, 3)
    c.rect(5, 14, 11, 16, 2); c.frame(3, 15, 13, 17, 3)
    c.frame(2, 18, 14, 22, 3, fill=0)
    c.pat(3, 19, 13, 21, lambda x, y: 2 if (x + y) % 2 == 0 else 0)
    return c


def panel():
    """Plain framed board (spare tile)."""
    c = C(8, 8)
    c.frame(0, 0, 8, 8, 3); c.hline(6, 1, 7, 1); c.vline(6, 1, 7, 1)
    return c.a


def home_common(T, floor=FLOOR, wall=WALL):
    """Tiles that Red's house and the town houses number the same way."""
    T[0x00] = wall; T[0x01] = floor; T[0x10] = BLACK; T[0x11] = WHITE
    put(T, stool(floor), [[0x02, 0x03], [0x12, 0x13]])
    T[0x04], T[0x14] = mat()
    T[0x05] = panel(); T[0x15] = panel()
    put(T, tv(floor), [[0x06, 0x07], [0x16, 0x17]])
    put(T, pc(True, wall), [[0x40, 0x41], [0x20, 0x21], [0x42, 0x43]])
    put(T, shelf_books(0), [[0x30, 0x31]])
    return T


def build():
    T = home_common({})
    p = plant()
    put(T, p, [[0x44, 0x45], [0x08, 0x09], [0x46, 0x47], [0x18, 0x19]])
    put(T, stairs_down(), [[0x0A, 0x0B], [0x1A, 0x1B]])
    put(T, stairs_up(), [[0x0C, 0x0D], [0x1C, 0x1D]])
    put(T, console(), [[0x0E, 0x0F], [0x1E, 0x1F]])
    put(T, shelf_books(1), [[0x22, 0x23]])
    put(T, shelf_doors(), [[0x32, 0x33]])
    put(T, window(2), [[0x24, 0x25], [0x34, 0x35]])
    t = table(4, 4)
    vase(t, 14, 3)
    put(T, t, [[0x26, None, 0x28, 0x29], [0x36, 0x37, 0x38, 0x39], [0x2C, 0x2A, None, 0x2B], [0x3C, 0x3A, None, 0x3B]])
    put(T, table(3, 2), [[None, 0x27, None]])
    b = bed()
    put(T, b, [[0x2D, 0x2E], [0x3D, 0x3E], [0x3F, 0x2F]])
    return T


@drawer("tilesets/reds_house.png")
def reds_house(rel, a):
    return build_sheet(build(), a, WALK, "reds_house")
