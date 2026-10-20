"""CLEAN ROOM: the roster's numbers are our own.

Rewrites, in the clean tree, keeping every table's format and the engine's
structure (which slot evolves into which, effect ids, TM/HM compatibility):
  data/pokemon/base_stats/*.asm   stats, types (from world.ROSTER), catch rate, base exp, level-1 moves
  data/pokemon/evos_moves.asm     evolution levels shifted, learnsets rebuilt from type pools
  data/moves/moves.asm            power / accuracy / PP retuned (effects and types kept)
  data/pokemon/dex_entries.asm    heights and weights from our body plans

    python -m games.pokered.data_gen <tree>
"""
import glob
import os
import re
import sys

import numpy as np

from cleanroom.decomp.gen import h32
from games.pokered import world

INV_TYPES = {v: k for k, v in world.TYPES.items()}
LEGEND = {"ARTICUNO": 580, "ZAPDOS": 580, "MOLTRES": 580, "MEWTWO": 680, "MEW": 600}
PLAN_HW = {"quad": (0.9, 30), "biped": (1.2, 45), "serpent": (2.5, 60), "bird": (0.9, 18), "fish": (1.0, 25),
           "blob": (0.7, 20), "bug": (0.6, 10), "plant": (0.8, 14), "shell": (0.7, 30), "ghost": (1.3, 3),
           "golem": (1.1, 140)}


def R(*k):
    return np.random.default_rng(h32("kithbound-data", *k))


def read(tree, rel):
    return open(os.path.join(tree, rel), encoding="utf8").read()


def write(tree, rel, s):
    open(os.path.join(tree, rel), "w", encoding="utf8", newline="\n").write(s)


def camel(c):
    return "".join(w.capitalize() for w in c.split("_"))


def evo_graph(tree):
    """{const: [evolves-into consts]} and stage numbers, from the engine's own tables."""
    s = read(tree, "data/pokemon/evos_moves.asm")
    blocks = re.split(r"\n(?=\w+EvosMoves:)", s)
    into = {}
    for b in blocks:
        m = re.match(r"(\w+)EvosMoves:", b)
        if not m:
            continue
        name = m.group(1)
        into[name] = re.findall(r"db EVOLVE_\w+,.*?,\s*(\w+)\s*$", b, re.M)
    return into


def stages(spec, into):
    by_camel = {camel(c): c for c in spec}
    by_camel.update({"NidoranM": "NIDORAN_M", "NidoranF": "NIDORAN_F", "MrMime": "MR_MIME"})
    parent, kids = {}, {}
    for a, outs in into.items():
        ca = by_camel.get(a)
        for o in outs:
            parent[o] = ca
            kids.setdefault(ca, []).append(o)
    st = {}
    for c in spec:
        n, x = 1, c
        while x in parent:
            x, n = parent[x], n + 1
        depth = n
        y, below = c, 0
        while kids.get(y):
            y, below = kids[y][0], below + 1
        st[c] = (depth, depth + below)
    return st


def move_types(tree):
    out = {}
    for m in re.finditer(r"^\s*move\s+(\w+),\s*(\w+),\s*(\d+),\s*(\w+),\s*(\d+),\s*(\d+)", read(tree, "data/moves/moves.asm"), re.M):
        out[m.group(1)] = (m.group(2), int(m.group(3)), m.group(4))
    return out


def pools(mt):
    by = {}
    for mv, (eff, pw, ty) in mt.items():
        if mv in ("STRUGGLE", "CUT", "FLY", "SURF", "STRENGTH", "FLASH"):
            continue
        by.setdefault(ty, []).append((pw, mv))
    for v in by.values():
        v.sort()
    return by


