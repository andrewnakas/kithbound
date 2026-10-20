"""pokered audio command files: parse, size, play out to note events.

Used on both sides: the dirty room reads structure facts (tempo, channel count,
loop, length, byte size) and exports retail notes for the originality gate;
the clean side measures and exports what we composed.

    labels = parse_files([...asm])            {label: [(cmd, [args])]}
    size(cmds)                                 bytes the commands assemble to
    play(labels, start, ch)                    -> [(tick, key, dur)] one pass, loops unrolled once
    python -m games.pokered.audio_asm midi <tree> <outdir>   one .mid per music file (all channels)
"""
import glob
import os
import re
import sys

SIZES = {"note": 1, "rest": 1, "drum_note": 2, "drum_note_short": 1, "note_type": 2, "drum_speed": 1,
         "octave": 1, "toggle_perfect_pitch": 1, "vibrato": 3, "pitch_slide": 3, "duty_cycle": 2,
         "tempo": 3, "stereo_panning": 2, "unknownmusic0xef": 2, "volume": 2, "execute_music": 1,
         "duty_cycle_pattern": 2, "sound_call": 3, "sound_loop": 4, "sound_ret": 1, "square_note": 4,
         "noise_note": 3, "pitch_sweep": 2, "channel_count": 0, "channel": 0}
PITCH = {"C_": 0, "C#": 1, "D_": 2, "D#": 3, "E_": 4, "F_": 5, "F#": 6, "G_": 7, "G#": 8, "A_": 9,
         "A#": 10, "B_": 11}
LINE = re.compile(r"^\s*([a-z_0-9]+)\b\s*(.*)$")
LABEL = re.compile(r"^([A-Za-z_.][\w.]*?)(::?)\s*$")


def parse_files(paths):
    labels, order, glob_label = {}, [], None
    for p in paths:
        cur = None
        for raw in open(p, encoding="utf8"):
            line = raw.split(";")[0].rstrip()
            if not line.strip():
                continue
            m = LABEL.match(line.strip()) if not line[0].isspace() or line.strip().startswith(".") else None
            if m:
                name = m.group(1)
                if name.startswith("."):
                    name = glob_label + name
                else:
                    glob_label = name
                cur = name
                labels[cur] = []
                order.append(cur)
                continue
            mm = LINE.match(line)
            if mm and cur is not None:
                args = [a.strip() for a in mm.group(2).split(",")] if mm.group(2).strip() else []
                args = [(glob_label + a) if a.startswith(".") else a for a in args]
                labels[cur].append((mm.group(1), args))
    # fall-through: a label's command list continues into the next label in file order
    flat, index = [], {}
    for name in order:
        index[name] = len(flat)
        flat += labels[name]
    return {"flat": flat, "index": index, "order": order}


def size(cmds):
    return sum(SIZES.get(c, 0) for c, _ in cmds)


def _num(a):
    a = a.strip()
    if a.startswith("$"):
        return int(a[1:], 16)
    if a.startswith("%"):
        return int(a[1:], 2)
    return int(a)


def play(lib, start, ch, max_ticks=200000):
    """note events of one channel; infinite loops are followed once; ticks = units * speed."""
    flat, index = lib["flat"], lib["index"]
    pc, stack, loops = index[start], [], {}
    t, octave, speed, out, seen_inf = 0, 4, 12, [], set()
    loop_at = None
    steps = 0
    while pc < len(flat) and steps < 100000 and t < max_ticks:
        steps += 1
        c, a = flat[pc]
        pc += 1
        if c == "note":
            if ch == 4:     # drum_note_short on noise
                n = _num(a[1]) * speed
                out.append((t, 36 + _num(a[0]), n))
                t += n
                continue
            n = _num(a[1]) * speed
            out.append((t, 12 * (octave + 1) + PITCH[a[0]], n))
            t += n
        elif c == "drum_note":
            n = _num(a[1]) * speed
            out.append((t, 36 + _num(a[0]), n))
            t += n
        elif c == "rest":
            t += _num(a[0]) * speed
        elif c == "octave":
            octave = _num(a[0])
        elif c in ("note_type", "drum_speed"):
            speed = _num(a[0])
        elif c == "sound_call":
            stack.append(pc)
            pc = index[a[0]]
        elif c == "sound_ret":
            if not stack:
                break
            pc = stack.pop()
        elif c == "sound_loop":
            cnt, target = _num(a[0]), a[1]
            if cnt == 0:
                if target in seen_inf:
                    break
                seen_inf.add(target)
                loop_at = loop_at if loop_at is not None else (index[target], t)
                break           # one pass is enough for comparison and length facts
            key = pc
            loops[key] = loops.get(key, cnt) - 1
            if loops[key] > 0:
                pc = index[target]
            else:
                del loops[key]
    return out, t, loop_at is not None


def music_files(tree):
    return sorted(glob.glob(os.path.join(tree, "audio", "music", "*.asm")))


def headers(tree):
    """{song label: [(channel number, channel label)]} from the music headers."""
    out, cur = {}, None
    for p in sorted(glob.glob(os.path.join(tree, "audio", "headers", "musicheaders*.asm"))):
        for line in open(p, encoding="utf8"):
            line = line.split(";")[0].rstrip()
            m = re.match(r"^(Music_\w+)::", line)
            if m:
                cur = m.group(1)
                out[cur] = []
            m = re.match(r"^\s*channel\s+(\d+),\s*(\w+)", line)
            if m and cur:
                out[cur].append((int(m.group(1)), m.group(2)))
    return out


def song_file(tree):
    """{song label: music file} by which file defines the channel labels."""
    lib_by_file = {}
    for p in music_files(tree):
        lib_by_file[p] = parse_files([p])
    out = {}
    for song, chans in headers(tree).items():
        for p, lib in lib_by_file.items():
            if chans and chans[0][1] in lib["index"]:
                out[song] = p
    return out, lib_by_file


def to_midi_bytes(tracks, division=48):
    from cleanroom.audio import midi
    from cleanroom.audio.notes import Note
    notes = []
    for ch, evs in tracks.items():
        for t, k, d in evs:
            notes.append(Note(t, ch - 1, max(0, min(127, k)), 100, max(1, d)))
    return midi.write(sorted(notes), division)


def export_midi(tree, outdir):
    os.makedirs(outdir, exist_ok=True)
    sf, libs = song_file(tree)
    allp = music_files(tree)
    lib = parse_files(allp)
    n = 0
    for song, chans in headers(tree).items():
        tracks = {}
        for chn, lab in chans:
            evs, _, _ = play(lib, lab, chn)
            tracks[chn] = evs
        open(os.path.join(outdir, song + ".mid"), "wb").write(to_midi_bytes(tracks))
        n += 1
    return n


if __name__ == "__main__":
    if sys.argv[1] == "midi":
        print(export_midi(sys.argv[2], sys.argv[3]), "songs ->", sys.argv[3])
