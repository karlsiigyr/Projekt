"""Builds every logo file into ../A-klassik and ../B-kaarid.

    pip install -r requirements.txt
    python build.py
"""
import io
import os

import cairosvg
from PIL import Image

import leola as L

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

COLORS = {
    "must": "#141414",
    "valge": "#FFFFFF",
    "kuld": "#C2A36B",
}
BLACK_BG = "#121212"


def svg_text(shape, fill, pad=0.04, bg=None, size=None, dims=None, title="Leola meestejuuksur"):
    """Tight viewBox around the outline with a little air; or centred on a fixed canvas.
    dims: physical width/height strings (e.g. "297mm") instead of pixel sizes."""
    b = shape.bounds
    w, h = b[2] - b[0], b[3] - b[1]
    if size:  # centred on a fixed canvas (W, H, fraction of canvas the mark may use)
        W, H, frac = size
        s = min(W * frac / w, H * frac / h)
        g = shape.transformed(s, 0, 0, s, W / 2 - s * (b[0] + b[2]) / 2, H / 2 - s * (b[1] + b[3]) / 2)
    else:
        p = max(w, h) * pad
        W, H = w + 2 * p, h + 2 * p
        g = shape.moved(p - b[0], p - b[1])
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    dw, dh = dims or (f"{W:.0f}", f"{H:.0f}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
            f'width="{dw}" height="{dh}"><title>{title}</title>{bg_rect}'
            f'<path fill="{fill}" d="{g.d(2)}"/></svg>\n')


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode) as f:
        f.write(data)


def png(svg, width=None, height=None):
    return cairosvg.svg2png(bytestring=svg.encode(), output_width=width, output_height=height)


def export_set(folder, prefix, marks):
    """marks: {suffix: (shape, png_width, png_height)}"""
    for suffix, (shape, pw, ph) in marks.items():
        for cname, col in COLORS.items():
            base = f"{prefix}{suffix}-{cname}"
            svg = svg_text(shape, col)
            write(os.path.join(folder, base + ".svg"), svg)
            write(os.path.join(folder, "png", base + ".png"), png(svg, pw, ph))


def on_black(folder, base, shape):
    """A4 landscape sheet, the gold logo centred on the dark background:
    a vector PDF and the same as a 300 dpi PNG (for viewers that show only pictures)."""
    svg = svg_text(shape, COLORS["kuld"], bg=BLACK_BG, size=(2970, 2100, 0.74), dims=("297mm", "210mm"))
    write(os.path.join(folder, "pdf", base + ".pdf"), cairosvg.svg2pdf(bytestring=svg.encode()))
    im = Image.open(io.BytesIO(png(svg, 3508, 2480))).convert("RGB")  # opaque: it has its own background
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    write(os.path.join(folder, "png", base + ".png"), buf.getvalue())


def favicons(folder, mark):
    out = os.path.join(folder, "favicon")
    gold = COLORS["kuld"]
    big = svg_text(mark, gold, bg=BLACK_BG, size=(512, 512, 0.74))
    write(os.path.join(out, "favicon.svg"), big)
    for name, px in (("favicon-32.png", 32), ("apple-touch-icon.png", 180),
                     ("icon-192.png", 192), ("icon-512.png", 512)):
        write(os.path.join(out, name), png(big, px, px))
    ico = Image.open(io.BytesIO(png(big, 256, 256)))
    ico.save(os.path.join(out, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


def social(folder, prefix, seal, lockup):
    out = os.path.join(folder, "sotsiaalmeedia")
    gold = COLORS["kuld"]
    write(os.path.join(out, f"{prefix}profiilipilt.png"),
          png(svg_text(seal, gold, bg=BLACK_BG, size=(1080, 1080, 0.80)), 1080, 1080))
    write(os.path.join(out, f"{prefix}jagamispilt-1200x630.png"),
          png(svg_text(lockup, gold, bg=BLACK_BG, size=(1200, 630, 0.62)), 1200, 630))


def main():
    a = os.path.join(ROOT, "A-klassik")
    klassik = L.lockup_klassik()
    klassik_compact = L.lockup_klassik_compact()
    seal_a = L.seal_klassik()
    export_set(a, "leola-klassik", {
        "": (klassik, 3000, None),
        "-nimi": (L.script_name(), 3000, None),
        "-horisontaalne": (klassik_compact, 3000, None),
        "-vertikaalne": (L.vertical(klassik_compact), None, 3000),
        "-pitser": (seal_a, 2000, None),
        "-L": (L.script_name("L"), 1200, None),
    })
    favicons(a, L.script_name("L"))
    social(a, "leola-klassik-", seal_a, klassik)
    on_black(a, "leola-klassik-kuld-mustal", klassik)
    on_black(a, "leola-klassik-horisontaalne-kuld-mustal", klassik_compact)

    b = os.path.join(ROOT, "B-kaarid")
    kaarid = L.lockup_kaarid()
    seal_b = L.seal_kaarid()
    mark_b = L.scissors_name("L")
    export_set(b, "leola-kaarid", {
        "": (kaarid, 3000, None),
        "-nimi": (L.scissors_name(), 3000, None),
        "-vertikaalne": (L.vertical(kaarid), None, 3000),
        "-pitser": (seal_b, 2000, None),
        "-L": (mark_b, 1200, None),
    })
    favicons(b, mark_b)
    social(b, "leola-kaarid-", seal_b, kaarid)
    print("valmis:", a, b)


if __name__ == "__main__":
    main()
