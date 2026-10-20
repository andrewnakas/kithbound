"""Static map bot: walks every built map by the engine's movement rules and checks
that each thing the game needs can be reached.

Rules: walk on passable tiles; surf on water (all field moves assumed learnt);
cut trees count as passable; ledges only jump downward/sideways in their direction
(a ledge tile is crossed from its high side, never climbed); boulders and NPCs are
ignored. Start: every warp step and every edge step facing a connected map.
Targets: warps, NPC / item positions (a neighbour must be reachable), sign and hidden
event fronts, script trigger coordinates (spec/maps.json terminals).

    python -m games.pokered.mapbot <tree> [--md report.md]
"""
import json
import os
import re
import sys
from collections import deque

from games.pokered.maps_kit import Kit

HERE = os.path.dirname(os.path.abspath(__file__))
WATER = {0x14, 0x32, 0x48}
CUT_TREE_TILES = {0x3D, 0x2E}   # overworld cut tree / gym bush tiles (bottom-left of the block's steps)


def ledge_table(kit):
    s = kit.read("data/tilesets/ledge_tiles.asm")
    out = []
    for d, stand, ledge, pad in re.findall(r"db SPRITE_FACING_(\w+),\s*\$([0-9A-Fa-f]+),\s*\$([0-9A-Fa-f]+),\s*(\w+)", s):
        out.append((d.lower(), int(stand, 16), int(ledge, 16)))
    return out


def check_map(kit, mp, spec_m, ledges, moves=True):
    ts = kit.tilesets[mp.tileset]
    b = kit.blocks(mp)
    W, H = mp.w * 2, mp.h * 2
    tile = {(x, y): kit.step_tile(mp.tileset, b, x, y) for y in range(H) for x in range(W)}
    cut_blocks = set()
    if mp.tileset in ("OVERWORLD", "GYM"):
        s = kit.read("data/tilesets/cut_tree_blocks.asm")
        cut_blocks = {int(a, 16) for a, c in re.findall(r"db \$([0-9A-Fa-f]+), \$([0-9A-Fa-f]+)", s)}

    people = {tuple(o) for o in spec_m.get("objects", [])}

    def passable(p):
        if p in people:
            return False                                 # NPCs and item balls stand in the way
        t = tile.get(p)
        if t is None:
            return False
        if t in ts.coll:
            return True
        if moves and ts.water and t in WATER:
            return True
        if moves and int(b[p[1] // 2, p[0] // 2]) in cut_blocks:
            return True
        return False
    dirs = {"down": (0, 1), "up": (0, -1), "left": (-1, 0), "right": (1, 0)}
    jump = {}
    if mp.tileset == "OVERWORLD":
        for d, stand, ledge in ledges:
            jump.setdefault(d, set()).add((stand, ledge))
    start = [(x, y) for (x, y, dest, i) in mp.warps if (x, y) in tile]
    for d, lab, c, off in mp.connections:
        line = {"north": [(x, 0) for x in range(W)], "south": [(x, H - 1) for x in range(W)],
                "west": [(0, y) for y in range(H)], "east": [(W - 1, y) for y in range(H)]}[d]
        start += [p for p in line if passable(p)]
    seen = set(start)
    q = deque(start)
    while q:
        p = q.popleft()
        for d, (dx, dy) in dirs.items():
            n = (p[0] + dx, p[1] + dy)
            if n not in tile:
                continue
            tn = tile[n]
            if mp.tileset == "OVERWORLD" and any(tn == l for _, l in jump.get(d, ())) and \
                    (tile[p], tn) in jump.get(d, set()):
                n2 = (n[0] + dx, n[1] + dy)              # hop over the ledge
                if n2 in tile and passable(n2) and n2 not in seen:
                    seen.add(n2)
                    q.append(n2)
                continue
            if passable(n) and n not in seen:
                seen.add(n)
                q.append(n)
    bad = []
    for t in spec_m["terminals"]:
        x, y = t[0], t[1]
        if len(t) > 3 and not t[3]:
            continue                                     # the old map did not reach it either
        p = (x, y)
        if p in seen:
            continue
        if any((x + dx, y + dy) in seen for dx, dy in dirs.values()):
            continue                                     # talk / read from a neighbour
        if any(tile.get((x + dx, y + dy)) in ts.counters and (x + 2 * dx, y + 2 * dy) in seen
               for dx, dy in dirs.values()):
            continue                                     # talk across a counter
        bad.append(p)
    if not moves:
        # without field moves every walk region's terminals must share one component (no new gates)
        comp, cid = {}, 0
        for p0 in tile:
            if p0 in comp or not passable(p0):
                continue
            cid += 1
            comp[p0] = cid
            qq = deque([p0])
            while qq:
                c = qq.popleft()
                for dx, dy in dirs.values():
                    n = (c[0] + dx, c[1] + dy)
                    if n in tile and n not in comp and passable(n):
                        comp[n] = cid
                        qq.append(n)
        groups = {}
        for t in spec_m["terminals"]:
            if spec_m["regions"].get(str(t[2])) == "walk" and (t[0], t[1]) in comp:
                groups.setdefault(t[2], set()).add(comp[(t[0], t[1])])
        bad = [f"region {r} split in {len(c)}" for r, c in groups.items() if len(c) > 1]
    return len(spec_m["terminals"]), bad


def main(argv):
    tree = argv[1]
    kit = Kit(tree)
    base = {}
    bp = os.path.join(os.environ.get("POKERED_ORIG", "D:/n64work/pokered/orig"), "mapbot_retail.json")
    if os.path.exists(bp):
        base = json.load(open(bp))        # dirty side: targets the old maps did not reach either
    spec = json.load(open(os.path.join(HERE, "spec/maps.json")))["maps"]
    ledges = ledge_table(kit)
    rows, nbad = [], 0
    for label, mp in sorted(kit.maps.items()):
        if label not in spec:
            continue
        n, bad = check_map(kit, mp, spec[label], ledges)
        bad = bad + check_map(kit, mp, spec[label], ledges, moves=False)[1]
        if "--save-base" not in argv:
            skip = {tuple(p) if isinstance(p, list) else p for p in base.get(label, [])}
            bad = [p for p in bad if (tuple(p) if isinstance(p, list) else p) not in skip]
        rows.append((label, n, bad))
        nbad += bool(bad)
    if "--save-base" in argv:
        json.dump({l: b for l, n, b in rows if b}, open(bp, "w"))
        print(f"mapbot: base saved ({sum(1 for r in rows if r[2])} maps with targets the old maps leave out)")
        return 0
    print(f"mapbot: {len(rows)} maps, {nbad} with unreachable targets")
    for label, n, bad in rows:
        if bad:
            print(f"  {label}: {len(bad)}/{n} unreachable, e.g. {bad[:4]}")
    if "--md" in argv:
        with open(argv[argv.index("--md") + 1], "w") as f:
            f.write("# Map bot (static reachability)\n\n| map | targets | unreachable |\n|---|---|---|\n")
            for label, n, bad in rows:
                f.write(f"| {label} | {n} | {len(bad)}{' ' + str(bad[:6]) if bad else ''} |\n")
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
