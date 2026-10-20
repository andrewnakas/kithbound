"""Art helper: draw a subset of pictures into a scratch tree, compare each with the
retail picture (originality images gate) and write one contact sheet.

    python -m games.pokered.imgcheck <scratch dir> "<pattern>" [sheet.png]
e.g.  python -m games.pokered.imgcheck D:/n64work/pokered/art_kith "pokemon/*" D:/n64work/pokered/sheets/kith.png
"""
import fnmatch
import json
import os
import sys

from cleanroom.gb import gfx
from cleanroom.originality import images
from cleanroom.originality.config import merged
from games.pokered import generate

PRISTINE = os.environ.get("POKERED_PRISTINE", "D:/n64work/pokered/pristine")


def main(argv):
    out, pat = argv[1], argv[2]
    generate.main(out, pat)
    spec = json.load(open(os.path.join(generate.HERE, "spec", "assets.json")))
    cfg = merged()["images"]
    from PIL import Image
    import numpy as np
    fails, items = [], []
    for rel in sorted(spec):
        if not fnmatch.fnmatch(rel, pat):
            continue
        c = np.asarray(Image.open(os.path.join(out, "gfx", rel)).convert("L"))
        r = np.asarray(Image.open(os.path.join(PRISTINE, "gfx", rel)).convert("L"))
        res = images.compare(r, c, cfg)
        if res["fail"]:
            fails.append((rel, res))
        items.append((os.path.basename(rel)[:-4][:12], gfx.read_png(os.path.join(out, "gfx", rel))))
    print(f"imgcheck {pat}: {len(items)} pictures, {len(fails)} too close to retail")
    for rel, r in fails[:25]:
        print(f"  FAIL {rel}: ssim {r['ssim']} phash {r['phash']} dhash {r['dhash']}")
    if len(argv) > 3:
        gfx.sheet(items, scale=2, cols=12).save(argv[3])
        print("  sheet ->", argv[3])
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
