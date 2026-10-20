"""Render maps of a tree (its .blk + blocksets + clean tileset pictures) to one sheet.

    python -m games.pokered.maps_view <tree> <out.png> Label1,Label2,...  [--tiles <tree with gfx pngs>]
"""
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

from games.pokered.maps_kit import Kit


def tileset_png(kit, tiles_tree, const):
    ts = kit.tilesets[const]
    s = kit.read("gfx/tilesets.asm")
    m = re.search(ts.name + r"_GFX::\s*INCBIN \"([^\"]+)\"", s)
    if not m:
        # shared GFX label lines: find the INCBIN after the label
        i = s.index(ts.name + "_GFX::")
        m = re.search(r"INCBIN \"([^\"]+)\"", s[i:])
    path = os.path.join(tiles_tree, m.group(1).replace(".2bpp", ".png"))
    return np.asarray(Image.open(path).convert("L"))


def render(kit, tiles_tree, label):
    mp = kit.maps[label]
    b = kit.blocks(mp)
    ts = kit.tilesets[mp.tileset]
    pic = tileset_png(kit, tiles_tree, mp.tileset)
    tw = pic.shape[1] // 8
    out = np.full((mp.h * 32, mp.w * 32), 255, np.uint8)
    for by in range(mp.h):
        for bx in range(mp.w):
            for i, t in enumerate(ts.blocks[b[by, bx]]):
                ty, tx = divmod(int(t), tw)
                if ty * 8 + 8 <= pic.shape[0]:
                    out[by * 32 + (i // 4) * 8:by * 32 + (i // 4) * 8 + 8,
                        bx * 32 + (i % 4) * 8:bx * 32 + (i % 4) * 8 + 8] = pic[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8]
    img = Image.fromarray(out).convert("RGB")
    d = ImageDraw.Draw(img)
    for (x, y, dest, i) in mp.warps:
        d.rectangle([x * 16 + 4, y * 16 + 4, x * 16 + 11, y * 16 + 11], outline=(255, 0, 0))
    for (x, y, sp, mv) in mp.objects:
        d.ellipse([x * 16 + 4, y * 16 + 4, x * 16 + 11, y * 16 + 11], outline=(0, 120, 255))
    return img


def main(argv):
    tree, out, labels = argv[1], argv[2], argv[3].split(",")
    tiles = argv[argv.index("--tiles") + 1] if "--tiles" in argv else tree
    kit = Kit(tree)
    imgs = [(l, render(kit, tiles, l)) for l in labels]
    W = sum(i.width for _, i in imgs) + 8 * len(imgs)
    H = max(i.height for _, i in imgs) + 14
    sheet = Image.new("RGB", (W, H), (40, 44, 60))
    x = 0
    d = ImageDraw.Draw(sheet)
    for l, i in imgs:
        sheet.paste(i, (x, 14))
        d.text((x, 1), l, fill=(255, 255, 0))
        x += i.width + 8
    sheet.save(out)
    print("sheet ->", out)


if __name__ == "__main__":
    main(sys.argv)
