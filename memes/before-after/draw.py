#!/usr/bin/env python3
"""The before-and-after meme for the long-term-memory-structure profile README.

His design (2026-11-23): a graph that grows over time; red = the past, already
written; green = the future, not yet written.  BEFORE: the whole graph, red and
green, inside the confines of one window.  AFTER: the red part moved out of the
window, onto a disk, where it is kept; the window keeps the green, with room, and
one older red node is read back into it by its address.

Red and green are told apart by more than colour: written nodes are solid
discs joined by solid lines; not-yet-written nodes are hollow rings with dashed
outlines, joined by dashed lines.  A read by address is the picture's one solid
ink arrow with a head: from a ringed older node on the disk to a ringed copy of
it inside the window, the copy joined to the green by a dashed green line.  The
labels' pointers are plain lines, with no head.

The red in BEFORE is spread by pushing its nodes apart until no two are closer
than STEP + 4 (the walls and the green's corner hold them in), so it packs against
every wall; AFTER draws the same graph at the same relative coordinates.  Every
mark that sits in a window lies inside the window's frame in the geometry itself
(guarded below); the BEFORE window's clip path is kept, and nothing needs it.

Writes, next to this file (NAME = this folder's name): NAME-light.svg and
NAME-dark.svg, and alt.txt; and each SVG rendered by rsvg-convert to a 2000-px-wide
PNG, NAME-light.png and NAME-dark.png, in profile/memes/ (the README shows them from there).
Deterministic: the layout draws only from random.Random(seed).random(), a
sequence Python keeps the same across versions, and fixed rounds of arithmetic.
Needs rsvg-convert and the Fira Sans family (SIL OFL): Fira Sans Condensed Heavy
for the captions, Fira Sans Medium and SemiBold for the rest.

    python3 -I draw.py
"""
import math
import os
import pathlib
import random
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
NAME = HERE.name
PNGS = HERE.parent.parent / "profile" / "memes"   # the README shows the PNGs from there

# ---- canvas -----------------------------------------------------------------
W = 2000
M = 44                      # outer margin
CAP = 150                   # caption band above each row
TB = 100                    # window title bar: holds a 64-px title
CH = 300                    # window content height
WW = 800                    # window width: the SAME window in both rows
WH = TB + CH
ROWGAP = 40
Y1 = M + CAP                              # BEFORE: the window's top
Y2 = Y1 + WH + ROWGAP + CAP               # AFTER: the window's top
X1 = (W - WW) / 2                         # BEFORE: one window, centred
X2 = W - M - WW                           # AFTER: the window on the right, the disk on the left
H = Y2 + WH + 3 + M

TEXT = 64                   # every word but the two captions: 64 px on the 2000-px canvas
R = 18                      # node radius: red disc, green ring
PAD = R + 3                 # red nodes press against the frame (its stroke reaches 2.5 px in)
GAP = 14                    # the shortest red link wanted, disc edge to disc edge
STEP = 2 * R + GAP
N_RED = 86                  # red nodes: enough to fill the window wall to wall at that spacing
ROUNDS = 400                # rounds of pushing them apart
LINK = 8                    # red link: solid
RING = 8                    # green ring outline: dashed
RING_DASH = (14, 2 * math.pi * R / 5 - 14)   # five dashes round each ring
EDGE = 8                    # green link: dashed
EDGE_DASH = (22, 13)
MARK = 8                    # the by-address arrow, and the rings at its two ends
MARK_R = R + 13             # those rings' radius
HALO = 4                    # a band of the surface round each ring, keeping it clear of the nodes near it
INNER = 2.5                 # a window frame's stroke reaches this far into the content

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

TITLE = "Before and after: the written graph moved out of the context window, onto a disk"
ALT = ("Before and after. BEFORE: one context window packed wall to wall with a red graph of "
       "everything already written, solid discs joined by solid lines; the green of what is not yet "
       "written, hollow dashed rings, is crushed into its bottom corner. AFTER: the red graph has moved "
       "out of the window onto a disk, where it is kept; the same window now holds the green graph with "
       "room to grow, and a solid arrow marked by address copies one older red node from the disk into "
       "the window, where a dashed line joins it to the green.")


