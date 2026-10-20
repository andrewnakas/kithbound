"""KITHBOUND people kit, part 2: outfit details, face extras and held props.

Each helper returns a layer function f(s) for a Person s (see k_people_kit), so a
character is a parameter dict plus a list of these layers.
"""
import math

from games.pokered.art.k_people_kit import _edge


def _c(s):
    r = s.r
    if r["kind"] == "bust":
        return r["tx"], r["neck"][1], 56
    return r["tx"], r["neck"][1], r.get("low", 36)


# ---------------------------------------------------------------- outfit (on the torso)
def vneck(depth=7, c=None):
    def fn(s):
        f = s.f; x, y, _ = _c(s); k = depth * (s.r["rx"] / 8.5)
        c_ = s.p.get("skin", 0) if c is None else c
        m = f.P([(x - 3.5 * s.u, y - 1), (x + 3.5 * s.u, y - 1), (x - 0.5, y + k)]) & s.body
        f.part(m, c_, shadow=False)
    return fn


def lapels(inner=0, depth=14, tie=None, open_=True):
    """Open jacket: a shirt triangle with lapel edges (and an optional tie)."""
    def fn(s):
        f = s.f; x, y, low = _c(s); k = depth * (s.r["rx"] / 8.5); w = 4.5 * s.u
        m = f.P([(x - w, y - 1), (x + w, y - 1), (x + 0.5, y + k)]) & s.body
        f.part(m, inner, shadow=False)
        if tie is not None:
            f.part(f.P([(x - 1.0 * s.u, y), (x + 1.4 * s.u, y), (x + 1.6 * s.u, y + k * 0.8), (x + 0.2, y + k * 0.95), (x - 1.2 * s.u, y + k * 0.8)]) & m, tie, shadow=False)
        f.line([(x - w - 1.5, y), (x - 1.5, y + k * 0.75)]); f.line([(x + w + 1.5, y), (x + 2.5, y + k * 0.75)])
        if open_:
            f.line([(x + 0.5, y + k), (x + 0.5, low)])
    return fn


def zipline(c=3, x_off=0.5):
    def fn(s):
        f = s.f; x, y, low = _c(s)
        f.line([(x + x_off, y + 1), (x + x_off, low)], c)
    return fn


def buttons(n=3, x_off=0.5, gap=4, c=3):
    def fn(s):
        f = s.f; x, y, low = _c(s)
        for i in range(n):
            f.px(x + x_off, y + 4 + i * gap * s.u, c)
    return fn


def belt(dy=None, c=3, buckle=True):
    def fn(s):
        f = s.f; x, y, low = _c(s)
        yy = (low - 3 if s.r["kind"] == "full" else 50) if dy is None else y + dy
        f.part(s.body & (f.Y >= yy) & (f.Y < yy + 2.2 * s.u), c, shadow=False)
        if buckle:
            f.part(f.R(x - 1.5 * s.u, yy - 0.5, x + 2 * s.u, yy + 2.6 * s.u), 0 if c >= 2 else 3, shadow=False)
    return fn


def stripes(c=2, gap=3, region=None, dirn=(0, 1)):
    def fn(s):
        f = s.f; m = s.body & ~_edge(s.body)
        if region is not None:
            m &= region(s)
        f.stripes(m, c, gap=gap, dirn=dirn)
    return fn


def sash(c=3, w=2.2, rev=False):
    def fn(s):
        f = s.f; x, y, low = _c(s); sw = s.r["sw"] * s.p.get("build", 1)
        a, b = ((x - sw, y + 2), (x + sw, low - 2)) if not rev else ((x + sw, y + 2), (x - sw, low - 2))
        f.part(f.cap([a, b], w * s.u) & s.body, c, shadow=False)
    return fn


def emblem(rows, dx=-5, dy=9):
    def fn(s):
        x, y, _ = _c(s)
        s.f.stamp(rows, x + dx * s.u, y + dy * s.u)
    return fn


