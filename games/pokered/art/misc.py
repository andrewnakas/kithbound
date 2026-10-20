"""Small UI / title / symbol sheets, all drawn here (no retail pixel is read).

Emotes, party balls, THE END, overworld bits, Pokedex frame, Town Map, trainer card,
copyright lines, title lettering, slot machine frame and the Super Game Boy borders.

Spinner arrows: each tile is one diagonal stroke of a chevron.  Tileset tiles (facility
$20 $21 $30 $31, gym $4C $3C $4D $3D) are the strokes  \\ / / \\ ; `spinner_stroke(kind, 0)`
gives the resting frame for the tileset drawer, the sheet here holds frame 1.
"""
import numpy as np

from games.pokered.art import art, blit, drawer, sheet
from games.pokered.art.font import G, bold, glyph
from games.pokered.art.text import S3, _glyph, ptext, width
from games.pokered.art.tilekit import C

# ---- narrow lettering (our own): 4x7 capitals, 3x7 lower case ---------------------------

CAP4 = {
    "A": "0110/1001/1001/1111/1001/1001/1001", "C": "0111/1000/1000/1000/1000/1000/0111",
    "D": "1110/1001/1001/1001/1001/1001/1110", "E": "1111/1000/1000/1110/1000/1000/1111",
    "I": "111/010/010/010/010/010/111", "N": "1001/1101/1101/1011/1011/1001/1001",
    "O": "0110/1001/1001/1001/1001/1001/0110", "P": "1110/1001/1001/1110/1000/1000/1000",
    "R": "1110/1001/1001/1110/1010/1001/1001", "T": "111/010/010/010/010/010/010",
    "U": "1001/1001/1001/1001/1001/1001/0110", "Y": "101/101/101/010/010/010/010",
    " ": "00",
}
LOW3 = {
    "a": "000/000/110/001/011/101/011", "c": "000/000/011/100/100/100/011",
    "d": "001/001/011/101/101/101/011", "e": "000/000/010/101/111/100/011",
    "i": "1/0/1/1/1/1/1", "n": "000/000/110/101/101/101/101",
    "o": "000/000/010/101/101/101/010", "r": "000/000/101/110/100/100/100",
    "s": "000/000/011/100/010/001/110", "t": "010/010/111/010/010/010/001",
    "u": "000/000/101/101/101/101/011", ".": "0/0/0/0/0/0/1", " ": "00",
}


def _rows(ch, table):
    if table is not None and ch in table:
        return table[ch].split("/")
    return _glyph(ch, False)


def ntext(c, s, x, y, shade=3, table=None, gap=1):
    """Text with glyphs from `table` (CAP4 / LOW3 / both merged) else the 5x7 font."""
    for ch in s:
        rows = _rows(ch, table)
        for j, r in enumerate(rows):
            for i, v in enumerate(r):
                if v == "1":
                    c.px(x + i, y + j, shade)
        x += len(rows[0]) + gap
    return x


def nwidth(s, table=None, gap=1):
    return sum(len(_rows(ch, table)[0]) + gap for ch in s) - gap


NARROW = {**CAP4, **LOW3}


def tiles_of(a):
    a = a.a if isinstance(a, C) else a
    return [a[y:y + 8, x:x + 8].copy() for y in range(0, a.shape[0], 8) for x in range(0, a.shape[1], 8)]


def bold_at(c, ch, x, y, shade=3):
    for dx in (0, 1):
        for j, r in enumerate(G[ch].split("/")):
            for i, v in enumerate(r):
                if v == "1":
                    c.px(x + i + dx, y + j, shade)


def disc(c, cx, cy, r, s, outline=3):
    return c.ellipse(cx, cy, r, r, s, outline)


# ---- emotes -------------------------------------------------------------------------------

def bubble():
    c = C(16, 16)
    m = np.zeros((16, 16), bool)
    m[1:12, 1:15] = True
    m[1, 1] = m[1, 14] = m[11, 1] = m[11, 14] = False
    m[12, 5:9] = True; m[13, 5:8] = True; m[14, 5:7] = True; m[15, 5] = True
    c.fill(m, 1, outline=3)
    c.a[11, 6:8] = 1
    return c


@drawer("emotes/happy.png")
def emote_happy(rel, a):
    c = bubble()
    c.put(" # /# #", 4, 4).put(" # /# #", 9, 4)           # eyes
    c.put("#    #/ #### ", 5, 7)                           # smile
    return c.a


@drawer("emotes/question.png")
def emote_question(rel, a):
    c = bubble()
    bold_at(c, "?", 5, 3)
    return c.a


@drawer("emotes/shock.png")
def emote_shock(rel, a):
    c = bubble()
    c.rect(7, 3, 9, 8, 3); c.rect(7, 9, 9, 11, 3)
    return c.a


# ---- battle: party status balls (normal, status, fainted, empty slot) ---------------------