def fail(msg):
    sys.exit(f"draw.py: {msg}")


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
    """Prim's minimum spanning tree from root: short edges only, one graph.
    The edges come in the order the tree grew: read as the order the nodes were written."""
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


def relax(rng, n, seed_pts, spacing, rounds):
    """n points spread by pushing apart any two closer than `spacing`; the walls and the
    green's corner hold them in, so they pack against every wall.  seed_pts stay put."""
    x0, y0, x1, y1 = PAD, PAD, WW - PAD, CH - PAD
    lim = -(R + 4)

    def hold(x, y):
        x, y = min(max(x, x0), x1), min(max(y, y0), y1)
        d = depth(x, y) - lim
        if d > 0:                                   # inside the corner: back out across the hypotenuse
            x, y = x - d * N[0], y - d * N[1]
        return min(max(x, x0), x1), min(max(y, y0), y1)

    pts = list(seed_pts)
    while len(pts) < n:
        x, y = x0 + (x1 - x0) * rng.random(), y0 + (y1 - y0) * rng.random()
        if depth(x, y) <= lim:
            pts.append((x, y))
    fixed = len(seed_pts)
    for _ in range(rounds):
        moved = []
        for i in range(fixed, n):
            xi, yi = pts[i]
            mx = my = 0.0
            for j in range(n):
                if j == i:
                    continue
                dx, dy = xi - pts[j][0], yi - pts[j][1]
                d2 = dx * dx + dy * dy
                if d2 < spacing * spacing:
                    d = math.sqrt(d2) or 1e-6
                    push = 0.5 * (spacing - d) / d
                    mx, my = mx + dx * push, my + dy * push
            moved.append(hold(xi + mx, yi + my))
        pts[fixed:] = moved
    return pts


def red_graph():
    """The past: wall to wall, a row of it pressing on the green's corner."""
    wall = [on_line(t, -(R + 4)) for t in range(-int(HYP), int(HYP), STEP)]
    wall = [p for p in wall if inside(*p)]
    pts = relax(random.Random(7), N_RED, wall, STEP + 4, ROUNDS)
    root = min(range(len(pts)), key=lambda i: pts[i][0] + abs(pts[i][1] - CH / 2))
    # the newest written node: on the row facing the corner, nearest its middle
    front = min(range(len(wall)), key=lambda i: (wall[i][0] - HYP_MID[0]) ** 2 + (wall[i][1] - HYP_MID[1]) ** 2)
    return pts, tree(pts, root), root, front


def written_order(n, root, edges):
    """rank[i]: when node i was written (the root first, then in the order the tree grew)."""
    rank = {root: 0}
    for k, (_, i) in enumerate(edges):
        rank[i] = k + 1
    return [rank[i] for i in range(n)]


def hops_from(n, edges, start):
    """Tree distance, in links, from start to every node."""
    nbr = {i: [] for i in range(n)}
    for a, b in edges:
        nbr[a].append(b)
        nbr[b].append(a)
    dist, todo = {start: 0}, [start]
    while todo:
        i = todo.pop(0)
        for k in nbr[i]:
            if k not in dist:
                dist[k] = dist[i] + 1
                todo.append(k)
    return [dist[i] for i in range(n)]


# the future in BEFORE: flattened rings stacked into the corner.  Each row is
# (offset along the hypotenuse from the row's centre, depth into the corner, rx);
# a row's centre follows the corner's altitude, so the stack reaches the tip.
CRUSHED = [(0, 20, 27), (-62, 20, 27), (62, 20, 27),
           (-52, 44, 25), (0, 44, 25), (52, 44, 25),
           (-24, 68, 22), (24, 68, 22),
           (0, 92, 18)]
CRUSHED_EDGES = [(0, 1), (0, 2), (1, 3), (0, 4), (2, 5), (4, 6), (5, 7), (6, 8)]
CRUSHED_RY = 9
CRUSHED_DASH = (10, 6)


def green_room(first, shift):
    """AFTER: the future, with room: laid out as before the copy came in, then moved
    right by `shift` to leave the copy its place at the window's left."""
    rng = random.Random(11)
    pts = poisson(rng, (60, 50, WW * 0.72, CH - 50), 98, 4000, seed_pts=[(first[0] - shift, first[1])])
    pts = [(x + shift, y) for x, y in pts]
    return pts, tree(pts, 0)


