"""Creature, trainer and other figure pictures: the kept silhouette is filled from
our own brief (games/pokered/briefs/*.json), or from the coarse shade grid alone
while a picture has no brief yet.

A brief describes the figure in picture pixels (x right, y down), shades 0 white,
1 light, 2 dark, 3 black. Everything is clipped to the inside of the silhouette and
the black outline is put back on top.

  {"base": 1,                      body shade (omit to shade from the coarse grid)
   "bevel": 0.8,                   strength of the top-left light on the body, 0 = flat
   "ops": [
     {"poly": [[x, y], ...], "s": 2}                 filled region (belly, wing, marking, shadow)
     {"ell": [cx, cy, rx, ry], "s": 0, "line": 3}    filled ellipse, optional outline shade
     {"line": [[x, y], ...], "s": 3, "w": 1}         stroke (limb edge, mouth, crease)
     {"dots": [[x, y], ...], "s": 3}                 single pixels
     {"eye": [cx, cy], "r": [rx, ry], "pupil": [dx, dy], "kind": "round"}
            kinds: round (white ball, black rim, pupil), dot (pupil with a glint), slit,
                   closed (arc), angry (round with a slanted brow)
     {"stripes": [[x, y], ...], "s": 3, "dir": [dx, dy], "gap": 4}   lines across a region
     {"dither": [[x, y], ...], "s": 2}               checker of shade s over a region
     {"shade": [[x, y], ...], "d": 1}                darken (d > 0) or lighten a region by d steps
     {"art": ["..##..", "-++-", ...], "at": [x, y]}  small stamp of your own pixel art (' ' is
                                                     transparent, '.' white, '-' light, '+' dark, '#' black):
                                                     for faces and details that need exact pixels
     {"cut": [[x, y], ...]}                          carve a gap out of the silhouette (between limbs, wings)
     {"add": [[x, y], ...]}                          add a part to the silhouette (tail, antenna, whisker: thin
                                                     parts are not in the kept silhouette); "cut"/"add" also take
                                                     "ell": [cx, cy, rx, ry] or "line": [[x, y], ...] + "w"
   ]}
The kept silhouette is deliberately coarse (gaps closed, thin lines dropped), so the figure's
character comes from the brief.
Any op may carry "over": true to draw over the outline as well.
"""
import glob
import json
import os

import numpy as np

from cleanroom.gb import gfx
from games.pokered import drawn
from games.pokered.art import drawer
from games.pokered.art.tilekit import C

HERE = os.path.dirname(os.path.abspath(__file__))
_BRIEFS = None


def briefs():
    global _BRIEFS
    if _BRIEFS is None:
        _BRIEFS = {}
        for f in sorted(glob.glob(os.path.join(HERE, "..", "briefs", "*.json"))):
            try:
                _BRIEFS.update(json.load(open(f, encoding="utf-8")))
            except Exception as e:
                print(f"  BRIEF FILE FAILED: {os.path.basename(f)}: {e}")
    return _BRIEFS


def _line_mask(c, pts, w):
    m = np.zeros((c.h, c.w), bool)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1) * 2)
        for i in range(n + 1):
            x, y = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
            for dx in range(w):
                for dy in range(w):
                    xi, yi = int(round(x)) + dx, int(round(y)) + dy
                    if 0 <= xi < c.w and 0 <= yi < c.h:
                        m[yi, xi] = True
    return m


