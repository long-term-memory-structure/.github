#!/usr/bin/env python3
"""The before-and-after meme for the long-term-memory-structure profile README.

His design (2026-11-23): a graph that grows over time; red = the past, already
written; green = the future, not yet written.  BEFORE: the whole graph, red and
green, inside the confines of one window.  AFTER: the red part moved out of the
window.

Red and green are told apart by more than colour: written nodes are solid
discs joined by solid lines; not-yet-written nodes are hollow rings with dashed
outlines, joined by dashed lines.

Writes meme-light.svg and meme-dark.svg next to this file and renders each to a
2000-px-wide PNG with rsvg-convert.  Deterministic: the layout draws only from
random.Random(seed).random(), a sequence Python keeps the same across versions.
Needs rsvg-convert and the Fira Sans family (SIL OFL): Fira Sans Condensed
Heavy for the captions, Fira Sans Medium and SemiBold for the rest.

    python3 meme.py
"""
import math
import pathlib
import random
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

# ---- canvas -----------------------------------------------------------------
W = 2000
M = 44                      # outer margin
CAP = 150                   # caption band above each row
TB = 72                     # window title bar
CH = 300                    # window content height
WW = 800                    # window width: the SAME window in both rows
WH = TB + CH
ROWGAP = 40
H = M + CAP + WH + ROWGAP + CAP + WH + M
WIN = ((W - WW) / 2, M + CAP),                        # BEFORE: one window, centred
WIN += ((W - M - WW, M + CAP + WH + ROWGAP + CAP),)   # AFTER: window right, the red outside it

R = 14                      # node radius
PAD = R + 3                 # red nodes press against the frame
GAP = 6                     # space between neighbouring red nodes

# The green's corner in BEFORE: the right triangle at the content's bottom-right
# corner, legs A (along the bottom) and B (up the right side).
A, B = 230, 165
HYP = math.hypot(A, B)
DEPTH_MAX = A * B / HYP     # from the hypotenuse to the corner
U = (A / HYP, -B / HYP)     # along the hypotenuse, up and to the right
N = (B / HYP, A / HYP)      # across it, into the corner
HYP_MID = (WW - A / 2, CH - B / 2)
HYP_DEG = math.degrees(math.atan2(-B, A))
T_CORNER = (A * A - B * B) / (2 * HYP)   # where the corner's altitude meets the hypotenuse

THEMES = {
    "light": dict(
        bg="#f3f0e8", frame="#1d1d1f", titlebar="#e4e0d6", content="#ffffff",
        dot="#b3ada1", title="#4d4a44", ink="#1d1d1f",
        red="#b81d24", green="#23a55a",
        cap_fill="#ffffff", cap_stroke="#000000",
    ),
    "dark": dict(
        bg="#16191e", frame="#aab2bd", titlebar="#2a3038", content="#0f1217",
        dot="#5d6670", title="#c3cad3", ink="#e8ebef",
        red="#d93a42", green="#4cc777",
        cap_fill="#ffffff", cap_stroke="#000000",
    ),
}


# ---- the graph --------------------------------------------------------------
def depth(x, y):
    """Signed distance into the green's corner: > 0 inside the triangle."""
    return ((x - HYP_MID[0]) * N[0] + (y - HYP_MID[1]) * N[1])


def on_line(t, d):
    """The point t along the hypotenuse from its midpoint, d into the corner."""
    return (HYP_MID[0] + t * U[0] + d * N[0], HYP_MID[1] + t * U[1] + d * N[1])


def poisson(rng, box, dmin, tries, keep=lambda x, y: True, seed_pts=()):
    """Dart throwing: points in box, no two closer than dmin."""
    x0, y0, x1, y1 = box
    pts = list(seed_pts)
    for _ in range(tries):
        x = x0 + (x1 - x0) * rng.random()
        y = y0 + (y1 - y0) * rng.random()
        if not keep(x, y):
            continue
        if all((x - px) ** 2 + (y - py) ** 2 >= dmin * dmin for px, py in pts):
            pts.append((x, y))
    return pts


def tree(pts, root):
    """Prim's minimum spanning tree from root: short edges only, one graph."""
    d2 = lambda a, b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
    best = {i: (d2(pts[root], pts[i]), root) for i in range(len(pts)) if i != root}
    edges = []
    while best:
        i = min(best, key=lambda k: best[k][0])
        edges.append((best.pop(i)[1], i))
        for k in best:
            d = d2(pts[i], pts[k])
            if d < best[k][0]:
                best[k] = (d, i)
    return edges


def inside(x, y):
    return PAD <= x <= WW - PAD and PAD <= y <= CH - PAD