# ---- the AFTER row's disk: a drum round the red, with room to spare ----------
DISK_SIDE = 22              # room between the red's outermost possible disc and the drum's side
DISK_RX = (WW - 2 * (PAD - R)) / 2 + DISK_SIDE
DISK_CX = M + 2.5 + DISK_RX
LID_E = 40                  # the lid's half-height (and the bottom's)
LID_Y = Y2 + 18             # the lid's middle: clear of the AFTER caption above it
CLEAR = 8                   # the least room between a red disc and the drum's outline
PILE_X = DISK_CX - WW / 2                   # local (content) x -> canvas x
PILE_Y = LID_Y + LID_E + CLEAR - (PAD - R)  # the top row clears the lid's front edge
COPY = (96, 205)            # the copy, in the window's content
SHIFT = 150                 # the green moves right this far to make room for it


def drum_y(x, middle):
    """The drum's front edge at canvas x: the lid's (middle = LID_Y) or the bottom's."""
    u = (x - DISK_CX) / DISK_RX
    return middle + LID_E * math.sqrt(max(0.0, 1 - u * u))


def drum_bottom():
    """Where the drum's sides end: its lowest point level with the window's foot, and
    low enough that every disc the red could hold clears the rounded bottom by CLEAR."""
    need = Y2 + WH - LID_E
    for cx in (PAD, WW - PAD):
        x0, y0 = PILE_X + cx, PILE_Y + CH - PAD
        for k in range(360):
            a = math.radians(k)
            x, y = x0 + R * math.cos(a), y0 + R * math.sin(a)
            need = max(need, y + CLEAR - (drum_y(x, 0.0)))
    return math.ceil(need)


# ---- drawing ----------------------------------------------------------------
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def dash(pattern):
    return " ".join(f(v) for v in pattern)


def red_node(x, y, T):
    """A solid disc, no ring round it: a link runs into it unbroken."""
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{R}" fill="{T["red"]}"/>'


def green_node(x, y, T):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{R}" fill="{T["content"]}" '
            f'stroke="{T["green"]}" stroke-width="{RING}" stroke-dasharray="{dash(RING_DASH)}"/>')


def crushed_node(x, y, T, rx, rot):
    return (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{CRUSHED_RY}" '
            f'transform="rotate({f(rot)} {f(x)} {f(y)})" fill="{T["content"]}" '
            f'stroke="{T["green"]}" stroke-width="{RING}" stroke-dasharray="{dash(CRUSHED_DASH)}"/>')


def red_edge(a, b, T):
    return (f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["red"]}" stroke-width="{LINK}" stroke-linecap="round"/>')


def green_edge(a, b, T, start=R + RING / 2):
    """Dashed; the pattern is set so a whole dash begins `start` along from a."""
    period = sum(EDGE_DASH)
    offset = (period - start % period) % period
    return (f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["green"]}" stroke-width="{EDGE}" stroke-dasharray="{dash(EDGE_DASH)}" '
            f'stroke-dashoffset="{f(offset)}"/>')


def window(x, y, T):
    out = [
        f'<rect x="{f(x)}" y="{y}" width="{WW}" height="{WH}" rx="18" fill="{T["content"]}"/>',
        f'<path d="M{f(x)} {y + TB} V{y + 18} a18 18 0 0 1 18 -18 H{f(x + WW - 18)} '
        f'a18 18 0 0 1 18 18 V{y + TB} Z" fill="{T["titlebar"]}"/>',
        f'<line x1="{f(x)}" y1="{y + TB}" x2="{f(x + WW)}" y2="{y + TB}" stroke="{T["frame"]}" stroke-width="4"/>',
    ]
    for i in range(3):
        out.append(f'<circle cx="{f(x + 40 + 36 * i)}" cy="{f(y + TB / 2)}" r="12" fill="{T["dot"]}"/>')
    # the title's ink (ascenders to baseline) is 52 px tall at 64 px: baseline 25 below the bar's middle
    out.append(f'<text x="{f(x + WW / 2)}" y="{f(y + TB / 2 + 25)}" text-anchor="middle" '
               f'font-family="Fira Sans" font-weight="500" font-size="{TEXT}" fill="{T["title"]}">'
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


def label(text, x, y, T, anchor="middle"):
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="Fira Sans" '
            f'font-weight="600" font-size="{TEXT}" fill="{T["ink"]}">{text}</text>')


