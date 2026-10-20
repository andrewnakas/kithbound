"""KITHBOUND people: small held props (drawn at a hand position)."""
import numpy as np

from games.pokered.art.k_people_gear import _c
from games.pokered.art.k_people_kit import _edge


# ------------------------------------------------------------------ small prop drawers


def p_book(s, x, y):
    f = s.f; u = s.u
    m = f.P([(x - 6 * u, y - 4 * u), (x + 3 * u, y - 6 * u), (x + 5 * u, y + 3 * u), (x - 4 * u, y + 5 * u)])
    f.part(m, 1)
    f.line([(x - 5 * u, y - 2 * u), (x + 3.5 * u, y - 4 * u)], 2)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_jar(s, x, y):
    f = s.f; u = s.u
    m = f.R(x - 4 * u, y - 9 * u, x + 4 * u, y + 1 * u)
    f.part(m, 0)
    f.part(f.R(x - 4.5 * u, y - 11 * u, x + 4.5 * u, y - 8.5 * u), 2)
    f.stamp("+ +/.#./###/.#.", x, y - 4.5 * u)
    f.part(f.E(x, y + 1 * u, s.r["hand"] * 1.1), s.p.get("skin", 0))


def p_flask(s, x, y):
    f = s.f; u = s.u
    f.part(f.R(x - 1.3 * u, y - 10 * u, x + 1.5 * u, y - 4 * u), 0)
    f.part(f.E(x, y - 2.5 * u, 3.6 * u, 3.4 * u), 1)
    f.flat(f.E(x, y - 1.8 * u, 2.4 * u, 1.8 * u) & ~_edge(f.E(x, y - 2.5 * u, 3.6 * u, 3.4 * u)), 2)
    for k, (dx, dy) in enumerate(((-1, -13), (2, -16), (-2, -19))):
        f.part(f.E(x + dx * u, y + dy * u, 1.3 * u), 0)
    f.part(f.E(x, y + 1 * u, s.r["hand"]), s.p.get("skin", 0))


def p_orb(s, x, y, r=4.0):
    f = s.f; u = s.u
    f.part(f.E(x, y, r * u), 1, shadow=False)
    f.flat(f.E(x - 1 * u, y - 1 * u, 1.2 * u), 0)
    f.part(f.ring(x, y, r * u + 2.5, 1.0) & ((f.X - x) * (f.Y - y) > 0), 2, line=None, shadow=False)


def p_cards(s, x, y):
    f = s.f; u = s.u
    for k, a in enumerate((-0.5, 0.0, 0.5)):
        cx_, cy_ = x - 2 * u + a * 6 * u, y - 5 * u - (1 - abs(a)) * 2 * u
        m = f.P([(cx_ - 2.5 * u, cy_ - 4 * u), (cx_ + 2.5 * u, cy_ - 4 * u), (cx_ + 2.5 * u, cy_ + 4 * u), (cx_ - 2.5 * u, cy_ + 4 * u)])
        f.part(m, 0, shadow=False)
        f.stamp(["#", " #", "#"][k] if k != 1 else "+#+", cx_, cy_)
    f.part(f.E(x, y, s.r["hand"] * 1.05), s.p.get("skin", 0))


def p_wrench(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x + 6 * u, y + 6 * u), (x - 6 * u, y - 9 * u)], 1.6 * u), 2)
    m = f.E(x - 7.5 * u, y - 11 * u, 4 * u) & ~f.P([(x - 9 * u, y - 18 * u), (x - 7 * u, y - 11 * u), (x - 4 * u, y - 16 * u)])
    f.part(m, 2)
    f.part(f.E(x, y, s.r["hand"] * 1.1), s.p.get("glove", 0))


