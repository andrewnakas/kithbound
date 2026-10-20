"""KITHBOUND people: battle portraits of our tamers, the player, the rival, and the
intro creatures (QUILLORD, TUNEPUFF, NIGHTGRIN) - all our own designs, drawn by the
parametric figure kit (k_people_kit + k_people_gear + k_people_props, cast in k_people_cast).
"""
import os

import numpy as np

from games.pokered.art import drawer
from games.pokered.art.k_people_cast import C
from games.pokered.art.k_people_gear import _c
from games.pokered.art.k_people_kit import BUST, FULL, Fig, Person, _edge


# ------------------------------------------------------------------ rendering
def skirt_layer(s):
    sk = s.p.get("skirt")
    if not sk:
        return
    f = s.f; x, y, low = _c(s); c, ln = sk
    sw = s.r["sw"] * s.p.get("build", 1)
    m = f.P([(x - sw + 1, low - 3), (x + sw - 1, low - 3), (x + sw + 3, low + ln), (x - sw - 3, low + ln)])
    f.part(m, c)
    for k in (-0.5, 0, 0.5):
        f.line([(x + k * sw * 0.8, low), (x + k * sw * 1.3, low + ln - 1)], min(c + 1, 3))


def build(p, k=1.0, ox=0.0, oy=0.0, w=56, h=56):
    p = dict(p)
    rig = p.get("rig", BUST)
    f = Fig(w, h, k, ox, oy, open_bottom=(rig["kind"] == "bust"))
    p.setdefault("mid", [])
    if p.get("skirt"):
        p["mid"] = [skirt_layer] + list(p["mid"])
    p["top"] = p.get("top", 1)
    p_layers = list(p.get("top_layers", []))
    person = Person(f, p)
    person.p["top"] = p["top"]
    # the kit reads 'top' as the shirt shade; held props go in the last layer list
    person.p["top"] = p["top"]
    person.p.setdefault("pre", [])
    person.p["toplayers"] = p_layers
    _draw(person)
    f.outline_all()
    return f.a


def _draw(person):
    p = person.p
    for fn in p.get("pre", []):
        fn(person)
    person.arm("back")
    if person.r["kind"] == "full":
        person.legs()
    for fn in p.get("mid", []):
        fn(person)
    person.torso()
    person.neck()
    person.face_head()
    for fn in p.get("post", []):
        fn(person)
    person.arm("front")
    for fn in p.get("toplayers", []):
        fn(person)


@drawer("trainers/*.png")
def trainer_portrait(rel, a):
    name = os.path.basename(rel)[:-4]
    p = C.get(name)
    if p is None:
        return None
    return build(p)


# ------------------------------------------------------------------ player + intro
from games.pokered.art import k_people_intro as KI     # noqa: E402
from games.pokered.art import k_people_intro2 as KI2   # noqa: E402


@drawer("player/red.png")
def player_portrait(rel, a):
    return build(KI.ARLO)


@drawer("player/shrink1.png")
def player_shrink1(rel, a):
    k = 0.66
    return build(KI.ARLO, k=k, ox=28 * (1 - k), oy=28 * (1 - k))


@drawer("player/shrink2.png")
def player_shrink2(rel, a):
    k = 0.45
    return build(KI.ARLO, k=k, ox=28 * (1 - k), oy=28 * (1 - k))


@drawer("player/redb.png")
def player_back(rel, a):
    return KI.arlo_back(a["w"], a["h"])


@drawer("title/player.png")
def title_player(rel, a):
    return build(KI.ARLO_TITLE, ox=-8, w=a["w"], h=a["h"])


@drawer("battle/oldmanb.png")
def oldman_back(rel, a):
    return KI2.holt_back(a["w"], a["h"])


@drawer("battle/ghost.png")
def tower_ghost(rel, a):
    return KI.ghost(a["w"], a["h"])


@drawer("intro/red_nidorino_*.png")
def intro_quillord(rel, a):
    return KI.quillord(int(rel[-5]))


@drawer("intro/blue_jigglypuff_*.png")
def intro_tunepuff(rel, a):
    return KI2.tunepuff(int(rel[-5]))


@drawer("intro/gengar.png")
def intro_nightgrin(rel, a):
    return KI2.nightgrin(a)
