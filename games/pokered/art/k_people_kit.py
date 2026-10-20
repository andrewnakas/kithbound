"""KITHBOUND people kit: a small parametric figure builder for battle portraits.

Everything is drawn in a 'design space' (56x56 for a portrait) and mapped to pixels by a
scale k and offset (ox, oy), so the same character can be drawn smaller (intro shrink).
Shades: 0 white, 1 light, 2 dark, 3 black.  Every part gets a black outline, a shadow band
on its right/bottom side (light comes from the top left) and is painted back to front.
"""
import math

import numpy as np


def _edge(m, open_bottom=False):
    p = np.pad(m, 1, constant_values=False)
    if open_bottom:
        p[-1, 1:-1] = m[-1]
    inner = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return m & ~inner


def _shift(m, dx, dy):
    """out[y, x] = m[y + dy, x + dx] (False outside)."""
    h, w = m.shape
    out = np.zeros_like(m)
    ys = slice(max(dy, 0), h + min(dy, 0)); yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0)); xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[yd, xd] = m[ys, xs]
    return out


class Fig:
    def __init__(s, w=56, h=56, k=1.0, ox=0.0, oy=0.0, open_bottom=True):
        s.w, s.h, s.k, s.ox, s.oy = w, h, k, ox, oy
        s.a = np.zeros((h, w), np.uint8)
        s.m = np.zeros((h, w), bool)
        yy, xx = np.mgrid[0:h, 0:w]
        s.X = (xx + 0.5 - ox) / k
        s.Y = (yy + 0.5 - oy) / k
        s.open_bottom = open_bottom
        s.info = {}

    def pose(s, ang=0.0, sx=1.0, sy=1.0, px=0.0, py=0.0, tx=0.0, ty=0.0):
        """Rotate (degrees, clockwise on screen) and squash the design space about (px, py),
        then move it by (tx, ty): design point -> pixel = M @ (x, y, 1)."""
        c, n = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        A = np.array([[c * sx, -n * sy], [n * sx, c * sy]]) * s.k
        p0 = np.array([px, py])
        b = np.array([s.ox, s.oy]) + s.k * (p0 + np.array([tx, ty])) - A @ p0
        s.M = (A, b)
        Ai = np.linalg.inv(A)
        yy, xx = np.mgrid[0:s.h, 0:s.w]
        P = np.stack([xx + 0.5 - b[0], yy + 0.5 - b[1]])
        s.X = Ai[0, 0] * P[0] + Ai[0, 1] * P[1]
        s.Y = Ai[1, 0] * P[0] + Ai[1, 1] * P[1]
        return s

    # ---- shapes (design space) -> masks
    def E(s, cx, cy, rx, ry=None):
        ry = rx if ry is None else ry
        return ((s.X - cx) / rx) ** 2 + ((s.Y - cy) / ry) ** 2 <= 1.0

    def R(s, x0, y0, x1, y1):
        return (s.X >= x0) & (s.X < x1) & (s.Y >= y0) & (s.Y < y1)

    def P(s, pts):
        X, Y = s.X, s.Y
        m = np.zeros(X.shape, bool)
        n = len(pts)
        for i in range(n):
            (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
            if ya == yb:
                continue
            cond = ((ya <= Y) & (Y < yb)) | ((yb <= Y) & (Y < ya))
            xi = xa + (Y - ya) * (xb - xa) / (yb - ya)
            m ^= cond & (X < xi)
        return m

    def cap(s, pts, r, r2=None):
        """Thick polyline (capsule chain), radius r (tapering to r2)."""
        r2 = r if r2 is None else r2
        m = np.zeros(s.X.shape, bool)
        n = len(pts) - 1
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            ra = r + (r2 - r) * i / n
            rb = r + (r2 - r) * (i + 1) / n
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy or 1e-6
            t = np.clip(((s.X - x0) * dx + (s.Y - y0) * dy) / L2, 0, 1)
            d = np.hypot(s.X - (x0 + t * dx), s.Y - (y0 + t * dy))
            m |= d <= ra + (rb - ra) * t
        return m

    def ring(s, cx, cy, r, w=1.2):
        d = np.hypot(s.X - cx, s.Y - cy)
        return (d <= r) & (d >= r - w)

    # ---- painting
    def part(s, m, shade, line=3, shadow=True, hl=True, open_bottom=None, band=None):
        if not m.any():
            return m
        ob = s.open_bottom if open_bottom is None else open_bottom
        s.a[m] = shade
        s.m |= m
        d = band or max(1, int(round(1.6 * s.k)))
        if shadow and shade < 3:
            sh = m & ~(_shift(m, d, 0) & _shift(m, 0, d))
            if ob:
                sh &= ~(_shift(m, d, 0) & s._bottom_rows(d))
            if shade < 2:
                s.a[sh] = shade + 1
            else:
                hi = m & ~(_shift(m, -1, 0) & _shift(m, 0, -1))
                s.a[hi] = 1
        if hl and shade == 3:
            hi = m & ~(_shift(m, -d, 0) & _shift(m, 0, -d))
            s.a[hi] = 2
        if line is not None:
            s.a[_edge(m, ob)] = line
        return m

    def _bottom_rows(s, d):
        b = np.zeros((s.h, s.w), bool)
        b[s.h - d:, :] = True
        return b

    def flat(s, m, shade):
        """Paint without outline or shading (markings inside a part)."""
        s.a[m] = shade
        return m

    def dither(s, m, shade, phase=0):
        yy, xx = np.mgrid[0:s.h, 0:s.w]
        s.a[m & ((xx + yy + phase) % 2 == 0)] = shade

    def stripes(s, m, shade, gap=3, dirn=(0, 1), phase=0):
        v = s.X * dirn[0] + s.Y * dirn[1]
        s.a[m & (np.floor(v + phase).astype(int) % gap == 0)] = shade

    # ---- pixel-space strokes and stamps
    def T(s, x, y):
        if getattr(s, "M", None) is not None:
            A, b = s.M
            return A[0, 0] * x + A[0, 1] * y + b[0], A[1, 0] * x + A[1, 1] * y + b[1]
        return s.ox + x * s.k, s.oy + y * s.k

    def px(s, x, y, shade):
        X, Y = s.T(x, y)
        xi, yi = int(math.floor(X)), int(math.floor(Y))
        if 0 <= xi < s.w and 0 <= yi < s.h:
            s.a[yi, xi] = shade

    def line(s, pts, shade=3):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            X0, Y0 = s.T(x0, y0); X1, Y1 = s.T(x1, y1)
            n = int(max(abs(X1 - X0), abs(Y1 - Y0)) * 2) + 1
            for i in range(n + 1):
                X = X0 + (X1 - X0) * i / n; Y = Y0 + (Y1 - Y0) * i / n
                xi, yi = int(math.floor(X)), int(math.floor(Y))
                if 0 <= xi < s.w and 0 <= yi < s.h:
                    s.a[yi, xi] = shade

    def stamp(s, rows, x, y, centre=True):
        """Pixel art at a design point; ' ' transparent, . - + # = shades 0..3."""
        if isinstance(rows, str):
            rows = rows.split("/")
        X, Y = s.T(x, y)
        if centre:
            X -= len(rows[0]) / 2; Y -= len(rows) / 2
        X, Y = int(round(X)), int(round(Y))
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c != " " and 0 <= X + i < s.w and 0 <= Y + j < s.h:
                    s.a[Y + j, X + i] = ".-+#".index(c)

    def outline_all(s):
        s.a[_edge(s.m, s.open_bottom)] = 3

    def size(s, r):
        return r * s.k


# ======================================================================== person
SKIN = 0

BUST = dict(kind="bust", cx=26, cy=17.5, rx=10, ry=11, tx=29, neck=(27, 32), shy=33, sw=14,
            arm=(11, 10.5), at=3.6, hand=2.9, low=56)
FULL = dict(kind="full", cx=27, cy=10.5, rx=8.6, ry=8.8, tx=28, neck=(19, 22), shy=22.5, sw=10,
            arm=(9, 8), at=3.1, hand=2.5, low=37, hip=37, foot=52.5)

FRONT_ARM = {"down": ((-2, 12), (-2.5, 23)), "hip": ((-8, 8), (-1.5, 15)), "cross": ((-3, 10), (13, 10)),
                 "hold": ((-5, 10), (-9, 1)), "raise": ((-5, -9), (-4, -20)), "point": ((-8, 5), (-19, 3)),
                 "wave": ((-8, 3), (-9, -8)), "chest": ((-2, 11), (8, 4)), "low": ((-4, 11), (-10, 18)),
                 "fist": ((-8, 6), (-14, -2)), "pocket": ((-3, 11), (0, 19))}
BACK_ARM = {"down": ((2, 12), (2.5, 23)), "hip": ((8, 8), (1.5, 15)), "cross": ((3, 10), (-11, 8)),
                "hold": ((5, 10), (9, 1)), "raise": ((5, -9), (4, -20)), "point": ((8, 5), (19, 3)),
                "wave": ((8, 3), (9, -8)), "chest": ((3, 11), (-6, 5)), "low": ((4, 11), (10, 18)),
                "fist": ((8, 6), (5, -2)), "pocket": ((3, 11), (0, 19))}


class Person:
    """p keys: rig, build, skin, top, sleeve ('long'/'short'/'none'), arms (front, back), hair,
    hairc, hat, hatc, eyes, brow, mouth, legs (full), pants, shoes, extras before/after..."""

    def __init__(s, fig, p):
        s.f, s.p = fig, dict(p)
        r = dict(p.get("rig", BUST))
        r.update(p.get("rigmod", {}))
        s.r = r
        s.u = r["rx"] / 8.5        # face unit

    # -- geometry helpers
    def head(s):
        r = s.r
        return r["cx"], r["cy"], r["rx"], r["ry"]

    def shoulders(s):
        r, b = s.r, s.p.get("build", 1.0)
        W = r["sw"] * b
        y = r["shy"] + (3.5 if r["kind"] == "bust" else 2.2)
        return (r["tx"] - W + 1.5, y), (r["tx"] + W - 1.5, y)

    # -- layers
    def draw(s):
        f, p = s.f, s.p
        for fn in p.get("pre", []):
            fn(s)
        s.arm("back")
        if s.r["kind"] == "full":
            s.legs()
        s.torso()
        for fn in p.get("mid", []):
            fn(s)
        s.neck()
        s.face_head()
        for fn in p.get("post", []):
            fn(s)
        s.arm("front")
        for fn in p.get("top", []):
            fn(s)
        return f

    def arm(s, side):
        p, r, f = s.p, s.r, s.f
        pose = p.get("arms", ("down", "down"))[0 if side == "front" else 1]
        if pose is None:
            return
        S = s.shoulders()[0 if side == "front" else 1]
        table = FRONT_ARM if side == "front" else BACK_ARM
        sc = r["arm"][0] / 11.5
        if isinstance(pose, tuple):
            (ex, ey), (hx, hy) = pose
        else:
            (ex, ey), (hx, hy) = table[pose]
        E = (S[0] + ex * sc, S[1] + ey * sc)
        H = (S[0] + hx * sc, S[1] + hy * sc)
        s.p.setdefault("hands", {})[side] = H
        s.p.setdefault("elbows", {})[side] = E
        t = r["at"] * p.get("armw", 1.0) * (p.get("build", 1.0) ** 0.5)
        sleeve = p.get("sleeve", "long")
        sc_ = p.get("sleevec", p.get("top", 1))
        upper = f.cap([S, E], t, t * 0.92)
        fore = f.cap([E, H], t * 0.9, t * 0.8)
        skin = p.get("skin", SKIN)
        if sleeve == "long":
            f.part(upper | fore, sc_)
        elif sleeve == "short":
            f.part(fore, skin)
            f.part(upper & ~f.E(E[0], E[1], t * 0.6), sc_)
        else:
            f.part(upper | fore, skin)
        if p.get("cuff") is not None and sleeve == "long":
            cx_, cy_ = E[0] + (H[0] - E[0]) * 0.8, E[1] + (H[1] - E[1]) * 0.8
            f.part(f.E(cx_, cy_, t * 1.0), p["cuff"])
        hs = p.get("glove", skin)
        hr = r["hand"] * p.get("handw", 1.0)
        if not p.get("nohand", {}).get(side) and H[1] < r.get("low", 56) + 30:
            f.part(f.E(H[0], H[1], hr * 1.05, hr), hs)

    def torso(s):
        p, r, f = s.p, s.r, s.f
        b = p.get("build", 1.0)
        c, W, y0 = r["tx"], r["sw"] * b, r["shy"]
        n0 = r["neck"][1]
        if r["kind"] == "bust":
            body = f.P([(c - 5, n0 - 1), (c + 5, n0 - 1), (c + W - 2, y0), (c + W + 1, y0 + 6),
                        (c + W + 1.5, 57), (c - W - 1.5, 57), (c - W - 1, y0 + 6), (c - W + 2, y0)])
            body |= f.E(c - W + 2.5, y0 + 4, 4.5, 5) | f.E(c + W - 2.5, y0 + 4, 4.5, 5)
        else:
            low = p.get("hem", r["low"])
            flare = p.get("flare", 0)
            body = f.P([(c - 2.5, n0 - 1), (c + 2.5, n0 - 1), (c + W - 1, y0 + 0.5), (c + W, y0 + 5),
                        (c + W - 1.5 + flare, low), (c - W + 1.5 - flare, low), (c - W, y0 + 5), (c - W + 1, y0 + 0.5)])
            body |= f.E(c - W + 1.8, y0 + 2.5, 2.6, 2.8) | f.E(c + W - 1.8, y0 + 2.5, 2.6, 2.8)
        s.body = body
        f.part(body, p.get("top", 1))
        for fn in p.get("outfit", []):
            fn(s)

    def legs(s):
        p, r, f = s.p, s.r, s.f
        c = r["tx"]
        hip, foot = r["hip"], r["foot"]
        lt = p.get("legw", 3.0)
        stance = p.get("stance", 4.0)
        L = [(c - 2.5, hip - 1), (c - stance - 0.5, foot - 1)]
        Rr = [(c + 2.5, hip - 1), (c + stance + 0.5, foot - 1)]
        pants = p.get("pants", 2)
        shorts = p.get("shorts")
        skin = p.get("skin", SKIN)
        for leg in (Rr, L):
            m = f.cap(leg, lt, lt * 0.9)
            if shorts:
                f.part(m, p.get("legskin", skin))
                f.part(m & (f.Y < hip + shorts), pants)
            else:
                f.part(m, pants)
            if p.get("socks") is not None:
                f.part(m & (f.Y > foot - 5), p["socks"])
            fx, fy = leg[1]
            f.part(f.E(fx - 1.2, fy + 1.0, 3.2, 1.9), p.get("shoes", 3))

    def neck(s):
        r, f, p = s.r, s.f, s.p
        cx = r["cx"] + 1
        w = 3.2 * s.u * p.get("neckw", 1.0)
        f.part(f.R(cx - w, r["neck"][0], cx + w, r["neck"][1] + 1.5), p.get("skin", SKIN))
        for fn in p.get("collar", []):
            fn(s)

    def face_head(s):
        f, p = s.f, s.p
        cx, cy, rx, ry = s.head()
        skin = p.get("skin", SKIN)
        # hair behind the head (long hair, ponytails) is in 'pre'
        hm = f.E(cx, cy, rx, ry)
        jaw = p.get("jaw", 1.0)
        hm |= f.P([(cx - rx * 0.95, cy + 1), (cx - rx * 0.5, cy + ry * 1.02 * jaw), (cx + rx * 0.15, cy + ry * 1.04 * jaw),
                   (cx + rx * 0.85, cy + ry * 0.6), (cx + rx * 0.9, cy)])
        hm |= f.E(cx - rx + 0.4 * s.u, cy + 2.2 * s.u, 1.5 * s.u, 1.4 * s.u)         # nose bump (faces left)
        s.headmask = hm
        f.part(hm, skin, shadow=False)
        # cheek shadow on the back of the face
        f.a[_edge(hm)] = 3
        if p.get("ear", True):
            ex, ey = cx + rx * 0.42, cy + 1.6 * s.u
            f.part(f.E(ex, ey, 1.8 * s.u, 2.4 * s.u), skin, shadow=False)
            f.px(ex - 0.6 * s.u, ey, min(skin + 1, 2)); f.px(ex - 0.6 * s.u, ey + 1, min(skin + 1, 2))
        for fn in p.get("face_pre", []):
            fn(s)
        s.face()
        hair(s, p.get("hair", "short"), p.get("hairc", 2))
        for fn in p.get("face", []):
            fn(s)
        hat(s, p.get("hat"), p.get("hatc", 2))

    def face(s):
        f, p, u = s.f, s.p, s.u
        cx, cy, rx, ry = s.head()
        eyes = p.get("eyes", "dot")
        big = rx * f.k >= 7.5
        e1, e2, ey = cx - 4.6 * u, cx + 1.3 * u, cy + 1.2 * u
        s.eyepos = (e1, e2, ey)
        if eyes in ("dot", "big", "round"):
            if big:
                e = "##/##/##" if eyes == "round" else "##/##"
                if eyes == "big":
                    e = "-#/##/##"
                f.stamp(e, e1, ey); f.stamp(e, e2, ey)
            elif rx * f.k >= 4.5:
                f.stamp("#/#", e1, ey); f.stamp("#/#", e2, ey)
            else:
                f.px(e1, ey, 3); f.px(e2, ey, 3)
        elif eyes == "closed":
            f.line([(e1 - 1, ey), (e1, ey + 0.7), (e1 + 1, ey)]); f.line([(e2 - 1, ey), (e2, ey + 0.7), (e2 + 1, ey)])
        elif eyes == "narrow":
            f.line([(e1 - 1, ey), (e1 + 1, ey)]); f.line([(e2 - 1, ey), (e2 + 1, ey)])
        elif eyes == "glow":
            f.stamp("###/#.#/###", e1, ey); f.stamp("###/#.#/###", e2, ey)
        elif eyes == "none":
            pass
        brow = p.get("brow")
        if brow and big:
            by = ey - 2.8 * u
            if brow == "angry":
                f.line([(e1 - 1.5, by - 1), (e1 + 1.2, by + 0.5)]); f.line([(e2 - 1.2, by + 0.5), (e2 + 1.5, by - 1)])
            elif brow == "thick":
                f.line([(e1 - 1.5, by), (e1 + 1.5, by)]); f.line([(e1 - 1.5, by - 0.8), (e1 + 1.5, by - 0.8)])
                f.line([(e2 - 1.5, by), (e2 + 1.5, by)]); f.line([(e2 - 1.5, by - 0.8), (e2 + 1.5, by - 0.8)])
            elif brow == "worry":
                f.line([(e1 - 1.5, by + 0.5), (e1 + 1.2, by - 1)]); f.line([(e2 - 1.2, by - 1), (e2 + 1.5, by + 0.5)])
            else:
                f.line([(e1 - 1.5, by), (e1 + 1.5, by)]); f.line([(e2 - 1.5, by), (e2 + 1.5, by)])
        mouth = p.get("mouth", "flat")
        mx, my = cx - 2.6 * u, cy + 5.8 * u
        if not big:
            my = cy + 4.6 * u
            if rx * f.k >= 4.5 and mouth != "none":
                f.line([(mx - 1, my), (mx + 1, my)])
            return
        if mouth == "smile":
            f.line([(mx - 2.2, my - 0.8), (mx - 1, my), (mx + 1.2, my), (mx + 2.2, my - 0.8)])
        elif mouth == "grin":
            f.stamp("#####/#...#/.###.", mx, my + 0.5)
        elif mouth == "frown":
            f.line([(mx - 2, my + 0.6), (mx - 1, my), (mx + 1.2, my), (mx + 2, my + 0.6)])
        elif mouth == "open":
            f.stamp("###/#+#/###", mx, my + 0.5)
        elif mouth == "smirk":
            f.line([(mx - 1.8, my), (mx + 1, my), (mx + 2.2, my - 1)])
        elif mouth == "flat":
            f.line([(mx - 1.6, my), (mx + 1.6, my)])
        elif mouth == "teeth":
            f.stamp("#####/#.#.#/#####", mx, my + 0.5)


# ======================================================================== hair
def hair(s, style, c):
    f = s.f
    cx, cy, rx, ry = s.head()
    u = s.u
    if style in (None, "bald"):
        return
    big = f.E(cx + 0.8 * u, cy - 1.6 * u, rx + 2.0 * u, ry + 1.4 * u)
    back = big & (f.X > cx + rx * 0.5) & (f.Y < cy + ry * 0.5 - (f.X - cx - rx * 0.5) * 0.35)
    back |= big & (f.X > cx + rx * 0.2) & (f.Y < cy - ry * 0.2)

    def fr(pts):          # fringe: polygon of points in head units (x from -1..1, y from -1..1)
        return f.P([(cx + x * rx, cy + y * ry) for x, y in pts])

    m = None
    if style == "short":
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.4), (0.3, -0.35), (-0.3, -0.4), (-0.7, -0.25), (-1.4, -0.35)]) | back)
    elif style == "sweep":       # long fringe sweeping to the front
        m = big & (fr([(-1.5, -1.6), (1.6, -1.6), (1.6, 0.4), (0.4, -0.45), (-0.4, -0.15), (-1.1, 0.2), (-1.5, -0.1)]) | back)
    elif style == "spiky":
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.4), (0.3, -0.4), (0.0, -0.15), (-0.4, -0.45), (-0.8, -0.2), (-1.4, -0.45)]) | back)
        for (ax, ay, bx, by_) in ((-0.9, -0.8, -1.5, -1.25), (-0.4, -0.95, -0.6, -1.65), (0.2, -1.0, 0.4, -1.75),
                                  (0.7, -0.85, 1.35, -1.45), (1.0, -0.3, 1.65, -0.55)):
            m |= f.P([(cx + (ax - 0.25) * rx, cy + (ay + 0.15) * ry), (cx + bx * rx, cy + by_ * ry),
                      (cx + (ax + 0.3) * rx, cy + (ay + 0.25) * ry)])
    elif style == "tuft":        # messy with a cowlick
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.4), (0.4, -0.3), (0.0, -0.5), (-0.5, -0.3), (-0.9, -0.5), (-1.4, -0.3)]) | back)
        m |= f.cap([(cx - 0.1 * rx, cy - 1.05 * ry), (cx - 0.5 * rx, cy - 1.5 * ry), (cx - 0.9 * rx, cy - 1.45 * ry)], 1.2 * u, 0.6 * u)
    elif style == "slick":       # combed back, forehead clear
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.4), (0.4, -0.6), (-0.4, -0.7), (-1.0, -0.62), (-1.4, -0.6)]) | back)
        m |= f.E(cx + rx * 0.7, cy - ry * 0.55, rx * 0.65, ry * 0.6)
    elif style == "bob":
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.9), (0.3, -0.4), (-0.6, -0.45), (-1.3, -0.2)]) | back)
        m |= f.P([(cx + 0.2 * rx, cy - 0.2 * ry), (cx + 1.25 * rx, cy - 0.5 * ry), (cx + 1.25 * rx, cy + 0.9 * ry), (cx + 0.55 * rx, cy + 0.95 * ry)])
        m |= f.P([(cx - 0.9 * rx, cy - 0.5 * ry), (cx - 1.15 * rx, cy - 0.2 * ry), (cx - 1.05 * rx, cy + 0.55 * ry), (cx - 0.78 * rx, cy + 0.3 * ry)])
    elif style == "curly":
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.5), (0.3, -0.35), (-1.4, -0.35)]) | back)
        for a in range(0, 360, 36):
            t = math.radians(a)
            x, y = math.cos(t) * 1.02, -abs(math.sin(t)) * 0.95 - 0.1
            if a > 200:
                continue
            m |= f.E(cx + (x * 1.0 + 0.1) * rx, cy + y * ry, 2.3 * u, 2.2 * u)
        m |= f.E(cx + 0.95 * rx, cy + 0.2 * ry, 2.3 * u, 2.4 * u)
    elif style == "mohawk":
        m = f.P([(cx - 0.6 * rx, cy - 0.85 * ry), (cx - 0.1 * rx, cy - 1.95 * ry), (cx + 0.5 * rx, cy - 2.1 * ry),
                 (cx + 1.2 * rx, cy - 1.6 * ry), (cx + 1.1 * rx, cy - 0.3 * ry), (cx + 0.5 * rx, cy - 0.85 * ry)])
        m &= ~f.E(cx, cy, rx * 0.8, ry * 0.8)
    elif style == "buzz":
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.3), (0.5, -0.62), (-1.4, -0.62)]) | back) & f.E(cx, cy - 0.3 * u, rx + 0.4 * u, ry + 0.3 * u)
    elif style == "fringe":      # straight-cut bangs
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.8), (0.6, -0.15), (-1.4, -0.15)]) | back)
    elif style == "side":        # long side-part covering one eye area at the back
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 1.0), (0.55, 0.1), (0.1, -0.3), (-0.6, -0.55), (-1.4, -0.5)]) | back)
    elif style == "wave":        # big wave crest at the back
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.6), (0.3, -0.4), (-0.6, -0.5), (-1.3, -0.25)]) | back)
        m |= f.P([(cx - 0.2 * rx, cy - 1.0 * ry), (cx + 0.6 * rx, cy - 1.75 * ry), (cx + 1.7 * rx, cy - 1.5 * ry),
                  (cx + 1.35 * rx, cy - 1.15 * ry), (cx + 1.6 * rx, cy - 0.5 * ry), (cx + 0.9 * rx, cy - 0.2 * ry)])
    elif style == "topknot":
        m = big & (fr([(-1.4, -1.6), (1.6, -1.6), (1.6, 0.4), (0.4, -0.65), (-1.4, -0.65)]) | back)
        m |= f.E(cx + 0.35 * rx, cy - 1.25 * ry, 2.6 * u, 2.4 * u)
    elif style == "fade":        # sides shaved, flat top
        m = f.R(cx - 0.75 * rx, cy - 1.45 * ry, cx + 0.95 * rx, cy - 0.45 * ry) & f.E(cx + 0.1 * rx, cy - 0.7 * ry, rx * 1.0, ry * 0.85)
    elif style == "sides":       # bald on top, hair at the back/sides
        m = big & f.E(cx + rx * 0.9, cy + 0.0, rx * 0.55, ry * 0.55) & ~f.E(cx, cy - ry * 0.4, rx * 0.95, ry * 0.7)
    if m is None:
        return
    m &= ~(f.Y > s.r["neck"][1] + 6)
    if s.p.get("hat") in ("cap", "beanie", "helmet", "hard", "peak", "pom", "bucket", "wide", "bush", "hood", "bowl", "dealer"):
        pass
    f.part(m, c, shadow=c < 2)
    s.hairmask = m
    # a few strands
    if c < 3 and s.r["rx"] * f.k >= 7:
        sc = min(c + 1, 3)
        for k in (-0.5, 0.1, 0.65):
            x0 = cx + k * rx
            f.line([(x0, cy - 0.95 * ry), (x0 + 0.25 * rx, cy - 0.55 * ry)], sc)
        if not (m & f.E(cx + 0.9 * rx, cy, 1, 1)).any():
            return
        f.line([(cx + 0.95 * rx, cy - 0.6 * ry), (cx + 1.05 * rx, cy + 0.1 * ry)], sc)


