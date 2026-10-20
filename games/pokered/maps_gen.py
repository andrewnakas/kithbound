"""CLEAN ROOM: new layouts for every map of KITHBOUND.

Input: spec/maps.json (size, tileset, anchor blocks, terminal steps with their
region, region links through water / cut trees, edge openings) + the blockset
vocabulary (which blocks are floor, grass, water, solid, cut tree; weights from
how often the kit uses them) + a seed per map. Output: maps/<Name>.blk.

Every terminal is reached by new meandering paths inside its own region, regions
stay apart except through the planned surf or cut links, routes get grass
patches, and the rest becomes scenery.

    python -m games.pokered.maps_gen <tree> [only-map-label]
"""
import heapq
import json
import os
import re
import sys

import numpy as np

from cleanroom.decomp.gen import h32
from games.pokered.maps_kit import Kit

HERE = os.path.dirname(os.path.abspath(__file__))
WATER_TILES = {0x14}
OUTDOOR = {"OVERWORLD", "FOREST", "PLATEAU"}
OPEN = {"REDS_HOUSE_1", "REDS_HOUSE_2", "MART", "POKECENTER", "HOUSE", "GATE", "FOREST_GATE", "MUSEUM", "LAB",
        "LOBBY", "CLUB", "INTERIOR", "SHIP", "DOJO", "GYM", "MANSION", "FACILITY", "CEMETERY", "UNDERGROUND"}


def vocab(kit, spec):
    """per tileset: floor / grass / water / solid / cut block choices with weights."""
    cut_ids = {int(a, 16) for a, b in re.findall(r"db \$([0-9A-Fa-f]+), \$([0-9A-Fa-f]+)",
                                                  kit.read("data/tilesets/cut_tree_blocks.asm"))}
    out = {}
    for const, ts in kit.tilesets.items():
        use = {int(k): v for k, v in spec["usage"].get(const, {}).items()}
        cand = {"floor": [], "grass": [], "water": [], "solid": [], "cut": []}
        specials = set(ts.doors) | set(ts.warps) | set(ts.counters)
        for blk in range(len(ts.blocks)):
            q = kit.quad_tiles(const, blk)
            tiles = set(int(t) for t in ts.blocks[blk])
            walk = [t in ts.coll for t in q.values()]
            n = use.get(blk, 0)
            if n == 0:
                continue
            if all(walk) and ts.grass >= 0 and all(t == ts.grass for t in q.values()):
                cand["grass"].append((n, blk))
            elif blk in cut_ids and const in ("OVERWORLD", "GYM") and not any(walk):
                cand["cut"].append((n, blk))
            elif all(t in WATER_TILES for t in q.values()) and ts.water:
                cand["water"].append((n, blk))
            elif all(walk) and not (tiles & specials) and not (tiles & WATER_TILES):
                cand["floor"].append((n, blk))
            elif not any(walk) and not (tiles & WATER_TILES) and not (tiles & specials):
                cand["solid"].append((n, blk))
        if const == "OVERWORLD":
            for k in ("street", "lawn", "flower", "fence", "tree", "ledge"):
                cand[k] = []
            for blk in range(len(ts.blocks)):
                q = kit.quad_tiles(const, blk)
                tl = [int(t) for t in ts.blocks[blk]]
                tiles = set(tl)
                walk = [t in ts.coll for t in q.values()]
                n = use.get(blk, 0) + 1

                def cnt(ids):
                    return sum(t in ids for t in tl)
                if tiles & specials or tiles & WATER_TILES:
                    continue
                if all(walk):
                    if cnt({0x5B}) >= 8:
                        cand["street"].append((1000 * cnt({0x5B}) + n, blk))
                    if cnt({0x2C}) >= 10:
                        cand["lawn"].append((n, blk))
                    if cnt({0x03}) >= 2:
                        cand["flower"].append((n, blk))
                elif not any(walk):
                    if cnt({0x20, 0x10}) >= 2:
                        cand["fence"].append((n, blk))
                    if cnt({0x40, 0x41, 0x50, 0x51}) >= 12:
                        cand["tree"].append((n, blk))
                if q[(0, 0)] in ts.coll and q[(0, 1)] in ts.coll and q[(1, 0)] in (0x37, 0x36) \
                        and q[(1, 1)] in (0x37, 0x36):
                    cand["ledge"].append((n, blk))
        for k in cand:
            cand[k].sort(reverse=True)
        out[const] = cand
    return out


