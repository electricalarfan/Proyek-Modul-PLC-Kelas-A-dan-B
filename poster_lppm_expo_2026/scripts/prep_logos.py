"""Normalise the five HD logos: transparent background, tight crop, print-ready size.

usage: prep_logos.py <unib.webp> <twh.svg> <acquin.webp> <lppm.webp> <blu.webp> <out_dir>

  unib / lppm / blu : already RGBA with real transparency -> crop + resize only
  acquin            : opaque white background -> flood-fill the outside, un-mix a 3 px
                      edge band so the red ring has no white fringe (inner white disc kept)
  twh               : native vector from Kemendikdasmen, rasterised at 1400 px via Chromium
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
NODE_PATH = "/opt/node22/lib/node_modules"


def crop_to_alpha(im, thresh=8):
    a = np.asarray(im.getchannel("A"))
    ys, xs = np.where(a > thresh)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def fit(im, max_w, max_h):
    s = min(max_w / im.width, max_h / im.height, 1.0)
    if s < 1.0:
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im


def key_white_outside(path):
    rgb = Image.open(path).convert("RGB")
    p = np.asarray(rgb).astype(float)
    m = p.min(axis=2)
    # RGB mask: ImageDraw.floodfill is unreliable on single-band "L" images
    mask = Image.fromarray(((m >= 238) * 255).astype("uint8")).convert("RGB")
    w, h = mask.size
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if mask.getpixel(pt) == (255, 255, 255):
            ImageDraw.floodfill(mask, pt, (255, 0, 0))
    mk = np.asarray(mask)
    outside = (mk[..., 0] == 255) & (mk[..., 1] == 0)
    grown = np.asarray(Image.fromarray((outside * 255).astype("uint8")).filter(ImageFilter.MaxFilter(7))) > 0
    band = grown & ~outside
    alpha = np.ones(outside.shape)
    alpha[outside] = 0
    est = np.clip((255.0 - m) / 195.0, 0, 1)
    alpha[band] = est[band]
    a3 = np.maximum(alpha, 1e-3)[..., None]
    fg = np.where(band[..., None], (p - 255.0 * (1 - a3)) / a3, p)
    out = np.dstack([np.clip(fg, 0, 255), alpha * 255]).round().astype("uint8")
    return Image.fromarray(out, "RGBA")


def main(unib, twh, acquin, lppm, blu, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_twh_raw.png"
    env = dict(os.environ, NODE_PATH=NODE_PATH)
    subprocess.run(["node", str(HERE / "render_svg.js"), twh, str(tmp), "1400"], check=True, env=env)

    jobs = {
        "unib": (Image.open(unib).convert("RGBA"), 1000),
        "twh": (Image.open(tmp).convert("RGBA"), 1000),
        "acquin": (key_white_outside(acquin), 1000),
        "blu": (Image.open(blu).convert("RGBA"), 1000),
        "lppm": (Image.open(lppm).convert("RGBA"), 1800),
    }
    for key, (im, maxw) in jobs.items():
        im = fit(crop_to_alpha(im), maxw, maxw)
        im.save(out / f"{key}.png", optimize=True)
        print(f"{key}: {im.size[0]}x{im.size[1]}  aspect {im.size[0] / im.size[1]:.3f}")
    tmp.unlink()


if __name__ == "__main__":
    main(*sys.argv[1:7])
