"""KITHBOUND cast: one parameter dict per battle portrait (engine file name -> our character).

Names follow games/pokered/world.py (TRAINER_CLASSES, PEOPLE).  Keys of a dict are read by
k_people_kit.Person; layer lists (pre, mid, outfit, collar, face, post, top_layers) hold
functions from k_people_gear / k_people_props / below.
"""
import numpy as np

from games.pokered.art.k_people_gear import *          # noqa: F401,F403
from games.pokered.art.k_people_gear import H, _c
from games.pokered.art.k_people_kit import BUST, FULL, _edge, long_back, ponytail, buns, braid
from games.pokered.art.k_people_props import *         # noqa: F401,F403


def mk(**p):
    return p


def T(**kw):
    """Shorthand for a full-body figure."""
    kw.setdefault("rig", FULL)
    return kw


# ------------------------------------------------------------------ one-off details
def _magnifier(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x + 1 * u, y + 2 * u), (x - 3 * u, y - 6 * u)], 1.1 * u), 3, hl=False)
    f.part(f.ring(x - 5 * u, y - 11 * u, 5 * u, 1.6), 3, line=None, hl=False)
    f.flat(f.E(x - 5 * u, y - 11 * u, 3.4 * u), 0)
    f.px(x - 6.5 * u, y - 12.5 * u, 1); f.px(x - 6 * u, y - 13 * u, 1)
    f.part(f.E(x, y, s.r["hand"]), 0)


def soot(s):
    f = s.f; cx, cy, rx, ry = s.head(); u = s.u
    for dx, dy in ((-5, 4), (-4, 5), (-6, 5), (2, 5), (3, 4)):
        f.px(cx + dx * u, cy + dy * u, 2)


def feather(s):
    f = s.f; cx, cy, rx, ry = s.head(); u = s.u
    f.part(f.cap([(cx + rx * 0.9, cy - ry * 0.9), (cx + rx * 1.6, cy - ry * 1.9), (cx + rx * 2.0, cy - ry * 2.2)], 1.6 * u, 0.6 * u), 0)
    f.line([(cx + rx * 0.95, cy - ry * 0.95), (cx + rx * 1.9, cy - ry * 2.1)], 2)


def star_clip(s):
    cx, cy, rx, ry = s.head()
    s.f.stamp("  #  /  #  /#####/ ### / # # ", cx + rx * 0.75, cy - ry * 0.75)


def shell_earring(s):
    cx, cy, rx, ry = s.head(); u = s.u
    s.f.stamp(" ### /#-+-#/ ### ", cx + rx * 0.42, cy + 5.5 * u)


def bubbles(s):
    f = s.f; cx, cy, rx, ry = s.head(); u = s.u
    for dx, dy, r in ((-14, -2, 2.0), (-16, -9, 1.5), (-13, -14, 2.4)):
        f.part(f.E(cx + dx * u, cy + dy * u, r * u), 0, shadow=False)


def snorkel(s):
    f = s.f; cx, cy, rx, ry = s.head(); u = s.u
    f.part(f.cap([(cx - 3 * u, cy + 6 * u), (cx + rx * 0.9, cy + 4 * u), (cx + rx * 1.2, cy - ry * 1.3)], 1.0 * u), 1)


def dive_mask(s):
    f = s.f; cx, cy, rx, ry = s.head(); u = s.u; e1, e2, ey = s.eyepos
    m = f.R(cx - rx * 1.05, ey - 3 * u, cx + 3.8 * u, ey + 3 * u) & (s.headmask | f.R(cx - rx * 1.2, 0, cx, 56))
    f.part(m, 0)
    f.flat(m & ~_edge(m) & f.R(cx - rx, ey - 2 * u, cx - rx * 0.6, ey + 2 * u), 1)
    f.part(f.R(cx + 3.8 * u, ey - 1 * u, cx + rx * 1.05, ey + 1 * u) & f.E(cx, cy, rx * 1.1, ry * 1.1), 3, line=None, hl=False)
    f.stamp("##/##", e1, ey); f.stamp("##/##", e2, ey)


def sack(s):
    f = s.f; x, y, _ = _c(s)
    f.part(f.E(x + 14, y - 2, 9, 8) | f.cap([(x + 8, y - 8), (x + 12, y - 12)], 2.5), 1)
    f.stamp("###/#.#/###", x + 15, y - 1)


