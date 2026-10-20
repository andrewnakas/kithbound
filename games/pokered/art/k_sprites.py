"""KITHBOUND overworld sprites and small pictures, all our own designs.

People are built by k_sprites_lib (round-headed chibi kit, styled per engine name);
creatures and objects are hand-drawn in k_sprites_obj; the rest (fishing poses, icons,
trade, slots, badges, cursor, shadow ...) are drawn here. No retail outline is used.
"""
import os

import numpy as np

from games.pokered.art import drawer
from games.pokered.art import k_sprites_lib as L
from games.pokered.art import k_sprites_obj as O
from games.pokered.art import k_sprites_misc as M

# engine name -> (KITHBOUND role, style)
STYLES = {
    "red": ("ARLO, the player", dict(hair="beanie", hat_s=2, top_s=1, leg_s=2, extras=("pack", "belt"))),
    "blue": ("SILAS, the rival", dict(hair="fringe", hair_s=2, top_s=3, leg_s=2, bangs=(3, 4, 5, 6), extras=("collar",))),
    "oak": ("PROF.BRAMBLE", dict(hair="hat", hat_s=2, beard=True, beard_s=1, wear="coat", top_s=1, extras=("buttons",))),
    "mom": ("MOM", dict(hair="bun", hair_s=2, top_s=2, wear="skirt", leg_s=2, extras=("apron",))),
    "daisy": ("JUNE", dict(hair="pony", hair_s=3, wear="dress", top_s=1, skirt_s=2, bangs=(3, 12, 7))),
    "nurse": ("REST HOUSE keeper", dict(hair="band", hair_s=2, hat_s=1, wear="dress", top_s=1, skirt_s=1, extras=("cross",))),
    "clerk": ("SUPPLY clerk", dict(hair="cap", hat_s=3, top_s=2, leg_s=2, extras=("apron",))),
    "youngster": ("SCAMP", dict(hair="cap", hat_s=1, top_s=2, wear="shorts", leg_s=2, extras=("stripes",))),
    "girl": ("SCHOOLGIRL", dict(hair="twin", hair_s=3, top_s=1, wear="skirt", leg_s=2, extras=("collar",))),
    "little_girl": ("little girl", dict(kid=True, hair="twin", hair_s=2, wear="dress", top_s=1, skirt_s=1)),
    "little_boy": ("little boy", dict(kid=True, hair="spiky", hair_s=3, top_s=1, wear="shorts", leg_s=2)),
    "fisher": ("ANGLER", dict(hair="hat", hat_s=1, top_s=2, leg_s=3, extras=("vest", "rod"))),
    "fishing_guru": ("old angler", dict(hair="bald", fringe_s=1, beard=True, beard_s=1, top_s=2, leg_s=2, extras=("rod",))),
    "rocket": ("GLOAM agent", dict(hair="hood", hood_s=3, hair_s=3, mask=True, mask_s=2, top_s=3, leg_s=2, gloves=True, extras=("emblem",))),
    "giovanni": ("VANCE", dict(hair="short", hair_s=3, bangs=(3, 4, 11, 12), wear="coat", top_s=2, extras=("tie",))),
    "gambler": ("GAMESTER", dict(hair="hat", hat_s=3, top_s=1, leg_s=2, mustache=True, extras=("vest",))),
    "cook": ("cook", dict(hair="chef", hair_s=3, top_s=1, leg_s=2, extras=("buttons",))),
    "scientist": ("RESEARCHER", dict(hair="short", hair_s=2, glasses=True, wear="coat", top_s=1, extras=("tie",))),
    "sailor": ("DECKHAND", dict(hair="bandana", hat_s=1, hair_s=3, top_s=1, leg_s=2, extras=("stripes",))),
    "biker": ("ROADHOG", dict(hair="helmet", hat_s=3, top_s=3, leg_s=2, gloves=True, goggles=True)),
    "hiker": ("TREKKER", dict(hair="band", hair_s=3, hat_s=1, beard=True, beard_s=3, top_s=2, leg_s=2, extras=("bag",))),
    "super_nerd": ("TECHIE", dict(hair="spiky", hair_s=2, glasses=True, top_s=1, leg_s=2, extras=("bag",))),
    "gentleman": ("SQUIRE", dict(hair="tophat", hat_s=3, hair_s=2, mustache=True, wear="coat", top_s=2, extras=("cane",))),
    "beauty": ("STARLET", dict(hair="long", hair_s=3, wear="dress", top_s=2, skirt_s=1, blush=True)),
    "brunette_girl": ("girl", dict(hair="pony", hair_s=2, top_s=1, wear="skirt", leg_s=3, bangs=(3, 12, 6))),
    "cooltrainer_m": ("VETERAN", dict(hair="spiky", hair_s=3, top_s=3, leg_s=2, extras=("collar", "belt"))),
    "cooltrainer_f": ("VETERAN", dict(hair="long", hair_s=2, top_s=3, wear="skirt", leg_s=2)),
    "channeler": ("MEDIUM", dict(hair="hood", hood_s=1, hair_s=1, wear="robe", top_s=1, extras=("staff",))),
    "agatha": ("MOIRA", dict(hair="bun", hair_s=1, wear="robe", top_s=3, extras=("cane",))),
    "bruno": ("TORVALD", dict(hair="bandana", hat_s=1, hair_s=3, top_s=1, leg_s=3, extras=("belt",))),
    "koga": ("HEMLOCK", dict(hair="band", hair_s=3, hat_s=2, mask=True, top_s=2, leg_s=3, extras=("scarf",), scarf_s=1)),
    "lance": ("ORRIN", dict(hair="spiky", hair_s=3, top_s=2, leg_s=2, extras=("cape",), cape_s=3)),
    "lorelei": ("NEVE", dict(hair="long", hair_s=2, glasses=True, wear="dress", top_s=1, skirt_s=2)),
    "mr_fuji": ("OLD HOLT", dict(hair="bald", fringe_s=1, beard=True, beard_s=1, wear="robe", top_s=2, extras=("cane",))),
    "gramps": ("old man", dict(hair="bald", fringe_s=2, mustache=True, top_s=2, leg_s=3, extras=("cane",))),
    "granny": ("old woman", dict(hair="bun", hair_s=1, top_s=2, wear="skirt", leg_s=3, extras=("cane",))),
    "balding_guy": ("bald man", dict(hair="bald", fringe_s=3, top_s=1, leg_s=2, extras=("belt",))),
    "middle_aged_man": ("man", dict(hair="short", hair_s=2, mustache=True, top_s=2, leg_s=3, extras=("tie",))),
    "middle_aged_woman": ("woman", dict(hair="bun", hair_s=3, wear="dress", top_s=2, skirt_s=2, extras=("bag",))),
    "bike_shop_clerk": ("cycle clerk", dict(hair="cap", hat_s=1, top_s=2, leg_s=3, extras=("apron",))),
    "captain": ("CAPTAIN", dict(hair="cap", hat_s=1, beard=True, beard_s=2, wear="coat", top_s=3, extras=("buttons",))),
    "gameboy_kid": ("kid with a handheld", dict(kid=True, hair="cap", hat_s=2, top_s=1, wear="shorts", leg_s=2, extras=("book",))),
    "guard": ("guard", dict(hair="helmet", hat_s=2, top_s=2, leg_s=3, extras=("belt", "whistle"))),
    "gym_guide": ("gym guide", dict(hair="band", hair_s=3, hat_s=1, top_s=1, leg_s=2, smile=True, extras=("buttons",))),
    "link_receptionist": ("link desk", dict(hair="bun", hair_s=3, top_s=2, wear="skirt", leg_s=2, extras=("collar",))),
    "safari_zone_worker": ("park ranger", dict(hair="hat", hat_s=1, top_s=2, leg_s=2, extras=("belt", "badge"))),
    "silph_president": ("VANTEC head", dict(hair="bald", fringe_s=2, mustache=True, wear="coat", top_s=3, extras=("tie",), tie_s=1)),
    "silph_worker_m": ("VANTEC worker", dict(hair="short", hair_s=3, top_s=1, leg_s=3, extras=("tie",))),
    "silph_worker_f": ("VANTEC worker", dict(hair="bun", hair_s=2, top_s=2, wear="skirt", leg_s=2, extras=("collar",))),
    "warden": ("WARDEN", dict(hair="hat", hat_s=3, beard=True, beard_s=1, top_s=2, leg_s=2, extras=("vest",))),
    "waiter": ("waiter", dict(hair="short", hair_s=3, top_s=1, leg_s=3, extras=("tie", "tray"))),
    "rocker": ("GUITARIST", dict(hair="spiky", hair_s=1, top_s=3, leg_s=2, extras=("guitar",))),
    "swimmer": ("DIVER", dict(hair="beanie", hat_s=2, goggles=True, top_s=1, leg_s=2)),
    "red_bike": ("ARLO cycling", dict(hair="beanie", hat_s=2, top_s=1, leg_s=2, extras=("pack",))),
}


