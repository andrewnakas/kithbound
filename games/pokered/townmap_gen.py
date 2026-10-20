"""CLEAN ROOM: the world map picture of KITHBOUND (gfx/town_map/town_map.rle).

Only the anchors the engine hard-wires are kept: each outdoor place's map-cursor
position (data/maps/town_map_entries.asm, code) and which places connect
(map headers). Coastlines, land shapes and route lines are drawn here, seeded.

    python -m games.pokered.townmap_gen <tree>
"""
import os
import re
import sys

import numpy as np

from cleanroom.decomp.gen import h32
from games.pokered.maps_kit import Kit

BLANK, ROUTE_V, ROUTE_H, CITY_LAND, SEA, CITY, LAND, ROUTE, SW, SE, NE, NW, SPOT, SEA_DOT, SEA_H, SEA_V = range(16)
W, H = 20, 18


def main(argv):
    tree = argv[1]
    kit = Kit(tree)
    s = kit.read("data/maps/town_map_entries.asm")
    names = re.findall(r"outdoor_map\s+(\d+),\s*(\d+),\s*(\w+)Name", s)
    pos = {}
    for x, y, nm in names:
        if (x, y) == ("0", "0"):
            continue
        pos[nm] = (int(x) + 2, int(y) + 1)
    r = np.random.default_rng(h32("kithbound-townmap"))
    g = np.full((H, W), SEA, np.uint8)
    sea_routes = {"Route19", "Route20", "Route21"}
    land = np.zeros((H, W), bool)
    for nm, (x, y) in pos.items():
        if nm in sea_routes:
            continue
        rad = 1 + int(r.integers(0, 2))
        for dy in range(-rad, rad + 1):
            for dx in range(-rad - 1, rad + 2):
                if abs(dx) + abs(dy) <= rad + 1 and 0 <= y + dy < H and 0 <= x + dx < W and r.random() < 0.85:
                    land[y + dy, x + dx] = True
    # connections between outdoor places
    label_of = {m.const: m.label for m in kit.maps.values()}
    links = set()
    for m in kit.maps.values():
        if m.label not in pos:
            continue
        for d, lab, c, off in m.connections:
            if lab in pos:
                links.add(tuple(sorted((m.label, lab))))
    for a, b in sorted(links):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        sea = a in sea_routes or b in sea_routes
        horiz_first = r.random() < 0.5
        pts = []
        if horiz_first:
            pts += [(x, y0) for x in range(min(x0, x1), max(x0, x1) + 1)]
            pts += [(x1, y) for y in range(min(y0, y1), max(y0, y1) + 1)]
        else:
            pts += [(x0, y) for y in range(min(y0, y1), max(y0, y1) + 1)]
            pts += [(x, y1) for x in range(min(x0, x1), max(x0, x1) + 1)]
        for (x, y) in pts:
            if sea:
                if not land[y, x]:
                    g[y, x] = SEA_DOT
            else:
                land[y, x] = True
                g[y, x] = ROUTE
    g[land & (g == SEA)] = LAND
    for (x, y) in [pos[n] for n in pos if n.endswith(("Town", "City", "Island", "Plateau"))]:
        g[y, x] = CITY
    # straight route pieces get their own tiles
    for y in range(H):
        for x in range(W):
            if g[y, x] == ROUTE:
                v = (y > 0 and g[y - 1, x] in (ROUTE, CITY)) or (y < H - 1 and g[y + 1, x] in (ROUTE, CITY))
                h = (x > 0 and g[y, x - 1] in (ROUTE, CITY)) or (x < W - 1 and g[y, x + 1] in (ROUTE, CITY))
                if v and not h:
                    g[y, x] = ROUTE_V
                elif h and not v:
                    g[y, x] = ROUTE_H
    flat = list(g.flatten())
    out = bytearray()
    i = 0
    while i < len(flat):
        t, n = flat[i], 1
        while i + n < len(flat) and flat[i + n] == t and n < 15:
            n += 1
        out.append((int(t) << 4) | n)
        i += n
    out.append(0)
    open(os.path.join(tree, "gfx/town_map/town_map.rle"), "wb").write(out)
    print(f"town map: {len(pos)} places, {len(links)} links, {len(out)} bytes")


if __name__ == "__main__":
    main(sys.argv)
