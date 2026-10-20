"""Overworld sprites (16x16 frames). Each frame is rebuilt from the kept silhouette
and the 4x4 shade grid of that frame, then given drawn features: people get a face
(skin, eyes) by frame direction; things get their own details from THINGS.

Frame order in a strip: stand down, up, left, then walk down, up, left.
Sprite shades: 0 transparent, 1 light (skin), 2 dark, 3 black.
"""
import json
import os

import numpy as np

from cleanroom.gb import gfx
from games.pokered import drawn
from games.pokered.art import drawer

FACING = ["down", "up", "side", "down", "up", "side"]


def base(m, grid):
    f = drawn.autoshade(m, grid, bias=0.25, bevel=0.0)
    f[m & (f == 0)] = 1
    return f


def _shade(v, hi, lo):
    return 3 if v >= hi else (2 if v >= lo else 1)


def person(m, grid, facing, opts):
    """A little figure in bands: hair or hat, face, top, legs. Band shades come from
    the centre cells of the frame's grid; the layout is ours."""
    f = np.zeros((16, 16), np.uint8)
    if not m.any():
        return f
    d = drawn.depth_map(m, edge_inside=False)
    rows = np.nonzero(m.any(1))[0]
    top, bot = int(rows[0]), int(rows[-1])
    xs = np.nonzero(m[top + 2:top + 8].any(0))[0]
    cx = (xs[0] + xs[-1]) / 2
    yy, xx = np.mgrid[0:16, 0:16]
    inner = m & (d >= 2)
    c = [((r[1] if r[1] is not None else 2.0) + (r[2] if r[2] is not None else 2.0)) / 2 for r in grid]
    hair = opts.get("hair", 3 if c[0] >= 2.15 else 2)      # on screen 1 is white, 2 light grey, 3 black
    body = opts.get("top", _shade(c[2], 2.6, 2.0))
    legs = opts.get("legs", _shade(c[3], 2.6, 2.0))
    f[m] = 3
    ry = yy - top
    f[inner & (ry <= 3)] = hair
    band = inner & (ry >= 4) & (ry <= 8)
    f[band] = hair
    ey = top + 5 + opts.get("eye_dy", 0)
    if facing == "down":
        f[band & (abs(xx - cx) <= 3.5)] = 1
        for ex in (int(np.floor(cx - 1.5)), int(np.ceil(cx + 1.5))):
            f[ey:ey + 2, ex][m[ey:ey + 2, ex]] = 3
        if opts.get("glasses"):
            f[ey, int(np.floor(cx - 2.5)):int(np.ceil(cx + 2.5)) + 1] = 3
        if opts.get("beard"):
            f[band & (abs(xx - cx) <= 3.5) & (ry >= 7)] = 2
    elif facing == "side":
        f[band & (xx >= cx - 4.5) & (xx <= cx + 0.5)] = 1
        ex = int(np.floor(cx - 2))
        f[ey:ey + 2, ex][m[ey:ey + 2, ex]] = 3
    else:
        f[band & (ry == 8)] = 1
    f[inner & (ry >= 9) & (ry <= 12)] = body
    f[inner & (ry >= 13)] = legs
    torso = inner & (ry >= 9) & (ry <= 12)
    if facing != "side":                             # arms: a line each side of the chest, hands below
        cols = np.nonzero(torso.any(0))[0]
        if cols.size >= 7:
            for xa, xh in ((cols[0] + 2, cols[0]), (cols[-1] - 2, cols[-1])):
                f[torso & (xx == xa)] = 2 if body == 3 else 3
                f[torso & (xx >= min(xa, xh)) & (xx <= max(xa, xh)) & (xx != xa) & (ry >= 11)] = 1
    else:
        f[torso & (xx == int(cx)) & (ry <= 11)] = 2 if body == 3 else 3
    f[inner & (ry == 13) & (d >= 2)] = 3 if legs != 3 else 2      # belt
    if facing != "side":
        f[inner & (ry >= 14) & (xx == int(round(cx)))] = 3 if legs != 3 else 2
    f[bot][m[bot]] = 3
    return f


def ball(m, grid, facing, opts):
    f = base(m, grid)
    ys = np.nonzero(m.any(1))[0]; xs = np.nonzero(m.any(0))[0]
    cy, cx = (ys[0] + ys[-1]) // 2, (xs[0] + xs[-1]) // 2
    yy, xx = np.mgrid[0:16, 0:16]
    f[m & (yy < cy)] = 2
    f[m & (yy > cy)] = 1
    f[m & (yy == cy)] = 3
    f[cy - 1:cy + 2, cx:cx + 2][m[cy - 1:cy + 2, cx:cx + 2]] = 1
    d = drawn.depth_map(m, edge_inside=False)
    f[m & (d == 1)] = 3
    return f