def leader(x1, y1, x2, y2, T):
    """A label's pointer: a plain line, no head (the one arrow with a head is the read by address)."""
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{T["ink"]}" '
            f'stroke-width="6" stroke-linecap="round"/>')


def mark_ring(x, y, T):
    """The ring round a node read by address: ink, over a thin band of the surface."""
    return [f'<circle cx="{f(x)}" cy="{f(y)}" r="{MARK_R}" fill="none" stroke="{T["content"]}" '
            f'stroke-width="{MARK + 2 * HALO}"/>',
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{MARK_R}" fill="none" stroke="{T["ink"]}" '
            f'stroke-width="{MARK}"/>']


def head(tip, ux, uy, T, length=40, half=22):
    """A filled arrowhead with its tip at `tip`, pointing along the unit vector (ux, uy)."""
    bx, by = tip[0] - ux * length, tip[1] - uy * length
    pts = (f"{f(tip[0])},{f(tip[1])} {f(bx - uy * half)},{f(by + ux * half)} "
           f"{f(bx + uy * half)},{f(by - ux * half)}")
    return (bx, by), f'<polygon points="{pts}" fill="{T["ink"]}"/>'


def disk(bottom, T):
    """A disk (a drum): the body from the lid's middle down to `bottom`, rounded
    below; the lid on top, in the title bar's colour."""
    cx, rx, e = DISK_CX, DISK_RX, LID_E
    return [f'<path d="M{f(cx - rx)} {f(LID_Y)} V{f(bottom)} A{f(rx)} {f(e)} 0 0 0 {f(cx + rx)} {f(bottom)} '
            f'V{f(LID_Y)} Z" fill="{T["content"]}" stroke="{T["frame"]}" stroke-width="5" '
            f'stroke-linejoin="round"/>',
            f'<ellipse cx="{f(cx)}" cy="{f(LID_Y)}" rx="{f(rx)}" ry="{f(e)}" fill="{T["titlebar"]}" '
            f'stroke="{T["frame"]}" stroke-width="5"/>']


def cubic(p0, c1, c2, p3, t):
    s = 1 - t
    return tuple(s ** 3 * p0[i] + 3 * s * s * t * c1[i] + 3 * s * t * t * c2[i] + t ** 3 * p3[i] for i in (0, 1))


# ---- guards: what the picture needs without a clip ---------------------------
def in_content(px, py, wx, wy):
    """Is the canvas point inside the window's content, short of its frame's stroke?"""
    x, y = px - wx, py - (wy + TB)
    if not (INNER <= x <= WW - INNER and 2 <= y <= CH - INNER):
        return False
    rc = 18 - INNER                                  # the frame's rounded bottom corners, inner edge
    for cx in (18, WW - 18):
        cy = CH - 18
        if (x - cx) * (1 if cx > WW / 2 else -1) > 0 and y > cy and math.hypot(x - cx, y - cy) > rc:
            return False
    return True


