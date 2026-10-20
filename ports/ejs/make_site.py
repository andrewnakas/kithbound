"""Assemble the web site: EmulatorJS runtime + gambatte core + our page + the clean ROMs.

    python ports/ejs/make_site.py <site dir> <emulatorjs package dir> <core package dir> <rom> [<rom> ...]

Refuses any ROM whose SHA1 is a retail one (never publish retail data).
"""
import hashlib
import os
import shutil
import sys

RETAIL_SHA1 = ("ea9bcae617fdf159b045185467ae58b2e4a48b9a",      # retail red build
               "d7037c83e1ae5b39bde3c30787637ba1d4c48ce2",      # retail blue build
               "5b1456177671b79b263c614ea0e7cc9ac542e9c4")      # Blue debug build
HERE = os.path.dirname(os.path.abspath(__file__))

NOTICE = """# KITHBOUND: credits and third-party notices

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
"""
ROM_NAMES = {"pokered.gbc": "kithbound-dawn.gbc", "pokeblue.gbc": "kithbound-dusk.gbc"}
DROP = ["compression/libunrar.js", "compression/libunrar.wasm"]


def main(argv):
    site, ejs, core, roms = argv[1], argv[2], argv[3], argv[4:]
    blobs = []
    for r in roms:
        data = open(r, "rb").read()
        if hashlib.sha1(data).hexdigest() in RETAIL_SHA1:
            sys.exit(f"refusing: {r} is a retail ROM")
        blobs.append((ROM_NAMES.get(os.path.basename(r), os.path.basename(r)), data))
    if os.path.exists(site):
        for n in os.listdir(site):
            if n == ".git":
                continue
            p = os.path.join(site, n)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(site, exist_ok=True)
    shutil.copytree(os.path.join(ejs, "data"), os.path.join(site, "data"), dirs_exist_ok=True)
    shutil.copyfile(os.path.join(ejs, "LICENSE"), os.path.join(site, "data", "LICENSE.EmulatorJS"))
    for rel in DROP:                                   # the ROMs are not archives: no unrar
        p = os.path.join(site, "data", rel)
        if os.path.exists(p):
            os.remove(p)
    cores = os.path.join(site, "data", "cores")
    os.makedirs(os.path.join(cores, "reports"), exist_ok=True)
    for n in os.listdir(core):
        if n.endswith(".data"):
            shutil.copyfile(os.path.join(core, n), os.path.join(cores, n))
    for n in os.listdir(os.path.join(core, "reports")):
        shutil.copyfile(os.path.join(core, "reports", n), os.path.join(cores, "reports", n))
    shutil.copyfile(os.path.join(HERE, "index.html"), os.path.join(site, "index.html"))
    for name, data in blobs:
        open(os.path.join(site, name), "wb").write(data)
    open(os.path.join(site, "THIRD_PARTY.md"), "w", encoding="utf-8", newline="\n").write(NOTICE)
    open(os.path.join(site, ".nojekyll"), "w").close()
    total = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(site) for f in fs)
    print(f"site: {site} ({total // 1024} KB), roms " + ", ".join(f"{n} {hashlib.sha1(d).hexdigest()[:10]}" for n, d in blobs))


if __name__ == "__main__":
    main(sys.argv)
