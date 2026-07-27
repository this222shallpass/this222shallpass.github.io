#!/usr/bin/env python3
"""
Generates the background drawings: a brutalist complex in exploded
axonometric. Each volume is drawn twice — a ghost outline at its
original position and the piece itself where it has shifted to — tied
together by hairline leaders. Circles project to ellipses, stairs climb
in z, and a few bold screen-space arcs carry the contrast.

    python3 gen-background.py            # all 8 variants
    python3 gen-background.py 3          # just variant 3

Variants differ in view angle, seed and arrangement. Output: images/bg-NN.svg
"""
import math
import random
import sys
import os

SHEET_W, SHEET_H = 900, 1400
MARGIN = 46

INK = "#1a1a1a"
GHOST = "#c2748c"      # "was here" construction lines
AXIS = "#7d93c4"       # shift-in-axis marks
ACCENT = "#d8402f"


class Drawing:
    def __init__(self, ax, ay, seed):
        self.ax, self.ay = math.radians(ax), math.radians(ay)
        self.rng = random.Random(seed)
        self.parts = []
        self.pts = []

    # ---------------------------------------------------------- projection
    def p(self, x, y, z=0.0, rec=True):
        """Project a world point. rec=False keeps it out of the fit bounds —
        for lines that are meant to run off the edge of the sheet."""
        X = x * math.cos(self.ax) - y * math.cos(self.ay)
        Y = x * math.sin(self.ax) + y * math.sin(self.ay) - z
        if rec:
            self.pts.append((X, Y))
        return X, Y

    # -------------------------------------------------------------- output
    def emit(self, s):
        self.parts.append(s)

    def poly(self, pts, w=0.4, color=INK, close=True, dash=None, op=None, cap="round"):
        d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + ("Z" if close else "")
        a = (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
             f'stroke-linecap="{cap}"')
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if op is not None:
            a += f' opacity="{op}"'
        self.emit(a + "/>")

    def seg(self, a, b, w=0.4, **kw):
        self.poly([a, b], w, close=False, **kw)

    def dot(self, pt, r=1.6, color=INK, op=1.0):
        self.emit(f'<circle cx="{pt[0]:.1f}" cy="{pt[1]:.1f}" r="{r}" fill="{color}" '
                  f'stroke="none" opacity="{op}"/>')

    def fill(self, pts, color, op):
        d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
        self.emit(f'<path d="{d}" fill="{color}" stroke="none" opacity="{op}"/>')

    # ---------------------------------------------------------- primitives
    def slab(self, ox, oy, w, d, z, h, hatch=7, ghost_at=None, sw=0.55):
        """A volume: hatched top, the two visible sides, hard edges."""
        top = [self.p(ox, oy, z + h), self.p(ox + w, oy, z + h),
               self.p(ox + w, oy + d, z + h), self.p(ox, oy + d, z + h)]
        self.fill(top, "#ffffff", 0.62)
        self.poly(top, sw)

        if h > 0:
            front = [self.p(ox, oy + d, z + h), self.p(ox + w, oy + d, z + h),
                     self.p(ox + w, oy + d, z), self.p(ox, oy + d, z)]
            side = [self.p(ox + w, oy, z + h), self.p(ox + w, oy + d, z + h),
                    self.p(ox + w, oy + d, z), self.p(ox + w, oy, z)]
            for face in (front, side):
                self.fill(face, "#ffffff", 0.5)
                self.poly(face, sw * 0.8)
            self.fill(side, INK, 0.05)
            # shutter lines down the front face
            for k in range(1, 6):
                t = k / 6
                self.seg(self.p(ox + w * t, oy + d, z + h),
                         self.p(ox + w * t, oy + d, z), 0.25)

        if hatch:
            for k in range(1, hatch + 1):
                t = k / (hatch + 1)
                self.seg(self.p(ox + 2, oy + d * t, z + h),
                         self.p(ox + w - 2, oy + d * t, z + h), 0.28)

        if ghost_at:
            gx, gy = ghost_at
            g = [self.p(gx, gy, 0), self.p(gx + w, gy, 0),
                 self.p(gx + w, gy + d, 0), self.p(gx, gy + d, 0)]
            self.poly(g, 0.3, GHOST, dash="4 4", op=0.55)
            for a, b in zip(top, g):
                self.seg(a, b, 0.28, color=GHOST, dash="2 6", op=0.5)

    def court(self, ox, oy, w, d, z):
        self.poly([self.p(ox, oy, z), self.p(ox + w, oy, z),
                   self.p(ox + w, oy + d, z), self.p(ox, oy + d, z)], 0.45)

    def stair(self, ox, oy, n, run, wide, rise, z=0.0, along="x"):
        """A flight climbing in z."""
        for k in range(n + 1):
            t, zz = k * run, z + k * rise
            if along == "x":
                a, b = self.p(ox + t, oy, zz), self.p(ox + t, oy + wide, zz)
                self.seg(a, b, 0.42)
                if k < n:
                    self.seg(a, self.p(ox + t, oy, zz + rise), 0.3)
                    self.seg(b, self.p(ox + t, oy + wide, zz + rise), 0.3)
            else:
                a, b = self.p(ox, oy + t, zz), self.p(ox + wide, oy + t, zz)
                self.seg(a, b, 0.42)
                if k < n:
                    self.seg(a, self.p(ox, oy + t, zz + rise), 0.3)
                    self.seg(b, self.p(ox + wide, oy + t, zz + rise), 0.3)
        if along == "x":
            self.seg(self.p(ox, oy, z), self.p(ox + n * run, oy, z + n * rise), 0.5)
            self.seg(self.p(ox, oy + wide, z),
                     self.p(ox + n * run, oy + wide, z + n * rise), 0.5)
        else:
            self.seg(self.p(ox, oy, z), self.p(ox, oy + n * run, z + n * rise), 0.5)
            self.seg(self.p(ox + wide, oy, z),
                     self.p(ox + wide, oy + n * run, z + n * rise), 0.5)

    def ring(self, cx, cy, r, z=0.0, w=0.4, color=INK, dash=None, op=None, n=72):
        pts = [self.p(cx + r * math.cos(2 * math.pi * k / n),
                      cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n + 1)]
        self.poly(pts, w, color, close=False, dash=dash, op=op)

    def radial(self, cx, cy, r0, r1, n, z=0.0, w=0.28):
        for k in range(n):
            a = 2 * math.pi * k / n
            self.seg(self.p(cx + r0 * math.cos(a), cy + r0 * math.sin(a), z),
                     self.p(cx + r1 * math.cos(a), cy + r1 * math.sin(a), z), w)

    def sine_path(self, x0, x1, y0, amp, wavelen, z=0.0, w=0.45, phase=0.0, dash=None):
        n = 120
        pts = []
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / n
            pts.append(self.p(x, y0 + amp * math.sin(x / wavelen * 2 * math.pi + phase), z))
        self.poly(pts, w, close=False, dash=dash)

    def wall(self, x0, y0, x1, y1, h, z=0.0):
        q = [self.p(x0, y0, z), self.p(x1, y1, z),
             self.p(x1, y1, z + h), self.p(x0, y0, z + h)]
        self.fill(q, "#ffffff", 0.45)
        self.poly(q, 0.45)

    def cross(self, pt, s=7, w=0.45, color=INK):
        self.seg((pt[0] - s, pt[1]), (pt[0] + s, pt[1]), w, color=color)
        self.seg((pt[0], pt[1] - s), (pt[0], pt[1] + s), w, color=color)


