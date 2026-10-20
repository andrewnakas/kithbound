"""CLEAN ROOM: all music, sound effects, cries and instruments of KITHBOUND.

Inputs are structure facts only (spec/music.json: channels, tempo, loop flag,
length, byte budget; spec/sfx.json: labels, channel, command counts, byte
budget) plus seeds. Melodies come from cleanroom.audio.compose; effects,
cries and drum/wave instruments are procedural. Output is pokered's own audio
command format, each file within its retail byte budget so the banks fit.

    python -m games.pokered.audio_gen <tree>      writes audio/music, audio/sfx, wave samples, cry table
"""
import json
import os
import re
import sys

import numpy as np

from cleanroom.audio.compose import compose
from cleanroom.decomp.gen import h32
from games.pokered import audio_asm

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["C_", "C#", "D_", "D#", "E_", "F_", "F#", "G_", "G#", "A_", "A#", "B_"]
UNIT = 12                     # composer ticks per length unit (division 48 -> 16th notes)
DRUM_INST = {36: 1, 38: 2, 42: 3, 46: 4}
DRUM_PRIO = [36, 38, 46, 42]


def rng_for(*key):
    return np.random.default_rng(h32("kithbound-audio", *key))


def moods_for(song):
    s = song.lower()
    if "battle" in s:
        return ["fast", "tense", "minor"], 1.0
    if any(k in s for k in ("tower", "lavender", "mansion", "dungeon", "silph", "evil")):
        return ["dark", "eerie"], 0.8
    if any(k in s for k in ("halloffame", "credits", "defeated", "title", "indigo")):
        return ["heroic", "bright"], 1.0
    if any(k in s for k in ("pokecenter", "healed", "oakslab", "jigglypuff", "surfing", "ssanne")):
        return ["calm", "happy"], 0.7
    return ["bright", "major"], 0.9


def roles_for(chans):
    base = {1: "lead", 2: "counter", 3: "bass", 4: "drums"}
    return [base[c] for c in chans]


# ------------------------------------------------------------- music encoder

def mono(notes, drums=False):
    """quantise to units; one note at a time per channel."""
    by_t = {}
    for n in notes:
        t = int(round(n.time / UNIT))
        d = max(1, int(round(n.dur / UNIT)))
        if drums:
            cur = by_t.get(t)
            if cur is None or DRUM_PRIO.index(n.key) < DRUM_PRIO.index(cur[0]):
                by_t[t] = (n.key, d)
        else:
            cur = by_t.get(t)
            if cur is None or n.key > cur[0]:
                by_t[t] = (n.key, d)
    out = []
    ts = sorted(by_t)
    for i, t in enumerate(ts):
        k, d = by_t[t]
        if i + 1 < len(ts):
            d = min(d, ts[i + 1] - t)
        out.append((t, k, d))
    return out


def channel_body(events, total, ch):
    """-> (lines, bytes) for the notes of one channel lasting exactly `total` units."""
    lines, nbytes, t, octave = [], 0, 0, None

    def rest(n):
        nonlocal nbytes
        while n > 0:
            m = min(16, n)
            lines.append(f"\trest {m}")
            nbytes += 1
            n -= m

    for st, k, d in events:
        if st >= total:
            break
        if st > t:
            rest(st - t)
        d = min(d, total - st)
        if ch == 4:
            inst = DRUM_INST.get(k, 3)
            first = min(16, d)
            lines.append(f"\tdrum_note {inst}, {first}")
            nbytes += 2
            rest(d - first)
        else:
            while k < 12 * 2:
                k += 12
            while k > 12 * 9 - 1:
                k -= 12
            o, p = k // 12 - 1, k % 12
            if o != octave:
                lines.append(f"\toctave {o}")
                nbytes += 1
                octave = o
            first = min(16, d)
            lines.append(f"\tnote {NAMES[p]}, {first}")
            nbytes += 1
            rest(d - first)
        t = st + d
    if t < total:
        rest(total - t)
    return lines, nbytes