def p_lantern(s, x, y):
    f = s.f; u = s.u
    f.line([(x, y), (x, y + 3 * u)])
    f.part(f.R(x - 3.5 * u, y + 3 * u, x + 3.5 * u, y + 12 * u), 0)
    f.part(f.E(x, y + 7.5 * u, 1.6 * u, 2.4 * u), 1, line=None, shadow=False)
    f.part(f.R(x - 4.5 * u, y + 2 * u, x + 4.5 * u, y + 4 * u), 3)
    f.part(f.R(x - 4.5 * u, y + 11.5 * u, x + 4.5 * u, y + 13 * u), 3)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_mirror(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x, y + 2 * u), (x - 1 * u, y - 6 * u)], 1.0 * u), 2)
    f.part(f.E(x - 1.8 * u, y - 10 * u, 3.6 * u, 4.4 * u), 2)
    f.flat(f.E(x - 1.8 * u, y - 10 * u, 2.2 * u, 3 * u), 0)
    f.px(x - 2.6 * u, y - 11.5 * u, 1)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_can(s, x, y):           # watering can
    f = s.f; u = s.u
    f.part(f.cap([(x - 5 * u, y + 4 * u), (x - 14 * u, y - 3 * u)], 1.0 * u, 0.8 * u), 2)
    f.part(f.E(x - 14.5 * u, y - 3.5 * u, 2 * u, 1.5 * u), 2)
    f.part(f.R(x - 6 * u, y + 1 * u, x + 4 * u, y + 11 * u), 1)
    f.part(f.ring(x + 0.5 * u, y + 1.5 * u, 4 * u, 1.4) & (f.Y < y + 1.5 * u), 3, line=None, shadow=False, hl=False)
    for dx, dy in ((-17, 0), (-18, 3), (-16, 5)):
        f.px(x + dx * u, y + dy * u, 2)
    f.part(f.E(x, y - 1 * u, s.r["hand"]), s.p.get("skin", 0))


def p_guitar(s, x, y):
    f = s.f; u = s.u
    bx, by = x + 9 * u, y + 7 * u
    body = f.E(bx, by, 7 * u, 5.5 * u) | f.E(bx - 6 * u, by - 3 * u, 5 * u, 4 * u)
    f.part(body, 2)
    f.part(f.E(bx - 2 * u, by - 1 * u, 1.8 * u), 3, line=None, hl=False)
    f.part(f.cap([(bx - 7 * u, by - 4 * u), (x - 12 * u, y - 14 * u)], 1.3 * u), 1)
    f.part(f.R(x - 15 * u, y - 18 * u, x - 10 * u, y - 13 * u), 3)
    f.line([(bx + 2 * u, by + 1 * u), (x - 12 * u, y - 14 * u)], 3)


def p_fan(s, x, y):
    f = s.f; u = s.u
    m = f.E(x - 1 * u, y - 4 * u, 9 * u, 9 * u) & (f.Y < y - 4 * u) & ((f.X - x) < (f.Y - y) * -0.2 + 5 * u)
    f.part(m, 0)
    for a in (-0.8, -0.3, 0.2, 0.7):
        f.line([(x, y - 3 * u), (x - 1 * u + a * 9 * u, y - 4 * u - (1 - abs(a)) * 8 * u)], 2)
    f.part(f.E(x, y - 2 * u, s.r["hand"]), s.p.get("skin", 0))


def p_bird(s, x, y):          # falcon on a glove
    f = s.f; u = s.u
    body = f.E(x + 1 * u, y - 7 * u, 4.5 * u, 6 * u)
    f.part(body, 2)
    f.part(f.E(x - 1 * u, y - 13.5 * u, 3.4 * u, 3.2 * u), 1)
    f.part(f.P([(x - 4 * u, y - 14 * u), (x - 7 * u, y - 12.5 * u), (x - 4 * u, y - 12 * u)]), 3)
    f.px(x - 2 * u, y - 14.5 * u, 3)
    f.part(f.P([(x + 3 * u, y - 10 * u), (x + 12 * u, y - 15 * u), (x + 9 * u, y - 4 * u)]), 3)
    f.part(f.P([(x + 3 * u, y - 2 * u), (x + 7 * u, y + 4 * u), (x + 1 * u, y + 1 * u)]), 3)
    f.part(f.E(x, y, s.r["hand"] * 1.3, s.r["hand"] * 1.1), s.p.get("glove", 2))


