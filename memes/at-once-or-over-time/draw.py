#!/usr/bin/env python3
"""Meme 2 for the long-term-memory-structure profile README: many agents at once, or one agent over time.

His recording 05 (2026-11-22): a task too big for one context window is split HORIZONTALLY (many agents
at once, each its own window, the work passed between them in messages, details lost) or VERTICALLY
(one agent carried over time, all the reasoning in one place, a long-term memory read without filling
its window).  This treatment makes time the axis; time runs down the page.

  HORIZONTAL  at one moment, four windows side by side.  One graph, cut into a piece per window; what
              lay between two windows goes in a message (an envelope), and what falls out is lost.
  VERTICAL    one window at three moments down the time axis (faint = where it was earlier).  The record
              (red) outlives the windows: its spine runs down beside the column, outside every frame, as
              the page keeps it on disk; a branch reaches into each faint frame (what the window held
              then), and its newest node joins the new work in the window by a dashed edge through the
              window's left frame, as meme 1's AFTER joins its red to its window.  One node of it,
              outside the old frames, is read back into the window by its address: a solid ink arrow,
              to a red copy inside, joined to the new work.

The series' conventions; meme 1 (memes/before-after/draw.py in the profile repository) is the reference:
  meme 1's palette T, its window chrome (a title bar with three dots) and its caption() lettering;
  written = red solid discs on solid lines; not yet written = green hollow dashed rings on dashed lines;
  the read by address is the only solid arrow with a head (so the time axis has ticks, not a head);
  every word at least 64 px tall on the 2000-px canvas;
  QtSvg (no clipping): each clipPath sits in <defs>, its path filled with the content colour, and every
  edge is cut at the window frames here, in the script, so nothing needs the clip to read right.
Every window has the same size: a smaller swarm window would say, falsely, that a swarm's agents have
smaller windows.  Words: the two titles and three tags (time, lost, by address).

Writes, next to this file (NAME = this folder's name): NAME-light.svg and NAME-dark.svg, each rendered by
rsvg-convert to a 2000-px-wide PNG in profile/memes/ (the README shows them from there), and alt.txt (the alt text; the SVG's <desc> too).
In checks/: NAME-same-colour.svg/.png and NAME-same-colour-dark.svg/.png, the pictures with red and
green in one grey (not published).  check.py makes the views to look at and measures the rest.
Deterministic: no randomness; every position below is computed from the constants.
Needs rsvg-convert and the Fira Sans family (SIL OFL): Fira Sans Condensed Heavy for the titles, Fira
Sans SemiBold for the tags.

    python3 -I draw.py
"""
import math
import pathlib
import subprocess
import sys
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
NAME = HERE.name                      # the outputs are named after this folder
PNGS = HERE.parent.parent / "profile" / "memes"   # the README shows the PNGs from there

TITLE = "Many agents at once, or one agent over time"
ALT = (
    "Many agents at once, or one agent over time. "
    "On the left, under HORIZONTAL, four windows of the same size sit side by side at one moment, each "
    "working on its own piece of one graph: red solid dots joined by solid lines are work already written, "
    "green hollow rings joined by dashed lines are work not yet written. "
    "Where the graph crossed from one window to the next it is cut, an envelope (a message) bridges each "
    "gap, and the pieces that lay between the windows fall into a heap marked lost. "
    "On the right, under VERTICAL, one window is carried down an axis marked time; faint outlines show "
    "where it was earlier. "
    "Its red record runs down beside those outlines, outside them, with short branches reaching into "
    "each; its newest node joins the green work in the window by a dashed line, and an arrow marked by "
    "address reads one old red node back into the window as a copy, joined to the new green work."
)

# ---- canvas and the one window size ------------------------------------------
W = 2000
H = 1190
TB = 44                    # window title bar
CW, CH = 230, 210          # window content
WW, WH = CW, TB + CH       # every window in the picture has this size
RX = 14                    # window corner radius
FRAME = 5                  # the frame's stroke
BAR = 3                    # the line under the title bar

