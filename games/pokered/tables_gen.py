"""CLEAN ROOM: KITHBOUND's tables are our own design.

Rewrites, in the given tree, keeping each file's format, labels and table lengths:
  data/trainers/parties.asm         themed parties (class theme, stage by level, levels +-1);
                                    rival / professor starter slots stay in place
  data/trainers/special_moves.asm   leaders' and elites' signature moves of their type
  data/wild/maps/*.asm              habitat encounter tables (levels +-2, DAWN/DUSK differ)
  data/wild/good_rod.asm, super_rod.asm   fishing
  data/types/type_matchups.asm      our own chart for the 15 types
  data/items/prices.asm, tm_prices.asm    our economy
  data/sgb/sgb_palettes.asm         our colours;  data/pokemon/palettes.asm  palette per kith
  data/sgb/sgb_border.asm           border colours
  data/events/slot_machine_wheels.asm     reel layout (new symbol counts and order)

    python -m games.pokered.tables_gen <tree>
"""
import colorsys
import os
import re
import sys

import numpy as np

from cleanroom.decomp.gen import h32
from games.pokered import world
from games.pokered.data_gen import camel, read, write

INV_TYPES = {v: k for k, v in world.TYPES.items()}
LEGENDS = {"ARTICUNO", "ZAPDOS", "MOLTRES", "MEWTWO", "MEW"}
STARTER_ROOTS = {"BULBASAUR", "CHARMANDER", "SQUIRTLE"}
RARE_ROOTS = {"LAPRAS", "SNORLAX", "DRATINI", "OMANYTE", "KABUTO", "AERODACTYL", "EEVEE", "PORYGON", "DITTO",
              "CHANSEY", "KANGASKHAN", "SCYTHER", "PINSIR", "TAUROS", "LICKITUNG", "HITMONLEE", "HITMONCHAN",
              "JYNX", "ELECTABUZZ", "MAGMAR", "MR_MIME", "FARFETCHD"}
STATS = {}


def R(*k):
    return np.random.default_rng(h32("kithbound-tables", *k))


def stat(name, total, changed):
    a, b = STATS.get(name, (0, 0))
    STATS[name] = (a + total, b + changed)


# ------------------------------------------------------------------ evolution families

class Dex:
    def __init__(self, tree):
        self.spec = world.species_by_const(tree)
        by_camel = {camel(c): c for c in self.spec}
        by_camel.update({"NidoranM": "NIDORAN_M", "NidoranF": "NIDORAN_F", "MrMime": "MR_MIME"})
        self.edges, self.parent = {}, {}
        s = read(tree, "data/pokemon/evos_moves.asm")
        for part in re.split(r"(?m)^(?=\w+EvosMoves:)", s):
            m = re.match(r"(\w+)EvosMoves:", part)
            if not m or m.group(1) not in by_camel:
                continue
            a = by_camel[m.group(1)]
            evo = part.split("; Learnset")[0]
            for mm in re.finditer(r"db EVOLVE_(LEVEL|ITEM|TRADE),\s*([^\n;]*)", evo):
                f = [x.strip() for x in mm.group(2).split(",")]
                kind, child = mm.group(1), f[-1]
                req = int(f[0]) if kind == "LEVEL" else 0
                self.edges.setdefault(a, []).append((kind, req, child))
                self.parent[child] = a
        self.roots = [c for c in self.spec if c not in self.parent]

    def root(self, c):
        while c in self.parent:
            c = self.parent[c]
        return c

    def members(self, r):
        out, todo = [], [r]
        while todo:
            x = todo.pop(0)
            out.append(x)
            todo += [e[2] for e in self.edges.get(x, [])]
        return out

    def types(self, r):
        t = set()
        for m in self.members(r):
            t |= {self.spec[m][1], self.spec[m][2]} - {None}
        return t

    def type1s(self, r):
        return {self.spec[m][1] for m in self.members(r)}

    def evolve(self, c, lvl, rng, mode, prefer=()):
        """Highest stage the level allows. mode: base | wild | trainer | fixed."""
        if mode == "base":
            return c
        node, prev = c, 0
        while self.edges.get(node):
            opts = self.edges[node]
            fit = [o for o in opts if {self.spec[o[2]][1], self.spec[o[2]][2]} & set(prefer)]
            opts = fit or opts
            kind, req, child = opts[0] if mode == "fixed" and len(opts) == 1 else opts[int(rng.integers(len(opts)))]
            need = req if kind == "LEVEL" else max(prev + 8, 26) if kind == "ITEM" else max(prev + 8, 34)
            if lvl < need:
                break
            slack = lvl - need
            if mode == "wild" and rng.random() > (0.35 if slack < 5 else 0.75):
                break
            if mode == "trainer" and slack < 3 and rng.random() < 0.3:
                break
            node, prev = child, need
        return node

    def pool(self, prim, sec=(), plans=(), rare=False, starters=False, own=False, land=False):
        """[(root, weight)] for a theme."""
        out = []
        for r in self.roots:
            if r in LEGENDS or r in ("MISSINGNO",) or (r in STARTER_ROOTS and not starters):
                continue
            if r in RARE_ROOTS and not rare:
                continue
            ty, t1 = self.types(r), self.type1s(r)
            if land and any(self.spec[m][3] == "fish" for m in self.members(r)):
                continue
            if own:  # wild: the first two stages must fit the habitat
                near = [r] + [e[2] for e in self.edges.get(r, [])]
                ty = {t for m in near for t in self.spec[m][1:3]} - {None}
                t1 = {self.spec[m][1] for m in near}
            w = 0.0
            if t1 & set(prim):
                w = 5.0
            elif ty & set(prim):
                w = 2.5
            elif ty & set(sec):
                w = 1.0
            if self.spec[r][3] in plans:
                w = max(w, 3.0)
            if w:
                out.append((r, w))
        return out