def long_back(s, c=None, length=1.0, width=1.0):
    """Long hair falling behind the shoulders (a 'pre' layer)."""
    f = s.f
    cx, cy, rx, ry = s.head()
    c = s.p.get("hairc", 2) if c is None else c
    yb = cy + ry * (1.2 + 1.6 * length)
    m = f.P([(cx - rx * 0.9 * width, cy - ry * 0.3), (cx + rx * 1.3 * width, cy - ry * 0.5), (cx + rx * 1.55 * width, yb),
             (cx + rx * 0.5, yb + ry * 0.2), (cx - rx * 1.05 * width, yb - ry * 0.15)]) | f.E(cx + 0.5, cy - 0.5, rx * 1.15, ry * 1.05)
    f.part(m, c, shadow=c < 2)
    if c < 3:
        for k in (0.2, 0.7, 1.1):
            f.line([(cx + rx * k, cy + ry * 0.6), (cx + rx * (k + 0.15), yb - 2)], min(c + 1, 3))


def ponytail(s, c=None, high=False):
    f = s.f
    cx, cy, rx, ry = s.head()
    c = s.p.get("hairc", 2) if c is None else c
    y0 = cy - ry * (0.75 if high else 0.1)
    m = f.cap([(cx + rx * 0.9, y0), (cx + rx * 1.6, y0 + ry * 0.4), (cx + rx * 1.65, y0 + ry * 1.3)], 2.6 * s.u, 1.4 * s.u)
    f.part(m, c, shadow=c < 2)
    f.part(f.E(cx + rx * 0.95, y0, 1.8 * s.u, 1.8 * s.u), s.p.get("tiec", 1))


