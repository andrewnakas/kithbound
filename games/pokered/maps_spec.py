"""DIRTY ROOM: gameplay anchors and connectivity of every map -> spec/maps.json.

Kept (structure + anchors only, per the owner's bar):
  * size, tileset, border block (engine facts)
  * anchor blocks: the block under each warp (with the building around an outdoor door),
    under signs / hidden events / NPCs that stand on solid ground (counters, PCs),
    blocks that scripts replace (ReplaceTileBlock coordinates), counter blocks
  * terminals: steps that must be walkable (warps, NPCs, item balls, sign fronts, script
    trigger coordinates, fly / special warp landing spots) with their connectivity region
  * the region graph: which walk regions join through water (surf) or a cut tree
  * edge openings toward connected maps
Not kept: where anything else is. The clean generator lays out paths, rooms and scenery.

    python -m games.pokered.maps_spec <pristine tree>
"""
import json
import os
import re
import sys
from collections import Counter

import numpy as np
from scipy import ndimage

from games.pokered.maps_kit import Kit

HERE = os.path.dirname(os.path.abspath(__file__))
WATER_TILES = {0x14, 0x32, 0x48}


def cut_blocks(kit):
    s = kit.read("data/tilesets/cut_tree_blocks.asm")
    return {int(a, 16) for a, b in re.findall(r"db \$([0-9A-Fa-f]+), \$([0-9A-Fa-f]+)", s)}


def hidden_events(kit):
    s = kit.read("data/events/hidden_events.asm")
    out, cur = {}, None
    for line in s.split("\n"):
        m = re.match(r"\s*hidden_events_for (\w+)", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"\s*hidden_(?:event|text_predef)\s+(\d+),\s*(\d+)", line)
        if m and cur:
            out.setdefault(cur, []).append((int(m.group(1)), int(m.group(2))))
    return out


def script_coords(kit):
    """{map label: {"trig": [(x, y)], "blocks": [(by, bx)]}} from scripts/<label>.asm."""
    out = {}
    for p in os.listdir(os.path.join(kit.tree, "scripts")):
        lab = p[:-4]
        s = open(os.path.join(kit.tree, "scripts", p), encoding="utf8").read()
        trig = [(int(x), int(y)) for x, y in re.findall(r"dbmapcoord\s+(\d+),\s*(\d+)", s)]
        lines = s.split("\n")
        blocks = []
        for i, l in enumerate(lines):
            if "ReplaceTileBlock" in l:
                for k in range(max(0, i - 5), i):
                    m = re.match(r"\s*lb bc,\s*(\d+),\s*(\d+)", lines[k])
                    if m:
                        blocks.append((int(m.group(1)), int(m.group(2))))
        out[lab] = {"trig": trig, "blocks": blocks}
    return out


def special_spots(kit):
    """{map const: [(x, y)]} fly / dungeon / new game landing spots."""
    s = kit.read("data/maps/special_warps.asm")
    out = {}
    for c, x, y in re.findall(r"fly_warp\s+(\w+),\s*(\d+),\s*(\d+)", s):
        out.setdefault(c, []).append((int(x), int(y)))
    for c, x, y in re.findall(r"special_warp_spec\s+(\w+),\s*(\d+),\s*(\d+)", s):
        out.setdefault(c, []).append((int(x), int(y)))
    return out


def building_blocks(kit):
    """per tileset: blocks seen right around door blocks (the pieces buildings are made of)."""
    out = {}
    for mp in kit.maps.values():
        ts = kit.tilesets[mp.tileset]
        if not ts.doors:
            continue
        b = kit.blocks(mp)
        for (x, y, d, i) in mp.warps:
            by, bx = y // 2, x // 2
            if by >= mp.h or bx >= mp.w:
                continue
            if kit.step_tile(mp.tileset, b, x, y) not in ts.doors:
                continue
            for dy in (-2, -1, 0):
                for dx in (-2, -1, 0, 1, 2):
                    yy, xx = by + dy, bx + dx
                    if 0 <= yy < mp.h and 0 <= xx < mp.w:
                        out.setdefault(mp.tileset, Counter())[int(b[yy, xx])] += 1
    return out


