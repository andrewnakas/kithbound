"""Overworld tileset: towns and routes. Every tile is drawn here from what the
tile is (lawn, tree, roof, ledge ...), in our own style."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex

WALK = (0x00, 0x10, 0x1b, 0x20, 0x21, 0x23, 0x2c, 0x2d, 0x2e, 0x30, 0x31, 0x33, 0x39, 0x3c, 0x3e, 0x52, 0x54, 0x58, 0x5b)

LAWN = T8("""
........
.-...-..
-...-...
........
........
...-...-
..-...-.
........""")
SAND = T8("""
........
..-.....
........
......-.
........
.-......
....-...
........""")
TUFT = T8("""
........
.+...+..
..+.+...
...+....
........
+...+...
.+.+....
..+.....""")
TALL = T8("""
.#....#.
.#+..#+.
#+#.#+#.
#+#+#+#+
.+#.+#+.
...#....
.#+#+#..
..#+#...""")
WATER = T8("""
++++++++
+--+++++
-++-++-+
++++++++
++++--++
+++-++-+
++++++++
++++++++""")
ROCK = T8("""
--------
--+-----
------.-
-.------
----+---
--------
-+----.-
--------""")
PLANK = T8("""
--------
---.----
--------
++++++++
--------
-------.
--------
++++++++""")
PLANK2 = T8("""
--------
-+----+-
--------
++++++++
--------
-+----+-
--------
++++++++""")
PAVE = T8("""
-------+
-------+
-------+
-------+
-------+
-------+
-------+
++++++++""")
LEDGE = T8("""
........
########
-+-+-+-+
+-+-+-+-
++++++++
+#+#+#+#
########
........""")
LEDGE_L = T8("""
........
..######
.#-+-+-+
.#+-+-+-
.#++++++
.##+#+#+
..######
........""")
FLOWER = ["""
........
...##...
..#--#..
.#-++-#.
..#--#..
...##...
...+....
..++....""", """
........
..##....
.#--#...
#-++-#..
.#--#...
..##....
...+....
..++....""", """
........
....##..
...#--#.
..#-++-#
...#--#.
....##..
...+....
..++...."""]
S3 = {"P": "111/101/111/100/100", "O": "111/101/101/101/111", "K": "101/101/110/101/101",
      "E": "111/100/110/100/111", "M": "101/111/111/101/101", "A": "010/101/111/101/101",
      "R": "110/101/110/101/101", "T": "111/010/010/010/010", "G": "111/100/101/101/111",
      "Y": "101/101/010/010/010"}

FACE_L = tex(lambda x, y: 3 if (x + y) % 8 == 2 else (1 if (x + y) % 8 == 6 else 2))
FACE_R = tex(lambda x, y: 3 if (x - y) % 4 == 0 else 2)


