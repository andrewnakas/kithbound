"""Taint scan for Game Boy picture trees (pret-style: PNG sources, 2bpp/1bpp/pic built forms).

    python -m cleanroom.gb.taint <built dirty tree> <built clean tree> <spec assets.json> [--list N]

Every generated picture is compared with the retail pictures in all stored forms:

  tiles     each 8x8 tile of a clean picture against the set of ALL retail tiles
            (from every retail PNG and every built .2bpp/.1bpp, so any tile order counts)
  near      sheets (no kept silhouette): each clean tile against the retail tile at the same
            place; over the pixels where either tile is not the retail tile's background shade,
            NEAR or more are equal
  inside    pictures with a kept silhouette: share of interior pixels equal to retail
  built     built .2bpp/.1bpp/.pic byte streams: shared runs >= RUN bytes (cleanroom.taint windows)
  whole     a picture identical to its retail one

What counts as a coincidence (small low-colour tiles collide by chance):
  * a tile whose rows are all constant or whose columns are all constant (blank, solid, bars);
  * in a silhouette picture, a tile whose interior (2+ pixels inside the kept outline) is one flat
    shade, or smaller than MIN_INTERIOR pixels: it is determined by the kept silhouette plus one
    shade;
  * a rectilinear tile: at most 4 different rows and at most 4 different columns (box corners,
    frames, bevelled edges: a few straight bands, the same in any drawing style);
  * a tile with at most SMALL_INK non-background pixels or at most 2 shades and SMALL_EDGES shade
    changes (a dot, a short stroke, a corner): too little content to be a copy.
Everything else that matches is FAILING and must be redrawn.
"""
import glob
import json
import os
import sys

import numpy as np

from cleanroom import taint as bytescan
from cleanroom.gb import gfx

NEAR = 0.8
MIN_INTERIOR = 12
SMALL_INK = 6
SMALL_EDGES = 14
INSIDE_FAIL = 0.90
RUN = 32


def edges(t):
    return int((t[:, 1:] != t[:, :-1]).sum() + (t[1:, :] != t[:-1, :]).sum())


def bars(t):
    return bool((t == t[:, :1]).all() or (t == t[:1, :]).all())


def simple(t):
    if bars(t):
        return True
    if len({r.tobytes() for r in t}) <= 4 and len({c.tobytes() for c in t.T}) <= 4:
        return True
    vals, counts = np.unique(t, return_counts=True)
    if 64 - counts.max() <= SMALL_INK:
        return True
    return len(vals) <= 2 and edges(t) <= SMALL_EDGES


def depth(inside):
    d = np.zeros(inside.shape, np.int32)
    cur = inside.copy()
    for k in (1, 2):
        d[cur] = k
        p = np.pad(cur, 1, constant_values=False)
        cur = cur & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return d


def retail_tiles(dirty):
    s = set()
    for f in glob.glob(os.path.join(dirty, "gfx", "**", "*.png"), recursive=True):
        for t in gfx.tiles(gfx.read_png(f)):
            s.add(t.tobytes())
    for f in glob.glob(os.path.join(dirty, "gfx", "**", "*.2bpp"), recursive=True):
        for t in gfx.from_2bpp(open(f, "rb").read()):
            s.add(t.tobytes())
    for f in glob.glob(os.path.join(dirty, "gfx", "**", "*.1bpp"), recursive=True):
        for t in gfx.from_1bpp(open(f, "rb").read()):
            s.add(t.tobytes())
    return s