def draw(rng, pool, exclude=()):
    p = [(r, w) for r, w in pool if r not in exclude] or pool
    w = np.array([x[1] for x in p], float)
    return p[int(rng.choice(len(p), p=w / w.sum()))][0]


# ------------------------------------------------------------------ 1. trainer parties

THEMES = {  # engine class: (primary types, secondary types, body plans)
    "YOUNGSTER": (["PLAIN"], ["SOIL", "VENOM", "GALE"], ()), "BUG_CATCHER": (["HIVE"], [], ()),
    "LASS": (["PLAIN", "LEAF"], ["MIND"], ()), "SAILOR": (["TIDE"], ["BRAWL"], ()),
    "JR_TRAINER_M": (["STONE", "EMBER"], ["PLAIN", "SOIL"], ()), "JR_TRAINER_F": (["LEAF", "TIDE"], ["PLAIN", "MIND"], ()),
    "POKEMANIAC": (["WYRM", "STONE"], ["SOIL", "TIDE"], ()), "SUPER_NERD": (["VOLT", "EMBER"], ["VENOM"], ()),
    "HIKER": (["STONE", "SOIL"], ["BRAWL"], ()), "BIKER": (["VENOM"], ["EMBER"], ()),
    "BURGLAR": (["EMBER"], ["SHADE", "PLAIN"], ()), "ENGINEER": (["VOLT"], [], ()),
    "UNUSED_JUGGLER": (["MIND"], [], ()), "FISHER": (["TIDE"], [], ()), "SWIMMER": (["TIDE"], ["FROST"], ()),
    "CUE_BALL": (["BRAWL"], ["VENOM"], ()), "GAMBLER": (["VOLT", "PLAIN"], ["MIND"], ()),
    "BEAUTY": (["LEAF", "TIDE"], ["PLAIN"], ()), "PSYCHIC_TR": (["MIND"], [], ()),
    "ROCKER": (["VOLT"], ["EMBER"], ()), "JUGGLER": (["MIND"], ["VENOM"], ()),
    "TAMER": (["EMBER", "SOIL"], ["PLAIN"], ("quad",)), "BIRD_KEEPER": (["GALE"], [], ("bird",)),
    "BLACKBELT": (["BRAWL"], [], ()), "CHIEF": (["PLAIN"], [], ()), "SCIENTIST": (["VOLT", "VENOM"], ["MIND"], ()),
    "ROCKET": (["VENOM", "SHADE"], ["PLAIN"], ()), "COOLTRAINER_M": (["WYRM", "EMBER", "SOIL", "BRAWL"], ["PLAIN"], ()),
    "COOLTRAINER_F": (["TIDE", "LEAF", "MIND", "FROST"], ["PLAIN"], ()), "GENTLEMAN": (["PLAIN", "EMBER"], [], ("quad",)),
    "CHANNELER": (["SHADE"], ["MIND"], ()), "PROF_OAK": (["LEAF", "PLAIN"], ["SOIL"], ()),
    # leaders and the top four
    "BROCK": (["STONE"], [], ()), "MISTY": (["TIDE"], [], ()), "LT_SURGE": (["VOLT"], [], ()),
    "ERIKA": (["LEAF"], [], ()), "KOGA": (["VENOM"], [], ()), "SABRINA": (["MIND"], [], ()),
    "BLAINE": (["EMBER"], [], ()), "GIOVANNI": (["SOIL"], ["STONE"], ()),
    "LORELEI": (["FROST"], ["TIDE"], ()), "BRUNO": (["BRAWL"], ["STONE"], ()),
    "AGATHA": (["SHADE"], ["VENOM", "MIND"], ()), "LANCE": (["WYRM"], ["GALE"], ()),
}
BOSSES = {"BROCK", "MISTY", "LT_SURGE", "ERIKA", "KOGA", "SABRINA", "BLAINE", "GIOVANNI",
          "LORELEI", "BRUNO", "AGATHA", "LANCE"}
STARTER_KEEP = {"RIVAL1", "RIVAL2", "RIVAL3", "PROF_OAK"}