def render(a, b):
    h, w = a["h"], a["w"]
    inside = gfx.unpack_mask(a["sil"], h, w)
    c0 = C(w, h)
    for op in b.get("ops", []):
        for key, val in (("cut", False), ("add", True)):
            if key in op:
                v = op[key]
                if v == "ell" or "ell" in op:
                    m = c0.emask(*op["ell"])
                elif "line" in op:
                    m = _line_mask(c0, op["line"], int(op.get("w", 1)))
                else:
                    m = c0.pmask(v)
                inside = (inside | m) if val else (inside & ~m)
    d = drawn.depth_map(inside)
    if "base" in b:
        grid = [[float(b["base"]) + 0.45] * 4] * 4
        out = drawn.autoshade(inside, grid, bevel=b.get("bevel", 0.8))
    else:
        out = drawn.autoshade(inside, a["grid"], bevel=b.get("bevel", 0.9))
    c = C(w, h)
    yy, xx = c.grid()
    edge = inside & (d == 1)
    body = inside & ~edge
    for op in b.get("ops", []):
        clip = inside if op.get("over") else body
        try:
            if "cut" in op or "add" in op:
                continue
            if "poly" in op:
                out[c.pmask(op["poly"]) & clip] = op["s"]
            elif "art" in op:
                x0, y0 = (int(v) for v in op["at"])
                for j, row in enumerate(op["art"]):
                    for i, ch in enumerate(row):
                        x, y = x0 + i, y0 + j
                        if ch != " " and 0 <= x < w and 0 <= y < h and clip[y, x]:
                            out[y, x] = {".": 0, "-": 1, "+": 2, "#": 3}[ch]
            elif "ell" in op:
                m = c.emask(*op["ell"])
                out[m & clip] = op["s"]
                if "line" in op:
                    dm = drawn.depth_map(m, edge_inside=False)
                    out[m & (dm == 1) & clip] = op["line"]
            elif "line" in op:
                out[_line_mask(c, op["line"], int(op.get("w", 1))) & clip] = op.get("s", 3)
            elif "dots" in op:
                for x, y in op["dots"]:
                    x, y = int(round(x)), int(round(y))
                    if 0 <= x < w and 0 <= y < h and clip[y, x]:
                        out[y, x] = op.get("s", 3)
            elif "eye" in op:
                cx, cy = op["eye"]
                rx, ry = op.get("r", [2.5, 2.5])
                px, py = op.get("pupil", [0, 0])
                kind = op.get("kind", "round")
                if kind in ("round", "angry"):
                    m = c.emask(cx, cy, rx, ry)
                    dm = drawn.depth_map(m, edge_inside=False)
                    out[m & clip] = 0
                    out[m & (dm == 1) & clip] = 3
                    pm = c.emask(cx + px, cy + py, max(rx * 0.5, 1.0), max(ry * 0.6, 1.0)) & m
                    out[pm & clip] = 3
                    if kind == "angry":
                        s = 1 if op.get("side", 1) > 0 else -1
                        out[_line_mask(c, [(cx - rx * s, cy - ry - 1), (cx + rx * s, cy - ry + 1)], 1) & clip] = 3
                        out[m & (yy < cy - ry + 1 + (xx - cx + rx * s) * s * 0.0) & False] = 3
                elif kind == "dot":
                    pm = c.emask(cx, cy, max(rx * 0.6, 0.9), max(ry * 0.6, 0.9))
                    out[pm & clip] = 3
                    gx, gy = int(cx - 0.5), int(cy - 0.5)
                    if rx >= 2 and 0 <= gx < w and 0 <= gy < h and clip[gy, gx]:
                        out[gy, gx] = 0
                elif kind == "slit":
                    out[_line_mask(c, [(cx - rx, cy), (cx + rx, cy - py)], 1) & clip] = 3
                elif kind == "closed":
                    pts = [(cx - rx, cy), (cx, cy + ry * 0.5), (cx + rx, cy)]
                    out[_line_mask(c, pts, 1) & clip] = 3
            elif "stripes" in op:
                m = c.pmask(op["stripes"])
                dx, dy = op.get("dir", [1, 0])
                n = (dx * dx + dy * dy) ** 0.5 or 1
                t = np.floor((xx * dx + yy * dy) / n).astype(int)
                out[m & (t % int(op.get("gap", 4)) == 0) & clip] = op.get("s", 3)
            elif "dither" in op:
                out[c.pmask(op["dither"]) & ((xx + yy) % 2 == 0) & clip] = op["s"]
            elif "shade" in op:
                m = c.pmask(op["shade"]) & clip
                out[m] = np.clip(out[m].astype(int) + int(op.get("d", 1)), 0, 3)
        except Exception as e:
            print(f"  brief op failed ({e}): {json.dumps(op)[:80]}")
    out[~inside] = 0
    return out


@drawer("intro/gengar.png")
def intro_gengar(rel, a):
    """Three poses side by side. The second tile of the first column is not part of the
    figure: the intro uses it (tile 1) as the solid black of the letterbox bars."""
    b = briefs().get(rel)
    if "sil" not in a:
        return None                 # retired: retail outlines are no longer kept
    inside = gfx.unpack_mask(a["sil"], a["h"], a["w"])
    # a black shadow figure: the build de-duplicates this picture's tiles, and a flat body keeps
    # the tiles that must be equal looking the same
    out = render(a, b) if b else np.where(inside, 3, 0).astype(np.uint8)
    out[8:16, 0:8] = 3
    return out


@drawer("trade/game_boy.png")
def trade_handheld(rel, a):
    """A handheld console of our own design for the trade animation (48x64)."""
    c = C(a["w"], a["h"])
    c.frame(1, 1, 47, 63, 3, fill=1)
    c.frame(6, 6, 42, 30, 3, fill=2)            # screen bezel
    c.frame(10, 9, 38, 27, 3, fill=0)           # screen
    c.rect(10, 42, 13, 51, 3); c.rect(7, 45, 16, 48, 3)      # d-pad
    c.ellipse(33, 48, 3, 3, 3); c.ellipse(40, 44, 3, 3, 3)   # buttons
    c.line(20, 56, 23, 54, 3); c.line(26, 56, 29, 54, 3)     # start / select
    for k in range(3):
        c.line(36 + k * 3, 60, 39 + k * 3, 55, 2)            # speaker
    return c.a


@drawer("pokemon/*/*.png")
def creature(rel, a):
    b = briefs().get(rel)
    return render(a, b) if b and "sil" in a else None


@drawer("trainers/*.png")
def trainer(rel, a):
    b = briefs().get(rel)
    return render(a, b) if b and "sil" in a else None


@drawer("*/*.png")
def other_figure(rel, a):
    b = briefs().get(rel)
    return render(a, b) if b and "sil" in a else None
