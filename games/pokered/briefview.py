"""Dev tool for writing picture briefs: each picture as [retail with a pixel ruler] [ours].

    python -m games.pokered.briefview <out.png> <name or glob under gfx/> ... [--scale 6] [--cols 3] [--clean-only]

The retail picture (dirty tree) gets a grid every 8 pixels with coordinates on the top and
left edges; ours is regenerated from the current briefs each time (nothing has to be built).
"""
import argparse
import fnmatch
import json
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
from PIL import Image, ImageDraw

from cleanroom.gb import gfx
from games.pokered import generate

HERE = os.path.dirname(os.path.abspath(__file__))
DIRTY = os.environ.get("POKERED_DIRTY", "D:/n64work/pokered/dirty")


def img(idx, s):
    return Image.fromarray(((3 - idx) * 85).astype(np.uint8), "L").convert("RGB").resize(
        (idx.shape[1] * s, idx.shape[0] * s), Image.NEAREST)


def ruled(idx, s):
    h, w = idx.shape
    m = 14
    im = Image.new("RGB", (w * s + m, h * s + m), (40, 44, 60))
    im.paste(img(idx, s), (m, m))
    d = ImageDraw.Draw(im)
    for g in range(0, w + 1, 8):
        d.line([(m + g * s, m), (m + g * s, m + h * s)], fill=(255, 70, 70))
        d.text((m + g * s + 1, 0), str(g), fill=(255, 230, 120))
    for g in range(0, h + 1, 8):
        d.line([(m, m + g * s), (m + w * s, m + g * s)], fill=(255, 70, 70))
        d.text((0, m + g * s + 1), str(g), fill=(255, 230, 120))
    for g in range(4, w, 8):
        d.line([(m + g * s, m), (m + g * s, m + h * s)], fill=(120, 60, 60))
    for g in range(4, h, 8):
        d.line([(m, m + g * s), (m + w * s, m + g * s)], fill=(120, 60, 60))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("names", nargs="+")
    ap.add_argument("--scale", type=int, default=6)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--clean-only", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "spec", "assets.json")))
    generate.load_drawers()
    salts = generate.load_salts()
    rels = []
    for n in a.names:
        rels += [r for r in sorted(spec) if fnmatch.fnmatch(r, n) or r == n]
    cells = []
    for rel in rels:
        sp = spec[rel]
        ours, _ = generate.render(rel, sp)
        ours = generate.constrain(rel, sp, generate.stipple(rel, sp, np.asarray(ours, np.uint8), salts))
        right = ruled(ours, a.scale)
        if a.clean_only:
            cell = right
        else:
            left = ruled(gfx.read_png(os.path.join(DIRTY, "gfx", rel)), a.scale)
            cell = Image.new("RGB", (left.size[0] + right.size[0] + 4, left.size[1] + 12), (40, 44, 60))
            cell.paste(left, (0, 12)); cell.paste(right, (left.size[0] + 4, 12))
        ImageDraw.Draw(cell).text((2, 0), rel, fill=(140, 255, 160))
        cells.append(cell)
    cw, ch = max(c.size[0] for c in cells) + 6, max(c.size[1] for c in cells) + 6
    cols = min(a.cols, len(cells))
    sheet = Image.new("RGB", (cols * cw, ((len(cells) + cols - 1) // cols) * ch), (40, 44, 60))
    for i, c in enumerate(cells):
        sheet.paste(c, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(a.out)
    print(f"{len(cells)} pictures -> {a.out} {sheet.size}")


if __name__ == "__main__":
    main()
