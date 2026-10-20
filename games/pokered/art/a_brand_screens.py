"""Our own screen layouts with their tile maps: the slot machine and the Super Game Boy
frames (DAWN / DUSK).  Each screen is drawn whole, cut into tiles, de-duplicated and
numbered here, so the picture and its tile map always agree.

Engine facts kept (engine code only):
  slots  20x12 map at the top of the screen; BG tiles $00..$24 are ours ($25.. are the
         reel symbols); lamps sit at columns 3 and 16 on rows 2..11 and the engine writes
         $14 (top) / $15 (bottom) there when they light; coin counts are printed on row 1
         at columns 5..8 and 11..14; the reels are sprites behind BG colours 1..3 at
         columns 5-6, 9-10, 13-14 on rows 4..9, so those cells stay white.
  sgb    32x28 map of (tile, attribute) pairs, attribute = V H 0 P P P t t with border
         palettes 4..6; tiles 0..95 exist; the game window is columns 6..25, rows 5..22
         and must stay colour 0.
"""
import functools
import math

import numpy as np

from games.pokered.art import DRAWERS, sheet, tilemap
from games.pokered.art.font import G
from games.pokered.art.text import ptext, width
from games.pokered.art.tilekit import C


def front(pattern):
    def reg(fn):
        DRAWERS.insert(0, (pattern, fn))
        return fn
    return reg


def cells(a):
    h, w = a.shape
    return [[a[y:y + 8, x:x + 8].copy() for x in range(0, w, 8)] for y in range(0, h, 8)]


def bold(c, ch, x, y, s):
    for j, r in enumerate(G[ch].split("/")):
        for i, v in enumerate(r):
            if v == "1":
                c.px(x + i, y + j, s); c.px(x + i + 1, y + j, s)


# ---- slot machine ---------------------------------------------------------------------------

REEL_COLS = (5, 6, 9, 10, 13, 14)
FREE = [n for n in range(0x25) if n not in (0x14, 0x15, 0x17, 0x22)]


def lamp(c, x, y, lit):
    if lit:
        c.ellipse(x + 4, y + 8, 3.6, 5.6, 0, outline=3)
        for dx, dy in ((0, -7), (0, 7), (-3, -6), (3, -6), (-3, 6), (3, 6)):
            c.px(x + 4 + dx, y + 8 + dy, 2)
        c.rect(x + 3, y + 6, x + 5, y + 10, 1)
    else:
        c.ellipse(x + 4, y + 8, 3.6, 5.6, 2, outline=3)
        c.px(x + 2, y + 5, 1).px(x + 2, y + 6, 1)


