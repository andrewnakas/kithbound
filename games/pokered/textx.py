"""Text slots of the pokered tree: find, measure, validate and replace every
display string literal (dialogue, menus, names, dex entries).

Structure only is kept: which macro holds the string, its label, the order,
control tokens and the width budget. The words come from
games/pokered/text/new/*.json (our own writing, {id: text}).

    python -m games.pokered.textx scan <tree> <out.json>          (dirty room: slots + retail text)
    python -m games.pokered.textx packets <slots.json> <outdir>   (dirty room: writer packets, name-mapped)
    python -m games.pokered.textx check <slots.json>              (validate our writing; one screen)
    python -m games.pokered.textx apply <tree>                    (clean tree: write our strings in)
    python -m games.pokered.textx dump <tree> <out.json>          (strings per block, for the gate)

id = "<relpath>|<label>|<n>": n counts string pieces under the last label.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.join(HERE, "text", "new")

MACROS = ("text", "line", "cont", "para", "next", "page", "db", "li", "dname", "npctrade",
          "ld_hli_a_string", "dex")
BOX = {"text", "line", "cont", "para", "next", "page"}
SKIP_FILES = {"constants/charmap.asm", "data/text/dakutens.asm", "data/text/alphabets.asm"}
SKIP_DIRS = ("macros/",)
LINE_RE = re.compile(r'^(\s*)(?:[A-Za-z_.][\w.]*:+\s*)?(%s)\b(.*)$' % "|".join(MACROS))
EQUS_RE = re.compile(r'^\s*DEF\s+(PLAYERNAME\d|RIVALNAME\d)\s+EQUS\s+(".*")')
LABEL_RE = re.compile(r'^([A-Za-z_][\w]*)(:+)')
LOCAL_RE = re.compile(r'^(\.[\w]+):?')
STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')

# control tokens that must survive in order; '@' terminators included
KEEP = ["<SCROLL>", "<TARGET>", "<USER>", "<PAGE>", "<NEXT>", "<LINE>", "<PARA>", "<CONT>",
        "<_CONT>", "<DONE>", "<PROMPT>", "<DEXEND>", "@", "<NULL>"]
# tokens that print a word or name: width when shown
WIDE = {"<PLAYER>": 7, "<RIVAL>": 7, "#": 4, "<PKMN>": 2, "<PC>": 2, "<TM>": 2, "<TRAINER>": 5,
        "<ROCKET>": 5, "<TARGET>": 0, "<USER>": 0, "<……>": 2, "<LV>": 1, "<ID>": 1, "<to>": 1,
        "<ED>": 1, "<COLON>": 1, "<DOT>": 1}
TOKEN_RE = re.compile(r"<[^>]+>|'[dlstvrm]|.", re.S)


def tokens(s):
    return TOKEN_RE.findall(s)


def width(s):
    w = 0
    for t in tokens(s):
        if t in WIDE:
            w += WIDE[t]
        elif t.startswith("<") and len(t) > 1:
            w += 0 if t in KEEP else 1
        elif t == "@":
            pass
        else:
            w += 1
    return w


def controls(s):
    return [t for t in tokens(s) if t in KEEP]


def has_words(s):
    return re.search(r"[A-Za-z]{2,}|[぀-ヿ]", re.sub(r"<[^>]+>", "", s)) is not None


def files(tree):
    for p in sorted(glob.glob(os.path.join(tree, "**", "*.asm"), recursive=True)):
        rel = os.path.relpath(p, tree).replace("\\", "/")
        if rel in SKIP_FILES or rel.startswith(SKIP_DIRS) or rel.startswith("tools/"):
            continue
        yield rel, p


def scan_file(rel, path):
    out = []
    label, count = "_top", {}
    lines = open(path, encoding="utf8").read().split("\n")
    for ln, raw in enumerate(lines):
        code = raw
        m = LABEL_RE.match(code)
        if m:
            label = m.group(1)
        else:
            lm = LOCAL_RE.match(code)
            if lm:
                label = label.split(".")[0] + lm.group(1)
        semi = _comment_start(code)
        body = code[:semi]
        mm = LINE_RE.match(body)
        macro = None
        if mm:
            macro = mm.group(2)
        else:
            em = EQUS_RE.match(body)
            if em:
                macro = "equs"
        if not macro:
            continue
        for sm in STR_RE.finditer(body):
            s = sm.group(1)
            if macro not in ("equs",) and mm and sm.start() < mm.start(3):
                continue
            n = count.get(label, 0)
            count[label] = n + 1
            if not has_words(s):
                continue
            out.append({"id": f"{rel}|{label}|{n}", "file": rel, "line": ln, "span": [sm.start(1), sm.end(1)],
                        "macro": macro, "text": s})
    return out


def _comment_start(code):
    q = False
    for i, c in enumerate(code):
        if c == '"':
            q = not q
        elif c == ";" and not q:
            return i
    return len(code)


def scan(tree):
    out = []
    for rel, p in files(tree):
        out += scan_file(rel, p)
    budgets(out)
    return out


def budgets(slots):
    """Width budget per slot: text box lines 18; names and lists the table's widest
    retail entry; other db strings their own retail width (ending '@' may shrink,
    otherwise the width is exact so fixed records keep their stride)."""
    tmax, lmax, dmax = {}, {}, {}
    for s in slots:
        w = width(s["text"])
        if s["macro"] in ("li", "dname"):
            tmax[s["file"]] = max(tmax.get(s["file"], 0), w)
        k = (s["file"], s["id"].split("|")[1])
        lmax[k] = max(lmax.get(k, 0), w)
        if s["macro"] == "db" and s["text"].endswith("@"):
            dmax[s["file"]] = max(dmax.get(s["file"], 0), w)
    for s in slots:
        w = width(s["text"])
        menu = not s["file"].startswith(("text/", "data/text/", "data/pokemon/dex_text"))
        if menu and s["macro"] in BOX | {"db"}:
            # menus and screens: the box is as wide as the label's widest retail line
            lw = lmax[(s["file"], s["id"].split("|")[1])]
            if s["file"].startswith("data/") and s["macro"] == "db" and s["text"].endswith("@"):
                lw = max(lw, dmax[s["file"]])
            if s["file"] == "data/pokemon/dex_entries.asm":
                lw = 10
            s["budget"] = lw
            s["exact"] = s["macro"] == "db" and not s["text"].endswith("@") and \
                lmax[(s["file"], s["id"].split("|")[1])] == w and _alone(s, slots)
            continue
        if s["macro"] in BOX:
            s["budget"], s["exact"] = max(18, w), False
        elif s["macro"] in ("li", "dname"):
            s["budget"], s["exact"] = tmax[s["file"]], False
        elif s["macro"] in ("equs",):
            s["budget"], s["exact"] = 7, False
        elif s["macro"] == "npctrade":
            s["budget"], s["exact"] = 10, False
        else:
            ends = s["text"].endswith("@")
            s["budget"], s["exact"] = w, not ends
    for s in slots:
        for rx, b in OVERRIDE:
            if rx.search(s["id"]):
                s["budget"], s["exact"] = b, False


_LABEL_N = {}


def _alone(s, slots):
    """True when the slot is the only string under its label (a fixed field)."""
    if not _LABEL_N:
        for x in slots:
            k = (x["file"], x["id"].split("|")[1])
            _LABEL_N[k] = _LABEL_N.get(k, 0) + 1
    return _LABEL_N[(s["file"], s["id"].split("|")[1])] == 1


# buffers bigger than the retail string (engine facts): wGymCityName ds 17, wGymLeaderName ds NAME_LENGTH
OVERRIDE = [(re.compile(r"^scripts/\w+Gym\.asm\|.*\.CityName\|"), 16),
            (re.compile(r"^scripts/\w+Gym\.asm\|.*\.LeaderName\|"), 10)]


def load_new():
    new = {}
    for p in sorted(glob.glob(os.path.join(NEW, "**", "*.json"), recursive=True)):
        new.update(json.load(open(p, encoding="utf8")))
    return new


ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ()[]:;é'-?!./,♂♀×¥…“”‘’·▶▷▼▲#@′″")
_BW = os.path.join(os.environ.get("POKERED_ORIG", "D:/n64work/pokered/orig"), "banned_words.json")
BANNED = re.compile(json.load(open(_BW))["banned_re"] if os.path.exists(_BW) else r"(?!x)x", re.I)   # dirty side


def validate(slot, new):
    """-> list of problems for one rewrite."""
    errs = []
    for t in tokens(new):
        if t.startswith("<") and len(t) > 1:
            continue
        if t.startswith("'") and len(t) == 2:
            continue
        if t not in ALLOWED:
            errs.append(f"char {t!r}")
    if '"' in new or "\\" in new or "{" in new:
        errs.append("quote/brace/backslash")
    if controls(new) != controls(slot["text"]):
        errs.append(f"controls {controls(new)} != {controls(slot['text'])}")
    w = width(new)
    if w > slot["budget"]:
        errs.append(f"width {w} > {slot['budget']}")
    if slot.get("exact") and w != slot["budget"]:
        errs.append(f"width {w} must equal {slot['budget']} (pad with spaces)")
    if BANNED.search(new.replace("#", "")):
        errs.append("banned word")
    if "#" in new:
        errs.append("'#' prints the old creature word; write KITH")
    if re.search(r"<(PKMN|PK|MN)>", new):
        errs.append("<PKMN>/<PK><MN> glyphs are retired; write KITH")
    return errs


def apply(tree, new=None, slots=None):
    new = new if new is not None else load_new()
    slots = slots if slots is not None else scan(tree)
    byfile = {}
    for s in slots:
        if s["id"] in new:
            byfile.setdefault(s["file"], []).append(s)
    n = 0
    for rel, ss in byfile.items():
        p = os.path.join(tree, rel)
        lines = open(p, encoding="utf8").read().split("\n")
        for s in sorted(ss, key=lambda s: (s["line"], -s["span"][0])):
            a, b = s["span"]
            L = lines[s["line"]]
            lines[s["line"]] = L[:a] + new[s["id"]] + L[b:]
            n += 1
        open(p, "w", encoding="utf8", newline="\n").write("\n".join(lines))
    return n, len(slots)


def blocks(slots):
    """Join box pieces per label into one string (the gate compares whole speeches)."""
    out, cur, key = [], [], None
    for s in slots:
        k = (s["file"], s["id"].split("|")[1])
        if k != key and cur:
            out.append(" ".join(cur))
            cur = []
        key = k
        cur.append(s["text"])
    if cur:
        out.append(" ".join(cur))
    return out


def main(argv):
    cmd = argv[1]
    if cmd == "scan":
        slots = scan(argv[2])
        json.dump(slots, open(argv[3], "w", encoding="utf8"), ensure_ascii=False, indent=0)
        from collections import Counter
        print(f"{len(slots)} slots in {len({s['file'] for s in slots})} files;",
              dict(Counter(s["macro"] for s in slots)))
    elif cmd == "dump":
        slots = scan(argv[2])
        json.dump(blocks(slots), open(argv[3], "w", encoding="utf8"), ensure_ascii=False, indent=0)
        print(f"{len(slots)} slots -> {argv[3]}")
    elif cmd == "check":
        slots = json.load(open(argv[2], encoding="utf8"))
        new = load_new()
        ids = {s["id"] for s in slots}
        bad, missing = [], [s for s in slots if s["id"] not in new]
        for s in slots:
            if s["id"] in new:
                e = validate(s, new[s["id"]])
                if e:
                    bad.append((s["id"], e))
        extra = [k for k in new if k not in ids]
        print(f"text: {len(slots)} slots, {len(slots) - len(missing)} written, {len(missing)} missing, "
              f"{len(bad)} invalid, {len(extra)} unknown ids")
        for i, e in bad[:int(argv[3]) if len(argv) > 3 else 15]:
            print("  BAD", i, "|", "; ".join(e))
        for k in extra[:5]:
            print("  UNKNOWN", k)
        byf = {}
        for s in missing:
            byf[s["file"]] = byf.get(s["file"], 0) + 1
        if missing:
            print("  missing by file:", sorted(byf.items(), key=lambda x: -x[1])[:12])
        return 1 if bad or missing else 0
    elif cmd == "packets":
        slots = json.load(open(argv[2], encoding="utf8"))
        idx = write_packets(slots, argv[3])
        print(f"{len(idx)} packets -> {argv[3]}")
    elif cmd == "verify":
        return verify_cmd(argv[2:])
    elif cmd == "apply":
        n, t = apply(argv[2])
        print(f"text: wrote {n} of {t} slots into {argv[2]}")
    return 0



# ---------------------------------------------------------------- writer side
ORIG = os.environ.get("POKERED_ORIG", "D:/n64work/pokered/orig")


def name_map():
    return json.load(open(os.path.join(ORIG, "names.json"), encoding="utf8"))


def map_names(s, names):
    for k in sorted(names, key=len, reverse=True):
        s = re.sub(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])", names[k], s, flags=re.I)
    return s.replace("#MON", "KITH").replace("#", "KITH").replace("<PKMN>", "KITH")


def write_packets(slots, outdir, tree=None):
    """one text file per source file: the source lines of every block that holds a slot;
    slot lines show id, macro, budget and the name-mapped old line, other code lines
    (text_ram, text_decimal, done, prompt ...) are shown after '|' for context."""
    tree = tree or os.environ.get("POKERED_PRISTINE", "D:/n64work/pokered/pristine")
    names = name_map()
    os.makedirs(outdir, exist_ok=True)
    byf = {}
    for s in slots:
        byf.setdefault(s["file"], []).append(s)
    index = []
    for f, ss in byf.items():
        src = open(os.path.join(tree, f), encoding="utf8").read().split("\n")
        byline = {}
        for s in ss:
            byline.setdefault(s["line"], []).append(s)
        keep = set()
        for ln in byline:
            a = ln
            while a > 0 and not LABEL_RE.match(src[a]) and not LOCAL_RE.match(src[a]):
                a -= 1
            b = ln + 1
            while b < len(src) and not LABEL_RE.match(src[b]) and not LOCAL_RE.match(src[b]):
                b += 1
            keep.update(range(a, b))
        out, prev = [], -2
        for ln in sorted(keep):
            if ln != prev + 1:
                out.append("")
            prev = ln
            code = src[ln][:_comment_start(src[ln])].rstrip()
            if ln in byline:
                for s in byline[ln]:
                    ex = " EXACT" if s.get("exact") else ""
                    out.append(f"{s['id']}\t{s['macro']}\t[{s['budget']}{ex}]\t{map_names(s['text'], names)}")
            elif LABEL_RE.match(code) or LOCAL_RE.match(code):
                out.append(f"## {code}")
            elif code.strip():
                out.append(f"    | {map_names(code.strip(), names)}")
        p = os.path.join(outdir, f.replace("/", "__").replace(".asm", ".txt"))
        open(p, "w", encoding="utf8").write(f"# {f}: {len(ss)} slots\n" + "\n".join(out) + "\n")
        index.append((f, len(ss)))
    return index


def _bigrams(ws):
    return {(a, b) for a, b in zip(ws, ws[1:])}


def verify(slots, new, retail_blocks, names, cfg=None):
    """problems per id/label: invalid, missing, 5-word run with any retail block,
    retail name kept, block too close to its own old wording (bigram containment)."""
    from cleanroom.originality import text as otext
    probs = []
    for s in slots:
        if s["id"] not in new:
            probs.append((s["id"], "missing"))
            continue
        e = validate(s, new[s["id"]])
        if e:
            probs.append((s["id"], "; ".join(e)))
    byl = {}
    for s in slots:
        byl.setdefault((s["file"], s["id"].split("|")[1]), []).append(s)
    clean_blocks, keys = [], []
    for k, ss in byl.items():
        if all(s["id"] in new for s in ss):
            clean_blocks.append(" ".join(new[s["id"]] for s in ss))
            keys.append((k, ss))
    for i, w in otext.shared_runs(clean_blocks, retail_blocks):
        probs.append((keys[i][0][1], f"shares 5+ words with old text: \"{w}\""))
    for i, n in otext.name_hits(clean_blocks, names):
        probs.append((keys[i][0][1], f"keeps old name {n}"))
    for (k, ss), cb in zip(keys, clean_blocks):
        old = otext.words(" ".join(s["text"] for s in ss))
        nw = otext.words(cb)
        nb, ob = _bigrams(nw), _bigrams(old)
        if len(nb) >= 6 and len(nb & ob) / len(nb) > 0.35:
            probs.append((k[1], f"too close to the old wording ({len(nb & ob)}/{len(nb)} word pairs shared)"))
    return probs


def verify_cmd(argv):
    """python -m games.pokered.textx verify <new.json> [--files a.asm,b.asm]: one screen."""
    slots = json.load(open(os.path.join(ORIG, "slots.json"), encoding="utf8"))
    new = {}
    src = argv[0]
    for p in ([src] if src.endswith(".json") else sorted(glob.glob(os.path.join(src, "**", "*.json"), recursive=True))):
        new.update(json.load(open(p, encoding="utf8")))
    files_ = set(argv[argv.index("--files") + 1].split(",")) if "--files" in argv else \
        {k.split("|")[0] for k in new}
    mine = [s for s in slots if s["file"] in files_]
    retail = blocks(slots)
    names = {k: v for k, v in name_map().items() if len(k) >= 3}
    probs = verify(mine, new, retail, names)
    print(f"verify: {len(mine)} slots in {len(files_)} files, {sum(1 for s in mine if s['id'] in new)} written, "
          f"{len(probs)} problems")
    for i, p in probs[:40]:
        print("  ", i, "|", p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
