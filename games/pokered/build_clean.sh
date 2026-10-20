#!/bin/sh
# Clean build: pristine code + data, no retail picture, every picture generated.
#   sh games/pokered/build_clean.sh [fresh]     -> D:/n64work/pokered/clean/pokered.gbc, pokeblue.gbc
set -e
W=${POKERED_WORK:-/d/n64work/pokered}
R="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="$HOME/bin:$W/rgbds:$PATH" OPENBLAS_NUM_THREADS=1
if true; then   # always from pristine: the generators rewrite tables in place
  rm -rf "$W/clean"
  cp -r "$W/pristine" "$W/clean"
  rm -rf "$W/clean/.git"
  find "$W/clean/gfx" -name '*.png' -delete      # no retail picture stays in the clean tree
fi
# our words, music, effects and tables replace the old ones (structure stays)
(cd "$R" && PYTHONIOENCODING=utf-8 python -m games.pokered.textx apply "$W/clean" && python -m games.pokered.audio_gen "$W/clean" && python -m games.pokered.blocks write "$W/clean" && python -m games.pokered.data_gen "$W/clean" && python -m games.pokered.tables_gen "$W/clean" && python -m games.pokered.anims_gen "$W/clean" && python -m games.pokered.maps_gen "$W/clean" && python -m games.pokered.townmap_gen "$W/clean") || exit 1
# block files no map header uses are not part of the game: blank the ones maps.asm still
# INCBINs (unused maps), delete the rest
WM=$(cygpath -m "$W")
(cd "$R" && python -c "
from games.pokered.maps_kit import Kit; import os,glob,re
k=Kit('$WM/clean'); used={m.blk for m in k.maps.values()}
inc=set(re.findall(r'INCBIN \"(maps/[^\"]+)\"', k.read('maps.asm')))
for p in glob.glob('$WM/clean/maps/*.blk'):
    rel='maps/'+os.path.basename(p)
    if rel in used: continue
    if rel in inc: open(p,'wb').write(bytes(os.path.getsize(p)))
    else: os.remove(p)
")
sed -i 's/-t "POKEMON RED"/-t "KITHBOUND DAWN"/; s/-t "POKEMON BLUE"/-t "KITHBOUND DUSK"/; s/-k 01 /-k 00 /' "$W/clean/Makefile"
cd "$W/clean"
find gfx \( -name '*.2bpp' -o -name '*.1bpp' -o -name '*.pic' \) -delete
rm -f gfx/*.o pokered.gbc pokeblue.gbc
(cd "$R" && python -m games.pokered.generate "$W/clean")
make -j2 red blue > "$W/clean_build.log" 2>&1 || { grep -i -m8 "error\|overflow\|too big" "$W/clean_build.log"; tail -3 "$W/clean_build.log"; exit 1; }
sha1sum pokered.gbc pokeblue.gbc | cut -c1-12,41-
ls -l pokered.gbc | awk '{print "size", $5}'