R = 15                     # node radius
RING = 3                   # a red node's ring, in the colour of the surface under it
NODE = R + RING / 2        # how far a node's ink reaches from its centre (a green ring: R - 1 + 5 / 2)
S = 52                     # spacing along the spine
B = 40                     # a branch's step across the spine
RED_W, GREEN_W = 7, 5      # a written edge; a not-yet-written edge
INK_W = 6                  # the arrow and the time axis
MARK_W = 5                 # the read's two rings, the envelopes, the motion streaks
READ_RING = R + 8          # the radius of the ring around each end of the read
STUB = 30                  # a torn edge's length, from its node's centre
CUT = 1.5                  # an edge cut at a frame stops this far inside the frame's line, under its stroke
CLEAR = 4                  # the least room between a node and a frame's stroke, inside or outside

TOP = 214                  # the first moment: the swarm's row and the single window's first place

# HORIZONTAL: four windows side by side
LEFT_X0, GAP = 44, 56
ROW_X = [LEFT_X0 + i * (WW + GAP) for i in range(4)]
LEFT_X1 = ROW_X[-1] + WW
# the time axis, between the two halves
AXIS_X = LEFT_X1 + 36
TICK = 16                  # a tick's length
TICKS_X = (AXIS_X - TICK, AXIS_X)   # each tick, on the axis's left side only: the record's spine runs on its right
# VERTICAL: one window at three moments
COL_X = AXIS_X + 84
COL_GAP = 60
COL_Y = [TOP + i * (WH + COL_GAP) for i in range(3)]
SPINE_X = COL_X - 42       # the record's spine: down the left of the column, between the time axis and the frames
READ_FROM = (COL_X + WW + 35, COL_Y[0] + TB + 156)    # the node read back: outside the first place's right side
LOOP = 170                 # the read's arrow bows out this far past the column's right frame (control points)

THEMES = {
    "light": dict(
        bg="#f3f0e8", frame="#1d1d1f", titlebar="#e4e0d6", content="#ffffff",
        dot="#b3ada1", ink="#1d1d1f", ghosts=(0.42, 0.62),
        red="#b81d24", green="#23a55a",
        cap_fill="#ffffff", cap_stroke="#000000",
    ),
    "dark": dict(
        bg="#16191e", frame="#aab2bd", titlebar="#2a3038", content="#0f1217",
        dot="#5d6670", ink="#e8ebef", ghosts=(0.42, 0.58),
        red="#d93a42", green="#4cc777",
        cap_fill="#ffffff", cap_stroke="#000000",
    ),
}
# the shape-only checks: red and green in one grey (written to checks/, not published)
THEMES["same-colour"] = dict(THEMES["light"], red="#7a7a7a", green="#7a7a7a")
THEMES["same-colour-dark"] = dict(THEMES["dark"], red="#8a8a8a", green="#8a8a8a")


# ---- the graph: a spine of turns, tool calls branching off it -----------------
# HORIZONTAL's graph; VERTICAL's has its own branch lists, drawn by the same rules.
# BRANCH[k] = list of (side, depth) for spine node k: side -1/+1, depth 1 or 2.
BRANCH = {
    0: [(-1, 2)], 1: [(1, 2)], 2: [(-1, 1)], 3: [(1, 2)], 4: [(-1, 2)],
    5: [(1, 1), (-1, 2)], 6: [(1, 2)], 7: [(-1, 1)], 8: [(1, 2)], 9: [(-1, 2)],
    10: [(1, 2)], 11: [(-1, 1)], 12: [(1, 1)], 13: [(-1, 2)], 14: [(1, 2)],
    15: [(-1, 1)], 16: [(1, 2)], 17: [(-1, 2)], 18: [(1, 1)],
}


