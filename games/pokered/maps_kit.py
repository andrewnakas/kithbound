"""Map facts of a pokered tree, read from the engine's own tables.

    kit = Kit(tree)
    kit.maps[label] -> Map(label, const, w, h, tileset, blk path, connections, warps, bgs, objects, border)
    kit.tilesets[name] -> Tileset(name, const, blocks (n,16), coll set, doors, warps, grass, counters, water)
    kit.step_tile(map, blocks, sx, sy) -> tile id under a 16x16 step (bottom-left 8x8 tile)
"""
import glob
import os
import re
from dataclasses import dataclass, field

import numpy as np


def _num(s):
    s = s.strip()
    if s.startswith("$"):
        return int(s[1:], 16)
    if s.startswith("-"):
        return -int(s[1:])
    return int(s)


@dataclass
class Tileset:
    name: str
    const: str
    index: int
    block_file: str
    blocks: np.ndarray
    coll: set
    doors: set = field(default_factory=set)
    warps: set = field(default_factory=set)
    grass: int = -1
    counters: tuple = ()
    water: bool = False


@dataclass
class Map:
    label: str
    const: str
    w: int
    h: int
    tileset: str
    blk: str = ""
    connections: list = field(default_factory=list)   # (dir, label, const, offset)
    warps: list = field(default_factory=list)         # (x, y, dest, idx)
    bgs: list = field(default_factory=list)           # (x, y, text)
    objects: list = field(default_factory=list)       # (x, y, sprite, movement)
    border: int = 0


