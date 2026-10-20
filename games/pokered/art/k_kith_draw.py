"""KITHBOUND creature raster engine (our own code, no retail data).

A Fig collects parts drawn in a 0..100 design space (x right, y down, ground at y=100,
creature faces LEFT).  render() turns them into a 2bpp picture: parts are filled with
their shade, shaded from a top-left light, outlined in black (outside edge and where a
front part overlaps another group), then pixel details (lines, eyes) go on top.
Shades: 0 white, 1 light, 2 dark, 3 black.
"""
import math

import numpy as np

SS = 4  # supersampling per pixel axis


class Fig:
    def __init__(self, W, H, back=False, sc=None, ox=None, oy=None, shift=0.0, probe=False):
        self.W, self.H, self.back = W, H, back
        self.sc = sc if sc is not None else W / 100.0
        self.ox = ox if ox is not None else W / 2.0
        self.oy = oy if oy is not None else H
        self.probe = probe
        self.shift = shift
        self.parts = []
        self.post = []
        ys = (np.arange(H * SS) + 0.5) / SS
        xs = (np.arange(W * SS) + 0.5) / SS
        self.gx, self.gy = np.meshgrid(xs, ys)

    # ---- transforms -------------------------------------------------------------------
    def P(self, u, v):
        u = u + self.shift
        if self.back:
            return self.ox - (u - 50.0) * self.sc, self.oy + (v - 100.0) * self.sc
        return self.ox + (u - 50.0) * self.sc, self.oy + (v - 100.0) * self.sc

    def px(self, r):
        return r * self.sc

    def flipx(self):
        return -1.0 if self.back else 1.0

    # ---- mask builders (pixel space, supersampled) --------------------------------------
    def _down(self, m):
        H, W = self.H, self.W
        return m.reshape(H, SS, W, SS).mean(axis=(1, 3)) >= 0.42

    def m_ell(self, cx, cy, rx, ry, ang=0.0):
        X, Y = self.P(cx, cy)
        rx, ry = max(self.px(rx), 0.55), max(self.px(ry), 0.55)
        a = math.radians(ang) * self.flipx()
        c, s = math.cos(a), math.sin(a)
        dx, dy = self.gx - X, self.gy - Y
        xr = dx * c + dy * s
        yr = -dx * s + dy * c
        return (xr / rx) ** 2 + (yr / ry) ** 2 <= 1.0

    def m_poly(self, pts):
        q = [self.P(u, v) for u, v in pts]
        inside = np.zeros(self.gx.shape, bool)
        n = len(q)
        for i in range(n):
            x1, y1 = q[i]
            x2, y2 = q[(i + 1) % n]
            if y1 == y2:
                continue
            cond = (self.gy >= min(y1, y2)) & (self.gy < max(y1, y2))
            xint = x1 + (self.gy - y1) * (x2 - x1) / (y2 - y1)
            inside ^= cond & (self.gx < xint)
        return inside

    def m_stroke(self, pts, r0, r1=None):
        if r1 is None:
            r1 = r0
        q = [self.P(u, v) for u, v in pts]
        n = len(q)
        lens = [math.hypot(q[i + 1][0] - q[i][0], q[i + 1][1] - q[i][1]) for i in range(n - 1)]
        tot = sum(lens) or 1.0
        out = np.zeros(self.gx.shape, bool)
        acc = 0.0
        for i in range(n - 1):
            (x1, y1), (x2, y2) = q[i], q[i + 1]
            ra = max(self.px(r0 + (r1 - r0) * acc / tot), 0.6)
            acc += lens[i]
            rb = max(self.px(r0 + (r1 - r0) * acc / tot), 0.6)
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy or 1e-9
            t = np.clip(((self.gx - x1) * dx + (self.gy - y1) * dy) / L2, 0, 1)
            d = np.hypot(self.gx - (x1 + t * dx), self.gy - (y1 + t * dy))
            out |= d <= ra + (rb - ra) * t
        return out

    # ---- parts -----------------------------------------------------------------------
    def _add(self, m, s, kind="shape", line=True, group=None, sh=None, hl=False, clip=None, face=False):
        if face and self.back:
            m = np.zeros_like(m)
        self.parts.append(dict(m=self._down(m), s=s, kind=kind, line=line,
                               group=group if group is not None else len(self.parts),
                               sh=sh, hl=hl, clip=clip))
        return len(self.parts) - 1

    def ell(self, cx, cy, rx, ry, s=1, ang=0.0, **k):
        return self._add(self.m_ell(cx, cy, rx, ry, ang), s, **k)

    def poly(self, pts, s=1, **k):
        return self._add(self.m_poly(pts), s, **k)

    def stroke(self, pts, r0, r1=None, s=1, **k):
        return self._add(self.m_stroke(pts, r0, r1), s, **k)

    def mark_ell(self, cx, cy, rx, ry, s, ang=0.0, clip=None, face=False):
        return self._add(self.m_ell(cx, cy, rx, ry, ang), s, kind="mark", line=False, clip=clip, face=face)

    def mark_poly(self, pts, s, clip=None):
        return self._add(self.m_poly(pts), s, kind="mark", line=False, clip=clip)

    def mark_stroke(self, pts, r0, r1=None, s=2, clip=None):
        return self._add(self.m_stroke(pts, r0, r1), s, kind="mark", line=False, clip=clip)

    def cut_ell(self, cx, cy, rx, ry, ang=0.0):
        return self._add(self.m_ell(cx, cy, rx, ry, ang), 0, kind="cut", line=False)

    def cut_poly(self, pts):
        return self._add(self.m_poly(pts), 0, kind="cut", line=False)

    # ---- pixel details -----------------------------------------------------------------
    def line(self, pts, s=3, clip=None, face=False):
        if face and self.back:
            return
        self.post.append(("line", [self.P(u, v) for u, v in pts], s, clip))

    def dot(self, u, v, s=3, face=False):
        if face and self.back:
            return
        self.post.append(("dot", self.P(u, v), s))

    def eye(self, u, v, r=3.0, kind="dot", look=-1, brow=0):
        """look -1 = toward the left of the design (mirrored on backs)."""
        if self.back:
            return
        self.post.append(("eye", self.P(u, v), max(1, int(round(self.px(r)))), kind, look, brow))

    # ---- render ----------------------------------------------------------------------
    def bbox(self):
        """Design-space bounding box of all shape parts."""
        m = np.zeros((self.H, self.W), bool)
        for p in self.parts:
            if p["kind"] == "shape":
                m |= p["m"]
        ys, xs = np.nonzero(m)
        if not len(xs):
            return 0, 0, 100, 100
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        sgn = -1 if self.back else 1
        ua = (x0 - self.ox) / (self.sc * sgn) + 50 - self.shift
        ub = (x1 - self.ox) / (self.sc * sgn) + 50 - self.shift
        return min(ua, ub), (y0 - self.oy) / self.sc + 100, max(ua, ub), (y1 - self.oy) / self.sc + 100

    def render(self):
        H, W = self.H, self.W
        owner = np.full((H, W), -1, int)
        for i, p in enumerate(self.parts):
            if p["kind"] == "shape":
                owner[p["m"]] = i
            elif p["kind"] == "cut":
                owner[p["m"]] = -1
        base = np.zeros((H, W), int)
        delta = np.zeros((H, W), int)
        for i, p in enumerate(self.parts):
            if p["kind"] != "shape":
                continue
            own = owner == i
            if not own.any():
                continue
            base[own] = p["s"]
            m = p["m"]
            ys, xs = np.nonzero(m)
            bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
            k = p["sh"]
            if k is None:
                k = 0 if min(bw, bh) < 5 else int(np.clip(round(min(bw, bh) * 0.16), 1, 4))
            if k > 0 and p["s"] < 3:
                sh = np.zeros_like(m)
                sh[:H - k, :W - k] = m[k:, k:]
                shadow = m & ~sh
                delta[own & shadow] = 1
            if p["hl"] and p["s"] >= 1:
                cx, cy = xs.min() + 0.32 * bw, ys.min() + 0.28 * bh
                rx, ry = max(0.6, 0.13 * bw), max(0.6, 0.10 * bh)
                yy, xx = np.mgrid[0:H, 0:W]
                spot = (((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1) & own
                base[spot] = p["s"] - 1
                delta[spot] = 0
        for i, p in enumerate(self.parts):
            if p["kind"] != "mark":
                continue
            m = p["m"] & (owner >= 0)
            if p["clip"] is not None:
                cl = p["clip"] if isinstance(p["clip"], (list, tuple, set)) else [p["clip"]]
                m &= np.isin(owner, list(cl))
            base[m] = p["s"]
        out = base.copy()
        chk = (np.add.outer(np.arange(H), np.arange(W)) % 2) == 0
        out[(base == 0) & (delta == 1)] = 1
        out[(base == 1) & (delta == 1)] = 2
        out[owner < 0] = 0
        # outlines
        line = np.zeros((H, W), bool)
        grp = np.array([p["group"] for p in self.parts] + [-99])
        lin = np.array([p["line"] for p in self.parts] + [False])
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nb = np.full((H + 2, W + 2), -2, int)
            nb[1:-1, 1:-1] = owner
            n = nb[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
            fig = owner >= 0
            line |= fig & (n == -1)
            both = fig & (n >= 0)
            o = np.where(both, owner, 0)
            nn = np.where(both, n, 0)
            diff = both & (grp[o] != grp[nn]) & (o > nn) & lin[o]
            line |= diff
        out[line] = 3
        self.out = out
        for op in self.post:
            getattr(self, "_p_" + op[0])(*op[1:])
        return np.clip(self.out, 0, 3).astype(np.uint8)

    # ---- pixel ops ---------------------------------------------------------------------
    def _set(self, x, y, s):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < self.W and 0 <= y < self.H:
            self.out[y, x] = s

    def _p_line(self, q, s, clip):
        for (x1, y1), (x2, y2) in zip(q, q[1:]):
            n = int(max(abs(x2 - x1), abs(y2 - y1)) * 2) + 1
            for t in np.linspace(0, 1, n + 1):
                x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                xi, yi = int(math.floor(x)), int(math.floor(y))
                if 0 <= xi < self.W and 0 <= yi < self.H and (clip is None or self.out[yi, xi] != 0):
                    self.out[yi, xi] = s

    def _p_dot(self, q, s):
        self._set(q[0], q[1], s)

    def _p_eye(self, q, r, kind, look, brow):
        x0, y0 = int(math.floor(q[0])), int(math.floor(q[1]))
        L = look * (-1 if self.back else 1)
        S = self._set
        if kind == "dot":
            w, h = max(1, r), r + 1
            for yy in range(h):
                for xx in range(w):
                    if r >= 3 and (yy in (0, h - 1)) and (xx in (0, w - 1)):
                        continue
                    S(x0 + xx - w // 2, y0 + yy - h // 2, 3)
            if r >= 2:
                S(x0 - w // 2 + (w - 1 if L > 0 else 0) + (0 if r < 3 else (-1 if L > 0 else 1)), y0 - h // 2 + (1 if r >= 3 else 0), 0)
        elif kind in ("round", "angry", "slit", "glow", "sad"):
            rx, ry = max(1.6, r + 0.2), max(2.1, r + 0.7)
            for yy in range(-int(ry) - 1, int(ry) + 2):
                for xx in range(-int(rx) - 1, int(rx) + 2):
                    d = (xx / rx) ** 2 + (yy / ry) ** 2
                    if d <= 1.0:
                        S(x0 + xx, y0 + yy, 0)
                    elif d <= (1 + 1.0 / min(rx, ry)) ** 2 + 0.25:
                        S(x0 + xx, y0 + yy, 3)
            if kind == "slit":
                for yy in range(-int(ry) + 1, int(ry)):
                    S(x0 + (L if r >= 3 else 0) * 0, y0 + yy, 3)
            elif kind != "glow":
                pw = 1 if r <= 2 else 2
                px0 = x0 + (L * max(0, int(rx) - pw) if L else 0)
                if L < 0:
                    px0 = x0 - int(rx) + 1
                elif L > 0:
                    px0 = x0 + int(rx) - pw
                for yy in range(0, max(2, r)):
                    for xx in range(pw):
                        S(px0 + xx, y0 - (r // 2) + yy + 1, 3)
            if kind == "angry" or brow > 0:
                for xx in range(-int(rx) - 1, int(rx) + 2):
                    t = (xx * (-L if L else 1)) / (rx + 1)
                    yb = y0 - int(ry) - 1 + int(round((t + 1) * 1.0))
                    S(x0 + xx, yb, 3)
                    S(x0 + xx, yb - 1, 0) if False else None
            if kind == "sad" or brow < 0:
                for xx in range(-int(rx) - 1, int(rx) + 2):
                    t = (xx * (L if L else 1)) / (rx + 1)
                    yb = y0 - int(ry) - 1 + int(round((t + 1) * 1.0))
                    S(x0 + xx, yb, 3)
        elif kind == "closed":  # lid line, ends drooping
            w = max(2, r + 1)
            for xx in range(-w, w + 1):
                S(x0 + xx, y0 + (1 if abs(xx) == w else 0), 3)
        elif kind == "happy":   # ^ arc
            w = max(2, r + 1)
            for xx in range(-w, w + 1):
                S(x0 + xx, y0 + abs(xx) * 2 // (w + 1) - 1 + (1 if abs(xx) == w else 0), 3)
        elif kind == "sleepy":  # flat lid with a pupil below
            w = max(2, r + 1)
            for xx in range(-w, w + 1):
                S(x0 + xx, y0, 3)
            for xx in range(-w // 2, w // 2 + 1):
                S(x0 + xx + (L if r > 2 else 0), y0 + 1, 3)