def slot_canvas():
    c = C(160, 96)
    # marquee with bulbs, a diamond badge in the middle
    c.rect(0, 0, 160, 8, 3)
    for x in range(8, 152, 8):
        if x // 8 in (9, 10):
            continue
        c.ellipse(x + 4, 4, 2.2, 2.2, 1).px(x + 3, 3, 0)
    c.rect(0, 0, 2, 2, 0).px(2, 0, 0).px(0, 2, 0)
    c.rect(158, 0, 160, 2, 0).px(157, 0, 0).px(159, 2, 0)
    c.poly([(80, 0), (87, 4), (80, 8), (73, 4)], 2, outline=1)
    c.rect(78, 3, 82, 5, 0)
    # side rails and panels
    for x in (0, 152):
        c.rect(x, 8, x + 8, 96, 2).vline(x + 1, 8, 96, 3).vline(x + 6, 8, 96, 3).vline(x + 3, 8, 96, 1)
    for (x0, x1, y0, y1) in ((8, 32, 8, 16), (128, 152, 8, 16), (8, 16, 16, 96), (144, 152, 16, 96)):
        c.pat(x0, y0, x1, y1, lambda x, y: 2 if (x + y) % 4 == 0 else 1)
    # row 1: coin and star icons, count windows, sun|moon badge
    c.ellipse(36, 12, 3.4, 3.4, 1, outline=3).vline(36, 10, 14, 2)
    c.pat(120, 8, 128, 16, lambda x, y: None)
    c.poly([(124, 8), (125.5, 11), (128, 11.5), (126, 13.5), (126.5, 16), (124, 14.5), (121.5, 16), (122, 13.5),
            (120, 11.5), (122.5, 11)], 1, outline=3)
    for x0 in (40, 88):
        c.rect(x0, 8, x0 + 32, 16, 0).hline(8, x0, x0 + 32, 3).hline(15, x0, x0 + 32, 3)
    c.rect(72, 8, 88, 16, 3)
    m = c.emask(80, 12, 4.5, 4.5) & (c.grid()[1] < 80)
    c.a[m] = 1
    m = c.emask(80, 12, 4.5, 4.5) & ~c.emask(82.5, 10.5, 3.6, 3.6) & (c.grid()[1] >= 80)
    c.a[m] = 1
    # bet numerals (8x16 badges) beside the lamps
    for k, d in enumerate("32123"):
        y = 16 + k * 16
        for x in (16, 136):
            c.rect(x, y + 1, x + 8, y + 15, 3).px(x, y + 1, 1).px(x + 7, y + 1, 1).px(x, y + 14, 1).px(x + 7, y + 14, 1)
            for j, r in enumerate(G[d].split("/")):
                for i, v in enumerate(r):
                    if v == "1":
                        c.px(x + 1 + i, y + 4 + j, 0)
        for x in (24, 128):
            lamp(c, x, y, False)
    # hood over the reels: lattice row and a row with down arrows over each reel
    c.rect(32, 16, 128, 24, 2)
    c.pat(32, 16, 128, 24, lambda x, y: 1 if (abs((x % 8) - 3.5) + abs((y % 8) - 3.5)) < 2 else None)
    c.hline(16, 32, 128, 3)
    c.rect(32, 24, 128, 32, 1).hline(31, 32, 128, 3)
    for col in (5, 9, 13):
        x = col * 8
        c.poly([(x + 3, 25), (x + 13, 25), (x + 8, 30.5)], 3)
    # reel frames
    for col in (4, 8, 12):
        x = col * 8
        c.rect(x, 32, x + 8, 80, 2).vline(x + 7, 32, 80, 3).vline(x + 2, 32, 80, 1)
    for col in (7, 11, 15):
        x = col * 8
        c.rect(x, 32, x + 8, 80, 2).vline(x, 32, 80, 3).vline(x + 5, 32, 80, 1)
    for y in (48, 56):                                     # pay line pointers
        c.poly([(33, y + 1), (38, y + 4), (33, y + 7)], 0, outline=3)
        c.poly([(126, y + 1), (121, y + 4), (126, y + 7)], 0, outline=3)
    # ledge, coin slot and kick panel
    c.rect(32, 80, 128, 88, 1).hline(80, 32, 128, 3).hline(87, 32, 128, 2)
    c.rect(32, 88, 128, 96, 2)
    c.pat(32, 88, 128, 96, lambda x, y: 3 if (x % 4 == 1 and y % 4 == 2) else None)
    c.rect(74, 82, 86, 86, 3).hline(83, 76, 84, 0)
    return c.a


@functools.lru_cache(None)
def slot_layout():
    a = slot_canvas()
    nums, tiles, used = {}, {}, iter(FREE)
    m = np.zeros((12, 20), np.uint8)
    for r, row in enumerate(cells(a)):
        for k, t in enumerate(row):
            if (r in range(4, 10) and k in REEL_COLS) or not t.any():
                m[r, k] = 0x17
                continue
            key = t.tobytes()
            if key not in nums:
                n = next(used)
                nums[key] = n
                tiles[n] = t
            m[r, k] = nums[key]
    lit = C(8, 16)
    lamp(lit, 0, 0, True)
    tiles[0x14], tiles[0x15] = lit.a[:8], lit.a[8:]
    return m, tiles


