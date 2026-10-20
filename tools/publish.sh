#!/bin/sh
# Rebuild the clean ROMs and the site; with "push" as $1 also push gh-pages. Taint must be 0 failing.
#   sh tools/publish.sh [push] ["message"]
set -e
W=${POKERED_WORK:-/d/n64work/pokered}
R="$(cd "$(dirname "$0")/.." && pwd)"
cd "$R"
export OPENBLAS_NUM_THREADS=1
sh games/pokered/build_clean.sh | tail -3
python -m cleanroom.gb.taint "$W/dirty" "$W/clean" games/pokered/spec/assets.json --list 8 | tee "$W/taint.txt" | head -8
grep -q "FAILING: 0" "$W/taint.txt" || { echo "taint not clean: not publishing"; exit 1; }
python ports/ejs/make_site.py "$W/site" "$W/ejs/emulatorjs-emulatorjs-4.2.3/package" "$W/ejs/emulatorjs-core-gambatte-4.2.3/package" "$W/clean/pokered.gbc" "$W/clean/pokeblue.gbc"
[ "$1" = push ] || exit 0
cd "$W/site"
[ -d .git ] || { git init -q && git remote add origin https://github.com/andrewnakas/pokered-cleanroom.git; }
git config user.name andre; git config user.email treesixtyweather@gmail.com
# one orphan commit per deploy keeps the Pages branch small
git checkout -q --orphan tmp && git add -A && git commit -qm "Site: ${2:-rebuild}" && { git branch -D gh-pages -q 2>/dev/null || true; } && git branch -m gh-pages && git push -q -f origin gh-pages && echo "pushed gh-pages"
