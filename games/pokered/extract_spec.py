"""DIRTY ROOM: read the retail pictures of a built pret/pokered tree and keep
only the approved coarse facts, as games/pokered/spec/assets.json.

    python -m games.pokered.extract_spec <built dirty tree>

Kept per picture: path, size, bit depth, kind, and
  pic     one drawn subject: 4x4 grid of mean shade (inside pixels) + 1-bit silhouette
  sprite  a strip of 16x16 frames: the same two facts per frame
  sheet   a sheet of tiles/glyphs: 4x4 grid for the whole sheet + which tiles are blank
          (no silhouette: it would be a copy of the glyphs)
  + for the two pictures the build de-duplicates: which tiles are equal (layout fact,
    the tilemaps in the code index the de-duplicated tiles).
Nothing else leaves the dirty room.
"""
import glob
import json
import os
import sys

import numpy as np

from cleanroom.gb import gfx

HERE = os.path.dirname(os.path.abspath(__file__))

PIC = ("pokemon/front/", "pokemon/back/", "trainers/", "player/", "battle/oldmanb", "battle/ghost",
       "intro/", "title/player", "trade/game_boy",
       # sheets of separate drawn subjects (effects, icons, symbols), not glyphs or map tiles
       "icons/", "battle/move_anim_", "overworld/red_fish_", "overworld/fishing_rod", "overworld/smoke",
       "trade/bubble", "trade/cable_ball", "trade/link_cable", "trainer_card/badges", "slots/red_slots_2",
       "slots/blue_slots_2", "splash/falling_star")
TRIM = ("tilesets/", "slots/red_slots_1", "slots/blue_slots_1", "battle/move_anim_")   # trailing blank tiles are trimmed
# drawn on a white background (no real transparency): their silhouette is closed and coarsened;
# the rest are sprite sheets whose shade 0 is real transparency (kept as the 1-bit alpha)
FIGURE = ("pokemon/", "trainers/", "player/", "battle/oldmanb", "battle/ghost", "intro/", "title/player")
DEDUPE = ("intro/gengar", "trade/game_boy")


def kind_of(rel):
    if rel.startswith("sprites/"):
        return "sprite"
    if rel.startswith(PIC):
        return "pic"
    return "sheet"


def dilate(m, r):
    for _ in range(r):
        p = np.pad(m, 1, constant_values=False)
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


def silhouette(idx, r=3):
    """Inside of a figure drawn on white. The retail line art often leaves the outline open
    where a white body meets the white background, so gaps up to 2r pixels are closed:
    the ink is grown by r, the outside is flooded from the border, then grown back by r."""
    ink = idx != 0
    grown = dilate(ink, r)
    pad = np.pad(grown, r + 1, constant_values=False)          # room to flood around figures that touch the border
    out = gfx.flood_outside((pad).astype(np.uint8))
    out = dilate(out, r)[r + 1:-(r + 1), r + 1:-(r + 1)]
    inside = ~(out & ~ink)
    # drop what is only a line (whiskers, motion marks, open outline strokes): a part survives
    # if it is at least 2 pixels thick somewhere near, so no retail line art is carried over
    core = ~dilate(~inside, 1)
    return inside & dilate(core, 2)


def grid4(idx, inside):
    """4x4 grid of the mean shade of the inside pixels (None where a cell is empty)."""
    h, w = idx.shape
    ys = [round(i * h / 4) for i in range(5)]
    xs = [round(i * w / 4) for i in range(5)]
    out = []
    for j in range(4):
        row = []
        for i in range(4):
            m = inside[ys[j]:ys[j + 1], xs[i]:xs[i + 1]]
            v = idx[ys[j]:ys[j + 1], xs[i]:xs[i + 1]][m]
            row.append(round(float(v.mean()), 2) if v.size else None)
        out.append(row)
    return out


def main(tree):
    assets = {}
    counts = {}
    for f in sorted(glob.glob(os.path.join(tree, "gfx", "**", "*.png"), recursive=True)):
        rel = os.path.relpath(f, os.path.join(tree, "gfx")).replace("\\", "/")
        base = f[:-4]
        built = [e for e in ("2bpp", "1bpp", "pic") if os.path.exists(base + "." + e)]
        if not built:
            continue                                    # not part of Red/Blue: not regenerated
        idx = gfx.read_png(f)
        h, w = idx.shape
        kind = kind_of(rel)
        a = {"w": w, "h": h, "depth": 1 if "1bpp" in built else 2, "kind": kind}
        if kind == "pic":
            inside = silhouette(idx) if rel.startswith(FIGURE) else ~gfx.flood_outside(idx)
            a["grid"] = grid4(idx, inside)
            a["sil"] = gfx.pack_mask(inside)
        elif kind == "sprite":
            inside = idx != 0
            a["grid"] = [grid4(idx[y:y + 16], inside[y:y + 16]) for y in range(0, h, 16)]
            a["sil"] = gfx.pack_mask(inside)
        else:
            a["grid"] = grid4(idx, np.ones_like(idx, bool))
        if rel.startswith(TRIM):
            a["blank"] = [int(i) for i, t in enumerate(gfx.tiles(idx)) if not t.any()]
        if rel.startswith(DEDUPE):
            seen, cls = {}, []
            for t in gfx.tiles(idx):
                cls.append(seen.setdefault(t.tobytes(), len(seen)))
            a["classes"] = cls
        assets[rel] = a
        counts[kind] = counts.get(kind, 0) + 1
    os.makedirs(os.path.join(HERE, "spec"), exist_ok=True)
    out = os.path.join(HERE, "spec", "assets.json")
    with open(out, "w") as fh:
        json.dump(assets, fh, separators=(",", ":"), sort_keys=True)
    print(f"spec: {len(assets)} pictures {counts} -> {out} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1])