def apron(c=1, top=8):
    def fn(s):
        f = s.f; x, y, low = _c(s)
        hw = s.r["sw"] * s.p.get("build", 1) * 0.6
        m = f.P([(x - hw * 0.7, y + top), (x + hw * 0.7, y + top), (x + hw, low + 1), (x - hw, low + 1)])
        if s.r["kind"] == "full":
            m = f.P([(x - hw * 0.8, y + top * 0.5), (x + hw * 0.8, y + top * 0.5), (x + hw * 1.4, low + 9), (x - hw * 1.4, low + 9)])
        f.part(m, c)
        f.line([(x - hw * 0.7, y + top), (x - 4, y)]); f.line([(x + hw * 0.7, y + top), (x + 5, y)])
    return fn


def pads(c=2, size=1.0):
    """Shoulder plates / epaulettes."""
    def fn(s):
        f = s.f
        (lx, ly), (rx_, ry) = s.shoulders()
        for x, y in ((rx_, ry), (lx, ly)):
            f.part(f.E(x, y - 2.5 * s.u, 5.5 * size * s.u, 3.3 * size * s.u) & (f.Y < y + 0.5 * s.u), c)
    return fn


def coat_tails(c=None, length=10):
    """Long coat hanging below the waist (full-body figures; a 'pre' layer)."""
    def fn(s):
        f = s.f; x, y, low = _c(s); sw = s.r["sw"] * s.p.get("build", 1)
        m = f.P([(x - sw, low - 6), (x + sw, low - 6), (x + sw + 3, low + length), (x - sw - 2, low + length)])
        f.part(m, s.p.get("top", 1) if c is None else c)
        f.line([(x + 0.5, low - 2), (x + 0.5, low + length - 1)])
    return fn


def cape(c=3, wide=1.0, low=None):
    def fn(s):
        f = s.f; x, y, lo = _c(s); sw = s.r["sw"] * s.p.get("build", 1)
        bot = (low or (57 if s.r["kind"] == "bust" else s.r["foot"] + 2))
        m = f.P([(x - sw * 0.9, y + 1), (x + sw * 0.9, y + 1), (x + sw * (1.25 + 0.4 * wide), bot), (x - sw * (1.0 + 0.3 * wide), bot)])
        f.part(m, c)
    return fn


def collar_high(c=None, h=4):
    def fn(s):
        f = s.f; r = s.r; cx = r["cx"] + 1; w = 4.6 * s.u
        y1 = r["neck"][1] + 1.5
        f.part(f.P([(cx - w, y1 - h * s.u), (cx + w + 1, y1 - h * s.u - 1), (cx + w + 2, y1 + 1), (cx - w - 1, y1 + 1)]), s.p.get("top", 1) if c is None else c)
    return fn


def scarf(c=1, tail=True, side=1):
    def fn(s):
        f = s.f; r = s.r; cx = r["cx"] + 1; y1 = r["neck"][1]; u = s.u
        f.part(f.E(cx, y1, 6.5 * u, 2.8 * u), c)
        if tail:
            f.part(f.cap([(cx + 3 * u * side, y1 + 1), (cx + 5 * u * side, y1 + 7 * u), (cx + 4 * u * side, y1 + 12 * u)], 1.8 * u, 1.6 * u), c)
    return fn


def strap(c=3, rev=False, w=1.2):
    def fn(s):
        f = s.f; x, y, low = _c(s); sw = s.r["sw"] * s.p.get("build", 1)
        a, b = ((x + sw - 3, y + 1), (x - sw + 1, low)) if not rev else ((x - sw + 3, y + 1), (x + sw - 1, low))
        f.part(f.cap([a, b], w * s.u) & s.body, c, shadow=False)
    return fn


def necklace(c=3, pendant=None):
    def fn(s):
        f = s.f; r = s.r; cx = r["cx"] + 1; y1 = r["neck"][1]; u = s.u
        f.line([(cx - 4 * u, y1 + 0.5), (cx - 1, y1 + 4 * u), (cx + 1, y1 + 4 * u), (cx + 4 * u, y1 + 0.5)], c)
        if pendant:
            f.stamp(pendant, cx, y1 + 5.5 * u)
    return fn


