"""16:9 poster drawn from the clean build only: a town rendered from our tiles, our
title lettering, three of our creature pictures. No retail art.

    python -m games.pokered.poster <clean tree> poster.png
"""
import os
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
from PIL import Image

from cleanroom.gb import gfx
from games.pokered import tsview
from games.pokered.art.tilekit import C
from games.pokered.art.text import ptext, width

W, H = 1280, 720


def tint(idx, pal, scale):
    rgb = np.array(pal, np.uint8)[idx]
    return Image.fromarray(rgb, "RGB").resize((idx.shape[1] * scale, idx.shape[0] * scale), Image.NEAREST)


def text_img(s, pal, scale, small=False):
    c = C(width(s, small) + 2, 9)
    ptext(c, s, 1, 1, small=small)
    return tint(c.a, pal, scale)


def main(tree, out):
    grass = [(232, 244, 216), (150, 200, 120), (64, 120, 84), (24, 36, 40)]
    ts, full, bst = tsview.load(tree, "overworld")
    m = np.frombuffer(open(os.path.join(tree, "maps", "PalletTown.blk"), "rb").read(), np.uint8)
    w = 10
    h = len(m) // w
    pic = np.zeros((h * 32, w * 32), np.uint8)
    for i in range(w * h):
        pic[(i // w) * 32:(i // w) * 32 + 32, (i % w) * 32:(i % w) * 32 + 32] = tsview.block_img(full, bst[m[i]])
    town = tint(pic, grass, 3)                                   # 960 x 864
    im = Image.new("RGB", (W, H), (16, 18, 24))
    im.paste(town.crop((0, 60, 800, 780)), (0, 0))
    panel = Image.new("RGB", (480, H), (16, 18, 24))
    logo = gfx.read_png(os.path.join(tree, "gfx", "title", "pokemon_logo.png"))
    lg = tint(logo, [(16, 18, 24), (250, 208, 60), (190, 120, 30), (250, 250, 250)], 3)
    panel.paste(lg, ((480 - lg.size[0]) // 2, 40))
    ink = [(16, 18, 24), (0, 0, 0), (0, 0, 0), (240, 240, 244)]
    red = [(16, 18, 24), (0, 0, 0), (0, 0, 0), (232, 80, 70)]
    blue = [(16, 18, 24), (0, 0, 0), (0, 0, 0), (90, 140, 240)]
    dim = [(16, 18, 24), (0, 0, 0), (0, 0, 0), (150, 158, 172)]
    y = 230
    parts = [("RED", red), (" AND ", ink), ("BLUE", blue)]
    imgs = [text_img(s, p, 5) for s, p in parts]
    x = (480 - sum(i.size[0] for i in imgs)) // 2
    for i in imgs:
        panel.paste(i, (x, y)); x += i.size[0]
    t = text_img("CLEAN ROOM", dim, 4, small=True)
    panel.paste(t, ((480 - t.size[0]) // 2, 296))
    pals = [[(16, 18, 24), (120, 200, 130), (50, 120, 90), (236, 240, 232)],
            [(16, 18, 24), (240, 150, 80), (190, 80, 50), (250, 240, 228)],
            [(16, 18, 24), (120, 180, 240), (60, 100, 190), (236, 240, 250)]]
    for k, name in enumerate(("bulbasaur", "charmander", "squirtle")):
        p = gfx.read_png(os.path.join(tree, "gfx", "pokemon", "front", name + ".png"))
        # figures are drawn on white: flip shades so the page background shows through
        g = tint(p, [pals[k][0], pals[k][1], pals[k][2], pals[k][3]], 3)
        panel.paste(g, (30 + k * 145 + (120 - g.size[0]) // 2, 380 + (150 - g.size[1]) // 2))
    t = text_img("EVERY PICTURE REDRAWN", dim, 3, small=True)
    panel.paste(t, ((480 - t.size[0]) // 2, 580))
    t = text_img("NO ORIGINAL GAME FILES NEEDED", dim, 3, small=True)
    panel.paste(t, ((480 - t.size[0]) // 2, 610))
    im.paste(panel, (800, 0))
    im.save(out)
    print(f"poster -> {out} {im.size}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