def ball(kind):
    c = C(8, 8)
    if kind == "empty":
        disc(c, 3.5, 4.5, 2.6, 0, outline=2)
        c.a[3:6, 2:5] = 0
        return c.a
    m = c.emask(3.5, 4.5, 3.3, 3.3)
    c.fill(m, 1, outline=3)
    if kind == "normal":
        top = m & (c.grid()[0] < 4) & (c.a == 1)
        c.a[top] = 2
        c.hline(4, 1, 6, 3)
        c.px(3, 4, 1)
    elif kind == "status":
        inner = m & (c.a == 1)
        y, x = c.grid()
        c.a[inner & ((x + y) % 2 == 0)] = 2
    elif kind == "fainted":
        for k in range(-2, 3):
            c.px(3 + k, 4 + k, 3); c.px(3 + k, 4 - k, 3)
    return c.a


@drawer("battle/balls.png")
def balls(rel, a):
    return sheet([ball(k) for k in ("normal", "status", "fainted", "empty")], a["w"], a["h"])


# ---- credits: THE END, one tall letter per 8x16 column -------------------------------------

@drawer("credits/the_end.png")
def the_end(rel, a):
    out = np.zeros((a["h"], a["w"]), np.uint8)
    for n, ch in enumerate("THEND"):
        g = art(G[ch], 5, 7)
        tall = np.repeat(g, 2, axis=0)                     # 5 x 14
        big = np.zeros((14, 6), np.uint8)
        big[:, :5] = tall
        big[:, 1:] = np.maximum(big[:, 1:], tall)
        blit(out, big, n * 8 + 1, 1)
    return out


# ---- overworld bits ---------------------------------------------------------------------

@drawer("overworld/battle_transition.png")
def battle_transition(rel, a):
    return np.full((a["h"], a["w"]), 3, np.uint8)


@drawer("overworld/shadow.png")
def shadow(rel, a):
    """Top-left quarter of the hop shadow (the game mirrors it into an oval)."""
    c = C(8, 8)
    c.ellipse(8, 8, 7, 3.6, 3)
    return c.a


def spinner_stroke(kind, frame=0):
    """One chevron stroke. kind: 0 '\\' (inside upper right), 1 '/' (inside lower right),
    2 '/' (inside upper left), 3 '\\' (inside lower left). frame 0 = resting, 1 = lit."""
    c = C(8, 8)
    back = kind in (0, 3)
    for y in range(8):
        for x in range(8):
            d = (x - y) if back else (x + y - 7)
            side = {0: d, 1: d, 2: -d, 3: -d}[kind]          # > 0 on the inside of the chevron
            if frame == 0:
                s = 3 if abs(d) <= 1 else (1 if 1 < side <= 3 else 0)
            else:
                s = 2 if abs(d) <= 1 else (3 if 1 < side <= 2 else (1 if -3 <= side < -1 else 0))
            c.px(x, y, s)
    return c.a


@drawer("overworld/spinners.png")
def spinners(rel, a):
    return sheet([spinner_stroke(k, 1) for k in range(4)], a["w"], a["h"])


@drawer("overworld/heal_machine.png")
def heal_machine(rel, a):
    mon = C(8, 8)
    mon.rect(1, 1, 7, 5, 2).hline(2, 2, 5, 1)
    b = C(8, 8)
    disc(b, 4, 4.5, 2.6, 1, outline=3)
    b.hline(4, 2, 6, 3).px(3, 3, 2).px(4, 3, 2)
    return sheet([mon.a, b.a], a["w"], a["h"])


# ---- Pokedex frame tiles ($60..$71) ----------------------------------------------------------

@drawer("pokedex/pokedex.png")
def pokedex(rel, a):
    f = C(24, 24, 2)                                        # a 3x3 tile box: the screen frame
    f.rect(2, 2, 22, 22, 3).rect(4, 4, 20, 20, 0)
    for x, y in ((2, 2), (21, 2), (2, 21), (21, 21)):
        f.px(x, y, 2)
    f.hline(4, 4, 20, 1).vline(4, 4, 20, 1)
    ft = tiles_of(f)                                        # 0 UL 1 top 2 UR 3 left 5 right 6 LL 7 bottom 8 LR
    foot = C(8, 8).put("..##/..##/.##./.#..", 0, 0).a
    inch = C(8, 8).put(".##.##/.##.##/##.##./#..#..", 0, 0).a
    dot = C(8, 8).put("##/##", 3, 3).a
    hl = C(8, 8).rect(0, 3, 8, 5, 3).a
    box = C(8, 8).rect(0, 3, 8, 5, 3).ellipse(4, 4, 3.4, 3.4, 1, outline=3).a
    left = ft[3].copy(); left[3:5, 4:] = 3
    right = ft[5].copy(); right[3:5, :4] = 3
    notch = ft[7].copy(); notch[2:4, 3:5] = 3
    vl = C(8, 8).rect(3, 0, 5, 8, 3).a
    vbox = C(8, 8).rect(3, 0, 5, 8, 3).ellipse(4, 4, 3.4, 3.4, 1, outline=3).a
    return sheet([foot, inch, dot, ft[0], ft[1], ft[2], ft[3], ft[5], left, box, right, hl,
                  ft[6], notch, ft[8], ft[7], vbox, vl], a["w"], a["h"])


# ---- Town Map ------------------------------------------------------------------------------