def main(argv):
    dirty, clean, specp = argv[1], argv[2], argv[3]
    nlist = int(argv[argv.index("--list") + 1]) if "--list" in argv else 12
    spec = json.load(open(specp))
    R = retail_tiles(dirty)
    fails, nears, coinc, inside_stats, whole = [], [], 0, [], []
    ntiles = 0
    for rel, a in sorted(spec.items()):
        cp, dp = os.path.join(clean, "gfx", rel), os.path.join(dirty, "gfx", rel)
        if not os.path.exists(cp):
            fails.append((rel, -1, "missing in clean tree"))
            continue
        c, d = gfx.read_png(cp), gfx.read_png(dp)
        if c.shape == d.shape and (c == d).all() and not all(bars(t) for t in gfx.tiles(c)):
            whole.append(rel)
        sil = gfx.unpack_mask(a["sil"], a["h"], a["w"]) if "sil" in a else None
        interior = depth(sil) >= 2 if sil is not None else None
        ct, dt = gfx.tiles(c), gfx.tiles(d)
        it = gfx.tiles(interior.astype(np.uint8)) if interior is not None else None
        for i, t in enumerate(ct):
            ntiles += 1
            if simple(t):
                continue
            flat = False
            if it is not None:
                v = t[it[i] > 0]
                flat = v.size < MIN_INTERIOR or (v == v[0]).all()
            if t.tobytes() in R:
                if flat:
                    coinc += 1
                else:
                    fails.append((rel, i, "tile equals a retail tile"))
                continue
            if it is None and i < len(dt) and not simple(dt[i]):
                r = dt[i]
                bg = np.bincount(r.ravel(), minlength=4).argmax()
                u = (t != bg) | (r != bg)
                if u.sum() >= 8 and float((t == r)[u].mean()) >= NEAR:
                    nears.append((rel, i, f"{float((t == r)[u].mean()):.0%} of the drawn pixels equal the retail tile in place"))
        if interior is not None and interior.sum() >= 40 and c.shape == d.shape:
            share = float((c[interior] == d[interior]).mean())
            inside_stats.append((share, rel))
            if share >= INSIDE_FAIL:
                fails.append((rel, -1, f"interior {share:.0%} equal to retail"))
    # built forms
    built_fail = []
    exts = ("2bpp", "1bpp", "pic")
    dstreams = [open(f, "rb").read() for e in exts for f in glob.glob(os.path.join(dirty, "gfx", "**", "*." + e), recursive=True)]
    index = bytescan.build_index(dstreams)
    cfiles = [] if "--png" in argv else [f for e in exts for f in glob.glob(os.path.join(clean, "gfx", "**", "*." + e), recursive=True)]
    hits = bytescan.scan(index, ((os.path.relpath(f, clean).replace("\\", "/"), open(f, "rb").read()) for f in cfiles))
    pic_fail = [(h[0], h[3]) for h in hits if h[3] >= RUN and h[0].endswith(".pic")]
    short = sum(1 for h in hits if h[3] < RUN)
    for name, run in pic_fail:
        fails.append((name, -1, f"compressed stream shares a {run} byte run"))
    inside_stats.sort(reverse=True)
    med = inside_stats[len(inside_stats) // 2][0] if inside_stats else 0
    top = inside_stats[0] if inside_stats else (0, "-")
    print(f"taint: {len(spec)} pictures, {ntiles} tiles, {len(cfiles)} built files scanned against {len(R)} retail tiles")
    print(f"  coincidences excused: {coinc} silhouette-determined tiles; {short} short byte runs (< {RUN} B) in built files")
    print(f"  interior agreement with retail (silhouette pictures): median {med:.0%}, highest {top[0]:.0%} ({top[1]})")
    print(f"  near copies (>= {NEAR:.0%} of drawn pixels in place): {len(nears)}")
    print(f"  identical pictures: {len(whole)}")
    total = len(fails) + len(nears) + len(whole)
    print(f"  FAILING: {total}")
    by = {}
    for rel, i, why in fails + nears:
        by.setdefault(rel, []).append((i, why))
    for rel in whole:
        by.setdefault(rel, []).append((-1, "identical picture"))
    for rel, items in sorted(by.items(), key=lambda kv: -len(kv[1]))[:nlist]:
        tiles_ = " ".join(f"{i:02X}" for i, _ in items if i >= 0)
        print(f"    {rel}: {len(items)} ({items[0][1]}) {tiles_[:90]}")
    if "--out" in argv:                      # tile numbers only: feedback for the generator's salts
        out = {}
        for rel, i, why in fails:
            if i >= 0 and "sil" in spec.get(rel, {}):
                out.setdefault(rel, []).append(i)
        json.dump(out, open(argv[argv.index("--out") + 1], "w"))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
