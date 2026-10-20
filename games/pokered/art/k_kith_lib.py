"""KITHBOUND part library and body-plan templates (design space 0..100, facing left)."""
import math
import random


def rot(pts, ang, ox=0.0, oy=0.0):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(ox + x * c - y * s, oy + x * s + y * c) for x, y in pts]


def arc(cx, cy, rx, ry, a0, a1, n=12):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def lerp(a, b, t):
    return a + (b - a) * t


# ------------------------------------------------------------------ simple features
def flame(f, x, y, w, h, ang=0.0, n=3, s=1, inner=True, **k):
    """Flame rooted at (x, y) pointing up (ang rotates clockwise)."""
    pts = [(-w / 2, 0)]
    for i in range(n):
        t0 = (i + 0.5) / n
        tip_h = h * (0.75 + 0.25 * math.sin(math.pi * t0)) * (1.0 if i != n // 2 else 1.0)
        pts.append(((-w / 2 + w * t0) * 1.1 + (w * 0.12 if i < n / 2 else -w * 0.12) * 0, -tip_h))
        if i < n - 1:
            pts.append((-w / 2 + w * (i + 1) / n, -h * 0.45))
    pts.append((w / 2, 0))
    pts += [(w * 0.35, h * 0.18), (0, h * 0.24), (-w * 0.35, h * 0.18)]
    i = f.poly(rot(pts, ang, x, y), s, **k)
    if inner and h > 8:
        q = [(-w * 0.22, h * 0.05), (0, -h * 0.55), (w * 0.22, h * 0.05), (0, h * 0.12)]
        f.mark_poly(rot(q, ang, x, y), 0 if s >= 1 else 1, clip=i)
    return i


def leaf(f, x, y, ln, wd, ang, s=1, vein=True, **k):
    """Leaf from stem (x, y) of length ln pointing at angle ang (0 = right, 90 = down)."""
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((ln * t, -wd * math.sin(math.pi * t) * (1 - 0.3 * t)))
    for i in range(7, 0, -1):
        t = i / 8
        pts.append((ln * t, wd * math.sin(math.pi * t) * (1 - 0.3 * t)))
    j = f.poly(rot(pts, ang, x, y), s, **k)
    if vein and ln > 8:
        f.line(rot([(ln * 0.1, 0), (ln * 0.8, 0)], ang, x, y), 3, clip=True)
    return j


def horn(f, x, y, ln, wd, ang, curve=0.0, s=0, **k):
    """Tapered horn from base centre (x, y), angle ang (-90 = up)."""
    pts = []
    for i in range(7):
        t = i / 6
        pts.append((ln * t, -wd / 2 * (1 - t) + curve * t * t * ln * 0.3))
    for i in range(5, -1, -1):
        t = i / 6
        pts.append((ln * t, wd / 2 * (1 - t) + curve * t * t * ln * 0.3))
    return f.poly(rot(pts, ang, x, y), s, **k)


def spikes(f, pts, ln, wd, s=2, side=-1, n=None, **k):
    """Row of triangles along a polyline, on the given normal side."""
    out = []
    segs = list(zip(pts, pts[1:]))
    tot = sum(math.dist(a, b) for a, b in segs)
    n = n or max(2, int(tot / (wd * 1.1)))
    for i in range(n):
        d = (i + 0.5) / n * tot
        for a, b in segs:
            L = math.dist(a, b)
            if d <= L or (a, b) == segs[-1]:
                t = min(1, d / L)
                x, y = lerp(a[0], b[0], t), lerp(a[1], b[1], t)
                tx, ty = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                nx, ny = -ty * side, tx * side
                tri = [(x - tx * wd / 2, y - ty * wd / 2), (x + nx * ln, y + ny * ln), (x + tx * wd / 2, y + ty * wd / 2)]
                out.append(f.poly(tri, s, **k))
                break
            d -= L
    return out


def stripes(f, clip, x0, y0, x1, y1, n, w, s=2, ang=90, ln=40):
    """n bands across the region from (x0, y0) to (x1, y1), perpendicular-ish at ang."""
    for i in range(n):
        t = (i + 0.5) / n
        x, y = lerp(x0, x1, t), lerp(y0, y1, t)
        a = math.radians(ang)
        dx, dy = math.cos(a) * ln / 2, math.sin(a) * ln / 2
        f.mark_stroke([(x - dx, y - dy), (x + dx, y + dy)], w, s=s, clip=clip)


def spots(f, clip, cx, cy, rx, ry, n, r, s=2, seed=1):
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, math.tau)
        d = math.sqrt(rng.uniform(0.05, 1))
        f.mark_ell(cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d, r * rng.uniform(0.7, 1.2), r * rng.uniform(0.7, 1.1), s, clip=clip)


