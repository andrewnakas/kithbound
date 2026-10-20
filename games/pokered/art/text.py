"""Typesetting on pictures: proportional text in our 5x7 font or in 3x5 small capitals.

    ptext(canvas, "Red Version", x, y)              -> x after the text
    ptext(canvas, "KITH CREW", x, y, small=True)
    width("Red Version")                            -> pixels
"""
from games.pokered.art.font import G

S3 = {
    "A": "010/101/111/101/101", "B": "110/101/110/101/110", "C": "011/100/100/100/011",
    "D": "110/101/101/101/110", "E": "111/100/110/100/111", "F": "111/100/110/100/100",
    "G": "011/100/101/101/011", "H": "101/101/111/101/101", "I": "111/010/010/010/111",
    "J": "001/001/001/101/010", "K": "101/101/110/101/101", "L": "100/100/100/100/111",
    "M": "101/111/111/101/101", "N": "110/101/101/101/101", "O": "010/101/101/101/010",
    "P": "110/101/110/100/100", "Q": "010/101/101/111/011", "R": "110/101/110/101/101",
    "S": "011/100/010/001/110", "T": "111/010/010/010/010", "U": "101/101/101/101/111",
    "V": "101/101/101/101/010", "W": "101/101/111/111/101", "X": "101/101/010/101/101",
    "Y": "101/101/010/010/010", "Z": "111/001/010/100/111",
    "0": "111/101/101/101/111", "1": "010/110/010/010/111", "2": "110/001/010/100/111",
    "3": "110/001/010/001/110", "4": "101/101/111/001/001", "5": "111/100/110/001/110",
    "6": "011/100/111/101/111", "7": "111/001/010/010/010", "8": "111/101/111/101/111",
    "9": "111/101/111/001/110", ".": "0/0/0/0/1", "'": "1/1/0/0/0", " ": "00/00/00/00/00",
    "-": "000/000/111/000/000", "!": "1/1/1/0/1", "?": "110/001/010/000/010", ":": "0/1/0/1/0",
}


def _glyph(ch, small):
    if small:
        rows = S3[ch].split("/")
    elif ch == " ":
        rows = ["00"]
    else:
        rows = G[ch].split("/")
        used = [i for i in range(5) if any(r[i] == "1" for r in rows)]
        rows = [r[used[0]:used[-1] + 1] for r in rows]          # trim side bearings
    return rows


def width(s, small=False, gap=1):
    return sum(len(_glyph(c, small)[0]) + gap for c in s) - gap


def ptext(c, s, x, y, shade=3, small=False, gap=1):
    """Draw on a tilekit canvas (or anything with px(x, y, shade))."""
    for ch in s:
        rows = _glyph(ch, small)
        for j, r in enumerate(rows):
            for i, v in enumerate(r):
                if v == "1":
                    c.px(x + i, y + j, shade)
        x += len(rows[0]) + gap
    return x