class Kit:
    def __init__(self, tree):
        self.tree = tree
        self.sizes = {}
        for m in re.finditer(r"map_const\s+(\w+),\s*(\d+),\s*(\d+)", self.read("constants/map_constants.asm")):
            self.sizes[m.group(1)] = (int(m.group(2)), int(m.group(3)))
        self._tilesets()
        self._maps()

    def read(self, rel):
        return open(os.path.join(self.tree, rel), encoding="utf8").read()

    def _tilesets(self):
        consts = re.findall(r"const (\w+)\s*;", self.read("constants/tileset_constants.asm"))
        files, label_of = {}, {}
        pend = []
        for line in self.read("gfx/tilesets.asm").split("\n"):
            m = re.match(r"(\w+)_Block::\s*(?:INCBIN \"([^\"]+)\")?", line)
            if m:
                pend.append(m.group(1))
                if m.group(2):
                    for p in pend:
                        files[p] = m.group(2)
                    pend = []
        coll, cur = {}, []
        for line in self.read("data/tilesets/collision_tile_ids.asm").split("\n"):
            m = re.match(r"(\w+)_Coll::", line)
            if m:
                cur.append(m.group(1))
                continue
            m = re.match(r"\s*coll_tiles\s*(.*)", line)
            if m and cur:
                ids = {_num(x) for x in m.group(1).split(",") if x.strip()}
                for c in cur:
                    coll[c] = ids
                cur = []
        rows = re.findall(r"^\s*tileset (\w+),\s*([-$\w]+),\s*([-$\w]+),\s*([-$\w]+),\s*([-$\w]+)", self.read(
            "data/tilesets/tileset_headers.asm"), re.M)
        doors = self._door_tiles()
        warps = self._warp_tiles()
        water = set(re.findall(r"^\s*db (\w+)$", self.read("data/tilesets/water_tilesets.asm"), re.M))
        self.tilesets = {}
        for i, (name, c1, c2, c3, grass) in enumerate(rows):
            const = consts[i]
            data = open(os.path.join(self.tree, files[name]), "rb").read()
            self.tilesets[const] = Tileset(name, const, i, files[name], np.frombuffer(data, np.uint8).reshape(-1, 16),
                                           coll[name], doors.get(const, set()), warps.get(i, set()), _num(grass),
                                           tuple(_num(c) for c in (c1, c2, c3) if _num(c) >= 0), const in water)

    def _door_tiles(self):
        s = self.read("data/tilesets/door_tile_ids.asm")
        ptr = dict(re.findall(r"dbw (\w+),\s*(\.\w+)", s))
        lists = dict(re.findall(r"(\.\w+):\s*\n\s*door_tiles\s*([^\n]*)", s))
        out = {}
        for const, lab in ptr.items():
            out[const] = {_num(x) for x in lists.get(lab, "").split(",") if x.strip()}
        return out

    def _warp_tiles(self):
        s = self.read("data/tilesets/warp_tile_ids.asm")
        order = re.findall(r"dw (\.\w+)", s)
        out = {}
        lines = s.split("\n")
        for i, lab in enumerate(order):
            ids = set()
            start = next(n for n, l in enumerate(lines) if l.strip() == lab + ":")
            for l in lines[start + 1:]:
                l = l.split(";")[0].strip()
                if not l or l.endswith(":"):
                    continue
                if l.startswith("db "):
                    ids |= {_num(x) for x in l[3:].split(",") if x.strip()}
                elif l.startswith("warp_tiles"):
                    ids |= {_num(x) for x in l[10:].split(",") if x.strip()}
                    break
            out[i] = ids
        return out

    def _maps(self):
        blk = {}
        pend = []
        for line in self.read("maps.asm").split("\n"):
            for m in re.finditer(r"(\w+)_Blocks:", line):
                pend.append(m.group(1))
            m = re.search(r'INCBIN "(maps/[^"]+)"', line)
            if m:
                for p in pend:
                    blk[p] = m.group(1)
                pend = []
        self.maps = {}
        for p in sorted(glob.glob(os.path.join(self.tree, "data/maps/headers/*.asm"))):
            s = open(p, encoding="utf8").read()
            m = re.search(r"map_header\s+(\w+),\s*(\w+),\s*(\w+)", s)
            if not m:
                continue
            label, const, ts = m.groups()
            w, h = self.sizes[const]
            mp = Map(label, const, w, h, ts, blk.get(label, ""))
            mp.connections = [(a, b, c, int(d)) for a, b, c, d in
                              re.findall(r"connection\s+(\w+),\s*(\w+),\s*(\w+),\s*(-?\d+)", s)]
            op = os.path.join(self.tree, "data/maps/objects", label + ".asm")
            if os.path.exists(op):
                o = open(op, encoding="utf8").read()
                b = re.search(r"db \$([0-9a-fA-F]+) ; border block", o)
                mp.border = int(b.group(1), 16) if b else 0
                mp.warps = [(int(x), int(y), d, i) for x, y, d, i in
                            re.findall(r"warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\w+)", o)]
                mp.bgs = [(int(x), int(y), t) for x, y, t in re.findall(r"bg_event\s+(\d+),\s*(\d+),\s*(\w+)", o)]
                mp.objects = [(int(x), int(y), sp, mv) for x, y, sp, mv in
                              re.findall(r"object_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\w+)", o)]
            self.maps[label] = mp

    def blocks(self, mp):
        data = open(os.path.join(self.tree, mp.blk), "rb").read()
        a = np.frombuffer(data, np.uint8)[:mp.w * mp.h]
        if len(a) < mp.w * mp.h:            # a few maps read past their file into the next one
            a = np.concatenate([a, np.full(mp.w * mp.h - len(a), mp.border, np.uint8)])
        return a.reshape(mp.h, mp.w).copy()

    def step_tile(self, ts, blocks, sx, sy):
        b = blocks[sy // 2, sx // 2]
        t = self.tilesets[ts].blocks[b]
        return int(t[(2 * (sy % 2) + 1) * 4 + 2 * (sx % 2)])

    def quad_tiles(self, ts, block):
        """the four tiles that decide collision for a block's 2x2 steps: [(qy,qx) -> tile]."""
        t = self.tilesets[ts].blocks[block]
        return {(qy, qx): int(t[(2 * qy + 1) * 4 + 2 * qx]) for qy in (0, 1) for qx in (0, 1)}