def boulder(m, grid, facing, opts):
    f = base(m, grid)
    d = drawn.depth_map(m, edge_inside=False)
    yy, xx = np.mgrid[0:16, 0:16]
    f[m & (d >= 2)] = 2
    f[m & (d >= 2) & (xx + yy < 13)] = 1
    for x, y in ((9, 6), (10, 7), (10, 8), (6, 10), (7, 11), (11, 11)):
        if m[y, x]:
            f[y, x] = 3
    return f


def sheet_of_paper(m, grid, facing, opts):
    f = base(m, grid)
    d = drawn.depth_map(m, edge_inside=False)
    yy, xx = np.mgrid[0:16, 0:16]
    inner = m & (d >= 2)
    f[inner] = 1
    f[inner & (yy % 3 == 2) & (d >= 3)] = 2
    return f


def creature(m, grid, facing, opts):
    """Animal sprites: shading from the grid plus an eye on the head side."""
    f = base(m, grid)
    if not m.any():
        return f
    rows = np.nonzero(m.any(1))[0]
    top = int(rows[0])
    xs = np.nonzero(m[top + 2:top + 7].any(0))[0]
    cx = (xs[0] + xs[-1]) / 2
    ey = top + 4
    if facing == "down":
        for ex in (int(np.floor(cx - 1.5)), int(np.ceil(cx + 1.5))):
            if m[ey, ex]:
                f[ey, ex] = 3
    elif facing == "side":
        ex = int(np.floor(cx - 2))
        if m[ey, ex]:
            f[ey, ex] = 3
    return f


THINGS = {
    "poke_ball": ball, "boulder": boulder, "paper": sheet_of_paper, "clipboard": sheet_of_paper,
    "pokedex": sheet_of_paper, "fossil": boulder, "old_amber": boulder,
    "bird": creature, "fairy": creature, "monster": creature, "seel": creature, "snorlax": creature,
}
OPTS = {
    "oak": {}, "gramps": {"beard": True}, "gambler": {}, "scientist": {"glasses": True},
    "super_nerd": {"glasses": True}, "bike_shop_clerk": {"glasses": True}, "hiker": {"beard": True},
    "fisher": {}, "mr_fuji": {"beard": True}, "warden": {"beard": True}, "gentleman": {},
}


_SB = None


def sprite_briefs():
    """games/pokered/sprite_briefs.json: our own per-character drawing on top of the bands.
       {"oak": {"opts": {"hair": 2, "top": 1, "legs": 2, "glasses": false, "beard": false},
                "down": [16 rows of 16 chars], "up": [...], "side": [...],
                "walk_down": [...], "walk_up": [...], "walk_side": [...]}}
    Stamp characters: ' ' keep what is there, '.' white, '-' light grey, '#' black (as seen on
    screen). Stamps are clipped to the kept silhouette. Without walk_* stamps the walking frames
    take the first 10 rows (the head) of the standing stamp of the same direction."""
    global _SB
    if _SB is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprite_briefs.json")
        try:
            _SB = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        except Exception as e:
            print(f"  SPRITE BRIEFS FAILED: {e}")
            _SB = {}
    return _SB


def stamp(f, m, rows, limit=16):
    for j, row in enumerate(rows[:limit]):
        for i, ch in enumerate(row[:16]):
            if ch != " " and m[j, i]:
                f[j, i] = {".": 1, "-": 2, "#": 3}[ch]
    return f


@drawer("sprites/*.png")
def sprite(rel, a):
    name = os.path.basename(rel)[:-4]
    if "sil" not in a:
        return None                 # retired: retail outlines are no longer kept
    h, w = a["h"], a["w"]
    inside = gfx.unpack_mask(a["sil"], h, w)
    out = np.zeros((h, w), np.uint8)
    fn = THINGS.get(name, person)
    b = sprite_briefs().get(name, {})
    opts = dict(OPTS.get(name, {}), **b.get("opts", {}))
    for n, y in enumerate(range(0, h, 16)):
        m = inside[y:y + 16]
        f = fn(m, a["grid"][n], FACING[n % 6], opts)
        face = FACING[n % 6]
        if n >= 3 and ("walk_" + face) in b:
            f = stamp(f, m, b["walk_" + face])
        elif face in b:
            f = stamp(f, m, b[face], 16 if n < 3 else 10)
        out[y:y + 16] = f
    out[~inside] = 0
    return out