# ---------------------------------------------------------------- head / face extras
def glasses(kind="round", c=3):
    def fn(s):
        f = s.f; e1, e2, ey = s.eyepos; u = s.u
        if kind == "round":
            for e in (e1, e2):
                f.part(f.ring(e, ey, 2.7 * u, 1.0), c, line=None, shadow=False)
            f.line([(e1 + 2.4 * u, ey - 0.8), (e2 - 2.4 * u, ey - 0.8)], c)
        elif kind == "shades":
            for e in (e1, e2):
                f.part(f.E(e, ey, 2.6 * u, 1.8 * u), 3, line=None, shadow=False, hl=False)
            f.line([(e1, ey - 1), (e2, ey - 1)], 3)
        elif kind == "square":
            for e in (e1, e2):
                m = f.R(e - 2.4 * u, ey - 1.8 * u, e + 2.4 * u, ey + 2 * u)
                f.a[_edge(m)] = c
            f.line([(e1 + 2.4 * u, ey - 1), (e2 - 2.4 * u, ey - 1)], c)
        f.line([(e2 + 2.4 * u, ey - 1), (s.r["cx"] + s.r["rx"] * 0.45, ey)], c)
    return fn


def goggles(on="forehead", c=2):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        y = cy - ry * 0.55 if on == "forehead" else s.eyepos[2]
        f.part(f.R(cx - rx * 1.02, y - 1.0 * u, cx + rx * 1.05, y + 1.2 * u) & f.E(cx, cy, rx * 1.1, ry * 1.1), 3, line=None, hl=False)
        for e in (cx - 4.3 * u, cx + 1.6 * u):
            f.part(f.E(e, y, 2.6 * u, 2.3 * u), c)
            f.px(e - 0.8 * u, y - 0.8 * u, 0)
    return fn


def monocle():
    def fn(s):
        f = s.f; e1, e2, ey = s.eyepos
        f.part(f.ring(e2, ey, 2.8 * s.u, 1.0), 3, line=None, shadow=False)
        f.line([(e2 + 1.5 * s.u, ey + 2.5 * s.u), (e2 + 3 * s.u, ey + 9 * s.u)], 3)
    return fn


def mustache(kind="curl", c=None):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        c_ = s.p.get("hairc", 2) if c is None else c
        mx, my = cx - 2.6 * u, cy + 4.4 * u
        if kind == "curl":
            m = f.E(mx, my, 3.4 * u, 1.3 * u) | f.cap([(mx - 3 * u, my), (mx - 4.6 * u, my - 1.6 * u)], 0.8 * u) | f.cap([(mx + 3 * u, my), (mx + 4.6 * u, my - 1.6 * u)], 0.8 * u)
        elif kind == "thick":
            m = f.E(mx, my + 0.3, 3.6 * u, 1.6 * u)
        else:
            m = f.E(mx, my, 3.0 * u, 1.0 * u)
        f.part(m, c_, shadow=False)
    return fn


def beard(kind="full", c=None):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        c_ = s.p.get("hairc", 2) if c is None else c
        if kind == "full":
            m = s.headmask & (f.Y > cy + 2.5 * u) & ~f.E(cx - 2.6 * u, cy + 5.9 * u, 2.6 * u, 1.2 * u)
            m |= f.E(cx - 1.5 * u, cy + ry * 0.95, rx * 0.75, ry * 0.45)
        elif kind == "bushy":
            m = s.headmask & (f.Y > cy + 2.0 * u) & ~f.E(cx - 2.6 * u, cy + 5.9 * u, 2.4 * u, 1.0 * u)
            m |= f.E(cx - 1.0 * u, cy + ry * 1.05, rx * 0.95, ry * 0.6)
            for a in (-0.7, -0.2, 0.3, 0.75):
                m |= f.E(cx + a * rx, cy + ry * 1.45, 2.0 * u, 2.0 * u)
        elif kind == "goatee":
            m = f.E(cx - 2.6 * u, cy + ry * 0.98, 2.2 * u, 2.4 * u)
        elif kind == "braided":
            m = s.headmask & (f.Y > cy + 3 * u) & ~f.E(cx - 2.6 * u, cy + 5.9 * u, 2.4 * u, 1.0 * u)
            m |= f.cap([(cx - 2 * u, cy + ry), (cx - 2.5 * u, cy + ry * 1.9)], 2.2 * u, 1.4 * u)
        elif kind == "stubble":
            m = s.headmask & (f.Y > cy + 3.5 * u) & ~_edge(s.headmask)
            f.dither(m, 1)
            return
        f.part(m, c_, shadow=c_ < 2)
        if kind in ("full", "bushy", "braided"):
            f.line([(cx - 4.4 * u, cy + 5.8 * u), (cx - 0.8 * u, cy + 5.8 * u)], 3)
    return fn