def ellipse_outline(cx, cy, rx, ry, rot_deg, k=180):
    """Points on an ellipse's outline (rx, ry already include half the stroke)."""
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    out = []
    for i in range(k):
        a = 2 * math.pi * i / k
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def build(theme):
    T = THEMES[theme]
    reds, red_edges, root, front = red_graph()
    rank = written_order(len(reds), root, red_edges)
    hops = hops_from(len(reds), red_edges, front)

    body = []
    # ---- BEFORE: the whole graph inside the one window ---------------------
    wx, wy = X1, Y1
    body += caption("BEFORE", W / 2, wy - 30, T)
    body += window(wx, wy, T)
    body.append(content_clip("before", wx, wy, T))
    body.append('<g clip-path="url(#before)">')
    P = lambda p: (wx + p[0], wy + TB + p[1])
    crushed = [on_line(t + T_CORNER * d / DEPTH_MAX, d) for t, d, _ in CRUSHED]
    fx, fy = reds[front]
    for a, b in red_edges:
        body.append(red_edge(P(reds[a]), P(reds[b]), T))
    body.append(green_edge(P((fx, fy)), P(crushed[0]), T, start=R))
    for a, b in CRUSHED_EDGES:
        body.append(green_edge(P(crushed[a]), P(crushed[b]), T))
    for p in reds:
        body.append(red_node(*P(p), T))
    for p, (_, _, rx) in zip(crushed, CRUSHED):
        body.append(crushed_node(*P(p), T, rx, HYP_DEG))
    body.append('</g>')
    body.append(frame(wx, wy, T))
    # guard: every mark in this window is inside its frame without the clip
    for p, (_, _, rx) in zip(crushed, CRUSHED):
        for q in ellipse_outline(*P(p), rx + RING / 2, CRUSHED_RY + RING / 2, HYP_DEG):
            if not in_content(*q, wx, wy):
                fail(f"BEFORE: the crushed ring at {tuple(round(v) for v in p)} crosses the frame at "
                     f"{tuple(round(v) for v in q)}; move it in (CRUSHED) or shrink its rx")
    for p in reds:
        for q in ellipse_outline(*P(p), R, R, 0, 72):
            if not in_content(*q, wx, wy):
                fail(f"BEFORE: the red node at {tuple(round(v) for v in p)} crosses the frame; PAD is {PAD}")
    mid = wy + TB + CH / 2
    body.append(label("written", wx - 74, mid + 17, T, anchor="end"))
    body.append(leader(wx - 60, mid, wx - 14, mid, T))
    gx, gy = P(crushed[2])
    ly = gy + 6
    body.append(label("not yet written", wx + WW + 84, ly + 17, T, anchor="start"))
    body.append(leader(wx + WW + 72, ly, gx + 34, gy - 2, T))

    # ---- AFTER: the red on the disk; the window holds the green, and one copy ---
    wx, wy = X2, Y2
    body += caption("AFTER", W / 2, wy - 30, T)
    bottom = drum_bottom()
    body += disk(bottom, T)
    body.append(label("on disk", DISK_CX, LID_Y + 25, T))
    Q = lambda p: (PILE_X + p[0], PILE_Y + p[1])          # the red, on the disk
    G = lambda p: (wx + p[0], wy + TB + p[1])              # inside the window
    for a, b in red_edges:
        body.append(red_edge(Q(reds[a]), Q(reds[b]), T))
    for p in reds:
        body.append(red_node(*Q(p), T))

    # the node read back: on the red's bottom row, written before the newest and far from
    # it along the tree; of those, the one nearest the corner the green had (the shortest run)
    old = [i for i, p in enumerate(reds) if p[1] >= CH - PAD - 2 and rank[i] < rank[front] and hops[i] >= 10]
    if not old:
        fail(f"no bottom-row node written before the newest (rank {rank[front]}) and 10 or more links "
             f"from it; bottom row: {[(round(reds[i][0]), rank[i], hops[i]) for i in range(len(reds)) if reds[i][1] >= CH - PAD - 2]}")
    src_i = max(old, key=lambda i: reds[i][0])
    src, cpy = Q(reds[src_i]), G(COPY)

    body += window(wx, wy, T)
    greens, gedges = green_room((COPY[0] + SHIFT, COPY[1]), SHIFT)
    g0 = G(greens[0])
    out_r = MARK_R + MARK / 2 + HALO                       # the copy's ring, outer edge with its band
    ux, uy = (g0[0] - cpy[0]) / math.dist(cpy, g0), (g0[1] - cpy[1]) / math.dist(cpy, g0)
    body.append(green_edge((cpy[0] + ux * out_r, cpy[1] + uy * out_r), g0, T, start=0))   # copy -> green
    for a, b in gedges:
        body.append(green_edge(G(greens[a]), G(greens[b]), T))
    for p in greens:
        body.append(green_node(*G(p), T))
    body.append(red_node(*cpy, T))
    body.append(frame(wx, wy, T))
    body += mark_ring(*src, T)
    body += mark_ring(*cpy, T)
    for p in greens:                                       # guard: the green and the copy sit inside
        for q in ellipse_outline(*G(p), R + RING / 2, R + RING / 2, 0, 72):
            if not in_content(*q, wx, wy):
                fail(f"AFTER: the green ring at {tuple(round(v) for v in p)} crosses the frame; SHIFT is {SHIFT}")
    for q in ellipse_outline(*cpy, out_r, out_r, 0, 72):
        if not in_content(*q, wx, wy):
            fail(f"AFTER: the copy's ring at {COPY} crosses the frame")

    # the arrow: under the bottom row, inside the drum; up through the corner the green had
    # (empty now); out through the drum's side and into the window, to the copy
    reach = MARK_R + MARK / 2 + 6                          # it starts and stops this far from a centre
    sx, sy = reds[src_i]
    yb = CH - PAD + R + 9 + MARK / 2                       # its run under the bottom row (local)
    ye = cpy[1] - PILE_Y                                   # the copy's level (local)
    x_start = sx + math.sqrt(reach * reach - (yb - sy) ** 2)
    x_rise, x_top = 590, 700
    tip = (cpy[0] - reach, cpy[1])
    (bx, by), arrowhead = head(tip, 1.0, 0.0, T)
    a, b = Q((x_start, yb)), Q((x_rise, yb))
    c1, c2, d = Q((x_rise + 55, yb)), Q((x_top - 55, ye)), Q((x_top, ye))
    body.append(f'<path d="M{f(a[0])} {f(a[1])} H{f(b[0])} C{f(c1[0])} {f(c1[1])} {f(c2[0])} '
                f'{f(c2[1])} {f(d[0])} {f(d[1])} H{f(bx)}" fill="none" stroke="{T["ink"]}" '
                f'stroke-width="{MARK}" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(arrowhead)
    # guard: the arrow passes every red node (but its own) and the drum's outline with room
    path = [(a[0] + (b[0] - a[0]) * t / 40, a[1]) for t in range(41)]
    path += [cubic(b, c1, c2, d, t / 40) for t in range(41)]
    path += [(d[0] + (bx - d[0]) * t / 40, d[1]) for t in range(41)]
    for i, p in enumerate(reds):
        if i != src_i:
            gap = min(math.dist(Q(p), q) for q in path) - R - MARK / 2
            if gap < 8:
                fail(f"the by-address arrow passes {gap:.1f} px from red node {i} at "
                     f"{tuple(round(v) for v in p)}; move x_rise/x_top or the band")
    for q in path:
        if DISK_CX - DISK_RX < q[0] < DISK_CX + DISK_RX and drum_y(q[0], bottom) - q[1] - MARK / 2 < 14:
            fail(f"the by-address arrow runs within 14 px of the drum's bottom at x={q[0]:.0f}")
    lx = (DISK_CX + DISK_RX + wx) / 2                      # in the gap, over the arrow
    body.append(label("by", lx, cpy[1] - 32 - 76, T))
    body.append(label("address", lx, cpy[1] - 32, T))

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-labelledby="title desc">',
           f'<title id="title">{TITLE}</title>',
           f'<desc id="desc">{ALT}</desc>',
           f'<rect width="{W}" height="{H}" rx="28" fill="{T["bg"]}"/>']
    out += body
    out.append("</svg>")
    info = dict(red_nodes=len(reds), newest=front, newest_rank=rank[front],
                read_back=src_i, read_back_rank=rank[src_i], read_back_links_from_newest=hops[src_i],
                drum_bottom=bottom)
    return "\n".join(out) + "\n", info


def replace(path, data):
    """Write beside, then rename over: no half-written file is ever at the path."""
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def main():
    PNGS.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        svg = HERE / f"{NAME}-{theme}.svg"
        png = PNGS / f"{NAME}-{theme}.png"
        text, info = build(theme)
        replace(svg, text.encode())
        tmp = png.with_name(f".{png.name}.tmp")
        subprocess.run(["rsvg-convert", "-w", str(W), "-o", str(tmp), str(svg)], check=True)
        os.replace(tmp, png)
        print(f"{png.name}  {W}x{H}  {info}")
    replace(HERE / "alt.txt", (ALT + "\n").encode())


if __name__ == "__main__":
    sys.exit(main())