def slots_sheet(a, version):
    m, tiles = slot_layout()
    n = (a["w"] // 8) * (a["h"] // 8)
    out = []
    for i in range(n):
        t = tiles.get(i)
        if t is not None and version == "blue":
            t = t.copy()
            one, two = t == 1, t == 2
            t[one], t[two] = 2, 1                           # DUSK: light and dark trade places
        out.append(t)
    return sheet(out, a["w"], a["h"])


@front("slots/red_slots_1.png")
def dawn_slots(rel, a):
    return slots_sheet(a, "red")


@front("slots/blue_slots_1.png")
def dusk_slots(rel, a):
    return slots_sheet(a, "blue")


@tilemap("gfx/slots/slots.tilemap")
def slots_map():
    return slot_layout()[0].tobytes()


# ---- Super Game Boy frames ----------------------------------------------------------------

WIN = (6, 5, 26, 23)                                       # columns 6..25, rows 5..22


def plaque_word(c, word, col0, row, fg, bg, edge):
    n = len(word) + 2
    x0, y = col0 * 8, row * 8
    c.rect(x0, y, x0 + n * 8, y + 8, bg)
    c.hline(y, x0 + 1, x0 + n * 8 - 1, edge).hline(y + 7, x0 + 1, x0 + n * 8 - 1, edge)
    c.vline(x0, y + 1, y + 7, edge).vline(x0 + n * 8 - 1, y + 1, y + 7, edge)
    c.px(x0 + 3, y + 3, edge).px(x0 + 3, y + 4, edge).px(x0 + n * 8 - 4, y + 3, edge).px(x0 + n * 8 - 4, y + 4, edge)
    for i, ch in enumerate(word):
        bold(c, ch, x0 + 8 + i * 8 + 1, y, fg)


def border_canvas(version):
    c = C(256, 224)
    pal = np.full((28, 32), 4, np.uint8)
    dawn = version == "red"
    top, mid, low = (3, 2, 1) if dawn else (2, 1, 3)
    sil = 3 if dawn else 2
    # sky: three bands with checker seams
    for r in range(28):
        y = r * 8
        if r <= 6:
            s = top
        elif r <= 15:
            s = mid
        else:
            s = low
        c.rect(0, y, 256, y + 8, s)
        if r in (7, 16):
            prev = top if r == 7 else mid
            c.pat(0, y, 256, y + 4, lambda x, yy, p=prev: p if (x + yy) % 2 == 0 else None)
    # rolling hills along the bottom (silhouettes against the bright horizon)
    yy, xx = c.grid()
    hill = yy > 196 - 7 * np.sin(xx / 23.0) - 5 * np.sin(xx / 9.0 + 1)
    far = yy > 186 - 9 * np.sin(xx / 31.0 + 2)
    if dawn:
        c.a[far & ~hill] = 2
    else:
        c.a[far & ~hill] = 1
    c.a[hill] = sil
    if dawn:
        # rising sun at the lower left, rays fanning over the left panel
        sun = c.emask(22, 190, 15, 15)
        c.a[sun & ~hill & ~far] = 0
        c.a[sun & far & ~hill & (yy < 192)] = 0
        for k in range(5):
            t = math.radians(200 + k * 28)
            for rr in range(18, 30, 2):
                c.px(int(22 + rr * math.cos(t)), int(190 + rr * math.sin(t)), 0)
        for bx, by in ((222, 60), (236, 52), (230, 74)):    # birds on the right
            c.put("#   #/ # # /  #  ", bx, by)
    else:
        moon = c.emask(22, 22, 11, 11) & ~c.emask(28, 17, 9, 9)
        c.a[moon] = 0
        for i in range(46):                                # stars: fixed scatter
            x = (i * 53 + 17) % 256
            y = (i * 37 + 11) % 120
            if WIN[0] * 8 - 4 <= x < WIN[2] * 8 + 4 and y >= WIN[1] * 8 - 12:
                continue
            c.px(x, y, 0)
            if i % 5 == 0:
                c.px(x - 1, y, 3).px(x + 1, y, 3).px(x, y - 1, 3).px(x, y + 1, 3)
        for fx, fy in ((214, 170), (236, 160), (24, 150), (12, 172)):
            c.px(fx, fy, 0).px(fx + 1, fy, 3)
    # the frame round the game window and the two plaques (palette 6 dawn / 5 dusk)
    fp = 6 if dawn else 5
    x0, y0, x1, y1 = WIN[0] * 8 - 8, WIN[1] * 8 - 8, WIN[2] * 8 + 8, WIN[3] * 8 + 8
    if dawn:
        ring = (3, 1, 2, 1, 3)                             # grey, yellow, blue, yellow, grey
        fill, fg, edge = 3, 1, 2
    else:
        ring = (2, 3, 1, 3, 2)                             # dark blue, sand, red, sand, dark blue
        fill, fg, edge = 3, 1, 2
    c.rect(x0, y0, x1, y1, ring[2])
    for i, s in enumerate(ring):
        c.frame(x0 + i + (1 if i > 1 else 0), y0 + i + (1 if i > 1 else 0),
                x1 - i - (1 if i > 1 else 0), y1 - i - (1 if i > 1 else 0), s)
    for (cx, cy) in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        c.rect(cx - 2, cy - 2, cx + 3, cy + 3, ring[0]).px(cx, cy, ring[1])
    pal[WIN[1] - 1:WIN[3] + 1, WIN[0] - 1:WIN[2] + 1] = fp
    plaque_word(c, "KITHBOUND", 10, 2, fg, fill, edge)
    pal[2, 10:21] = fp
    plaque_word(c, "DAWN" if dawn else "DUSK", 13, 25, fg, fill, edge)
    pal[25, 13:19] = fp
    c.rect(WIN[0] * 8, WIN[1] * 8, WIN[2] * 8, WIN[3] * 8, 0)
    return c.a, pal


def variants(t):
    return ((t, 0), (t[:, ::-1], 0x40), (t[::-1], 0x80), (t[::-1, ::-1], 0xC0))


@functools.lru_cache(None)
def border_layout(version):
    a, pal = border_canvas(version)
    seen, tiles = {}, []
    tiles.append(np.zeros((8, 8), np.uint8))
    seen[tiles[0].tobytes()] = (0, 0)
    out = bytearray()
    for r, row in enumerate(cells(a)):
        for k, t in enumerate(row):
            hit = None
            for v, flip in variants(t):
                if v.tobytes() in seen:
                    n, f0 = seen[v.tobytes()]
                    hit = (n, flip ^ f0)
                    break
            if hit is None:
                n = len(tiles)
                tiles.append(t)
                seen[t.tobytes()] = (n, 0)
                hit = (n, 0)
            n, flip = hit
            p = pal[r, k]
            if WIN[0] <= k < WIN[2] and WIN[1] <= r < WIN[3]:
                n, flip, p = 0, 0x40, 6                     # blank window: any flip/palette will do
            out += bytes([n & 0xFF, flip | (p << 2) | (n >> 8)])
    if len(tiles) > 96:
        print(f"  sgb {version}: {len(tiles)} tiles, over the 96 budget")
    return bytes(out), tiles


def border_sheet(a, version):
    data, tiles = border_layout(version)
    n = (a["w"] // 8) * (a["h"] // 8)
    return sheet([tiles[i] if i < len(tiles) else None for i in range(n)], a["w"], a["h"])


@front("sgb/red_border.png")
def dawn_frame(rel, a):
    return border_sheet(a, "red")


@front("sgb/blue_border.png")
def dusk_frame(rel, a):
    return border_sheet(a, "blue")


@tilemap("gfx/sgb/red_border.tilemap")
def dawn_frame_map():
    return border_layout("red")[0]


@tilemap("gfx/sgb/blue_border.tilemap")
def dusk_frame_map():
    return border_layout("blue")[0]
