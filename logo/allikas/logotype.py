"""Tiny type-to-outline toolkit.

Shapes text with HarfBuzz (kerning, ligatures, contextual alternates), draws the
glyph outlines into skia-pathops paths and emits clean SVG path data, so the
finished logo files are pure outlines and need no fonts installed.

Coordinates are SVG-style: y grows downward, the text baseline sits at y=0.
"""
import glob
import math
import os

import pathops
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def find_font(family_dir, pattern="*"):
    hits = sorted(glob.glob(os.path.join(FONTDIR, family_dir, pattern + ".ttf")))
    if not hits:
        raise FileNotFoundError(f"{family_dir}/{pattern}")
    return hits[0]


class Font:
    def __init__(self, path, variations=None):
        self.path = path
        self.face = hb.Face(hb.Blob.from_file_path(path))
        self.hbfont = hb.Font(self.face)
        self.upem = self.face.upem
        if variations:
            self.hbfont.set_variations(variations)
        self.tt = TTFont(path, lazy=True)

    def shape(self, text, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        feats = {"kern": True, "liga": True, "calt": True}
        if features:
            feats.update(features)
        hb.shape(self.hbfont, buf, feats)
        return [(info.codepoint, pos.x_advance, pos.x_offset, pos.y_offset)
                for info, pos in zip(buf.glyph_infos, buf.glyph_positions)]


class Shape:
    """Outlines in SVG space, with boolean ops (| union, - difference, & intersection)."""

    def __init__(self, path=None):
        self.path = path if path is not None else pathops.Path()

    @property
    def bounds(self):
        return self.path.bounds  # (xmin, ymin, xmax, ymax)

    @property
    def width(self):
        b = self.bounds
        return b[2] - b[0]

    @property
    def height(self):
        b = self.bounds
        return b[3] - b[1]

    def copy(self):
        p = pathops.Path()
        self.path.draw(p.getPen())
        return Shape(p)

    def transformed(self, a=1, b=0, c=0, d=1, e=0, f=0):
        p = pathops.Path()
        self.path.draw(TransformPen(p.getPen(), (a, b, c, d, e, f)))
        return Shape(p)

    def moved(self, dx, dy):
        return self.transformed(1, 0, 0, 1, dx, dy)

    def scaled(self, s, cx=0, cy=0):
        return self.transformed(s, 0, 0, s, cx - s * cx, cy - s * cy)

    def __or__(self, other):
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.UNION, fix_winding=True))

    def __sub__(self, other):
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.DIFFERENCE, fix_winding=True))

    def __and__(self, other):
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.INTERSECTION, fix_winding=True))

    def add(self, other):
        """Append contours without boolean ops."""
        other.path.draw(self.path.getPen())
        return self

    def emboldened(self, d):
        """Grow the outline by d on every side (thickens hairlines evenly)."""
        if d <= 0:
            return self.copy()
        st = self.copy().path
        st.stroke(2 * d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        st.convertConicsToQuads()
        return self | Shape(st)

    def simplified(self):
        p = self.copy().path
        p.simplify(fix_winding=True, keep_starting_points=False)
        return Shape(p)

    def d(self, ndigits=2):
        pen = SVGPathPen(None, ntos=lambda v: _fmt(v, ndigits))
        self.path.draw(pen)
        return pen.getCommands()


def _fmt(v, nd):
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class _Pen(BasePen):
    """HarfBuzz draw callbacks -> any fontTools pen."""

    def __init__(self, pen):
        super().__init__(None)
        self.pen = pen

    def _moveTo(self, p):
        self.pen.moveTo(p)

    def _lineTo(self, p):
        self.pen.lineTo(p)

    def _curveToOne(self, p1, p2, p3):
        self.pen.curveTo(p1, p2, p3)

    def _qCurveToOne(self, p1, p2):
        self.pen.qCurveTo(p1, p2)

    def _closePath(self):
        self.pen.closePath()

    def _endPath(self):
        self.pen.endPath()


def text(font, s, size, x=0, y=0, tracking=0, features=None):
    """Lay out `s` with its baseline at y, starting at x. size = em size.

    tracking: extra space between glyphs in 1/1000 em.
    Returns (Shape, end_x, [(glyph Shape, origin_x, glyph name), ...]).
    """
    scale = size / font.upem
    glyphs = font.shape(s, features)
    pen_x = x
    out = Shape()
    parts = []
    for gid, adv, xo, yo in glyphs:
        gp = pathops.Path()
        t = (scale, 0, 0, -scale, pen_x + xo * scale, y - yo * scale)
        font.hbfont.draw_glyph_with_pen(gid, _Pen(TransformPen(gp.getPen(), t)))
        g = Shape(gp)
        parts.append((g, pen_x, font.tt.getGlyphName(gid)))
        out.add(g)
        pen_x += adv * scale + tracking * size / 1000
    if glyphs and tracking:
        pen_x -= tracking * size / 1000
    return out, pen_x, parts


def union_all(shapes):
    acc = Shape()
    for s in shapes:
        acc.add(s)
    return acc.simplified()


def rect(x, y, w, h):
    return polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def polygon(points):
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo(points[0])
    for pt in points[1:]:
        pen.lineTo(pt)
    pen.closePath()
    return Shape(p)


def ellipse(cx, cy, rx, ry=None):
    """Ellipse from four cubic arcs."""
    ry = rx if ry is None else ry
    k = 0.5522847498
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo((cx + rx, cy))
    pen.curveTo((cx + rx, cy + k * ry), (cx + k * rx, cy + ry), (cx, cy + ry))
    pen.curveTo((cx - k * rx, cy + ry), (cx - rx, cy + k * ry), (cx - rx, cy))
    pen.curveTo((cx - rx, cy - k * ry), (cx - k * rx, cy - ry), (cx, cy - ry))
    pen.curveTo((cx + k * rx, cy - ry), (cx + rx, cy - k * ry), (cx + rx, cy))
    pen.closePath()
    return Shape(p)


def ring(cx, cy, r_out, r_in):
    return ellipse(cx, cy, r_out) - ellipse(cx, cy, r_in)


def rotate(shape, deg, cx=0, cy=0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return shape.transformed(c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy)
