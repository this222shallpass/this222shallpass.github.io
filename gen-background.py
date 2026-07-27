#!/usr/bin/env python3
"""
Background drawing: a brutalist complex from above, exploded along a
diagonal axis. Almost entirely hairline construction geometry, with a
few very bold strokes and arcs carrying the contrast.
Portrait 900x1400.
"""
import math
import random

W, H = 900, 1400
INK = "#1a1a1a"
random.seed(11)
out = []
add = out.append


def esc(**kw):
    return " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())


def line(x1, y1, x2, y2, w=0.4, **kw):
    add(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke-width="{w}" {esc(**kw)}/>')


def path(d, w=0.4, **kw):
    add(f'<path d="{d}" stroke-width="{w}" {esc(**kw)}/>')


def circ(cx, cy, r, w=0.4, **kw):
    add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke-width="{w}" {esc(**kw)}/>')


def dot(cx, cy, r=1.8, op=1.0, fill=INK):
    add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="none" opacity="{op}"/>')


def poly(pts, w=0.5, close=True, **kw):
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + ("Z" if close else "")
    path(d, w, **kw)


def arc(cx, cy, r, a0, a1, w=0.4, **kw):
    """Arc from a0 to a1 degrees, drawn as a polyline so widths stay honest."""
    n = max(8, int(abs(a1 - a0) / 2))
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(pts, w, close=False, **kw)


def rot(p, a, o):
    """Rotate point p by a degrees about origin o."""
    ar = math.radians(a)
    dx, dy = p[0] - o[0], p[1] - o[1]
    return (o[0] + dx * math.cos(ar) - dy * math.sin(ar),
            o[1] + dx * math.sin(ar) + dy * math.cos(ar))


def plate(cx, cy, w_, h_, ang, hatch=0, hw=0.32, sw=0.6, hatch_ang=None):
    """A thin roof plate: outline plus optional fine parallel grain."""
    o = (cx, cy)
    corners = [(cx - w_ / 2, cy - h_ / 2), (cx + w_ / 2, cy - h_ / 2),
               (cx + w_ / 2, cy + h_ / 2), (cx - w_ / 2, cy + h_ / 2)]
    poly([rot(p, ang, o) for p in corners], sw)
    if hatch:
        ha = ang if hatch_ang is None else hatch_ang
        step = h_ / (hatch + 1)
        for k in range(1, hatch + 1):
            y = cy - h_ / 2 + k * step
            p1 = rot((cx - w_ / 2 + 2, y), ang, o)
            p2 = rot((cx + w_ / 2 - 2, y), ang, o)
            if hatch_ang is not None:
                p1 = rot(p1, ha - ang, o)
                p2 = rot(p2, ha - ang, o)
            line(*p1, *p2, hw)


def comb(x, y, n, length, gap, ang, w=0.5):
    """The little stair / ladder runs scattered through the drawing."""
    o = (x, y)
    for k in range(n):
        p1 = rot((x, y + k * gap), ang, o)
        p2 = rot((x + length, y + k * gap), ang, o)
        line(*p1, *p2, w)
    p1, p2 = rot((x, y), ang, o), rot((x, y + (n - 1) * gap), ang, o)
    line(*p1, *p2, 0.35)
    p1, p2 = rot((x + length, y), ang, o), rot((x + length, y + (n - 1) * gap), ang, o)
    line(*p1, *p2, 0.35)


def fan(x, y, r0, r1, a0, a1, n, w=0.3):
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * k / max(1, n - 1))
        line(x + r0 * math.cos(a), y + r0 * math.sin(a),
             x + r1 * math.cos(a), y + r1 * math.sin(a), w)


def cross(x, y, s=7, w=0.5):
    line(x - s, y, x + s, y, w)
    line(x, y - s, x, y + s, w)


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add('<!-- background drawing: brutalist complex, exploded on a diagonal -->')
add(f'<g fill="none" stroke="{INK}" stroke-linecap="round">')

# the whole composition sits on a diagonal axis, pulled in slightly so
# nothing runs off the right edge of the sheet
add('<g transform="rotate(-34 450 700) translate(450 700) scale(0.93) translate(-450 -700)">')

# ================================================== faint construction layer
add('<g opacity="0.3">')

# site boundary — an irregular polygon of long straight runs
SITE = [(120, 190), (470, 90), (742, 250), (800, 560), (690, 830),
        (742, 1120), (520, 1290), (250, 1210), (110, 940), (170, 520)]
poly(SITE, 0.35, stroke_dasharray="10 7")
poly([(x * 0.82 + 80, y * 0.82 + 120) for x, y in SITE], 0.3, stroke_dasharray="3 6")

# long lines radiating from a point well off the canvas
VP = (-260, -180)
for k in range(16):
    a = math.radians(18 + k * 3.4)
    line(VP[0], VP[1], VP[0] + 1900 * math.cos(a), VP[1] + 1900 * math.sin(a),
         0.28, stroke_dasharray="14 9")

