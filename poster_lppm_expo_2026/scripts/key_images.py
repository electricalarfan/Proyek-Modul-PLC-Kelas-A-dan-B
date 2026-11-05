"""Make header/footer art transparent so a category-coloured background can sit behind it.

header (image1.png): pure blue (0,0,255) background, baked red event text on the left.
  - event text region (x < 345) is removed; it is redrawn as live vector text in the master.
  - building (grey line art): unmix against blue assuming neutral foreground.
  - logos (colour): key near-pure-blue, unmix a thin edge band.
footer (image2.png): lavender (229,229,255) background, grey building line art.
Both are upscaled 3x (Lanczos, premultiplied) so print edges are smooth.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

SCALE = 3


def save(rgb, alpha, path):
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha * 255, 0, 255)]).round().astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    im.save(path, optimize=True)


def unmix(p, alpha, bg):
    a = np.maximum(alpha, 1e-3)[..., None]
    return (p - (1 - a) * np.asarray(bg, float)) / a


def header(src, dst):
    p = np.asarray(Image.open(src).convert("RGB")).astype(float)
    h, w, _ = p.shape
    R, G, B = p[..., 0], p[..., 1], p[..., 2]
    blue = (0.0, 0.0, 255.0)
    alpha = np.ones((h, w))
    rgb = p.copy()

    # building band: neutral-grey foreground over blue
    xs = slice(345, 957)
    g = (R[:, xs] + G[:, xs]) / 2
    a_b = np.clip(1 - (B[:, xs] - g) / 255.0, 0, 1)
    alpha[:, xs] = a_b
    rgb[:, xs] = unmix(p[:, xs], a_b, blue)

    # baked-in logos are dropped: the five HD logos are placed as separate pictures
    alpha[:, 957:] = 0       # LPPM, Tut Wuri, ACQUIN, BLU
    alpha[:100, 855:957] = 0  # UNIB emblem (sits above the building's right wing)

    alpha[:, :345] = 0      # baked event text -> replaced by live text
    alpha[0, :] = 0         # 1px grey rule along the top edge
    save(rgb, alpha, dst)


def footer(src, dst):
    p = np.asarray(Image.open(src).convert("RGB")).astype(float)
    R, G, B = p[..., 0], p[..., 1], p[..., 2]
    lav = (229.0, 229.0, 255.0)
    alpha = np.clip(1 - (B - (R + G) / 2) / 26.0, 0, 1)
    rgb = unmix(p, alpha, lav)
    save(rgb, alpha, dst)


if __name__ == "__main__":
    which, src, dst = sys.argv[1:4]
    {"header": header, "footer": footer}[which](src, dst)
