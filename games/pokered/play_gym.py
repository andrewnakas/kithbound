"""Headless playthrough to the first badge on the new maps (PyBoy + BFS on the clean
tree's collision data). Test-only help: after the starter is chosen the party's first
kith gets strong stats and full PP via WRAM writes (the ROM is untouched), so battles
end quickly; the route, scripts, warps and gym are played for real.

    python -m games.pokered.play_gym <rom> <clean tree> <out.png>

Route: new game -> starter + rival -> GREYWICK supply (parcel) -> back to the lab
(KITHLOG) -> PATH 2 -> TANGLEWOOD -> FLINTON -> gym trainers -> leader -> badge.
"""
import sys
from collections import deque

from PIL import Image, ImageDraw

from games.pokered.play_test import Player, sym


def sym_cache(p):
    if not hasattr(p, "_ev"):
        p._ev = p.sym1("wEventFlags")
    return p._ev


class GymPlayer(Player):
    def __init__(self, rom, tree):
        super().__init__(rom, tree)
        names = ["wPartyMon1Level", "wPartyMon1HP", "wPartyMon1MaxHP", "wPartyMon1Attack", "wPartyMon1Defense",
                 "wPartyMon1Speed", "wPartyMon1Special", "wPartyMon1PP", "wObtainedBadges", "wPartyCount"]
        self.A = dict(zip(names, sym(rom, *names)))
        import json, os
        self.spec = json.load(open(os.path.join(os.path.dirname(__file__), "spec", "maps.json")))["maps"]
        self.last_outdoor = None
        self.rom = rom
        self.log = []

    def flag(self, n):
        base = sym_cache(self)
        return (self.pb.memory[base + n // 8] >> (n % 8)) & 1

    def boost(self):
        m = self.pb.memory
        A = self.A
        if m[A["wPartyCount"]] == 0:
            return
        m[A["wPartyMon1Level"]] = 45
        ex = self.sym1("wPartyMon1Exp")                  # matching experience, or the next level-up resets it
        for i, v in enumerate((125000 >> 16, (125000 >> 8) & 0xFF, 125000 & 0xFF)):
            m[ex + i] = v
        for k, v in (("wPartyMon1MaxHP", 250), ("wPartyMon1HP", 250), ("wPartyMon1Attack", 220),
                     ("wPartyMon1Defense", 200), ("wPartyMon1Speed", 220), ("wPartyMon1Special", 200)):
            m[A[k]] = v >> 8
            m[A[k] + 1] = v & 0xFF
        m[self.sym1("wPartyMon1Moves")] = 0x22          # test aid: a plain full-power move in slot 1
        for i in range(4):
            m[A["wPartyMon1PP"] + i] = 30
        m[self.sym1("wRepelRemainingSteps")] = 250      # test aid: no wild encounters on the way

    def debug_tiles(self):
        tm = self.sym1("wTileMap")
        m = self.pb.memory
        _, px, py = self.pos()
        mp = self.mapobj()
        b = self.kit.blocks(mp)
        out = []
        for dy in (-2, -1, 0, 1, 2):
            row_s, row_e = [], []
            for dx in (-2, -1, 0, 1, 2):
                sx, sy = 8 + 2 * dx, 9 + 2 * dy        # bottom-left tile of each 16x16 cell on screen
                row_s.append("%02x" % m[tm + sy * 20 + sx] if 0 <= sy < 18 and 0 <= sx < 20 else "--")
                x, y = px + dx, py + dy
                ok = 0 <= x < mp.w * 2 and 0 <= y < mp.h * 2
                row_e.append("%02x" % self.kit.step_tile(mp.tileset, b, x, y) if ok else "--")
            out.append(" ".join(row_s) + "   |   " + " ".join(row_e))
        self.log.append("screen | expected at " + str((px, py)) + "\n" + "\n".join(out))

    def sym1(self, name):
        return sym(self.rom, name)[0]

    def fight(self, limit=1500):
        """mash through a battle (FIGHT, first move; B declines move learning / nicknames)."""
        n = 0
        while self.pb.memory[self.BATTLE] and n < limit:
            self.press("a", 4, 20)
            n += 1
            if getattr(self, "watch", False) and n % 12 == 0 and len(self.shots) < 40:
                self.shot(f"battle {n}")
            if n % 9 == 0:
                self.press("b", 4, 20)
        self.mash(8, "b", 30)
        self.boost()
        return n < limit

    # --- routing between maps -------------------------------------------------
    def neighbours(self, label):
        mp = self.kit.maps[label]
        out = []
        for d, lab, c, off in mp.connections:
            out.append((lab, ("edge", d)))
        for (x, y, dest, i) in mp.warps:
            if dest == "LAST_MAP":
                parents = [l for l, m2 in self.kit.maps.items() if any(w[2] == mp.const for w in m2.warps)]
                for p in parents:
                    out.append((p, ("warp", (x, y))))
            elif dest in self.by_const:
                out.append((self.by_const[dest].label, ("warp", (x, y))))
        return out

    def reachable_hop(self, how):
        mp = self.mapobj()
        if how[0] == "warp":
            t = how[1]
            return self.route(lambda p: p == t) is not None
        W, H = mp.w * 2, mp.h * 2
        edge = {"north": lambda p: p[1] == 0, "south": lambda p: p[1] == H - 1,
                "west": lambda p: p[0] == 0, "east": lambda p: p[0] == W - 1}[how[1]]
        return self.route(edge) is not None

    def plan(self, start, goal):
        prev, q = {start: None}, deque([start])
        while q:
            c = q.popleft()
            if c == goal:
                break
            for n, how in self.neighbours(c):
                if c == start and not self.reachable_hop(how):
                    continue                     # that exit is in a part of the map we cannot walk to
                if n not in prev:
                    prev[n] = (c, how)
                    q.append(n)
        if goal not in prev:
            return None
        path, c = [], goal
        while prev[c] is not None:
            p, how = prev[c]
            path.append((p, how, c))
            c = p
        return path[::-1]

    def travel(self, goal, tries=12):
        for _ in range(tries):
            cur = self.mapobj().label
            if cur == goal:
                return True
            hops = self.plan(cur, goal)
            if not hops:
                self.log.append(f"no plan {cur} -> {goal}")
                return False
            _, how, nxt = hops[0]
            m0 = self.pos()[0]
            if how[0] == "warp":
                tx, ty = how[1]
                self.go(lambda p: p == (tx, ty), f"warp in {cur}")
                if self.pos()[0] == m0:
                    _, wx, wy = self.pos()
                    mpw = self.mapobj()
                    first = ("up" if wy == 0 else "down" if wy == mpw.h * 2 - 1 else "left" if wx == 0 else
                             "right" if wx == mpw.w * 2 - 1 else "down")
                    for d in [first] + [d for d in ("down", "up", "left", "right") if d != first]:
                        self.press(d, 16, 40)
                        if self.pos()[0] != m0:
                            break
            else:
                d = how[1]
                mp = self.mapobj()
                W, H = mp.w * 2, mp.h * 2
                ops = {(o[0], o[1]) for o in self.spec.get(cur, {}).get("openings", {}).get(d, [])}
                edge = {"north": lambda p: p[1] == 0, "south": lambda p: p[1] == H - 1,
                        "west": lambda p: p[0] == 0, "east": lambda p: p[0] == W - 1}[d]
                if ops and self.route(lambda p: p in ops) is not None:
                    self.go(lambda p: p in ops, f"opening {d} of {cur}")
                else:
                    self.go(edge, f"edge {d} of {cur}")
                key = {"north": "up", "south": "down", "west": "left", "east": "right"}[d]
                for _ in range(3):
                    self.press(key, 12, 30)
                    if self.pos()[0] != m0:
                        break
            self.pb.tick(60, False)
            if self.pb.memory[self.BATTLE]:
                self.fight()
            self.mash(4, "b", 20)
        return self.mapobj().label == goal

    def go(self, goal_fn, label="", tries=12):
        self.blocked = set()                 # people move: forget old roadblocks
        for _ in range(tries):
            ok = super().go(goal_fn, label, tries=1)
            if self.pb.memory[self.BATTLE]:
                self.fight()
                self.blocked = set()         # the step was cut short by a battle, not a person
                continue
            if ok:
                return True
            self.mash(3, "b", 20)
        return False

    def talk_to(self, obj_index, label):
        mp = self.mapobj()
        if obj_index >= len(mp.objects):
            return False
        ox, oy = mp.objects[obj_index][:2]
        for (dx, dy, face) in ((0, 1, "up"), (0, -1, "down"), (1, 0, "left"), (-1, 0, "right")):
            if self.go(lambda p: p == (ox + dx, oy + dy), label, tries=2):
                self.press(face, 4, 12)
                self.press("a", 4, 40)
                return True
        return False


def main(rom, tree, outp):
    P = GymPlayer(rom, tree)
    pb = P.pb
    step = lambda s: (P.shot(s), P.log.append(s))
    pb.tick(900, False); P.press("start"); pb.tick(100, False); P.press("start"); pb.tick(60, False)
    P.mash(110, "a", 36); P.mash(6, "b", 30)
    P.warp_to("REDS_HOUSE_1F"); P.warp_to("LAST_MAP")
    P.go(lambda p: p[1] <= 1, "north exit"); pb.tick(200, False)
    P.mash(150, "a", 40); P.mash(6, "b", 30)
    lab = P.mapobj()
    balls = [(x, y) for (x, y, sp, mv) in lab.objects if "BALL" in sp]
    bx, by = balls[0]
    P.go(lambda p: p == (bx, by + 1), "ball"); P.press("up", 6, 20); P.press("a", 4, 60)
    for k in range(5):
        P.mash(40, "a", 40); P.press("b", 4, 40)
        if k == 1:
            P.go(lambda p: p[1] >= P.pos()[2] + 2, "walk away")
        if pb.memory[P.BATTLE]:
            P.fight()
    P.boost()
    step("starter + rival done")
    P.mash(30, "a", 40); P.mash(6, "b", 30)
    for goal in ("ViridianCity", "ViridianMart"):
        P.travel(goal)
    P.mash(40, "a", 40); P.mash(6, "b", 30)
    step(f"supply: parcel flag={P.flag(57)}")
    P.travel("OaksLab")
    oak = next((i for i, o in enumerate(P.mapobj().objects) if "OAK" in o[2]), 0)
    P.talk_to(oak, "professor")
    P.mash(120, "a", 40); P.mash(6, "b", 30)
    step(f"lab: KITHLOG flag={P.flag(37)} parcel delivered={P.flag(56)}")
    for goal in ("ViridianCity", "Route2", "ViridianForest", "PewterCity"):
        ok = P.travel(goal)
        step(f"reached {goal}" if ok else f"stuck before {goal}")
        if not ok:
            P.debug_tiles()
        P.mash(20, "a", 30); P.mash(6, "b", 30)
    P.travel("PewterGym")
    step("gym")
    gym = P.mapobj()
    for i in range(len(gym.objects) - 1, -1, -1):        # trainers first, the leader (object 0) last
        P.watch = (i == 0)
        t = P.talk_to(i, f"gym object {i}")
        fought = False
        for _ in range(30):
            P.press("a", 4, 30)
            if pb.memory[P.BATTLE]:
                fought = P.fight()
                break
        hp = pb.memory[P.A["wPartyMon1HP"]] * 256 + pb.memory[P.A["wPartyMon1HP"] + 1]
        P.log.append(f"gym object {i} {gym.objects[i][2]} at {gym.objects[i][:2]}: talked={t} battle_won={fought} hp={hp} pos={P.pos()}")
        P.mash(30, "a", 30); P.mash(6, "b", 30)
    P.mash(60, "a", 40)
    badge = pb.memory[P.A["wObtainedBadges"]] & 1
    step("BADGE 1 OBTAINED" if badge else "no badge")
    pb.stop(save=False)
    s, cols = 2, 5
    rows = (len(P.shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (160 * s + 4) + 4, rows * (144 * s + 18)), (40, 44, 60))
    d = ImageDraw.Draw(sheet)
    for n, (label, im) in enumerate(P.shots):
        x, y = 4 + (n % cols) * (160 * s + 4), (n // cols) * (144 * s + 18)
        sheet.paste(im.resize((160 * s, 144 * s), Image.NEAREST), (x, y + 14))
        d.text((x, y + 1), label, fill=(255, 230, 120))
    sheet.save(outp)
    print("\n".join(P.log))
    print("sheet ->", outp)
    return 0 if badge else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
