"""KITHBOUND body-plan templates.  Each takes a Fig and keyword parameters, draws the
base creature facing left and returns a dict of anchor points for features."""
import math

from games.pokered.art.k_kith_lib import (arc, bird_wing, flame, horn, leaf, rot, spikes,
                                          tail_fin, fang)


def _call(fn, f, a):
    if fn:
        for g in (fn if isinstance(fn, (list, tuple)) else [fn]):
            g(f, a)


# ------------------------------------------------------------------ ears / tails / faces
def ears(f, kind, x, y, r, s=1, far=False, inner=None, ang=0):
    """One ear rooted at (x, y), size r."""
    if not kind:
        return
    if kind == "point":
        pts = rot([(-r * 0.5, 0), (-r * 0.1, -r * 1.3), (r * 0.5, 0)], ang, x, y)
    elif kind == "tall":
        pts = rot([(-r * 0.45, 0), (-r * 0.15, -r * 1.9), (r * 0.45, 0)], ang, x, y)
    elif kind == "round":
        j = f.ell(x, y - r * 0.5, r * 0.6, r * 0.7, s, ang=ang)
        if inner is not None and not far:
            f.mark_ell(x, y - r * 0.45, r * 0.3, r * 0.4, inner, clip=j)
        return j
    elif kind == "long":
        j = f.ell(*rot([(0, -r * 1.1)], ang, x, y)[0], r * 0.4, r * 1.25, s, ang=ang)
        if inner is not None and not far:
            f.mark_ell(*rot([(0, -r * 1.0)], ang, x, y)[0], r * 0.18, r * 0.9, inner, ang=ang, clip=j)
        return j
    elif kind == "fold":
        pts = rot([(-r * 0.6, 0), (-r * 0.2, -r * 0.8), (r * 0.6, -r * 0.6), (r * 0.5, r * 0.1)], ang, x, y)
    elif kind == "moon":
        a = arc(0, -r * 0.6, r * 0.7, r * 0.8, 90, 270, 9)
        b = arc(r * 0.3, -r * 0.75, r * 0.5, r * 0.62, 260, 100, 9)
        pts = rot(a + b, ang, x, y)
    elif kind == "tuft":
        pts = rot([(-r * 0.5, 0), (-r * 0.2, -r * 1.3), (-r * 0.05, -r * 1.9), (0.0, -r * 1.25), (r * 0.5, 0)], ang, x, y)
    elif kind == "fin":
        pts = rot([(-r * 0.4, 0), (r * 0.5, -r * 1.3), (r * 0.2, -r * 0.6), (r * 0.7, -r * 0.9), (r * 0.5, 0)], ang, x, y)
    else:
        return
    j = f.poly(pts, s)
    if inner is not None and not far and kind in ("point", "tall", "tuft"):
        q = rot([(-r * 0.22, -r * 0.1), (-r * 0.1, -r * 0.9), (r * 0.18, -r * 0.1)], ang, x, y)
        f.mark_poly(q, inner, clip=j)
    return j


