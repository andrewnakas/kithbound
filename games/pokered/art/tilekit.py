"""Small raster kit for drawing our own tiles and objects.

    c = C(16, 16)                 # pixels; shades 0 white .. 3 black
    c.rect(0, 0, 16, 8, 1)        # x0, y0, x1, y1 (exclusive), shade
    c.frame(...)  c.hline(y, x0, x1, s)  c.vline(x, y0, y1, s)  c.line(x0, y0, x1, y1, s)
    c.ellipse(cx, cy, rx, ry, s, outline=3)   c.poly([(x, y), ...], s, outline=3)
    c.pat(x0, y0, x1, y1, fn)     # fn(x, y) -> shade or None
    c.blob(mask, tone)            # outlined, top-left lit solid (trees, rocks, posts)
    c.put("..#/.#.", x, y)        # text art, ' ' is transparent
    c.text("GYM", x, y, s)        # our 5x7 font
    put(T, c, [[0x40, 0x41], [0x50, 0x51]])   # cut into tiles T[index]

A tileset module fills T = {tile number: 8x8 array}; see ts_overworld.py.
"""
import numpy as np

from games.pokered import drawn
from games.pokered.art import CH


class C:
    def __init__(self, w, h, fill=0):
        self.a = np.full((h, w), fill, np.uint8)
        self.h, self.w = h, w

    def rect(self, x0, y0, x1, y1, s):
        self.a[max(y0, 0):max(y1, 0), max(x0, 0):max(x1, 0)] = s
        return self

    def frame(self, x0, y0, x1, y1, s, fill=None):
        if fill is not None:
            self.rect(x0, y0, x1, y1, fill)
        self.rect(x0, y0, x1, y0 + 1, s); self.rect(x0, y1 - 1, x1, y1, s)
        self.rect(x0, y0, x0 + 1, y1, s); self.rect(x1 - 1, y0, x1, y1, s)
        return self

    def hline(self, y, x0, x1, s):
        return self.rect(x0, y, x1, y + 1, s)

    def vline(self, x, y0, y1, s):
        return self.rect(x, y0, x + 1, y1, s)

    def px(self, x, y, s):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = s
        return self

    def line(self, x0, y0, x1, y1, s):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), s)
        return self

    def grid(self):
        return np.mgrid[0:self.h, 0:self.w]

    def emask(self, cx, cy, rx, ry):
        y, x = self.grid()
        return ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0

    def pmask(self, pts):
        y, x = self.grid()
        x, y = x + 0.5, y + 0.5
        m = np.zeros((self.h, self.w), bool)
        n = len(pts)
        for i in range(n):
            (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
            if ya == yb:
                continue
            cond = ((ya <= y) & (y < yb)) | ((yb <= y) & (y < ya))
            xi = xa + (y - ya) * (xb - xa) / (yb - ya)
            m ^= cond & (x < xi)
        return m

    def fill(self, mask, s, outline=None):
        self.a[mask] = s
        if outline is not None:
            d = drawn.depth_map(mask, edge_inside=False)
            self.a[mask & (d == 1)] = outline
        return self

    def ellipse(self, cx, cy, rx, ry, s, outline=None):
        return self.fill(self.emask(cx, cy, rx, ry), s, outline)

    def poly(self, pts, s, outline=None):
        return self.fill(self.pmask(pts), s, outline)

    def pat(self, x0, y0, x1, y1, fn):
        for y in range(max(y0, 0), min(y1, self.h)):
            for x in range(max(x0, 0), min(x1, self.w)):
                v = fn(x, y)
                if v is not None:
                    self.a[y, x] = v
        return self

    def blob(self, mask, tone=1.3, bevel=1.0, edge_inside=False):
        """Outlined solid lit from the top left; tone 0..3 is the body shade."""
        d = drawn.depth_map(mask, edge_inside=edge_inside)
        soft = drawn.blur(mask, 2)
        gy, gx = np.gradient(soft)
        t = tone - bevel * np.clip((gx + gy) * 2.2, -1, 1) * (d <= 3)
        out = np.zeros_like(self.a)
        out[t >= 0.5] = 1; out[t >= 1.5] = 2; out[t >= 2.5] = 3
        out[mask & (d == 1)] = 3
        self.a[mask] = out[mask]
        return self

    def put(self, rows, x, y):
        if isinstance(rows, str):
            rows = rows.strip("\n").split("\n") if "\n" in rows else rows.split("/")
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != " ":
                    self.px(x + i, y + j, CH[ch])
        return self

    def text(self, s, x, y, shade=3, gap=1):
        from games.pokered.art.font import G
        for ch in s:
            rows = G[ch].split("/")
            for j, r in enumerate(rows):
                for i, c in enumerate(r):
                    if c == "1":
                        self.px(x + i, y + j, shade)
            x += 5 + gap
        return self

    def paste(self, other, x, y, mask=None):
        src = other.a if isinstance(other, C) else np.asarray(other)
        h, w = src.shape
        for j in range(h):
            for i in range(w):
                if mask is None or mask[j, i]:
                    self.px(x + i, y + j, src[j, i])
        return self

    def tile(self, tx, ty):
        return self.a[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8].copy()


def T8(rows):
    """One 8x8 tile from text art."""
    return C(8, 8).put(rows, 0, 0).a


def tex(fn, w=8, h=8):
    """Tile from a function fn(x, y) -> shade."""
    return C(w, h).pat(0, 0, w, h, fn).a


def put(T, c, layout):
    """Cut canvas c into 8x8 tiles; layout[row][col] = tile number or None."""
    for ty, row in enumerate(layout):
        for tx, n in enumerate(row):
            if n is not None:
                T[n] = c.tile(tx, ty)


def checker(a, b):
    return lambda x, y: a if (x + y) % 2 == 0 else b


def fallback(walkable):
    """Tile for a number nobody drew yet: dotted floor or hatched block."""
    if walkable:
        return tex(lambda x, y: 1 if (x % 4 == 1 and y % 4 == 1) else 0)
    return tex(lambda x, y: 3 if x == 0 or y == 0 else (2 if (x + y) % 3 == 0 else 1))


def build_sheet(T, spec, walk=(), name=""):
    """T -> tileset picture; undrawn tiles get the fallback (and are counted)."""
    w, h = spec["w"], spec["h"]
    out = np.zeros((h, w), np.uint8)
    blank = set(spec.get("blank", []))
    missing = []
    for i in range((w // 8) * (h // 8)):
        if i in blank:
            continue
        t = T.get(i)
        if t is None:
            missing.append(i)
            t = fallback(i in walk)
        out[(i // 16) * 8:(i // 16) * 8 + 8, (i % 16) * 8:(i % 16) * 8 + 8] = t
    if missing:
        print(f"  {name}: {len(missing)} tiles not drawn yet: " + " ".join(f"{m:02X}" for m in missing[:40]))
    return out