def gen_parties(tree, dex):
    s = read(tree, "data/trainers/parties.asm")
    labels = re.findall(r"^\tdw (\w+)Data$", s, re.M)
    consts = re.findall(r"trainer_const (\w+)", read(tree, "constants/trainer_constants.asm"))[1:]
    cls_of = dict(zip(labels, consts))
    starters = {m for r in STARTER_ROOTS for m in dex.members(r)}
    # rival roles: each old non-starter family in the rival/professor teams gets one new family of the same type1
    role = {}
    used = set()
    for lab in ("Rival1", "Rival2", "Rival3", "ProfOak"):
        blk = re.search(rf"^{lab}Data:\n(.*?)(?=^\w+Data:|\Z)", s, re.M | re.S).group(1)
        for sp in re.findall(r"\b([A-Z][A-Z0-9_]+)\b", blk):
            if sp in dex.spec and sp not in starters:
                r = dex.root(sp)
                if r in role:
                    continue
                t1 = dex.spec[r][1]
                pool = [(x, w) for x, w in dex.pool([t1], rare=True) if x != r and x not in used]
                pool = [(x, w * (2 if len(dex.members(x)) > 1 else 1)) for x, w in pool] or dex.pool(["PLAIN"])
                role[r] = draw(R("rivalrole", r), pool)
                used.add(role[r])
    out, cur, idx, total, same = [], None, 0, 0, 0
    for line in s.split("\n"):
        m = re.match(r"^(\w+)Data:$", line)
        if m:
            cur, idx = m.group(1), 0
            out.append(line)
            continue
        m = re.match(r"^\tdb (.*), 0$", line)
        if not cur or cur not in cls_of or not m:
            out.append(line)
            continue
        cls = cls_of[cur]
        f = [x.strip() for x in m.group(1).split(",")]
        rng = R("party", cur, idx)
        idx += 1
        if f[0] == "$FF":
            pairs = [(int(f[i]), f[i + 1]) for i in range(1, len(f), 2)]
        else:
            pairs = [(int(f[0]), x) for x in f[1:]]
        lv_shift = {}
        new = []
        oldfam = {dex.root(o) for _, o in pairs if o in dex.spec}
        count = {}
        for pos, (lv, old) in enumerate(pairs):
            if f[0] == "$FF":
                key = (cur, lv) if cls in STARTER_KEEP else (cur, idx, pos)
                nl = int(np.clip(lv + R("lvl", *key).integers(-1, 2), 2, 100))
            else:
                jr = R("lvl", cur, lv) if cls in STARTER_KEEP else rng
                nl = lv_shift.setdefault("all", int(np.clip(lv + jr.integers(-1, 2), 2, 100)))
            if cls in STARTER_KEEP:
                if old in starters:
                    sp = dex.evolve(dex.root(old), nl, None, "fixed")  # same line, stage by level
                else:
                    sp = dex.evolve(role[dex.root(old)], nl, R("rivalbranch", role[dex.root(old)]), "fixed")
            else:
                prim, sec, plans = THEMES.get(cls, (["PLAIN"], [], ()))
                boss = cls in BOSSES
                base = dex.pool(prim, sec, plans, rare=(boss or nl >= 25))

                thin = sum(1 for x, w in base if dex.types(x) & set(prim)) < len(pairs)

                def room(x):  # a boss of a thin type may field a family twice (second one a stage lower)
                    return count.get(x, 0) < (2 if boss and thin and dex.types(x) & set(prim) else 1)
                if boss:  # the type comes first; the old party's families stay possible for a thin type
                    base = [(x, w * (1 if dex.types(x) & set(prim) else 0.15)) for x, w in base if x != "MAGIKARP"]
                    pool = [(x, w * (0.5 if x in oldfam else 1)) for x, w in base if room(x)]
                else:  # never echo the old party's families
                    pool = [(x, w) for x, w in base if room(x) and x not in oldfam]
                pool = pool or [(x, w) for x, w in base if room(x)] or base
                sp, r = old, None
                for _ in range(12):
                    r = draw(rng, pool)
                    sp = dex.evolve(r, nl, rng, "trainer", prim + sec)
                    if count.get(r):
                        if sp not in dex.parent:  # nothing a stage lower: drop this family here
                            pool = [(x, w) for x, w in pool if x != r] or pool
                            continue
                        sp = dex.parent[sp]
                    fits = {dex.spec[sp][1], dex.spec[sp][2]} & set(prim + sec) or dex.spec[sp][3] in plans
                    if sp != old and fits:
                        break
                    if not fits:
                        pool = [(x, w) for x, w in pool if x != r] or pool
                count[r] = count.get(r, 0) + 1
            new.append((nl, sp))
            total += 1
            same += sp == old
        if f[0] == "$FF":
            body = ", ".join(f"{l}, {sp}" for l, sp in new)
            out.append(f"\tdb $FF, {body}, 0")
        else:
            out.append(f"\tdb {new[0][0]}, " + ", ".join(sp for _, sp in new) + ", 0")
    write(tree, "data/trainers/parties.asm", "\n".join(out))
    stat("parties.asm (party slots)", total, total - same)
    return role


# ------------------------------------------------------------------ 2. signature moves

LONE = ["ROCK", "WATER", "ELECTRIC", "GRASS", "POISON", "PSYCHIC_TYPE", "FIRE", "GROUND"]
TEAM = {"LORELEI": "ICE", "BRUNO": "FIGHTING", "AGATHA": "GHOST", "LANCE": "DRAGON"}


def move_table(tree):
    out = {}
    for m in re.finditer(r"^\s*move\s+(\w+),\s*(\w+),\s*(\d+),\s*(\w+),\s*(\d+),\s*(\d+)", read(tree, "data/moves/moves.asm"), re.M):
        out[m.group(1)] = (m.group(2), int(m.group(3)), m.group(4))
    return out


def pick_move(mt, ty, old, key):
    c = [(pw, mv) for mv, (eff, pw, t) in mt.items() if t == ty and mv != old and eff not in ("OHKO_EFFECT", "DREAM_EATER_EFFECT")]
    c.sort(reverse=True)
    c = c[:2] or [(0, old)]
    return c[int(R("sigmove", key).integers(len(c)))][1]