def swimmer_frame(st, facing, walk):
    """A diver bobbing in the water: head, shoulders and ripples."""
    f = L.person(dict(st, wear="pants"), facing, False)
    f[12:] = 0
    wave = ["................",
            "..##..####..##..",
            ".#--##----##--#.",
            "................"]
    if walk:
        wave = ["................",
                "....##....##....",
                "..##--####--##..",
                "................"]
    for j, r in enumerate(wave):
        for i, c in enumerate(r):
            if c != ".":
                f[12 + j, i] = O.CH[c]
    f[11][(f[11] > 0)] = np.where(f[11][(f[11] > 0)] == 3, 3, 1)
    return f


def bike_frame(st, facing, walk):
    """ARLO on a cycle: upper body from the kit, the cycle drawn underneath."""
    f = L.person(dict(st, wear="pants"), facing, False)
    if facing in ("down", "up"):
        f[13:] = 0
        f[12, 3:13] = np.where(f[12, 3:13] > 0, f[12, 3:13], 0)
        bars = O.T(["................"] * 10 + [
            "..##........##..",
            "..#-#......#-#..",
            "...######+###...",
            "......#+#.......",
            "......#+#.......",
            "......###......."])
        if walk:
            bars[13:16] = 0
            bars[13, 6:9] = [3, 2, 3]; bars[14, 6:9] = [3, 3, 3]
        m = bars > 0
        f[m] = bars[m]
    else:
        f[13:] = 0
        cyc = O.T(["................"] * 10 + [
            "...###..........",
            "....#+#####.....",
            "..###.#+#.###...",
            ".#-+-##..#-+-#..",
            ".#+#+#...#+#+#..",
            "..###.....###..."])
        if walk:
            cyc[13] = O.T(["................"] * 13 + [".#+-+##..#+-+#.."])[13]
        m = cyc > 0
        f[m] = cyc[m]
    return f


@drawer("sprites/*.png")
def k_sprite(rel, a):
    name = os.path.basename(rel)[:-4]
    h = a["h"]
    if name in O.OBJECTS:
        out = np.zeros((h, 16), np.uint8)
        out[:16] = O.OBJECTS[name]
        return out
    if name in O.CREATURES:
        return O.creature_sheet(*O.CREATURES[name], h)
    if name not in STYLES:
        return None
    st = STYLES[name][1]
    frames = []
    for n in range(h // 16):
        facing, walk = L.FACING[n % 6], n >= 3
        if name == "swimmer":
            fr = swimmer_frame(st, facing, walk)
        elif name == "red_bike":
            fr = bike_frame(st, facing, walk)
        else:
            fr = L.person(st, facing, walk)
        frames.append(fr)
    return np.vstack(frames)