def bird_wing(f, x, y, ln, wd, ang, n=4, s=1, scallop=True, **k):
    """Feathered wing from shoulder (x, y); ang = direction of the wing tip."""
    pts = [(0, -wd * 0.35)]
    pts += [(ln * 0.45, -wd * 0.55), (ln, -wd * 0.1)]
    for i in range(n):
        t = 1 - (i + 1) / (n + 0.4)
        pts.append((ln * (t + 0.08), wd * (0.15 + 0.35 * (1 - t))))
        pts.append((ln * t, wd * (0.02 + 0.3 * (1 - t))) if scallop else (ln * t, wd * 0.3))
    pts.append((0, wd * 0.4))
    j = f.poly(rot(pts, ang, x, y), s, **k)
    return j


def bat_wing(f, x, y, ln, wd, ang, n=3, s=2, torn=False, **k):
    pts = [(0, 0), (ln * 0.4, -wd * 0.6), (ln, -wd * 0.25)]
    for i in range(n):
        t = 1 - (i + 1) / n
        ex = ln * (t + 0.5 / n)
        dip = wd * (0.35 if not torn or i % 2 else 0.55)
        pts.append((ex, -wd * 0.25 + dip + wd * 0.5 * (1 - t)))
        pts.append((ln * t + ln * 0.05, wd * 0.15 + wd * 0.45 * (1 - t) + wd * 0.2))
    pts[-1] = (0, wd * 0.5)
    j = f.poly(rot(pts, ang, x, y), s, **k)
    q = rot([(0, 0), (ln, -wd * 0.25)], ang, x, y)
    return j


def bug_wing(f, x, y, ln, wd, ang, s=0, veins=2, **k):
    j = f.ell(x + math.cos(math.radians(ang)) * ln / 2, y + math.sin(math.radians(ang)) * ln / 2, ln / 2, wd / 2, s, ang=ang, **k)
    for i in range(veins):
        t = (i + 1) / (veins + 1)
        f.line(rot([(ln * 0.1, 0), (ln * 0.85, (t - 0.5) * wd * 0.8)], ang, x, y), 2 if s == 0 else 3)
    return j


def fin(f, x, y, ln, wd, ang, s=1, n=3, **k):
    """Spined fin (dorsal / frill) from base centre."""
    pts = [(-wd / 2, 0)]
    for i in range(n):
        t = (i + 1) / n
        pts.append((-wd / 2 + wd * t * 0.85, -ln * (1 - 0.35 * t)))
        pts.append((-wd / 2 + wd * t, -ln * 0.35 * (1 - t) - 1))
    pts.append((wd / 2, 0))
    return f.poly(rot(pts, ang, x, y), s, **k)


def tail_fin(f, x, y, ln, wd, ang=0, s=1, fork=0.45, **k):
    pts = [(0, -wd * 0.12), (ln, -wd / 2), (ln * (1 - fork * 0.5), 0), (ln, wd / 2), (0, wd * 0.12)]
    return f.poly(rot(pts, ang, x, y), s, **k)


def spiral(f, cx, cy, r, turns=2.0, s=3, ang0=0.0):
    pts = []
    n = int(18 * turns)
    for i in range(n + 1):
        t = i / n
        a = math.radians(ang0) + t * turns * math.tau
        rr = r * (1 - t * 0.85)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    f.line(pts, s)


def star(cx, cy, r0, r1, n=5, ang=-90):
    pts = []
    for i in range(n * 2):
        a = math.radians(ang + i * 180 / n)
        r = r0 if i % 2 == 0 else r1
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def cog(cx, cy, r, teeth=8, depth=0.22, ang=0):
    pts = []
    for i in range(teeth * 4):
        a = math.radians(ang) + i * math.tau / (teeth * 4)
        rr = r if (i // 2) % 2 == 0 else r * (1 - depth)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


def blobpoly(cx, cy, rx, ry, n=10, amp=0.15, seed=1, drip=0.0):
    rng = random.Random(seed)
    pts = []
    for i in range(n * 3):
        a = i * math.tau / (n * 3)
        wob = 1 + amp * math.sin(a * n / 2 + rng.uniform(0, 1)) + rng.uniform(-amp, amp) * 0.4
        y = math.sin(a)
        pts.append((cx + math.cos(a) * rx * wob, cy + y * ry * (wob if y < 0 else 1.0)))
    return pts


# ------------------------------------------------------------------ faces
def mouth_smile(f, x, y, w, open_=False, s=3):
    if open_:
        f.poly([(x - w / 2, y), (x + w / 2, y), (x, y + w * 0.55)], 3, line=False, sh=0)
    else:
        f.line([(x - w / 2, y - w * 0.15), (x - w * 0.15, y + w * 0.2), (x + w / 2, y)], s)


def mouth_line(f, pts, s=3):
    f.line(pts, s)


def fang(f, x, y, ln, w=None):
    w = w or ln * 0.6
    f.poly([(x - w / 2, y), (x + w / 2, y), (x, y + ln)], 0, line=True, sh=0, face=True)