def tail(f, kind, x, y, ln, r, s=1, ang=-40, tip=None, **k):
    """Tail from root (x, y), going right/up at angle ang (degrees, 0 = right, -90 = up)."""
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
    mx, my = x + math.cos(a + 0.5) * ln * 0.55, y + math.sin(a + 0.5) * ln * 0.55
    out = {"tip": (ex, ey)}
    if kind in ("thin", "flame", "ring", "coil", "stinger", "club", "leaf", "bolt"):
        pts = [(x, y), (mx, my), (ex, ey)]
        if kind == "coil":
            pts = [(x, y), (mx, my), (ex, ey)] + [(ex + math.cos(t) * ln * 0.18 - ln * 0.18, ey + math.sin(t) * ln * 0.18) for t in
                                                  [0.6, 1.4, 2.2, 3.0, 3.8, 4.6]]
        out["id"] = f.stroke(pts, r, r * 0.6, s, **k)
        if kind == "flame":
            flame(f, ex, ey + r, r * 3.2, r * 5, ang=ang + 90, n=3, s=tip if tip is not None else 1)
        elif kind == "ring":
            for t in (0.35, 0.65, 0.9):
                px, py = (x + (ex - x) * t + (mx - (x + ex) / 2) * 1.2 * (1 - abs(2 * t - 1)),
                          y + (ey - y) * t + (my - (y + ey) / 2) * 1.2 * (1 - abs(2 * t - 1)))
                f.mark_ell(px, py, r * 1.1, r * 1.1, 2 if s < 2 else 0, clip=out["id"])
        elif kind == "stinger":
            horn(f, ex, ey, r * 4, r * 2, math.degrees(a), s=0)
        elif kind == "club":
            out["club"] = f.ell(ex, ey, r * 2.4, r * 2.0, s)
            spikes(f, arc(ex, ey, r * 2.4, r * 2.0, 180, 360, 6), r * 1.6, r * 1.4, s=0, side=1)
        elif kind == "leaf":
            leaf(f, ex - 1, ey + 1, r * 6, r * 2.3, ang, s=tip if tip is not None else 1)
        elif kind == "bolt":
            zz = [(0, -r), (r * 2, -r * 3), (r * 1.5, -r * 1), (r * 4, -r * 2), (r * 1.5, r * 1.5), (r * 2, 0)]
            f.poly(rot(zz, ang + 30, ex - r, ey), tip if tip is not None else 1)
    elif kind in ("bushy", "fox"):
        cx, cy = x + math.cos(a) * ln * 0.55, y + math.sin(a) * ln * 0.55
        out["id"] = f.ell(cx, cy, ln * 0.6, r, s, ang=ang, **k)
        if kind == "fox" or tip is not None:
            f.mark_ell(x + math.cos(a) * ln * 1.0, y + math.sin(a) * ln * 1.0, ln * 0.25, r * 0.9, tip if tip is not None else 0, ang=ang, clip=out["id"])
    elif kind == "stub":
        out["id"] = f.ell(x + 2, y - 1, r * 1.3, r, s)
    elif kind == "three":
        for d in (-22, 0, 22):
            aa = a + math.radians(d)
            f.stroke([(x, y), (x + math.cos(aa) * ln * 0.6, y + math.sin(aa) * ln * 0.6 + 3), (x + math.cos(aa) * ln, y + math.sin(aa) * ln)],
                     r, r * 0.4, s)
            f.ell(x + math.cos(aa) * ln, y + math.sin(aa) * ln, r * 1.2, r * 1.6, 2, ang=math.degrees(aa) + 90)
    return out


def eyes2(f, hx, hy, hr, kind="dot", r=None, look=-1, two=True, dx=0.0, dy=0.0, spread=0.52, brow=0):
    r = r or max(2.6, hr * 0.26)
    e1 = (hx - hr * 0.18 + dx, hy - hr * 0.12 + dy)
    f.eye(e1[0], e1[1], r, kind, look, brow)
    if two:
        e2 = (hx - hr * (0.18 + spread) + dx, hy - hr * 0.16 + dy)
        f.eye(e2[0], e2[1], r * 0.85, kind, look, brow)


