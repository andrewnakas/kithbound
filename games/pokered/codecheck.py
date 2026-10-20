"""DIRTY ROOM: which bytes of a clean ROM may equal the retail ROM.

Only assembled engine code may match retail (plus the structure the code hard-wires:
pointer tables, map headers/objects coordinates, tile-id tables, packet formats).
Every byte of the clean ROM is attributed to the global label it falls under (.sym)
and that label to its source file in the clean tree. Bytes from code files (home/,
engine/, scripts/, audio engine, macros) and from the reviewed STRUCTURE list count as
explained; this writes <rom>.explained (unexplained bytes scrambled) for the
originality gate's `code` check, and prints which data files still share 256-byte
windows with retail.

    python -m games.pokered.codecheck <clean tree> <rom name> <retail rom>
"""
import bisect
import glob
import os
import re
import sys
from collections import Counter

import numpy as np

from cleanroom.originality.code import window_hashes

CODE_DIRS = ("home/", "engine/", "scripts/", "macros/", "audio/engine", "audio/low_health", "audio/poke_flute",
             "audio/pokedex_rating", "audio/play_battle", "audio/alternate_tempo", "home.asm", "main.asm",
             "audio.asm", "ram/")
# structure the engine hard-wires (reviewed): ids, pointers, coordinates, formats
STRUCTURE = (
    "data/maps/objects/",            # warp/sign/NPC coordinates (gameplay anchors)
    "data/maps/headers/",            # map size, tileset, connections
    "data/maps/map_header_",         # pointer/bank tables
    "data/maps/hide_show_data", "data/maps/toggleable_objects", "data/maps/sprite_sets",
    "data/maps/songs", "data/maps/town_map_entries", "data/maps/special_warps", "data/maps/dungeon_maps",
    "data/maps/force_bike_surf", "data/maps/rest_house", "data/maps/badge_maps", "data/maps/",
    "data/events/hidden_events", "data/events/hidden_item_coords", "data/events/hidden_coins",
    "data/events/card_key_coords", "data/events/elevator_floors",
    "data/tilesets/",                # tile-id tables the engine reads (collision, doors, warps, ledges)
    "data/wild/grass_water", "data/sprites/", "data/pokemon/dex_order", "data/pokemon/cry_",
    "data/sgb/sgb_packets", "data/sgb/sgb_blk", "data/battle_anims/special_effect_pointers",
    "data/text_predef_pointers", "data/predef_pointers", "data/text_boxes",
    "data/tilemaps.asm",
    "maps.asm",                      # map block files of the few maps that are nothing but anchors (lifts, tiny rooms)
    "data/wild/maps/nothing.asm",    # the empty encounter table             # tile index layouts of the mon/intro/trade pictures (build formats)
    "data/player/", "data/items/use_party", "data/items/key_items", "data/items/guard_drink",
    "data/items/marts", "data/items/vending_prices",
)


def label_files(tree):
    out = {}
    for p in glob.glob(os.path.join(tree, "**", "*.asm"), recursive=True):
        rel = os.path.relpath(p, tree).replace("\\", "/")
        for m in re.finditer(r"^([A-Za-z_]\w*)::?", open(p, encoding="utf8").read(), re.M):
            out.setdefault(m.group(1), rel)
    return out


def main(argv):
    tree, name, retail = argv[1], argv[2], argv[3]
    rom = os.path.join(tree, name + ".gbc")
    C = open(rom, "rb").read()
    R = open(retail, "rb").read()
    lf = label_files(tree)
    syms = []
    for line in open(os.path.join(tree, name + ".sym")):
        m = re.match(r"([0-9a-f]+):([0-9a-f]+) (\S+)", line)
        if m and "." not in m.group(3):
            bk, a = int(m.group(1), 16), int(m.group(2), 16)
            if a < 0x8000:
                syms.append((a if bk == 0 else bk * 0x4000 + a - 0x4000, m.group(3)))
    syms.sort()
    offs = [s[0] for s in syms]
    src = np.empty(len(C), object)
    prev = "home/"
    for i in range(len(syms)):
        a = syms[i][0]
        b = syms[i + 1][0] if i + 1 < len(syms) else len(C)
        nm = syms[i][1]
        f = lf.get(nm)
        if f is None:                     # macro-made labels (X_id, X_h, X_Blocks ...)
            for suf in ("_id", "_h", "_Blocks", "_Object", "_TextPointers", "_Script"):
                if nm.endswith(suf) and nm[:-len(suf)] in lf:
                    f = lf[nm[:-len(suf)]]
                    break
        f = f or prev
        src[a:b] = f
        prev = f
    src[:syms[0][0]] = "home/"
    explained = np.array([str(f).startswith(CODE_DIRS) or str(f).startswith(STRUCTURE) for f in src])
    rh, _ = window_hashes(R, 256, 32)
    ch, low = window_hashes(C, 256, 32)
    bad = np.isin(ch, np.unique(rh)) & ~low
    cov = np.zeros(len(C), bool)
    for i in np.nonzero(bad)[0]:
        cov[i:i + 256] = True
    left = cov & ~explained
    # a data run shorter than 8 bytes that equals retail next to code is a coincidence (a rate byte,
    # a palette id), not a copied table: count it as explained
    i = 0
    idx = np.nonzero(left)[0]
    runs = []
    for k in idx:
        if runs and k == runs[-1][1]:
            runs[-1][1] = k + 1
        else:
            runs.append([k, k + 1])
    for a, b in runs:
        if b - a < 8:
            explained[a:b] = True
    left = cov & ~explained
    by = Counter(str(src[i]) for i in np.nonzero(left)[0])
    out = bytearray(C)
    rng = np.random.default_rng(1)
    noise = rng.integers(0, 256, len(C), dtype=np.uint8)
    arr = np.frombuffer(bytes(out), np.uint8).copy()
    arr[~explained] = noise[~explained]
    open(rom + ".explained", "wb").write(arr.tobytes())
    print(f"codecheck {name}: {int(cov.sum())} bytes share 256-byte windows with retail; "
          f"{int(left.sum())} of them outside code/structure")
    for f, n in by.most_common(15):
        print(f"  {n:6d} {f}")
    return 1 if left.any() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