def _sea(x, y):
    return 0 if (y % 4 == 1 and (x + (y // 4) * 4) % 8 in (1, 2, 3)) else 1


def _land(x, y):
    return 1 if ((x % 4 == 1 and y % 4 == 1) or (x % 4 == 3 and y % 4 == 3)) else 2


def tm_tile(kind):
    c = C(8, 8)
    if kind == "blank":
        return c.a
    if kind == "sea":
        return c.pat(0, 0, 8, 8, _sea).a
    if kind == "land":
        return c.pat(0, 0, 8, 8, _land).a
    if kind == "route":
        return c.a
    if kind == "route_v":
        return c.pat(0, 0, 8, 8, _land).rect(2, 0, 6, 8, 0).vline(1, 0, 8, 3).vline(6, 0, 8, 3).a
    if kind == "route_h":
        return c.pat(0, 0, 8, 8, _land).rect(0, 2, 8, 6, 0).hline(1, 0, 8, 3).hline(6, 0, 8, 3).a
    if kind == "city_land":
        c.pat(0, 0, 8, 8, _land)
        return disc(c, 4, 4, 3.2, 0, outline=3).a
    if kind == "city":
        return c.frame(0, 0, 8, 8, 3, fill=0).rect(2, 2, 6, 6, 2).rect(3, 3, 5, 5, 0).a
    if kind == "spot":
        disc(c, 4, 4, 2.4, 0, outline=3)
        return c.a
    if kind in ("sw", "se", "ne", "nw"):                    # the corner that is land
        def f(x, y):
            u = x if kind in ("se", "ne") else 7 - x
            v = y if kind in ("sw", "se") else 7 - y
            d = u + v - 7
            return _land(x, y) if d > 0 else (3 if d == 0 else _sea(x, y))
        return c.pat(0, 0, 8, 8, f).a
    c.pat(0, 0, 8, 8, _sea)                                 # sea routes: dotted
    if kind == "sea_h":
        c.rect(1, 3, 3, 5, 3).rect(5, 3, 7, 5, 3)
    elif kind == "sea_v":
        c.rect(3, 1, 5, 3, 3).rect(3, 5, 5, 7, 3)
    else:
        c.rect(3, 3, 5, 5, 3)
    return c.a


@drawer("town_map/town_map.png")
def town_map(rel, a):
    order = ["blank", "route_v", "route_h", "city_land", "sea", "city", "land", "route",
             "sw", "se", "ne", "nw", "spot", "sea_dot", "sea_h", "sea_v"]
    return sheet([tm_tile(k) for k in order], a["w"], a["h"])


@drawer("town_map/town_map_cursor.png")
def town_map_cursor(rel, a):
    c = C(16, 16)
    for x0, x1 in ((0, 6), (10, 16)):
        c.rect(x0, 0, x1, 2, 3).rect(x0, 14, x1, 16, 3)
    for y0, y1 in ((0, 6), (10, 16)):
        c.rect(0, y0, 2, y1, 3).rect(14, y0, 16, y1, 3)
    c.px(0, 0, 0).px(15, 0, 0).px(0, 15, 0).px(15, 15, 0)
    return c.a


@drawer("town_map/up_arrow.png")
def up_arrow(rel, a):
    return C(8, 8).put("...##.../..####../.######./########/...##.../...##...", 0, 1).a


@drawer("town_map/mon_nest_icon.png")
def mon_nest_icon(rel, a):
    """A paw print."""
    return C(8, 8).put(".#.##.#./.#.##.#./#......#/#.####.#/..####../.######./.######./..#..#..", 0, 0).a


# ---- trainer card ---------------------------------------------------------------------------

@drawer("trainer_card/badge_numbers.png")
def badge_numbers(rel, a):
    ts = []
    for d in "12345678":
        c = C(8, 8)
        c.rect(0, 0, 8, 8, 1)
        g = art(G[d], 5, 7)
        c.hline(7, 0, 8, 2).vline(7, 0, 8, 2)
        blit(c.a, g, 1, 0, transparent=0)
        ts.append(c.a)
    return sheet(ts, a["w"], a["h"])


@drawer("trainer_card/blank_leader_names.png")
def blank_leader_names(rel, a):
    return np.zeros((a["h"], a["w"]), np.uint8)             # the names are blank in this version


@drawer("trainer_card/circle_tile.png")
def circle_tile(rel, a):
    c = C(8, 8)
    disc(c, 4, 4, 2.6, 2, outline=3)
    return c.px(3, 3, 0).a


@drawer("trainer_card/trainer_info.png")
def trainer_info(rel, a):
    bgf = lambda x, y: 0 if (x % 4 == 0 and y % 4 == 0) or (x % 4 == 2 and y % 4 == 2) else 1
    f = C(24, 24).pat(0, 0, 24, 24, bgf)
    f.rect(2, 2, 22, 22, 3).rect(3, 3, 21, 21, 0).frame(4, 4, 20, 20, 2)
    for x, y in ((2, 2), (21, 2), (2, 21), (21, 21)):
        f.px(x, y, 1)
    t = tiles_of(f)
    bg = C(8, 8).pat(0, 0, 8, 8, bgf).a
    return sheet([t[7], t[5], t[0], t[1], t[2], t[3], t[6], t[8], bg], a["w"], a["h"])


# ---- copyright lines, company names -----------------------------------------------------

def _line(w, s, table=None, x=0, y=0, shade=3):
    c = C(w, 8)
    ntext(c, s, x, y, shade, table)
    return c


# splash/copyright.png and title/gamefreak_inc.png: drawn only by art/a_brand.py (our own credit lines).


@drawer("splash/gamefreak_presents.png")
def gamefreak_presents(rel, a):
    ts = [bold(ch) for ch in "GAMEFRK"]                     # sprites: one letter per tile
    c = C(48, 8)
    ptext(c, "PRESENTS", 0, 0)
    return sheet(ts + tiles_of(c), a["w"], a["h"])


@drawer("splash/gamefreak_logo.png")
def gamefreak_logo(rel, a):
    """Our own emblem: a cut gem on a small stand."""
    c = C(16, 24)
    gem = [(8, 1), (14, 7), (8, 19), (2, 7)]
    c.poly(gem, 1, outline=3)
    c.poly([(8, 3), (12, 7), (8, 16), (8, 3)], 2)
    c.line(3, 7, 13, 7, 3).line(8, 2, 5, 7, 3).line(8, 2, 11, 7, 3).line(5, 7, 8, 18, 3).line(11, 7, 8, 18, 3)
    c.rect(4, 20, 12, 22, 3).rect(2, 22, 14, 23, 3).hline(20, 5, 11, 2)
    return c.a


# ---- title screen --------------------------------------------------------------------------

@drawer("title/red_version.png")
def red_version(rel, a):
    c = C(a["w"], 8)
    ntext(c, "R", 0, 0, 3, CAP4); ntext(c, "ed", 5, 0)        # tiles 0-1
    ptext(c, "Version", 40, 0)                              # tiles 5-9
    return c.a


@drawer("title/blue_version.png")
def blue_version(rel, a):
    c = C(a["w"], 8)
    x = ptext(c, "Blue", 0, 0)
    ptext(c, "Version", a["w"] - width("Version"), 0)
    return c.a


def dilate(m, n=1):
    out = m.copy()
    for _ in range(n):
        p = np.pad(out, 1)
        out = np.zeros_like(m)
        for dy in range(3):
            for dx in range(3):
                out |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
    return out


def shift(m, dx, dy):
    out = np.zeros_like(m)
    out[dy:, dx:] = m[:m.shape[0] - dy, :m.shape[1] - dx]
    return out


def block_title(word, w, h, sx=3, sy=5, gap=2, y0=None):
    """Bold outlined block letters with a bevel and a drop shadow: our own lettering."""
    glyphs = []
    for ch in word:
        rows = "00010/00100/11111/10000/11110/10000/11111" if ch == "é" else G[ch]
        glyphs.append(np.kron(art(rows, 5, 7) > 0, np.ones((sy, sx), bool)))
    tw = sum(g.shape[1] for g in glyphs) + gap * (len(glyphs) - 1)
    th = 7 * sy
    x = (w - tw - 3) // 2 + 1
    y = (h - th - 3) // 2 if y0 is None else y0
    m = np.zeros((h, w), bool)
    for g in glyphs:
        m[y:y + th, x:x + g.shape[1]] |= g
        x += g.shape[1] + gap
    o = dilate(m)
    out = np.zeros((h, w), np.uint8)
    out[shift(o, 2, 2)] = 2
    out[o] = 3
    out[m] = 1
    return out


@drawer("title/pokemon_logo.png")
def pokemon_logo(rel, a):
    h, w = a["h"], a["w"]
    out = block_title("POKéMON", w, h, y0=5)
    c = C(w, h); c.a = out
    y = 47                                                  # a rule with a ball under the word
    c.rect(10, y, w - 10, y + 2, 3).hline(y + 2, 12, w - 8, 2)
    disc(c, w / 2, y + 1, 5.2, 1, outline=3)
    top = c.emask(w / 2, y + 1, 4, 4) & (c.grid()[0] < y)
    c.a[top & (c.a == 1)] = 2
    c.rect(w // 2 - 4, y, w // 2 + 4, y + 2, 3).rect(w // 2 - 1, y, w // 2 + 1, y + 2, 0)
    return c.a


# ---- slot machine frame -----------------------------------------------------------------

SLOT_MAP = """
00 00 00 00 00 02 03 04 05 00 00 06 07 08 09 00 00 00 00 00
01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01
0A 0E 0B 23 1C 1E 1F 1C 1C 1E 1F 1C 1C 1E 1F 1C 23 0A 0E 0B
0C 0F 0D 24 1D 20 21 1D 1D 20 21 1D 1D 20 21 1D 24 0C 0F 0D
0A 10 0B 23 16 17 17 16 16 17 17 16 16 17 17 16 23 0A 10 0B
0C 11 0D 24 16 17 17 16 16 17 17 16 16 17 17 16 24 0C 11 0D
0A 12 0B 23 16 17 17 16 16 17 17 16 16 17 17 16 23 0A 12 0B
0C 13 0D 24 16 17 17 16 16 17 17 16 16 17 17 16 24 0C 13 0D
0A 10 0B 23 16 17 17 16 16 17 17 16 16 17 17 16 23 0A 10 0B
0C 11 0D 24 16 17 17 16 16 17 17 16 16 17 17 16 24 0C 11 0D
0A 0E 0B 23 00 18 19 00 00 18 19 00 00 18 19 00 23 0A 0E 0B
0C 0F 0D 24 01 1A 1B 01 01 1A 1B 01 01 1A 1B 01 24 0C 0F 0D
"""


def parse_map(text, cols):
    rows = []
    for ln in text.strip("\n").split("\n"):
        toks = [t for t in (ln[i:i + 3] for i in range(0, len(ln), 3)) if t.strip()]
        names = [t.strip() for t in toks]
        if ".." in names:
            k = names.index("..")
            toks = toks[:k] + ["00 "] * (cols - len(toks) + 1) + toks[k + 1:]
        assert len(toks) == cols, (len(toks), ln)
        rows.append([(int(t[:2], 16), t[2:].strip()) for t in toks])
    return rows


def cut_map(c, rows, name=""):
    """Canvas + tilemap (tile, flip) -> {tile: picture}; reports tiles drawn two ways."""
    a = c.a if isinstance(c, C) else c
    T, bad = {}, set()
    for r, row in enumerate(rows):
        for col, (n, f) in enumerate(row):
            t = a[r * 8:r * 8 + 8, col * 8:col * 8 + 8]
            if f in ("h", "b"):
                t = t[:, ::-1]
            if f in ("v", "b"):
                t = t[::-1]
            if n in T:
                if not (T[n] == t).all():
                    bad.add(n)
            else:
                T[n] = t.copy()
    if bad:
        print(f"  {name}: tiles drawn inconsistently: " + " ".join(f"{b:02X}" for b in sorted(bad)))
    return T


SLOT_STRIP = [3, 0, 0, 1, 1, 2, 3, 2]


def slot_ball(c, x, y, lit):
    c.rect(x, y, x + 8, y + 16, 2)
    if lit:
        disc(c, x + 4, y + 8, 3.6, 0, outline=3)
        c.px(x + 5, y + 9, 1).px(x + 4, y + 10, 1).px(x + 5, y + 10, 1)
        for dx, dy in ((0, -6), (0, 5), (-4, -5), (3, -5), (-4, 4), (3, 4)):
            c.px(x + 4 + dx, y + 8 + dy, 0)
    else:
        disc(c, x + 4, y + 8, 3.6, 2, outline=3)
        c.px(x + 2, y + 6, 1).px(x + 3, y + 6, 1).px(x + 2, y + 7, 1)


def slots_canvas(version):
    c = C(160, 96, 2)
    for word, x0 in (("CREDIT", 40), ("PAYOUT", 88)):          # name plates in the header
        c.rect(x0, 0, x0 + 32, 8, 3)
        ntext(c, word, x0 + (32 - nwidth(word, CAP4)) // 2, 0, 0, CAP4)
        c.px(x0, 0, 2).px(x0 + 31, 0, 2)
    for i, s in enumerate(SLOT_STRIP):
        c.hline(8 + i, 0, 160, s)
    for side in (0, 136):                                     # pay line plates 3 2 1 2 3
        for k, d in enumerate("32123"):
            y = 16 + k * 16
            c.frame(side + 1, y + 1, side + 23, y + 15, 3, fill=1)
            c.hline(y + 2, side + 2, side + 22, 0)
            bold_at(c, d, side + 9, y + 4)
    for x in (24, 128):
        for k in range(5):
            slot_ball(c, x, 16 + k * 16, False)
    for col in (4, 7, 8, 11, 12, 15):                         # pillars between the reels
        x = col * 8
        c.rect(x, 16, x + 8, 80, 2).vline(x, 16, 80, 3).vline(x + 7, 16, 80, 3)
        c.vline(x + 3, 16, 80, 1)
    for col in (5, 9, 13):
        x = col * 8
        c.rect(x, 32, x + 16, 80, 0)                          # reel window (symbols are sprites)
        c.rect(x, 16, x + 16, 32, 3)                          # hood
        c.rect(x + 1, 18, x + 15, 30, 1).hline(18, x + 1, x + 15, 0)
        c.ellipse(x + 8, 24, 5, 3.6, 2 if version == "red" else 0, outline=3)
        c.hline(23, x + 6, x + 10, 1)
        c.rect(x, 80, x + 16, 88, 3)                          # tray
        c.rect(x + 1, 82, x + 15, 87, 1).hline(82, x + 1, x + 15, 0)
        for i in (3, 7, 11):
            c.rect(x + i, 84, x + i + 2, 86, 2)
    for i, s in enumerate(SLOT_STRIP):                        # foot trim under reels and pillars
        c.hline(88 + i, 32, 128, s)
    return c


def slots(version, a):
    c = slots_canvas(version)
    T = cut_map(c, parse_map(SLOT_MAP, 20), "slots")
    lit = C(8, 16)
    slot_ball(lit, 0, 0, True)
    T[0x14], T[0x15] = lit.a[:8], lit.a[8:]
    n = (a["w"] // 8) * (a["h"] // 8)
    return sheet([T.get(i) for i in range(n)], a["w"], a["h"])


@drawer("slots/red_slots_1.png")
def red_slots_1(rel, a):
    return slots("red", a)


@drawer("slots/blue_slots_1.png")
def blue_slots_1(rel, a):
    return slots("blue", a)


# ---- Super Game Boy borders -------------------------------------------------------------
# The whole 256x224 frame is drawn as one picture and cut into tiles by the tilemap
# (kept layout fact).  Only shades 1..3 are used outside the game window.

RED_MAP = """
10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11
20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21
10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11
20 30 31 31h30h52 52 52 52 52 52 52 52 52 16 12 13 14 52 52 52 52 52 52 52 52 52 30 31 31h30h21
10 30 31 31h30h01 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 0D 30 31 31h30h11
20 0E 0F 0Fh0Eh43 .. 43 0E 0F 0Fh0Eh21
10 34 35 36 1E 43 .. 43 38 39 3A 3B 11
20 44 45 46 47 43 .. 43 48 49 4A 4B 21
10 54 55 56 57 43 .. 43 58 59 5A 5B 11
20 1Eh52 37 1E 43 .. 43 1Eh52 52 1E 21
10 40 53 53 40h43 .. 43 40 53 53 40h11
20 50 51 51h50h43 .. 43 50 51 51h50h21
10 11 10 11 10 43 .. 43 11 10 11 10 11
20 21 20 21 20 43 .. 43 21 20 21 20 21
10 11 10 11 10 43 .. 43 11 10 11 10 11
20 0E 0F 0Fh0Eh43 .. 43 0E 0F 0Fh0Eh21
10 0E 0F 0Fh0Eh43 .. 43 0E 0F 0Fh0Eh11
20 38 39 3A 3B 43 .. 43 34 35 36 1E 21
10 30 31 31h30h43 .. 43 30 31 31h30h11
20 3C 3D 3E 32h43 .. 43 22 23 24 32h21
10 4C 4D 4E 4F 43 .. 43 25 26 27 28 11
20 5C 5D 5E 5F 43 .. 43 29 2A 2B 2C 21
10 32 2D 2E 2F 43 .. 43 32 17 18 19 11
20 40 53 53 40h3F 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 41 40 53 53 40h21
10 50 51 51h50h52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 50 51 51h50h11
20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21
10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11 10 11
20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21 20 21
"""

BLUE_MAP = """
5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A
3F 2C 2D 3F 3F 2Dh2Ch3F 3F 2Dh2Ch3F 3F 2C 2D 3F 3F 2Dh2Ch3F 3F 2Dh2Ch3F 3F 2C 2D 3F 3F 2Dh2Ch3F
3F 2E 2F 3F 3F 2Fh2Eh3F 3F 2Fh2Eh3F 3F 2E 2F 3F 3F 2Fh2Eh3F 3F 2Fh2Eh3F 3F 2E 2F 3F 3F 2Fh2Eh3F
5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av1B 17 18 19 1A 5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av
14 14 14 14 14 1F 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 0D 14 14 14 14 14
14h15 16 15h14 0F .. 0F 14 15 16 15h14
29h26 27 28 29 0F .. 0F 40 11 12 13 40h
35 36 37 38 39 0F .. 0F 20 21 22 23 20h
45 46 47 48 49 0F .. 0F 30 31 32 33 34
20v56 57 58 59 0F .. 0F 20v41 42 43 44
40v54 55 25 40b0F .. 0F 50 51 52 53 40b
14v15v16v15b14v0F .. 0F 14v15v16v15b14v
4Av4Av4Av4Av4Av0F .. 0F 4Av4Av4Av4Av4Av
01 01 01 01 01 0F .. 0F 01 01 01 01 01
01 01 01 01 01 0F .. 0F 01 01 01 01 01
4A 4A 4A 4A 4A 0F .. 0F 4A 4A 4A 4A 4A
14 15 16 15h14h0F .. 0F 14 15 16 15h14h
40 11 2Bv11h40h0F .. 0F 40 11 2Bv11h40h
20 3C 3D 3E 20h0F .. 0F 20 2A 0C 21h20h
4B 4C 4D 4E 4F 0F .. 0F 30 3A 10 0C 30h
5B 5C 5D 5E 5F 0F .. 0F 20v21v3A 24 20b
40v11v2Bh11b40b0F .. 0F 40v11v2B 11b40b
14v15v16v15b14b0F .. 0F 14v15v16v15b14b
14 14 14 14 14 1E 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 0E 14 14 14 14 14
5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A 5A
3F 2C 2D 3F 3F 2Dh2Ch3F 3F 2Dh2Ch3F 3F 2C 2D 3F 3F 2Dh2Ch3F 3F 2Dh2Ch3F 3F 2C 2D 3F 3F 2Dh2Ch3F
3F 2E 2F 3F 3F 2Fh2Eh3F 3F 2Fh2Eh3F 3F 2E 2F 3F 3F 2Fh2Eh3F 3F 2Fh2Eh3F 3F 2E 2F 3F 3F 2Fh2Eh3F
5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av5Av
"""


def window_frame(c, fill=2):
    """The ring of tiles around the 160x144 game window (tile cols 5..26, rows 4..23)."""
    x0, y0, x1, y1 = 40, 32, 216, 192
    c.rect(x0, y0, x1, y1, fill)
    c.frame(x0 + 2, y0 + 2, x1 - 2, y1 - 2, 1)
    c.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, 3)
    c.rect(x0 + 5, y0 + 5, x1 - 5, y1 - 5, 1)
    c.rect(x0 + 6, y0 + 6, x1 - 6, y1 - 6, fill)
    for x, y in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        c.px(x, y, 1)
    c.rect(x0 + 8, y0 + 8, x1 - 8, y1 - 8, 0)                # the window itself (tile 00)


def ic_drop(c, cx, cy, r, f, d):
    m = c.emask(cx, cy + r * 0.38, r * 0.62, r * 0.62) | c.pmask(
        [(cx - r * 0.55, cy + r * 0.2), (cx, cy - r), (cx + r * 0.55, cy + r * 0.2)])
    c.fill(m, f, outline=3)
    c.line(round(cx - r * 0.3), round(cy + r * 0.3), round(cx - r * 0.15), round(cy + r * 0.62), d)


def ic_flame(c, cx, cy, r, f, d):
    m = c.emask(cx, cy + r * 0.4, r * 0.6, r * 0.6) | c.pmask(
        [(cx - r * 0.6, cy + r * 0.4), (cx + r * 0.1, cy - r), (cx + r * 0.6, cy + r * 0.4)]) | c.pmask(
        [(cx - r * 0.6, cy + r * 0.5), (cx - r * 0.55, cy - r * 0.45), (cx, cy + r * 0.2)])
    c.fill(m, f, outline=3)
    c.fill(c.emask(cx + 0.5, cy + r * 0.52, r * 0.26, r * 0.34), d)


def ic_leaf(c, cx, cy, r, f, d):
    k = r * 1.15
    m = c.emask(cx, cy - k * 0.55, k, k) & c.emask(cx, cy + k * 0.55, k, k)
    c.fill(m, f, outline=3)
    c.line(round(cx - r * 0.55), round(cy), round(cx + r), round(cy), 3)
    for t in (-0.25, 0.2):
        c.line(round(cx + r * t), round(cy), round(cx + r * (t + 0.2)), round(cy - r * 0.25), d)
        c.line(round(cx + r * t), round(cy), round(cx + r * (t + 0.2)), round(cy + r * 0.25), d)


def ic_bolt(c, cx, cy, r, f, d):
    p = [(0.35, -1), (-0.5, 0.1), (-0.05, 0.1), (-0.6, 1), (0.55, -0.25), (0.1, -0.25), (0.6, -1)]
    c.poly([(cx + u * r, cy + v * r) for u, v in p], f, outline=3)


def letter_tile(ch, shade=1, back=2, y=0):
    c = C(8, 8, back)
    bold_at(c, ch, 1, y, shade)
    return c.a


def emblem_tile(back=2):
    c = C(8, 8, back)
    disc(c, 4, 4, 3.4, 1, outline=3)
    c.hline(4, 1, 7, 3)
    c.a[1:4, 1:7][c.a[1:4, 1:7] == 1] = 2
    return c.a


def red_canvas(word):
    def bg(x, y):
        u, v = x % 16, y % 16
        d = abs(u - 7.5) + abs(v - 7.5)
        if d <= 1:
            return 3
        if d <= 4:
            return 2
        return 2 if min(u, 15 - u) + min(v, 15 - v) <= 1 else 1
    c = C(256, 224).pat(0, 0, 256, 224, bg)
    P = 2
    c.rect(40, 24, 216, 32, P); c.rect(40, 192, 216, 200, P)        # strips above / below
    window_frame(c, P)
    for i, t in enumerate([emblem_tile(P)] + [letter_tile(ch, 1, P) for ch in word]):
        c.paste(t, (14 + i) * 8, 24)

    def base(x0, r0, r1):
        y0, y1 = r0 * 8, r1 * 8
        c.rect(x0, y0, x0 + 32, y1, P)
        c.vline(x0, y0, y1, 3).vline(x0 + 31, y0, y1, 3).vline(x0 + 1, y0, y1, 1).vline(x0 + 30, y0, y1, 1)

    def bar(x0, r):
        y = r * 8
        c.rect(x0, y, x0 + 32, y + 8, 1)
        c.hline(y, x0, x0 + 32, 3).hline(y + 7, x0, x0 + 32, 3).vline(x0, y, y + 8, 3).vline(x0 + 31, y, y + 8, 3)
        for k in range(4):
            c.rect(x0 + 3 + 8 * k, y + 3, x0 + 5 + 8 * k, y + 5, 2)

    def low(x0, r):                                           # 40 53 53 40h
        c.hline(r * 8 + 5, x0 + 2, x0 + 30, 1)

    def cap(x0, r):                                           # 50 51 51h 50h
        y = r * 8
        c.hline(y + 6, x0 + 1, x0 + 31, 1).hline(y + 7, x0, x0 + 32, 3)

    def orn(x0, r, n):
        for k in range(n):
            x, y = x0 + 3 + 8 * k, r * 8 + 3
            c.rect(x, y - 1, x + 2, y + 3, 1).rect(x - 1, y, x + 3, y + 2, 1).rect(x, y, x + 2, y + 2, 3)

    for x0, top, bottom in ((8, "A", "C"), (216, "B", "D")):
        base(x0, 3, 12)
        bar(x0, 3); bar(x0, 4)
        orn(x0, 6, 3 if top == "A" else 4)
        (ic_flame if top == "A" else ic_leaf)(c, x0 + 16, 64, 7, 1, 2)
        if top == "A":
            c.rect(x0 + 19, 75, x0 + 21, 77, 1)               # tile 37: a spark under the flame
        low(x0, 10); cap(x0, 11)
        base(x0, 15, 25)
        orn(x0, 17, 4 if top == "A" else 3)                   # the other block's top row
        bar(x0, 18)
        (ic_drop if bottom == "C" else ic_bolt)(c, x0 + 16, 168, 11, 1, 2)
        low(x0, 23); cap(x0, 24)
    return c


def blue_canvas(word):
    P = 2
    c = C(256, 224, P)
    for r in (1, 25):                                          # the two motif bands
        y = r * 8
        c.rect(0, y - 2, 256, y + 18, 1).hline(y - 2, 0, 256, 3).hline(y + 17, 0, 256, 3)
        for col, flip in ((1, 0), (5, 1), (9, 1), (13, 0), (17, 1), (21, 1), (25, 0), (29, 1)):
            m = C(16, 16, 1)
            ic_drop(m, 7, 8, 7, 2, 1)
            m.put("+.+/.+.", 12, 2)
            c.paste(m.a[:, ::-1] if flip else m.a, col * 8, y)
    window_frame(c, P)
    for i, t in enumerate([emblem_tile(P)] + [letter_tile(ch, 1, P, 1) for ch in word]):
        c.paste(t, (13 + i) * 8, 24)

    def crest(x0, r, flip):
        t = C(40, 8, P)
        t.rect(10, 3, 30, 8, 3).rect(11, 4, 29, 8, 1).rect(17, 1, 23, 4, 3).rect(18, 2, 22, 5, 1)
        c.paste(t.a[::-1] if flip else t.a, x0, r * 8)

    def box(x0, r):
        y0 = r * 8
        c.rect(x0 + 3, y0 + 3, x0 + 37, y0 + 37, 3).rect(x0 + 5, y0 + 5, x0 + 35, y0 + 35, 1)
        for x, y in ((x0 + 3, y0 + 3), (x0 + 36, y0 + 3), (x0 + 3, y0 + 36), (x0 + 36, y0 + 36)):
            c.px(x, y, P)
        for y in (y0 + 1, y0 + 35):                            # studs: top and bottom centre
            c.rect(x0 + 18, y, x0 + 22, y + 4, 3).rect(x0 + 19, y + 1, x0 + 21, y + 3, 1)
        for x in (x0 + 1, x0 + 35):                            # and the middle of each side
            c.rect(x, y0 + 18, x + 4, y0 + 22, 3).rect(x + 1, y0 + 19, x + 3, y0 + 21, 1)
        crest(x0, r - 1, False); crest(x0, r + 5, True)

    for x0 in (0, 216):
        for r in (6, 17):
            box(x0, r)
        y = 96                                                 # the label band between the boxes
        c.rect(x0, y + 6, x0 + 40, y + 26, 1).hline(y + 6, x0, x0 + 40, 3).hline(y + 25, x0, x0 + 40, 3)
        c.pat(x0, y + 8, x0 + 40, y + 24, lambda x, yy: 2 if (x % 8 in (3, 4) and yy % 8 in (3, 4)) else 1)
    ic_flame(c, 20, 68, 10, 2, 1)
    ic_bolt(c, 216 + 20, 68, 11, 2, 1)
    ic_drop(c, 20, 156, 10, 2, 1)
    ox, oy = 216 + 8, 17 * 8 + 8                               # a sash: only pieces that repeat
    for y in range(24):
        for x in range(24):
            d, s = x - y, x + y
            if abs(d) <= 3 and 5 <= s <= 41:
                edge = abs(d) == 3 or s in (5, 41)
                c.px(ox + x, oy + y, 3 if edge else 2)
    disc(c, ox + 12, oy + 12, 3.4, 1, outline=3)
    return c


def border(canvas, tilemap, a, name):
    T = cut_map(canvas, parse_map(tilemap, 32), name)
    n = (a["w"] // 8) * (a["h"] // 8)
    return sheet([T.get(i) for i in range(n)], a["w"], a["h"])


@drawer("sgb/red_border.png")
def red_border(rel, a):
    return border(red_canvas("RED"), RED_MAP, a, "red_border")


@drawer("sgb/blue_border.png")
def blue_border(rel, a):
    return border(blue_canvas("BLUE"), BLUE_MAP, a, "blue_border")
