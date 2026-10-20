"""Game Boy picture formats.

Pictures are index arrays (h, w) uint8 with shades 0 (white) .. 3 (black),
the way the pret disassemblies store them as greyscale PNGs.

  read_png / write_png      greyscale PNG <-> shade indices
  to_2bpp / from_2bpp       planar 8x8 tiles, 16 bytes each (row: low plane, high plane)
  to_1bpp / from_1bpp       8 bytes per tile
  tiles / untile            split into 8x8 tiles (row-major) and back
  flood_outside             border-connected white region (the outside of a picture)
"""
import numpy as np
from PIL import Image


def read_png(path):
    im = Image.open(path)
    g = np.asarray(im.convert("L"), np.int32)
    return (3 - (g + 42) // 85).clip(0, 3).astype(np.uint8)


def write_png(path, idx, depth=2):
    idx = np.asarray(idx, np.uint8)
    if depth == 1:
        idx = np.where(idx >= 2, 3, 0).astype(np.uint8)
    Image.fromarray(((3 - idx) * 85).astype(np.uint8), "L").save(path, optimize=True)


def tiles(idx):
    h, w = idx.shape
    return idx.reshape(h // 8, 8, w // 8, 8).swapaxes(1, 2).reshape(-1, 8, 8)


def untile(t, w):
    n = len(t)
    cols = w // 8
    rows = (n + cols - 1) // cols
    out = np.zeros((rows * cols, 8, 8), np.uint8)
    out[:n] = t
    return out.reshape(rows, cols, 8, 8).swapaxes(1, 2).reshape(rows * 8, cols * 8)


def to_2bpp(idx):
    t = tiles(idx)
    lo = np.packbits(t & 1, axis=2)[..., 0]
    hi = np.packbits(t >> 1, axis=2)[..., 0]
    return np.stack([lo, hi], axis=2).astype(np.uint8).tobytes()


def from_2bpp(data, w=None):
    a = np.frombuffer(data[:len(data) // 16 * 16], np.uint8).reshape(-1, 8, 2)
    lo = np.unpackbits(a[..., 0:1], axis=2)
    hi = np.unpackbits(a[..., 1:2], axis=2)
    t = (lo | (hi << 1)).astype(np.uint8)
    return t if w is None else untile(t, w)


def to_1bpp(idx):
    return np.packbits(tiles(idx) >= 2, axis=2)[..., 0].astype(np.uint8).tobytes()


def from_1bpp(data, w=None):
    a = np.frombuffer(data[:len(data) // 8 * 8], np.uint8).reshape(-1, 8, 1)
    t = (np.unpackbits(a, axis=2) * 3).astype(np.uint8)
    return t if w is None else untile(t, w)


def flood_outside(idx, bg=0):
    """True where a pixel is `bg` and connected (4-neighbour) to the border."""
    free = idx == bg
    out = np.zeros_like(free)
    out[0, :] = free[0, :]; out[-1, :] = free[-1, :]
    out[:, 0] = free[:, 0]; out[:, -1] = free[:, -1]
    while True:
        g = out.copy()
        g[1:, :] |= out[:-1, :]; g[:-1, :] |= out[1:, :]
        g[:, 1:] |= out[:, :-1]; g[:, :-1] |= out[:, 1:]
        g &= free
        if (g == out).all():
            return out
        out = g


def pack_mask(mask):
    return np.packbits(np.asarray(mask, bool)).tobytes().hex()


def unpack_mask(hexstr, h, w):
    return np.unpackbits(np.frombuffer(bytes.fromhex(hexstr), np.uint8))[:h * w].reshape(h, w).astype(bool)


def sheet(items, scale=3, cols=8, pad=4, label=True, bg=(40, 44, 60), grid=0):
    """Contact sheet: items = [(label, idx array)]. Returns a PIL image."""
    from PIL import ImageDraw
    lab = 10 if label else 0
    if cols > 0:
        cw = max(i.shape[1] for _, i in items) * scale + pad
        ch = max(i.shape[0] for _, i in items) * scale + pad + lab
        pos = [(pad + (n % cols) * cw, pad + (n // cols) * ch) for n in range(len(items))]
        size = (cols * cw + pad, ((len(items) + cols - 1) // cols) * ch + pad)
    else:                                   # shelf packing to a width of -cols pixels
        width, x, y, rowh, pos = -cols, pad, pad, 0, []
        for _, i in items:
            w, h = i.shape[1] * scale + pad, i.shape[0] * scale + pad + lab
            if x + w > width and x > pad:
                x, y, rowh = pad, y + rowh, 0
            pos.append((x, y)); x += w; rowh = max(rowh, h)
        size = (width, y + rowh + pad)
    im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    for n, (name, idx) in enumerate(items):
        x, y = pos[n]
        cw = idx.shape[1] * scale + pad
        g = Image.fromarray(((3 - idx) * 85).astype(np.uint8), "L").resize(
            (idx.shape[1] * scale, idx.shape[0] * scale), Image.NEAREST)
        im.paste(g, (x, y + (10 if label else 0)))
        if grid:
            for gx in range(0, idx.shape[1] + 1, grid):
                d.line([(x + gx * scale, y + 10), (x + gx * scale, y + 10 + idx.shape[0] * scale)], fill=(255, 60, 60))
            for gy in range(0, idx.shape[0] + 1, grid):
                d.line([(x, y + 10 + gy * scale), (x + idx.shape[1] * scale, y + 10 + gy * scale)], fill=(255, 60, 60))
        if label:
            d.text((x, y - 1), name[:max(4, cw // 6)], fill=(255, 230, 120))
    return im