def gen_special(tree):
    s = read(tree, "data/trainers/special_moves.asm")
    mt = move_table(tree)
    n = [0, 0]
    k = iter(range(100))

    def lone(m):
        i = next(k)
        mv = pick_move(mt, LONE[i], m.group(2), ("lone", i)) if i < len(LONE) else m.group(2)
        n[0] += 1
        n[1] += mv != m.group(2)
        return f"\tdb {m.group(1)}, {mv}"
    s = re.sub(r"^\tdb (\d+), (\w+)$", lone, s, flags=re.M)

    def team(m):
        mv = pick_move(mt, TEAM[m.group(1)], m.group(3), ("team", m.group(1)))
        n[0] += 1
        n[1] += mv != m.group(3)
        return f"\tdb {m.group(1)},{m.group(2)}{mv}"
    s = re.sub(r"^\tdb (LORELEI|BRUNO|AGATHA|LANCE),(\s*)(\w+)$", team, s, flags=re.M)
    write(tree, "data/trainers/special_moves.asm", s)
    stat("special_moves.asm", *n)


# ------------------------------------------------------------------ 3. wild tables

ROUTE_FLAVOR = {2: ["VENOM"], 3: ["SOIL"], 4: ["VENOM", "SOIL"], 5: ["MIND"], 6: ["MIND", "TIDE"], 7: ["EMBER"],
                8: ["EMBER", "MIND"], 9: ["VENOM", "SOIL"], 10: ["VOLT"], 11: ["SOIL"], 12: ["TIDE"],
                13: ["TIDE"], 14: ["VENOM"], 15: ["VENOM"], 16: ["BRAWL"], 17: ["BRAWL"], 18: ["BRAWL", "GALE"],
                21: ["TIDE"], 22: ["BRAWL"], 23: ["STONE", "BRAWL", "WYRM"], 24: ["MIND", "LEAF"], 25: ["MIND", "TIDE"]}
BASE_ROUTE = ["PLAIN", "GALE", "HIVE", "LEAF"]


def habitat(area, section):
    """(primary, secondary, rare allowed)"""
    if section == "water":
        return (["TIDE", "FROST"] if "Seafoam" in area else ["TIDE"]), [], False
    m = re.match(r"Route(\d+)$", area)
    if m:
        fl = ROUTE_FLAVOR.get(int(m.group(1)), [])
        return BASE_ROUTE, fl, False
    if "Forest" in area:
        return ["HIVE", "LEAF"], [], False
    if "Tower" in area:
        return ["SHADE"], ["MIND"], False
    if "PowerPlant" in area:
        return ["VOLT"], [], False
    if "Seafoam" in area:
        return ["FROST", "TIDE"], [], False
    if "Mansion" in area:
        return ["EMBER", "VENOM"], [], False
    if "Safari" in area:
        return ["PLAIN", "LEAF", "HIVE"], ["SOIL", "TIDE", "BRAWL"], True
    if "Diglett" in area:
        return ["SOIL"], ["STONE"], False
    if "CeruleanCave" in area:
        return ["STONE", "SOIL", "SHADE", "MIND"], ["WYRM", "FROST"], True
    if "VictoryRoad" in area:
        return ["STONE", "SOIL", "BRAWL"], ["SHADE"], False
    return ["STONE", "SOIL", "SHADE"], [], False  # caves


SLOTW = [6, 4, 3, 2, 1.5, 1]


def area_pool(dex, area, section, rng, used, n):
    prim, sec, rare = habitat(area, section)
    pool = dex.pool(prim, sec, rare=rare, own=True, land=section == "grass")
    if rare:
        pool = [(r, w * (1.5 if r in RARE_ROOTS else 1)) for r, w in pool]
    pool = [(r, w * (0.4 if r in used else 1.0)) for r, w in pool]
    fam = []
    for _ in range(min(n, len(pool))):
        fam.append(draw(rng, pool, fam))
    wt = dict(pool)
    fam = sorted(fam, key=lambda r: -wt[r])  # best habitat fit takes the common slots
    return fam, [wt[r] for r in fam]


def fill_slot(dex, fam, fw, extra, slot, lvl, rng, early):
    w = list(SLOTW[:len(fam)])
    if slot >= 6:
        w = w[::-1]
    w = [a * b for a, b in zip(w, fw)]
    cand = fam + ([extra] if extra else [])
    w = w + ([0.25 * sum(w)] if extra else [])
    # no redraw on a same-species slot: a thin habitat (one shade family) must still be its theme
    r = cand[int(rng.choice(len(cand), p=np.array(w) / sum(w)))]
    return dex.evolve(r, lvl, rng, "base" if early else "wild")