def channel_header(ch, r, song, tempo):
    duty = int(r.integers(0, 4))
    if ch == 1:
        h = [f"\ttempo {tempo}", "\tvolume 7, 7", f"\tduty_cycle {duty}",
             f"\tvibrato {int(r.integers(4, 12))}, {int(r.integers(1, 4))}, {int(r.integers(2, 6))}",
             f"\tnote_type 12, {int(r.integers(10, 13))}, {int(r.integers(1, 6))}"]
        return h, 3 + 2 + 2 + 3 + 2
    if ch == 2:
        return [f"\tduty_cycle {(duty + 1) % 4}",
                f"\tnote_type 12, {int(r.integers(8, 12))}, {int(r.integers(2, 7))}"], 4
    if ch == 3:
        return [f"\tnote_type 12, {int(r.integers(1, 3))}, {int(r.integers(0, 6))}"], 2
    return ["\tdrum_speed 12"], 1


SEEDS_PATH = os.path.join(HERE, "spec/music_seeds.json")
SEEDS = json.load(open(SEEDS_PATH)) if os.path.exists(SEEDS_PATH) else {}


def compose_song(song, fact, budget, seed=None):
    moods, dens = moods_for(song)
    chans = fact["channels"]
    roles = roles_for(chans)
    want = max(4, min(32, int(round(fact["ticks"] / 192))))
    want -= want % 2
    bars = want
    while True:
        s = compose(bpm=fact["tempo"] or 120, length=bars * 192, loop=None, roles=roles, moods=moods,
                    seed=seed if seed is not None else SEEDS.get(song, h32(song) & 0xFFFF))
        r = rng_for(song)
        chmap = {}
        for midi_ch, role in s.roles.items():
            chmap.setdefault(role, []).append(midi_ch)
        total = bars * 16
        if not fact["loops"]:
            total = min(total, max(8, int(round(fact["ticks"] / UNIT))))
        out, nbytes = {}, 0
        for ch, role in zip(chans, roles):
            mc = chmap[role].pop(0)
            ev = mono([n for n in s.notes if n.ch == mc], drums=(ch == 4))
            body, b = channel_body(ev, total, ch)
            head, hb = channel_header(ch, r, song, fact["tempo"] or 120)
            if budget < 120 and ch == 1:
                head, hb = [h for h in head if "vibrato" not in h], hb - 3
            end = 4 if fact["loops"] else 1
            out[ch] = (head, body)
            nbytes += b + hb + end
        if nbytes <= budget or bars <= 2:
            return out, nbytes, bars
        bars -= 2


def write_music(tree, facts):
    lines_total, report = 0, []
    byfile = {}
    for song, f in facts.items():
        byfile.setdefault(f["file"], []).append(song)
    for fname, songs in byfile.items():
        text = []
        for song in songs:
            f = facts[song]
            budget = f["file_bytes"] - (12 if song in ("Music_Cities1", "Music_MeetRival") else 0)
            chans, nbytes, bars = compose_song(song, f, budget - 2)
            report.append((song, nbytes, f["file_bytes"], bars))
            for ch, (head, body) in chans.items():
                lab = f"{song}_Ch{ch}"
                if ch == 1 and song in ("Music_Cities1", "Music_MeetRival"):
                    alt = int(f["tempo"] * 1.12)
                    text += [f"{lab}_AlternateTempo::", f"\ttempo {alt}", f"\tsound_loop 0, {lab}.body", ""]
                text.append(f"{lab}::")
                if ch == 1:
                    text.append(head[0])
                    text.append(".body:")
                    text += head[1:]
                else:
                    text += head
                text.append(".mainloop:")
                text += body
                text.append("\tsound_loop 0, .mainloop" if f["loops"] else "\tsound_ret")
                text.append("")
                if song == "Music_MeetRival":
                    # alternate starts jump straight into the main body
                    if ch == 1:
                        text += [f"{lab}_AlternateStartAndTempo::", f"\ttempo {int(f['tempo'] * 1.12)}",
                                 f"\tsound_loop 0, {lab}_AlternateStart.body", "",
                                 f"{lab}_AlternateStart::", head[0], ".body:"] + head[1:] + \
                                [f"\tsound_loop 0, {lab}.mainloop", ""]
                    else:
                        text += [f"{lab}_AlternateStart::"] + head + [f"\tsound_loop 0, {lab}.mainloop", ""]
        open(os.path.join(tree, "audio/music", fname), "w", encoding="utf8", newline="\n").write("\n".join(text))
        lines_total += len(text)
    # the unused song keeps its labels only
    open(os.path.join(tree, "audio/music/unusedsong.asm"), "w", newline="\n").write(
        "Music_UnusedSong_Ch1::\n\tsound_ret\n\nMusic_UnusedSong_Ch2::\n\tsound_ret\n")
    return report


