"""Pokemon Center / Mart tileset, and the shared indoor subjects (floor, wall boards,
counter, PC, plant, mat, shelves ...) that the gym, gate, lobby and underground
modules import so that every public building looks like the same world."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex

WALK = (0x11, 0x1a, 0x1c, 0x3c, 0x5e)

L3 = {"S": "###/#  /###/  #/###", "A": " # /# #/###/# #/# #", "L": "#  /#  /#  /#  /###",
      "E": "###/#  /## /#  /###", "P": "###/# #/###/#  /#  ", "C": "###/#  /#  /#  /###",
      "G": "###/#  /# #/# #/###", "Y": "# #/# #/ # / # / # ", "M": "# #/###/###/# #/# #",
      "F": "###/#  /## /#  /#  ", "B": "## /# #/## /# #/###", "1": " # /## / # / # /###",
      "2": "###/  #/###/#  /###", "X": "# #/# #/ # /# #/# #", "I": "###/ # / # / # /###",
      "T": "###/ # / # / # / # ", "N": "# #/###/###/###/# #", "O": "###/# #/# #/# #/###"}


def small(c, s, x, y, ch="#"):
    """3x5 capitals of our own."""
    for k in s:
        c.put(L3[k].replace("#", ch), x, y)
        x += 4
    return c


def on(bg, w, h, ox=0, oy=0):
    """Canvas w x h tiled with a background picture."""
    c = C(w, h)
    y, x = c.grid()
    c.a[:] = np.asarray(bg)[(y + oy) % bg.shape[0], (x + ox) % bg.shape[1]]
    return c


def shade(a):
    """The same surface in shadow."""
    return np.minimum(np.asarray(a) + 1, 2).astype(np.uint8) if np.asarray(a).max() < 3 else np.minimum(np.asarray(a) + 1, 3).astype(np.uint8)


def floor16():
    """Quiet square floor slab, 16x16 (TL TR / BL BR)."""
    c = C(16, 16)
    c.hline(15, 0, 16, 1); c.vline(15, 0, 16, 1); c.px(7, 7, 1)
    return c.a


FLOOR = floor16()
WALL = tex(lambda x, y: 2 if y % 4 == 3 else 1)                    # wall boards
BLACK = np.full((8, 8), 3, np.uint8)


def ball(c, cx, cy, r=3):
    """Small capsule ball: dark top, white bottom."""
    m = c.emask(cx, cy, r, r)
    y, x = c.grid()
    c.a[m] = 0
    c.a[m & (y < cy - 0.5)] = 2
    c.fill(m, None) if False else None
    from games.pokered import drawn
    d = drawn.depth_map(m, edge_inside=False)
    c.a[m & (d == 1)] = 3
    c.hline(int(cy - 0.5), int(cx - r + 1), int(cx + r), 3)
    return c


# ---- counter -------------------------------------------------------------
def counter_top(body=1):
    c = C(8, 8, body)
    c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 0 if body == 1 else 1); c.hline(7, 0, 8, 3)
    return c.a


def counter_front():
    """16x8: one front panel (left half, right half)."""
    c = C(16, 8, 2)
    c.vline(0, 0, 6, 3); c.hline(1, 2, 14, 1); c.rect(0, 6, 16, 8, 3)
    return c


def counter_block():
    """16x16 dark corner / end block of a counter."""
    c = C(16, 16, 2)
    c.frame(0, 0, 16, 16, 3); c.hline(1, 1, 15, 1); c.rect(0, 14, 16, 16, 3)
    c.frame(4, 5, 12, 11, 3)
    return c


def counter_v():
    """16x8: counter (or partition) running up and down."""
    c = C(16, 8, 1)
    c.vline(0, 0, 8, 3); c.vline(1, 0, 8, 0); c.vline(14, 0, 8, 2); c.vline(15, 0, 8, 3)
    return c


def panel():
    """16x8 light flap / sign panel."""
    c = C(16, 8, 1)
    c.frame(0, 0, 16, 8, 3); c.hline(1, 1, 15, 0); c.hline(6, 1, 15, 2)
    return c


# ---- furniture -----------------------------------------------------------
def pc(bg=FLOOR):
    """16x24: monitor over keyboard desk."""
    c = on(bg, 16, 24)
    c.frame(1, 1, 15, 13, 3, fill=1)
    c.frame(3, 3, 13, 10, 3, fill=2)
    c.line(5, 7, 7, 5, 0); c.px(9, 5, 0)
    c.px(12, 11, 3); c.hline(11, 3, 7, 0)
    c.rect(5, 13, 11, 15, 3)
    c.frame(0, 15, 16, 23, 3, fill=1)
    c.hline(16, 1, 15, 0)
    c.pat(2, 18, 14, 21, lambda x, y: 3 if (x % 2 == 0 and y % 2 == 0) else None)
    c.hline(23, 1, 15, 2)
    return c


def plant(bg=FLOOR):
    """16x32 potted plant."""
    c = on(bg, 16, 32)
    c.rect(7, 16, 9, 23, 3)
    c.poly([(4, 23), (12, 23), (11, 31), (5, 31)], 1, outline=3)
    c.frame(3, 21, 13, 24, 3, fill=0)
    c.hline(27, 6, 10, 2)
    m = c.emask(8, 6, 4.2, 5.6) | c.emask(4.5, 12, 4.2, 5.2) | c.emask(11.5, 12, 4.2, 5.2)
    c.blob(m, 1.9, 1.2)
    for x, y in ((7, 4), (4, 10), (11, 10), (8, 12)):
        c.line(x, y, x + 1, y + 4, 0)
    return c


def mat():
    """8x16 strip of the exit mat (repeats sideways)."""
    c = C(8, 16, 2)
    c.rect(0, 0, 8, 2, 0); c.hline(2, 0, 8, 3); c.hline(4, 0, 8, 1)
    c.hline(11, 0, 8, 1); c.hline(13, 0, 8, 3); c.rect(0, 14, 8, 16, 0)
    c.pat(0, 6, 8, 10, lambda x, y: 3 if (x + y) % 4 == 0 else None)
    return c


def shelf():
    """24x32 shop shelf: left, repeating middle, right columns; four rows of goods."""
    c = C(24, 32, 0)
    for r in range(4):
        y = r * 8
        c.hline(y + 6, 0, 24, 2); c.hline(y + 7, 0, 24, 3)
        for k in range(3):
            x = k * 8
            if r == 0:                                   # boxes
                c.frame(x + 1, y + 2, x + 7, y + 6, 3, fill=1); c.hline(y + 3, x + 2, x + 6, 0)
            elif r == 1:                                 # bottles
                for b in (1, 5):
                    c.rect(x + b, y + 2, x + b + 2, y + 6, 3); c.rect(x + b, y + 1, x + b + 2, y + 2, 2)
                    c.px(x + b, y + 3, 1)
            elif r == 2:                                 # cans
                c.ellipse(x + 4, y + 3.5, 3, 2.6, 2, outline=3); c.hline(y + 3, x + 3, x + 5, 0)
            else:                                        # bags
                c.poly([(x + 2, y + 1), (x + 6, y + 1), (x + 7, y + 6), (x + 1, y + 6)], 1, outline=3)
                c.px(x + 4, y + 3, 3)
    c.hline(0, 0, 24, 3); c.vline(0, 0, 32, 3); c.vline(23, 0, 32, 3)
    return c


def cabinet():
    """16x24 glass-door cooler."""
    c = C(16, 24, 1)
    c.frame(0, 0, 16, 24, 3)
    c.rect(7, 1, 9, 21, 3)
    for x0 in (1, 9):
        c.rect(x0, 1, x0 + 6, 20, 0)
        c.hline(10, x0, x0 + 6, 3)
        for bx in (x0 + 1, x0 + 4):
            for by in (6, 16):
                c.rect(bx, by, bx + 2, by + 4, 2); c.hline(by - 1, bx, bx + 2, 3)
        c.line(x0, 3, x0 + 2, 1, 1)
    c.rect(6, 11, 7, 14, 2); c.rect(9, 11, 10, 14, 2)
    c.rect(1, 20, 15, 23, 2); c.hline(20, 1, 15, 3)
    return c


def glass_box():
    """16x16 dark box behind glass: top half is shared by the healing machine and the sale case."""
    c = C(16, 16, 3)
    c.frame(1, 1, 15, 16, 1)
    c.line(3, 6, 6, 3, 1); c.px(4, 7, 2)
    return c


def bench_person(bg=FLOOR):
    """16x32 wall bench with somebody resting on it."""
    c = on(bg, 16, 32)
    c.frame(0, 0, 5, 30, 3, fill=2)
    c.frame(4, 0, 14, 30, 3, fill=1)
    c.vline(5, 1, 29, 0)
    c.rect(1, 30, 3, 32, 3); c.rect(11, 30, 13, 32, 3)
    c.hline(22, 5, 13, 2)
    c.frame(5, 10, 15, 18, 3, fill=2)                      # body
    c.rect(11, 14, 16, 18, 3); c.rect(12, 15, 15, 17, 0)    # knees
    c.ellipse(9, 6, 5, 5, 0, outline=3)
    y, x = c.grid()
    c.a[c.emask(9, 6, 5, 5) & ((y < 5) | (x < 7))] = 3      # hair
    c.px(10, 7, 3); c.px(12, 7, 3)
    return c


def build():
    T = {}
    T[0x00] = BLACK
    put(T, C(16, 16).paste(FLOOR, 0, 0), [[0x01, 0x0B], [0x11, 0x1B]])
    sh = shade(FLOOR)
    T[0x36] = sh[:8, :8]; T[0x1A] = sh[8:, :8]; T[0x37] = sh[:8, 8:]
    T[0x39] = tex(lambda x, y: sh[y, x] if x < y else FLOOR[y, x])
    T[0x3C] = tex(lambda x, y: sh[8 + y, x] if x < 7 else FLOOR[8 + y, x])
    T[0x3D] = np.full((8, 8), 2, np.uint8)
    T[0x28] = WALL
    c = C(8, 8).paste(WALL, 0, 0); c.vline(6, 0, 8, 2); c.vline(7, 0, 8, 3); c.hline(0, 0, 8, 3); T[0x59] = c.a
    # counter
    T[0x08] = counter_top(); T[0x38] = counter_top(2)
    c = C(8, 8).paste(T[0x08], 0, 0); ball(c, 4, 4, 2.6); T[0x0A] = c.a
    put(T, counter_front(), [[0x18, 0x19]])
    put(T, counter_block(), [[0x04, 0x05], [0x14, 0x15]])
    put(T, counter_v(), [[0x10, 0x29]])
    put(T, panel(), [[0x5A, 0x5B]])
    # wall poster
    c = on(WALL, 16, 16); c.frame(1, 1, 15, 15, 3, fill=0); ball(c, 8, 5, 3); small(c, "PC", 5, 9)
    put(T, c, [[0x02, 0x03], [0x12, 0x13]])
    # healing machine: monitor, box, ball trays, key panel
    c = on(WALL, 16, 16)
    c.rect(5, 12, 11, 16, 3)
    c.frame(1, 1, 15, 13, 3, fill=0); c.frame(3, 3, 13, 11, 3, fill=2)
    c.rect(7, 4, 9, 10, 0); c.rect(5, 6, 11, 8, 0)
    put(T, c, [[0x3A, 0x3B], [0x4A, 0x4B]])
    c = glass_box(); c.hline(15, 0, 16, 3); c.hline(11, 4, 12, 2); c.px(4, 13, 0); c.px(6, 13, 1); c.px(8, 13, 0)
    put(T, c, [[0x4C, 0x4D], [0x06, 0x16]])
    c = glass_box(); c.hline(15, 0, 16, 3); c.hline(14, 1, 15, 2)
    c.frame(3, 9, 7, 14, 1, fill=0); c.ellipse(11, 11.5, 2.5, 2.5, 1); c.px(11, 11, 0)
    put(T, c, [[None, None], [0x17, 0x1D]])
    c = C(8, 8, 1); c.vline(0, 0, 8, 3); ball(c, 4.5, 4, 3); T[0x48] = c.a
    T[0x49] = T[0x48][:, ::-1].copy()
    c = C(8, 16, 1); c.frame(1, 2, 7, 15, 3, fill=0); c.rect(2, 4, 6, 7, 2)
    for y in (9, 11, 13):
        c.px(3, y, 3); c.px(5, y, 3)
    c.hline(15, 0, 8, 2)
    put(T, c, [[0x07], [0x0D]])
    # PC, bench, mat, plants
    put(T, pc(), [[0x42, 0x46], [0x52, 0x56], [0x09, 0x58]])
    put(T, bench_person(), [[0x24, 0x25], [0x34, 0x35], [0x26, 0x27], [0x2A, 0x2B]])
    put(T, mat(), [[0x0C], [0x1C]])
    put(T, plant(), [[0x20, 0x21], [0x30, 0x31], [0x22, 0x23], [0x32, 0x33]])
    # mart: shelves, cooler, sale cases, till
    put(T, shelf(), [[0x40, 0x41, 0x43], [0x50, 0x51, 0x53], [0x44, 0x45, 0x47], [0x54, 0x55, 0x57]])
    put(T, cabinet(), [[0x2C, 0x2D], [0x2E, 0x2F], [0x3E, 0x3F]])
    c = C(16, 8, 1); c.hline(0, 0, 16, 3); c.hline(7, 0, 16, 3); small(c, "SALE", 1, 1)
    put(T, c, [[0x4E, 0x4F]])
    c = on(counter_v().a, 16, 16)
    c.frame(3, 7, 14, 15, 3, fill=0); c.frame(5, 2, 12, 8, 3, fill=2); c.hline(4, 7, 10, 0)
    c.pat(5, 9, 12, 13, lambda x, y: 3 if (x % 2 == 1 and y % 2 == 1) else None)
    c.hline(15, 2, 15, 2)
    put(T, c, [[0x0E, 0x0F], [0x1E, 0x1F]])
    # doorway in the back wall
    c = C(16, 16, 3)
    c.hline(4, 4, 12, 2); c.hline(6, 3, 13, 2)
    c.rect(1, 8, 15, 16, 0); c.rect(1, 8, 15, 10, 2); c.rect(1, 10, 15, 12, 1)
    put(T, c, [[0x5C, 0x5D], [0x5E, 0x5F]])
    return T


@drawer("tilesets/pokecenter.png")
def pokecenter(rel, a):
    return build_sheet(build(), a, WALK, "pokecenter")
