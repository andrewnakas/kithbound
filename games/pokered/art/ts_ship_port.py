"""Ship port tileset (Vermilion Dock): quay, water, float line, gangway, crates,
a truck and the moored liner (one 16x6-tile picture seen from above, bow to the left)."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex
from games.pokered.art.ts_overworld import PAVE, WATER, on

WALK = (0x0a, 0x1a, 0x32, 0x3b)

SHIP = [   # KITHBOUND liner, stern left / bow right; 0x14 = open water
    [0x00, 0x02, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x04, 0x14, 0x14, 0x14],
    [0x05, 0x06, 0x07, 0x09, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x15, 0x16, 0x17],
    [0x18, 0x19, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29],
    [0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x33, 0x34, 0x35, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3D],
    [0x3E, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x41, 0x42, 0x43],
    [0x44, 0x45, 0x4D, 0x4D, 0x4D, 0x4D, 0x4D, 0x4D, 0x4D, 0x4D, 0x4D, 0x4D, 0x4E, 0x4F, 0x51, 0x52],
]
SPARE_DECK = (0x5A, 0x5B, 0x5D)   # ship ids the liner no longer needs: drawn as plain deck
RAMP_CLEAT = (0x53, 0x55)        # ship ids reused for the gangway section with a cross cleat


def ship():
    """KITHBOUND liner: stern (rounded) to the left, bow (pointed) to the right, foam at both ends."""
    c = on(WATER, (128, 48))
    y, x = c.grid()
    hull = c.pmask([(10, 4), (100, 4), (126, 25), (100, 46), (10, 46), (3, 40), (3, 10)])
    c.fill(hull, 0, outline=3)
    inner = hull & (c.a != 3)
    deck = inner & (y < 30)
    c.a[deck & (x % 8 == 6)] = 1                           # deck planks run lengthwise
    c.a[inner & (y == 5)] = 2                              # rail shadow
    c.a[hull & (y == 30)] = 3
    side = inner & (y > 30)
    c.a[side & (y >= 33) & (y <= 34) & (x % 8 == 4) & (x > 10) & (x < 104)] = 3   # portholes
    c.a[side & (y == 37)] = 1
    c.a[side & (y >= 39) & (y <= 41)] = 2
    c.a[side & (y >= 42)] = 3
    # foam where the hull meets the water (stern and bow wake)
    for (fx, fy) in ((1, 12), (0, 26), (1, 38), (122, 12), (124, 38), (120, 44), (118, 8), (110, 43)):
        c.hline(fy, fx, fx + 4, 0); c.hline(fy + 2, fx + 2, fx + 6, 0)
    # stern: two lifeboats side by side
    for bx in (13, 27):
        m = c.emask(bx, 17, 5, 9)
        c.blob(m, 1.0, 1.0); c.vline(bx, 10, 25, 2)
    # long cabin with a window row
    c.frame(38, 10, 94, 28, 3, fill=1)
    c.hline(11, 39, 93, 0)
    for wx in range(41, 92, 6):
        c.rect(wx, 22, wx + 4, 25, 2); c.px(wx, 22, 3)
    # one wide funnel on the cabin
    c.ellipse(58, 16, 9, 5.5, 2, outline=3); c.ellipse(58, 15, 6, 3, 3)
    c.hline(19, 52, 64, 1)
    # bridge near the bow with its wheel-house windows
    c.frame(74, 12, 92, 20, 3, fill=0)
    for wx in (76, 81, 86):
        c.rect(wx, 14, wx + 4, 18, 2)
    # bow: anchor winch and a round hatch
    c.ellipse(104, 16, 3.5, 3.5, 1, outline=3); c.px(104, 16, 3)
    c.frame(100, 22, 107, 28, 3, fill=2)
    return c

def gangway():
    """16x8 boarding ramp: slatted planks with a handrail on its right side only."""
    c = C(16, 8, 1)
    c.hline(2, 0, 13, 2); c.hline(6, 0, 13, 2); c.px(4, 4, 2); c.px(9, 0, 2)
    c.vline(0, 0, 8, 3)
    c.rect(13, 0, 16, 8, 3); c.vline(14, 0, 8, 0)
    return c


def crate():
    """16x16 run of banded cargo boxes; tiles in any row repeat side by side."""
    c = C(16, 16, 1)
    c.hline(0, 0, 16, 3); c.hline(7, 0, 16, 3); c.hline(8, 0, 16, 3); c.hline(15, 0, 16, 3)
    c.vline(0, 0, 16, 3); c.vline(8, 0, 16, 3)
    for y0 in (1, 9):
        c.rect(1, y0, 8, y0 + 2, 0); c.rect(9, y0, 16, y0 + 2, 2)
        c.rect(3, y0, 5, y0 + 6, 2); c.rect(11, y0, 13, y0 + 6, 3)
    return c


def truck():
    """32x16 lorry, cab to the right, tarpaulin load behind."""
    c = on(PAVE, (32, 16))
    c.frame(0, 2, 22, 13, 3, fill=2)
    for xx in (5, 11, 17):
        c.vline(xx, 3, 12, 1)
    c.hline(3, 1, 21, 1)
    c.frame(21, 4, 31, 13, 3, fill=0)
    c.frame(24, 6, 29, 10, 3, fill=1); c.px(28, 7, 0)
    c.hline(13, 0, 32, 3)
    for cx in (5, 14, 26):
        c.ellipse(cx, 13.5, 2.6, 2.4, 3); c.px(cx, 13, 1)
    return c


def notice_board():
    """16x8 low notice board on two short legs."""
    c = on(PAVE, (16, 8))
    c.frame(0, 0, 16, 6, 3, fill=0)
    c.hline(2, 2, 12, 2); c.hline(4, 2, 9, 2)
    c.rect(2, 6, 4, 8, 3); c.rect(12, 6, 14, 8, 3)
    return c


def dock_sign():
    c = on(PAVE, (16, 16))
    c.rect(3, 11, 5, 16, 3); c.rect(11, 11, 13, 16, 3)
    c.frame(1, 1, 15, 12, 3, fill=0)
    c.hline(4, 3, 13, 2); c.hline(6, 3, 10, 2); c.hline(8, 3, 12, 2)
    return c


def build():
    T = {}
    T[0x0A] = PAVE; T[0x14] = WATER; T[0x5C] = np.full((8, 8), 3, np.uint8)
    T[0x1A] = C(8, 8).paste(PAVE, 0, 0).ellipse(3.5, 4, 3, 2.6, 0, outline=3).a
    T[0x3A] = tex(lambda x, y: 3 if y in (0, 7) else (3 if x == (1 if y < 4 else 5) and y != 3 else (1 if y == 1 else 2)))
    c = C(8, 8).paste(WATER, 0, 0); c.ellipse(4, 4, 3.2, 3.0, 0, outline=3); c.px(3, 3, 1); c.hline(5, 3, 6, 1)
    T[0x31] = c.a
    c = C(8, 8).paste(WATER, 0, 0); c.hline(3, 1, 5, 0); c.hline(6, 4, 7, 0); T[0x2A] = c.a   # spare: foam
    put(T, gangway(), [[0x32, 0x3B]])
    put(T, crate(), [[0x57, 0x56], [0x50, 0x01]])
    put(T, dock_sign(), [[0x54, 0x3F], [0x08, 0x47]])
    put(T, truck(), [[0x4B, 0x4A, 0x49, 0x48], [0x4C, 0x3C, 0x59, 0x58]])
    put(T, ship(), SHIP)
    for i in SPARE_DECK:
        T[i] = T[0x03]
    # KITHBOUND additions: quay edge with a tyre fender / with a bollard, pontoon float, notice board
    c = C(8, 8).paste(T[0x3A], 0, 0); c.ellipse(4, 5, 3.4, 3, 2, outline=3); c.ellipse(4, 5, 1.4, 1.2, 0)
    T[0x1B] = c.a
    c = C(8, 8).paste(T[0x3A], 0, 0); c.ellipse(4, 3.5, 2.6, 2.6, 1, outline=3); c.px(3, 2, 0)
    T[0x2B] = c.a
    c = C(8, 8).paste(WATER, 0, 0); c.frame(1, 1, 7, 7, 3, fill=1); c.hline(2, 2, 6, 0); c.vline(4, 2, 6, 2)
    T[0x46] = c.a
    put(T, notice_board(), [[0x5E, 0x5F]])
    c = C(16, 8).paste(gangway().a, 0, 0); c.rect(1, 3, 13, 5, 3); c.hline(3, 2, 12, 2)
    put(T, c, [list(RAMP_CLEAT)])
    return T


@drawer("tilesets/ship_port.png")
def ship_port(rel, a):
    return build_sheet(build(), a, WALK, "ship_port")