def graph(spine):
    """Nodes and edges for spine nodes at positions `spine` (distances along the spine); each node's
    coordinates are (a, c): a = distance along the spine, c = offset across it."""
    nodes, edges = {}, []
    for k, a in enumerate(spine):
        nodes[("s", k)] = (a, 0.0)
        if k:
            edges.append((("s", k - 1), ("s", k)))
        for side, depth in BRANCH.get(k, []):
            prev = ("s", k)
            for j in range(1, depth + 1):
                key = ("b", k, side, j)
                nodes[key] = (a + j * S / 2, side * j * B)
                edges.append((prev, key))
                prev = key
    return nodes, edges


# ---- geometry: frames, cuts, room ---------------------------------------------
def content_box(x, y):
    """Where a window's content may be drawn: CUT inside its frame's line, CUT below the title bar's line."""
    return (x + CUT, y + TB + CUT, x + WW - CUT, y + WH - CUT)


def cut(p, q, box):
    """The part of the segment p-q inside box (Liang-Barsky), or None.  A cut end must meet a straight
    part of the frame, not a rounded bottom corner (where a rectangle is not the frame's shape)."""
    x0, y0, x1, y1 = box
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for d, room in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if d == 0:
            if room < 0:
                return None
            continue
        t = room / d
        if d < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    if t0 >= t1:
        return None
    a = (p[0] + t0 * dx, p[1] + t0 * dy)
    b = (p[0] + t1 * dx, p[1] + t1 * dy)
    for end, was_cut in ((a, t0 > 0), (b, t1 < 1)):
        in_corner = end[1] > y1 - RX and (end[0] < x0 + RX or end[0] > x1 - RX)
        assert not (was_cut and in_corner), f"an edge cut in a rounded corner at {end}"
    return a, b


def where(p, r, places):
    """Which window (an index into places, a list of (x, y)) p lies wholly inside, with its reach r and
    CLEAR room from the frame's inner edge; None if it lies wholly outside every one.  A node across a
    frame, or on a title bar, is refused: nothing is left to a clip."""
    for i, (x, y) in enumerate(places):
        lo_x, hi_x = x + FRAME / 2 + CLEAR + r, x + WW - FRAME / 2 - CLEAR - r
        lo_y, hi_y = y + TB + BAR / 2 + CLEAR + r, y + WH - FRAME / 2 - CLEAR - r
        if lo_x <= p[0] <= hi_x and lo_y <= p[1] <= hi_y:
            return i
        near = FRAME / 2 + CLEAR + r
        assert not (x - near < p[0] < x + WW + near and y - near < p[1] < y + WH + near), \
            f"a node across a frame or on a title bar: {p}, window at {(x, y)}"
    return None


def clear_of_frames(x, y0, y1, width, places, room=8):
    """A vertical mark from (x, y0) down to (x, y1), `width` wide with round caps, lies outside every
    window in places and its ink clears each frame's ink (FRAME wide, on the window's outline) by at
    least `room` px.  Measured to the frame's rectangle, which holds its rounded corners, so the room
    is never overstated; a mark inside a window measures 0 to it and is refused."""
    for wx, wy in places:
        dx = max(wx - x, x - (wx + WW), 0.0)
        dy = max(wy - y1, y0 - (wy + WH), 0.0)
        room_left = math.hypot(dx, dy) - width / 2 - FRAME / 2
        assert room_left >= room, (f"a mark at x {f(x)}, y {f(y0)}-{f(y1)} is {room_left:.1f} px from the frame "
                                   f"of the window at {(wx, wy)}; it needs {room}")


# ---- drawing primitives -------------------------------------------------------
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def red_node(x, y, T, ring):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{R}" fill="{T["red"]}" '
            f'stroke="{ring}" stroke-width="{RING}"/>')


def green_node(x, y, T, fill):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{R - 1}" fill="{fill}" '
            f'stroke="{T["green"]}" stroke-width="5" stroke-dasharray="6.5 4"/>')


def red_edge(a, b, T):
    return (f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["red"]}" stroke-width="{RED_W}" stroke-linecap="round"/>')


def green_edge(a, b, T):
    return (f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["green"]}" stroke-width="{GREEN_W}" stroke-dasharray="9 7"/>')


