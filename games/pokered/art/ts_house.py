"""Town house tileset (homes, school, daycare, the burgled house). Furniture comes from
ts_reds_house so every home looks the same; the rest is drawn here."""
from games.pokered.art import drawer
from games.pokered.art.tilekit import C, build_sheet, put
from games.pokered.art.ts_reds_house import (FLOOR, WALL, cv, home_common, plant, shelf_doors, shelf_items,
                                             stairs_down, stairs_up, table, window)

WALK = (0x01, 0x12, 0x14, 0x28, 0x32, 0x37, 0x44, 0x54, 0x5c)


def wall_map(bg=WALL):
    """Framed map on the wall: land, a lake and a few routes."""
    c = cv(bg, 16, 16)
    c.frame(0, 1, 16, 14, 3, fill=0)
    c.frame(1, 2, 15, 13, 1)
    c.fill(c.emask(6, 6, 3.4, 2.4) | c.emask(10.5, 9, 3.2, 2.6), 1, outline=2)
    c.line(4, 10, 6, 8, 3); c.line(8, 5, 12, 5, 3); c.px(12, 4, 3); c.px(4, 11, 3)
    c.hline(14, 1, 15, 2)
    return c


def picture(bg=WALL, c=None):
    """Framed landscape painting on the wall (c: ready 16x16 background canvas)."""
    c = c or cv(bg, 16, 16)
    c.frame(0, 1, 16, 14, 3, fill=0)
    c.frame(1, 2, 15, 13, 2)
    c.poly([(2, 12), (6, 6), (9, 10), (11, 8), (14, 12)], 2)
    c.px(6, 6, 0); c.px(6, 7, 0); c.ellipse(11.5, 4.5, 1.5, 1.5, 1)
    c.hline(14, 1, 15, 2)
    return c


def blackboard(bg=WALL):
    """School blackboard, 4 x 2 tiles; the top middle tile repeats."""
    c = cv(bg, 32, 16)
    c.frame(0, 0, 32, 13, 3, fill=3)
    c.frame(1, 1, 31, 12, 1)
    c.rect(0, 13, 32, 15, 1); c.hline(15, 0, 32, 3); c.vline(0, 13, 15, 3); c.vline(31, 13, 15, 3)
    c.rect(11, 12, 15, 14, 0); c.rect(18, 12, 23, 14, 2); c.hline(12, 18, 23, 3)
    c.ellipse(5, 5, 2.4, 2.4, 3, outline=0)
    c.line(26, 3, 28, 6, 0); c.line(28, 3, 26, 6, 0)
    c.hline(9, 4, 12, 0); c.hline(9, 14, 20, 0); c.hline(9, 22, 27, 0); c.hline(10, 9, 11, 0)
    return c


def wall_hole(bg=WALL):
    """Hole smashed through the wall: ragged opening, ground showing at the foot, rubble."""
    c = cv(bg, 16, 16)
    c.poly([(2, 16), (1, 10), (3, 6), (2, 3), (6, 4), (8, 1), (11, 4), (14, 3), (13, 8), (15, 11), (14, 16)], 3, outline=3)
    c.poly([(4, 16), (4, 12), (7, 10), (10, 11), (12, 13), (12, 16)], 0)
    c.px(6, 13, 1); c.px(9, 14, 1)
    c.rect(1, 14, 4, 16, 1); c.px(1, 13, 3); c.px(2, 13, 3); c.px(3, 13, 3); c.px(0, 14, 3); c.px(0, 15, 3)
    c.rect(13, 14, 15, 16, 1); c.px(13, 13, 3); c.px(14, 13, 3); c.px(15, 14, 3); c.px(15, 15, 3)
    c.line(0, 2, 2, 4, 3); c.line(12, 1, 13, 3, 3)
    return c


def cracked(bg=WALL):
    c = cv(bg, 8, 8)
    c.line(2, 1, 4, 3, 3); c.line(4, 3, 3, 5, 3); c.line(4, 3, 6, 4, 3); c.px(6, 5, 3)
    return c.a


def tipped_stool(bg=FLOOR):
    """A stool knocked over on its side."""
    c = cv(bg, 16, 16)
    c.poly([(8, 1), (15, 8), (8, 15), (1, 8)], 1, outline=3)
    c.poly([(8, 4), (12, 8), (8, 12), (4, 8)], 0, outline=2)
    c.line(2, 10, 5, 13, 3); c.line(11, 13, 14, 10, 3)
    return c