# ===========================================================================
def build(v):
    d = Drawing(v["ax"], v["ay"], v["seed"])
    rng = d.rng
    G, n = v["grid"], v["gridn"]
    span = n * G

    # the ground grid is clipped to the same diagonal band as the buildings —
    # a full square grid would project to a wide diamond and flatten everything
    bw = v["band"] * G

    def clamp(a):
        return max(0.0, min(span, a))

    for i in range(n + 1):
        t = i * G
        d.seg(d.p(clamp(t - bw), t), d.p(clamp(t + bw), t), 0.22, op=0.4, dash="9 7")
        d.seg(d.p(t, clamp(t - bw)), d.p(t, clamp(t + bw)), 0.22, op=0.4, dash="9 7")

    placed = []
    for (cx, cy, w, dp, z, h, sh) in v["slabs"]:
        ghost = (cx - sh[0], cy - sh[1]) if sh else None
        d.slab(cx, cy, w, dp, z, h, hatch=v["hatch"], ghost_at=ghost)
        placed.append((cx, cy, w, dp, z, h))
        if w > 120 and dp > 90 and rng.random() < 0.7:
            d.court(cx + w * 0.28, cy + dp * 0.28, w * 0.4, dp * 0.4, z + h)

    for (cx, cy, w, dp, z, h) in placed[:3]:
        if w < 110:
            continue
        for i in range(3):
            for j in range(2):
                x, y = cx + w * (0.22 + i * 0.26), cy + dp * (0.28 + j * 0.34)
                d.poly([d.p(x, y, z + h), d.p(x + 12, y, z + h),
                        d.p(x + 12, y + 12, z + h), d.p(x, y + 12, z + h)], 0.35)

    for s in v["stairs"]:
        d.stair(*s)
    for w_ in v["walls"]:
        d.wall(*w_)

    for (cx, cy, r, z) in v["rings"]:
        d.ring(cx, cy, r, z, 0.5)
        d.ring(cx, cy, r * 0.62, z, 0.32)
        d.ring(cx, cy, r * 1.3, z, 0.28, dash="2 7")
        d.radial(cx, cy, r * 0.62, r, 24, z)
        d.dot(d.p(cx, cy, z), 1.8)

    # columns under anything that floats, so the elevated pieces read as built
    for (cx, cy, w, dp, z, h) in placed:
        if z <= 0:
            continue
        for fx in (0.12, 0.5, 0.88):
            for fy in (0.16, 0.84):
                x, y = cx + w * fx, cy + dp * fy
                d.seg(d.p(x, y, 0), d.p(x, y, z), 0.3)
                d.dot(d.p(x, y, 0), 1.2, INK, 0.55)

    # sine paths run *along* the band, threading the whole site
    for (off, amp, wl, wid, dash) in ((-bw * 0.5, G * 0.5, span * 0.55, 0.5, None),
                                      (-bw * 0.5, G * 0.16, span * 0.17, 0.28, None),
                                      (bw * 0.6, G * 0.62, span * 0.7, 0.35, "4 5")):
        pts = []
        for k in range(121):
            t = span * k / 120
            pts.append(d.p(t, t + off + amp * math.sin(t / wl * 2 * math.pi)))
        d.poly(pts, wid, close=False, dash=dash)

    for _ in range(v["axisn"]):
        t = rng.uniform(0, span)
        x, y = t, t + rng.uniform(-bw, bw)
        d.cross(d.p(x, y, 0), 5, 0.4, AXIS)
        d.dot(d.p(x, y, 0), 1.4, AXIS, 0.8)

    # long hairlines shooting along the axis, well past the site edges
    for _ in range(v["rays"]):
        off = rng.uniform(-bw * 1.4, bw * 1.4)
        d.seg(d.p(-span * 0.3, -span * 0.3 + off, rec=False),
              d.p(span * 1.3, span * 1.3 + off, rec=False),
              0.25, op=0.45, dash="14 9")

    return d