def red_graph():
    """The past: wall to wall, a row of it pressing on the green's corner."""
    step = 2 * R + GAP
    wall = [on_line(t, -(R + 4)) for t in range(-int(HYP), int(HYP), step)]
    wall = [p for p in wall if inside(*p)]
    rng = random.Random(7)
    keep = lambda x, y: depth(x, y) <= -(R + 4)
    pts = poisson(rng, (PAD, PAD, WW - PAD, CH - PAD), step, 40000, keep, seed_pts=wall)
    root = min(range(len(pts)), key=lambda i: pts[i][0] + abs(pts[i][1] - CH / 2))
    # the newest written node: on the row facing the corner, nearest its middle
    front = min(range(len(wall)), key=lambda i: (wall[i][0] - HYP_MID[0]) ** 2 + (wall[i][1] - HYP_MID[1]) ** 2)
    return pts, tree(pts, root), front


# the future in BEFORE: flattened rings stacked into the corner.  Each row is
# (offset along the hypotenuse from the row's centre, depth into the corner, rx);
# a row's centre follows the corner's altitude, so the stack reaches the tip.
CRUSHED = [(0, 20, 27), (-62, 20, 27), (62, 20, 27),
           (-52, 44, 25), (0, 44, 25), (52, 44, 25),
           (-24, 68, 22), (24, 68, 22),
           (0, 92, 18)]
CRUSHED_EDGES = [(0, 1), (0, 2), (1, 3), (0, 4), (2, 5), (4, 6), (5, 7), (6, 8)]


def green_room(front_y):
    """AFTER: the future, with room.  Its first node sits just inside the window."""
    rng = random.Random(11)
    first = (60.0, front_y)
    pts = poisson(rng, (60, 50, WW * 0.72, CH - 50), 98, 4000, seed_pts=[first])
    return pts, tree(pts, 0)


# ---- drawing ----------------------------------------------------------------
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def red_node(x, y, T, ring):
    """A solid disc; the ring is the colour of the surface under it."""
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{R}" fill="{T["red"]}" '
            f'stroke="{ring}" stroke-width="3"/>')


def green_node(x, y, T, rx=R, ry=R, rot=0.0):
    return (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}" '
            f'transform="rotate({f(rot)} {f(x)} {f(y)})" fill="{T["content"]}" '
            f'stroke="{T["green"]}" stroke-width="5" stroke-dasharray="7 4.5"/>')


def red_edge(a, b, T):
    return (f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["red"]}" stroke-width="6" stroke-linecap="round"/>')


def green_edge(a, b, T, width=5):
    return (f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["green"]}" stroke-width="{width}" stroke-dasharray="12 9"/>')


def window(x, y, T):
    out = [
        f'<rect x="{f(x)}" y="{y}" width="{WW}" height="{WH}" rx="18" fill="{T["content"]}"/>',
        f'<path d="M{f(x)} {y + TB} V{y + 18} a18 18 0 0 1 18 -18 H{f(x + WW - 18)} '
        f'a18 18 0 0 1 18 18 V{y + TB} Z" fill="{T["titlebar"]}"/>',
        f'<line x1="{f(x)}" y1="{y + TB}" x2="{f(x + WW)}" y2="{y + TB}" stroke="{T["frame"]}" stroke-width="4"/>',
    ]
    for i in range(3):
        out.append(f'<circle cx="{f(x + 40 + 36 * i)}" cy="{y + TB / 2}" r="12" fill="{T["dot"]}"/>')
    out.append(f'<text x="{f(x + WW / 2)}" y="{y + TB / 2 + 13}" text-anchor="middle" '
               f'font-family="Fira Sans" font-weight="500" font-size="38" fill="{T["title"]}">'
               f'context window</text>')
    return out


def content_clip(cid, x, y, T):
    """The window's content area (below the title bar, rounded at the bottom)."""
    top, bot = y + TB, y + WH
    return (f'<defs><clipPath id="{cid}"><path d="M{f(x)} {top} H{f(x + WW)} V{bot - 18} '
            f'a18 18 0 0 1 -18 18 H{f(x + 18)} a18 18 0 0 1 -18 -18 Z" fill="{T['content']}"/></clipPath></defs>')


def frame(x, y, T):
    return (f'<rect x="{f(x)}" y="{y}" width="{WW}" height="{WH}" rx="18" fill="none" '
            f'stroke="{T["frame"]}" stroke-width="5"/>')


def caption(text, cx, baseline, T, size=124):
    common = (f'x="{f(cx)}" y="{f(baseline)}" text-anchor="middle" font-family="Fira Sans Condensed" '
              f'font-weight="900" font-size="{size}" letter-spacing="5"')
    return [
        f'<text {common} fill="{T["cap_stroke"]}" stroke="{T["cap_stroke"]}" stroke-width="18" '
        f'stroke-linejoin="round">{text}</text>',
        f'<text {common} fill="{T["cap_fill"]}">{text}</text>',
    ]