def p_net(s, x, y):
    f = s.f; u = s.u
    hx, hy = x + 12 * u, y - 18 * u
    f.part(f.cap([(x - 3 * u, y + 5 * u), (hx, hy)], 0.8 * u), 2)
    ring = f.ring(hx + 3 * u, hy - 3 * u, 6 * u, 1.2)
    bag = f.E(hx + 3 * u, hy - 3 * u, 6 * u) & ~f.ring(hx + 3 * u, hy - 3 * u, 6 * u, 1.2)
    f.dither(bag, 1)
    f.flat(ring, 3)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_slingshot(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x, y + 2 * u), (x, y - 4 * u), (x - 3 * u, y - 9 * u)], 0.8 * u) | f.cap([(x, y - 4 * u), (x + 3 * u, y - 9 * u)], 0.8 * u), 2)
    f.line([(x - 3 * u, y - 9 * u), (x + 5 * u, y - 5 * u), (x + 3 * u, y - 9 * u)], 3)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_rings(s, x, y):
    f = s.f; u = s.u
    for dx, dy, r in ((-6, -10, 3.4), (2, -16, 3.4), (9, -9, 3.4)):
        f.part(f.ring(x + dx * u, y + dy * u, r * u, 1.6), 3, line=None, hl=False)


def p_hammer(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x - 3 * u, y + 7 * u), (x + 8 * u, y - 16 * u)], 1.3 * u), 1)
    head = f.P([(x + 2 * u, y - 18 * u), (x + 12 * u, y - 23 * u), (x + 15 * u, y - 17 * u), (x + 5 * u, y - 12 * u)])
    f.part(head, 2)
    f.part(f.E(x, y, s.r["hand"] * 1.15), s.p.get("glove", s.p.get("skin", 0)))


def p_paddle(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x + 4 * u, y + 10 * u), (x - 4 * u, y - 14 * u)], 1.1 * u), 2)
    f.part(f.E(x - 6 * u, y - 20 * u, 3.6 * u, 6.5 * u), 1)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_clipboard(s, x, y):
    f = s.f; u = s.u
    m = f.P([(x - 6 * u, y - 8 * u), (x + 4 * u, y - 9 * u), (x + 5 * u, y + 5 * u), (x - 5 * u, y + 6 * u)])
    f.part(m, 0)
    f.part(f.R(x - 2.5 * u, y - 10 * u, x + 1.5 * u, y - 7.5 * u), 3)
    for k in range(3):
        f.line([(x - 4 * u, y - 4 * u + k * 3 * u), (x + 3 * u, y - 4.5 * u + k * 3 * u)], 2)
    f.part(f.E(x + 1 * u, y + 2 * u, s.r["hand"]), s.p.get("skin", 0))


def p_device(s, x, y):        # handheld gadget with an antenna
    f = s.f; u = s.u
    m = f.R(x - 5 * u, y - 7 * u, x + 4 * u, y + 2 * u)
    f.part(m, 2)
    f.part(f.R(x - 3.5 * u, y - 5.5 * u, x + 2.5 * u, y - 1 * u), 0, line=3)
    f.line([(x + 3 * u, y - 7 * u), (x + 5 * u, y - 12 * u)], 3); f.px(x + 5 * u, y - 12.5 * u, 3)
    f.part(f.E(x, y + 2 * u, s.r["hand"]), s.p.get("skin", 0))


def p_plush(s, x, y):
    f = s.f; u = s.u
    f.part(f.E(x - 1 * u, y - 4 * u, 5 * u, 4.5 * u), 0)
    for dx in (-4, 2):
        f.part(f.P([(x + (dx - 1.5) * u, y - 7 * u), (x + dx * u, y - 12 * u), (x + (dx + 2) * u, y - 7.5 * u)]), 0)
    f.px(x - 3 * u, y - 4 * u, 3); f.px(x + 0.5 * u, y - 4 * u, 3)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("skin", 0))