def render(v, path):
    d = build(v)
    xs = [p[0] for p in d.pts]
    ys = [p[1] for p in d.pts]
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    s = min((SHEET_W - 2 * MARGIN) / bw, (SHEET_H - 2 * MARGIN) / bh) * v["zoom"]
    tx = SHEET_W / 2 - (min(xs) + bw / 2) * s
    ty = SHEET_H / 2 - (min(ys) + bh / 2) * s

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SHEET_W} {SHEET_H}" '
           f'width="{SHEET_W}" height="{SHEET_H}">',
           f'<!-- variant {v["name"]} — generated by gen-background.py -->',
           f'<g transform="rotate({v["spin"]} {SHEET_W // 2} {SHEET_H // 2}) '
           f'translate({tx:.1f} {ty:.1f}) scale({s:.4f})">']
    out += d.parts
    out.append('</g>')

    out.append(f'<g fill="none" stroke="{INK}" stroke-linecap="butt">')
    for (cx, cy, r, a0, a1, w) in v["arcs"]:
        n = max(10, int(abs(a1 - a0) / 2))
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
               for k in range(n + 1)]
        out.append('<path d="M' + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
                   + f'" stroke-width="{w:.1f}"/>')
    for (x1, y1, x2, y2, w) in v["bolds"]:
        out.append(f'<path d="M{x1:.0f} {y1:.0f}L{x2:.0f} {y2:.0f}" stroke-width="{w:.1f}"/>')
    out.append('</g>')

    for (x, y) in v["squares"]:
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="14" height="14" fill="{ACCENT}"/>')
    for (x, y, r) in v["circles"]:
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="none" '
                   f'stroke="{ACCENT}" stroke-width="1.2"/>')

    out.append('</svg>')
    svg = "\n".join(out)
    open(path, "w", encoding="utf-8").write(svg)
    return len(svg)


