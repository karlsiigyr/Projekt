"""Leola meestejuuksur: logo construction.

Geometry is in units where the name is set at 1000 units per em, y down,
baseline at y=0.

Two directions:
  klassik  Pinyon Script name, Bodoni Moda caps tagline.
  kaarid   Bodoni Moda Italic name whose L doubles as an open pair of shears:
           the stem and the foot are the blades, the screw sits in the corner
           and the finger rings grow out of it to the lower left.
"""
import math

from logotype import (Font, ellipse, find_font, polygon, rect, ring, rotate, text,
                      union_all)

BODONI_IT = ("bodonimoda", "*Italic*", {"opsz": 40, "wght": 750})
BODONI_CAPS = ("bodonimoda", "BodoniModa[[]*", {"opsz": 6, "wght": 600})
PINYON = ("pinyonscript", "*", None)

TAGLINE = "MEESTEJUUKSUR"
CITY = "VILJANDI"


def font(spec):
    fam, pat, var = spec
    return Font(find_font(fam, pat), var)


def caps_line(s, size, tracking=300, spec=BODONI_CAPS, embolden=0.0):
    shp, _, _ = text(font(spec), s, size, 0, 0, tracking=tracking)
    return shp.emboldened(embolden) if embolden else shp


def center_x(shape, cx):
    b = shape.bounds
    return shape.moved(cx - (b[0] + b[2]) / 2, 0)


def place_top(shape, y_top):
    return shape.moved(0, y_top - shape.bounds[1])


def hairline(x0, x1, y, w):
    return rect(x0, y - w / 2, x1 - x0, w)


def diamond(cx, cy, r):
    return polygon([(cx, cy - r), (cx + r * 0.72, cy), (cx, cy + r), (cx - r * 0.72, cy)])


# ------------------------------------------------------------ the shears L

def _finger_ring(cx, cy, rx, ry, w_side, w_end, angle):
    """Oval ring, sides heavier than the ends."""
    outer = ellipse(0, 0, rx, ry)
    inner = ellipse(0, 0, rx - w_end, ry - w_side)
    return rotate(outer - inner, angle).moved(cx, cy)


def _shank_with_ring(px, py, ang, length, w0, w_end, ring_spec, ring_angle):
    """Tapered shank leaving the pivot at `ang` degrees (0 = +x, 90 = down), then its ring."""
    rx, ry, ws, we = ring_spec
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    ex, ey = px + ux * length, py + uy * length
    shank = polygon([(px - uy * w0 / 2, py + ux * w0 / 2), (px + uy * w0 / 2, py - ux * w0 / 2),
                     (ex + uy * w_end / 2, ey - ux * w_end / 2), (ex - uy * w_end / 2, ey + ux * w_end / 2)])
    reach = rx if abs(math.cos(math.radians(ring_angle - ang))) > 0.7 else ry
    rcx, rcy = ex + ux * (reach - we * 0.6), ey + uy * (reach - we * 0.6)
    return shank | _finger_ring(rcx, rcy, rx, ry, ws, we, ring_angle)


def scissors_name(word="Leola", embolden=3.0):
    """Bodoni Moda Italic word; its L gets the pivot screw and finger rings."""
    shp, _, parts = text(font(BODONI_IT), word, 1000, 0, 0)
    L = parts[0][0]
    # the hairline foot serif left of the stem goes: the shanks take that corner
    L = L - rect(-200, -30, 36.9 + 200 - 2, 60)
    name = union_all([L] + [g for g, _, _ in parts[1:]])
    if embolden:  # sturdier hairlines for vinyl cutting and small screens
        name = name.emboldened(embolden)
    px, py = 122, -40  # pivot, inside the corner of the L
    lower = _shank_with_ring(px, py, 114, 120, 70, 40, (80, 118, 34, 12), 24)
    left = _shank_with_ring(px, py, 174, 140, 50, 36, (120, 78, 32, 11), -6)
    body = union_all([name, lower, left])
    return (body - ellipse(px, py, 32)) | ellipse(px, py, 13)


def script_name(word="Leola", embolden=5.0):
    shp, _, _ = text(font(PINYON), word, 1000, 0, 0)
    return shp.emboldened(embolden) if embolden else shp


# ------------------------------------------------------------ lockups

