"""Our own pixel art for the clean build. Shades: 0 white, 1 light, 2 dark, 3 black.

Tiles are written as text, one string per row: '.' 0, '-' 1, '+' 2, '#' 3.
"""
import numpy as np

DRAWERS = []          # (path pattern, function(rel, spec) -> picture), first match wins
TILEMAPS = {}         # tree-relative path -> function() -> bytes (tile maps that go with our pictures)


def tilemap(path):
    def reg(fn):
        TILEMAPS[path] = fn
        return fn
    return reg


def drawer(pattern):
    def reg(fn):
        DRAWERS.append((pattern, fn))
        return fn
    return reg


CH = {".": 0, " ": 0, "0": 0, "-": 1, "+": 2, "#": 3, "1": 3}


def art(rows, w=None, h=None):
    """Text rows -> array, padded with white to (h, w)."""
    if isinstance(rows, str):
        rows = rows.split("/")
    hh = h or len(rows)
    ww = w or max(len(r) for r in rows)
    a = np.zeros((hh, ww), np.uint8)
    for y, r in enumerate(rows[:hh]):
        for x, c in enumerate(r[:ww]):
            a[y, x] = CH[c]
    return a


def blit(dst, src, x, y, transparent=None):
    h, w = src.shape
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0:
        return dst
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    if transparent is None:
        dst[y0:y1, x0:x1] = s
    else:
        m = s != transparent
        dst[y0:y1, x0:x1][m] = s[m]
    return dst


def sheet(tiles, w, h):
    """List of 8x8 tiles (or None) in row-major order -> picture."""
    out = np.zeros((h, w), np.uint8)
    for i, t in enumerate(tiles):
        if t is None:
            continue
        x, y = (i % (w // 8)) * 8, (i // (w // 8)) * 8
        if y < h:
            blit(out, np.asarray(t, np.uint8)[:8, :8], x, y)
    return out
