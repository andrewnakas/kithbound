"""KITHBOUND overworld figure kit (our own chibi design, no retail outlines).

A figure is painted in layers on a 16x16 frame. Shades on sprites: 0 transparent,
1 light (skin / white cloth), 2 grey, 3 black. After painting, the silhouette gets a
black line, and two touching parts of the same shade get a dividing line on the part
painted later, so cloth and skin read apart without hand-placed lines.

Our proportions: a wide round head (12 px) set on a short body; the face sits low in
the head with eyes on row 6; the torso is a narrow block with stubby arms; feet are
split by a gap. Styles are dicts (see STYLE_KEYS below).
"""
import numpy as np

YY, XX = np.mgrid[0:16, 0:16]


def E(cx, cy, rx, ry):
    return ((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2 <= 1.0


def R(x0, y0, x1, y1):
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def mirror(m):
    return m[:, ::-1]


class Fig:
    def __init__(self):
        self.s = np.zeros((16, 16), np.uint8)
        self.id = np.zeros((16, 16), np.int32)
        self.n = 0
        self.noline = set()

    def paint(self, m, shade, line=True):
        if not np.any(m):
            return self
        self.n += 1
        self.s[m] = shade
        self.id[m] = self.n
        if not line:
            self.noline.add(self.n)
        return self

    def erase(self, m):
        self.s[m] = 0
        self.id[m] = 0
        return self

    def finish(self):
        s, ids = self.s.copy(), self.id
        inside = ids > 0
        out = s.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb_in = np.zeros_like(inside)
            nb_id = np.zeros_like(ids)
            nb_s = np.zeros_like(s)
            ys = slice(max(dy, 0), 16 + min(dy, 0)); yd = slice(max(-dy, 0), 16 + min(-dy, 0))
            xs = slice(max(dx, 0), 16 + min(dx, 0)); xd = slice(max(-dx, 0), 16 + min(-dx, 0))
            nb_in[yd, xd] = inside[ys, xs]
            nb_id[yd, xd] = ids[ys, xs]
            nb_s[yd, xd] = s[ys, xs]
            out[inside & ~nb_in] = 3
            sep = inside & nb_in & (nb_id != ids) & (nb_s == s) & (ids > nb_id)
            sep &= ~np.isin(ids, list(self.noline)) if self.noline else True
            out[sep] = 3
        self.s = out
        return self

    def px(self, x, y, v):
        if 0 <= x < 16 and 0 <= y < 16:
            self.s[y, x] = v
        return self

    def put(self, rows, x0=0, y0=0):
        """Overlay text art after finish: ' ' keeps, '.' clears to 0, '-' 1, '+' 2, '#' 3,
        'o' clears only where empty-figure... (kept simple)."""
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == " ":
                    continue
                self.px(x0 + i, y0 + j, {".": 0, "-": 1, "+": 2, "#": 3}[c])
        return self


# ---- people ------------------------------------------------------------------------------

def _head(f, st, facing, dy):
    """Hair, face and headwear. Returns the eye row."""
    hs = st.get("hair_s", 3)
    kind = st.get("hair", "short")
    small = st.get("kid", False)
    rx = 5.4 if small else 6.0
    cy = 4.5 + dy + (1.0 if small else 0)
    ry = 4.0 if small else 4.6
    head = E(8, cy, rx, ry)
    top = int(np.nonzero(head.any(1))[0][0])
    bot = int(np.nonzero(head.any(1))[0][-1])
    ey = bot - 3
    skin = 1
    # things behind the head
    if kind in ("long", "twin", "pony", "braid") and facing != "side":
        if kind == "long":
            f.paint((R(2, top + 3, 5, bot + 4) | R(11, top + 3, 14, bot + 4)) & ~R(0, 16, 16, 16), hs)
        if kind == "twin":
            f.paint(E(1.8, cy + 2.5, 1.8, 2.6) | E(14.2, cy + 2.5, 1.8, 2.6), hs)
        if kind == "pony" and facing == "up":
            f.paint(R(7, bot - 1, 9, bot + 4), hs)
    if kind in ("long", "pony", "braid") and facing == "side":
        if kind == "long":
            f.paint(R(9, top + 3, 13, bot + 4), hs)
        else:
            f.paint(E(13.2, cy + 1.5, 2.2, 2.0) | R(12, int(cy), 14, bot + 3), hs)
    if kind == "twin" and facing == "side":
        f.paint(E(12.5, cy + 2.5, 1.8, 2.6), hs)
    if kind == "hood":
        f.paint(E(8, cy + 0.6, rx + 0.8, ry + 0.9), st.get("hood_s", 2))
    # the head itself
    hair_cover = head.copy()
    if kind == "bald":
        f.paint(head, skin)
        if facing != "up" or True:
            side = (head & (YY >= ey - 1) & ((XX <= 3) | (XX >= 12)))
            if facing == "side":
                side = head & (YY >= ey - 1) & (XX >= 10)
            f.paint(side, st.get("fringe_s", hs))
    else:
        f.paint(head, hs)
    # face
    if facing == "down" and kind != "bald":
        face = E(8, ey + 0.8, 4.6, 3.3) & (YY >= ey - 2) & head
        if kind in ("cap", "hat", "helmet", "bandana", "beanie", "beret", "band", "tophat", "chef"):
            face = E(8, ey + 0.6, 4.8, 3.6) & (YY >= ey - 2) & head
        if kind == "fringe":
            face &= ~((YY == ey - 2) & (XX <= 8))
        f.paint(face, skin, line=hs != 1)
    elif facing == "side" and kind != "bald":
        face = E(6.3, ey + 0.8, 4.2, 3.3) & (YY >= ey - 2) & head & (XX <= 9)
        f.paint(face, skin, line=hs != 1)
    elif facing == "side" and kind == "bald":
        pass
    # headwear
    hat_s = st.get("hat_s", 2)
    if kind == "cap":
        if facing == "down":
            f.paint(head & (YY < ey - 2), hat_s)
            f.paint(R(3, ey - 2, 13, ey - 1) & ~E(8, ey - 9, 1, 1), 3)
        elif facing == "up":
            f.paint(head & (YY < ey - 1), hat_s)
        else:
            f.paint(head & (YY < ey - 2), hat_s)
            f.paint(R(0, ey - 2, 6, ey - 1), 3)
    if kind == "beanie":
        f.paint(head & (YY < ey - 1), hat_s)
        f.paint(head & (YY == ey - 2), 1 if hat_s != 1 else 2)
        f.paint(E(8 if facing != "side" else 9, top + 0.2, 1.6, 1.4), 1)
    if kind == "hat":                                  # wide brim
        brim = R(0, ey - 2, 16, ey - 1) & E(8, ey - 1.5, 8.4, 1.2)
        if facing == "side":
            brim = R(0, ey - 2, 14, ey - 1)
        f.paint(head & (YY < ey - 2), hat_s)
        f.paint(brim, 3 if hat_s != 3 else 2)
    if kind == "tophat":
        f.paint(R(4, 0, 12, ey - 2) if facing != "side" else R(5, 0, 12, ey - 2), hat_s)
        f.paint(R(2, ey - 2, 14, ey - 1) if facing != "side" else R(1, ey - 2, 14, ey - 1), 3)
        f.paint((R(4, ey - 4, 12, ey - 3) if facing != "side" else R(5, ey - 4, 12, ey - 3)), 1 if hat_s != 1 else 2, line=False)
    if kind == "chef":
        f.paint(E(8, 2, 5.5, 2.6) | R(4, 2, 12, ey - 1), 1)
        f.paint(R(4, ey - 2, 12, ey - 1) if facing != "side" else R(4, ey - 2, 12, ey - 1), 1)
    if kind == "helmet":
        f.paint(head & (YY < ey - 1), hat_s)
        f.paint(head & (YY == ey - 2), 3)
        if facing != "up":
            f.paint(R(7, top, 9, ey - 2) & head, 1)
    if kind == "bandana":
        f.paint(head & (YY >= ey - 3) & (YY <= ey - 2), hat_s)
        if facing == "side":
            f.paint(R(12, ey - 2, 15, ey + 1) & ~R(14, ey, 15, ey + 1), hat_s)
        if facing == "up":
            f.paint(R(7, ey - 2, 9, ey + 1), hat_s)
    if kind == "band":
        f.paint(head & (YY == ey - 2), hat_s)
    if kind == "beret":
        b = E(7 if facing != "side" else 9, top + 1.2, 5.5, 2.2)
        f.paint(b, hat_s)
        f.paint(R(7 if facing != "side" else 9, top - 1, 8 if facing != "side" else 10, top + 1) & ~b, 3)
    if kind in ("short", "fringe", "spiky", "long", "pony", "twin", "braid", "bun") and facing == "down":
        for x in st.get("bangs", (3, 12)):
            f.paint(R(x, ey - 2, x + 1, ey - 1) & head, hs, line=False)
    if kind in ("short", "fringe", "spiky", "long", "pony", "twin", "braid", "bun") and facing == "side":
        for x in st.get("side_bangs", (3, 4)):
            f.paint(R(x, ey - 2, x + 1, ey - 1) & head, hs, line=False)
    if kind == "spiky":
        for x in range(3, 13, 3):
            f.paint(R(x, top - 1, x + 1, top + 1) & (YY >= 0), hs)
    if kind == "bun":
        f.paint(E(8 if facing != "side" else 10, top + 0.3, 2.2, 1.8), hs)
    if kind == "crest":
        f.paint(R(7, 0, 9, top + 2), 3)
    if kind == "crown":
        f.paint(R(4, top - 1, 12, top + 2) & ((XX % 3 != 0) | (YY >= top)), st.get("hat_s", 1))
    # features
    if facing == "down":
        for ex in (6, 9):
            f.px(ex, ey, 3).px(ex, ey + 1, 3)
        if st.get("glasses"):
            for x, v in zip(range(4, 12), (3, 1, 3, 3, 3, 3, 1, 3)):
                f.px(x, ey, v)
            f.px(6, ey, 3); f.px(9, ey, 3); f.px(5, ey, 1); f.px(10, ey, 1)
            f.px(6, ey + 1, 1); f.px(9, ey + 1, 1); f.px(5, ey + 1, 3); f.px(10, ey + 1, 3)
        if st.get("goggles"):
            for x in range(3, 13):
                f.px(x, ey - 1, 3)
            f.px(5, ey, 1); f.px(10, ey, 1); f.px(6, ey, 1); f.px(9, ey, 1)
        if st.get("beard"):
            for y in range(ey + 2, bot + 2):
                for x in range(4, 12):
                    if head[min(y, 15), x] or y == bot + 1 and 6 <= x <= 9:
                        f.px(x, y, st.get("beard_s", 2))
            f.px(7, ey + 2, 3); f.px(8, ey + 2, 3)
        if st.get("mustache"):
            for x in range(6, 10):
                f.px(x, ey + 2, 3)
        if st.get("blush"):
            f.px(4, ey + 2, 2); f.px(11, ey + 2, 2)
        if st.get("smile"):
            f.px(7, ey + 3, 2); f.px(8, ey + 3, 2)
        if st.get("mask"):
            for y in (ey + 2, ey + 3):
                for x in range(4, 12):
                    if head[y, x]:
                        f.px(x, y, st.get("mask_s", 3))
    elif facing == "side":
        f.px(4, ey, 3).px(4, ey + 1, 3)
        if st.get("glasses"):
            for x in range(2, 7):
                f.px(x, ey, 3)
        if st.get("goggles"):
            for x in range(2, 10):
                f.px(x, ey - 1, 3)
            f.px(4, ey, 1)
        if st.get("beard"):
            for y in range(ey + 2, bot + 2):
                for x in range(2, 9):
                    if head[min(y, 15), x]:
                        f.px(x, y, st.get("beard_s", 2))
        if st.get("mustache"):
            f.px(2, ey + 2, 3); f.px(3, ey + 2, 3)
        if st.get("blush"):
            f.px(5, ey + 2, 2)
        if st.get("mask"):
            for y in (ey + 2, ey + 3):
                for x in range(2, 9):
                    if head[y, x]:
                        f.px(x, y, st.get("mask_s", 3))
    return bot


BODY = {
    ("down", 0): ["...##TTTTTT##...",
                  "...#A#TTTT#A#...",
                  "...#A#TTTT#A#...",
                  "...#H#TTTT#H#...",
                  "...##LLLLLL##...",
                  "....#L#..#L#....",
                  "....###..###...."],
    ("down", 1): ["...##TTTTTT##...",
                  "...#A#TTTT#A#...",
                  "...#A#TTTT#H#...",
                  "...#H#TTTT###...",
                  "...##LLLLLL#....",
                  "....###..#L#....",
                  ".........###...."],
    ("side", 0): [".....#TTTTT#....",
                  ".....#T#A#T#....",
                  ".....#T#A#T#....",
                  ".....#T#H#T#....",
                  "......#LLLL#....",
                  "......#LLL#.....",
                  ".....#####......"],
    ("side", 1): [".....#TTTTT#....",
                  ".....#A#TTT#....",
                  "....#A#TTTT#....",
                  "....#H#TTTT#....",
                  ".....#LLLLL#....",
                  "....#L#...#L#...",
                  "...###....###..."],
}
BODY[("up", 0)] = BODY[("down", 0)]
BODY[("up", 1)] = BODY[("down", 1)]

# row overrides per garment (row index 0 = sprite row 9)
WEAR = {
    "coat": {("down", 0): {4: "...##TTTTTT##...", 5: "....#TTTTTT#....", 6: "....##L##L##...."},
             ("down", 1): {4: "...##TTTTTT#....", 5: "....#TTTTTT#....", 6: "....###..#L#...."},
             ("side", 0): {4: ".....#TTTTT#....", 5: ".....#TTTTT#....", 6: ".....######....."},
             ("side", 1): {4: ".....#TTTTT#....", 5: "....#LTTTTT#....", 6: "...###...###...."}},
    "robe": {("down", 0): {4: "...#TTTTTTTT#...", 5: "...#TTTTTTTT#...", 6: "...##########..."},
             ("down", 1): {4: "...#TTTTTTTT#...", 5: "...#TTTTTTTT#...", 6: "...##########..."},
             ("side", 0): {4: "....#TTTTTT#....", 5: "....#TTTTTTT#...", 6: "....#########..."},
             ("side", 1): {4: "....#TTTTTT#....", 5: "...#TTTTTTTT#...", 6: "...##########..."}},
    "dress": {("down", 0): {3: "..##H#KKKK#H##..", 4: "..#KKKKKKKKKK#..", 5: "..############..", 6: "....#S#..#S#...."},
              ("down", 1): {3: "..##H#KKKK####..", 4: "..#KKKKKKKKKK#..", 5: "..############..", 6: "....#S#..###...."},
              ("side", 0): {3: "....#T#H#TT#....", 4: "...#KKKKKKKK#...", 5: "...##########...", 6: "......#S#S#....."},
              ("side", 1): {3: "...#H#KKKKK#....", 4: "...#KKKKKKKK#...", 5: "...##########...", 6: "....#S#...#S#..."}},
    "skirt": {("down", 0): {4: "..#LLLLLLLLLL#..", 5: "..############..", 6: "....#S#..#S#...."},
              ("down", 1): {4: "..#LLLLLLLLLL#..", 5: "..############..", 6: "....#S#..###...."},
              ("side", 0): {4: "...#LLLLLLLL#...", 5: "...##########...", 6: "......#S#S#....."},
              ("side", 1): {4: "...#LLLLLLLL#...", 5: "...##########...", 6: "....#S#...#S#..."}},
    "shorts": {("down", 0): {5: "....#S#..#S#...."},
               ("down", 1): {5: "....###..#S#...."},
               ("side", 0): {5: "......#SSS#....."},
               ("side", 1): {5: "....#S#...#S#..."}},
}
for _w in WEAR.values():
    if ("down", 0) in _w:
        _w.setdefault(("up", 0), _w[("down", 0)])
        _w.setdefault(("up", 1), _w[("down", 1)])


def body_rows(st, facing, walk):
    rows = list(BODY[(facing, int(walk))])
    for k, v in WEAR.get(st.get("wear", "pants"), {}).get((facing, int(walk)), {}).items():
        rows[k] = v
    return rows


def stamp_body(out, st, facing, walk):
    top_s = st.get("top_s", 2)
    cmap = {"T": top_s, "A": st.get("arm_s", top_s), "H": 3 if st.get("gloves") else 1,
            "L": st.get("leg_s", 2), "S": 1, "K": st.get("skirt_s", top_s), "#": 3}
    y0 = 9
    for j, r in enumerate(body_rows(st, facing, walk)):
        for i, c in enumerate(r):
            if c != ".":
                out[y0 + j, i] = cmap[c]
    return out


def _extras_before(f, st, facing, walk):
    ex = st.get("extras", ())
    if "cape" in ex:
        if facing == "up":
            f.paint(R(4, 9, 12, 16) | R(3, 11, 13, 16), st.get("cape_s", 3))
        elif facing == "down":
            f.paint(R(2, 9, 14, 15), st.get("cape_s", 3))
        else:
            f.paint(R(8, 9, 14, 16) & ~R(13, 9, 14, 11), st.get("cape_s", 3))
    if "pack" in ex and facing == "side":
        f.paint(R(10, 9, 14, 14), st.get("pack_s", 2))
    if "tail" in ex and facing == "side":
        f.paint(R(11, 12, 15, 14), 2)
    if "rod" in ex:
        if facing == "down":
            f.paint(R(13, 4, 14, 13), 2)
        elif facing == "side":
            f.paint(R(1, 3, 2, 13), 2)
    if "guitar" in ex and facing == "down":
        pass


# overlays drawn on the finished frame: (extra, facing) -> (x, y, rows); ' ' keeps,
# 'T' is the top shade, 'P' the pack shade, other chars as in text art
OVER = {
    ("pack", "up"): (4, 9, ["  ######  ", "  #PPPP#  ", "  #P##P#  ", "  #PPPP#  ", "  ######  "]),
    ("pack", "down"): (6, 9, ["#  #", "#  #"]),
    ("tie", "down"): (7, 9, ["##", "##", " #"]),
    ("collar", "down"): (5, 9, ["#-##-#"]),
    ("scarf", "down"): (3, 9, ["##----##", "  #--#  ", "   #-#  "]),
    ("scarf", "up"): (3, 9, ["##----##"]),
    ("scarf", "side"): (5, 9, ["#----###", "     #-#", "     ###"]),
    ("apron", "down"): (6, 10, ["----", "----", "----", "#--#"]),
    ("belt", "down"): (5, 12, ["######"]),
    ("belt", "up"): (5, 12, ["######"]),
    ("belt", "side"): (5, 12, ["##   ##"]),
    ("stripes", "down"): (6, 10, ["----", "    ", "----"]),
    ("stripes", "up"): (6, 10, ["----", "    ", "----"]),
    ("emblem", "down"): (6, 10, ["-#", "#-"]),
    ("emblem", "up"): (6, 10, ["-#", "#-"]),
    ("buttons", "down"): (7, 10, ["#", " ", "#"]),
    ("badge", "down"): (6, 10, ["-"]),
    ("cane", "down"): (12, 10, ["###", "#+#", " #+#", " #+#", " #+#", " ###"]),
    ("cane", "side"): (1, 10, ["###", "#+#", "#+#", "#+#", "#+#", "###"]),
    ("bag", "down"): (12, 10, ["###", "#+#", "#+#", "###"]),
    ("bag", "side"): (9, 10, ["####", "#++#", "####"]),
    ("bag", "up"): (1, 10, ["###", "#+#", "#+#", "###"]),
    ("book", "down"): (5, 11, ["######", "#-#--#", "######"]),
    ("tray", "down"): (11, 6, [" ### ", " #-# ", "#####", "#+++#", "#####"]),
    ("tray", "side"): (0, 6, [" ### ", " #-# ", "#####", "#+++#", "#####"]),
    ("staff", "down"): (12, 2, [" ### ", "#---#", " ### ", "  #  ", "  #  ", "  #  ", "  #  ",
                                "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "]),
    ("staff", "side"): (0, 2, [" ###", "#---#", " ###", "  # ", "  # ", "  # ", "  # ", "  # ",
                               "  # ", "  # ", "  # ", "  # ", "  # ", "  # "]),
    ("rod", "down"): (12, 3, ["   #", "  # ", "  # ", " #  ", " #  ", " #  ", "#   ", "#   "]),
    ("rod", "side"): (0, 4, ["#   ", "#   ", " #  ", " #  ", " #  ", "  # ", "  # "]),
    ("helmetlamp", "down"): (7, 1, ["--"]),
    ("guitar", "down"): (9, 10, ["  ###", " #++#", "#++# ", "###  "]),
    ("guitar", "side"): (2, 10, ["###  ", "#++# ", " #++#", "  ###"]),
    ("clip", "down"): (5, 11, ["######", "#----#", "######"]),
    ("medal", "down"): (7, 10, ["--", "--"]),
    ("cross", "down"): (6, 10, [" -- ", "----", " -- "]),
    ("cross", "up"): (6, 10, [" -- ", "----", " -- "]),
    ("whistle", "down"): (8, 10, ["#-"]),
    ("vest", "down"): (6, 10, ["-  -", "-  -", "-  -"]),
    ("spots", "down"): (6, 10, ["- ", "  ", " -"]),
}


def _extras_after(f, st, facing, walk):
    for ex in st.get("extras", ()):
        o = OVER.get((ex, facing))
        if not o:
            continue
        x0, y0, rows = o
        if walk and ex in ("cane", "bag", "tray", "staff", "rod") and facing != "side":
            y0 -= 1
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == " ":
                    continue
                v = {"T": st.get("top_s", 2), "P": st.get("pack_s", 2)}.get(c)
                if v is None:
                    v = {".": 0, "-": 1, "+": 2, "#": 3}[c]
                f.px(x0 + i, y0 + j, v)


def person(st, facing, walk=False):
    f = Fig()
    _extras_before(f, st, facing, walk)
    _head(f, st, facing, st.get("dy", 0))
    f.finish()
    out = f.s
    stamp_body(out, st, facing, walk)
    f.s = out
    _extras_after(f, st, facing, walk)
    _feat_after(f, st, facing)
    return f.s


def _feat_after(f, st, facing):
    pass


FACING = ["down", "up", "side", "down", "up", "side"]


def person_sheet(st, h):
    frames = []
    for n in range(h // 16):
        frames.append(person(st, FACING[n % 6], walk=n >= 3))
    return np.vstack(frames)