def fallen_plant(bg=FLOOR):
    """House plant lying on the floor (2 x 2) and its broken pot with spilt soil (2 x 2)."""
    c = cv(bg, 32, 16)
    crown = c.emask(6, 6, 5.5, 4.4) | c.emask(9, 10.5, 5.5, 4)
    c.blob(crown, 1.9, 1.2)
    c.px(4, 5, 0); c.px(8, 9, 0); c.line(7, 7, 12, 11, 3)
    c.line(13, 11, 18, 11, 3); c.line(13, 12, 18, 12, 2)
    c.poly([(18, 7), (26, 5), (27, 14), (18, 13)], 2, outline=3)
    c.poly([(25, 4), (28, 4), (29, 15), (26, 15)], 1, outline=3)
    c.line(21, 7, 22, 10, 3); c.line(22, 10, 20, 12, 3)
    for x, y in ((20, 3), (23, 2), (29, 2), (30, 6), (30, 12), (24, 15), (21, 14)):
        c.px(x, y, 3); c.px(x + 1, y, 2)
    return c


def wreck(bg=FLOOR):
    """Pulled-out drawer upside down with papers around it."""
    c = cv(bg, 16, 16)
    c.poly([(2, 5), (11, 3), (14, 9), (5, 12)], 2, outline=3)
    c.line(5, 7, 10, 6, 1); c.px(8, 8, 3)
    c.poly([(9, 10), (15, 11), (14, 15), (8, 14)], 0, outline=3)
    c.hline(12, 10, 13, 2)
    c.poly([(1, 11), (5, 13), (3, 15), (0, 14)], 0, outline=3)
    c.px(13, 2, 3); c.px(14, 3, 2)
    return c


def book(c, x, y):
    """Open notebook, 12 x 10."""
    c.frame(x, y, x + 12, y + 10, 3, fill=0)
    c.vline(x + 5, y, y + 10, 3); c.vline(x + 6, y + 1, y + 9, 1)
    for j in (2, 4, 6):
        c.hline(y + j, x + 2, x + 4, 2); c.hline(y + j, x + 8, x + 10, 2)
    return c


def build():
    T = home_common({})
    put(T, plant(), [[0x0A, 0x0B], [0x08, 0x09], [0x1A, 0x1B], [0x18, 0x19]])
    put(T, fallen_plant(), [[0x2A, 0x2B, 0x2C, 0x25], [0x0C, 0x0D, 0x35, 0x38]])
    put(T, shelf_items(), [[0x0E, 0x0F]])
    put(T, shelf_doors(), [[0x1E, 0x1F]])
    c = cv(FLOOR, 8, 8); c.frame(1, 1, 7, 7, 3, fill=2); c.rect(2, 2, 6, 3, 0); c.hline(5, 2, 6, 1); T[0x22] = c.a
    put(T, wall_hole(), [[0x23, 0x4A], [0x54, 0x55]])
    put(T, window(1), [[0x24], [0x34]])
    t = table(3, 3)
    put(T, t, [[0x26, 0x27, 0x29], [0x36, 0x2F, 0x39], [0x3C, 0x3A, 0x3B]])
    t = table(4, 4); book(t, 3, 11)
    put(T, t, [[None, None], [0x46, 0x47], [0x56, 0x57]])
    c = cv(FLOOR, 8, 8); c.rect(2, 1, 5, 4, 2); c.px(2, 1, 0); c.rect(3, 5, 5, 7, 2); c.px(5, 2, 1); T[0x28] = c.a
    c = cv(FLOOR, 8, 8)
    for x, y in ((1, 1), (4, 2), (2, 4), (5, 5), (3, 6)):
        c.px(x, y, 2); c.px(x + 1, y, 1)
    T[0x37] = c.a
    put(T, wall_map(), [[0x2D, 0x2E], [0x3D, 0x3E]])
    T[0x3F] = cracked()
    put(T, stairs_up(), [[0x4E, 0x4F], [0x32, 0x33]])
    put(T, stairs_down(), [[0x4C, 0x4D], [0x5C, 0x5D]])
    put(T, tipped_stool(), [[0x1C, 0x1D], [0x44, 0x45]])
    put(T, blackboard(), [[0x48, None, 0x49, 0x4B], [0x58, 0x59, 0x5A, 0x5B]])
    put(T, wreck(), [[0x50, 0x51], [0x52, 0x53]])
    return T


@drawer("tilesets/house.png")
def house(rel, a):
    return build_sheet(build(), a, WALK, "house")
