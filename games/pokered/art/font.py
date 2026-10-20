"""Text font, text box frame, HP bar and battle HUD tiles: all drawn here.

The font is our own 5x7 design (one pixel strokes, lower case with descenders
in the eighth row), placed one pixel in from the left of each 8x8 cell.
"""
import numpy as np

from games.pokered.art import art, blit, drawer, sheet

G = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01110/10001/10000/10000/10000/10001/01110",
    "D": "11100/10010/10001/10001/10001/10010/11100",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01110/10001/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "01110/00100/00100/00100/00100/00100/01110",
    "J": "00111/00010/00010/00010/00010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/11011/10001",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "a": "00000/00000/01110/00001/01111/10001/01111",
    "b": "10000/10000/10110/11001/10001/10001/11110",
    "c": "00000/00000/01110/10000/10000/10001/01110",
    "d": "00001/00001/01101/10011/10001/10001/01111",
    "e": "00000/00000/01110/10011/11100/10000/01110",
    "f": "00110/01001/01000/11100/01000/01000/01000",
    "g": "00000/00000/01111/10001/10001/01111/00001/01110",
    "h": "10000/10000/10110/11001/10001/10001/10001",
    "i": "00100/00000/01100/00100/00100/00100/01110",
    "j": "00010/00000/00110/00010/00010/00010/10010/01100",
    "k": "10000/10000/10010/10100/11000/10100/10010",
    "l": "01100/00100/00100/00100/00100/00100/01110",
    "m": "00000/00000/11010/10101/10101/10101/10101",
    "n": "00000/00000/10110/11001/10001/10001/10001",
    "o": "00000/00000/01110/10001/10001/10001/01110",
    "p": "00000/00000/11110/10001/10001/11110/10000/10000",
    "q": "00000/00000/01111/10001/10001/01111/00001/00001",
    "r": "00000/00000/10110/11001/10000/10000/10000",
    "s": "00000/00000/01111/11000/00110/00011/11110",
    "t": "01000/01000/11100/01000/01000/01001/00110",
    "u": "00000/00000/10001/10001/10001/10011/01101",
    "v": "00000/00000/10001/10001/10001/01010/00100",
    "w": "00000/00000/10001/10001/10101/10101/01010",
    "x": "00000/00000/10001/01010/00100/01010/10001",
    "y": "00000/00000/10001/10001/10001/01111/00001/01110",
    "z": "00000/00000/01111/00010/00100/01000/11110",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11110/00001/00001/01110/00001/00001/11110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/11110/00001/00001/10001/01110",
    "6": "00110/01000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00010/01100",
    "(": "00010/00100/01000/01000/01000/00100/00010",
    ")": "01000/00100/00010/00010/00010/00100/01000",
    ":": "00000/01100/01100/00000/01100/01100/00000",
    ";": "00000/01100/01100/00000/01100/00100/01000",
    "[": "01110/01000/01000/01000/01000/01000/01110",
    "]": "01110/00010/00010/00010/00010/00010/01110",
    "é": "00010/00100/01110/10001/11111/10000/01110",
    "'": "00100/00100/01000",
    "-": "00000/00000/00000/11111",
    "?": "01110/10001/00001/00010/00100/00000/00100",
    "!": "00100/00100/00100/00100/00100/00000/00100",
    ".": "00000/00000/00000/00000/00000/01100/01100",
    ",": "00000/00000/00000/00000/01100/00100/01000",
    "/": "00001/00001/00010/00100/01000/10000/10000",
    "x_times": "00000/10001/01010/00100/01010/10001",
    "male": "00111/00011/00101/01100/10010/10010/01100",
    "female": "00100/01010/01010/00100/01110/00100/00000",
    "money": "01110/01001/01001/11110/01000/11110/01000",
    "tri_open": "10000/11000/10100/10010/10100/11000/10000",
    "tri": "10000/11000/11100/11110/11100/11000/10000",
    "tri_down": "00000/11111/11111/01110/01110/00100",
    "kana_a": "00000/00000/11111/00001/00110/00100/01000",
    "kana_u": "00000/00100/11111/10001/00001/00010/00100",
    "kana_e": "00000/00000/01110/00100/00100/11111",
    "dot_mid": "00000/00000/00000/01100/01100",
    "dots": "00000/00000/00000/00000/00000/10101",
    "quote_l1": "00100/01000/01000",
    "quote_r1": "00100/00100/01000",
    "quote_l2": "01010/10100/10100",
    "quote_r2": "01010/01010/10100",
    "hira_a": "00100/11110/00100/01110/10101/10101/01001",
    "hira_e": "01110/00000/11110/00100/01100/10010/10011",
    "hira_o": "01000/11101/01000/01110/11001/01001/11010",
    "hira_i": "00000/00000/10010/10001/10001/01001/00100",
    "hira_u": "00000/01110/00000/01110/00001/00010/01100",
}
SMALL = {"P": "111/101/111/100/100", "K": "101/101/110/101/101", "M": "101/111/111/101/101",
         "N": "1001/1101/1011/1001/1001", "H": "101/101/111/101/101", "I": "111/010/010/010/111",
         "D": "110/101/101/101/110", "o": "000/000/010/101/010", "L": "100/100/100/100/111",
         "E": "111/100/110/100/111", "t": "010/111/010/010/011", "v": "000/000/101/101/010"}