def gen_stats(tree, spec, st):
    n = 0
    for p in glob.glob(os.path.join(tree, "data/pokemon/base_stats/*.asm")):
        s = open(p, encoding="utf8").read()
        m = re.search(r"db DEX_(\w+)", s)
        if not m or m.group(1) not in spec:
            continue
        c = m.group(1)
        name, t1, t2, plan, concept = spec[c]
        d, top = st[c]
        r = R("stats", name)
        total = LEGEND.get(c) or {1: 300, 2: 410, 3: 505}.get(d, 300) + (60 if top == 1 else 0)
        total = int(total + r.integers(-25, 26))
        bias = {"golem": [1.1, 1.2, 1.5, 0.6, 0.8], "bird": [0.9, 1.0, 0.8, 1.5, 0.9],
                "ghost": [0.8, 0.8, 0.8, 1.2, 1.4], "blob": [1.4, 0.9, 1.0, 0.7, 1.0],
                "shell": [0.9, 1.0, 1.6, 0.7, 0.9], "bug": [0.9, 1.0, 0.9, 1.1, 0.8]}.get(plan, [1, 1, 1, 1, 1])
        w = r.dirichlet([8, 8, 8, 8, 8]) * np.array(bias)
        vals = np.clip(np.round(w / w.sum() * total), 15, 200).astype(int)
        ty1, ty2 = INV_TYPES[t1], INV_TYPES[t2 or t1]
        catch = int({1: 200, 2: 110, 3: 45}.get(d, 120) if c not in LEGEND else 3) + int(r.integers(-15, 16))
        catch = int(np.clip(catch, 3, 255))
        bexp = int(total * 0.36 + r.integers(-8, 9))
        s = re.sub(r"(db\s+)\d+,\s*\d+,\s*\d+,\s*\d+,\s*\d+(\s*\n\s*;\s*hp)",
                   lambda mm: mm.group(1) + ", ".join(f"{v:3d}" for v in vals) + mm.group(2), s, 1)
        s = re.sub(r"db \w+, \w+ ; type", f"db {ty1}, {ty2} ; type", s, 1)
        s = re.sub(r"db \d+ ; catch rate", f"db {catch} ; catch rate", s, 1)
        s = re.sub(r"db \d+ ; base exp", f"db {bexp} ; base exp", s, 1)
        open(p, "w", encoding="utf8", newline="\n").write(s)
        n += 1
    return n


def gen_learnsets(tree, spec, st, mt):
    pool = pools(mt)
    by_camel = {camel(c): c for c in spec}
    by_camel.update({"NidoranM": "NIDORAN_M", "NidoranF": "NIDORAN_F", "MrMime": "MR_MIME"})
    s = read(tree, "data/pokemon/evos_moves.asm")
    first_moves = {}

    def fix(m):
        name, body = m.group(1), m.group(2)
        c = by_camel.get(name)
        evo, _, learn = body.partition("; Learnset")

        def lvl(mm):
            r = R("evo", name)
            return f"db EVOLVE_LEVEL, {int(np.clip(int(mm.group(1)) + r.integers(-3, 4), 5, 60))},"
        evo = re.sub(r"db EVOLVE_LEVEL, (\d+),", lvl, evo)
        if c is None:
            return f"{name}EvosMoves:{evo}; Learnset{learn}"
        nm, t1, t2, plan, concept = spec[c]
        r = R("learn", nm)
        types = [INV_TYPES[t1], INV_TYPES[t2 or t1], "NORMAL"]
        cand = []
        for ty in types:
            cand += [mv for pw, mv in pool.get(ty, [])]
        cand = list(dict.fromkeys(cand))
        k = int(r.integers(6, 10))
        picks = list(r.choice(cand, size=min(k + 2, len(cand)), replace=False))
        dmg = [mv for mv in cand if 20 <= mt[mv][1] <= 50 and mt[mv][0] == "NO_ADDITIONAL_EFFECT"] or               [mv for mv in pool["NORMAL"] and [m2 for p2, m2 in pool["NORMAL"] if 20 <= p2 <= 50]]
        opener = str(r.choice(dmg))
        picks = [mv for mv in picks if mv != opener and mv not in ("HORN_DRILL", "FISSURE", "GUILLOTINE")]
        picks.sort(key=lambda mv: mt[mv][1])
        first_moves[c] = [opener, picks[0]]
        rest = picks[1:]
        levels = np.sort(r.choice(np.arange(6, 56), size=len(rest), replace=False))
        lines = "".join(f"\tdb {int(l)}, {mv}\n" for l, mv in zip(levels, rest))
        return f"{name}EvosMoves:{evo}; Learnset\n{lines}\tdb 0\n"
    parts = re.split(r"(?m)^(?=\w+EvosMoves:)", s)
    out = []
    for part in parts:
        m = re.match(r"(\w+)EvosMoves:(.*?\n\tdb 0\n; Learnset\n.*?\tdb 0\n)", part, re.S)
        if m:
            part = fix(m) + part[m.end():]
        out.append(part)
    s = "".join(out)
    write(tree, "data/pokemon/evos_moves.asm", s)
    # level-1 moves in base stats
    for p in glob.glob(os.path.join(tree, "data/pokemon/base_stats/*.asm")):
        t = open(p, encoding="utf8").read()
        m = re.search(r"db DEX_(\w+)", t)
        if m and m.group(1) in first_moves:
            a = first_moves[m.group(1)] + ["NO_MOVE", "NO_MOVE"]
            t = re.sub(r"db \w+, \w+, \w+, \w+ ; level 1 learnset", f"db {a[0]}, {a[1]}, NO_MOVE, NO_MOVE ; level 1 learnset", t, 1)
            open(p, "w", encoding="utf8", newline="\n").write(t)
    return len(first_moves)


