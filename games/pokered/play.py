"""Headless run of a ROM in PyBoy: scripted buttons, screenshots on one sheet.

    python -m games.pokered.play <rom> <out.png> --keys "300:start,360:a,..." --shots 200,400,600 [--state in.state] [--save out.state]

keys: frame:button (a b start select up down left right), optional :frames held (default 6).
"mash:a:from:to:every" presses a button repeatedly.
"""
import argparse
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYBOY_NO_SOUND", "1")

from PIL import Image, ImageDraw
from pyboy import PyBoy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom"); ap.add_argument("out")
    ap.add_argument("--keys", default="")
    ap.add_argument("--shots", default="300")
    ap.add_argument("--state"); ap.add_argument("--save")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--scale", type=int, default=2)
    a = ap.parse_args()
    pb = PyBoy(a.rom, window="null", sound_emulated=False)
    pb.set_emulation_speed(0)
    if a.state:
        with open(a.state, "rb") as f:
            pb.load_state(f)
    ev = {}
    for k in filter(None, a.keys.split(",")):
        p = k.split(":")
        if p[0] == "mash":
            for t in range(int(p[2]), int(p[3]), int(p[4])):
                ev.setdefault(t, []).append((p[1], 4))
        else:
            ev.setdefault(int(p[0]), []).append((p[1], int(p[2]) if len(p) > 2 else 6))
    shots = [int(s) for s in a.shots.split(",")]
    imgs = []
    for f in range(max(shots) + 1):
        for b, d in ev.get(f, []):
            pb.button(b, d)
        pb.tick(1, f in shots)
        if f in shots:
            imgs.append((f, pb.screen.image.convert("RGB").copy()))
    if a.save:
        with open(a.save, "wb") as fh:
            pb.save_state(fh)
    pb.stop(save=False)
    s, cols = a.scale, min(a.cols, len(imgs))
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (160 * s + 4) + 4, rows * (144 * s + 14) + 4), (40, 44, 60))
    d = ImageDraw.Draw(sheet)
    for n, (f, im) in enumerate(imgs):
        x, y = 4 + (n % cols) * (160 * s + 4), 4 + (n // cols) * (144 * s + 14)
        sheet.paste(im.resize((160 * s, 144 * s), Image.NEAREST), (x, y + 10))
        d.text((x, y - 1), str(f), fill=(255, 230, 120))
    sheet.save(a.out)
    print(f"{len(imgs)} shots -> {a.out}")


if __name__ == "__main__":
    main()