def gen_wild(tree, dex):
    order = re.findall(r'INCLUDE "data/wild/maps/(\w+)\.asm"', read(tree, "data/wild/grass_water.asm"))
    used = set()
    total = same = rbdiff = rbfiles = 0
    for area in order:
        rel = f"data/wild/maps/{area}.asm"
        s = read(tree, rel)
        lines = s.split("\n")
        maxlv = {}
        sec = None
        for ln in lines:
            if "def_grass_wildmons" in ln:
                sec = "grass"
            elif "def_water_wildmons" in ln:
                sec = "water"
            m = re.match(r"^\tdb\s+(\d+), ([A-Z][A-Z0-9_]*)\s*$", ln)
            if m:
                maxlv[sec] = max(maxlv.get(sec, 0), int(m.group(1)))
        pools = {}
        for sc in maxlv:
            rng = R("wildpool", area, sc)
            fam, fw = area_pool(dex, area, sc, rng, used, 4)
            rest = [r for r, w in dex.pool(*habitat(area, sc)[:2], rare=habitat(area, sc)[2], own=True, land=sc == "grass") if r not in fam]
            ex = list(rng.choice(rest, size=min(2, len(rest)), replace=False)) if rest else []
            pools[sc] = (fam, fw, ex + [None] * (2 - len(ex)))
            used |= set(fam) | set(x for x in ex if x)
        out, sec, ver, slot, red_start, blk = [], None, None, 0, 0, {}
        for ln in lines:
            if "def_grass_wildmons" in ln:
                sec, slot = "grass", 0
            elif "def_water_wildmons" in ln:
                sec, slot = "water", 0
            if ln.startswith("IF DEF(_RED)"):
                ver, red_start = "RED", slot
            elif ln.startswith("IF DEF(_BLUE)"):
                ver, slot = "BLUE", red_start
            elif ln.startswith("ENDC"):
                ver = None
            m = re.match(r"^\tdb\s+(\d+), ([A-Z][A-Z0-9_]*)\s*$", ln)
            if m and sec in pools:
                lv, old = int(m.group(1)), m.group(2)
                rng = R("wild", area, sec, ver, slot)
                nl = int(np.clip(lv + rng.integers(-2, 3), 2, 100))
                fam, fw, ex = pools[sec]
                extra = ex[0] if ver == "RED" else ex[1] if ver == "BLUE" else None
                sp = fill_slot(dex, fam, fw, extra, slot, nl, rng, maxlv[sec] <= 15)
                if ver:
                    blk.setdefault(ver, []).append(sp)
                out.append(f"\tdb {nl:2d}, {sp}")
                total += 1
                same += sp == old
                slot += 1
                continue
            out.append(ln)
        if blk:
            rbfiles += 1
            rbdiff += blk.get("RED") != blk.get("BLUE")
        write(tree, rel, "\n".join(out))
    stat("wild maps (slots)", total, total - same)
    print(f"  wild: {len(order)} areas, {rbdiff}/{rbfiles} DAWN/DUSK blocks differ, {len(used)} families placed")
    # fishing
    for rel, theme in (("data/wild/good_rod.asm", "good"), ("data/wild/super_rod.asm", "super")):
        if not os.path.exists(os.path.join(tree, rel)):
            continue
        s = read(tree, rel)
        group = ["main"]
        n = [0, 0]

        def fish(m, group=group, n=n, theme=theme):
            lv, old = int(m.group(1)), m.group(2)
            rng = R("fish", theme, group[0], m.start())
            prim = ["TIDE", "FROST"] if group[0] in (".Group8", ".Group9") else ["TIDE"]
            pool = dex.pool(prim, rare=group[0] in (".Group6", ".Group9"), own=True)
            nl = int(np.clip(lv + rng.integers(-2, 3), 2, 100))
            sp = old
            for _ in range(8):
                sp = dex.evolve(draw(rng, pool), nl, rng, "wild")
                if sp != old:
                    break
            n[0] += 1
            n[1] += sp != old
            return f"\tdb {nl:2d}, {sp}" if m.group(0).startswith("\tdb  ") else f"\tdb {nl}, {sp}"

        out = []
        for ln in s.split("\n"):
            if re.match(r"^\.Group\d+:", ln):
                group[0] = ln[:-1]
            out.append(re.sub(r"^\tdb\s+(\d+), ([A-Z][A-Z0-9_]*)\s*$", fish, ln))
        write(tree, rel, "\n".join(out))
        stat(os.path.basename(rel), *n)


# ------------------------------------------------------------------ 4. type chart

# attacker: {defender: multiplier}  2 = strong, .5 = weak, 0 = none.  Our own elemental logic:
# light (ember, volt) burns away shade; stone has no mind and cannot be poisoned; frost locks water
# and kills swarms; wyrms rule the sky; fists smash gears and scales; soil smothers flame and crawlers;
# wind scatters fumes and dust; vines short volt; mud blunts water.
CHART = {
    "PLAIN": {"SHADE": 0, "WYRM": .5, "BRAWL": .5},
    "BRAWL": {"STONE": 2, "VOLT": 2, "WYRM": 2, "PLAIN": 2, "SHADE": .5, "TIDE": .5, "LEAF": .5},
    "GALE": {"EMBER": 2, "SOIL": 2, "VENOM": 2, "STONE": .5, "WYRM": .5, "FROST": .5},
    "VENOM": {"TIDE": 2, "BRAWL": 2, "PLAIN": 2, "LEAF": 2, "STONE": 0, "VOLT": .5, "VENOM": .5},
    "SOIL": {"EMBER": 2, "VOLT": 2, "FROST": 2, "HIVE": 2, "TIDE": .5, "GALE": .5, "SHADE": .5},
    "STONE": {"GALE": 2, "FROST": 2, "VOLT": 2, "TIDE": .5, "WYRM": .5, "LEAF": .5},
    "HIVE": {"LEAF": 2, "SOIL": 2, "MIND": .5, "FROST": .5, "STONE": .5, "EMBER": .5},
    "SHADE": {"MIND": 2, "SHADE": 2, "BRAWL": 2, "PLAIN": 0, "VOLT": .5, "EMBER": .5},
    "EMBER": {"LEAF": 2, "FROST": 2, "SHADE": 2, "VENOM": 2, "TIDE": .5, "SOIL": .5, "EMBER": .5},
    "TIDE": {"EMBER": 2, "STONE": 2, "SOIL": .5, "FROST": .5, "VENOM": .5},
    "LEAF": {"TIDE": 2, "STONE": 2, "VOLT": 2, "EMBER": .5, "FROST": .5},
    "VOLT": {"TIDE": 2, "GALE": 2, "HIVE": 2, "SHADE": 2, "SOIL": 0, "STONE": .5},
    "MIND": {"VENOM": 2, "BRAWL": 2, "WYRM": 2, "STONE": 0, "SHADE": .5, "HIVE": .5},
    "FROST": {"TIDE": 2, "WYRM": 2, "LEAF": 2, "HIVE": 2, "EMBER": .5, "STONE": .5},
    "WYRM": {"WYRM": 2, "GALE": 2, "MIND": .5, "FROST": .5},
}
MULT = {2: "SUPER_EFFECTIVE", .5: "NOT_VERY_EFFECTIVE", 0: "NO_EFFECT"}


