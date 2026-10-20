"""Club tileset: the bike shop and the two link rooms (trade and battle). Wall, mat, PC and
panel fronts are the shared home drawings; bikes, counter, floor markings and machines are drawn here."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put, tex
from games.pokered.art.ts_interior import face
from games.pokered.art.ts_reds_house import BLACK, WALL, WHITE, cv, mat, pc

WALK = (0x0f, 0x1a, 0x1f, 0x26, 0x28, 0x29, 0x2c, 0x2d, 0x2e, 0x2f, 0x41)

PLAIN = WHITE                                               # white floor square
TILE = tex(lambda x, y: 1 if (x in (1, 6) and 1 <= y <= 6) or (y in (1, 6) and 1 <= x <= 6) or (x, y) == (3, 3) else 0)
MARK = 2                                                    # shade of the lines painted on the floor


def bike(bg):
    """Bicycle seen from the side, 3 x 2 tiles."""
    c = cv(bg, 24, 16)
    for cx in (5.5, 18.5):
        c.ellipse(cx, 10.5, 4.6, 4.6, 0, outline=3)
        c.ellipse(cx, 10.5, 1.2, 1.2, 3)
    c.line(5, 10, 9, 5, 3); c.line(9, 5, 16, 5, 3); c.line(16, 5, 18, 10, 3)
    c.line(9, 5, 12, 10, 3); c.line(12, 10, 16, 5, 3); c.line(5, 10, 12, 10, 2)
    c.rect(7, 2, 11, 4, 3); c.vline(9, 4, 5, 3)
    c.line(16, 5, 17, 2, 3); c.hline(1, 16, 20, 3); c.px(20, 2, 3)
    c.rect(11, 10, 14, 12, 3)
    return c


def counter_top(l=False, r=False, t=False):
    c = C(8, 8, 1)
    if t:
        c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 0)
    if l:
        c.vline(0, 0, 8, 3); c.vline(1, 1 if t else 0, 8, 0)
    if r:
        c.vline(7, 0, 8, 3); c.vline(6, 2 if t else 0, 8, 2)
    return c.a


def column():
    """Round pillar against the wall: one shaft tile (repeats down) and its foot on the floor."""
    c = cv(WALL, 8, 16)
    c.rect(1, 0, 7, 13, 0); c.vline(1, 0, 13, 3); c.vline(6, 0, 13, 3); c.vline(5, 0, 13, 1); c.vline(4, 0, 8, 1)
    c.rect(0, 8, 8, 16, 0)
    c.rect(1, 8, 7, 11, 0); c.vline(1, 8, 11, 3); c.vline(6, 8, 11, 3); c.vline(5, 8, 11, 1)
    c.frame(0, 11, 8, 14, 3, fill=1)
    return c


def poster():
    """Poster: two handhelds joined by a cable."""
    c = cv(WALL, 16, 16)
    c.frame(1, 1, 15, 15, 3, fill=0)
    for x0, y0 in ((3, 3), (9, 7)):
        c.frame(x0, y0, x0 + 4, y0 + 6, 3, fill=1); c.px(x0 + 1, y0 + 1, 0); c.px(x0 + 2, y0 + 1, 0); c.px(x0 + 2, y0 + 4, 3)
    c.line(7, 5, 10, 5, 2); c.px(10, 6, 2)
    c.hline(4, 9, 13, 2)
    return c


def board():
    """Wide notice board on the wall, 4 x 2; the middle column repeats."""
    c = cv(WALL, 32, 16)
    c.frame(0, 1, 32, 15, 3, fill=0)
    c.frame(2, 3, 30, 13, 3, fill=2)
    for x in range(4, 28, 4):
        c.rect(x + 1, 6, x + 3, 8, 0); c.px(x + 1, 10, 1); c.px(x + 2, 10, 1)
    c.hline(15, 1, 31, 2)
    return c


def trade_machine():
    """Link machine: a console either side of a tall domed column, 4 x 3 on the white floor
    (only the column reaches into the top row)."""
    c = cv(PLAIN, 32, 24)
    c.rect(0, 20, 32, 24, 2); c.frame(0, 19, 32, 24, 3)
    for x0 in (1, 21):
        c.frame(x0, 11, x0 + 10, 20, 3, fill=1)
        c.frame(x0 + 2, 13, x0 + 8, 17, 3, fill=0); c.px(x0 + 3, 14, 1)
        c.px(x0 + 2, 18, 3); c.px(x0 + 4, 18, 0); c.px(x0 + 6, 18, 0)
    y, x = c.grid()
    col = ((abs(x - 15.5) <= 4.5) & (y >= 6) & (y <= 21)) | c.emask(16, 6.5, 5, 5)
    c.blob(col, 1.2, 1.0)
    c.hline(10, 12, 20, 3); c.hline(16, 12, 20, 3); c.hline(21, 11, 21, 3)
    c.px(15, 4, 0); c.px(14, 13, 0); c.px(17, 13, 3); c.px(14, 18, 3); c.px(17, 18, 0)
    return c


def battle_table():
    """Table top with a handheld at each end, 4 x 1 (the front is the panel row below)."""
    c = C(32, 8, 1)
    c.hline(0, 0, 32, 3); c.hline(1, 1, 31, 0); c.vline(0, 0, 8, 3); c.vline(31, 0, 8, 3)
    for x0 in (3, 23):
        c.frame(x0, 2, x0 + 6, 8, 3, fill=0); c.rect(x0 + 1, 3, x0 + 5, 5, 2); c.px(x0 + 2, 6, 3); c.px(x0 + 4, 6, 1)
    c.line(9, 5, 22, 5, 2)
    return c


def seat(with_pc=False):
    """Round stool on the white floor; with_pc: the link PC stands behind it (2 x 4 tiles)."""
    c = cv(PLAIN, 16, 32)
    if with_pc:
        c.paste(pc(False, PLAIN), 0, 0)
        c.rect(0, 16, 16, 24, 0)
        c.frame(2, 17, 14, 21, 3, fill=0); c.pat(3, 18, 13, 20, lambda x, y: 2 if (x + y) % 2 == 0 else 0)
    c.rect(6, 27, 10, 31, 2); c.vline(5, 27, 31, 3); c.vline(10, 27, 31, 3); c.hline(31, 3, 13, 3)
    c.ellipse(8, 25.5, 6.4, 3.4, 1, outline=3)
    c.hline(24, 5, 9, 0)
    return c


def pump():
    """Tool box with a tyre pump standing in it."""
    c = cv(PLAIN, 16, 16)
    c.frame(1, 7, 12, 15, 3, fill=1); c.hline(8, 2, 11, 0); c.rect(5, 10, 8, 12, 3)
    c.rect(12, 3, 14, 15, 3); c.vline(12, 4, 14, 0); c.hline(2, 10, 16, 3); c.hline(15, 9, 16, 3)
    return c


def build():
    T = {}
    T[0x00] = WHITE; T[0x0F] = PLAIN; T[0x1F] = TILE; T[0x1E] = TILE; T[0x06] = WALL; T[0x19] = BLACK
    T[0x0A], T[0x1A] = mat()
    put(T, bike(WALL), [[0x01, 0x02, 0x03], [0x11, 0x12, 0x13]])
    put(T, bike(PLAIN), [[0x0B, 0x0C, 0x0E], [0x1B, 0x1C, 0x09]])
    put(T, pump(), [[0x1D, 0x0D], [0x15, 0x16]])
    # counter
    T[0x07] = counter_top(l=True); T[0x08] = counter_top(r=True)
    T[0x36] = counter_top(l=True, t=True); T[0x10] = counter_top(t=True); T[0x05] = counter_top(r=True, t=True)
    put(T, face(2), [[0x17, 0x18]])
    # wall pieces
    c = cv(WALL, 8, 16)
    c.ellipse(4, 4, 3.6, 3.6, 0, outline=3); c.line(4, 4, 4, 2, 3); c.line(4, 4, 5, 5, 3)
    c.frame(1, 9, 7, 15, 3, fill=0); c.hline(11, 2, 6, 2); c.hline(13, 2, 5, 2)
    put(T, c, [[0x04], [0x14]])
    put(T, poster(), [[0x30, 0x31], [0x32, 0x33]])
    put(T, column(), [[0x34], [0x35]])
    put(T, board(), [[0x3F, 0x44, None, 0x45], [0x42, 0x43, None, 0x46]])
    # floor markings
    T[0x28] = tex(lambda x, y: MARK if x - y in (0, 1) else 0)
    T[0x29] = T[0x28][:, ::-1].copy()
    T[0x2C] = tex(lambda x, y: MARK if y in (1, 2) else 0)
    T[0x2D] = tex(lambda x, y: MARK if y in (5, 6) else 0)
    T[0x2E] = tex(lambda x, y: MARK if x in (1, 2) else 0)
    T[0x2F] = tex(lambda x, y: MARK if x in (5, 6) else 0)
    # machines and seats
    put(T, trade_machine(), [[None, 0x40, 0x41, None], [0x3B, 0x3C, 0x3D, 0x3E], [0x37, 0x38, 0x39, 0x3A]])
    put(T, battle_table(), [[0x47, 0x48, 0x49, 0x4A]])
    put(T, seat(True), [[0x20, 0x21], [0x22, 0x23], [0x24, 0x25], [0x26, 0x27]])
    put(T, seat(False), [[None, None], [None, None], [0x2A, 0x2B], [None, None]])
    return T


@drawer("tilesets/club.png")
def club(rel, a):
    return build_sheet(build(), a, WALK, "club")
