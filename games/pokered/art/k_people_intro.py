"""KITHBOUND intro / player pictures: ARLO (player), his back view, OLD HOLT's back view,
the unidentified tower ghost, and the intro creatures QUILLORD, TUNEPUFF and NIGHTGRIN.
All shapes are our own designs (see world.py ROSTER concepts).
"""
import numpy as np

from cleanroom.gb import gfx
from games.pokered import drawn
from games.pokered.art.k_people_gear import goggles, scarf, strap, collar_high, zipline, snare, belt
from games.pokered.art.k_people_kit import FULL, Fig, _edge

# ------------------------------------------------------------------ ARLO, the player
ARLO = dict(rig=FULL, hair="tuft", hairc=2, eyes="big", mouth="smile", top=1, sleevec=2, cuff=3,
            arms=("hold", "hip"), pants=2, shoes=3, face=[goggles(c=1)], collar=[scarf(c=0, tail=False)],
            outfit=[strap(c=3, w=0.9)], rigmod=dict(cy=11.5, neck=(19.5, 22.5), shy=23), top_layers=[snare()])
ARLO_TITLE = dict(ARLO, arms=("wave", "hip"))


def arlo_back(w=32, h=32):
    """Back view, head and shoulders, seen over the shoulder in battle."""
    f = Fig(w, h)
    # arms + jacket
    f.part(f.cap([(6, 25), (3, 33)], 3.4), 2)
    f.part(f.cap([(26, 25), (29, 33)], 3.4), 2)
    body = f.P([(9, 19), (23, 19), (28, 24), (30, 33), (2, 33), (4, 24)]) | f.E(7, 25, 4, 4) | f.E(25, 25, 4, 4)
    f.part(body, 1)
    f.part(f.cap([(25, 21), (8, 33)], 1.1) & body, 3, shadow=False)          # satchel strap
    f.line([(16, 24), (16, 32)], 2)                                          # back seam
    # neck + scarf
    f.part(f.R(12, 15, 20, 21), 0)
    f.part(f.E(16, 20, 8.5, 2.8), 0)
    f.part(f.cap([(20, 21), (23, 26), (22, 30)], 1.8, 1.4), 0)
    # head: hair from behind, ears, goggle strap
    f.part(f.E(7.5, 12, 1.8, 2.4) | f.E(24.5, 12, 1.8, 2.4), 0, shadow=False)
    head = f.E(16, 10.5, 8.2, 8.6)
    for a, b in (((10, 4), (6, 0)), ((15, 2.5), (14, -2)), ((20, 3.5), (24, -0.5)), ((23, 7), (28, 4))):
        head |= f.P([(a[0] - 2.5, a[1] + 1.5), b, (a[0] + 2.5, a[1] + 1.5)])
    head |= f.P([(10, 16), (16, 20), (22, 16), (22, 14), (10, 14)])
    f.part(head, 2)
    for x0 in (11, 15, 19):
        f.line([(x0, 4), (x0 + 1, 9)], 3)
    for x0 in (9, 13, 17, 21):
        f.line([(x0, 12), (x0 + 1, 16)], 1)
    f.flat(f.R(7.5, 10, 24.5, 11) & f.E(16, 10.5, 8.6, 9), 3)                 # goggle strap
    f.stamp("####/#--#/####", 16, 10.5)
    f.outline_all()
    return f.a


def holt_back(w=32, h=32):
    """OLD HOLT from behind: bald crown, white fringe, round shoulders, striped shawl."""
    f = Fig(w, h)
    f.part(f.cap([(5, 24), (2, 33)], 3.2), 2)
    f.part(f.cap([(27, 24), (30, 33)], 3.2), 2)
    body = f.P([(8, 20), (24, 20), (29, 25), (31, 33), (1, 33), (3, 25)]) | f.E(6, 25, 4.5, 4.5) | f.E(26, 25, 4.5, 4.5)
    f.part(body, 2)
    shawl = f.P([(6, 20), (26, 20), (27, 25), (16, 30), (5, 25)])
    f.part(shawl, 1)
    f.stripes(shawl & ~_edge(shawl), 2, gap=3, dirn=(0, 1))
    f.part(f.R(12, 16, 20, 21), 0)
    f.part(f.E(8.5, 13.5, 1.8, 2.6) | f.E(23.5, 13.5, 1.8, 2.6), 0, shadow=False)
    f.part(f.E(16, 12, 7.6, 8.0), 0)                                         # bald head (lit crown)
    f.flat(f.E(18.5, 14.5, 4.5, 4.5) & ~_edge(f.E(16, 12, 7.6, 8.0)), 1)
    f.px(13, 7, 1); f.px(12, 8, 1)
    fringe = f.E(16, 12, 8.4, 8.6) & ~f.E(16, 9.5, 7.4, 7.2) & (f.Y > 10)
    f.part(fringe, 1)
    f.dither(fringe & ~_edge(fringe), 0)
    f.outline_all()
    return f.a