def is_town(label):
    return label.endswith(("Town", "City", "Island")) or label == "IndigoPlateau"


def pick(r, lst, top=3):
    lst = lst[:top]
    w = np.array([n for n, b in lst], float)
    return int(lst[int(r.choice(len(lst), p=w / w.sum()))][1])


class Layout:
    def __init__(self, label, m, voc, seed):
        self.label, self.m, self.voc = label, m, voc
        self.W, self.H = m["w"], m["h"]
        self.r = np.random.default_rng(h32("kithbound-map", label, seed))
        self.cls = [[None] * self.W for _ in range(self.H)]
        self.reg = np.zeros((self.H, self.W), int)
        self.sreg = np.zeros((self.H * 2, self.W * 2), int)     # step region; 0 solid/unknown, -9 foreign walk
        self.noise = self._noise()
        if is_town(label) and m["tileset"] == "OVERWORLD":
            self.noise = self.noise * 0.15          # towns: straight streets
        self.kind = {int(k): v for k, v in m["regions"].items()}
        self.problems = []
        self.crowd = []
        self.notes = []

    def _noise(self):
        # smooth random field: path meanders follow it
        small = self.r.random((self.H // 3 + 2, self.W // 3 + 2))
        big = np.kron(small, np.ones((3, 3)))[:self.H, :self.W]
        return big * 4 + self.r.random((self.H, self.W))

    # ---- step/block helpers
    def steps(self, by, bx):
        return [(bx * 2 + qx, by * 2 + qy) for qy in (0, 1) for qx in (0, 1)]

    def can_be(self, by, bx, region):
        """block may become walk/water of `region` without touching another region."""
        if not (0 <= by < self.H and 0 <= bx < self.W):
            return False
        c = self.cls[by][bx]
        if c is not None and not (c in ("F", "W") and self.reg[by, bx] == region):
            return False
        for sx, sy in self.steps(by, bx):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                x, y = sx + dx, sy + dy
                if x // 2 == bx and y // 2 == by:
                    continue
                if 0 <= x < self.W * 2 and 0 <= y < self.H * 2:
                    o = self.sreg[y, x]
                    if o and o != region and not self._linked(o, region):
                        return False
        return True

    def unreached(self):
        """(region, start region) pairs for terminals the player must reach but cannot."""
        W2, H2 = self.W * 2, self.H * 2
        starts = [(t[0], t[1]) for t in self.m["terminals"] if self.is_start(t[0], t[1])]
        ok = lambda x, y: self.sreg[y, x] != 0 or self.cls[y // 2][x // 2] in ("C", "D")
        seen, q = set(p for p in starts if ok(*p)), [p for p in starts if ok(*p)]
        while q:
            x, y = q.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < W2 and 0 <= n[1] < H2 and n not in seen and ok(*n):
                    seen.add(n)
                    q.append(n)
        main = None
        for p in starts:
            if self.sreg[p[1], p[0]] > 0:
                main = int(self.sreg[p[1], p[0]])
                break
        out = []
        for t in self.m["terminals"]:
            if len(t) > 3 and not t[3]:
                continue
            x, y, rg = t[0], t[1], t[2]
            if (x, y) in seen or any((x + dx, y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            if any(0 <= x + dx < W2 and 0 <= y + dy < H2 and self.cls[(y + dy) // 2][(x + dx) // 2] == "A"
                   and (x + 2 * dx, y + 2 * dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue                     # talked to across a counter / desk
            if main and rg != main:
                out.append((rg, main))
        return list(dict.fromkeys(out))

    def is_start(self, x, y):
        if (x, y) in self.warp_steps:
            return True
        return False

    def blocker(self, by, bx, region):
        """the other region whose steps keep this block from joining `region`."""
        c = self.cls[by][bx]
        if c in ("F", "W") and self.reg[by, bx] != region:
            return int(self.reg[by, bx])
        for sx, sy in self.steps(by, bx):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                x, y = sx + dx, sy + dy
                if x // 2 == bx and y // 2 == by:
                    continue
                if 0 <= x < self.W * 2 and 0 <= y < self.H * 2:
                    o = self.sreg[y, x]
                    if o and o != region and not self._linked(o, region):
                        return int(o)
        return None

    def _linked(self, a, b):
        # surf: land next to its own water region is allowed only through planned links (set later)
        return (min(a, b), max(a, b)) in self.allowed

    def set_block(self, by, bx, c, region):
        self.cls[by][bx] = c
        self.reg[by, bx] = region
        for sx, sy in self.steps(by, bx):
            self.sreg[sy, sx] = region if c in ("F", "W", "C") else 0

    # ---- build
    def run(self):
        m = self.m
        self.allowed = {(min(a, b), max(a, b)) for a, b, k in m["edges"] if k == "surf"}
        terms = {}
        for (x, y, rg, *_) in m["terminals"]:
            terms.setdefault(rg, set()).add((x, y))
        anch = {tuple(int(v) for v in k.split(",")): b for k, b in m["anchors"].items()}
        tstep = {(x, y): rg for (x, y, rg, *_) in m["terminals"]}
        for (by, bx), b in anch.items():
            self.cls[by][bx] = "A"
            for sx, sy in self.steps(by, bx):
                self.sreg[sy, sx] = tstep.get((sx, sy), 0)
        # terminal steps outside anchors claim their block (land first, water after)
        order = sorted(tstep.items(), key=lambda kv: self.kind.get(kv[1]) == "water")
        for (x, y), rg in order:
            by, bx = y // 2, x // 2
            if (by, bx) in anch:
                continue
            c = "W" if self.kind.get(rg) == "water" else "F"
            if self.cls[by][bx] is None:
                if self.can_be(by, bx, rg):
                    self.set_block(by, bx, c, rg)
                else:
                    self.problems.append(f"terminal {x},{y} crowded")
                    self.crowd.append((rg, self.blocker(by, bx, rg)))
            elif self.reg[by, bx] != rg:
                self.problems.append(f"terminal clash at {x},{y}")
        # steps inside anchors (doors, counters) get a free neighbour block of their own region
        for (x, y), rg in order:
            if (y // 2, x // 2) not in anch or self.kind.get(rg) == "water":
                continue
            nbs = [(x + dx, y + dy) for dx, dy in ((0, 1), (0, -1), (-1, 0), (1, 0))
                   if 0 <= x + dx < self.W * 2 and 0 <= y + dy < self.H * 2]
            if any(self.sreg[ny, nx] == rg and (ny // 2, nx // 2) not in anch for nx, ny in nbs):
                continue
            for nx, ny in nbs:
                b = (ny // 2, nx // 2)
                if b not in anch and self.cls[b[0]][b[1]] is None and self.can_be(b[0], b[1], rg):
                    self.set_block(b[0], b[1], "F", rg)
                    break
        # NPCs and item balls block their step: keep room to walk round them
        self.people = {tuple(o) for o in m.get("objects", [])}
        for (x, y) in self.people:
            rg = tstep.get((x, y))
            if not rg or self.kind.get(rg) != "walk":
                continue
            for dx, dy in ((0, 1), (0, -1), (-1, 0), (1, 0)):
                nx, ny = x + dx, y + dy
                b = (ny // 2, nx // 2)
                if 0 <= nx < self.W * 2 and 0 <= ny < self.H * 2 and b not in anch and                         self.cls[b[0]][b[1]] is None and self.can_be(b[0], b[1], rg):
                    self.set_block(b[0], b[1], "F", rg)
        # connect every region's terminals, step by step
        for rg, st in terms.items():
            st = [t for t in st if self.sreg[t[1], t[0]] == rg]
            if not st:
                continue
            tree = self.flood(st[0], rg)
            for t in st:
                if t in tree:
                    continue
                path = self.step_path(tree, t, rg)
                if path is None:
                    # last resort: ignore the separation from neighbouring regions (gating loosens,
                    # nothing becomes unreachable)
                    def free(by, bx, r):
                        return 0 <= by < self.H and 0 <= bx < self.W and self.cls[by][bx] in (None, "F", "L", "P")
                    path = self.step_path(tree, t, rg, allow=free)
                    if path is not None:
                        self.notes.append(f"region {rg}: step {t} joined across a region edge")
                if path is None:
                    self.problems.append(f"region {rg}: step {t} unreachable")
                    continue
                c = "W" if self.kind.get(rg) == "water" else "F"
                for (x, y) in path:
                    if self.cls[y // 2][x // 2] is None:
                        self.set_block(y // 2, x // 2, c, rg)
                tree = self.flood(st[0], rg)
        # links between regions (surf, cut)
        for a, b, k in m["edges"]:
            self.link(a, b, k)
        if is_town(self.label) and self.m["tileset"] == "OVERWORLD" and self.voc.get("street"):
            self.town()
        else:
            self.widen()
            if m.get("grass") and m["tileset"] in OUTDOOR:
                self.grass()
        return self

    def flood(self, start, rg):
        seen, todo = {start}, [start]
        while todo:
            x, y = todo.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and 0 <= n[0] < self.W * 2 and 0 <= n[1] < self.H * 2 and self.sreg[n[1], n[0]] == rg:
                    seen.add(n)
                    todo.append(n)
        return seen

    def step_path(self, src, dst, rg, allow=None):
        """steps from the region's tree to dst over own walkable steps or free blocks that may join rg."""
        dist = {s: 0.0 for s in src}
        pq = [(0.0, s) for s in src]
        prev, ok = {}, {}
        while pq:
            d, cur = heapq.heappop(pq)
            if (cur in dst) if isinstance(dst, set) else (cur == dst):
                path = [cur]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return path[::-1]
            if d > dist.get(cur, 1e18):
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cur[0] + dx, cur[1] + dy)
                if not (0 <= n[0] < self.W * 2 and 0 <= n[1] < self.H * 2):
                    continue
                if n in getattr(self, "people", ()) and n != dst and not (isinstance(dst, set) and n in dst):
                    continue
                if self.sreg[n[1], n[0]] == rg:
                    cost = 0.1
                else:
                    blk = (n[1] // 2, n[0] // 2)
                    if blk not in ok:
                        ok[blk] = allow(blk[0], blk[1], rg) if allow else                             (self.cls[blk[0]][blk[1]] is None and self.can_be(blk[0], blk[1], rg))
                    if not ok[blk]:
                        continue
                    cost = 0.5 + 0.5 * self.noise[blk]
                nd = d + cost
                if nd < dist.get(n, 1e18):
                    dist[n] = nd
                    prev[n] = cur
                    heapq.heappush(pq, (nd, n))
        return None

    def region_blocks(self, rg):
        return {(y, x) for y in range(self.H) for x in range(self.W)
                if self.cls[y][x] in ("F", "W") and self.reg[y, x] == rg}

    def astar(self, src, dst, rg, through=None):
        """block path from any src to any dst over free blocks (or blocks of rg)."""
        dist = {s: 0.0 for s in src}
        pq = [(0.0, s) for s in src]
        prev = {}
        while pq:
            d, cur = heapq.heappop(pq)
            if cur in dst:
                path = [cur]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return path[::-1]
            if d > dist.get(cur, 1e18):
                continue
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (cur[0] + dy, cur[1] + dx)
                if nb in dist and dist[nb] <= d:
                    continue
                if nb not in dst and not (through or self.can_be)(nb[0], nb[1], rg):
                    continue
                if nb in dst and not (0 <= nb[0] < self.H and 0 <= nb[1] < self.W):
                    continue
                if nb in dst and self.cls[nb[0]][nb[1]] not in (None, "F", "W") and nb not in src:
                    pass
                step = 1.0 + self.noise[nb]
                nd = d + step
                if nd < dist.get(nb, 1e18):
                    dist[nb] = nd
                    prev[nb] = cur
                    heapq.heappush(pq, (nd, nb))
        return None

    def steps_of(self, rg):
        return {(x, y) for y in range(self.H * 2) for x in range(self.W * 2) if self.sreg[y, x] == rg}

    def border_of(self, rg):
        out = set()
        for (x, y) in self.steps_of(rg):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < self.W * 2 and 0 <= n[1] < self.H * 2 and self.sreg[n[1], n[0]] != rg                         and self.cls[n[1] // 2][n[0] // 2] is None:
                    out.add(n)
        return out

    def link(self, a, b, kind):
        if kind == "surf":
            land, water = (a, b) if self.kind.get(a) == "walk" else (b, a)
            L, Wt = self.steps_of(land), self.steps_of(water)
            if not L:
                self.problems.append(f"surf link {land}-{water}: no land")
                return
            if any((x + dx, y + dy) in Wt for (x, y) in L for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                return
            dst = self.border_of(land)
            if not Wt:
                for (x, y) in sorted(dst, key=lambda s: self.noise[s[1] // 2, s[0] // 2]):
                    if self.can_be(y // 2, x // 2, water):
                        self.set_block(y // 2, x // 2, "W", water)
                        return
                self.problems.append(f"surf link {land}-{water}: no room")
                return
            path = self.step_path(Wt, dst, water)
            if path is None:
                self.problems.append(f"surf link {land}-{water} failed")
                return
            for (x, y) in path:
                if self.cls[y // 2][x // 2] is None:
                    self.set_block(y // 2, x // 2, "W", water)
        elif kind == "ledge":
            self.ledge_link(a, b)
        else:
            A, B = self.steps_of(a), self.steps_of(b)
            if not A or not B:
                self.problems.append(f"cut link {a}-{b}: missing side")
                return
            dst = self.border_of(b)

            def free(by, bx, rg):
                return 0 <= by < self.H and 0 <= bx < self.W and self.cls[by][bx] is None
            path = self.step_path(A, dst, a, allow=free)
            if path is None:
                self.problems.append(f"cut link {a}-{b} failed")
                return
            blocks = []
            for (x, y) in path:
                blk = (y // 2, x // 2)
                if self.cls[blk[0]][blk[1]] is None and blk not in blocks:
                    blocks.append(blk)
            if not blocks:
                self.problems.append(f"cut link {a}-{b}: regions touch")
                return
            mid = len(blocks) // 2
            for i, blk in enumerate(blocks):
                if i == mid:
                    self.set_block(*blk, "C", 0)
                elif i < mid:
                    self.set_block(*blk, "F", a)
                else:
                    self.set_block(*blk, "F", b)

    def ledge_link(self, a, b):
        """one-way drop from region a (above) to region b (below) through a ledge block."""
        if not self.voc.get("ledge"):
            self.problems.append(f"ledge link {a}-{b}: no ledge block")
            return
        A, B = self.steps_of(a), self.steps_of(b)
        if not A or not B:
            self.problems.append(f"ledge link {a}-{b}: missing side")
            return
        bA = {(y // 2, x // 2) for x, y in A if self.cls[y // 2][x // 2] in ("F", "W")}
        cands = []
        for (y, x) in bA:
            ly = y + 1
            if ly + 1 >= self.H or self.cls[ly][x] is not None:
                continue
            cands.append((self.noise[ly, x], ly, x))
        for _, ly, x in sorted(cands):
            below = (ly + 1, x)
            cb = self.cls[below[0]][below[1]]
            if cb is not None and not (cb == "F" and self.reg[below] == b):
                continue
            if cb is None and not self.can_be(below[0], below[1], b):
                continue
            self.cls[ly][x] = "D"
            self.reg[ly, x] = a
            for qx in (0, 1):
                self.sreg[ly * 2, x * 2 + qx] = a
                self.sreg[ly * 2 + 1, x * 2 + qx] = 0
            if cb is None:
                self.set_block(below[0], below[1], "F", b)
            src = {(x * 2 + qx, (ly + 1) * 2 + qy) for qx in (0, 1) for qy in (0, 1)}
            tgt = B - src
            if tgt and not (self.flood(next(iter(src)), b) & tgt):
                path = self.step_path(src, tgt, b)
                if path is None:
                    self.problems.append(f"ledge link {a}-{b}: landing cut off")
                    return
                for (px, py) in path:
                    if self.cls[py // 2][px // 2] is None:
                        self.set_block(py // 2, px // 2, "F", b)
            return
        self.notes.append(f"ledge {a}-{b} placed as a plain path")
        self.walk_link(a, b)

    def walk_link(self, a, b):
        A = self.steps_of(a)
        dst = self.border_of(b)
        if not A or not dst:
            self.problems.append(f"walk link {a}-{b}: missing side")
            return

        def free(by, bx, rg):
            return 0 <= by < self.H and 0 <= bx < self.W and self.cls[by][bx] is None
        path = self.step_path(A, dst, a, allow=free)
        if path is None:
            self.problems.append(f"walk link {a}-{b} failed")
            return
        for (x, y) in path:
            if self.cls[y // 2][x // 2] is None:
                self.set_block(y // 2, x // 2, "F", a)
        self.allowed.add((min(a, b), max(a, b)))

    def town(self):
        """towns: lawns wherever the regions allow, paved streets on the carved paths,
        fenced yards beside buildings, a plaza and flower beds."""
        streets = set((y, x) for y in range(self.H) for x in range(self.W) if self.cls[y][x] == "F")
        # avenues: from a hub near the centre of each region to every door and map exit of it
        cy, cx = self.H, self.W
        imp = {}
        for t in self.m["terminals"]:
            if (t[0], t[1]) in self.warp_steps and self.sreg[t[1], t[0]] == t[2]:
                imp.setdefault(t[2], []).append((t[0], t[1]))
        for rg, pts in imp.items():
            hub = min(pts, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
            for p in pts:
                if p == hub:
                    continue
                path = self.step_path({hub}, p, rg)
                if not path:
                    continue
                for (x, y) in path:
                    blk = (y // 2, x // 2)
                    if self.cls[blk[0]][blk[1]] is None and self.can_be(blk[0], blk[1], rg):
                        self.set_block(blk[0], blk[1], "F", rg)
                    if self.cls[blk[0]][blk[1]] == "F":
                        streets.add(blk)
        for _ in range(self.W + self.H):
            grew = False
            for y in range(1, self.H - 1):
                for x in range(1, self.W - 1):
                    if self.cls[y][x] is not None:
                        continue
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if self.cls[ny][nx] in ("F", "L") and self.can_be(y, x, self.reg[ny, nx]):
                            self.set_block(y, x, "F", self.reg[ny, nx])
                            self.cls[y][x] = "L"
                            grew = True
                            break
            if not grew:
                break
        for (y, x) in streets:
            if self.cls[y][x] == "F":
                self.cls[y][x] = "P"
        cy, cx = self.H // 2, self.W // 2
        best = None
        for y in range(1, self.H - 2):
            for x in range(1, self.W - 2):
                cells = [(y + i, x + j) for i in range(3) for j in range(3)]
                if all(self.cls[a][b] in ("L", "P") for a, b in cells):
                    d = abs(y + 1 - cy) + abs(x + 1 - cx)
                    if best is None or d < best[0]:
                        best = (d, cells)
        if best:
            for k, (a, b) in enumerate(best[1]):
                self.cls[a][b] = "Q" if k == 4 else "P"
        anch = [(y, x) for y in range(self.H) for x in range(self.W) if self.cls[y][x] == "A"]
        for (y, x) in anch:
            for dy, dx in ((0, -1), (0, 1), (-1, 0), (-1, -1), (-1, 1)):
                ny, nx = y + dy, x + dx
                if not (0 <= ny < self.H and 0 <= nx < self.W) or self.cls[ny][nx] != "L":
                    continue
                if (ny, nx) in self.terminal_blocks:
                    continue
                rg = self.reg[ny, nx]
                self.set_block(ny, nx, "S", 0)
                if self.connected():
                    self.cls[ny][nx] = "Y"
                else:
                    self.set_block(ny, nx, "F", rg)
                    self.cls[ny][nx] = "L"
        for y in range(self.H):
            for x in range(self.W):
                if self.cls[y][x] == "L" and self.r.random() < 0.12:
                    self.cls[y][x] = "Q"
        for y in range(1, self.H - 1):
            for x in range(1, self.W - 1):
                if self.cls[y][x] is None and self.r.random() < 0.5 and any(
                        self.cls[y + dy][x + dx] in ("L", "P", "Q") for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.cls[y][x] = "Y"

    def widen(self):
        ts = self.m["tileset"]
        if ts in OPEN:
            # rooms: open floor everywhere below the back wall, then furniture where it blocks nothing
            for _ in range(self.W + self.H):
                grew = False
                for y in range(1, self.H):
                    for x in range(self.W):
                        if self.cls[y][x] is not None:
                            continue
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.H and 0 <= nx < self.W and self.cls[ny][nx] == "F"                                     and self.can_be(y, x, self.reg[ny, nx]):
                                self.set_block(y, x, "F", self.reg[ny, nx])
                                grew = True
                                break
                if not grew:
                    break
            if ts in ("HOUSE", "REDS_HOUSE_1", "REDS_HOUSE_2", "POKECENTER", "MART", "GATE", "LOBBY", "MUSEUM",
                      "FOREST_GATE", "INTERIOR", "CLUB", "SHIP", "GYM", "DOJO", "LAB"):
                self.furnish()
            return
        p = 0.3
        for _ in range(2):
            for y in range(self.H):
                for x in range(self.W):
                    if self.cls[y][x] not in ("F",):
                        continue
                    rg = self.reg[y, x]
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 < ny < self.H - 1 and 0 < nx < self.W - 1 and self.cls[ny][nx] is None                                 and self.r.random() < p and self.can_be(ny, nx, rg):
                            self.set_block(ny, nx, "F", rg)

    def connected(self):
        terms = {}
        for (x, y, rg, *_) in self.m["terminals"]:
            if self.sreg[y, x] == rg:
                terms.setdefault(rg, []).append((x, y))
        for rg, st in terms.items():
            f = self.flood(st[0], rg)
            if any(t not in f for t in st):
                return False
        return True

    def furnish(self):
        """turn a few floor blocks into furniture (solid) where every terminal stays reachable."""
        near = {(y + dy, x + dx) for (y, x) in self.terminal_blocks for dy in (-1, 0, 1) for dx in (-1, 0, 1)}
        F = [(y, x) for y in range(1, self.H) for x in range(self.W)
             if self.cls[y][x] == "F" and (y, x) not in near]
        self.r.shuffle(F)
        want = max(1, len(F) // 5)
        placed = 0
        for (y, x) in F:
            if placed >= want:
                break
            rg = self.reg[y, x]
            self.set_block(y, x, "S", 0)
            if self.connected():
                placed += 1
                self.cls[y][x] = "U"            # furniture
            else:
                self.set_block(y, x, "F", rg)

    def grass(self):
        F = [(y, x) for y in range(self.H) for x in range(self.W) if self.cls[y][x] == "F"]
        if not F or not self.voc["grass"]:
            return
        seeds = [F[i] for i in self.r.choice(len(F), size=max(1, len(F) // 12), replace=False)]
        for (y, x) in seeds:
            for dy in range(-1, 2):
                for dx in range(-1, 3):
                    ny, nx = y + dy, x + dx
                    if (ny, nx) in self.terminal_blocks:
                        continue
                    if 0 <= ny < self.H and 0 <= nx < self.W and self.cls[ny][nx] == "F" and self.r.random() < 0.8:
                        self.cls[ny][nx] = "G"

    def render(self, anchors):
        v = self.voc
        out = np.zeros((self.H, self.W), np.uint8)
        floor = pick(self.r, v["floor"], 2) if v["floor"] else 0
        alt_floor = pick(self.r, v["floor"], 4) if v["floor"] and self.m["tileset"] in OUTDOOR else floor
        solid = v["solid"][0][1] if v["solid"] else floor
        solid2 = pick(self.r, v["solid"][1:], 4) if len(v["solid"]) > 1 else solid
        furn = [b for n, b in v["solid"][1:6]] or [solid]
        for y in range(self.H):
            for x in range(self.W):
                c = self.cls[y][x]
                if c == "A":
                    out[y, x] = anchors[(y, x)]
                elif c == "F":
                    out[y, x] = floor if self.noise[y, x] < 3.6 else alt_floor
                elif c == "G":
                    out[y, x] = v["grass"][0][1]
                elif c == "W":
                    out[y, x] = v["water"][0][1] if v["water"] else floor
                elif c == "C":
                    out[y, x] = v["cut"][0][1] if v["cut"] else solid
                elif c == "P":
                    out[y, x] = v["street"][0][1] if v.get("street") else floor
                elif c == "L":
                    out[y, x] = pick(self.r, v["lawn"], 2) if v.get("lawn") else floor
                elif c == "Q":
                    out[y, x] = pick(self.r, v["flower"], 2) if v.get("flower") else floor
                elif c == "Y":
                    out[y, x] = pick(self.r, v["fence"], 2) if v.get("fence") else solid
                elif c == "D":
                    out[y, x] = v["ledge"][0][1]
                elif c == "U":
                    out[y, x] = furn[(x * 7 + y * 3) % len(furn)]
                else:
                    out[y, x] = solid2 if self.noise[y, x] > 4.4 else solid
        return out


def merged_spec(m, pairs):
    """regions that crowd each other at a block are joined (edge strips, shore steps)."""
    import copy
    m = copy.deepcopy(m)
    kind = {int(k): v for k, v in m["regions"].items()}
    for a, b in pairs:
        if b is None or a == b:
            continue
        if kind.get(a) == "walk" and kind.get(b) == "walk":
            lo, hi = min(a, b), max(a, b)
            m["terminals"] = [[t[0], t[1], lo if t[2] == hi else t[2]] + t[3:] for t in m["terminals"]]
            m["edges"] = [[lo if e0 == hi else e0, lo if e1 == hi else e1, k] for e0, e1, k in m["edges"]]
            m["edges"] = [e for e in m["edges"] if e[0] != e[1]]
            m["regions"].pop(str(hi), None)
            kind.pop(hi, None)
        else:
            m["edges"].append([min(a, b), max(a, b), "surf"])
    return m


def build_one(label, m, voc, seed):
    for _ in range(4):
        lay = Layout(label, m, voc[m["tileset"]], seed)
        lay.terminal_blocks = {(t[1] // 2, t[0] // 2) for t in m["terminals"]}
        lay.warp_steps = {(o[0], o[1]) for side in m["openings"].values() for o in side} | \
            {tuple(w) for w in m.get("warps", [])}
        lay.run()
        pairs = list(lay.crowd) + lay.unreached()
        if not pairs:
            break
        m = merged_spec(m, pairs)
    anchors = {tuple(int(v) for v in k.split(",")): b for k, b in m["anchors"].items()}
    return lay.render(anchors), lay.problems


def generate(tree, only=None):
    kit = Kit(tree)
    spec = json.load(open(os.path.join(HERE, "spec/maps.json")))
    voc = vocab(kit, spec)
    seeds = {}
    sp = os.path.join(HERE, "spec/map_seeds.json")
    if os.path.exists(sp):
        seeds = json.load(open(sp))
    done, report = set(), []
    for label, m in sorted(spec["maps"].items()):
        if only and label != only:
            continue
        if m["blk"] in done:
            continue                      # maps sharing one block file get one layout
        done.add(m["blk"])
        blk, problems = build_one(label, m, voc, seeds.get(label, 0))
        with open(os.path.join(tree, m["blk"]), "r+b") as f:
            f.write(blk.tobytes()[:os.path.getsize(os.path.join(tree, m["blk"]))])
        report.append((label, problems))
    bad = [(l, p) for l, p in report if p]
    print(f"maps: {len(report)} layouts written, {len(bad)} with problems")
    for l, p in bad[:15]:
        print("  ", l, "; ".join(p[:3]))
    return report


if __name__ == "__main__":
    generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
