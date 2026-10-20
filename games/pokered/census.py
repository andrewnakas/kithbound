"""Dirty room: one-screen census of the picture assets (sizes, depth, use).

    python -m games.pokered.census <built dirty tree>
"""
import collections
import glob
import os
import sys

from PIL import Image


def main(tree):
    c = collections.Counter()
    unused = collections.Counter()
    for f in sorted(glob.glob(os.path.join(tree, "gfx", "**", "*.png"), recursive=True)):
        rel = os.path.relpath(f, os.path.join(tree, "gfx")).replace("\\", "/")
        d = os.path.dirname(rel)
        im = Image.open(f)
        base = f[:-4]
        built = [e for e in ("2bpp", "1bpp", "pic") if os.path.exists(base + "." + e)]
        if not built:
            unused[d] += 1
            continue
        c[(d, im.size, im.mode, "+".join(built))] += 1
    for k, v in sorted(c.items()):
        print(v, *k)
    print("unused:", dict(unused))


if __name__ == "__main__":
    main(sys.argv[1])
