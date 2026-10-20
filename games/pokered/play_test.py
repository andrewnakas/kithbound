"""Headless play test on the NEW maps: routes are planned with BFS over the clean
tree's own collision data (maps_kit), positions read from WRAM (.sym).

    python -m games.pokered.play_test <rom> <clean tree> <out.png>

Plays: title -> new game -> bedroom -> stairs -> front door -> home town -> north exit
(professor's cutscene) -> lab -> pick a starter -> rival battle -> out of the lab ->
north to the first route -> grass until a wild battle. One contact sheet.
"""
import os
import re
import sys
from collections import deque

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

from PIL import Image, ImageDraw
from pyboy import PyBoy

from games.pokered.maps_kit import Kit


def sym(rom, *names):
    out = {}
    for line in open(rom[:-4] + ".sym"):
        p = line.split()
        if len(p) == 2 and p[1] in names:
            out[p[1]] = int(p[0].split(":")[1], 16)
    return [out[n] for n in names]


class Player:
    def __init__(self, rom, tree):
        self.kit = Kit(tree)
        self.consts = re.findall(r"map_const\s+(\w+),", self.kit.read("constants/map_constants.asm"))
        self.by_const = {m.const: m for m in self.kit.maps.values()}
        self.X, self.Y, self.MAP, self.BATTLE = sym(rom, "wXCoord", "wYCoord", "wCurMap", "wIsInBattle")
        self.pb = PyBoy(rom, window="null", sound_emulated=False)
        self.pb.set_emulation_speed(0)
        self.shots = []
        self.blocked = set()

    def pos(self):
        m = self.pb.memory
        return m[self.MAP], m[self.X], m[self.Y]

    def mapobj(self):
        return self.by_const[self.consts[self.pos()[0]]]

    def shot(self, label):
        self.pb.tick(1, True)
        mp = self.mapobj()
        self.shots.append((f"{label}: {mp.label} {self.pos()[1:]}", self.pb.screen.image.convert("RGB").copy()))
        print(self.shots[-1][0], flush=True)

    def press(self, b, hold=8, wait=24):
        self.pb.button(b, hold)
        self.pb.tick(hold + wait, False)

    def walkable(self, mp):
        ts = self.kit.tilesets[mp.tileset]
        b = self.kit.blocks(mp)
        W, H = mp.w * 2, mp.h * 2
        return {(x, y) for y in range(H) for x in range(W) if self.kit.step_tile(mp.tileset, b, x, y) in ts.coll}

    def route(self, goal_fn):
        mp = self.mapobj()
        walk = self.walkable(mp)
        _, x0, y0 = self.pos()
        prev, q = {(x0, y0): None}, deque([(x0, y0)])
        while q:
            c = q.popleft()
            if goal_fn(c):
                path = [c]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                return path[::-1]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if n not in prev and n in walk and (mp.label, n) not in self.blocked:
                    prev[n] = c
                    q.append(n)
        return None

    def go(self, goal_fn, label="", tries=4):
        for _ in range(tries):
            path = self.route(goal_fn)
            m0 = self.pos()[0]
            if path is None:
                print(f"  no route for {label} on {self.mapobj().label} from {self.pos()[1:]}")
                return False
            for (x, y) in path[1:]:
                _, cx, cy = self.pos()
                d = "right" if x > cx else "left" if x < cx else "down" if y > cy else "up"
                self.press(d, 10, 14)
                if self.pos()[0] != m0 or self.pb.memory[self.BATTLE]:
                    return True
                if self.pos()[1:] != (x, y):
                    for _ in range(3):           # an NPC in the way: wait and retry
                        self.pb.tick(40, False)
                        self.press(d, 10, 14)
                        if self.pos()[1:] == (x, y):
                            break
                    if self.pos()[1:] != (x, y):
                        self.blocked.add((self.mapobj().label, (x, y)))   # someone stands there: route around
                        break
            if goal_fn(self.pos()[1:]) or self.pos()[0] != m0:
                return True
        print(f"  {label}: stopped at {self.pos()}")
        return False

    def warp_to(self, dest_const):
        mp = self.mapobj()
        ws = [(x, y) for (x, y, d, i) in mp.warps if d == dest_const or (dest_const == "LAST_MAP" and d == "LAST_MAP")]
        m0 = self.pos()[0]
        ok = self.go(lambda p: p in ws, f"warp {dest_const}")
        if self.pos()[0] == m0:
            _, wx, wy = self.pos()
            mpw = self.mapobj()
            first = ("up" if wy == 0 else "down" if wy == mpw.h * 2 - 1 else "left" if wx == 0 else
                     "right" if wx == mpw.w * 2 - 1 else "down")
            for d in [first] + [d for d in ("down", "up", "left", "right") if d != first]:  # door mats need a push out of the map
                self.press(d, 16, 40)
                if self.pos()[0] != m0:
                    break
        self.pb.tick(90, False)
        return self.pos()[0] != m0

    def mash(self, n, b="a", wait=40):
        for _ in range(n):
            self.press(b, 4, wait)