def analyse(kit, mp, extra):
    ts = kit.tilesets[mp.tileset]
    b = kit.blocks(mp)
    H, W = mp.h * 2, mp.w * 2
    tile = np.array([[kit.step_tile(mp.tileset, b, x, y) for x in range(W)] for y in range(H)])
    walk = np.isin(tile, list(ts.coll))
    water = np.isin(tile, list(WATER_TILES)) & ts.water
    if mp.tileset == "SHIP_PORT":
        water = (tile == 0x14)
    cuts = extra["cut"]
    cutm = np.zeros_like(walk)
    for by in range(mp.h):
        for bx in range(mp.w):
            if mp.tileset in ("OVERWORLD", "GYM") and int(b[by, bx]) in cuts:
                cutm[by * 2:by * 2 + 2, bx * 2:bx * 2 + 2] = ~walk[by * 2:by * 2 + 2, bx * 2:bx * 2 + 2]
    if mp.tileset == "OVERWORLD":
        # sideways ledges join regions; downward ledges stay one-way links (below)
        walk = walk | np.isin(tile, list(extra["ledges_side"]))
    land = walk & ~water
    lab_land, nl = ndimage.label(land)
    lab_w, nw = ndimage.label(water)
    region = np.where(land, lab_land, 0)
    region = np.where(water, lab_w + nl, region)          # water regions numbered after land
    anchors = {}

    def anchor(by, bx):
        if 0 <= by < mp.h and 0 <= bx < mp.w:
            anchors[(by, bx)] = int(b[by, bx])
    terms = set()

    def term(x, y):
        if 0 <= x < W and 0 <= y < H and region[y, x]:
            terms.add((x, y))

    def front(x, y):
        for dx, dy in ((0, 1), (0, -1), (-1, 0), (1, 0)):
            if 0 <= x + dx < W and 0 <= y + dy < H and land[y + dy, x + dx]:
                term(x + dx, y + dy)
                return

    bset = extra["building"].get(mp.tileset, {})
    for (x, y, d, i) in mp.warps:
        if not (0 <= x < W and 0 <= y < H):
            continue
        anchor(y // 2, x // 2)
        term(x, y)
        if kit.step_tile(mp.tileset, b, x, y) in ts.doors and mp.tileset in ("OVERWORLD", "PLATEAU", "FOREST"):
            # the building around an outdoor door: building pieces within 2 blocks
            seen, todo = {(y // 2, x // 2)}, [(y // 2, x // 2)]
            while todo:
                cy, cx = todo.pop()
                for dy, dx in ((-1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)):
                    ny, nx = cy + dy, cx + dx
                    if (ny, nx) in seen or not (0 <= ny < mp.h and 0 <= nx < mp.w):
                        continue
                    if abs(ny - y // 2) > 2 or abs(nx - x // 2) > 2:
                        continue
                    blk = int(b[ny, nx])
                    sub = walk[ny * 2:ny * 2 + 2, nx * 2:nx * 2 + 2]
                    if bset.get(blk, 0) >= 2 and not sub.all():
                        seen.add((ny, nx))
                        todo.append((ny, nx))
            for by, bx in seen:
                anchor(by, bx)
    for (x, y, t) in mp.bgs:
        if 0 <= x < W and 0 <= y < H:
            if land[y, x]:
                term(x, y)
            else:
                anchor(y // 2, x // 2)
                front(x, y)
    for (x, y) in extra["hidden"].get(mp.const, []):
        if 0 <= x < W and 0 <= y < H:
            if land[y, x]:
                term(x, y)
            else:
                anchor(y // 2, x // 2)
                front(x, y)
    for (x, y, sp, mv) in mp.objects:
        if 0 <= x < W and 0 <= y < H:
            if region[y, x]:
                term(x, y)
            else:
                anchor(y // 2, x // 2)
                front(x, y)
    sc = extra["scripts"].get(mp.label, {"trig": [], "blocks": []})
    for (x, y) in sc["trig"] + extra["special"].get(mp.const, []):
        term(x, y)
    for (by, bx) in sc["blocks"]:
        anchor(by, bx)
        for qy in (0, 1):
            for qx in (0, 1):
                term(bx * 2 + qx, by * 2 + qy)
    if ts.counters:
        for by in range(mp.h):
            for bx in range(mp.w):
                if set(int(t) for t in ts.blocks[b[by, bx]]) & set(ts.counters):
                    anchor(by, bx)
    # a block holding walk steps of two regions must keep its shape
    per_block = {}
    for (x, y) in terms:
        per_block.setdefault((y // 2, x // 2), set()).add(int(region[y, x]))
    for (by, bx), rs in per_block.items():
        if len(rs) > 1:
            anchor(by, bx)
    # walkable steps of anchored blocks are terminals too (they must stay connected)
    for (by, bx) in anchors:
        for qy in (0, 1):
            for qx in (0, 1):
                if region[by * 2 + qy, bx * 2 + qx]:
                    term(bx * 2 + qx, by * 2 + qy)
    # region graph
    edges = set()
    for y in range(H):
        for x in range(W):
            if not region[y, x]:
                continue
            for dx, dy in ((1, 0), (0, 1)):
                xx, yy = x + dx, y + dy
                if xx < W and yy < H and region[yy, xx] and region[yy, xx] != region[y, x]:
                    a, c = sorted((int(region[y, x]), int(region[yy, xx])))
                    if (a > nl) != (c > nl):
                        edges.add((a, c, "surf"))
    for y in range(H):
        for x in range(W):
            if cutm[y, x]:
                near = {int(region[yy, xx]) for xx, yy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                        if 0 <= xx < W and 0 <= yy < H and region[yy, xx] and region[yy, xx] <= nl}
                near = sorted(near)
                for i in range(len(near)):
                    for j in range(i + 1, len(near)):
                        edges.add((near[i], near[j], "cut"))
    if mp.tileset == "OVERWORLD":
        for y in range(1, H - 1):
            for x in range(W):
                if tile[y, x] in extra["ledges_down"]:
                    a, c = int(region[y - 1, x]), int(region[y + 1, x])
                    if a and c and a != c and a <= nl and c <= nl:
                        edges.add((a, c, "ledge"))
    # connection openings
    openings = {}
    for d, lab, c, off in mp.connections:
        line = {"north": [(x, 0) for x in range(W)], "south": [(x, H - 1) for x in range(W)],
                "west": [(0, y) for y in range(H)], "east": [(W - 1, y) for y in range(H)]}[d]
        ops = [(x, y) for x, y in line if region[y, x]]
        inner = {int(region[y, x]) for x, y in terms}
        inner |= {e[1] if e[0] in inner else e[0] for e in edges if (e[0] in inner) != (e[1] in inner)}
        keep_ops = [(x, y) for x, y in ops if int(region[y, x]) in inner]
        if not keep_ops and ops:     # strips outside the scenery border reach no anchor: drop them
            big = Counter(int(region[y, x]) for x, y in ops).most_common(1)[0][0]
            keep_ops = [(x, y) for x, y in ops if int(region[y, x]) == big]
        openings[d] = [[x, y, int(region[y, x])] for x, y in keep_ops]
        pending_ops = keep_ops
        for x, y in pending_ops:
            terms.add((x, y))
    kinds = {int(r): ("water" if r > nl else "walk") for r in np.unique(region) if r}
    used = {int(region[y, x]) for x, y in terms}
    # keep regions with terminals and water/land regions that link two kept regions
    keep = set(used)
    for _ in range(3):
        for r in kinds:
            if r in keep:
                continue
            nb = {a if c == r else c for a, c, k in edges if r in (a, c)}
            if len(nb & keep) >= 2:
                keep.add(r)
    grass = bool(ts.grass >= 0 and (tile == ts.grass).any())
    return {
        "w": mp.w, "h": mp.h, "tileset": mp.tileset, "border": mp.border, "blk": mp.blk,
        "anchors": {f"{by},{bx}": v for (by, bx), v in sorted(anchors.items())},
        "terminals": sorted([[x, y, int(region[y, x])] for x, y in terms if int(region[y, x]) in keep]),
        "regions": {str(r): kinds[r] for r in sorted(keep)},
        "edges": sorted([[a, c, k] for a, c, k in edges if a in keep and c in keep]),
        "openings": openings,
        "grass": grass,
        "warps": [[x, y] for (x, y, d, i) in mp.warps if 0 <= x < W and 0 <= y < H],
        "objects": [[x, y] for (x, y, sp, mv) in mp.objects if 0 <= x < W and 0 <= y < H],
        "water_share": round(float(water.mean()), 3),
    }


def kit_stats(kit):
    """per tileset: how often each block is used (the kit's vocabulary weights)."""
    out = {}
    for mp in kit.maps.values():
        b = kit.blocks(mp)
        c = out.setdefault(mp.tileset, Counter())
        for v in b.flat:
            c[int(v)] += 1
    return {k: dict(v.most_common()) for k, v in out.items()}


def main(argv):
    kit = Kit(argv[1])
    lt = re.findall(r"db SPRITE_FACING_(\w+),\s*\$[0-9A-Fa-f]+,\s*\$([0-9A-Fa-f]+)", kit.read("data/tilesets/ledge_tiles.asm"))
    extra = {"ledges_down": {int(t, 16) for d, t in lt if d == "DOWN"},
             "ledges_side": {int(t, 16) for d, t in lt if d != "DOWN"}, "cut": cut_blocks(kit), "hidden": hidden_events(kit), "scripts": script_coords(kit),
             "special": special_spots(kit), "building": building_blocks(kit)}
    maps = {}
    done_blk = {}
    for lab, mp in sorted(kit.maps.items()):
        maps[lab] = analyse(kit, mp, extra)
    # which terminals a player can reach on the old maps (a fact the new layout must keep)
    from games.pokered import mapbot
    ledges = mapbot.ledge_table(kit)
    for lab, m in maps.items():
        n, bad = mapbot.check_map(kit, kit.maps[lab], m, ledges)
        bad = {tuple(b) for b in bad}
        m["terminals"] = [[x, y, r, 0 if (x, y) in bad else 1] for x, y, r in m["terminals"]]
    out = {"maps": maps, "usage": kit_stats(kit),
           "building": {k: dict(v.most_common()) for k, v in extra["building"].items()}}
    json.dump(out, open(os.path.join(HERE, "spec/maps.json"), "w"), indent=0)
    na = sum(len(m["anchors"]) for m in maps.values())
    nb = sum(m["w"] * m["h"] for m in maps.values())
    print(f"maps: {len(maps)} maps, {na}/{nb} blocks anchored ({100 * na / nb:.1f}%), "
          f"{sum(len(m['terminals']) for m in maps.values())} terminals, "
          f"{sum(len(m['edges']) for m in maps.values())} region links")


if __name__ == "__main__":
    main(sys.argv)