def gen_types(tree):
    rel = "data/types/type_matchups.asm"
    s = read(tree, rel)
    old = set(re.findall(r"^\tdb (\w+),\s+(\w+),\s+(\w+)\s*$", s, re.M))
    rows = []
    for a, d in CHART.items():
        for b, x in d.items():
            rows.append((INV_TYPES[a], INV_TYPES[b], MULT[x]))
    new_share = sum(r not in old for r in rows) / len(rows)
    assert new_share >= 0.6, new_share
    head = s.split("\n\tdb ")[0]
    body = "".join(f"\tdb {a + ',':<13} {b + ',':<13} {m}\n" for a, b, m in rows)
    write(tree, rel, head + "\n" + body + "\tdb -1 ; end\n")
    stat("type_matchups.asm (new triples)", len(rows), sum(r not in old for r in rows))


# ------------------------------------------------------------------ 5. prices

PRICES = dict(
    ULTRA_BALL=1100, GREAT_BALL=550, POKE_BALL=150, SAFARI_BALL=800, ANTIDOTE=150, BURN_HEAL=200, ICE_HEAL=200,
    AWAKENING=250, PARLYZ_HEAL=150, FULL_RESTORE=2800, MAX_POTION=2200, HYPER_POTION=1200, SUPER_POTION=650,
    POTION=250, ESCAPE_ROPE=450, REPEL=300, FIRE_STONE=2400, THUNDER_STONE=2600, WATER_STONE=2200,
    LEAF_STONE=2000, HP_UP=8500, PROTEIN=9000, IRON=8800, CARBOS=9200, CALCIUM=9500, RARE_CANDY=5500,
    X_ACCURACY=800, NUGGET=8000, ITEM_32=9000, POKE_DOLL=900, FULL_HEAL=700, REVIVE=1800, MAX_REVIVE=3500,
    GUARD_SPEC=600, SUPER_REPEL=450, MAX_REPEL=650, DIRE_HIT=600, COIN=20, FRESH_WATER=150, SODA_POP=250,
    LEMONADE=400, X_ATTACK=450, X_DEFEND=400, X_SPEED=500, X_SPECIAL=450,
)


def gen_prices(tree, mt):
    rel = "data/items/prices.asm"
    s = read(tree, rel)
    n = [0, 0]

    def fix(m):
        old, name = int(m.group(1)), m.group(2)
        v = 0 if old == 0 else PRICES.get(name, int(round(old * 0.85 / 50) * 50) or 50)
        n[0] += old != 0
        n[1] += old != 0 and v != old
        return f"bcd3 {v:<5} ; {name}"
    s = re.sub(r"bcd3 (\d+)\s*; (\w+)", fix, s)
    write(tree, rel, s)
    stat("prices.asm (priced items)", *n)
    rel = "data/items/tm_prices.asm"
    if os.path.exists(os.path.join(tree, rel)):
        tms = re.findall(r"^\tadd_tm (\w+)", read(tree, "constants/item_constants.asm"), re.M)
        s = read(tree, rel)
        n = [0, 0]

        def tm(m):
            i, old = int(m.group(2)) - 1, int(m.group(1))
            eff, pw, ty = mt.get(tms[i], ("", 0, ""))
            v = 6 if eff == "OHKO_EFFECT" else 2 if pw == 0 else int(np.clip(1 + round(pw / 30), 1, 9))
            n[0] += 1
            n[1] += v != old
            return f"nybble {v} ; TM{m.group(2)}"
        s = re.sub(r"nybble (\d+) ; TM(\d+)", tm, s)
        write(tree, rel, s)
        stat("tm_prices.asm", *n)


# ------------------------------------------------------------------ 6. palettes

LIGHT, DARK = (31, 30, 27), (2, 3, 4)
WATER = (18, 25, 30)
TOWN = dict(ROUTE=(18, 27, 12), PALLET=(27, 28, 19), VIRIDIAN=(19, 23, 15), PEWTER=(22, 22, 19),
            CERULEAN=(14, 22, 29), LAVENDER=(24, 19, 28), VERMILION=(29, 21, 8), CELADON=(30, 22, 26),
            FUCHSIA=(15, 25, 19), CINNABAR=(29, 13, 7), INDIGO=(20, 21, 29), SAFFRON=(29, 25, 10))