def label(text, x, y, T, size=54, anchor="middle", weight=600):
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="Fira Sans" '
            f'font-weight="{weight}" font-size="{size}" fill="{T["ink"]}">{text}</text>')


def arrow(x1, y1, x2, y2, bend, T, width=5):
    """A curved pointer in ink from (x1, y1) to (x2, y2); bend moves the control point."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    cx, cy = mx - dy * bend, my + dx * bend
    tx, ty = x2 - cx, y2 - cy                       # tangent at the tip
    n = math.hypot(tx, ty)
    ux, uy = tx / n, ty / n
    L, Wd = 26, 13
    bx, by = x2 - ux * L, y2 - uy * L
    head = f"{f(x2)},{f(y2)} {f(bx - uy * Wd)},{f(by + ux * Wd)} {f(bx + uy * Wd)},{f(by - ux * Wd)}"
    return [f'<path d="M{f(x1)} {f(y1)} Q{f(cx)} {f(cy)} {f(bx)} {f(by)}" fill="none" '
            f'stroke="{T["ink"]}" stroke-width="{width}" stroke-linecap="round"/>',
            f'<polygon points="{head}" fill="{T["ink"]}"/>']


def build(theme):
    T = THEMES[theme]
    reds, red_edges, front = red_graph()
    fx, fy = reds[front]

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" rx="28" fill="{T["bg"]}"/>']

    # ---- BEFORE: the whole graph inside the one window ---------------------
    wx, wy = WIN[0]
    out += caption("BEFORE", W / 2, wy - 30, T)
    out += window(wx, wy, T)
    out.append(content_clip("before", wx, wy, T))
    out.append('<g clip-path="url(#before)">')
    P = lambda p: (wx + p[0], wy + TB + p[1])
    crushed = [on_line(t + T_CORNER * d / DEPTH_MAX, d) for t, d, _ in CRUSHED]
    for a, b in red_edges:
        out.append(red_edge(P(reds[a]), P(reds[b]), T))
    out.append(green_edge(P((fx, fy)), P(crushed[0]), T))
    for a, b in CRUSHED_EDGES:
        out.append(green_edge(P(crushed[a]), P(crushed[b]), T))
    for p in reds:
        out.append(red_node(*P(p), T, T["content"]))
    for p, (_, _, rx) in zip(crushed, CRUSHED):
        out.append(green_node(*P(p), T, rx=rx, ry=9, rot=HYP_DEG))
    out.append('</g>')
    out.append(frame(wx, wy, T))
    mid = wy + TB + CH / 2
    out.append(label("written", wx - 74, mid + 18, T, anchor="end"))
    out += arrow(wx - 62, mid, wx - 12, mid, 0.0, T)
    gx, gy = P(crushed[2])
    ly = gy + 6
    out.append(label("not yet written", wx + WW + 84, ly + 18, T, anchor="start"))
    out += arrow(wx + WW + 72, ly, gx + 30, gy - 2, 0.0, T)

    # ---- AFTER: the red part outside the window, still connected -----------
    wx, wy = WIN[1]
    out += caption("AFTER", W / 2, wy - 30, T)
    out += window(wx, wy, T)
    Q = lambda p: (M + p[0] - PAD + R, wy + TB + p[1])      # the red, outside on the left
    G = lambda p: (wx + p[0], wy + TB + p[1])
    greens, green_edges = green_room(fy)
    out.append(green_edge(Q((fx, fy)), G(greens[0]), T, width=6))   # newest written -> first not yet written
    for a, b in red_edges:
        out.append(red_edge(Q(reds[a]), Q(reds[b]), T))
    for p in reds:
        out.append(red_node(*Q(p), T, T["bg"]))
    for a, b in green_edges:
        out.append(green_edge(G(greens[a]), G(greens[b]), T))
    for p in greens:
        out.append(green_node(*G(p), T))
    out.append(frame(wx, wy, T))
    pile_mid = M + (WW - 2 * PAD + 2 * R) / 2
    out.append(label("on disk", pile_mid, wy + TB - 22, T))
    qx, qy = Q((fx, fy))
    pile_right = max(Q(p)[0] for p in reds) + R
    out.append(label("by address", (pile_right + wx) / 2, qy - 26, T, size=50))

    out.append("</svg>")
    return "\n".join(out)


def main():
    for theme in THEMES:
        svg = HERE / f"meme-{theme}.svg"
        png = HERE / f"meme-{theme}.png"
        svg.write_text(build(theme))
        subprocess.run(["rsvg-convert", "-w", str(W), "-o", str(png), str(svg)], check=True)
        print(f"{png}  {W}x{H}")


if __name__ == "__main__":
    sys.exit(main())