# Heavy letters: every glyph is the 5x7 skeleton with doubled upright strokes (6 wide);
# the few that would clog are drawn by hand, 7 wide.
WIDE = {
    "M": "1100011/1110111/1111111/1101011/1100011/1100011/1100011",
    "W": "1100011/1100011/1100011/1101011/1111111/1110111/1100011",
    "N": "110011/111011/111111/110111/110011/110011/110011",
    "m": "0000000/0000000/1110110/1111111/1101011/1101011/1101011",
    "w": "0000000/0000000/1100011/1101011/1101011/1111111/0110110",
    "0": "011110/110011/110111/111011/110011/110011/011110",
}
THIN = ("tri_open", "tri", "tri_down", "dots", "dot_mid", "x_times", "/", "kana_a", "kana_u", "kana_e",
        "hira_a", "hira_e", "hira_o", "hira_i", "hira_u", "male", "female", "money")


def heavy(name):
    if name in WIDE:
        return art(WIDE[name])
    g = art(G[name], 5)
    if name in THIN:
        return g
    out = np.zeros((g.shape[0], 6), np.uint8)
    out[:, :5] = g
    out[:, 1:] |= g
    return out


def glyph(name, x=None, y=0):
    t = np.zeros((8, 8), np.uint8)
    g = heavy(name)
    return blit(t, g, (0 if g.shape[1] >= 7 else 1) if x is None else x, y)


def bold(name):
    """Display capital: the heavy glyph with a grey drop shadow."""
    g = heavy(name)
    t = np.zeros((8, 8), np.uint8)
    x = 0 if g.shape[1] >= 7 else 1
    blit(t, (g > 0).astype(np.uint8) * 2, x + 1, 1, transparent=0)
    blit(t, g, x, 0, transparent=0)
    return t


def apostrophe(letter):
    t = np.zeros((8, 8), np.uint8)
    blit(t, heavy(letter), 2, 0)
    t[0, 0] = t[0, 1] = t[1, 0] = 3
    t[0:2, 2:4] = 0
    return t


def pair(a, b):
    """Two small capitals in one cell, the second set lower (PK, MN)."""
    t = np.zeros((8, 8), np.uint8)
    blit(t, art(SMALL[a]), 0, 0)
    sb = art(SMALL[b])
    blit(t, sb, 8 - sb.shape[1], 3)
    return t


@drawer("font/font.png")
def font(rel, a):
    row = {}
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ():;[]abcdefghijklmnopqrstuvwxyz"):
        row[i] = glyph(c)
    row[0x3a] = glyph("é")
    for i, c in enumerate("dlstv"):
        row[0x3b + i] = apostrophe(c)
    row[0x60] = glyph("'"); row[0x61] = pair("P", "K"); row[0x62] = pair("M", "N")
    row[0x63] = glyph("-"); row[0x64] = apostrophe("r"); row[0x65] = apostrophe("m")
    row[0x66] = glyph("?"); row[0x67] = glyph("!"); row[0x68] = glyph(".")
    for i, c in enumerate(["kana_a", "kana_u", "kana_e", "tri_open", "tri", "tri_down", "male",
                           "money", "x_times", ".", "/", ",", "female"]):
        row[0x69 + i] = glyph(c)
    for i, c in enumerate("0123456789"):
        row[0x76 + i] = glyph(c)
    return sheet([row.get(i) for i in range(128)], a["w"], a["h"])


# ---- text box frame: one thick rounded line -------------------------------------------

def frame(kind):
    """Text box frame: a 3 pixel band (black, light core, black) at rows/columns 2-4."""
    t = np.zeros((8, 8), np.uint8)
    band = (3, 1, 3)
    if kind == "h":
        for k, s in enumerate(band):
            t[2 + k, :] = s
        return t
    if kind == "v":
        for k, s in enumerate(band):
            t[:, 2 + k] = s
        return t
    top, left = kind[0] == "t", kind[1] == "l"
    xs = slice(2, 8) if left else slice(0, 5)
    ys = slice(2, 8) if top else slice(0, 5)
    for k, s in enumerate(band):
        t[2 + k, xs] = s
    for k, s in enumerate(band):
        t[ys, 2 + k] = s
    t[2:5, 2:5] = 3
    t[3, 3] = 1
    t[3, 4 if left else 2] = 1
    t[4 if top else 2, 3] = 1
    return t