def main(rom, tree, outp):
    P = Player(rom, tree)
    pb = P.pb
    pb.tick(900, False); P.press("start"); pb.tick(100, False); P.press("start"); pb.tick(60, False)
    P.shot("title")
    P.mash(110, "a", 36); P.mash(6, "b", 30)
    P.shot("bedroom")
    P.warp_to("REDS_HOUSE_1F"); P.shot("downstairs")
    P.warp_to("LAST_MAP"); P.shot("outside")
    # north edge of the home town: the professor stops the player
    P.go(lambda p: p[1] <= 1, "north exit")
    pb.tick(200, False); P.shot("stopped")
    P.mash(150, "a", 40); P.mash(6, "b", 30)
    P.shot("lab")
    lab = P.mapobj()
    balls = [(x, y) for (x, y, sp, mv) in lab.objects if "BALL" in sp]
    if balls:
        bx, by = balls[0]
        P.go(lambda p: p == (bx, by + 1), "in front of a ball")
        P.press("up", 6, 20)
        P.press("a", 4, 60)
    P.shot("ball")
    for k in range(5):
        P.mash(40, "a", 40); P.press("b", 4, 40)
        if k == 1:
            P.go(lambda p: p[1] >= P.pos()[2] + 2, "walk away")
        P.shot(f"story{k}")
    P.mash(60, "a", 40); P.mash(6, "b", 30)
    P.warp_to("LAST_MAP"); P.shot("leave lab")
    P.go(lambda p: p[1] == 0, "to route 1")
    P.press("up", 16, 60); pb.tick(60, False); P.shot("route")
    # grass: walk back and forth on grass steps until a battle starts
    mp = P.mapobj()
    ts = P.kit.tilesets[mp.tileset]
    b = P.kit.blocks(mp)
    grass = {(x, y) for y in range(mp.h * 2) for x in range(mp.w * 2) if P.kit.step_tile(mp.tileset, b, x, y) == ts.grass}
    if grass:
        P.go(lambda p: p in grass, "grass")
        for i in range(80):
            if pb.memory[P.BATTLE]:
                break
            for d in ("up", "down", "left", "right"):
                x, y = P.pos()[1:]
                n = {"up": (x, y - 1), "down": (x, y + 1), "left": (x - 1, y), "right": (x + 1, y)}[d]
                if n in grass:
                    P.press(d, 10, 14)
                    break
        pb.tick(200, False)
    P.shot("wild battle" if pb.memory[P.BATTLE] else "no battle")
    P.mash(3, "a", 60)
    P.shot("battle menu")
    pb.stop(save=False)
    s, cols = 2, 6
    rows = (len(P.shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (160 * s + 4) + 4, rows * (144 * s + 18)), (40, 44, 60))
    d = ImageDraw.Draw(sheet)
    for n, (label, im) in enumerate(P.shots):
        x, y = 4 + (n % cols) * (160 * s + 4), (n // cols) * (144 * s + 18)
        sheet.paste(im.resize((160 * s, 144 * s), Image.NEAREST), (x, y + 14))
        d.text((x, y + 1), label, fill=(255, 230, 120))
    sheet.save(outp)
    print("sheet ->", outp)


if __name__ == "__main__":
    main(*sys.argv[1:4])
