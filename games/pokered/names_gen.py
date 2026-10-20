"""Name tables of KITHBOUND -> games/pokered/text/new/00_names.json.

Reads only the clean tree's code (constants, labels, list order) to know which
slot holds which name; the names themselves come from world.py.

    python -m games.pokered.names_gen <tree>
"""
import json
import os
import re
import sys

from games.pokered import textx, world


def consts(tree, rel, prefix="const"):
    """const list with const_skip / const_def gaps -> [name or None] from index 0."""
    out = []
    for line in open(os.path.join(tree, rel), encoding="utf8"):
        line = line.split(";")[0].strip()
        m = re.match(r"(?:trainer_)?const\s+([A-Z0-9_]+)", line)
        if m:
            out.append(m.group(1))
        elif line.startswith("const_skip"):
            n = re.findall(r"\d+", line)
            out += [None] * (int(n[0]) if n else 1)
    return out


def main(argv):
    tree = argv[1]
    slots = textx.scan(tree)
    by = {}
    for s in slots:
        by.setdefault((s["file"], s["id"].split("|")[1]), []).append(s)
    new = {}

    def put_list(rel, label, names):
        ss = by[(rel, label)]
        for s in ss:
            n = int(s["id"].rsplit("|", 1)[1])
            if n < len(names) and names[n] is not None:
                new[s["id"]] = names[n]

    # creatures, in internal index order (dname list position = index - 1)
    spec = world.species_by_const(tree)
    internal = consts(tree, "constants/pokemon_constants.asm")[1:]
    put_list("data/pokemon/names.asm", "MonsterNames",
             [spec[c][0] if c in spec else "NOBODY" for c in internal])
    # NIDORAN_M / NIDORAN_F appear in the dex list with that spelling too
    moves = [c for c in consts(tree, "constants/move_constants.asm")[1:]]
    put_list("data/moves/names.asm", "MoveNames", [world.MOVES.get(c) for c in moves])
    items = consts(tree, "constants/item_constants.asm")[1:]
    put_list("data/items/names.asm", "ItemNames", [world.ITEMS.get(c) for c in items])
    tc = consts(tree, "constants/trainer_constants.asm")[1:]
    put_list("data/trainers/names.asm", "TrainerNames", [world.TRAINER_CLASSES.get(c) for c in tc])
    # defeat-speech short names: label .XxxName -> class
    camel = {c.replace("_", "").lower(): v for c, v in world.TRAINER_CLASSES.items()}
    camel.update({"psychic": world.TRAINER_CLASSES["PSYCHIC_TR"], "jrtrainerm": "CADET♂",
                  "jrtrainerf": "CADET♀", "fisherman": "ANGLER", "pokemaniac": "KITH BUFF"})
    for (rel, label), ss in by.items():
        if rel == "data/trainers/name_pointers.asm":
            key = label.split(".")[-1][:-4].lower()
            if key in camel:
                new[ss[0]["id"]] = camel[key] + "@"
    tmap = {"." + k.title().replace("_", ""): v for k, v in world.TYPES.items()}
    tmap[".Psychic"] = world.TYPES["PSYCHIC_TYPE"]
    for (rel, label), ss in by.items():
        if rel == "data/types/names.asm":
            v = tmap.get("." + label.split(".")[-1])
            if v:
                new[ss[0]["id"]] = v + "@"
        if rel == "data/maps/names.asm" and label in world.MAP_NAMES:
            new[ss[0]["id"]] = world.MAP_NAMES[label] + "@"
    put_list("data/moves/field_move_names.asm", "FieldMoveNames",
             [world.MOVES[m] + "@" for m in ("CUT", "FLY")] + [None] +
             [world.MOVES[m] + "@" for m in ("SURF", "STRENGTH", "FLASH", "DIG", "TELEPORT", "SOFTBOILED")])
    # vitamins / stat mods
    put_list("data/battle/stat_names.asm", "VitaminStats", ["VIGOR", "BRAWN", "GUARD", "DASH", "WIT"])
    put_list("data/battle/stat_mod_names.asm", "StatModTextStrings",
             ["BRAWN", "GUARD", "DASH", "WIT", "AIM", "DODGE"])
    # badges (Route 23 guards) and gym buffers
    for (rel, label), ss in by.items():
        m = re.match(r"(\w+)BadgeText$", label)
        if rel == "scripts/Route23.asm" and m and m.group(1).upper() in world.BADGES:
            new[ss[0]["id"]] = world.BADGES[m.group(1).upper()] + "BADGE@"
    gyms = {"Pewter": ("FLINTON", "CRAG"), "Cerulean": ("BRINEFORD", "MAREN"),
            "Vermilion": ("PORTSALT", "MAJ.VOLTA"), "Celadon": ("BLOSSBURY", "FLORA"),
            "Fuchsia": ("MARSHGATE", "HEMLOCK"), "Saffron": ("SPIREHOLM", "SIBYL"),
            "Cinnabar": ("EMBERKEY", "ASHBY"), "Viridian": ("GREYWICK", "VANCE")}
    for (rel, label), ss in by.items():
        m = re.match(r"scripts/(\w+)Gym\.asm$", rel)
        if m and m.group(1) in gyms:
            if label.endswith(".CityName"):
                new[ss[0]["id"]] = gyms[m.group(1)][0] + "@"
            elif label.endswith(".LeaderName"):
                new[ss[0]["id"]] = gyms[m.group(1)][1] + "@"
    pl = world.PEOPLE["player (default names, DAWN)"]
    rv = world.PEOPLE["rival (default names, DAWN)"]
    put_list("constants/player_constants.asm", "_top", pl + rv + rv + pl)
    # engine words printed by text tokens
    fixed = {
        "home/text.asm|PlacePOKeText|0": "KITH@", "home/text.asm|TrainerCharText|0": "TAMER@",
        "home/text.asm|RocketCharText|0": "GLOAM@", "home/text.asm|TMCharText|0": "SC@",
        "home/text.asm|PCCharText|0": "PC@", "home/text.asm|EnemyText|0": "Foe @",
        "home/names.asm|TechnicalPrefix|0": "SC", "home/names.asm|HiddenPrefix|0": "KS",
    }
    new.update({k: v for k, v in fixed.items() if any(s["id"] == k for s in slots)})
    nick = ["PIPSQUEAK", "MARLOWE", "BUZZY", "SKIPPER", "DOODLE", "WHISKERS", "BOBBIN", "SPROCKET",
            "TWIGGY", "CORAL"]
    put_list("data/events/trades.asm", "_top", nick) if ("data/events/trades.asm", "_top") in by else None
    for (rel, label), ss in by.items():
        if rel == "data/events/trades.asm":
            for i, s in enumerate(ss):
                new[s["id"]] = nick[i % len(nick)]
        if rel == "data/text/unused_names.asm":
            for i, s in enumerate(ss):
                new[s["id"]] = (("NIL" + str(i))[:s["budget"]] + "@") if s["text"].endswith("@")                     else ("NIL" + str(i)).ljust(s["budget"])[:s["budget"]]
    out = os.path.join(textx.NEW, "00_names.json")
    os.makedirs(textx.NEW, exist_ok=True)
    bad = [(k, textx.validate(next(s for s in slots if s["id"] == k), v)) for k, v in new.items()]
    bad = [b for b in bad if b[1]]
    json.dump(dict(sorted(new.items())), open(out, "w", encoding="utf8"), ensure_ascii=False, indent=0)
    print(f"names: {len(new)} slots -> {out}; {len(bad)} invalid")
    for k, e in bad[:12]:
        print("  BAD", k, e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