FRAME = [frame("tl"), frame("h"), frame("tr"), frame("v"), frame("bl"), frame("br")]


@drawer("font/font_extra.png")
def font_extra(rel, a):
    row = [bold(c) for c in "ABCDEFGHIVSLM"]
    row += [glyph(":"), glyph("hira_i"), glyph("hira_u")]
    row += [glyph(c) for c in ("quote_l1", "quote_r1", "quote_l2", "quote_r2", "dot_mid", "dots",
                               "hira_a", "hira_e", "hira_o")]
    row += FRAME + [None]
    return sheet(row, a["w"], a["h"])


# ---- HP bar and battle HUD ----------------------------------------------------------------

def bar(fill, left=False, right=None):
    t = np.zeros((8, 8), np.uint8)
    if right is None:
        t[1, :] = 3; t[6, :] = 3
        t[2:6, :fill] = 2
        t[2, :fill] = 1
    return t


def small_text(a, b, gap=1, y=1):
    t = np.zeros((8, 8), np.uint8)
    sa, sb = art(SMALL[a]), art(SMALL[b])
    blit(t, sa, 0, y)
    blit(t, sb, sa.shape[1] + gap, y)
    return t


def bar_left():
    t = np.zeros((8, 8), np.uint8)
    t[2, 0] = t[4, 0] = 3              # colon after HP
    t[1:7, 4:6] = 3                    # bar cap
    t[1, 6:] = 3; t[6, 6:] = 3
    t[1, 4] = t[6, 4] = 0
    return t


def bar_right(line):
    t = np.zeros((8, 8), np.uint8)
    t[1:7, 0:2] = 3
    t[1, 1] = t[6, 1] = 0
    if line:
        t[:, 3:5] = 3
    return t


def hud_v():
    t = np.zeros((8, 8), np.uint8); t[:, 3:5] = 3; return t


def hud_h(y=4):
    t = np.zeros((8, 8), np.uint8); t[y:y + 2, :] = 3; return t


def hud_corner(left):
    t = np.zeros((8, 8), np.uint8)
    t[0:6, 3:5] = 3
    if left:
        t[4:6, 3:] = 3
    else:
        t[4:6, :5] = 3
    return t


def hud_end(point_left):
    t = np.zeros((8, 8), np.uint8)
    for r, c in ((2, 7), (3, 5), (4, 3), (5, 1)):
        t[r, c:] = 3
    return t if point_left else t[:, ::-1]


def lv():
    t = np.zeros((8, 8), np.uint8)
    t[2, 0] = t[5, 0] = 3
    blit(t, art("1000/1000/1000/1000/1000/1111"), 3, 1)
    return t


def bracket():
    t = np.zeros((8, 8), np.uint8)
    t[1, 2:7] = 3; t[1:7, 2] = 3
    return t


def number_sign():
    t = np.zeros((8, 8), np.uint8)
    blit(t, art(SMALL["N"]), 0, 1)
    blit(t, art("010/101/010/000/111"), 5, 1)
    return t


@drawer("font/font_battle_extra.png")
def font_battle_extra(rel, a):
    under, raised = np.zeros((8, 8), np.uint8), np.zeros((8, 8), np.uint8)
    under[6:8, 1:7] = 3; raised[3:5, 1:7] = 3
    row = [bar_left()] + [bar(k) for k in range(9)] + [bar_right(False), bar_right(True), lv(), hud_end(True),
                                                        small_text("t", "o", 1, 1)]
    row += [small_text("H", "P", 1, 1), bracket(), small_text("I", "D", 1, 1), number_sign(), glyph("dots"),
            under, raised, hud_end(False)] + FRAME + [None]
    return sheet(row, a["w"], a["h"])


@drawer("battle/battle_hud_1.png")
def battle_hud_1(rel, a):
    return sheet([bar_right(True), lv(), hud_end(True)], a["w"], a["h"])


@drawer("battle/battle_hud_2.png")
def battle_hud_2(rel, a):
    return sheet([hud_v(), hud_corner(True), glyph("dots")], a["w"], a["h"])


@drawer("battle/battle_hud_3.png")
def battle_hud_3(rel, a):
    return sheet([hud_h(), hud_corner(False), hud_end(False)], a["w"], a["h"])


@drawer("font/AB.png")
def ab(rel, a):
    out = np.zeros((16, 8), np.uint8)
    out[:8] = bold("A"); out[8:] = bold("B")
    return out


@drawer("font/P.png")
def p_tile(rel, a):
    return bold("P")


@drawer("font/ED.png")
def ed(rel, a):
    return small_text("E", "D", 1, 1)
