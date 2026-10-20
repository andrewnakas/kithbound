"""Clean room drawing: pictures from the kept facts (silhouette + 4x4 shade grid)
and from our own briefs. Shades: 0 white .. 3 black.
"""
import numpy as np


def _shift(m, dy, dx, fill):
    out = np.full_like(m, fill)
    h, w = m.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = m[ys, xs]
    return out


def depth_map(inside, edge_inside=True):
    """Distance (4-neighbour steps) from each inside pixel to the outside; 1 = on the edge.
    The picture border counts as inside (cropped pictures get no line there)."""
    d = np.zeros(inside.shape, np.int32)
    cur = inside.copy()
    k = 0
    while cur.any():
        k += 1
        d[cur] = k
        er = cur.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            er &= _shift(cur, dy, dx, edge_inside)
        if (er == cur).all():
            d[cur] = k + 8
            break
        cur = er
    return d


def blur(a, n=2):
    a = a.astype(np.float32)
    for _ in range(n):
        p = np.pad(a, 1, mode="edge")
        a = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:] + 4 * p[1:-1, 1:-1]) / 8
    return a


def grid_field(grid, h, w, default=1.0):
    """Bilinear field from a 4x4 grid of cell means (None cells take their neighbours' mean)."""
    g = np.array([[np.nan if v is None else v for v in row] for row in grid], np.float32)
    if np.isnan(g).all():
        g[:] = default
    while np.isnan(g).any():
        p = np.pad(g, 1, constant_values=np.nan)
        nb = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        cnt = (~np.isnan(nb)).sum(0)
        fill = np.where(cnt > 0, np.nansum(nb, 0) / np.maximum(cnt, 1), np.nan)
        g = np.where(np.isnan(g), fill, g)
    ny, nx = g.shape
    y = (np.arange(h) + 0.5) / h * ny - 0.5
    x = (np.arange(w) + 0.5) / w * nx - 0.5
    y0 = np.clip(np.floor(y).astype(int), 0, ny - 2); fy = np.clip(y - y0, 0, 1)[:, None]
    x0 = np.clip(np.floor(x).astype(int), 0, nx - 2); fx = np.clip(x - x0, 0, 1)[None, :]
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return a * (1 - fy) * (1 - fx) + b * (1 - fy) * fx + c * fy * (1 - fx) + d * fy * fx


def autoshade(inside, grid, bias=0.45, bevel=0.9, line=True):
    """Flat-shaded figure: black outline on the silhouette edge, body tone from the
    coarse grid, lit from the top left."""
    h, w = inside.shape
    d = depth_map(inside)
    tone = grid_field(grid, h, w) - bias
    soft = blur(inside, 3)
    gy, gx = np.gradient(soft)
    lit = (gx + gy) * 2.0                 # > 0 on the top-left faces
    tone = tone - bevel * np.clip(lit, -1, 1) * (d <= 4)
    out = np.zeros((h, w), np.uint8)
    out[tone >= 0.55] = 1
    out[tone >= 1.45] = 2
    out[tone >= 2.6] = 3
    out[~inside] = 0
    if line:
        out[inside & (d == 1)] = 3
    return out
