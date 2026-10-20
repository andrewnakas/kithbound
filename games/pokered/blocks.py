"""Blocksets of KITHBOUND: our own block -> tile tables (games/pokered/blocks/<file>.json).

Each block id keeps its ROLE (spec/blockroles.json, dirty-room facts: per block the
walk/solid pattern of its four collision steps and which special tile class sits on
each step: door, warp, water, grass, ledge, counter, cut tree), so maps, anchors and
the engine's block swaps still work. The 16 tiles are composed anew.

    python -m games.pokered.blocks roles <pristine>                (dirty: spec/blockroles.json)
    python -m games.pokered.blocks show <file> <tree> <out.png>    (sheet: role tags | old | new, with clean tiles)
    python -m games.pokered.blocks check [file]                    (rules + similarity, one screen)
    python -m games.pokered.blocks write <tree>                    (gfx/blocksets/*.bst from the JSONs)

JSON: {"blocks": [[16 tile ids] ...]} in block order, same count as the role list.
Rules: each collision step tile (index 4, 6, 12, 14 = bottom-left of each 16x16 step)
must keep its class (walk/solid + special class); the block must not equal the old
composition and may share at most 8 of 16 tiles in place with it, unless the role is
uniform (all 16 tiles one tile, e.g. water, tall grass, plain floor).
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BLK = os.path.join(HERE, "blocks")
ROLES = os.path.join(HERE, "spec", "blockroles.json")
STEP = [4, 6, 12, 14]          # bottom-left tile of each 16x16 step: decides collision
WATER = {0x14, 0x32, 0x48}


def classes(kit, ts):
    """tile id -> class name for a tileset (from the engine's data tables)."""
    t = kit.tilesets[ts]
    s = kit.read("data/tilesets/ledge_tiles.asm")
    ledges = {int(x, 16) for x in re.findall(r"\$[0-9A-Fa-f]+,\s*\$([0-9A-Fa-f]+),", s)} if ts == "OVERWORLD" else set()

    def cls(tile):
        parts = ["walk" if tile in t.coll else "solid"]
        if tile in t.doors:
            parts.append("door")
        if tile in t.warps:
            parts.append("warp")
        if t.water and tile in WATER:
            parts.append("water")
        if tile == t.grass:
            parts.append("grass")
        if tile in ledges:
            parts.append("ledge")
        if tile in t.counters:
            parts.append("counter")
        return "+".join(parts)
    return cls


def files_of(kit):
    """blockset file -> one tileset const that uses it (classes are per tileset; shared files must agree)."""
    out = {}
    for const, t in kit.tilesets.items():
        out.setdefault(os.path.basename(t.block_file)[:-4], []).append(const)
    return out


def roles(pristine):
    from games.pokered.maps_kit import Kit
    kit = Kit(pristine)
    out = {}
    for f, consts in files_of(kit).items():
        t = kit.tilesets[consts[0]]
        cl = {c: classes(kit, c) for c in consts}
        rows = []
        for b in t.blocks:
            rows.append({"steps": [[cl[c](int(b[i])) for c in consts] for i in STEP],
                         "uniform": bool(len(set(int(x) for x in b)) == 1)})
        out[f] = {"tilesets": consts, "count": len(t.blocks), "blocks": rows}
    json.dump(out, open(ROLES, "w"), indent=0)
    print(f"block roles: {len(out)} blocksets, {sum(v['count'] for v in out.values())} blocks -> {ROLES}")


def load_new(f):
    p = os.path.join(BLK, f + ".json")
    return json.load(open(p))["blocks"] if os.path.exists(p) else None


def check(pristine, only=None, quiet=False):
    from games.pokered.maps_kit import Kit
    kit = Kit(pristine)
    R = json.load(open(ROLES))
    bad_total, report = 0, []
    for f, r in sorted(R.items()):
        if only and f != only:
            continue
        new = load_new(f)
        old = kit.tilesets[r["tilesets"][0]].blocks
        if new is None:
            report.append((f, "missing", r["count"]))
            bad_total += 1
            continue
        cl = {c: classes(kit, c) for c in r["tilesets"]}
        probs, same, nonuni = [], 0, 0
        if len(new) != r["count"]:
            probs.append(f"{len(new)} blocks, need {r['count']}")
        for i, (nb, role) in enumerate(zip(new, r["blocks"])):
            if len(nb) != 16:
                probs.append(f"block {i}: {len(nb)} tiles")
                continue
            for k, si in enumerate(STEP):
                got = [cl[c](int(nb[si])) for c in r["tilesets"]]
                if got != role["steps"][k]:
                    probs.append(f"block {i:02X} step {k}: {got[0]} != {role['steps'][k][0]}")
                    break
            if role["uniform"]:
                continue
            nonuni += 1
            eq = sum(int(a) == int(b) for a, b in zip(nb, old[i]))
            if eq == 16:
                same += 1
                probs.append(f"block {i:02X}: identical to the old one")
            elif eq > 8:
                probs.append(f"block {i:02X}: {eq}/16 tiles in place like the old one")
        report.append((f, probs, nonuni))
        bad_total += bool(probs)
    if not quiet:
        print(f"blocks: {len(report)} blocksets, {bad_total} with problems")
        for f, p, n in report:
            if p == "missing":
                print(f"  {f}: missing ({n} blocks)")
            elif p:
                print(f"  {f}: {len(p)} problems: " + "; ".join(p[:4]))
    return bad_total


def show(f, tree, out):
    """sheet: per block: id, usage tags, old composition, new composition (clean tiles)."""
    from PIL import Image, ImageDraw
    from games.pokered.maps_kit import Kit
    from games.pokered.maps_view import tileset_png
    kit = Kit(tree)
    R = json.load(open(ROLES))[f]
    t = kit.tilesets[R["tilesets"][0]]
    pic = tileset_png(kit, tree, R["tilesets"][0])
    tw = pic.shape[1] // 8
    pr = os.environ.get("POKERED_PRISTINE", "D:/n64work/pokered/pristine")
    old = np.frombuffer(open(os.path.join(pr, t.block_file), "rb").read(), np.uint8).reshape(-1, 16)
    new = load_new(f)

    def draw(b):
        a = np.full((32, 32), 255, np.uint8)
        for i, tile in enumerate(b):
            ty, tx = divmod(int(tile), tw)
            if ty * 8 + 8 <= pic.shape[0]:
                a[(i // 4) * 8:(i // 4) * 8 + 8, (i % 4) * 8:(i % 4) * 8 + 8] = pic[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8]
        return Image.fromarray(a).resize((64, 64), Image.NEAREST)
    cols = 6
    n = len(old)
    W, H = cols * 150, ((n + cols - 1) // cols) * 84
    sheet = Image.new("RGB", (W, H), (40, 44, 60))
    d = ImageDraw.Draw(sheet)
    for i in range(n):
        x, y = (i % cols) * 150, (i // cols) * 84
        d.text((x + 2, y + 1), f"{i:02X} " + ",".join(sorted({s[0].replace('walk', 'w').replace('solid', 's')
                                                               for s in R['blocks'][i]['steps']})), fill=(255, 230, 120))
        sheet.paste(draw(old[i]), (x + 2, y + 16))
        if new is not None and i < len(new):
            sheet.paste(draw(new[i]), (x + 72, y + 16))
    sheet.save(out)
    print("sheet ->", out)


def write(tree):
    from games.pokered.maps_kit import Kit
    kit = Kit(tree)
    n = 0
    for f, consts in files_of(kit).items():
        new = load_new(f)
        if new is None:
            continue
        p = os.path.join(tree, kit.tilesets[consts[0]].block_file)
        open(p, "wb").write(bytes(int(x) for b in new for x in b))
        n += 1
    print(f"blocks: wrote {n} blocksets")


if __name__ == "__main__":
    a = sys.argv
    pr = os.environ.get("POKERED_PRISTINE", "D:/n64work/pokered/pristine")
    if a[1] == "roles":
        roles(a[2])
    elif a[1] == "show":
        show(a[2], a[3], a[4])
    elif a[1] == "check":
        sys.exit(1 if check(pr, a[2] if len(a) > 2 else None) else 0)
    elif a[1] == "write":
        write(a[2])