def net_back(s):
    f = s.f; x, y, _ = _c(s)
    f.part(f.cap([(x + 10, y + 14), (x + 20, y - 18)], 1.0), 2)
    ring = f.ring(x + 21, y - 25, 7.5, 1.3)
    bag = f.E(x + 21, y - 25, 7.5)
    f.dither(bag & ~ring, 1)
    f.part(ring, 3, line=None, hl=False)


def rope_shoulder(s):
    f = s.f; x, y, low = _c(s); sw = s.r["sw"] * s.p.get("build", 1)
    m = f.cap([(x + sw - 3, y + 1), (x - sw + 2, low)], 2.4) & s.body
    f.part(m, 1, shadow=False)
    f.stripes(m & ~_edge(m), 2, gap=2, dirn=(1, 1))


def chain(s):
    f = s.f; r = s.r; cx = r["cx"] + 1; y1 = r["neck"][1]; u = s.u
    for k in range(-3, 4):
        f.px(cx + k * 1.6 * u, y1 + 3.5 * u - abs(k) * 0.9 * u, 3 if k % 2 else 1)


def studs(s):
    f = s.f
    (lx, ly), (rx_, ry) = s.shoulders()
    for x, y in ((lx, ly), (rx_, ry)):
        for k in (-3, 0, 3):
            f.px(x + k, y - 3, 0)


def pockets(s):
    f = s.f; x, y, low = _c(s)
    for px_, py_ in ((x - 9, y + 12), (x + 5, y + 12), (x - 9, y + 19), (x + 5, y + 19)):
        f.part(f.R(px_, py_, px_ + 6, py_ + 5), 2, shadow=False)


def watch_chain(s):
    f = s.f; x, y, low = _c(s)
    f.line([(x + 1, y + 16), (x - 4, y + 19), (x - 8, y + 17)], 1)
    f.part(f.E(x - 9, y + 17, 1.6), 1, shadow=False)


def gasmask(s):
    f = s.f; x, y, low = _c(s)
    f.part(f.E(x - 5, y + 9, 4, 3.5), 2)
    f.part(f.E(x - 8, y + 11, 1.8), 3, line=None, hl=False)
    f.part(f.E(x - 2, y + 11, 1.8), 3, line=None, hl=False)


