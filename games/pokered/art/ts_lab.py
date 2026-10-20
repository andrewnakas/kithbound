"""Lab tileset (Cinnabar Lab, Warden's house ...). Also the home of the indoor
subjects the other technical tilesets import: plant, machine, table, chair, PC,
bookshelf, door, stairs."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex

WALK = (0x0C, 0x26, 0x16, 0x1E, 0x34, 0x37)

BLACK = np.full((8, 8), 3, np.uint8)
WHITE = np.zeros((8, 8), np.uint8)
LIGHT = np.full((8, 8), 1, np.uint8)
DARK = np.full((8, 8), 2, np.uint8)


def on(bg, w, h):
    out = C(w, h)
    out.a[:] = np.tile(bg, (h // 8, w // 8))
    return out


def edged(base, l=None, r=None, t=None, b=None):
    """Copy of a tile with edge lines: each of l/r/t/b is a list of shades from the edge inwards."""
    c = C(8, 8); c.a[:] = base
    for i, s in enumerate(t or ()):
        c.hline(i, 0, 8, s)
    for i, s in enumerate(b or ()):
        c.hline(7 - i, 0, 8, s)
    for i, s in enumerate(l or ()):
        c.vline(i, 0, 8, s)
    for i, s in enumerate(r or ()):
        c.vline(7 - i, 0, 8, s)
    return c.a


# ---------------------------------------------------------------- shared subjects
def plant(bg_top=WHITE, bg_bot=WHITE):
    """Potted plant, 16 wide: foliage 16 high over pot 16 high."""
    c = C(16, 32)
    c.a[:16] = np.tile(bg_top, (2, 2)); c.a[16:] = np.tile(bg_bot, (2, 2))
    c.rect(7, 14, 9, 21, 3)
    y, x = c.grid()
    crown = c.emask(8, 8, 7.8, 7.6) & (y < 16)
    c.blob(crown, 2.0, 1.2)
    for lx, ly in ((4, 4), (8, 2), (11, 5), (6, 8), (10, 10), (3, 9), (12, 11), (7, 12)):   # leaf blades
        c.line(lx, ly, lx + 2, ly + 2, 1); c.px(lx, ly, 0)
    for lx, ly in ((6, 5), (10, 7), (5, 11), (9, 13)):
        c.px(lx, ly, 3); c.px(lx + 1, ly + 1, 3)
    c.poly([(3, 23), (13, 23), (11.5, 31), (4.5, 31)], 1, outline=3)
    c.rect(4, 26, 6, 29, 0); c.vline(10, 25, 30, 2)
    c.frame(2, 20, 14, 24, 3, fill=2); c.hline(21, 3, 13, 1)
    c.hline(31, 4, 12, 3)
    return c


def machine(n=2):
    """Instrument cabinet: a row of gauges (8 high) over a vented base (8 high); n tiles wide,
    every tile framed on its own so the tiles can be mixed."""
    c = C(8 * n, 16, 2)
    for i in range(n):
        x = 8 * i
        c.frame(x, 0, x + 8, 8, 3, fill=2)
        c.ellipse(x + 4, 4, 2.6, 2.6, 0, outline=3)
        c.px(x + 4, 4, 3); c.px(x + 5 - (i % 2) * 2, 3, 3)
        c.rect(x, 8, x + 8, 16, 2)
        c.hline(10, x + 1, x + 7, 3); c.hline(12, x + 1, x + 7, 3)
        c.hline(15, x, x + 8, 3); c.rect(x + 3, 14, x + 5, 15, 0)
        c.hline(8, x, x + 8, 1)
    c.vline(0, 0, 16, 3); c.vline(8 * n - 1, 0, 16, 3)
    return c


def chair(bg=WHITE):
    c = on(bg, 16, 16)
    c.frame(3, 0, 13, 9, 3, fill=1); c.frame(5, 2, 11, 6, 2, fill=0)
    c.frame(2, 8, 14, 13, 3, fill=2); c.hline(9, 3, 13, 1)
    c.rect(3, 13, 5, 16, 3); c.rect(11, 13, 13, 16, 3)
    return c


def pc(w=16):
    """Monitor and keyboard on a transparent (white) ground; 14 x 15 pixels."""
    c = C(16, 16)
    c.frame(1, 0, 15, 10, 3, fill=1)
    c.frame(3, 2, 13, 8, 3, fill=2); c.line(4, 6, 7, 3, 0); c.px(11, 6, 1)
    c.rect(6, 10, 10, 11, 3)
    c.frame(1, 11, 15, 15, 3, fill=0)
    for kx in range(3, 13, 2):
        c.px(kx, 12, 2)
    c.hline(13, 4, 12, 2)
    return c


def keypad(bg=WHITE):
    """16x8 key panel (wall panel, or keyboard lying on a table)."""
    c = on(bg, 16, 8)
    c.frame(1, 1, 15, 7, 3, fill=0)
    for kx in (3, 6, 9, 12):
        c.px(kx, 3, 3)
    c.hline(5, 4, 12, 2)
    return c


def shelf_row():
    """Bookshelf, 16x8 repeating downwards: books on a board."""
    c = C(16, 8, 3)
    hs = [(1, 5, 1), (3, 4, 0), (4, 5, 2), (6, 3, 1), (8, 5, 0), (9, 4, 2), (11, 5, 1), (13, 4, 0)]
    for x, h, s in hs:
        c.rect(x, 6 - h, x + (2 if s == 1 else 1), 6, s)
    c.hline(6, 1, 15, 1); c.hline(7, 0, 16, 3)
    c.vline(0, 0, 8, 3); c.vline(15, 0, 8, 3)
    return c


def door():
    """Inner door set in a wall, 16x16."""
    c = C(16, 16, 3)
    c.frame(1, 1, 15, 17, 3, fill=1)
    c.rect(2, 2, 14, 3, 0)
    c.frame(4, 4, 8, 8, 2, fill=0); c.frame(9, 4, 13, 8, 2, fill=0)
    c.frame(4, 10, 8, 14, 2); c.frame(9, 10, 13, 14, 2)
    c.rect(12, 8, 14, 10, 3)
    c.hline(15, 0, 16, 3)
    return c


def stairs_up(bg=WHITE):
    """Stairs rising to the right, 16x16, white treads."""
    c = on(bg, 16, 16)
    for i in range(4):
        x0, y0 = 1 + i * 4, 11 - i * 3
        c.rect(x0, y0, 16, 16, 2)
        c.rect(x0, y0, x0 + 4, y0 + 2, 0)
        c.hline(y0 - 1, x0, x0 + 4, 3); c.vline(x0 - 1, y0 - 1, min(y0 + 3, 16), 3)
    c.vline(15, 1, 16, 3); c.hline(15, 0, 16, 3); c.vline(0, 10, 16, 3)
    return c


def stairs_down():
    """Stairwell going down into the dark, 16x16: treads darken with depth."""
    c = C(16, 16, 3)
    for i, sh in enumerate((0, 1, 2, 2)):
        y0 = 1 + i * 4
        c.rect(1 + i, y0, 15 - i, y0 + 3, sh)
        c.hline(y0 + 2, 1 + i, 15 - i, 2 if sh < 2 else 3)
    c.vline(0, 0, 16, 3); c.vline(15, 0, 16, 3); c.hline(0, 0, 16, 3)
    return c


def table_tiles(T, tl, t, tr, l, m, r, fl=None, f=None, fr=None, bg=WHITE):
    """Table seen from above/front: light top, black outline, dark front with legs."""
    if m is not None:
        T[m] = LIGHT.copy()
    if t is not None:
        T[t] = edged(LIGHT, t=[3, 0])
    if l is not None:
        T[l] = edged(LIGHT, l=[3, 0])
    if r is not None:
        T[r] = edged(LIGHT, r=[3, 2])
    if tl is not None:
        T[tl] = edged(edged(LIGHT, t=[3, 0]), l=[3, 0])
    if tr is not None:
        T[tr] = edged(edged(LIGHT, t=[3, 0]), r=[3, 2])
    c = on(bg, 24, 8)
    c.rect(0, 0, 24, 4, 2); c.hline(0, 0, 24, 3); c.hline(4, 0, 24, 3)
    c.vline(0, 0, 8, 3); c.vline(23, 0, 8, 3)
    c.frame(0, 4, 4, 8, 3, fill=2); c.frame(20, 4, 24, 8, 3, fill=2)
    c.hline(2, 9, 15, 3)
    put(T, c, [[fl, f, fr]])


def pokeball(bg=LIGHT):
    c = C(8, 8); c.a[:] = bg
    c.ellipse(4, 4, 3.4, 3.4, 0, outline=3)
    c.rect(2, 2, 6, 4, 2); c.hline(4, 1, 7, 3); c.px(4, 4, 0); c.px(3, 4, 0)
    return c.a


# ---------------------------------------------------------------- the lab
FLOOR = tex(lambda x, y: 0 if (x == 0 or y == 0) else 1)        # the dark square of the chequered floor
WALL = tex(lambda x, y: 3 if x == 7 else (1 if x == 0 else 2))  # upright boards
MAT = tex(lambda x, y: 3 if (x + y) % 4 == 0 and (x - y) % 4 == 0 else 2)


def desk():
    """PC desk, 32x16 top, then front + chair, 32x16."""
    top = C(32, 16, 1)
    top.frame(0, 0, 32, 16, 3); top.hline(1, 1, 31, 0); top.vline(30, 1, 15, 2)
    top.paste(pc(), 2, 1, mask=None)
    top.rect(1, 2, 2, 15, 1); top.rect(2, 1, 3, 2, 0)
    # flask and notes
    top.poly([(22, 3), (25, 3), (25, 7), (28, 13), (19, 13), (22, 7)], 0, outline=3)
    top.rect(21, 10, 27, 12, 2); top.hline(2, 21, 26, 3)
    low = C(32, 16)
    low.rect(0, 0, 32, 5, 2); low.hline(0, 0, 32, 3); low.hline(5, 0, 32, 3)
    low.vline(0, 0, 8, 3); low.vline(31, 0, 8, 3)
    low.frame(0, 5, 4, 8, 3, fill=2); low.frame(28, 5, 32, 8, 3, fill=2)
    low.hline(2, 20, 28, 3)
    ch = chair()
    low.paste(ch, 0, 2, mask=(ch.a != 0) | (np.indices((16, 16))[0] < 13))
    low.rect(0, 2, 2, 5, 2); low.rect(14, 2, 16, 5, 2); low.vline(0, 0, 8, 3)
    return top, low


def tank():
    """Tall glass tank, one tile wide, four tiles high (45, 55, 4A, 5A)."""
    c = C(8, 32, 0)
    c.vline(0, 0, 32, 3); c.vline(7, 0, 32, 3)
    c.rect(1, 0, 7, 3, 2); c.hline(0, 0, 8, 3); c.hline(3, 0, 8, 3)
    c.rect(1, 12, 7, 28, 1); c.hline(12, 1, 7, 2)
    c.vline(2, 5, 27, 0); c.px(5, 16, 0); c.px(4, 21, 0); c.px(5, 25, 0)
    c.rect(1, 28, 7, 32, 2); c.hline(28, 0, 8, 3); c.hline(31, 0, 8, 3)
    return c


def vents():
    """Slatted column next to the tanks (46, 56, 4B, 5B)."""
    c = C(8, 32, 2)
    c.vline(0, 0, 32, 3); c.vline(7, 0, 32, 3); c.hline(0, 0, 8, 3); c.hline(31, 0, 8, 3)
    for y in range(3, 30, 3):
        c.hline(y, 2, 6, 3)
    c.rect(2, 13, 6, 18, 0); c.frame(1, 12, 7, 19, 3); c.px(3, 15, 3); c.px(4, 16, 2)
    return c


def build():
    T = {}
    T[0x36] = BLACK
    T[0x01] = FLOOR
    T[0x22] = WALL
    T[0x23] = edged(WALL, l=[3, 3])
    T[0x0C] = tex(lambda x, y: 2 if (x % 4, y % 4) in ((0, 0), (2, 2)) else 1)
    T[0x0D] = T[0x0C]
    T[0x27] = edged(MAT, t=[0, 3]); T[0x37] = edged(MAT, b=[0, 3])
    # desk with PC and chair
    top, low = desk()
    put(T, top, [[0x02, 0x03, 0x04, 0x05], [0x12, 0x13, 0x14, 0x15]])
    put(T, low, [[0x06, 0x07, 0x08, 0x09], [0x16, 0x17, None, None]])
    put(T, chair(), [[0x0E, 0x0F], [0x1E, 0x1F]])
    put(T, machine(2), [[0x0A, 0x0B], [0x1A, 0x1B]])
    # tables
    table_tiles(T, 0x40, 0x41, 0x42, 0x50, 0x51, 0x52, 0x53, 0x3A, 0x54)
    T[0x1C] = T[0x50]; T[0x1D] = T[0x52]
    back = edged(LIGHT, t=[3, 2, 2, 3, 0])
    T[0x58] = back; T[0x57] = edged(back, l=[3]); T[0x59] = edged(back, r=[3])
    glass = tex(lambda x, y: 0 if (x - y) % 8 in (0, 1) else 1)       # glass-topped lower shelf
    T[0x4E] = glass; T[0x24] = edged(glass, l=[3, 2]); T[0x25] = edged(glass, r=[3, 2])
    T[0x2A] = edged(WALL, l=[3, 3], t=[3]); T[0x2B] = edged(WALL, r=[3, 3], t=[3])
    T[0x47] = pokeball()
    c = C(8, 8, 1); c.frame(1, 1, 7, 7, 3, fill=0); c.hline(3, 2, 6, 2); c.hline(5, 2, 5, 2); T[0x48] = c.a
    c = C(8, 8, 1); c.poly([(3, 1), (5, 1), (5, 3), (7.5, 7), (0.5, 7), (3, 3)], 0, outline=3); c.rect(2, 5, 6, 6, 2); T[0x49] = c.a
    put(T, keypad(WALL), [[0x18, 0x19]])
    # wall things
    c = on(WALL, 16, 16)
    c.frame(1, 1, 15, 14, 3, fill=0); c.frame(2, 2, 14, 13, 2)
    c.line(4, 10, 6, 6, 3); c.line(6, 6, 9, 9, 3); c.line(9, 9, 11, 4, 3); c.hline(11, 4, 12, 2)
    put(T, c, [[0x10, 0x11], [0x20, 0x21]])
    c = on(WALL, 16, 8)
    c.rect(0, 2, 16, 6, 1); c.hline(2, 0, 16, 3); c.hline(6, 0, 16, 3); c.hline(3, 0, 16, 0)
    c.frame(3, 1, 8, 8, 3, fill=2); c.px(5, 4, 0); c.rect(4, 0, 7, 1, 3); c.vline(13, 2, 7, 3)
    put(T, c, [[0x30, 0x31]])
    put(T, door(), [[0x4C, 0x4D], [0x34, 0x35]])
    put(T, shelf_row(), [[0x28, 0x29]])
    p = plant()
    put(T, p, [[0x2C, 0x2D], [0x3C, 0x3D], [0x2E, 0x2F], [0x3E, 0x3F]])
    # specimen boulder
    c = C(16, 16)
    c.blob(c.emask(8, 8, 7.6, 7.2), 2.1, 1.1)
    c.line(5, 4, 8, 6, 3); c.line(8, 6, 7, 9, 3); c.line(10, 10, 12, 8, 3); c.px(4, 5, 0); c.px(5, 4, 0)
    c.hline(15, 3, 13, 3)
    put(T, c, [[0x32, 0x33], [0x43, 0x44]])
    # specimen tube
    c = C(8, 16)
    c.frame(1, 1, 7, 15, 3, fill=0); c.rect(2, 6, 6, 14, 1); c.hline(6, 2, 6, 2)
    c.rect(1, 0, 7, 2, 3); c.rect(1, 14, 7, 16, 3); c.vline(3, 3, 13, 0); c.px(4, 9, 2); c.px(5, 11, 2)
    put(T, c, [[0x38], [0x39]])
    # big apparatus
    put(T, tank(), [[0x45], [0x55], [0x4A], [0x5A]])
    put(T, vents(), [[0x46], [0x56], [0x4B], [0x5B]])
    T[0x3B] = tex(lambda x, y: 3 if x in (0, 7) or y == 7 else (0 if x == 2 else (2 if y in (2, 3) else 1)))
    return T


@drawer("tilesets/lab.png")
def lab(rel, a):
    return build_sheet(build(), a, WALK, "lab")
