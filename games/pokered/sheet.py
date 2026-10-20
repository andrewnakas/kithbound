"""Contact sheet of PNGs from a tree (dev tool; dirty sheets are never committed).

    python -m games.pokered.sheet <tree> <out.png> <glob under gfx/> [--scale 3] [--cols 8] [--grid 8]
    --pair <other tree>   put the same picture from another tree next to each one
"""
import argparse
import glob
import os

from cleanroom.gb import gfx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree"); ap.add_argument("out"); ap.add_argument("globs", nargs="+")
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--grid", type=int, default=0)
    ap.add_argument("--pair", default=None)
    ap.add_argument("--skip", type=int, default=0)
    ap.add_argument("--limit", type=int, default=10000)
    a = ap.parse_args()
    files = []
    for g in a.globs:
        files += sorted(glob.glob(os.path.join(a.tree, "gfx", g), recursive=True))
    files = files[a.skip:a.skip + a.limit]
    items = []
    for f in files:
        rel = os.path.relpath(f, os.path.join(a.tree, "gfx")).replace("\\", "/")
        name = os.path.splitext(os.path.basename(f))[0]
        items.append((name, gfx.read_png(f)))
        if a.pair:
            p = os.path.join(a.pair, "gfx", rel)
            if os.path.exists(p):
                items.append(("=" + name, gfx.read_png(p)))
    im = gfx.sheet(items, a.scale, a.cols, grid=a.grid)
    im.save(a.out)
    print(f"{len(items)} pictures -> {a.out} {im.size}")


if __name__ == "__main__":
    main()
