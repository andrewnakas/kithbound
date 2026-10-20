"""KITHBOUND creature pictures: every front and back is drawn by our own procedural
generator (body-plan templates + per-family features from the roster concept).
No retail picture, outline or silhouette is read: only the picture size from the spec.
"""
import os

import numpy as np

from games.pokered.art import drawer
from games.pokered.art.k_kith_draw import Fig

# engine picture names in national order (matches world.ROSTER order)
STEMS = ("bulbasaur ivysaur venusaur charmander charmeleon charizard squirtle wartortle blastoise caterpie "
         "metapod butterfree weedle kakuna beedrill pidgey pidgeotto pidgeot rattata raticate spearow fearow "
         "ekans arbok pikachu raichu sandshrew sandslash nidoranf nidorina nidoqueen nidoranm nidorino nidoking "
         "clefairy clefable vulpix ninetales jigglypuff wigglytuff zubat golbat oddish gloom vileplume paras "
         "parasect venonat venomoth diglett dugtrio meowth persian psyduck golduck mankey primeape growlithe "
         "arcanine poliwag poliwhirl poliwrath abra kadabra alakazam machop machoke machamp bellsprout weepinbell "
         "victreebel tentacool tentacruel geodude graveler golem ponyta rapidash slowpoke slowbro magnemite "
         "magneton farfetchd doduo dodrio seel dewgong grimer muk shellder cloyster gastly haunter gengar onix "
         "drowzee hypno krabby kingler voltorb electrode exeggcute exeggutor cubone marowak hitmonlee hitmonchan "
         "lickitung koffing weezing rhyhorn rhydon chansey tangela kangaskhan horsea seadra goldeen seaking "
         "staryu starmie mrmime scyther jynx electabuzz magmar pinsir tauros magikarp gyarados lapras ditto "
         "eevee vaporeon jolteon flareon porygon omanyte omastar kabuto kabutops aerodactyl snorlax articuno "
         "zapdos moltres dratini dragonair dragonite mewtwo mew").split()
assert len(STEMS) == 151


def roster_name(stem):
    from games.pokered.world import ROSTER
    return ROSTER[STEMS.index(stem)][0]


def fit(W, H, box, back=False, fill=0.94, margin=1.0, wfill=None, bw_=1.6, bh_=1.22, bcrop=0.15, btop=None):
    u0, v0, u1, v1 = box
    bw, bh = max(u1 - u0, 1), max(v1 - v0, 1)
    cu = (u0 + u1) / 2 - 50
    if back:
        sc = min(W * bw_ / bw, H * bh_ / bh)
        fw, fh = bw * sc, bh * sc
        ox = W / 2 + cu * sc if fw <= W else W - 1 + (u0 - 50) * sc
        bottom = max(H + bcrop * fh, fh + 1) if btop is None else btop + fh
        return dict(sc=sc, ox=ox, oy=bottom - (v1 - 100) * sc)
    sc = min(W * (wfill or fill) / bw, (H - margin) * fill / bh)
    return dict(sc=sc, ox=W / 2 - cu * sc, oy=H - margin - (v1 - 100) * sc)


def draw_creature(name, W, H, back=False):
    from games.pokered.art import k_kith_fam as fam
    fn, st, opts = fam.lookup(name)
    o = dict(opts)
    o.update(o.pop("b", {}) if back else {})
    probe = Fig(W, H, back=back, sc=W / 140.0, ox=W / 2.0, oy=H * 0.85)
    fn(probe, st)
    t = fit(W, H, probe.bbox(), back=back, **o)
    f = Fig(W, H, back=back, **t)
    fn(f, st)
    return f.render()


@drawer("pokemon/*/*.png")
def kith(rel, a):
    stem = os.path.basename(rel)[:-4].replace(".", "")
    back = "/back/" in rel
    if back and stem.endswith("b"):
        stem = stem[:-1]
    if stem.startswith("fossil"):
        from games.pokered.art import k_kith_fam5
        return k_kith_fam5.fossil(stem, a["w"], a["h"])
    if stem not in STEMS:
        return None
    return draw_creature(roster_name(stem), a["w"], a["h"], back)