# ------------------------------------------------------------- instruments

def write_waves(tree):
    """six channel-3 instruments of our own: soft saw, square-ish, rounded triangle, organ, hollow, bell."""
    x = np.arange(32) / 32
    shapes = [
        15 * (1 - x) ** 1.4,
        np.where(x < 0.3, 13, 2) + 0 * x,
        15 * (1 - np.abs(2 * x - 1)) ** 0.8,
        7.5 + 4 * np.sin(2 * np.pi * x) + 3 * np.sin(6 * np.pi * x),
        7.5 + 7 * np.sin(2 * np.pi * x) * np.abs(np.sin(np.pi * x)),
        7.5 + 5 * np.sin(2 * np.pi * x) + 2.5 * np.sin(10 * np.pi * x),
    ]
    out = ["; This file is INCLUDEd three times, once for each audio engine.", ""]
    out += [f"\tdw .wave{i}" for i in range(6)] + ["\tdw .wave5"] * 3 + [""]
    for i, s in enumerate(shapes):
        v = np.clip(np.round(s), 0, 15).astype(int)
        out += [f".wave{i}", "\tdn " + ", ".join(str(a) for a in v), ""]
    open(os.path.join(tree, "audio/wave_samples.asm"), "w", newline="\n").write("\n".join(out))


KIT = {  # noise instrument number -> list of (length, volume, fade, noise param): our own drum kit
    1: [(1, 13, 1, 0x6b), (2, 9, 2, 0x7c)], 2: [(2, 12, 2, 0x34)], 3: [(0, 8, 1, 0x11)],
    4: [(1, 9, 3, 0x12)], 5: [(3, 11, 3, 0x55)], 6: [(0, 10, 1, 0x22)], 7: [(2, 7, 4, 0x46)],
    8: [(1, 12, 1, 0x5d), (1, 8, 2, 0x6e)], 9: [(4, 9, 5, 0x37)], 10: [(0, 6, 1, 0x10)],
    11: [(2, 10, 2, 0x26)], 12: [(1, 11, 2, 0x4c)], 13: [(3, 8, 3, 0x15)], 14: [(5, 9, 6, 0x48)],
    15: [(0, 12, 1, 0x29)], 16: [(1, 7, 2, 0x13)], 17: [(2, 13, 1, 0x63)], 18: [(6, 8, 7, 0x24)],
    19: [(1, 10, 3, 0x3a)],
}


# ------------------------------------------------------------- effects and cries