def lockup_kaarid(tag_size=92, tag_track=300, tag_top=150):
    """Name with the tagline hanging right-aligned from the stem of the a,
    level with the lower finger ring."""
    name = scissors_name()
    xr = 2452  # right edge of the a's stem
    cap = caps_line(TAGLINE, tag_size, tracking=tag_track, embolden=1.0)
    cap = place_top(cap.moved(xr - cap.bounds[2], 0), tag_top)
    return union_all([name, cap])


def lockup_klassik(tag_size=96, tag_track=320, rule_len=190, rule_gap=70, rule_w=6):
    """Centred: name, tagline between hairline rules, city."""
    name = script_name()
    nb = name.bounds
    cx = (nb[0] + nb[2]) / 2
    cap = caps_line(TAGLINE, tag_size, tracking=tag_track, embolden=1.0)
    cap = place_top(center_x(cap, cx), nb[3] + 120)
    cb = cap.bounds
    ry = (cb[1] + cb[3]) / 2
    city = caps_line(CITY, tag_size * 0.64, tracking=tag_track * 1.5, embolden=0.8)
    return union_all([
        name, cap,
        hairline(cb[0] - rule_gap - rule_len, cb[0] - rule_gap, ry, rule_w),
        hairline(cb[2] + rule_gap, cb[2] + rule_gap + rule_len, ry, rule_w),
        place_top(center_x(city, cx), cb[3] + 75),
    ])


def lockup_klassik_compact(tag_size=88, tag_track=300):
    """Name with the tagline right-aligned under 'eola' (used for the vertical strip)."""
    name = script_name()
    nb = name.bounds
    cap = caps_line(TAGLINE, tag_size, tracking=tag_track, embolden=1.0)
    cap = place_top(cap.moved(nb[2] - 60 - cap.bounds[2], 0), 95)
    return union_all([name, cap])


def vertical(shape):
    """Rotate 90 degrees clockwise: reads top to bottom, like the reference sign."""
    return shape.transformed(0, 1, -1, 0, 0, 0)


# ------------------------------------------------------------ seal / monogram

def text_on_circle(s, size, r, center_deg=-90, tracking=300, spec=BODONI_CAPS, bottom=False,
                   embolden=0.0):
    """Caps around a circle centred on (0,0). Top text: feet towards the centre, reading
    clockwise. Bottom text: heads towards the centre, reading left to right."""
    _, total, parts = text(font(spec), s, size, 0, 0, tracking=tracking)
    out = []
    for g, _, _ in parts:
        if g.width == 0:
            continue
        b = g.bounds
        gx = (b[0] + b[2]) / 2
        d = gx - total / 2
        if not bottom:
            ang = center_deg + math.degrees(d / r)
            gg = rotate(g.moved(-gx, -r), ang + 90)
        else:
            ang = center_deg - math.degrees(d / r)
            gg = rotate(g.moved(-gx, r - b[1]), ang - 90)
        out.append(gg)
    shp = union_all(out)
    return shp.emboldened(embolden) if embolden else shp


def _max_radius(shape, cx, cy):
    pts = [pt for _, seg in shape.path.segments for pt in seg]
    return max(math.hypot(x - cx, y - cy) for x, y in pts)


def fit_in_circle(shape, r, optical=(0, 0)):
    b = shape.bounds
    cx, cy = (b[0] + b[2]) / 2 + optical[0], (b[1] + b[3]) / 2 + optical[1]
    return shape.moved(-cx, -cy).scaled(r / _max_radius(shape, cx, cy))


def seal(center, R=560, band=150, inner_fit=0.92, optical=(0, 0)):
    """Round badge: double ring, LEOLA on top, MEESTEJUUKSUR below, mark in the middle."""
    mid = R - band / 2
    return union_all([
        ring(0, 0, R, R - 9),
        ring(0, 0, R - band, R - band - 5),
        fit_in_circle(center, (R - band) * inner_fit, optical),
        text_on_circle("LEOLA", 86, mid - 86 * 0.36, center_deg=-90, tracking=420, embolden=0.8),
        text_on_circle(TAGLINE, 66, mid - 66 * 0.34, center_deg=90, tracking=300, bottom=True,
                       embolden=0.8),
        diamond(-mid, 0, 15),
        diamond(mid, 0, 15),
    ])


def seal_kaarid():
    return seal(scissors_name("L"), inner_fit=0.9, optical=(-20, 0))


def seal_klassik():
    return seal(script_name("L"), inner_fit=0.92)
