#!/bin/sh
# Both publish gates on the current clean build (run build_clean.sh first):
# originality (music, text, pictures, maps) -> ORIGINALITY.md, taint -> TAINT.md, ROM word scan.
#   sh games/pokered/gate.sh
W=${POKERED_WORK:-/d/n64work/pokered}
R="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$R"
export PYTHONIOENCODING=utf-8 OPENBLAS_NUM_THREADS=1
rm -rf "$W/clean/orig_midi"
python -m games.pokered.textx dump "$W/clean" "$W/clean/orig_text.json" > /dev/null
python -m games.pokered.audio_asm midi "$W/clean" "$W/clean/orig_midi" > /dev/null
for r in pokered pokeblue; do python -m games.pokered.codecheck "$W/clean" $r "$W/dirty/$r.gbc" | head -6; done
python -m games.pokered.mapbot "$W/clean" --md MAPBOT.md | head -8
python -m games.pokered.blocks check | head -6
python -m cleanroom.originality "$W" "$W" games/pokered/spec --manifest games/pokered/originality.json --report ORIGINALITY.md | head -12
python -m cleanroom.gb.taint "$W/dirty" "$W/clean" games/pokered/spec/assets.json --list 8 > "$W/taint.txt"; head -12 "$W/taint.txt"
{ echo "# Taint scan: pokered (KITHBOUND)"; echo; echo '```'; cat "$W/taint.txt"; echo '```'; } > TAINT.md
for r in pokered pokeblue; do python -m games.pokered.romscan "$W/clean" "$W/clean/$r.gbc" | head -3; done