def mask_lower(c=2):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        m = s.headmask & (f.Y > cy + 2.6 * u)
        m |= f.P([(cx - rx * 1.1, cy + 2.6 * u), (cx + rx * 0.4, cy + 2.6 * u), (cx + rx * 0.3, cy + ry + 1)]) & s.headmask
        f.part(m, c, shadow=False)
        f.part(f.cap([(cx + rx * 0.6, cy + 3 * u), (cx + rx * 1.5, cy + 5 * u), (cx + rx * 1.4, cy + 9 * u)], 1.2 * u, 0.8 * u), c)
    return fn


def visor_mask(c=3):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        m = s.headmask & (f.Y > cy - 1.6 * u) & (f.Y < cy + 3.4 * u) & (f.X < cx + rx * 0.4)
        f.part(m, c, line=3, hl=True)
        e1, e2, ey = s.eyepos
        f.stamp(".-", e1, ey); f.stamp(".-", e2, ey)
    return fn


def scar(c=3):
    def fn(s):
        e1, e2, ey = s.eyepos; u = s.u
        s.f.line([(e2 + 0.5 * u, ey - 3.5 * u), (e2 + 2.5 * u, ey + 3.5 * u)], c)
    return fn


def bandaid():
    def fn(s):
        cx, cy, rx, ry = s.head(); u = s.u
        s.f.stamp("####/#..#/####", cx - 3.4 * u, cy + 3.4 * u)
    return fn


def gem(c=3):
    def fn(s):
        cx, cy, rx, ry = s.head(); u = s.u
        s.f.stamp(" # /#.#/ # ", cx - 1.6 * u, cy - 3.2 * u)
    return fn


def earring(c=3):
    def fn(s):
        cx, cy, rx, ry = s.head(); u = s.u
        s.f.stamp(" # /#.#/ # ", cx + rx * 0.4, cy + 5 * u)
    return fn


def headset():
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        f.part(f.ring(cx + 0.5, cy - 0.5, rx * 1.15, 1.6 * u) & (f.Y < cy) & (f.X > cx - rx * 0.4), 3, line=None, hl=False)
        f.part(f.E(cx + rx * 0.45, cy + 1.6 * u, 2.6 * u, 3.2 * u), 2)
        f.line([(cx + rx * 0.3, cy + 4 * u), (cx - rx * 0.4, cy + 6.5 * u)], 3)
        f.px(cx - rx * 0.45, cy + 6.5 * u, 3); f.px(cx - rx * 0.55, cy + 6.5 * u, 3)
    return fn


def flower_crown():
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        for i, a in enumerate(range(200, 345, 24)):
            t = math.radians(a)
            x, y = cx + math.cos(t) * rx * 1.02, cy - 1 * u + math.sin(t) * ry * 0.85
            f.part(f.E(x, y, 2.3 * u, 2.1 * u), 0 if i % 2 == 0 else 1)
            f.px(x, y, 3 if i % 2 == 0 else 2)
    return fn


def circlet(c=2, horns=True):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        f.part(f.R(cx - rx * 1.02, cy - 0.62 * ry, cx + rx * 0.9, cy - 0.42 * ry) & f.E(cx, cy, rx * 1.08, ry * 1.08), c)
        if horns:
            for x0, x1 in ((-0.6, -1.3), (0.5, 1.2)):
                f.part(f.P([(cx + x0 * rx - 1.5 * u, cy - 0.6 * ry), (cx + x1 * rx, cy - 1.6 * ry), (cx + x0 * rx + 1.5 * u, cy - 0.6 * ry)]), c)
    return fn