# ------------------------------------------------------------------ QUAD
def quad(f, **p):
    q = dict(bx=58, by=70, brx=24, bry=14, bs=1, tilt=0,
             hx=30, hy=48, hr=14, hry=None, hs=None,
             sn=0.0, snr=None, snd=0.25, nose=True,
             ll=None, lr=4.5, lg=None, paws=True, fs=None,
             neck=None, ears=None, er=8, ear_in=None, ear_ang=0,
             tail=None, tl=22, trr=3.0, tang=-50, ttip=None,
             eye="dot", eyer=None, two=True, look=-1, brow=0,
             mouth="smile", fangs=0, belly=None,
             pre=None, back=None, head=None, legs=4)
    q.update(p)
    bx, by, brx, bry, bs = q["bx"], q["by"], q["brx"], q["bry"], q["bs"]
    hs = q["hs"] if q["hs"] is not None else bs
    hr = q["hr"]
    hry = q["hry"] or hr * 0.92
    gy = 97
    fs = q["fs"] if q["fs"] is not None else bs
    _call(q["pre"], f, q)
    lx = [bx - brx * 0.55, bx + brx * 0.58]
    # far legs
    if q["legs"]:
        for x in lx:
            f.stroke([(x + 4, by), (x + 5, gy - 2)], q["lr"] * 0.9, q["lr"] * 0.8, 2, group="far")
    if q["tail"]:
        q["tailinfo"] = tail(f, q["tail"], bx + brx * 0.85, by - bry * 0.35, q["tl"], q["trr"], bs, q["tang"], q["ttip"])
    body = f.ell(bx, by, brx, bry, bs, ang=q["tilt"], group="body", hl=False)
    q["body"] = body
    if q["belly"] is not None:
        f.mark_ell(bx - brx * 0.1, by + bry * 0.75, brx * 0.75, bry * 0.5, q["belly"], clip=body)
    if q["legs"]:
        for x in lx:
            f.stroke([(x - 1, by + bry * 0.2), (x - 1, gy - 2)], q["lr"], q["lr"] * 0.85, fs, group="body")
            if q["paws"]:
                f.ell(x - 2.2, gy - 1.6, q["lr"] * 1.15, q["lr"] * 0.65, fs, group="body")
    _call(q["back"], f, q)
    nk = q["neck"]
    if nk is None:
        nk = hr * 0.55
    if nk:
        f.stroke([(bx - brx * 0.55, by - bry * 0.3), (q["hx"] + hr * 0.2, q["hy"] + hry * 0.2)], nk, nk * 0.9, hs, group="body")
    hx, hy = q["hx"], q["hy"]
    if q["ears"]:
        ears(f, q["ears"], hx - hr * 0.45, hy - hry * 0.7, q["er"] * 0.9, hs, far=True, ang=q["ear_ang"] - 15)
    head = f.ell(hx, hy, hr, hry, hs, group="head")
    q["headid"] = head
    if q["sn"]:
        snr = q["snr"] or hr * 0.48
        f.ell(hx - hr * 0.75 - q["sn"] * 0.3, hy + hry * q["snd"], q["sn"] * 0.55 + snr * 0.5, snr, hs, group="head")
        if q["nose"]:
            f.ell(hx - hr * 0.75 - q["sn"] * 0.85 - snr * 0.4, hy + hry * q["snd"] - snr * 0.45, 1.8, 1.4, 3, sh=0, face=True)
    if q["ears"]:
        ears(f, q["ears"], hx + hr * 0.25, hy - hry * 0.75, q["er"], hs, inner=q["ear_in"], ang=q["ear_ang"] + 10)
    _call(q["head"], f, q)
    ex = 0 if not q["sn"] else -hr * 0.18
    eyes2(f, hx, hy, hr, q["eye"], q["eyer"], q["look"], q["two"], dx=ex, brow=q["brow"])
    mx = hx - hr * 0.62 - q["sn"] * 0.6
    my = hy + hry * (0.45 if not q["sn"] else 0.55)
    if q["mouth"] == "smile":
        f.line([(mx - 2, my - 1), (mx + 2, my + 0.5), (mx + 5, my - 0.5)], 3, face=True)
    elif q["mouth"] == "open":
        f.poly([(mx - 3, my - 1.5), (mx + 5, my - 0.5), (mx + 1, my + 4)], 3, line=False, sh=0, face=True)
    elif q["mouth"] == "line":
        f.line([(mx - 2, my), (mx + 5, my)], 3, face=True)
    for i in range(q["fangs"]):
        fang(f, mx + i * 3.0 - 1, my - 0.2, 3.6, 2.6)
    return q


