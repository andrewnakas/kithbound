"""DIRTY ROOM: retail proper noun -> our name, for the originality gate and the
writer packets. Output stays in the work dir (never committed).

    python -m games.pokered.orig_names <pristine> <out names.json>
"""
import json
import os
import re
import sys

from games.pokered import textx, world

# ordinary English words that also name a retail move/item/type: not proper nouns
COMMON = set("""CUT FLY SURF STRENGTH FLASH DIG TELEPORT IRON COIN BICYCLE NUGGET LEMONADE REST GROWL ROAR
SING BITE LEER SLAM BIND WRAP STOMP HEADBUTT TACKLE SCRATCH POUND GUST MIST HAZE REFLECT BARRIER COUNTER
SPLASH SWIFT TRANSFORM SUBSTITUTE STRUGGLE ABSORB GROWTH DISABLE ACID EMBER SMOG SLUDGE TOXIC RAGE MIMIC
SCREECH HARDEN MINIMIZE WITHDRAW BIDE CLAMP CONSTRICT AMNESIA GLARE BARRAGE BUBBLE SPORE PECK THRASH
CONFUSION HYPNOSIS MEDITATE AGILITY RECOVER EXPLOSION SHARPEN CONVERSION SLASH SUPERSONIC LICK SURFBOARD
NORMAL FIGHTING FLYING POISON GROUND ROCK BIRD BUG GHOST FIRE WATER GRASS ELECTRIC PSYCHIC ICE DRAGON
REPEL REVIVE ETHER PROTEIN CALCIUM ANTIDOTE AWAKENING NEW NAME OLD MAN BOX FIGHT ATTACK DEFENSE SPEED
SPECIAL HEALTH ACCURACY EVADE CANCEL QUIT DOME HELIX WATERFALL TOWN MAP FRESH WATER SODA POP COIN CASE
LIFT KEY CARD KEY SECRET KEY ITEMFINDER PP UP OLD ROD GOOD ROD SUPER ROD KINESIS FISSURE DOUBLE TEAM
FOCUS ENERGY LIGHT SCREEN SAILOR LASS HIKER BIKER BURGLAR ENGINEER JUGGLER FISHERMAN SWIMMER GAMBLER BEAUTY
ROCKER TAMER SCIENTIST GENTLEMAN CHANNELER CHIEF RIVAL BLACKBELT YOUNGSTER POTION""".split())


def main(argv):
    tree, out = argv[1], argv[2]
    slots = {s["id"]: s for s in textx.scan(tree)}
    new = json.load(open(textx.NEW + "/00_names.json", encoding="utf8"))
    names = {}
    for k, v in new.items():
        r = slots[k]["text"].replace("@", "").strip()
        if not re.search(r"[A-Za-z]{3,}", r) or k.startswith(("data/text/unused", "constants/player")):
            continue
        r = r.replace("#", "POKé").replace("<PKMN>", "POKéMON")
        if r.upper() in COMMON or r.upper().replace(".", " ") in COMMON:
            continue
        names[r] = v.replace("@", "").strip()
    # hand-picked retail names (prose spellings, people, places) live on the dirty side only
    extra = json.load(open(os.path.join(os.path.dirname(out), "names_extra.json"), encoding="utf8"))
    for k, v in extra.items():
        names.setdefault(k, v)
    json.dump(dict(sorted(names.items())), open(out, "w", encoding="utf8"), ensure_ascii=False, indent=0)
    print(f"names map: {len(names)} retail names -> {out}")


if __name__ == "__main__":
    main(sys.argv)
