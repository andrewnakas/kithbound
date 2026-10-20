"""DIRTY ROOM (rejection only): pick composer seeds whose songs stay clearly
away from every retail song under the originality gate, with a margin.
Writes spec/music_seeds.json ({song: seed}); retail notes never enter a song.

    python -m games.pokered.music_seeds <retail midi dir>
"""
import glob
import json
import os
import sys

from cleanroom.audio.notes import load
from cleanroom.originality import music
from cleanroom.originality.config import merged
from games.pokered import audio_asm, audio_gen


def notes_of(chans):
    tracks = {}
    lib = audio_asm.parse_files  # noqa
    out = []
    from cleanroom.audio.notes import Note
    for ch, (head, body) in chans.items():
        t, octave = 0, 4
        for line in body:
            w = line.split()
            if w[0] == "octave":
                octave = int(w[1])
            elif w[0] == "note":
                n = int(w[2])
                out.append(Note(t * 12, ch - 1, 12 * (octave + 1) + audio_gen.NAMES.index(w[1].rstrip(",")), 100, n * 12))
                t += n
            elif w[0] in ("rest",):
                t += int(w[1])
            elif w[0] == "drum_note":
                n = int(w[2])
                out.append(Note(t * 12, ch - 1, 36 + int(w[1].rstrip(",")), 100, n * 12))
                t += n
    return sorted(out)


def main(argv):
    cfg = merged()["music"]
    strict = dict(cfg)
    strict["ngram_max"] = {k: v * 0.8 for k, v in cfg["ngram_max"].items()}
    strict["dtw_sim_max"] = cfg["dtw_sim_max"] * 0.8
    retail = {os.path.basename(p): load(p)[1] for p in glob.glob(os.path.join(argv[1], "*.mid"))}
    facts = json.load(open(os.path.join(audio_gen.HERE, "spec/music.json")))
    seeds = {}
    for song, f in facts.items():
        budget = f["file_bytes"] - (12 if song in ("Music_Cities1", "Music_MeetRival") else 0) - 2
        for k in range(200):
            seed = (audio_gen.h32(song, k) & 0xFFFF)
            chans, _, _ = audio_gen.compose_song(song, f, budget, seed=seed)
            cn = notes_of(chans)
            worst = max((music.compare(cn, rn, strict) for rn in retail.values()), key=lambda r: r["score"])
            if not worst["fail"]:
                seeds[song] = seed
                break
        print(song, seed, k, round(worst["score"], 2), flush=True)
    json.dump(seeds, open(audio_gen.SEEDS_PATH, "w"), indent=0)
    print(f"seeds: {len(seeds)}/{len(facts)}")


if __name__ == "__main__":
    main(sys.argv)
