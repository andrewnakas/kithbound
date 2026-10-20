"""DIRTY ROOM (rejection only): per map, try seeds until the new layout (1) passes the
map bot (every target reachable, no region split without field moves), (2) logs no
generator problem and (3) stays clearly unlike the retail grid (blockmap gate with a
margin). Writes spec/map_seeds.json ({label: seed}).

    python -m games.pokered.map_seeds <pristine tree> <scratch clean tree with our blocksets>
"""
import json
import os
import sys

import numpy as np

from cleanroom.originality import blockmap
from cleanroom.originality.config import merged
from games.pokered import mapbot, maps_gen
from games.pokered.maps_kit import Kit


def main(argv):
    pristine, tree = argv[1], argv[2]
    kit = Kit(tree)
    spec = json.load(open(os.path.join(maps_gen.HERE, "spec/maps.json")))
    voc = maps_gen.vocab(kit, spec)
    ledges = mapbot.ledge_table(kit)
    cfg = dict(merged()["blockmap"])
    cfg["equal_max"] *= 0.8
    bp = os.path.join(os.environ.get("POKERED_ORIG", "D:/n64work/pokered/orig"), "mapbot_retail.json")
    base = json.load(open(bp)) if os.path.exists(bp) else {}
    seeds, worst, done = {}, [], set()
    for label, m in sorted(spec["maps"].items()):
        if m["blk"] in done:
            continue
        done.add(m["blk"])
        w, h = m["w"], m["h"]
        path = os.path.join(tree, m["blk"])
        size = os.path.getsize(path)
        r = np.frombuffer(open(os.path.join(pristine, m["blk"]), "rb").read(), np.uint8)[:w * h]
        r = np.pad(r, (0, w * h - len(r))).reshape(h, w)
        anch = [[int(a) for a in k.split(",")] for k in m["anchors"]]
        best = None
        for seed in range(30):
            blk, probs = maps_gen.build_one(label, m, voc, seed)
            open(path, "r+b").write(blk.tobytes()[:size])
            mp = kit.maps[label]
            bad = mapbot.check_map(kit, mp, m, ledges)[1] + mapbot.check_map(kit, mp, m, ledges, moves=False)[1]
            skip = {tuple(p) if isinstance(p, list) else p for p in base.get(label, [])}
            bad = [p for p in bad if (tuple(p) if isinstance(p, list) else p) not in skip]
            res = blockmap.compare(r, blk, anch, cfg)
            key = (len(bad), res["fail"], len(probs), res["score"])
            if best is None or key < best[0]:
                best = (key, seed, blk)
            if not bad and not res["fail"] and not probs:
                break
        open(path, "r+b").write(best[2].tobytes()[:size])
        if best[1]:
            seeds[label] = best[1]
        worst.append((best[0], label))
    json.dump(seeds, open(os.path.join(maps_gen.HERE, "spec/map_seeds.json"), "w"), indent=0)
    worst.sort(reverse=True)
    left = [(k, l) for k, l in worst if k[0] or k[1] or k[2]]
    print(f"map seeds: {len(seeds)} maps re-seeded; {len(left)} maps still imperfect: {left[:8]}")


if __name__ == "__main__":
    main(sys.argv)