def scales(s):
    f = s.f
    m = s.body & ~_edge(s.body)
    yy, xx = np.mgrid[0:f.h, 0:f.w]
    f.a[m & ((xx + (yy // 3) * 2) % 4 == 0) & (yy % 3 == 0)] = 3


def fur(s):
    f = s.f
    (lx, ly), (rx_, ry) = s.shoulders()
    m = f.E(lx + 2, ly - 1, 8, 5) | f.E(rx_ - 2, ry - 1, 8, 5) | f.E((lx + rx_) / 2, ly - 3, 10, 4)
    f.part(m, 1)
    f.dither(m & ~_edge(m), 2)


def medal(s):
    x, y, _ = _c(s)
    s.f.stamp(" # / # /###/#.#/###", x + 7, y + 9)


def bolt_badge(s):
    if hasattr(s, "badge"):
        s.f.stamp(" #/##/#", *s.badge)


def bowtie(s):
    x, y, _ = _c(s)
    s.f.stamp("#   #/## ##/#####/## ##/#   #", x + 0.5, y + 2)


def flower_clip(s):
    cx, cy, rx, ry = s.head()
    s.f.stamp(" ### /##.##/#.#.#/##.##/ ### ", cx + rx * 0.7, cy - ry * 0.7)


def crescent(dx=-6, dy=10):
    return emblem(" ### /##   /#    /##   / ### ", dx=dx, dy=dy)


def backpack_frame(s):
    f = s.f
    f.part(f.R(32, 8, 47, 38), 2)
    f.part(f.R(34, 3, 45, 9), 1)
    f.part(f.E(39.5, 30, 6.5, 3.5), 1)
    f.line([(33, 19), (46, 19)])


# ------------------------------------------------------------------ cast
C = {}

# PROF.BRAMBLE: field naturalist, bushy beard, pinned bush hat, many-pocket vest, magnifier
C["prof.oak"] = mk(hair="sides", hairc=1, hat="bush", hatc=1, eyes="dot", brow="thick", mouth="none",
                   top=1, sleevec=0, arms=("hold", "pocket"), build=1.05,
                   outfit=[lapels(inner=0, depth=30, open_=True), pockets],
                   face=[beard("bushy", c=1), glasses("round")], top_layers=[held(_magnifier)])

# SILAS (rival): long fringe, high-collar coat, smirk; grows a cape by the league
_SILAS = dict(hair="side", hairc=2, eyes="dot", brow="angry", mouth="smirk", top=2, sleevec=2,
              arms=("pocket", "pocket"), collar=[collar_high(c=2, h=5)], outfit=[zipline(c=3)])
C["rival1"] = dict(_SILAS, top=1, sleevec=1, arms=("hip", "pocket"), mouth="grin", collar=[scarf(c=2, tail=True, side=1)],
                   outfit=[zipline(c=3), strap(c=3, rev=True, w=1.0)])
C["rival2"] = dict(_SILAS, face=[earring()], outfit=[zipline(c=3), emblem(" # /###/ # ", dx=-7, dy=10)])
C["rival3"] = dict(_SILAS, arms=("point", "pocket"), build=1.05, pre=[cape(c=3)], face=[earring()],
                   outfit=[zipline(c=3), pads(c=3, size=0.9)], collar=[collar_high(c=3, h=6), necklace(c=3, pendant=" # /#.#/ # ")])

# GLOAM agent: pointed hood, visor half-mask, crescent sigil
C["rocket"] = mk(hair=None, hat="hood", hatc=2, eyes="dot", mouth="flat", top=3, sleevec=3, glove=2,
                 arms=("fist", "hip"), face=[visor_mask(c=3)], outfit=[crescent(), belt(c=2, buckle=False)])

# ---- gym leaders
C["brock"] = mk(hair="bald", hat="band", hatc=1, eyes="dot", brow="thick", mouth="flat", skin=1, top=2,
                sleeve="none", arms=("hold", "hip"), build=1.2, armw=1.3,
                face=[beard("goatee", c=3)], outfit=[pads(c=1, size=1.1), belt(c=3)], top_layers=[held(p_hammer)])
C["misty"] = mk(hair="wave", hairc=2, pre=[lambda s: ponytail(s, high=True)], eyes="big", mouth="grin", top=1, sleevec=2,
                arms=("hold", "hip"), face=[shell_earring],
                outfit=[zipline(c=3), stripes(c=2, gap=4, dirn=(1, 1))], top_layers=[held(p_paddle)])
C["lt.surge"] = mk(hair="bob", hairc=3, hat="peak", hatc=2, eyes="dot", brow="angry", mouth="smirk", top=2, sleevec=2,
                   arms=(((-7, -7), (5, -21)), "hold"), glove=0, face=[bolt_badge],
                   outfit=[buttons(n=4, c=3), pads(c=1, size=0.9), medal], top_layers=[lambda s: p_spark(s, *H(s, "back"))])
C["erika"] = mk(hair="fringe", hairc=2, pre=[braid], eyes="closed", mouth="smile", top=1, sleevec=1,
                arms=("hold", "down"), face=[flower_clip], outfit=[apron(c=0, top=6)], top_layers=[held(p_can)])
C["koga"] = mk(hair="slick", hairc=3, pre=[lambda s: ponytail(s)], eyes="narrow", brow="angry", top=2, sleevec=2, glove=3,
               arms=("cross", "cross"), face=[mask_lower(c=3)], collar=[collar_high(c=2, h=4)],
               outfit=[sash(c=1, w=2.6), p_vials, gasmask])
C["sabrina"] = mk(hair="bob", hairc=3, eyes="glow", mouth="flat", top=3, sleevec=3, arms=("hold", "hold"),
                  pre=[cape(c=2, wide=1.4)], collar=[collar_high(c=3, h=7)], face=[gem()],
                  outfit=[emblem("  #  / ### /#####/ ### /  #  ", dx=0, dy=12)],
                  top_layers=[held(lambda s, x, y: p_orb(s, x - 2, y - 6)),
                              lambda s: p_orb(s, H(s, "back")[0] + 3, H(s, "back")[1] - 8, 3.2)])
C["blaine"] = mk(hair="spiky", hairc=3, hat="bandana", hatc=2, eyes="dot", brow="angry", mouth="grin", top=0, sleeve="short",
                 sleevec=0, glove=3, arms=("hold", "hip"), build=1.1, face=[soot], outfit=[apron(c=2, top=2)],
                 top_layers=[held(p_tongs)])
C["giovanni"] = mk(hair="slick", hairc=1, eyes="dot", brow="angry", mouth="smirk", top=3, sleevec=3, glove=3,
                   arms=("hold", "pocket"), build=1.1, collar=[collar_high(c=3, h=5)],
                   outfit=[lapels(inner=1, depth=14, tie=3), crescent(dx=-8, dy=18)],
                   top_layers=[staff(top=(-1, -14), bottom=(2, 30), c=3, head=p_knob, w=1.0)])

# ---- elite four
C["lorelei"] = mk(hair="sweep", hairc=3, hat="parka", hatc=1, eyes="narrow", mouth="flat", top=1, sleevec=1, glove=2,
                  arms=("hold", "down"), outfit=[zipline(c=3), stripes(c=0, gap=6)],
                  top_layers=[staff(top=(-3, -28), bottom=(2, 22), c=2, head=p_icetip, w=1.1)])
C["bruno"] = mk(hair="topknot", hairc=2, eyes="dot", brow="thick", mouth="flat", skin=1, top=2, sleeve="none",
                arms=("cross", "cross"), build=1.35, armw=1.5, cuff=0, face=[beard("braided", c=2)], post=[fur],
                outfit=[belt(c=3)])
C["agatha"] = mk(rigmod=dict(cx=23, cy=21), hair="sides", hairc=0, hat="hood", hatc=2, eyes="narrow", brow="worry", mouth="frown",
                 top=2, sleevec=2, arms=("hold", "down"), outfit=[necklace(c=3, pendant=" # /###/ # ")],
                 top_layers=[staff(top=(-2, -28), bottom=(2, 22), c=1, head=p_crook, w=1.1)])
C["lance"] = mk(hair="sweep", hairc=3, pre=[cape(c=3, wide=1.2), lambda s: long_back(s, length=0.7)], eyes="dot", brow="angry",
                mouth="flat", top=2, sleevec=2, glove=3, arms=("point", "hip"), face=[circlet(c=1)],
                outfit=[scales, pads(c=1, size=1.0)])

# ---- tamer classes
C["youngster"] = T(hair="tuft", hairc=2, eyes="big", mouth="grin", top=0, sleeve="short", sleevec=0,
                   arms=("hold", "hip"), shorts=6, pants=2, socks=0, shoes=3, face=[bandaid()],
                   outfit=[stripes(c=1, gap=2), lambda s: s.f.part(s.body & (s.f.Y > 28), 2), strap(c=2, w=0.9), strap(c=2, rev=True, w=0.9)],
                   top_layers=[held(p_slingshot)])
C["bugcatcher"] = mk(hair="short", hairc=2, hat="bucket", hatc=1, eyes="big", mouth="open", top=1, sleeve="short", sleevec=1,
                     arms=("hold", "down"), pre=[net_back], outfit=[strap(c=3)], top_layers=[held(p_jar)])
C["lass"] = T(hair="fringe", hairc=3, eyes="big", mouth="smile", top=2, sleevec=2,
              arms=("chest", "chest"), skirt=(1, 9), pants=0, socks=0, shoes=3, legw=1.8, stance=2.5,
              face=[buns], outfit=[lapels(inner=0, depth=7, tie=3, open_=False)], top_layers=[held(p_book)])
C["sailor"] = mk(hair="short", hairc=1, hat="beanie", hatc=2, eyes="dot", brow="thick", mouth="smile", top=1, sleevec=1,
                 arms=("cross", "cross"), build=1.15, face=[beard("stubble")], collar=[collar_high(c=1, h=4)],
                 outfit=[stripes(c=2, gap=3), rope_shoulder])
C["jr.trainerm"] = T(hair="spiky", hairc=3, hat="backcap", hatc=2, eyes="big", mouth="grin", top=1, sleevec=2,
                     arms=("hold", "hip"), shorts=7, pants=2, shoes=3, socks=0, outfit=[zipline(c=3)], top_layers=[snare()])
C["jr.trainerf"] = T(hair="fringe", hairc=2, pre=[lambda s: ponytail(s, high=True)], eyes="big", mouth="smile", top=0, sleeve="short",
                     sleevec=2, arms=("point", "hip"), shorts=5, pants=2, shoes=3, socks=0, outfit=[sash(c=2, w=1.5)])
C["pokemaniac"] = mk(hair="short", hairc=2, hat="hood", hatc=1, eyes="round", mouth="open", top=1, sleevec=1,
                     arms=("hold", "down"), face=[glasses("round"), ears_hood(c=1)],
                     outfit=[emblem("###/#.#/###", dx=-8, dy=9), emblem(" # /###/ # ", dx=6, dy=13), emblem("#.#/.#./#.#", dx=-3, dy=17)],
                     top_layers=[held(p_plush)])
C["supernerd"] = mk(hair="curly", hairc=2, eyes="dot", mouth="flat", top=2, sleevec=2, arms=("hold", "down"),
                    face=[glasses("square"), headset()], outfit=[zipline(c=3)], top_layers=[held(p_device)])
C["hiker"] = T(hair="short", hairc=2, hat="pom", hatc=2, eyes="dot", mouth="smile", top=1, sleevec=1,
               arms=("hold", "down"), build=1.25, pants=2, shoes=3, legw=3.0, pre=[backpack_frame],
               face=[beard("full", c=1)], outfit=[strap(c=3, rev=True)],
               top_layers=[staff(top=(-1, -16), bottom=(1, 16), c=2, w=0.9)])
C["biker"] = mk(hair=None, hat="helmet", hatc=2, eyes="narrow", brow="angry", mouth="teeth", top=3, sleevec=3, glove=3,
                arms=("cross", "cross"), build=1.2, collar=[chain], outfit=[lapels(inner=1, depth=16), pads(c=3, size=0.8), studs])
C["burglar"] = mk(hair="short", hairc=3, hat="beanie", hatc=3, eyes="dot", brow="angry", top=2, sleevec=2, glove=3,
                  arms=("low", "down"), pre=[sack], face=[mask_lower(c=1)], outfit=[stripes(c=3, gap=3)])
C["engineer"] = mk(hair="buzz", hairc=2, eyes="dot", brow="thick", mouth="smile", top=1, sleevec=1, glove=2,
                   arms=("hold", "hip"), build=1.1, face=[goggles(), beard("stubble")],
                   outfit=[zipline(c=2), emblem("####/#..#/####", dx=5, dy=8)], top_layers=[held(p_wrench)])
C["juggler"] = T(hair="topknot", hairc=3, eyes="closed", mouth="smile", top=0, sleeve="none", arms=("raise", "raise"),
                 pants=1, shoes=3, legw=2.2, stance=4.5,
                 outfit=[lambda s: s.f.dither(s.body & ~_edge(s.body) & (s.f.Y > 25), 1)],
                 top_layers=[lambda s: p_rings(s, H(s, "front")[0] + 6, H(s, "front")[1] + 4)])
C["fisher"] = mk(hair="short", hairc=2, hat="wide", hatc=1, eyes="dot", mouth="smile", top=1, sleevec=0,
                 arms=("hold", "pocket"), face=[mustache("thick", c=2)], outfit=[pockets, zipline(c=3)],
                 top_layers=[rod(tip=(-6, -32), c=2, line_to=(-6, 26))])
C["swimmer"] = mk(hair="buzz", hairc=3, eyes="dot", mouth="smile", top=2, sleevec=2, arms=("wave", "down"),
                  face=[goggles(c=1)], collar=[scarf(c=0, tail=True, side=-1)], outfit=[zipline(c=0), stripes(c=1, gap=5, dirn=(1, 0))])
C["cueball"] = mk(hair="fade", hairc=3, eyes="dot", brow="angry", mouth="frown", top=0, skin=1, sleeve="none", build=1.3, armw=1.45,
                  arms=("fist", "fist"), face=[scar()], collar=[chain])
C["gambler"] = mk(hair="slick", hairc=2, hat="dealer", hatc=1, eyes="dot", mouth="smirk", top=2, sleevec=0,
                  arms=("hold", "hip"), face=[mustache("thin", c=3)], outfit=[lapels(inner=0, depth=16, tie=3)],
                  top_layers=[held(p_cards), lambda s: p_dice(s, *H(s, "back"))])
C["beauty"] = mk(hair="wave", hairc=2, pre=[lambda s: long_back(s, length=1.0)], eyes="big", mouth="smile", top=2, sleevec=2,
                 arms=("hold", "down"), face=[star_clip, earring()], outfit=[vneck(depth=10)],
                 collar=[necklace(c=3)], top_layers=[held(p_mirror)])
C["psychic"] = mk(hair="short", hairc=3, eyes="closed", mouth="flat", top=1, sleevec=1, arms=("hold", "hold"),
                  face=[veil(c=2), gem()], outfit=[sash(c=2, w=2.0)],
                  top_layers=[lambda s: p_orb(s, (H(s, "front")[0] + H(s, "back")[0]) / 2, H(s, "front")[1] - 7, 4.5)])
C["rocker"] = mk(hair="mohawk", hairc=3, eyes="narrow", brow="angry", mouth="open", top=3, sleeve="none",
                 arms=("chest", "hold"), face=[earring()], outfit=[studs], top_layers=[held(p_guitar)])
C["tamer"] = mk(hair="short", hairc=2, hat="wide", hatc=2, eyes="dot", brow="thick", top=1, sleevec=1, glove=2,
                arms=("hold", "hip"), face=[mustache("thick", c=3)], collar=[scarf(c=2, tail=False)],
                outfit=[belt(c=3)], top_layers=[held(p_rope)])
C["birdkeeper"] = mk(hair="short", hairc=1, hat="bucket", hatc=2, eyes="dot", mouth="smile", top=1, sleevec=1, glove=2,
                     arms=("hold", "down"), face=[feather], outfit=[strap(c=2)], top_layers=[held(p_bird)])
C["blackbelt"] = T(hair="short", hairc=3, hat="band", hatc=0, eyes="dot", brow="angry", mouth="open", top=0, sleevec=0,
                   arms=("fist", "hip"), pants=0, shoes=0, stance=5.5, legw=3.0, build=1.15,
                   outfit=[lapels(inner=0, depth=7, open_=False), belt(c=3, buckle=False)])
C["scientist"] = mk(hair="curly", hairc=1, eyes="dot", mouth="open", top=0, sleevec=0, arms=("hold", "pocket"),
                    face=[goggles()], outfit=[lapels(inner=2, depth=18, tie=3), emblem("#/#/#", dx=7, dy=10)],
                    top_layers=[held(p_flask)])
C["cooltrainerm"] = mk(hair="spiky", hairc=3, eyes="dot", brow="angry", mouth="flat", top=2, sleevec=2, glove=3,
                       arms=("cross", "cross"), face=[scar()], outfit=[lapels(inner=1, depth=14), pads(c=3, size=0.9)])
C["cooltrainerf"] = mk(hair="side", hairc=2, pre=[lambda s: long_back(s, length=1.3)], eyes="big", brow="flat", mouth="smile",
                       top=1, sleevec=1, glove=3, arms=("hold", "hip"), outfit=[lapels(inner=3, depth=14), belt(c=3)],
                       top_layers=[snare()])
C["gentleman"] = mk(hair="slick", hairc=1, eyes="dot", brow="thick", mouth="none", top=3, sleevec=3, arms=("hold", "pocket"),
                    face=[mustache("thick", c=1)], outfit=[lapels(inner=0, depth=14), bowtie, watch_chain],
                    top_layers=[staff(top=(-1, -12), bottom=(2, 30), c=2, head=p_knob, w=1.0)])
C["channeler"] = mk(hair="fringe", hairc=3, hat="hood", hatc=1, eyes="closed", mouth="open", top=2, sleevec=2,
                    arms=("raise", "down"), collar=[necklace(c=3, pendant="#.#/.#./#.#")],
                    top_layers=[lambda s: p_lantern(s, *H(s, "front"))])