def gen_entry(e, fname):
    """new commands for one sfx channel label within its byte budget."""
    r = rng_for(fname, e["label"])
    lab, ch, budget = e["label"], e["ch"], e["bytes"]
    cmds = []
    if m := re.match(r"SFX_Noise_Instrument(\d+)_\d_Ch8", lab):
        for p in KIT[int(m.group(1))]:
            cmds.append(("noise_note", p, 3))
    elif e["music"]:
        cmds += [("execute_music", (), 1)]
        if ch == 5:
            cmds += [("tempo", (256,), 3), ("volume", (7, 7), 2)]
        if ch in (5, 6):
            cmds += [("duty_cycle", (int(r.integers(0, 4)),), 2)]
        root = int(rng_for(fname).integers(0, 12))
        if ch == 7:
            cmds += [("note_type", (int(r.choice([4, 6, 8])), 1, int(r.integers(0, 6))), 2)]
        else:
            cmds += [("note_type", (int(r.choice([4, 6, 8])), int(r.integers(10, 14)),
                                    int(r.integers(1, 5))), 2)]
        octv = {5: 4, 6: 4, 7: 3}.get(ch, 4)
        cmds += [("octave", (octv,), 1)]
        scale = [0, 2, 4, 7, 9, 12, 14, 16]
        n = max(1, e["notes"])
        mr = rng_for(fname, "motif")
        shape = np.cumsum(mr.integers(-1, 3, size=n))
        off = {5: 0, 6: 2, 7: -2}.get(ch, 0)
        for i in range(n):
            deg = int(np.clip(shape[i] + off, 0, len(scale) - 1))
            k = root + scale[deg]
            ln = 8 if i == n - 1 else int(mr.choice([1, 2, 2, 4]))
            cmds.append(("note", (NAMES[k % 12], ln), 1))
    else:
        kind = "noise" if ch == 8 else "square"
        n = e["noise"] if kind == "noise" else e["square"]
        n = max(1, n)
        if kind == "square" and e["square"] and budget >= 4 * n + 3:
            cmds.append(("duty_cycle", (int(r.integers(0, 4)),), 2))
        f0 = int(r.integers(1300, 1990))
        step = int(r.integers(-60, 61))
        for i in range(n):
            ln = int(r.integers(1, 16))
            vol = int(r.integers(6, 16))
            fade = int(r.integers(1, 8)) * (1 if r.uniform() < 0.85 else -1)
            if kind == "noise":
                cmds.append(("noise_note", (ln, vol, fade, int(r.integers(0x10, 0x80))), 3))
            else:
                f = int(np.clip(f0 + step * i + r.integers(-24, 25), 1024, 2040))
                cmds.append(("square_note", (ln, vol, fade, f), 4))
    cmds.append(("sound_ret", (), 1))
    while sum(c[2] for c in cmds) > budget and len(cmds) > 2:
        # drop from the middle of the effect, keep the end
        idx = next((i for i in range(len(cmds) - 2, -1, -1) if cmds[i][0] in
                    ("note", "square_note", "noise_note", "duty_cycle", "vibrato")), None)
        if idx is None:
            break
        cmds.pop(idx)
    return [f"{lab}:"] + [f"\t{c} " + ", ".join(str(a) for a in args) if args else f"\t{c}"
                          for c, args, _ in cmds]


def write_sfx(tree, facts):
    n = 0
    for fname, ents in facts.items():
        out = []
        for e in ents:
            if e["ch"] is None:
                continue
            out += gen_entry(e, re.sub(r"_[123]\.asm$", "", fname)) + [""]
            n += 1
        open(os.path.join(tree, "audio/sfx", fname), "w", newline="\n").write("\n".join(out))
    return n


def write_cry_table(tree):
    p = os.path.join(tree, "data/pokemon/cries.asm")
    lines = open(p, encoding="utf8").read().split("\n")
    out, i = [], 0
    for line in lines:
        m = re.match(r"^(\s*)mon_cry\s+SFX_CRY_[0-9A-F]+,\s*\$[0-9A-F]+,\s*\$[0-9A-F]+(.*)$", line)
        if m:
            r = rng_for("cry", i)
            base = int(r.integers(0, 0x26))
            line = f"{m.group(1)}mon_cry SFX_CRY_{base:02X}, ${int(r.integers(0, 256)):02X}, " \
                   f"${int(r.integers(0x50, 0xC1)):02X}"
            i += 1
        out.append(line)
    open(p, "w", encoding="utf8", newline="\n").write("\n".join(out))
    return i


def main(argv):
    tree = argv[1]
    mf = json.load(open(os.path.join(HERE, "spec/music.json")))
    sf = json.load(open(os.path.join(HERE, "spec/sfx.json")))
    rep = write_music(tree, mf)
    write_waves(tree)
    ns = write_sfx(tree, sf)
    nc = write_cry_table(tree)
    over = [r for r in rep if r[1] > r[2]]
    print(f"audio: {len(rep)} songs (bars {min(r[3] for r in rep)}-{max(r[3] for r in rep)}, "
          f"{sum(r[1] for r in rep)}/{sum(r[2] for r in rep)} B), {ns} effect channels, {nc} cries; "
          f"{len(over)} over budget")
    for r in over:
        print("  OVER", r)
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