# ------------------------------------------------------------------ tower ghost
def ghost(w=48, h=48):
    """An unidentified shade: a hooded wisp leaning in, hollow eyes, ragged trailing hem."""
    f = Fig(w, h)
    body = f.E(25, 15, 11, 11.5)
    body |= f.P([(14, 16), (36, 15), (39, 28), (45, 37), (40, 46), (34, 40), (29, 47), (23, 40), (16, 46), (13, 37), (9, 30)])
    body |= f.P([(26, 3), (33, 0), (36, 9)])                                 # hood tip
    arm = f.cap([(14, 24), (7, 27), (3, 33), (5, 38)], 3.2, 1.0)
    f.part(arm, 3, hl=False)
    f.part(body, 3, hl=False)
    soft = drawn.blur(body, 3)
    yy, xx = np.mgrid[0:h, 0:w]
    glow = body & ~_edge(body) & (yy < 30) & (xx < 30)
    f.a[glow & ((xx + yy) % 2 == 0) & (soft > 0.9)] = 2
    f.a[body & ~_edge(body) & (xx + 2 * yy > 60) & ((xx + yy) % 4 == 0)] = 2
    # hollow eyes and mouth
    for cx, cy in ((19.5, 15), (28, 14)):
        f.part(f.E(cx, cy, 2.4, 3.6), 0, line=None, shadow=False)
        f.px(cx, cy + 1, 1)
    f.part(f.E(23, 23, 2.2, 1.6), 1, line=None, shadow=False)
    f.outline_all()
    return f.a


# ------------------------------------------------------------------ QUILLORD (hedgehog, horned brow), facing right
def quillord(pose):
    f = Fig(48, 48, open_bottom=False)
    if pose == 1:
        f.pose(0)
        legs = (((30, 35), (32, 43)), ((26, 35), (25, 43)), ((15, 35), (13, 43)), ((19, 35), (20, 43)))
    elif pose == 2:
        f.pose(0, sx=1.08, sy=0.82, px=24, py=44)
        legs = (((31, 35), (35, 42)), ((27, 35), (29, 43)), ((15, 35), (10, 42)), ((19, 35), (15, 43)))
    else:
        f.pose(-22, px=24, py=30, ty=-6)
        legs = (((31, 35), (41, 37)), ((27, 36), (36, 41)), ((15, 35), (5, 39)), ((19, 36), (9, 43)))
    # far legs first
    for (a, b) in (legs[1], legs[2]):
        f.part(f.cap([a, b], 2.4, 2.0), 2)
    # quill mantle behind the body
    quills = np.zeros((48, 48), bool)
    for i in range(9):
        t = i / 8
        bx, by = 9 + t * 24, 30 - np.sin(t * 3.1) * 9 - t * 2
        tip = (bx - 9 + t * 4, by - 9 + t * 1)
        quills |= f.P([(bx - 3, by + 2), tip, (bx + 3, by + 1)])
    f.part(quills, 2)
    f.part(f.E(22, 30, 13, 8.5), 1)
    f.flat(f.E(25, 34, 9, 3.6) & ~_edge(f.E(22, 30, 13, 8.5)), 0)            # pale belly
    for i in range(5):                                                       # quill lines over the back
        x = 12 + i * 4.5
        f.line([(x, 24 + abs(i - 2)), (x - 4, 19 + abs(i - 2))], 3)
    for (a, b) in (legs[0], legs[3]):
        f.part(f.cap([a, b], 2.6, 2.2), 1)
        f.part(f.E(b[0] + 0.8, b[1] + 0.5, 3.0, 1.8), 1)
    # head
    f.part(f.E(34, 26, 7.5, 6.8), 1)
    f.part(f.E(41, 28.5, 4.0, 2.8), 0)
    f.px(44.5, 27.5, 3); f.px(44.5, 28.2, 3)
    f.part(f.P([(31, 22), (40, 12), (37, 22)]), 3)                            # horned brow
    f.part(f.P([(28, 21), (25, 16), (31, 20)]), 2)                            # ear
    f.stamp("#  /##./###", 37, 25.5)                                          # fierce eye
    f.line([(39, 31), (42, 31)], 3)
    f.outline_all()
    return f.a