# ------------------------------------------------------------------ BIPED
def biped(f, **p):
    q = dict(tx=54, ty=62, trx=16, tr_y=20, bs=1, hs=None,
             hx=47, hy=30, hr=15, hry=None,
             sn=0, snr=None, legr=5.5, legx=6.5, legy=None, feet=True, fs=None, footl=1.0,
             arm="side", armr=4.0, hand=None, as_=None, far_arm=True,
             ears=None, er=8, ear_in=None, ear_ang=0,
             tail=None, tl=22, trr=3.5, tang=-30, ttip=None,
             eye="dot", eyer=None, two=True, look=-1, brow=0, mouth="smile", fangs=0,
             belly=None, neck=0, pre=None, back=None, head=None, front=None)
    q.update(p)
    tx, ty, trx, tr_y = q["tx"], q["ty"], q["trx"], q["tr_y"]
    bs = q["bs"]
    hs = q["hs"] if q["hs"] is not None else bs
    fs = q["fs"] if q["fs"] is not None else bs
    as_ = q["as_"] if q["as_"] is not None else bs
    hr = q["hr"]
    hry = q["hry"] or hr * 0.92
    gy = 97
    _call(q["pre"], f, q)
    if q["tail"]:
        q["tailinfo"] = tail(f, q["tail"], tx + trx * 0.7, ty + tr_y * 0.45, q["tl"], q["trr"], bs, q["tang"], q["ttip"])
    # far arm
    sx, sy = tx - trx * 0.15, ty - tr_y * 0.55
    arms = {
        "side": [(0, 0), (-trx * 0.5, tr_y * 0.45), (-trx * 0.75, tr_y * 0.8)],
        "fwd": [(0, 0), (-trx * 0.8, tr_y * 0.25), (-trx * 1.25, tr_y * 0.05)],
        "up": [(0, 0), (-trx * 0.6, -tr_y * 0.3), (-trx * 0.8, -tr_y * 0.8)],
        "guard": [(0, 0), (-trx * 0.9, tr_y * 0.4), (-trx * 1.2, -tr_y * 0.1)],
        "hips": [(0, 0), (-trx * 0.75, tr_y * 0.3), (-trx * 0.35, tr_y * 0.6)],
    }
    path = arms.get(q["arm"], arms["side"])
    if q["far_arm"] and q["arm"]:
        fp = [(tx + trx * 0.55 + dx * 0.8, sy + 1 + dy * 0.9) for dx, dy in path]
        f.stroke(fp, q["armr"] * 0.9, q["armr"] * 0.8, 2, group="farm")
        if q["hand"]:
            f.ell(fp[-1][0], fp[-1][1], q["hand"] * 0.9, q["hand"] * 0.9, 2, group="farm")
    # legs
    ly = q["legy"] if q["legy"] is not None else ty + tr_y * 0.55
    for i, lx in enumerate((tx + q["legx"], tx - q["legx"])):
        sh = 2 if i == 0 else fs
        f.stroke([(lx, ly), (lx - 1, gy - 3)], q["legr"], q["legr"] * 0.9, sh, group="leg%d" % i)
        if q["feet"]:
            f.ell(lx - 3 * q["footl"], gy - 2, q["legr"] * 1.35 * q["footl"], q["legr"] * 0.7, sh, group="leg%d" % i)
    body = f.ell(tx, ty, trx, tr_y, bs, group="body")
    q["body"] = body
    if q["belly"] is not None:
        f.mark_ell(tx - trx * 0.3, ty + tr_y * 0.12, trx * 0.6, tr_y * 0.72, q["belly"], clip=body)
    _call(q["back"], f, q)
    hx, hy = q["hx"], q["hy"]
    if q["neck"]:
        f.stroke([(tx, ty - tr_y * 0.5), (hx, hy)], q["neck"], q["neck"], hs, group="body")
    if q["ears"]:
        ears(f, q["ears"], hx - hr * 0.45, hy - hry * 0.7, q["er"] * 0.9, hs, far=True, ang=q["ear_ang"] - 15)
    head = f.ell(hx, hy, hr, hry, hs, group="head")
    q["headid"] = head
    if q["sn"]:
        snr = q["snr"] or hr * 0.45
        f.ell(hx - hr * 0.75 - q["sn"] * 0.3, hy + hry * 0.25, q["sn"] * 0.55 + snr * 0.5, snr, hs, group="head")
    if q["ears"]:
        ears(f, q["ears"], hx + hr * 0.25, hy - hry * 0.75, q["er"], hs, inner=q["ear_in"], ang=q["ear_ang"] + 10)
    _call(q["head"], f, q)
    ex = 0 if not q["sn"] else -hr * 0.15
    eyes2(f, hx, hy, hr, q["eye"], q["eyer"], q["look"], q["two"], dx=ex, brow=q["brow"])
    mx = hx - hr * 0.55 - q["sn"] * 0.6
    my = hy + hry * 0.45
    if q["mouth"] == "smile":
        f.line([(mx - 2, my - 1), (mx + 2, my + 0.5), (mx + 5, my - 0.5)], 3, face=True)
    elif q["mouth"] == "open":
        f.poly([(mx - 3, my - 1.5), (mx + 5, my - 0.5), (mx + 1, my + 4)], 3, line=False, sh=0, face=True)
    elif q["mouth"] == "line":
        f.line([(mx - 2, my), (mx + 5, my)], 3, face=True)
    for i in range(q["fangs"]):
        fang(f, mx + i * 3.0 - 1, my - 0.2, 3.6, 2.6)
    # near arm
    if q["arm"]:
        npth = [(sx + dx, sy + dy) for dx, dy in path]
        f.stroke(npth, q["armr"], q["armr"] * 0.85, as_, group="arm")
        q["handpos"] = npth[-1]
        q["farhand"] = (tx + trx * 0.55 + path[-1][0] * 0.8, sy + 1 + path[-1][1] * 0.9)
        if q["hand"]:
            f.ell(npth[-1][0], npth[-1][1], q["hand"], q["hand"], as_, group="arm")
    _call(q["front"], f, q)
    return q


