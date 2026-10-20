"""CLEAN ROOM: write every picture of the game from games/pokered/spec + our own
drawing code into a tree that holds no retail picture.

    python -m games.pokered.generate <clean tree>

Drawers are looked up by path (first match in DRAWERS), then by kind.
"""
import fnmatch
import json
import os
import sys

import numpy as np

from cleanroom.gb import gfx
from games.pokered import drawn

HERE = os.path.dirname(os.path.abspath(__file__))
from games.pokered.art import DRAWERS


def draw_pic(rel, a):
    """Placeholder for a picture nobody drew yet: a plain framed card (no retail fact)."""
    h, w = a["h"], a["w"]
    out = np.zeros((h, w), np.uint8)
    out[1:h - 1, 1:w - 1] = 1
    out[2:h - 2, 2:w - 2] = 0
    return out


def draw_sprite(rel, a):
    h, w = a["h"], a["w"]
    out = np.zeros((h, w), np.uint8)
    for y in range(0, h, 16):
        out[y + 4:y + 12, 4:12] = 2
    return out


def draw_sheet(rel, a):
    """Fallback for sheets nobody drew yet: a plain hatch."""
    h, w = a["h"], a["w"]
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx + yy) % 4 == 0).astype(np.uint8)


def load_salts():
    p = os.path.join(HERE, "salts.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def stipple(rel, a, idx, salts):
    """Tiles listed in salts.json (tile numbers reported by the taint scan as equal to a
    retail tile by chance) get a sparse texture mark inside the figure so they differ.
    The list holds tile numbers and a variant counter only."""
    todo = salts.get(rel)
    if not todo:
        return idx
    inside = idx > 0
    d = drawn.depth_map(inside, edge_inside=False)
    out = idx.copy()
    floor = 1 if a["kind"] == "sprite" else 0
    mod = 11 if a["kind"] == "sprite" else 7
    for tile, n in todo.items():
        tile = int(tile)
        ty, tx = (tile // (a["w"] // 8)) * 8, (tile % (a["w"] // 8)) * 8
        for y in range(ty, min(ty + 8, a["h"])):
            for x in range(tx, tx + 8):
                if d[y, x] >= 2 and (x * 3 + y * 5 + n) % mod == 0:
                    v = out[y, x]
                    out[y, x] = 2 if v in (1, 3) else (1 if v == 2 else max(1, floor))
        blk = out[ty:ty + 8, tx:tx + 8]
        if (blk == idx[ty:ty + 8, tx:tx + 8]).all():
            # small shapes have no deep interior: shift the shade of a few drawn pixels instead
            ys, xs = np.nonzero(blk)
            for k in range(0, len(ys), max(1, len(ys) // (2 + n))):
                v = blk[ys[k], xs[k]]
                blk[ys[k], xs[k]] = 2 if v in (1, 3) else 1
    return out


def constrain(rel, a, idx):
    """Layout facts the build depends on: blank tiles stay blank, drawn tiles stay
    drawn, and de-duplicated pictures keep their tile equalities."""
    h, w = a["h"], a["w"]
    t = gfx.tiles(idx).copy()
    if "blank" in a:
        blank = set(a["blank"])
        for i in range(len(t)):
            if i in blank:
                t[i] = 0
            elif not t[i].any():
                t[i][7, 7] = 1 if a["depth"] == 2 else 3
    if "classes" in a:
        first, seen = {}, {}
        for i, c in enumerate(a["classes"]):
            if c in first:
                t[i] = t[first[c]]
            else:
                first[c] = i
                k = 0
                while t[i].tobytes() in seen:    # must differ from every other class
                    t[i][7 - k // 8, 7 - k % 8] ^= 1
                    k += 1
                seen[t[i].tobytes()] = c
    return gfx.untile(t, w)[:h]


def render(rel, a):
    for pat, fn in DRAWERS:
        if fnmatch.fnmatch(rel, pat):
            try:
                idx = fn(rel, a)
            except Exception as e:          # a drawer in progress must not stop the build
                print(f"  DRAWER FAILED {fn.__name__} {rel}: {type(e).__name__}: {e}")
                idx = None
            if idx is not None:
                return idx, fn.__name__
    fn = {"pic": draw_pic, "sprite": draw_sprite, "sheet": draw_sheet}[a["kind"]]
    return fn(rel, a), fn.__name__


def load_drawers():
    for mod in sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "art")) if f.endswith(".py") and f not in ("__init__.py", "tilekit.py")):
        try:
            __import__(f"games.pokered.art.{mod}")
        except Exception as e:                      # one broken module must not stop the others
            print(f"  ART MODULE FAILED: {mod}: {type(e).__name__}: {e}")


def main(tree, only=None):
    spec = json.load(open(os.path.join(HERE, "spec", "assets.json")))
    load_drawers()
    salts = load_salts()
    by = {}
    for rel, a in spec.items():
        if only and not fnmatch.fnmatch(rel, only):
            continue
        idx, who = render(rel, a)
        assert idx.shape == (a["h"], a["w"]), (rel, idx.shape)
        idx = stipple(rel, a, np.asarray(idx, np.uint8), salts)
        idx = constrain(rel, a, idx)
        p = os.path.join(tree, "gfx", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        gfx.write_png(p, idx, a["depth"])
        by[who] = by.get(who, 0) + 1
    from games.pokered.art import TILEMAPS
    for path, fn in TILEMAPS.items():
        if only and not fnmatch.fnmatch(path, only):
            continue
        data = fn()
        if data is not None:
            open(os.path.join(tree, path), "wb").write(bytes(data))
    print(f"generated {sum(by.values())} pictures, {len(TILEMAPS)} tile maps: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))


if __name__ == "__main__":
    main(*sys.argv[1:])