# ------------------------------------------------------------------ TUNEPUFF (round songbird-ball with a curl), facing right
def tunepuff(pose):
    f = Fig(48, 48, open_bottom=False)
    if pose == 1:
        f.pose(0)
    elif pose == 2:
        f.pose(0, sx=1.12, sy=0.84, px=24, py=44)
    else:
        f.pose(-12, px=24, py=28, ty=-5)
    for x0, x1 in ((20, 18), (28, 30)):                                       # feet
        f.part(f.cap([(x0, 38), (x1, 43)], 1.3), 2)
        f.line([(x1 - 2, 44), (x1 + 2, 44)], 3)
    tail = f.cap([(11, 28), (4, 22)], 2.2, 1.0) | f.cap([(11, 30), (3, 29)], 2.2, 1.0) | f.cap([(12, 32), (5, 36)], 2.0, 1.0)
    f.part(tail, 2)
    curl = f.cap([(23, 15), (22, 9), (25, 5), (30, 6), (31, 10), (28, 12), (26, 10)], 1.6, 1.0)
    f.part(curl, 2)
    body = f.E(24, 27, 14, 13)
    f.part(body, 0)
    f.flat(body & ~_edge(body) & ~f.E(27, 30, 10, 9) & ~f.E(19, 20, 7, 6), 1)  # soft shading on the back
    wing_up = pose == 3
    if wing_up:
        f.part(f.P([(14, 26), (8, 14), (19, 22)]) | f.E(15, 24, 4, 3.5), 1)
    else:
        f.part(f.E(17, 28, 5, 4.5) | f.P([(13, 29), (9, 37), (20, 31)]), 1)
        f.line([(15, 30), (12, 35)], 2)
    if pose == 3:
        f.part(f.P([(37, 24), (44, 21), (38, 26)]), 2)                        # open beak
        f.part(f.P([(37, 28), (43, 30), (37, 30)]), 2)
        f.stamp(" ##/ # /## ", 42, 12)                                        # a sung note
        f.stamp("  ##/  # / ## /### ", 44, 5)
    else:
        f.part(f.P([(37, 25), (43, 27.5), (37, 30)]), 2)
    if pose == 2:
        f.line([(27, 22), (29, 23), (31, 22)], 3); f.line([(32, 22), (34, 23), (35, 22)], 3)
    else:
        f.stamp(".#/##/##", 29.5, 22); f.stamp(".#/##/##", 34.5, 22)
    f.dither(f.E(33, 29, 2.6, 1.6), 1)
    f.outline_all()
    return f.a


