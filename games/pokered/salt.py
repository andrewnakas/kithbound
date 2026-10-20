"""Merge the taint scan's list of chance collisions (picture + tile numbers only) into
salts.json; the generator then marks those tiles differently.

    python -m cleanroom.gb.taint <dirty> <clean> <spec> --png --out fails.json
    python -m games.pokered.salt fails.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(path):
    fails = json.load(open(path))
    p = os.path.join(HERE, "salts.json")
    salts = json.load(open(p)) if os.path.exists(p) else {}
    n = 0
    for rel, tiles in fails.items():
        for t in tiles:
            d = salts.setdefault(rel, {})
            d[str(t)] = d.get(str(t), 0) + 1
            n += 1
    json.dump(salts, open(p, "w"), indent=0, sort_keys=True)
    print(f"salts: {n} tiles bumped, {sum(len(v) for v in salts.values())} salted in {len(salts)} pictures")


if __name__ == "__main__":
    main(sys.argv[1])