def window(x, y, T, alpha=1.0, fill=True):
    """A framed app window: title bar with three dots.  alpha < 1: where the window was earlier."""
    g = [f'<g opacity="{alpha}">'] if alpha < 1 else []
    if fill:
        g.append(f'<rect x="{f(x)}" y="{f(y)}" width="{WW}" height="{WH}" rx="{RX}" fill="{T["content"]}"/>')
    g.append(f'<path d="M{f(x)} {f(y + TB)} V{f(y + RX)} a{RX} {RX} 0 0 1 {RX} -{RX} H{f(x + WW - RX)} '
             f'a{RX} {RX} 0 0 1 {RX} {RX} V{f(y + TB)} Z" fill="{T["titlebar"]}"/>')
    g.append(f'<line x1="{f(x)}" y1="{f(y + TB)}" x2="{f(x + WW)}" y2="{f(y + TB)}" '
             f'stroke="{T["frame"]}" stroke-width="{BAR}"/>')
    for i in range(3):
        g.append(f'<circle cx="{f(x + 24 + 20 * i)}" cy="{f(y + TB / 2)}" r="7" fill="{T["dot"]}"/>')
    g.append(f'<rect x="{f(x)}" y="{f(y)}" width="{WW}" height="{WH}" rx="{RX}" fill="none" '
             f'stroke="{T["frame"]}" stroke-width="{FRAME}"/>')
    if alpha < 1:
        g.append('</g>')
    return g


def content_clip(cid, x, y, T):
    """The window's content area (below the title bar, rounded at the bottom), as meme 1 has it: in
    <defs>, its path filled with the content colour.  QtSvg ignores the clip and draws a clipPath found
    outside <defs> as a black shape; the edges are cut in the script, so the clip changes nothing."""
    top, bot = y + TB, y + WH
    return (f'<defs><clipPath id="{cid}"><path d="M{f(x)} {f(top)} H{f(x + WW)} V{f(bot - RX)} '
            f'a{RX} {RX} 0 0 1 -{RX} {RX} H{f(x + RX)} a{RX} {RX} 0 0 1 -{RX} -{RX} Z" '
            f'fill="{T["content"]}"/></clipPath></defs>')


def caption(text, cx, baseline, T, size=124):
    common = (f'x="{f(cx)}" y="{f(baseline)}" text-anchor="middle" font-family="Fira Sans Condensed" '
              f'font-weight="900" font-size="{size}" letter-spacing="5"')
    return [f'<text {common} fill="{T["cap_stroke"]}" stroke="{T["cap_stroke"]}" stroke-width="18" '
            f'stroke-linejoin="round">{text}</text>',
            f'<text {common} fill="{T["cap_fill"]}">{text}</text>']


def label(text, x, y, T, size=64, anchor="middle", weight=600):
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="Fira Sans" '
            f'font-weight="{weight}" font-size="{size}" fill="{T["ink"]}">{text}</text>')


def head(tip, ux, uy, T, length=30, half=15):
    bx, by = tip[0] - ux * length, tip[1] - uy * length
    pts = (f"{f(tip[0])},{f(tip[1])} {f(bx - uy * half)},{f(by + ux * half)} "
           f"{f(bx + uy * half)},{f(by - ux * half)}")
    return f'<polygon points="{pts}" fill="{T["ink"]}"/>', (bx, by)


def cubic(p0, c1, c2, p1, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p1[0],
            u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p1[1])


def arrow(p0, c1, c2, p1, T, width=INK_W):
    """A solid ink cubic arrow p0 -> p1, its head at p1 along the end tangent.  Returns the marks and the
    drawn curve's farthest x (where the tag beside it may start)."""
    tx, ty = p1[0] - c2[0], p1[1] - c2[1]
    n = math.hypot(tx, ty)
    poly, base = head(p1, tx / n, ty / n, T)
    far = max(cubic(p0, c1, c2, base, i / 400)[0] for i in range(401)) + width / 2
    return [f'<path d="M{f(p0[0])} {f(p0[1])} C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} '
            f'{f(base[0])} {f(base[1])}" fill="none" stroke="{T["ink"]}" stroke-width="{width}" '
            f'stroke-linecap="round"/>', poly], far