def p_rope(s, x, y):
    f = s.f; u = s.u
    for k in range(3):
        f.part(f.ring(x + 1 * u, y + 2 * u + k * 0.8, (5.5 - k * 0.6) * u, 1.3), 2, line=None, shadow=False)
    f.part(f.E(x, y, s.r["hand"]), s.p.get("glove", s.p.get("skin", 0)))


def p_tongs(s, x, y):
    f = s.f; u = s.u
    f.part(f.cap([(x + 2 * u, y + 2 * u), (x - 10 * u, y - 12 * u)], 0.8 * u) | f.cap([(x + 2 * u, y + 2 * u), (x - 12 * u, y - 9 * u)], 0.8 * u), 3, hl=False)
    f.part(f.E(x - 13 * u, y - 12 * u, 2.8 * u, 2.5 * u), 1)
    f.part(f.E(x, y, s.r["hand"] * 1.15), s.p.get("glove", 2))


def p_spark(s, x, y):
    f = s.f; u = s.u
    f.part(f.P([(x - 1 * u, y - 15 * u), (x + 4 * u, y - 15 * u), (x + 1 * u, y - 9 * u), (x + 4 * u, y - 9 * u), (x - 4 * u, y + 0 * u),
                (x - 1 * u, y - 7 * u), (x - 4 * u, y - 7 * u)]), 0)


def p_dice(s, x, y):
    f = s.f; u = s.u
    for dx, dy in ((-5, -6), (1, -9)):
        f.part(f.R(x + dx * u, y + dy * u, x + (dx + 4.5) * u, y + (dy + 4.5) * u), 0, shadow=False)
        f.px(x + (dx + 2) * u, y + (dy + 2) * u, 3)


def p_vials(s):
    f = s.f; x, y, low = _c(s); u = s.u
    for k in range(4):
        vx, vy = x - 9 * u + k * 5 * u, y + 7 * u + k * 3.3 * u
        f.part(f.R(vx - 1.2 * u, vy - 3 * u, vx + 1.6 * u, vy + 3 * u), 0 if k % 2 else 1)


def p_trident(s, a):
    f = s.f; x, y = a; u = s.u
    for dx in (-3.5, 0, 3.5):
        f.part(f.cap([(x + dx * u * 0.4, y + 2 * u), (x + dx * u, y - 5 * u)], 0.8 * u), 2)
    f.part(f.R(x - 4 * u, y + 1 * u, x + 4 * u, y + 3 * u), 2)


def p_icetip(s, a):
    f = s.f; x, y = a; u = s.u
    f.part(f.P([(x, y - 9 * u), (x + 3.5 * u, y - 1 * u), (x, y + 3 * u), (x - 3.5 * u, y - 1 * u)]), 0)
    f.line([(x, y - 7 * u), (x, y + 1 * u)], 1)


def p_crook(s, a):
    f = s.f; x, y = a; u = s.u
    f.part(f.ring(x - 3 * u, y + 1 * u, 4 * u, 1.8) & (f.Y < y + 1.5 * u), 2, line=3)
    f.part(f.R(x - 9 * u, y + 2 * u, x - 5 * u, y + 9 * u) | f.E(x - 7 * u, y + 5.5 * u, 2.5 * u, 3 * u), 0)
    f.flat(f.E(x - 7 * u, y + 5.5 * u, 1 * u, 1.6 * u), 1)


def p_knob(s, a):
    f = s.f; x, y = a; u = s.u
    f.part(f.E(x, y, 2.4 * u, 2.0 * u), 3)


def p_wyrmhead(s, a):
    f = s.f; x, y = a; u = s.u
    f.part(f.P([(x - 2 * u, y + 2 * u), (x - 5 * u, y - 4 * u), (x + 0 * u, y - 7 * u), (x + 4 * u, y - 3 * u), (x + 2 * u, y + 2 * u)]), 1)
    f.px(x - 1 * u, y - 3 * u, 3)