# dotted construction circles
for (cx, cy, r) in ((450, 700, 306), (368, 512, 190), (596, 918, 232), (430, 1080, 140)):
    circ(cx, cy, r, 0.35, stroke_dasharray="2 7")

# a couple of full hairline circles
circ(450, 700, 232, 0.3)
circ(596, 918, 148, 0.3)

add('</g>')

# ================================================= the fragments (hairline)
# a loose cluster of plates drifting apart along the axis
plate(392, 300, 210, 118, 6, hatch=9)
plate(300, 470, 150, 250, -4, hatch=11)
plate(548, 452, 132, 132, 45)
plate(470, 640, 300, 96, 8, hatch=7)
plate(360, 812, 168, 168, -2, hatch=6)
plate(628, 800, 190, 104, 26, hatch=5)
plate(470, 980, 244, 88, -6, hatch=6)
plate(352, 1116, 178, 118, 10, hatch=5)
plate(636, 1078, 120, 120, 45)

# courtyard voids, drawn as simple inner outlines
plate(392, 300, 96, 48, 6)
plate(300, 470, 66, 108, -4)
plate(360, 812, 72, 72, -2)

# the stair combs
comb(250, 356, 9, 62, 7, 18)
comb(556, 566, 7, 48, 8, -30)
comb(214, 640, 11, 54, 7, 4)
comb(600, 700, 8, 44, 8, 62)
comb(392, 906, 10, 58, 7, -14)
comb(660, 962, 6, 40, 8, 34)
comb(268, 1044, 8, 50, 7, 22)
comb(508, 1178, 9, 56, 7, -8)

# sprays of thin lines — the "shift" fans
fan(450, 700, 40, 300, -120, -46, 13)
fan(596, 918, 30, 210, 100, 168, 11)
fan(300, 470, 24, 170, -20, 44, 9)

# small drums
for (cx, cy, r) in ((548, 452, 34), (360, 812, 26), (636, 1078, 22), (214, 900, 30)):
    circ(cx, cy, r, 0.6)
    circ(cx, cy, r * 0.42, 0.4)
    dot(cx, cy, 1.6)

# registration crosses
for (x, y) in ((330, 244), (612, 386), (238, 742), (700, 880), (410, 1042), (556, 1250)):
    cross(x, y, 7, 0.45)

# ------------------------------------------------------------ sine elements
def sine(y0, amp, wavelen, x0, x1, w=0.4, phase=0.0, dash=None):
    pts = [(x0 + k, y0 + amp * math.sin(k / wavelen * 2 * math.pi + phase))
           for k in range(x1 - x0 + 1)]
    kw = {"stroke_dasharray": dash} if dash else {}
    poly(pts, w, close=False, **kw)


# long wavelengths — these should read as sweeping drawn curves, not as
# a signal trace sitting on top of the plan
sine(1252, 34, 620, 90, 830, 0.7)
sine(1252, 11, 190, 90, 830, 0.3, phase=math.pi / 3)
sine(198, 26, 700, 120, 800, 0.5, phase=math.pi)
sine(902, 44, 760, 130, 790, 0.35, dash="3 6")

# ===================================================== the bold black marks
# a handful of heavy strokes doing all the contrast work
add(f'<g stroke="{INK}" stroke-linecap="butt">')
line(346, 402, 604, 690, 4.2)
line(268, 968, 452, 1128, 3.4)
line(590, 250, 668, 342, 2.8)

arc(450, 700, 258, 104, 246, 4.4)
arc(596, 918, 176, -66, 84, 3.8)
arc(330, 470, 132, 122, 286, 3.0)
arc(470, 1160, 150, -156, -36, 2.6)

add('</g>')

add('</g>')  # end diagonal rotation

# ------------------------------------------------- outlier, in sheet coords
# a fragment adrift in the empty top-right, tethered back to the complex by
# long hairlines. placed outside the rotation so it lands exactly.
add('<g opacity="0.45">')
for (x1, y1) in ((452, 470), (486, 556), (398, 424)):
    line(700, 236, x1, y1, 0.3, stroke_dasharray="13 8")
add('</g>')
add(f'<g stroke="{INK}" stroke-linecap="butt">')
arc(700, 236, 96, 128, 292, 4.0)
add('</g>')
arc(700, 236, 118, 128, 292, 0.35, stroke_dasharray="2 7")
cross(700, 236, 9, 0.5)
comb(742, 150, 6, 42, 7, 28)

add('</g>')  # end ink group

# accents, left upright so they read as marks on the sheet rather than plan
add('<rect x="176" y="252" width="15" height="15" fill="#d8402f"/>')
add('<rect x="706" y="1096" width="15" height="15" fill="#d8402f"/>')

add('</svg>')

dest = "/Users/sawa/Desktop/cluadeCodeFolder/this222shallpass.github.io/images/bg-brutalist.svg"
s = "\n".join(out)
open(dest, "w", encoding="utf-8").write(s)
print("wrote", dest, len(s) // 1024, "KB")