def envelope(cx, cy, rot, T, w=66, h=46):
    x, y = cx - w / 2, cy - h / 2
    return [f'<g transform="rotate({f(rot)} {f(cx)} {f(cy)})">',
            f'<rect x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" rx="5" fill="{T["content"]}" '
            f'stroke="{T["ink"]}" stroke-width="{MARK_W}"/>',
            f'<polyline points="{f(x + 3)},{f(y + 3)} {f(cx)},{f(y + h * 0.58)} {f(x + w - 3)},{f(y + 3)}" '
            f'fill="none" stroke="{T["ink"]}" stroke-width="{MARK_W}" stroke-linejoin="round"/>',
            '</g>']


STREAKS = ((-14, 26), (0, 40), (14, 26))   # each motion line: across from the group's centre, its length


def streak_lines(x, y):
    """The motion lines above a falling piece whose top is at y, the group centred on x: [(x, top, bottom)]."""
    return [(x + dx, y - R - 10 - ln, y - R - 10) for dx, ln in STREAKS]


def streaks(lines, T):
    """Motion lines, in full ink."""
    return [f'<line x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}" stroke="{T["ink"]}" '
            f'stroke-width="{MARK_W}" stroke-linecap="round"/>' for x, y0, y1 in lines]


# ---- HORIZONTAL ---------------------------------------------------------------
def row_layout():
    """The spine across the row: four nodes inside each window, one in each gap between two windows."""
    xs = []
    for i, wx in enumerate(ROW_X):
        xs += [wx + 30 + 50 * j for j in range(4)]
        if i < 3:
            xs.append(wx + WW + GAP / 2)
    return xs


def gap_of(x):
    for i in range(3):
        if ROW_X[i] + WW < x < ROW_X[i + 1]:
            return i
    return None


def window_of(x):
    for i, wx in enumerate(ROW_X):
        if wx <= x <= wx + WW:
            return i
    return None


GREEN_FROM = {0: 3, 1: 2, 2: 3, 3: 1}   # window -> its first spine node (0..3) not yet written