def on(bg, c):
    """Canvas of the size of c tiled with an 8x8 background."""
    out = C(c[0], c[1])
    out.a[:] = np.tile(bg, (c[1] // 8, c[0] // 8))
    return out


def small_text(c, s, x, y, shade=3):
    for ch in s:
        c.put(S3[ch].replace("0", " ").replace("1", "#" if shade == 3 else "."), x, y)
        x += 4


def tree():
    c = on(LAWN, (16, 16))
    c.rect(6, 11, 10, 15, 1); c.vline(6, 11, 15, 3); c.vline(9, 11, 15, 3); c.hline(15, 4, 12, 3)
    c.blob(c.emask(8, 6.5, 7.6, 6.4), 1.9, 1.2)
    for x, y in ((5, 4), (4, 6), (7, 3), (10, 9), (12, 7), (6, 9)):
        c.px(x, y, 1 if x < 8 else 3)
    return c


def bush():
    c = on(LAWN, (16, 16))
    c.rect(7, 11, 9, 15, 2); c.hline(15, 5, 11, 3)
    c.blob(c.emask(8, 7, 5.6, 5.2), 1.6, 1.2)
    c.px(6, 5, 0); c.px(9, 8, 3); c.px(7, 9, 3)
    return c


def bollard():
    c = C(16, 16)
    y, x = c.grid()
    body = (abs(x - 7.5) <= 6.5) & (y >= 5) & (y <= 14) | c.emask(8, 5.5, 6.9, 4.2) | c.emask(8, 12.5, 6.9, 3)
    c.blob(body, 1.2, 1.0)
    c.ellipse(8, 5.5, 5.4, 3.0, 0, outline=3)
    c.vline(8, 9, 14, 2)
    return c


def post():
    c = C(8, 16)
    y, x = c.grid()
    c.blob(((abs(x - 3.5) <= 2.5) & (y >= 4) & (y <= 13)) | c.emask(4, 4.5, 3, 3) | c.emask(4, 13, 3, 2), 1.1, 1.0)
    return c


def sign():
    c = C(16, 16)
    c.rect(3, 11, 5, 16, 3); c.rect(11, 11, 13, 16, 3)
    c.frame(1, 1, 15, 12, 3, fill=0)
    c.hline(4, 3, 13, 2); c.hline(6, 3, 10, 2); c.hline(8, 3, 12, 2)
    c.hline(12, 2, 15, 2)
    return c


def cave():
    c = on(FACE_R, (16, 16))
    c.fill(c.emask(8, 10, 7.2, 9.5), 1, outline=3)
    c.fill(c.emask(8, 11, 5.4, 8), 3)
    c.rect(0, 15, 16, 16, 3)
    return c


def roof():
    """Hip roof, 5 tiles wide (the middle column repeats) and 2 high."""
    c = C(40, 16)
    body = c.pmask([(12, 1), (28, 1), (39, 16), (1, 16)])
    c.a[body] = 2
    y, x = c.grid()
    c.a[body & ((y % 4) == 1)] = 3                         # shingle rows
    hipl = body & (x < 12); hipr = body & (x >= 28)
    c.a[hipl | hipr] = 1
    c.a[(hipl | hipr) & (x % 2 == 0)] = 2
    c.fill(body, None) if False else None
    d = np.zeros_like(body)
    d[:, 1:] |= body[:, 1:] & ~body[:, :-1]; d[:, :-1] |= body[:, :-1] & ~body[:, 1:]
    d[1:, :] |= body[1:, :] & ~body[:-1, :]
    c.a[d] = 3
    c.vline(12, 2, 16, 3); c.vline(27, 2, 16, 3)
    c.hline(15, 1, 39, 3)
    c.hline(2, 13, 27, 1)
    c.px(0, 7, 1)                                          # the corner tiles are never blank
    c.px(39, 7, 1)
    return c


def wall(kind):
    """kind: plain, eave, brick, left, right (edges at x=4 / x=3), base, base_l, base_r, posts."""
    c = C(8, 8)
    if kind == "brick":
        c.pat(0, 0, 8, 8, lambda x, y: 1 if (y % 4 == 3 or (x == (1 if y // 4 == 0 else 5) and y % 4 != 3)) else 0)
    if kind in ("eave", "eave_l", "eave_r"):
        c.rect(0, 0, 8, 2, 2)
    if kind in ("base", "base_l", "base_r", "posts"):
        c.hline(4, 0, 8, 3); c.rect(0, 5, 8, 7, 2); c.hline(7, 0, 8, 3)
    if kind == "posts":
        c.rect(1, 0, 2, 4, 3); c.rect(6, 0, 7, 4, 3)
    if kind in ("left", "eave_l", "base_l"):
        c.rect(0, 0, 4, 8, 0); c.vline(4, 0, 8, 3)
        if kind == "eave_l":
            c.rect(2, 0, 8, 2, 2)
    if kind in ("right", "eave_r", "base_r"):
        c.rect(4, 0, 8, 8, 0); c.vline(3, 0, 8, 3)
        if kind == "eave_r":
            c.rect(0, 0, 6, 2, 2)
    return c.a


def window():
    c = C(8, 8)
    c.frame(1, 1, 7, 7, 3, fill=2)
    c.line(2, 4, 4, 2, 0); c.px(5, 5, 1); c.hline(7, 1, 7, 2)
    return c.a


def door():
    c = C(16, 16)
    c.frame(2, 1, 14, 17, 3, fill=1)
    c.frame(5, 4, 11, 9, 3, fill=2); c.px(6, 5, 0); c.px(7, 5, 0)
    c.px(11, 11, 3); c.hline(15, 0, 16, 3)
    c.rect(3, 13, 13, 15, 2)
    return c


def board(text):
    c = C(16, 8, 0)
    c.hline(0, 0, 16, 3); c.hline(7, 0, 16, 3)
    small_text(c, text, (16 - (len(text) * 4 - 1)) // 2 + (1 if len(text) == 4 else 0), 1)
    return c


def build():
    T = {}
    T[0x23] = np.zeros((8, 8), np.uint8)
    T[0x00] = T[0x23]
    T[0x39] = SAND; T[0x2C] = LAWN; T[0x30] = TUFT; T[0x52] = TALL
    T[0x14] = WATER; T[0x11] = ROCK; T[0x3C] = PLANK; T[0x04] = PLANK2; T[0x5B] = PAVE
    T[0x03] = C(8, 8).paste(LAWN, 0, 0).put(FLOWER[0].replace(".", " "), 0, 0).a
    # ledges and cliffs
    T[0x37] = LEDGE; T[0x36] = LEDGE_L; T[0x34] = LEDGE_L[:, ::-1]
    T[0x27] = FACE_L; T[0x24] = FACE_R
    c = C(8, 8); c.paste(FACE_R, 0, 0); c.vline(0, 0, 8, 3); c.hline(7, 0, 8, 3); c.px(0, 7, 0); T[0x13] = c.a
    T[0x35] = T[0x13][:, ::-1]
    c = C(8, 8); c.paste(SAND, 0, 0); c.vline(6, 0, 8, 3); c.vline(7, 0, 8, 2); T[0x0D] = c.a
    c = C(8, 8); c.paste(LAWN, 0, 0); c.vline(6, 0, 8, 3); c.vline(7, 0, 8, 2); T[0x1D] = c.a
    c = C(8, 8); c.paste(ROCK, 0, 0); c.hline(0, 0, 8, 3); c.hline(1, 0, 8, 0); T[0x01] = c.a
    T[0x02] = tex(lambda x, y: 3 if x == y else (FACE_R[y, x] if x < y else 0))
    T[0x1E] = tex(lambda x, y: 3 if x + y == 7 else (FACE_L[y, x] if x + y > 7 else 0))
    # water edges
    c = C(8, 8); c.paste(WATER, 0, 0); c.rect(0, 0, 8, 2, 0); c.hline(2, 0, 8, 3); c.hline(3, 0, 8, 1); T[0x33] = c.a
    c = C(8, 8); c.paste(WATER, 0, 0); c.rect(0, 0, 2, 8, 0); c.vline(2, 0, 8, 3); c.vline(3, 0, 8, 1); T[0x32] = c.a
    T[0x54] = T[0x32][:, ::-1]
    c = C(8, 8); c.paste(WATER, 0, 0); c.rect(0, 0, 8, 3, 1); c.vline(3, 0, 3, 2); c.hline(3, 0, 8, 3)
    c.rect(1, 4, 3, 6, 3); c.rect(5, 4, 7, 6, 3); T[0x31] = c.a
    # fences and posts
    c = C(8, 8); c.hline(2, 0, 8, 3); c.rect(0, 3, 8, 5, 1); c.hline(5, 0, 8, 3); T[0x20] = c.a
    T[0x10] = T[0x20].T.copy()
    c = C(8, 8); c.blob(c.emask(4, 4, 3.6, 3.6), 1.0, 1.2); c.px(3, 2, 0); T[0x21] = c.a
    put(T, post(), [[0x0E], [0x55]])
    put(T, bollard(), [[0x2A, 0x2B], [0x3A, 0x3B]])
    put(T, tree(), [[0x40, 0x41], [0x50, 0x51]])
    put(T, bush(), [[0x2D, 0x2E], [0x3D, 0x3E]])
    put(T, sign(), [[0x46, 0x47], [0x56, 0x57]])
    put(T, cave(), [[0x48, 0x49], [0x58, 0x59]])
    # buildings
    put(T, roof(), [[0x05, 0x06, 0x07, 0x08, 0x09], [0x15, 0x16, 0x17, 0x18, 0x19]])
    T[0x25] = wall("eave_l"); T[0x26] = wall("eave"); T[0x28] = wall("eave"); T[0x29] = wall("eave_r")
    T[0x0F] = wall("left"); T[0x1F] = wall("right"); T[0x4B] = wall("brick")
    c = C(8, 8); c.hline(0, 0, 8, 1); T[0x22] = c.a
    T[0x1A] = wall("base"); T[0x4E] = wall("base_l"); T[0x4F] = wall("base_r"); T[0x4A] = wall("posts")
    T[0x0A] = window()
    put(T, door(), [[0x0B, 0x0C], [0x1B, 0x1C]])
    put(T, board("GYM"), [[0x2F, 0x3F]])
    put(T, board("POKE"), [[0x42, 0x43]])
    put(T, board("MART"), [[0x44, 0x45]])
    # big flat roofs
    T[0x53] = tex(lambda x, y: 3 if y in (0, 7) else (1 if (x + y) % 4 == 0 or (x - y) % 4 == 0 else 2))
    T[0x12] = tex(lambda x, y: 2 if (x % 4 == 2 and y % 4 == 2) else 1)
    T[0x38] = tex(lambda x, y: 3 if x in (3, 4) else (2 if (x % 4 == 2 and y % 4 == 2) else 1))
    T[0x5A] = tex(lambda x, y: 3 if x in (0, 7) else 2)
    c = C(8, 8, 2); c.vline(0, 0, 8, 3); c.vline(7, 0, 8, 3); c.hline(0, 0, 8, 3); c.hline(1, 1, 7, 1); T[0x4C] = c.a
    T[0x4D] = T[0x4C]
    c = C(8, 8, 2); c.vline(0, 0, 8, 3); c.vline(7, 0, 8, 3); c.hline(7, 0, 8, 3); c.hline(5, 1, 7, 3); T[0x5C] = c.a
    T[0x5D] = T[0x5C]
    return T


@drawer("tilesets/overworld.png")
def overworld(rel, a):
    return build_sheet(build(), a, WALK, "overworld")


@drawer("tilesets/flower/flower*.png")
def flower(rel, a):
    n = int(rel[-5]) - 1
    return C(8, 8).paste(LAWN, 0, 0).put(FLOWER[n].replace(".", " "), 0, 0).a