def ears_hood(c=1):
    """Creature-ear hood (kith fan)."""
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        for x0, x1 in ((-0.7, -1.2), (0.5, 1.15)):
            f.part(f.P([(cx + x0 * rx - 2.4 * u, cy - 0.85 * ry), (cx + x1 * rx, cy - 1.75 * ry), (cx + x0 * rx + 2.6 * u, cy - 0.95 * ry)]), c)
            f.part(f.P([(cx + x0 * rx - 0.8 * u, cy - 0.95 * ry), (cx + x1 * rx * 0.95, cy - 1.45 * ry), (cx + x0 * rx + 1.0 * u, cy - 1.0 * ry)]), 2, line=None, shadow=False)
    return fn


def veil(c=1):
    def fn(s):
        f = s.f; cx, cy, rx, ry = s.head(); u = s.u
        m = f.P([(cx - rx * 1.1, cy - ry * 0.4), (cx - rx * 0.3, cy - ry * 1.3), (cx + rx * 1.1, cy - ry * 1.2), (cx + rx * 1.8, cy + ry * 1.9),
                 (cx + rx * 0.4, cy + ry * 1.8)]) & ~f.E(cx - rx * 0.2, cy + ry * 0.25, rx * 0.95, ry * 0.95)
        f.part(m, c)
    return fn


# ---------------------------------------------------------------- held props
def H(s, side="front"):
    return s.p["hands"][side]


def snare(side="front", r=3.4, dx=-1.5, dy=-2):
    """Our capture device: a ball with a slot band and a ring latch."""
    def fn(s):
        f = s.f; x, y = H(s, side); x += dx * s.u; y += dy * s.u; rr = r * s.u
        f.part(f.E(x, y, rr), 0)
        f.part(f.E(x, y, rr) & (f.Y < y - 0.3 * rr), 2, line=None, shadow=False)
        f.a[_edge(f.E(x, y, rr))] = 3
        f.line([(x - rr, y - 0.3 * rr), (x + rr, y - 0.3 * rr)], 3)
        f.stamp("###/#.#/###", x, y - 0.25 * rr)
    return fn


def rod(side="front", tip=(-26, -26), c=2, line_to=None):
    def fn(s):
        f = s.f; x, y = H(s, side)
        tx, ty = x + tip[0] * s.u, y + tip[1] * s.u
        f.part(f.cap([(x + 2, y + 4), (tx, ty)], 0.9 * s.u, 0.5), c, line=3)
        if line_to:
            f.line([(tx, ty), (tx + line_to[0], ty + line_to[1])], 3)
            f.part(f.E(tx + line_to[0], ty + line_to[1] + 2, 2.2 * s.u, 1.5 * s.u), 1)
    return fn


def staff(side="front", top=(-2, -30), bottom=(2, 26), c=2, head=None, w=1.2):
    def fn(s):
        f = s.f; x, y = H(s, side)
        a, b = (x + top[0] * s.u, y + top[1] * s.u), (x + bottom[0] * s.u, y + bottom[1] * s.u)
        f.part(f.cap([b, a], w * s.u), c)
        if head:
            head(s, a)
        f.part(f.E(x, y, s.r["hand"] * 1.05, s.r["hand"]), s.p.get("glove", s.p.get("skin", 0)))
    return fn


def held(rows_fn):
    """Generic: rows_fn(s, x, y) draws something at the front hand, then the hand on top."""
    def fn(s):
        x, y = H(s, "front")
        rows_fn(s, x, y)
    return fn


def rehand(side="front"):
    def fn(s):
        f = s.f; x, y = H(s, side)
        f.part(f.E(x, y, s.r["hand"] * 1.05, s.r["hand"]), s.p.get("glove", s.p.get("skin", 0)))
    return fn
