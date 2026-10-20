# Game Boy clean rooms (notes from Pokemon Red/Blue)

The N64 playbook's rules and pipeline shape carry over (dirty tree -> spec of coarse facts ->
generate -> taint -> build -> headless check -> publish). What is different on Game Boy:

## Formats

| Thing | Stored form | Code |
|---|---|---|
| Picture source in pret trees | greyscale PNG, 4 shades (0 white .. 3 black), 1-bit for fonts | `cleanroom.gb.gfx.read_png / write_png` |
| Tiles in the ROM | 2bpp planar, 8x8, 16 bytes (row = low plane byte, high plane byte); 1bpp = 8 bytes | `to_2bpp / from_2bpp / to_1bpp / from_1bpp` |
| Compressed pictures (`.pic`) | the game's own bit-plane RLE/delta coder | never re-implemented: the repo's `tools/pkmncompress` runs in the build |
| Tilesets | 16 tiles per row, tile number = row*16+col; `.bst` blocksets = 4x4 tile numbers; maps = block numbers | `games/pokered/tsview.py` |
| Sprites | strips of 16x16 frames, shade 0 = transparent; on screen OBP0 maps 1 white, 2 light, 3 black | `games/pokered/art/sprites.py` |
| Sound | note/command sequences for the 4 channels + wave table: **code/data, kept** (no samples) | - |
| Palettes | SGB/GBC 4-colour tables in `data/sgb`: data tables, kept | - |

## Build

- rgbds 1.0.4 Windows binaries from the rgbds releases page -> `D:/n64work/pokered/rgbds`;
  `make` + `gcc` (zig) from `tools/setup_winbin.sh` build the four C tools of the repo.
- Round trip: `make red blue` in the untouched clone must give the sha1s in `roms.sha1`.
- Clean build: `sh games/pokered/build_clean.sh [fresh]` (copy of pristine with every PNG deleted,
  `python -m games.pokered.generate` writes all 509 used PNGs, then `make -j2 red blue`).

## Traps

- **numpy on a busy PC**: `OPENBLAS_NUM_THREADS=1` or imports die with "Memory allocation still failed".
- **Build flags that depend on the picture**: `tools/gfx --trim-whitespace` (trailing blank tiles
  are cut: keep the blank tile list as a layout fact), `--remove-duplicates` (the code's tilemaps index
  de-duplicated tiles: keep which tiles are equal), `--interleave`, rgbgfx `--columns`.
- **Shared frame tiles**: the same edge tile is used for top and bottom (left and right) of a text
  box: draw them symmetric, corners are not mirror images.
- **Open outlines**: a retail figure on white often has gaps in its outline; a flood fill from the
  border leaks in and the "silhouette" becomes the retail line art. Close gaps (grow ink, flood, grow
  back) and drop parts that are only a line.
- **An entry module that is also imported**: `python -m pkg.generate` and `import pkg.generate` are two
  module objects; keep registries (`DRAWERS`) in a third module.
- **Fonts**: a 5x7 pixel font is so standard that a third of its glyphs equal the retail ones pixel
  for pixel. Use a design of your own (here: doubled upright strokes) and let the taint scan confirm.
- **PyBoy** (`pip install pyboy`) runs the ROM headless at many times real speed: scripted buttons +
  screenshots in `games/pokered/play.py`. Use it for all gameplay checks; the browser only for the page.
- **EmulatorJS**: `EJS_core = "gb"` (system name, picks gambatte and the Game Boy touch pad); core files
  come from the npm package `@emulatorjs/core-gambatte`; `gambatte_gb_colorization: auto` gives the
  Game Boy Color palette that the hardware picks for the cartridge title.

## Taint rule for small low-colour tiles (`cleanroom/gb/taint.py`)

Every clean tile is looked up in the set of all retail tiles (all PNGs and all built 2bpp/1bpp files).
A match is a coincidence, not a failure, only when the tile is bars/blank/solid, has at most 6 drawn
pixels or 2 shades with at most 14 shade changes, or (in a picture with a kept silhouette) its
interior is one flat shade or under 12 pixels. Sheets are also checked tile by tile in place (80% of
the drawn pixels equal = near copy = failing); silhouette pictures by the share of equal interior
pixels (90% = failing); compressed `.pic` streams by shared byte runs (32 bytes = failing). Chance
collisions inside figures are fixed by `games/pokered/salts.json` (tile numbers only), which makes the
generator put a sparse texture mark in those tiles.
