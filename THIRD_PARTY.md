# KITHBOUND: credits and third-party notices

KITHBOUND DAWN and KITHBOUND DUSK are an original RPG built on the **pret/pokered disassembly**
(https://github.com/pret/pokered). `kithbound-dawn.gbc` / `kithbound-dusk.gbc` are assembled from its engine
code; every creature, trainer, map, tileset, picture, tune, sound, table and line of text was made for this
project. No original game file is needed or included. Clean-room pipeline:
https://github.com/andrewnakas/pokered-cleanroom (MIT).

## Third-party software in this site

| Component | Files | Licence | Source |
|---|---|---|---|
| EmulatorJS 4.2.3 | `data/` (loader, emulator, css, localization, 7z/zip extractors) | GPL-3.0 (`data/LICENSE.EmulatorJS`) | https://github.com/EmulatorJS/EmulatorJS |
| libretro gambatte core, built by the EmulatorJS project | `data/cores/gambatte-*.data` | GPL-2.0 | https://github.com/libretro/gambatte-libretro |
| RetroArch (libretro frontend linked into the core by EmulatorJS) | same files | GPL-3.0 | https://github.com/EmulatorJS/RetroArch |
| nipplejs (touch joystick, in EmulatorJS) | `data/src/nipplejs.js` | MIT | https://github.com/yoannmoinet/nipplejs |
| socket.io client (in EmulatorJS) | `data/src/socket.io.min.js` | MIT | https://github.com/socketio/socket.io |