# names: LARKFIELD wheat, GREYWICK moss-grey, FLINTON flint, BRINEFORD brine, HOLLOWAY dusk violet,
# PORTSALT harbour rust, BLOSSBURY blossom, MARSHGATE marsh teal, EMBERKEY ember, SUMMIT RISE snow, SPIREHOLM gold
SGB = {
    "TOWNMAP": [LIGHT, WATER, (18, 25, 11), DARK],
    ("LOGO1", "RED"): [LIGHT, (31, 26, 14), (30, 15, 6), (18, 4, 6)],
    ("LOGO1", "BLUE"): [LIGHT, (28, 26, 31), (12, 10, 24), (6, 4, 14)],
    "LOGO2": [LIGHT, (30, 28, 18), (17, 18, 26), (6, 6, 15)],
    "0F": [LIGHT, (23, 22, 30), (12, 19, 29), DARK],
    "MEWMON": [LIGHT, (30, 23, 19), (15, 15, 22), DARK], "BLUEMON": [LIGHT, (17, 21, 30), (8, 12, 24), DARK],
    "REDMON": [LIGHT, (31, 19, 12), (25, 7, 5), DARK], "CYANMON": [LIGHT, (19, 27, 29), (9, 18, 24), DARK],
    "PURPLEMON": [LIGHT, (26, 20, 29), (17, 11, 23), DARK], "BROWNMON": [LIGHT, (27, 21, 14), (18, 12, 7), DARK],
    "GREENMON": [LIGHT, (19, 28, 14), (7, 18, 9), DARK], "PINKMON": [LIGHT, (31, 21, 25), (26, 12, 19), DARK],
    "YELLOWMON": [LIGHT, (31, 29, 12), (25, 19, 2), DARK], "GRAYMON": [LIGHT, (24, 23, 23), (13, 13, 16), DARK],
    "SLOTS1": [LIGHT, (25, 22, 21), (28, 19, 5), DARK],
    ("SLOTS2", "RED"): [LIGHT, (31, 30, 15), (27, 15, 19), DARK],
    ("SLOTS3", "RED"): [LIGHT, (20, 30, 15), (27, 15, 19), DARK],
    ("SLOTS4", "RED"): [LIGHT, (15, 18, 30), (27, 15, 19), DARK],
    ("SLOTS2", "BLUE"): [LIGHT, (31, 30, 15), (15, 18, 30), DARK],
    ("SLOTS3", "BLUE"): [LIGHT, (20, 30, 15), (15, 18, 30), DARK],
    ("SLOTS4", "BLUE"): [LIGHT, (27, 15, 19), (15, 18, 30), DARK],
    "BLACK": [LIGHT, (6, 6, 6), (2, 2, 3), DARK],
    "GREENBAR": [LIGHT, (31, 28, 17), (8, 22, 10), DARK], "YELLOWBAR": [LIGHT, (31, 28, 17), (27, 21, 2), DARK],
    "REDBAR": [LIGHT, (31, 28, 17), (27, 8, 5), DARK], "BADGE": [LIGHT, (30, 24, 16), (10, 14, 24), DARK],
    "CAVE": [LIGHT, (22, 16, 10), (17, 23, 21), DARK], "GAMEFREAK": [LIGHT, (31, 27, 15), (23, 19, 11), DARK],
}
for _t, _c in TOWN.items():
    SGB[_t] = [LIGHT, _c, WATER, DARK]

TYPE_PAL = dict(EMBER="REDMON", TIDE="BLUEMON", FROST="CYANMON", GALE="CYANMON", LEAF="GREENMON",
                VOLT="YELLOWMON", HIVE="YELLOWMON", VENOM="PURPLEMON", SHADE="GRAYMON", MIND="PINKMON",
                SOIL="BROWNMON", STONE="GRAYMON", WYRM="BLUEMON", PLAIN="BROWNMON", BRAWL="BROWNMON")
WORD_PAL = [(("lab", "ancestral"), "MEWMON"), (("blue", "storm", "cloud"), "BLUEMON"),
            (("teal", "ice", "frost", "snow", "icicle"), "CYANMON"), (("lilac", "violet", "night", "dream"), "PURPLEMON"),
            (("coral", "pink", "bell"), "PINKMON"), (("amber", "gold", "coin", "lantern", "spark"), "YELLOWMON"),
            (("moss", "vine", "reed", "mushroom", "turnip"), "GREENMON"), (("slate", "grey", "iron", "mirror"), "GRAYMON"),
            (("fire", "flame", "coal", "lava", "blaz", "burn"), "REDMON"), (("sand", "dune", "wombat", "gourd"), "BROWNMON")]


def rgb(c):
    return ",".join(f"{v:02d}" for v in c)