def buns(s, c=None):
    f = s.f
    cx, cy, rx, ry = s.head()
    c = s.p.get("hairc", 2) if c is None else c
    for x, y in ((-0.45, -1.05), (0.75, -0.95)):
        f.part(f.E(cx + x * rx, cy + y * ry, 3.0 * s.u, 2.8 * s.u), c, shadow=c < 2)


def braid(s, c=None):
    f = s.f
    cx, cy, rx, ry = s.head()
    c = s.p.get("hairc", 2) if c is None else c
    pts = [(cx + rx * 0.7, cy + ry * 0.4), (cx + rx * 0.9, cy + ry * 1.4), (cx + rx * 0.6, cy + ry * 2.4)]
    for i in range(5):
        t = i / 4
        x = pts[0][0] + (pts[2][0] - pts[0][0]) * t + math.sin(t * 3) * 1.2
        y = pts[0][1] + (pts[2][1] - pts[0][1]) * t
        f.part(f.E(x, y, 2.1 * s.u, 2.0 * s.u), c, shadow=c < 2)


# ======================================================================== hats
def hat(s, kind, c):
    if not kind:
        return
    f = s.f
    cx, cy, rx, ry = s.head()
    u = s.u
    if kind == "cap":            # brim to the front (left)
        crown = f.E(cx + 0.5 * u, cy - 0.45 * ry, rx * 1.12, ry * 0.75) & (f.Y < cy - 0.45 * ry)
        f.part(crown, c)
        f.part(f.P([(cx - rx * 1.75, cy - 0.38 * ry), (cx - rx * 0.2, cy - 0.62 * ry), (cx + rx * 0.2, cy - 0.38 * ry),
                    (cx - rx * 1.6, cy - 0.15 * ry)]), min(c + 1, 3))
    elif kind == "backcap":      # cap worn backwards, brim at the back
        crown = f.E(cx + 0.5 * u, cy - 0.45 * ry, rx * 1.12, ry * 0.75) & (f.Y < cy - 0.45 * ry)
        f.part(crown, c)
        f.part(f.P([(cx + rx * 0.6, cy - 0.62 * ry), (cx + rx * 1.9, cy - 0.5 * ry), (cx + rx * 1.8, cy - 0.25 * ry), (cx + rx * 0.7, cy - 0.38 * ry)]), min(c + 1, 3))
    elif kind in ("beanie", "pom"):
        m = f.E(cx + 0.4 * u, cy - 0.5 * ry, rx * 1.12, ry * 0.85) & (f.Y < cy - 0.35 * ry)
        f.part(m, c)
        f.part(f.R(cx - rx * 1.1, cy - 0.55 * ry, cx + rx * 1.3, cy - 0.3 * ry) & f.E(cx + 0.4 * u, cy - 0.4 * ry, rx * 1.18, ry), min(c + 1, 3) if c < 2 else 1)
        f.stripes(m & (f.Y < cy - 0.6 * ry), min(c + 1, 3), gap=3, dirn=(1, 0))
        if kind == "pom":
            f.part(f.E(cx + 0.6 * u, cy - 1.35 * ry, 2.6 * u, 2.4 * u), 0)
    elif kind == "bucket":
        f.part(f.E(cx + 0.3, cy - 0.55 * ry, rx * 1.65, ry * 0.32), min(c + 1, 3))
        f.part(f.P([(cx - rx * 0.95, cy - 0.55 * ry), (cx - rx * 0.75, cy - 1.35 * ry), (cx + rx * 0.95, cy - 1.4 * ry),
                    (cx + rx * 1.15, cy - 0.55 * ry)]), c)
    elif kind == "wide":         # floppy wide brim
        f.part(f.E(cx + 0.5, cy - 0.5 * ry, rx * 2.0, ry * 0.36), c)
        f.part(f.E(cx + 0.5, cy - 0.95 * ry, rx * 0.95, ry * 0.6) & (f.Y < cy - 0.6 * ry), c)
        f.part(f.R(cx - rx * 0.95, cy - 0.8 * ry, cx + rx * 1.4, cy - 0.6 * ry) & f.E(cx + 0.5, cy - 0.9 * ry, rx * 1.0, ry), min(c + 1, 3))
    elif kind == "bush":         # field hat, one side pinned up
        f.part(f.P([(cx - rx * 1.7, cy - 0.35 * ry), (cx + rx * 1.0, cy - 0.65 * ry), (cx + rx * 1.4, cy - 1.45 * ry),
                    (cx + rx * 1.7, cy - 1.3 * ry), (cx + rx * 1.4, cy - 0.35 * ry), (cx - rx * 1.6, cy - 0.1 * ry)]), min(c + 1, 3))
        f.part(f.E(cx + 0.2 * u, cy - 0.85 * ry, rx * 1.0, ry * 0.6) & (f.Y < cy - 0.5 * ry), c)
        f.part(f.R(cx - rx * 1.0, cy - 0.75 * ry, cx + rx * 1.2, cy - 0.5 * ry) & f.E(cx + 0.2 * u, cy - 0.8 * ry, rx * 1.05, ry), 2)
    elif kind == "helmet":
        f.part(f.E(cx + 0.6 * u, cy - 0.15 * ry, rx * 1.3, ry * 1.12) & (f.Y < cy + 0.35 * ry) & ~f.P(
            [(cx - rx * 1.5, cy - 0.35 * ry), (cx + rx * 0.35, cy - 0.35 * ry), (cx + rx * 0.35, cy + ry), (cx - rx * 1.5, cy + ry)]), c)
        f.part(f.R(cx - rx * 1.2, cy - 0.6 * ry, cx + rx * 0.5, cy - 0.3 * ry), 3)
    elif kind == "hard":         # hard hat
        f.part(f.E(cx + 0.5 * u, cy - 0.55 * ry, rx * 1.12, ry * 0.85) & (f.Y < cy - 0.45 * ry), c)
        f.part(f.R(cx - rx * 1.55, cy - 0.55 * ry, cx + rx * 1.45, cy - 0.32 * ry), min(c + 1, 3))
        f.part(f.R(cx - 1.2 * u, cy - 1.4 * ry, cx + 1.8 * u, cy - 0.55 * ry), min(c + 1, 3), shadow=False)
    elif kind == "peak":         # officer cap
        f.part(f.P([(cx - rx * 1.05, cy - 0.45 * ry), (cx - rx * 1.25, cy - 1.15 * ry), (cx + rx * 0.6, cy - 1.45 * ry),
                    (cx + rx * 1.5, cy - 1.1 * ry), (cx + rx * 1.15, cy - 0.45 * ry)]), c)
        f.part(f.R(cx - rx * 1.05, cy - 0.68 * ry, cx + rx * 1.18, cy - 0.42 * ry), 3)
        f.part(f.P([(cx - rx * 1.7, cy - 0.42 * ry), (cx - rx * 0.4, cy - 0.5 * ry), (cx - rx * 0.6, cy - 0.25 * ry), (cx - rx * 1.6, cy - 0.25 * ry)]), 3)
        s.badge = (cx - rx * 0.35, cy - 0.95 * ry)
    elif kind == "band":         # headband with tails
        f.part(f.R(cx - rx * 1.05, cy - 0.55 * ry, cx + rx * 1.1, cy - 0.3 * ry) & f.E(cx, cy, rx * 1.12, ry * 1.1), c)
        f.part(f.cap([(cx + rx * 1.0, cy - 0.42 * ry), (cx + rx * 1.7, cy - 0.1 * ry), (cx + rx * 2.1, cy + 0.4 * ry)], 1.1 * u, 0.8 * u), c)
        f.part(f.cap([(cx + rx * 1.0, cy - 0.42 * ry), (cx + rx * 1.9, cy - 0.5 * ry), (cx + rx * 2.4, cy - 0.15 * ry)], 1.0 * u, 0.7 * u), c)
    elif kind == "bandana":
        f.part(f.E(cx + 0.5 * u, cy - 0.4 * ry, rx * 1.12, ry * 0.8) & (f.Y < cy - 0.35 * ry), c)
        f.part(f.P([(cx + rx * 0.9, cy - 0.5 * ry), (cx + rx * 1.9, cy - 0.2 * ry), (cx + rx * 1.6, cy + 0.3 * ry), (cx + rx * 1.0, cy - 0.1 * ry)]), c)
        f.dither(f.E(cx + 0.5 * u, cy - 0.4 * ry, rx * 1.12, ry * 0.8) & (f.Y < cy - 0.5 * ry) & (f.Y > cy - 1.1 * ry) & ~_edge(f.E(cx + 0.5 * u, cy - 0.4 * ry, rx * 1.12, ry * 0.8)), min(c + 1, 3))
    elif kind in ("hood", "parka"):
        outer = f.E(cx + 1.5 * u, cy - 0.3 * u, rx * 1.32, ry * 1.25)
        outer |= f.P([(cx + rx * 0.1, cy - ry * 1.1), (cx + rx * 1.5, cy - ry * 1.45), (cx + rx * 1.3, cy - ry * 0.5)])
        outer |= f.P([(cx - rx * 0.6, cy + ry * 0.7), (cx + rx * 1.4, cy + ry * 0.2), (cx + rx * 1.7, cy + ry * 1.55), (cx - rx * 0.4, cy + ry * 1.5)])
        hole = f.E(cx - rx * 0.28, cy + ry * 0.18, rx * 0.86, ry * 0.92)
        f.part(outer & ~hole, c)
        if kind == "parka":
            trim = f.E(cx - rx * 0.28, cy + ry * 0.18, rx * 1.08, ry * 1.12) & ~hole
            f.part(trim, 0, shadow=False)
            f.dither(trim & ~_edge(trim), 1)
        else:
            f.line([(cx + rx * 0.55, cy - ry * 0.75), (cx + rx * 0.9, cy + ry * 0.6)], min(c + 1, 3) if c < 3 else 2)
    elif kind == "crown":
        pts = [(cx - rx * 0.8, cy - 0.55 * ry), (cx - rx * 0.9, cy - 1.35 * ry), (cx - rx * 0.4, cy - 0.95 * ry),
               (cx + rx * 0.1, cy - 1.55 * ry), (cx + rx * 0.55, cy - 0.95 * ry), (cx + rx * 1.05, cy - 1.35 * ry), (cx + rx * 0.95, cy - 0.55 * ry)]
        f.part(f.P(pts), c)
    elif kind == "dealer":       # dealer visor
        f.part(f.R(cx - rx * 0.9, cy - 0.68 * ry, cx + rx * 1.1, cy - 0.45 * ry) & f.E(cx, cy, rx * 1.12, ry * 1.1), 3)
        f.part(f.P([(cx - rx * 1.8, cy - 0.5 * ry), (cx - rx * 0.6, cy - 0.68 * ry), (cx - rx * 0.4, cy - 0.38 * ry), (cx - rx * 1.6, cy - 0.25 * ry)]), c)
