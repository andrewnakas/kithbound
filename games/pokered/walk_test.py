"""Scripted play test with position feedback (PyBoy + the build's .sym file).

    python -m games.pokered.walk_test <rom> <out.png>

New game, then waypoints (map coordinates read from wXCoord / wYCoord): Red's room ->
stairs -> front door -> Pallet Town -> north to the grass (Oak's cutscene). One contact
sheet of the stops; prints the map id and position at each.
"""
import os
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

from PIL import Image, ImageDraw
from pyboy import PyBoy


def sym(rom, *names):
    out = {}
    for line in open(rom[:-4] + ".sym"):
        p = line.split()
        if len(p) == 2 and p[1] in names:
            out[p[1]] = int(p[0].split(":")[1], 16)
    return [out[n] for n in names]


def main(rom, outp):
    X, Y, MAP = sym(rom, "wXCoord", "wYCoord", "wCurMap")
    pb = PyBoy(rom, window="null", sound_emulated=False)
    pb.set_emulation_speed(0)
    shots = []

    def pos():
        return pb.memory[MAP], pb.memory[X], pb.memory[Y]

    def shot(label):
        pb.tick(1, True)
        shots.append((f"{label} map {pos()[0]} at {pos()[1:]}", pb.screen.image.convert("RGB").copy()))
        print(shots[-1][0])

    def press(b, hold=8, wait=24):
        pb.button(b, hold)
        pb.tick(hold + wait, False)

    def goto(tx, ty, tries=60):
        m0 = pos()[0]
        for _ in range(tries):
            m, x, y = pos()
            if m != m0 or (x, y) == (tx, ty):
                return
            press("right" if x < tx else "left" if x > tx else "down" if y < ty else "up", 10, 14)
            if pos() == (m, x, y):               # blocked: try the other axis
                if y != ty:
                    press("down" if y < ty else "up", 10, 14)
                elif x != tx:
                    press("right" if x < tx else "left", 10, 14)
        print(f"  goto({tx}, {ty}) stopped at {pos()}")

    pb.tick(900, False); press("start"); pb.tick(100, False); press("start"); pb.tick(60, False)
    shot("title")
    for _ in range(110):                       # new game, Oak's speech, default names
        press("a", 4, 36)
    for _ in range(6):
        press("b", 4, 30)
    shot("bedroom")
    goto(5, 6); goto(5, 1); goto(7, 1); pb.tick(80, False); shot("downstairs")
    goto(7, 6); goto(3, 6); goto(3, 7); press("down", 20, 60); pb.tick(80, False); shot("outside")
    goto(5, 8); goto(10, 8); goto(10, 1); press("up", 20, 40)
    pb.tick(200, False); shot("grass")
    for _ in range(150):                       # Oak's cutscene up to "which POKeMON do you want?"
        press("a", 4, 40)
    for _ in range(6):
        press("b", 4, 30)
    shot("lab")
    goto(5, 4); goto(6, 4); press("up", 10, 20)
    press("a", 4, 60); shot("ball")
    for k in range(6):                         # dex entry, yes, nickname no, rival picks, rival battle
        for _ in range(40):
            press("a", 4, 40)
        press("b", 4, 40)
        if k == 1:
            goto(5, 6); goto(5, 8)             # walking away starts the rival battle
        shot(f"story{k}")
    pb.stop(save=False)
    s = 2
    cols = 7
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (160 * s + 4) + 4, rows * (144 * s + 18)), (40, 44, 60))
    d = ImageDraw.Draw(sheet)
    for n, (label, im) in enumerate(shots):
        x, y = 4 + (n % cols) * (160 * s + 4), (n // cols) * (144 * s + 18)
        sheet.paste(im.resize((160 * s, 144 * s), Image.NEAREST), (x, y + 14))
        d.text((x, y + 1), label, fill=(255, 230, 120))
    sheet.save(outp)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