def gen_palettes(tree, dex):
    rel = "data/sgb/sgb_palettes.asm"
    s = read(tree, rel)
    ver, out, n = None, [], [0, 0]
    for ln in s.split("\n"):
        if ln.startswith("IF DEF(_RED)"):
            ver = "RED"
        elif ln.startswith("IF DEF(_BLUE)"):
            ver = "BLUE"
        elif ln.startswith("ENDC"):
            ver = None
        m = re.match(r"^\tRGB (.*) ; PAL_(\w+)$", ln)
        if m:
            cols = SGB.get((m.group(2), ver)) or SGB[m.group(2)]
            new = f"\tRGB {', '.join(rgb(c) for c in cols)} ; PAL_{m.group(2)}"
            n[0] += 1
            n[1] += re.sub(r"\s", "", new) != re.sub(r"\s", "", ln)
            ln = new
        out.append(ln)
    write(tree, rel, "\n".join(out))
    stat("sgb_palettes.asm", *n)
    rel = "data/pokemon/palettes.asm"
    s = read(tree, rel)
    n = [0, 0]

    def mon(m):
        old, name = m.group(1), m.group(2)
        if name not in dex.spec:
            return m.group(0)
        nm, t1, t2, plan, concept = dex.spec[name]
        pal = None
        for words, p in WORD_PAL:
            if any(w in concept.lower() for w in words):
                pal = p
                break
        pal = "PAL_" + (pal or TYPE_PAL[t1])
        n[0] += 1
        n[1] += pal != old
        return f"db {pal:<13} ; {name}"
    s = re.sub(r"db (PAL_\w+)\s*; (\w+)", mon, s)
    write(tree, rel, s)
    stat("pokemon/palettes.asm", *n)


# ------------------------------------------------------------------ 7. SGB border colours

def gen_border(tree):
    rel = "data/sgb/sgb_border.asm"
    s = read(tree, rel)
    # DAWN: sunrise ramps (peach, rose, gold); DUSK: twilight ramps (indigo, teal, violet)
    hues = {"RED": [0.07, 0.95, 0.12], "BLUE": [0.66, 0.50, 0.76]}
    ver, pal, k, out, n = None, -1, 0, [], [0, 0]
    for ln in s.split("\n"):
        if ln.startswith("IF DEF(_RED)"):
            ver = "RED"
        elif ln.startswith("IF DEF(_BLUE)"):
            ver = "BLUE"
        elif ln.startswith("ENDC"):
            ver = None
        m = re.match(r"^\tRGB (\d+),(\d+),(\d+)(.*)$", ln)
        if m and ver:
            if "PAL_SGB" in m.group(4):
                pal, k = int(re.search(r"PAL_SGB(\d)", m.group(4)).group(1)) - 1, 0
            h = hues[ver][pal % 3]
            v = [0.97, 0.78, 0.55, 0.30][k]
            sat = [0.10, 0.35, 0.55, 0.60][k]
            c = tuple(int(round(x * 31)) for x in colorsys.hsv_to_rgb(h, sat, v))
            new = f"\tRGB {c[0]},{c[1]},{c[2]}{m.group(4)}"
            n[0] += 1
            n[1] += new != ln
            ln, k = new, k + 1
        out.append(ln)
    write(tree, rel, "\n".join(out))
    stat("sgb_border.asm (colours)", *n)


# ------------------------------------------------------------------ 8. slot machine reels

SYMS = ["SLOTS7", "SLOTSBAR", "SLOTSCHERRY", "SLOTSFISH", "SLOTSBIRD", "SLOTSMOUSE"]


def gen_slots(tree):
    rel = "data/events/slot_machine_wheels.asm"
    s = read(tree, rel)
    blocks = re.split(r"(?m)^(?=SlotMachineWheel\d:)", s)
    out, n = [], [0, 0]
    for b in blocks:
        m = re.match(r"(SlotMachineWheel(\d):\n)((?:\tdw \w+\n)+)(.*)", b, re.S)
        if not m:
            out.append(b)
            continue
        old = re.findall(r"dw (\w+)", m.group(3))
        L = len(old)
        uniq = L - 3  # the last three repeat the first three so the reel wraps on screen
        old_counts = [old[:uniq].count(x) for x in SYMS]
        rng = R("reel", m.group(2))
        while True:
            # 7 and BAR stay scarce, fruit-like symbols fill the rest; at least one of each
            c = [int(rng.integers(1, 3)), int(rng.integers(1, 4))]
            rest = uniq - sum(c) - 4
            w = rng.dirichlet([3, 2, 2, 2])
            extra = np.floor(w * rest).astype(int)
            extra[int(np.argmax(w))] += rest - extra.sum()
            c += [1 + int(e) for e in extra]
            if c != old_counts:
                break
        bag = [x for x, k in zip(SYMS, c) for _ in range(k)]
        for _ in range(200):
            rng.shuffle(bag)
            if all(bag[i] != bag[(i + 1) % uniq] for i in range(uniq)):
                break
        reel = bag + bag[:3]
        n[0] += L
        n[1] += sum(a != b for a, b in zip(reel, old))
        out.append(m.group(1) + "".join(f"\tdw {x}\n" for x in reel) + m.group(4))
    write(tree, rel, "".join(out))
    stat("slot_machine_wheels.asm (reel cells)", *n)


# ------------------------------------------------------------------ main

def main(tree):
    dex = Dex(tree)
    mt = move_table(tree)
    gen_parties(tree, dex)
    gen_special(tree)
    gen_wild(tree, dex)
    gen_types(tree)
    gen_prices(tree, mt)
    gen_palettes(tree, dex)
    gen_border(tree)
    gen_slots(tree)
    print("tables_gen summary (entries, changed):")
    for k, (a, b) in STATS.items():
        print(f"  {k:<40} {a:5d}  {b:5d}  {100 * b / max(1, a):5.1f}%")


if __name__ == "__main__":
    main(sys.argv[1])