def _open(m, r):
    """Morphological opening with a disc (rounds convex corners); outside the picture counts as inside."""
    offs = [(dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dy * dy + dx * dx <= r * r + 1]
    h, w = m.shape
    p = np.pad(m, r, constant_values=True)
    er = np.ones_like(m)
    for dy, dx in offs:
        er &= p[r + dy:r + dy + h, r + dx:r + dx + w]
    p = np.pad(er, r, constant_values=False)
    p[:r, :] = p[r:r + 1, :].any(0) & False
    out = np.zeros_like(m)
    for dy, dx in offs:
        out |= p[r + dy:r + dy + h, r + dx:r + dx + w]
    # keep the picture border open: anything touching it stays as it was
    out[-r:, :] |= m[-r:, :]
    return out


# ------------------------------------------------------------------ NIGHTGRIN (grinning shadow beast), three 56x56 poses
def nightgrin(a):
    """Three poses side by side. The build de-duplicates this picture's tiles (spec
    'classes'): blank-class tiles stay white, the solid-black class stays black, and the
    intro uses tile 1 (second tile of the first column) as its letterbox black."""
    h, w = a["h"], a["w"]
    cls = a["classes"]
    W = w // 8
    from collections import Counter
    cnt = Counter(cls)
    blank_c = cls[0]
    black_c = cls[W]                       # tile 1: the letterbox tile
    allowed = np.zeros((h, w), bool)
    black = np.zeros((h, w), bool)
    for i, c in enumerate(cls):
        ty, tx = (i // W) * 8, (i % W) * 8
        if c != blank_c and i != W:
            allowed[ty:ty + 8, tx:tx + 8] = True
        if c == black_c:
            black[ty:ty + 8, tx:tx + 8] = True
    black[8:16, 0:8] = False
    out = np.zeros((h, w), np.uint8)
    feats = [
        # (panel, head centre, grin width, eye y offset, horns)
        dict(head=(14, 22), lean=-1, claws=[(3, 22), (3, 38)], fin=(44, 10)),
        dict(head=(38, 12), lean=0, gw=7, claws=[(4, 26), (4, 44)], fin=None),
        dict(head=(26, 19), lean=-1, claws=[(3, 30), (2, 42)], fin=None),
    ]
    yy, xx = np.mgrid[0:h, 0:56]
    for k, ft in enumerate(feats):
        x0 = k * 56
        al = allowed[:, x0:x0 + 56]
        bl = black[:, x0:x0 + 56]
        # our blobby beast: the allowed tile area, rounded off, with our own spikes and grin
        body = _open(al, 5) & al
        # tiles the rounding emptied become horns / ears (they must stay drawn)
        for i, c in enumerate(cls):
            ty, tx = (i // W) * 8, (i % W) * 8 - x0
            if not (0 <= tx < 56) or c in (blank_c, black_c) or i == W:
                continue
            if body[ty:ty + 8, tx:tx + 8].sum() < 14:
                hm = np.zeros_like(body)
                yy2, xx2 = np.mgrid[0:h, 0:56]
                lean = 2 if tx > 28 else -2
                apex = (tx + 4 + lean, ty)
                tri = (yy2 >= ty) & (yy2 < ty + 8) & (np.abs(xx2 + 0.5 - (apex[0] + (yy2 - ty) * -lean / 8)) <= (yy2 - ty + 1) * 0.5)
                body |= tri & al
        f = Fig(56, h, open_bottom=True)
        f.m = body.copy()
        f.a[body] = 3
        # spines along the top edge (inside the allowed tiles)
        top = body & ~np.roll(body, 1, axis=0)
        for x in range(2, 54, 5):
            ys = np.nonzero(top[:, x])[0]
            if len(ys):
                y = ys[0]
                spike = f.P([(x - 2, y + 2), (x + 1, y - 4), (x + 3, y + 2)]) & al
                f.a[spike] = 3; f.m |= spike
        # grey sheen on the upper-left of the body, mottled lower down
        inner = f.m & ~_edge(f.m, True)
        d = drawn.depth_map(f.m)
        f.a[inner & (d <= 3) & ((xx + yy) % 2 == 0) & (yy < 40)] = 2
        f.a[inner & ((((xx * 7 + yy * 13) ^ (xx * yy)) % 17) == 0)] = 2
        # face
        hx, hy = ft["head"]
        for ex, ey, sgn in ((hx - 5, hy - 2.5, 1), (hx + 5, hy - 3, -1)):
            eye = f.P([(ex - 3.5, ey - 1.5 * sgn), (ex + 3.5, ey + 1.5 * sgn), (ex + 1, ey + 2.2), (ex - 2.5, ey + 1.5)])
            f.a[eye] = 0
            f.px(ex + ft["lean"], ey + 0.8, 3); f.px(ex + ft["lean"], ey + 1.6, 3)
        gw = ft.get("gw", 11)
        grin = f.P([(hx - gw, hy + 3), (hx + gw, hy + 2), (hx + gw * 0.65, hy + 9), (hx - gw * 0.55, hy + 9)])
        f.a[grin & f.m] = 0
        for gx in range(int(hx - gw + 2), int(hx + gw - 1), 3):              # teeth gaps
            f.line([(gx, hy + 3), (gx + 1, hy + 9)], 2)
        f.a[_edge(grin) & f.m] = 3
        for cx, cy in ft["claws"]:
            for dy in (-3, 0, 3):
                f.line([(cx + 4, cy + dy - 1), (cx + 1, cy + dy), (cx, cy + dy + 2)], 2)
                f.px(cx, cy + dy + 2, 0)
        f.a[_edge(f.m, True)] = 3
        p = f.a.copy()
        p[~al] = 0
        p[bl] = 3
        out[:, x0:x0 + 56] = p
    out[8:16, 0:8] = 3
    # tiles that must be equal (other than blank/black) get the first one's pixels
    t = gfx.tiles(out).copy()
    first = {}
    for i, c in enumerate(cls):
        if c in (blank_c, black_c):
            continue
        if c in first and cnt[c] > 1:
            t[i] = t[first[c]]
        first.setdefault(c, i)
    return gfx.untile(t, w)[:h]