# ------------------------------------------------------------------ BIRD
def bird(f, **p):
    q = dict(bx=58, by=64, brx=21, bry=16, tilt=-18, bs=1, hs=None,
             hx=34, hy=40, hr=12, beak=8, beakw=5, beaks=0, hook=0, crest=None, cl=12,
             wing="fold", wl=26, ww=14, ws=None, wang=None, tailk="fan", tl=18, tw=10, ts=None,
             legs=True, legl=12, eye="dot", eyer=None, two=False, look=-1, brow=0,
             belly=None, neck=None, pre=None, back=None, head=None, fly=False)
    q.update(p)
    bx, by, brx, bry, bs = q["bx"], q["by"], q["brx"], q["bry"], q["bs"]
    hs = q["hs"] if q["hs"] is not None else bs
    ws = q["ws"] if q["ws"] is not None else (2 if bs < 2 else 1)
    ts = q["ts"] if q["ts"] is not None else ws
    hr = q["hr"]
    _call(q["pre"], f, q)
    if q["fly"]:   # far wing raised behind the body
        bird_wing(f, bx - 2, by - bry * 0.4, q["wl"] * 1.1, q["ww"], -125, n=4, s=2, group="farw")
    if q["legs"]:
        for dx, sh in ((4, 2), (-3, 3)):
            lx = bx + dx
            f.stroke([(lx, by + bry * 0.6), (lx - 1, by + bry * 0.6 + q["legl"])], 1.3, 1.1, 3, group="legs")
            ty = by + bry * 0.6 + q["legl"]
            f.stroke([(lx - 5, ty), (lx + 2, ty)], 1.1, 1.1, 3, group="legs")
    if q["tailk"]:
        tx = bx + brx * 0.8
        tyy = by + bry * 0.1
        if q["tailk"] == "fan":
            q["tailid"] = f.poly([(tx - 2, tyy - 4), (tx + q["tl"], tyy + q["tw"] * 0.1 - 4), (tx + q["tl"] * 1.05, tyy + q["tw"] * 0.6),
                                  (tx + q["tl"] * 0.8, tyy + q["tw"]), (tx - 3, tyy + 5)], ts)
        elif q["tailk"] == "long":
            q["tailid"] = f.poly([(tx - 2, tyy - 3), (tx + q["tl"], tyy + q["tl"] * 0.5), (tx + q["tl"] * 0.85, tyy + q["tl"] * 0.6 + q["tw"] * 0.5),
                                  (tx - 3, tyy + 6)], ts)
        elif q["tailk"] == "banner":
            pts = [(tx - 2, tyy - 3), (tx + q["tl"] * 0.6, tyy - 2), (tx + q["tl"], tyy - 6), (tx + q["tl"] * 0.9, tyy + q["tw"] * 0.4),
                   (tx + q["tl"] * 1.05, tyy + q["tw"]), (tx + q["tl"] * 0.5, tyy + q["tw"] * 0.7), (tx - 3, tyy + 6)]
            q["tailid"] = f.poly(pts, ts)
    body = f.ell(bx, by, brx, bry, bs, ang=q["tilt"], group="body")
    q["body"] = body
    if q["belly"] is not None:
        f.mark_ell(bx - brx * 0.35, by + bry * 0.3, brx * 0.62, bry * 0.65, q["belly"], ang=q["tilt"], clip=body)
    hx, hy = q["hx"], q["hy"]
    nk = q["neck"] if q["neck"] is not None else hr * 0.7
    if nk:
        f.stroke([(bx - brx * 0.5, by - bry * 0.3), (hx, hy)], nk, nk * 0.85, hs, group="body")
    _call(q["back"], f, q)
    if q["crest"]:
        c = q["crest"]
        cl = q["cl"]
        if c == "tuft":
            f.poly([(hx - 2, hy - hr * 0.8), (hx + cl * 0.6, hy - hr - cl * 0.9), (hx + cl * 0.35, hy - hr * 0.6), (hx + cl, hy - hr * 0.6 - cl * 0.4), (hx + hr * 0.7, hy - hr * 0.2)], hs)
        elif c == "plume":
            for i, a in enumerate((-70, -45, -20)):
                f.stroke([(hx + 2, hy - hr * 0.6), (hx + 2 + math.cos(math.radians(a)) * cl, hy - hr * 0.6 + math.sin(math.radians(a)) * cl)], 2.0, 1.0, 2 if i % 2 else hs)
        elif c == "spike":
            spikes(f, arc(hx, hy, hr, hr, 200, 330, 5), cl * 0.6, hr * 0.5, s=hs, side=1)
    head = f.ell(hx, hy, hr, hr * 0.95, hs, group="head")
    q["headid"] = head
    bk, bw = q["beak"], q["beakw"]
    if bk:
        bxx = hx - hr * 0.85
        pts = [(bxx + 2, hy - bw * 0.5), (bxx - bk, hy + q["hook"] * 0.5 + 1), (bxx + 2, hy + bw * 0.5 + 1)]
        if q["hook"]:
            pts = [(bxx + 2, hy - bw * 0.5), (bxx - bk, hy - bw * 0.1), (bxx - bk - 0.5, hy + q["hook"]), (bxx - bk * 0.6, hy + bw * 0.25), (bxx + 2, hy + bw * 0.5 + 1)]
        f.poly(pts, q["beaks"], group="beak")
    _call(q["head"], f, q)
    eyes2(f, hx + hr * 0.05, hy - 1, hr, q["eye"], q["eyer"], q["look"], q["two"], brow=q["brow"])
    if q["wing"] == "fold":
        wa = q["wang"] if q["wang"] is not None else 18
        q["wingid"] = bird_wing(f, bx - brx * 0.45, by - bry * 0.35, q["wl"], q["ww"], wa, n=4, s=ws, group="wing")
    elif q["wing"] == "up":
        wa = q["wang"] if q["wang"] is not None else -60
        q["wingid"] = bird_wing(f, bx - brx * 0.35, by - bry * 0.3, q["wl"] * 1.15, q["ww"] * 1.1, wa, n=5, s=ws, group="wing")
    return q