def horizontal(T):
    out = ['<g id="horizontal">']
    spine_y = TOP + TB + CH / 2
    xs = row_layout()
    nodes, edges = graph(xs)
    P = {k: (a, spine_y + c) for k, (a, c) in nodes.items()}
    first_k = {}
    for k, x in enumerate(xs):
        i = window_of(x)
        if i is not None:
            first_k.setdefault(i, k)

    def green(key):
        i = window_of(xs[key[1]])
        return i is not None and key[1] - first_k[i] >= GREEN_FROM[i]

    row = [(wx, TOP) for wx in ROW_X]
    # the row of windows at one moment; each holds its piece of the one graph, cut at its frame
    for i, wx in enumerate(ROW_X):
        out.append(f'<g id="swarm-window-{i + 1}">')
        out += window(wx, TOP, T)
        out.append(content_clip(f"row{i}", wx, TOP, T))
        out.append(f'<g clip-path="url(#row{i})">')
        box = content_box(wx, TOP)
        for a, b in edges:
            if i not in (window_of(P[a][0]), window_of(P[b][0])):
                continue
            seg = cut(P[a], P[b], box)
            if seg is not None:
                out.append(green_edge(*seg, T) if green(a) or green(b) else red_edge(*seg, T))
        for key, p in P.items():
            if window_of(p[0]) == i:
                assert where(p, NODE, row) == i
                out.append(green_node(*p, T, T["content"]) if green(key) else red_node(*p, T, T["content"]))
        out.append('</g>')
        out += window(wx, TOP, T, fill=False)     # the frame again, over the cut ends
        out.append('</g>')
    # each gap: an envelope where the link was; everything that lay in the gap falls out of it
    for gi in range(3):
        out.append(f'<g id="gap-{gi + 1}">')
        gx = ROW_X[gi] + WW + GAP / 2
        k = xs.index(gx)
        part = [key for key, p in P.items() if gap_of(p[0]) == gi]
        sx, sy = P[("s", k)]
        drop, rot = FALLS[gi]
        pts = []
        for a, b in edges:                       # the edges it had, torn off short
            if a not in part and b not in part:
                continue
            pa, pb = P[a], P[b]
            if a in part and b in part:
                seg = (pa, pb)
            else:
                near, far = (pa, pb) if a in part else (pb, pa)
                d = math.dist(near, far)
                seg = (near, (near[0] + (far[0] - near[0]) * STUB / d, near[1] + (far[1] - near[1]) * STUB / d))
            seg = tuple(turn(q, (sx, sy), rot, (0, drop)) for q in seg)
            pts += seg
            out.append(red_edge(*seg, T))
        for key in part:
            q = turn(P[key], (sx, sy), rot, (0, drop))
            pts.append(q)
            out.append(red_node(*q, T, T["bg"]))
        top = min(pts, key=lambda q: q[1])
        lines = streak_lines(top[0], top[1])
        if min(y0 for _, y0, _ in lines) < TOP + WH:     # still beside the windows: centred in the gap, off both frames
            lines = streak_lines(gx, top[1])
        for x, y0, y1 in lines:
            clear_of_frames(x, y0, y1, MARK_W, row)
        out += streaks(lines, T)
        out += envelope(gx, spine_y, (-14, 10, -8)[gi], T)
        out.append('</g>')
    # on the floor: pieces lost the same way, in a heap
    out.append('<g id="heap">')
    for cx0, dy, rot in HEAP:
        at = (cx0, FLOOR + dy)
        piece = [turn(q, (0, 0), rot, at) for q in PIECE_NODES]
        for a, b in PIECE_STUBS:
            out.append(red_edge(turn(a, (0, 0), rot, at), turn(b, (0, 0), rot, at), T))
        out.append(red_edge(piece[0], piece[1], T))
        for q in piece:
            out.append(red_node(*q, T, T["bg"]))
    out.append(label("lost", HEAP_LABEL[0], HEAP_LABEL[1], T, anchor="start"))
    out.append('</g>')
    out.append('</g>')
    return out


def turn(q, c, deg, shift):
    """q rotated by deg about c, then shifted."""
    a = math.radians(deg)
    dx, dy = q[0] - c[0], q[1] - c[1]
    return (c[0] + dx * math.cos(a) - dy * math.sin(a) + shift[0],
            c[1] + dx * math.sin(a) + dy * math.cos(a) + shift[1])


FALLS = ((180, -24), (470, 18), (320, -14))          # per gap: how far its piece has fallen, its tilt
FLOOR = H - 128
# a lost piece: a spine node and its branch node, the edges they had torn off short
PIECE_NODES = [(0, 0), (26, -40)]
PIECE_STUBS = [((0, 0), (-STUB, 0)), ((0, 0), (STUB, 0)),
               ((26, -40), (26 + 14 * STUB / math.hypot(14, 22), -40 - 22 * STUB / math.hypot(14, 22)))]
HEAP = [(x + 150, dy, rot) for x, dy, rot in [(372, 18, 8), (436, 22, -28), (508, 16, 62), (574, 20, 175), (404, -22, 140),
        (470, -16, -96), (540, -24, 32), (446, -62, 210), (512, -66, -150)]]
HEAP_LABEL = (790, FLOOR + 22)


# ---- VERTICAL -----------------------------------------------------------------
FIRST_GREEN_Y = COL_Y[-1] + TB + 34     # the window now's first green node, on its spine
RECORD_N = 13              # the record's spine nodes, S apart, from the first place's height down to FIRST_GREEN_Y
# the record's branches (tool calls), by spine node: each reaches right from its spine node, (across, down),
# into a faint frame and ends there in one node.  READ_SPINE's branch instead ends at READ_FROM.
RECORD_BRANCH = {0: (120, 26), 2: (120, 26), 6: (120, 26), 7: (120, 26), 8: (120, 26)}
READ_SPINE = 1


