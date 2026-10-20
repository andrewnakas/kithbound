"""Scan a built ROM for old words: decode every byte run through the game's
charmap (and plain ASCII) and look for each retail name / banned word.

    python -m games.pokered.romscan <tree> <rom> [names.json]
"""
import json
import re
import sys

from games.pokered import textx


def charmap(tree):
    m = {}
    for line in open(f"{tree}/constants/charmap.asm", encoding="utf8"):
        g = re.match(r'\s*charmap\s+"([^"]+)",\s*\$([0-9a-fA-F]+)', line)
        if g and len(g.group(1)) == 1 and int(g.group(2), 16) not in m:
            m[int(g.group(2), 16)] = g.group(1)
    return m


def main(argv):
    tree, rom = argv[1], argv[2]
    names = json.load(open(argv[3] if len(argv) > 3 else textx.ORIG + "/names.json", encoding="utf8"))
    data = open(rom, "rb").read()
    cm = charmap(tree)
    dec = "".join(cm.get(b, "\x00") for b in data)
    asc = "".join(chr(b) if 32 <= b < 127 else "\x00" for b in data)
    words = [k for k in names if len(re.sub(r"[^A-Za-z]", "", k)) >= 4] + json.load(open(textx.ORIG + "/banned_words.json")).get("words", [])
    hits = []
    for w in sorted(set(words)):
        for src, s in (("charmap", dec), ("ascii", asc)):
            for m in re.finditer(r"(?<![A-Z])" + re.escape(w.upper()) + r"(?![A-Z])", s.upper()):
                hits.append((w, src, m.start()))
    print(f"romscan: {rom}: {len(hits)} old words")
    for w, src, a in hits[:30]:
        print(f"  {w!r} ({src}) at 0x{a:05X}: {(dec if src == 'charmap' else asc)[max(0, a - 12):a + 20]!r}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