# ------------------------------------------------------------------ SERPENT
def serpent(f, path, r0, r1, bs=1, head=None, hr=None, hry=None, belly=None, bands=0, bandw=2.5, bands_s=2,
            eye="dot", eyer=None, look=-1, two=True, tongue=False, sn=0.0, jaw=False):
    body = f.stroke(path, r1, r0, bs, group="body")   # path from tail to head
    if bands:
        n = len(path)
        for i in range(bands):
            t = (i + 0.7) / (bands + 0.4)
            k = t * (n - 1)
            j = min(int(k), n - 2)
            u = k - j
            x = path[j][0] + (path[j + 1][0] - path[j][0]) * u
            y = path[j][1] + (path[j + 1][1] - path[j][1]) * u
            dx, dy = path[j + 1][0] - path[j][0], path[j + 1][1] - path[j][1]
            L = math.hypot(dx, dy) or 1
            rr = r1 + (r0 - r1) * t
            nx, ny = -dy / L * rr * 1.2, dx / L * rr * 1.2
            f.mark_stroke([(x - nx, y - ny), (x + nx, y + ny)], bandw * (0.6 + 0.4 * rr / r0), s=bands_s, clip=body)
    hx, hy = head or path[-1]
    hr = hr or r0 * 1.4
    hid = f.ell(hx, hy, hr * 1.15, hry or hr * 0.85, bs, group="head")
    if sn:
        f.ell(hx - hr * 0.9, hy + hr * 0.15, sn, hr * 0.5, bs, group="head")
    if tongue:
        tx = hx - hr * 1.15 - sn * 1.3
        f.line([(tx, hy + hr * 0.3), (tx - 5, hy + hr * 0.35), (tx - 7, hy + hr * 0.1)], 3, face=True)
        f.line([(tx - 5, hy + hr * 0.35), (tx - 7, hy + hr * 0.65)], 3, face=True)
    eyes2(f, hx + hr * 0.1, hy - hr * 0.1, hr, eye, eyer, look, two)
    if jaw:
        f.line([(hx - hr * 1.1 - sn, hy + hr * 0.35), (hx - hr * 0.1, hy + hr * 0.3)], 3, face=True)
    return body, hid
