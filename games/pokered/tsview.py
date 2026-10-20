"""Dev tool: a tileset (tile numbers in hex) and every block of its blockset, or a whole map.

    python -m games.pokered.tsview <tree> <tileset> <out.png> [--blocks 0:64] [--scale 3]
    python -m games.pokered.tsview <tree> <tileset> <out.png> --map maps/PalletTown.blk --width 10

<tree> may be the dirty tree (to learn what a tile is) or the clean tree (to check ours).
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

from cleanroom.gb import gfx

BLOCKSET = {"dojo": "gym", "mart": "pokecenter", "forest_gate": "gate", "museum": "gate",
            "reds_house_1": "reds_house", "reds_house_2": "reds_house"}


def load(tree, name):
    ts = gfx.read_png(os.path.join(tree, "gfx", "tilesets", name + ".png"))
    t = gfx.tiles(ts)
    full = np.zeros((256, 8, 8), np.uint8)
    full[:len(t)] = t
    bst = np.frombuffer(open(os.path.join(tree, "gfx", "blocksets", name + ".bst"), "rb").read(), np.uint8)
    return ts, full, bst.reshape(-1, 16)


def block_img(full, blk):
    out = np.zeros((32, 32), np.uint8)
    for i, t in enumerate(blk):
        out[(i // 4) * 8:(i // 4) * 8 + 8, (i % 4) * 8:(i % 4) * 8 + 8] = full[t]
    return out


def to_img(idx, scale):
    return Image.fromarray(((3 - idx) * 85).astype(np.uint8), "L").convert("RGB").resize(
        (idx.shape[1] * scale, idx.shape[0] * scale), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree"); ap.add_argument("tileset"); ap.add_argument("out")
    ap.add_argument("--blocks", default=None)
    ap.add_argument("--map", default=None); ap.add_argument("--width", type=int, default=10)
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--plain", action="store_true", help="no grid or numbers")
    ap.add_argument("--tiles", action="store_true", help="only the tileset, large, with tile numbers")
    ap.add_argument("--dump", action="store_true", help="print the block table (tile numbers) and exit")
    a = ap.parse_args()
    ts, full, bst = load(a.tree, BLOCKSET.get(a.tileset, a.tileset))
    s = a.scale
    if a.dump:
        for b, r in enumerate(bst):
            print(f"{b:02X}: " + " | ".join(" ".join(f"{t:02X}" for t in r[i * 4:i * 4 + 4]) for i in range(4)))
        return
    if a.tiles:
        k = 12
        im = to_img(ts, k)
        d = ImageDraw.Draw(im)
        for i in range(ts.shape[0] // 8 * 16):
            x, y = (i % 16) * 8 * k, (i // 16) * 8 * k
            d.rectangle([x, y, x + 8 * k, y + 8 * k], outline=(255, 60, 60))
            d.text((x + 2, y), f"{i:02X}", fill=(255, 40, 200))
        im.save(a.out)
        print(f"{a.tileset}: tiles -> {a.out} {im.size}")
        return
    if a.map:
        m = np.frombuffer(open(os.path.join(a.tree, a.map), "rb").read(), np.uint8)
        w = a.width
        h = len(m) // w
        pic = np.zeros((h * 32, w * 32), np.uint8)
        for i in range(w * h):
            pic[(i // w) * 32:(i // w) * 32 + 32, (i % w) * 32:(i % w) * 32 + 32] = block_img(full, bst[m[i]] if m[i] < len(bst) else bst[0])
        to_img(pic, s).save(a.out)
        print(f"map {w}x{h} blocks -> {a.out}")
        return
    lo, hi = (int(x) for x in a.blocks.split(":")) if a.blocks else (0, len(bst))
    hi = min(hi, len(bst))
    ts_s = 6
    top = to_img(ts, ts_s)
    d = ImageDraw.Draw(top)
    if not a.plain:
        for i in range(ts.shape[0] // 8 * 16):
            x, y = (i % 16) * 8 * ts_s, (i // 16) * 8 * ts_s
            d.rectangle([x, y, x + 8 * ts_s, y + 8 * ts_s], outline=(255, 60, 60))
            d.text((x + 2, y), f"{i:02X}", fill=(255, 40, 200))
    cols = 12
    n = hi - lo
    cell = 32 * s + 6
    bw = cols * cell
    im = Image.new("RGB", (max(top.size[0], bw), top.size[1] + 8 + ((n + cols - 1) // cols) * (cell + 10)), (40, 44, 60))
    im.paste(top, (0, 0))
    d = ImageDraw.Draw(im)
    for k in range(n):
        b = lo + k
        x, y = (k % cols) * cell, top.size[1] + 8 + (k // cols) * (cell + 10)
        im.paste(to_img(block_img(full, bst[b]), s), (x, y + 10))
        if not a.plain:
            for g in range(1, 4):
                d.line([(x + g * 8 * s, y + 10), (x + g * 8 * s, y + 10 + 32 * s)], fill=(255, 60, 60))
                d.line([(x, y + 10 + g * 8 * s), (x + 32 * s, y + 10 + g * 8 * s)], fill=(255, 60, 60))
        d.text((x, y - 1), f"{b:02X}: " + " ".join(f"{t:02X}" for t in bst[b][:4]), fill=(255, 230, 120))
    im.save(a.out)
    print(f"{a.tileset}: {len(bst)} blocks, {ts.shape[0] // 8 * 16} tiles -> {a.out} {im.size}")


if __name__ == "__main__":
    main()