def record():
    """The record (red): a spine of turns down the left of the column, outside every frame, from the first
    place's height to level with the window now's first green node; its branches reach right into the
    faint frames, one node each, and one runs on through the first frame to the node read back, outside
    the frame's right side.  Returns [(the spine node's y, its branch's node or None)]."""
    out = []
    for k in range(RECORD_N):
        y = FIRST_GREEN_Y - S * (RECORD_N - 1 - k)
        if k == READ_SPINE:
            out.append((y, READ_FROM))
        elif k in RECORD_BRANCH:
            dx, dy = RECORD_BRANCH[k]
            out.append((y, (SPINE_X + dx, y + dy)))
        else:
            out.append((y, None))
    return out


# the work now (green): side and depth of each branch, by spine node.  The first node has none: the edge
# from the record comes in on its left, level with it.
V_GREEN_BRANCH = [[], [(1, 1), (-1, 1)], [(-1, 1)]]


def vertical(T):
    out = ['<g id="vertical">']
    cx = COL_X + WW / 2
    now_y = COL_Y[-1]
    places = [(COL_X, y0) for y0 in COL_Y]
    P, E, colour = {}, [], {}
    prev = None
    rec = record()
    for k, (y, end) in enumerate(rec):
        P[("s", k)], colour[("s", k)] = (SPINE_X, y), "red"
        if prev is not None:
            E.append((prev, ("s", k)))
        prev = ("s", k)
        if end is not None:
            P[("b", k)], colour[("b", k)] = end, "red"
            E.append((("s", k), ("b", k)))
    newest = prev                           # the record's last node: the newest written
    for g, br in enumerate(V_GREEN_BRANCH):
        k = len(rec) + g
        y = FIRST_GREEN_Y + 56 * g
        P[("s", k)], colour[("s", k)] = (cx, y), "green"
        E.append((prev, ("s", k)))          # g = 0: the newest written joins the first not yet written
        prev = ("s", k)
        for side, depth in br:
            last = ("s", k)
            for j in range(1, depth + 1):
                key = ("b", k, side, j)
                P[key], colour[key] = (cx + side * j * B, y + j * S / 2), "green"
                E.append((last, key))
                last = key
    # every node wholly inside a window or wholly outside them all: the record's spine outside every frame,
    # each of its branches' nodes inside a faint frame (the one read back outside them all), the new work
    # inside the window now
    for key, p in P.items():
        w = where(p, NODE, places)
        if colour[key] == "green":
            assert w == 2, f"the new work's node {key} at {p}: window {w}"
        elif key[0] == "s" or key[1] == READ_SPINE:
            assert w is None, f"the record's node {key} at {p} lies in window {w}"
        else:
            assert w in (0, 1), f"the record's branch node {key} at {p}: window {w}, not a faint frame"
    assert P[newest][1] == P[("s", len(rec))][1], "the record ends level with the window now's first green node"
    axis_ink = max(AXIS_X, *TICKS_X) + INK_W / 2            # the axis's and its ticks' rightmost ink
    assert SPINE_X - NODE - axis_ink >= 8, "the record's spine clears the time axis and its ticks"
    src = P[("b", READ_SPINE)]
    dst = (cx + 62, now_y + TB + 50)        # the copy, read back into the window now
    reach = READ_RING + MARK_W / 2
    assert where(src, reach, places) is None, "the node read back lies outside the old frames"
    assert where(dst, reach, places) == 2, "the copy lies inside the window now"

    # where the window was: faint, empty
    out.append('<g id="earlier-places">')
    for y0, alpha in zip(COL_Y[:-1], T["ghosts"]):
        out += window(COL_X, y0, T, alpha=alpha, fill=False)
    out.append('</g>')
    out.append('<g id="window-now">')
    out += window(COL_X, now_y, T)
    out.append('</g>')
    # one graph, unbroken: the record outside the window now, the new work inside it
    out.append('<g id="record-and-work">')
    for a, b in E:
        if colour[a] == "red" and colour[b] == "red":
            out.append(red_edge(P[a], P[b], T))
        else:
            out.append(green_edge(P[a], P[b], T))
    out.append(green_edge(dst, P[("s", len(rec) + 1)], T))      # the copy joins the new work
    for key, p in P.items():
        out.append(red_node(*p, T, T["bg"]) if colour[key] == "red" else green_node(*p, T, T["content"]))
    out.append('</g>')
    # the window now's frame again, over the dashed edge that joins the record to the new work (meme 1's AFTER)
    out.append('<g id="window-now-frame">')
    out += window(COL_X, now_y, T, fill=False)
    out.append('</g>')
    # the read: one node of the record, read back into the window by its address
    out.append('<g id="read-by-address">')
    out.append(red_node(*dst, T, T["content"]))
    for c in (src, dst):
        out.append(f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{READ_RING}" fill="none" stroke="{T["ink"]}" '
                   f'stroke-width="{MARK_W}"/>')
    p0 = (src[0] + READ_RING, src[1])
    ang = math.radians(-35)
    p1 = (dst[0] + reach * math.cos(ang), dst[1] + reach * math.sin(ang))
    marks, far = arrow(p0, (COL_X + WW + LOOP, src[1] - 10), (COL_X + WW + LOOP, dst[1] - 90), p1, T)
    out += marks
    out.append(label("by address", far + 14, (src[1] + dst[1]) / 2 + 22, T, anchor="start"))
    out.append('</g>')
    out.append('</g>')
    return out