# ===========================================================================
AX = [30, 26, 34, 30, 22, 38, 28, 32]
AY = [30, 34, 26, 22, 30, 24, 38, 28]
SPIN = [0, -4, 5, -7, 3, -2, 7, -5]
HATCH = [7, 9, 6, 8, 10, 7, 9, 6]


def variant(i):
    """Eight arrangements — angle, seed and layout all differ."""
    rng = random.Random(1000 + i * 17)
    G, n = 100, 9
    span = n * G

    # In this projection screen-x follows (x - y) and screen-y follows (x + y),
    # so a site laid out on the diagonal projects tall — which is what a
    # portrait sheet wants. Keep |a - b| small and let (a + b) run.
    band = v_band = 2 + i % 2
    cells = [(a, b) for a in range(n) for b in range(n) if abs(a - b) <= band]
    rng.shuffle(cells)

    slabs = []
    for (a, b) in cells[: 15 + i % 4]:
        sh = (rng.uniform(-64, 64), rng.uniform(-64, 64)) if rng.random() < 0.72 else None
        slabs.append((a * G + rng.uniform(-16, 16), b * G + rng.uniform(-16, 16),
                      rng.choice([80, 100, 130, 165]), rng.choice([70, 95, 125]),
                      rng.choice([0, 0, 0, 28, 64]), rng.choice([0, 0, 24, 38, 58, 88]), sh))

    def on_band():
        a = rng.uniform(0, span)
        return a, a + rng.uniform(-band * G, band * G)

    stairs = []
    for _ in range(5 + i % 3):
        sx, sy = on_band()
        stairs.append((sx, sy, rng.randint(7, 13), 10, rng.choice([30, 42, 54]), 6.5,
                       rng.choice([0, 0, 28]), rng.choice(["x", "y"])))

    walls = []
    for _ in range(5):
        x0, y0 = on_band()
        ln, h = rng.uniform(80, 190), rng.choice([26, 44, 66])
        walls.append((x0, y0, x0 + ln, y0, h, 0) if rng.random() < 0.5
                     else (x0, y0, x0, y0 + ln, h, 0))

    rings = []
    for _ in range(3):
        cx, cy = on_band()
        rings.append((cx, cy, rng.choice([70, 95, 130]), 0))

    # bold overlay marks — the cluster auto-fits to the sheet centre, so aim
    # these at the middle and let them cut across it
    arcs = []
    for _ in range(2 + i % 2):
        a0 = rng.uniform(0, 360)
        arcs.append((rng.uniform(330, 570), rng.uniform(480, 940), rng.uniform(150, 290),
                     a0, a0 + rng.uniform(100, 170), rng.uniform(2.4, 3.8)))
    bolds = []
    for _ in range(2):
        x1, y1 = rng.uniform(250, 640), rng.uniform(400, 1000)
        bolds.append((x1, y1, x1 + rng.uniform(-240, 240), y1 + rng.uniform(-260, 260),
                      rng.uniform(2.2, 3.6)))

    return {
        "name": f"{i:02d}", "seed": 1000 + i * 17,
        "ax": AX[i - 1], "ay": AY[i - 1], "spin": SPIN[i - 1], "hatch": HATCH[i - 1],
        "zoom": 1.0, "grid": G, "gridn": n,
        "slabs": slabs, "stairs": stairs, "walls": walls, "rings": rings,
        "axisn": 10, "rays": 5, "band": band, "arcs": arcs, "bolds": bolds,
        "squares": [(rng.uniform(120, 740), rng.uniform(180, 1180)) for _ in range(2)],
        "circles": [(rng.uniform(200, 700), rng.uniform(300, 1100), 11)],
    }


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    which = [int(sys.argv[1])] if len(sys.argv) > 1 else range(1, 9)
    for i in which:
        p = os.path.join(here, "images", f"bg-{i:02d}.svg")
        print(f"bg-{i:02d}.svg  {render(variant(i), p) // 1024} KB")