def gen_moves(tree):
    s = read(tree, "data/moves/moves.asm")

    def fix(m):
        mv, eff, pw, ty, acc, pp = m.group(2), m.group(3), int(m.group(4)), m.group(5), int(m.group(6)), int(m.group(7))
        r = R("move", mv)
        if pw >= 10:
            pw = int(np.clip(round(pw * r.uniform(0.8, 1.2) / 5) * 5, 10, 200))
        acc = int(np.clip(acc + 5 * r.integers(-2, 2), 50, 100))
        pp = int(np.clip(5 * round(pp * r.uniform(0.75, 1.3) / 5), 5, 40))
        return f"{m.group(1)}move {mv}, {eff}, {pw}, {ty}, {acc}, {pp}"
    s = re.sub(r"^(\s*)move\s+(\w+),\s*(\w+),\s*(\d+),\s*(\w+),\s*(\d+),\s*(\d+)", fix, s, flags=re.M)
    write(tree, "data/moves/moves.asm", s)


def gen_dex(tree, spec, st):
    s = read(tree, "data/pokemon/dex_entries.asm")
    by_camel = {camel(c): c for c in spec}
    by_camel.update({"NidoranM": "NIDORAN_M", "NidoranF": "NIDORAN_F", "MrMime": "MR_MIME"})

    def fix(m):
        c = by_camel.get(m.group(1))
        if not c:
            return m.group(0)
        nm, t1, t2, plan, concept = spec[c]
        d, _ = st[c]
        r = R("dex", nm)
        hm, wk = PLAN_HW[plan]
        h = hm * (0.6 + 0.55 * d) * r.uniform(0.75, 1.3)
        w = wk * (0.4 + 0.8 * d) ** 2 * r.uniform(0.6, 1.5)
        inches = int(round(h * 39.37))
        return f"{m.group(1)}DexEntry:{m.group(2)}\tdb {inches // 12},{inches % 12}\n\tdw {int(np.clip(round(w * 22.05), 1, 9999))}\n"
    s = re.sub(r"(\w+)DexEntry:(\n\tdb \"[^\"]*\"\n)\tdb \d+,\d+\n\tdw \d+\n", fix, s)
    write(tree, "data/pokemon/dex_entries.asm", s)


def main(argv):
    tree = argv[1]
    spec = world.species_by_const(tree)
    st = stages(spec, evo_graph(tree))
    mt0 = move_types(tree)
    a = gen_stats(tree, spec, st)
    b = gen_learnsets(tree, spec, st, mt0)
    gen_moves(tree)
    gen_dex(tree, spec, st)
    print(f"data: {a} base stats, {b} learnsets, moves retuned, dex sizes")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