def time_axis(T):
    """Time runs down: a line with a tick at each of the single window's places (the row sits at the
    first), on its left side only, so none reaches the record's spine on its right.  No head: in this
    series the only solid arrow with a head is the read by address."""
    out = ['<g id="time-axis">',
           f'<line x1="{AXIS_X}" y1="{TOP}" x2="{AXIS_X}" y2="{H - 96}" stroke="{T["ink"]}" '
           f'stroke-width="{INK_W}" stroke-linecap="round"/>']
    for y0 in COL_Y:
        ym = y0 + WH / 2
        out.append(f'<line x1="{TICKS_X[0]}" y1="{f(ym)}" x2="{TICKS_X[1]}" y2="{f(ym)}" '
                   f'stroke="{T["ink"]}" stroke-width="{INK_W}" stroke-linecap="round"/>')
    out.append(label("time", AXIS_X, H - 36, T))
    out.append('</g>')
    return out


def build(theme):
    T = THEMES[theme]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(TITLE)}</title>',
           f'<desc id="desc">{escape(ALT)}</desc>',
           f'<rect width="{W}" height="{H}" rx="28" fill="{T["bg"]}"/>']
    out += caption("HORIZONTAL", (LEFT_X0 + LEFT_X1) / 2, TOP - 44, T)
    out += caption("VERTICAL", (COL_X + W - 40) / 2, TOP - 44, T)
    out += time_axis(T)
    out += horizontal(T)
    out += vertical(T)
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    assert ALT.startswith(TITLE + ". "), "the alt text opens with the title"
    checks = HERE / "checks"
    checks.mkdir(exist_ok=True)
    PNGS.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        where_to = checks if theme.startswith("same-colour") else HERE
        svg = where_to / f"{NAME}-{theme}.svg"
        png = (checks if theme.startswith("same-colour") else PNGS) / f"{NAME}-{theme}.png"
        svg.write_text(build(theme), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", str(W), "-o", str(png), str(svg)], check=True)
        print(f"{png}  {W}x{H}")
    alt = HERE / "alt.txt"
    alt.write_text(ALT + "\n", encoding="utf-8")
    print(alt)


if __name__ == "__main__":
    sys.exit(main())
