#!/usr/bin/env python3
"""Swarm picture B, "mismatch", for the long-term-memory-structure profile README.

It sits beside: "Cognition's Don't Build Multi-Agents gives an example: two subagents
can build a Flappy Bird game's background and bird in different styles, as neither sees
the other's work."

MANY AGENTS AT ONCE: three windows of the same size, side by side.  Each agent builds
its own piece of one graph and sees no other window, so the pieces come out in three
styles (discs, squares, diamonds) at three heights.  Where two pieces should join, in
the gap between their windows, each agent built its own half of the joint, heavy, in
its own style, aimed at the middle of the gap from its own height: the two ends arrive
there face to face, one higher than the other, and do not meet.

ONE AGENT OVER TIME: one window of that same size at the growing end of one graph in
one style.  The written part (red) is left behind, outside the window; the part not yet
written (green) grows inside it, joined across the frame.  One older written node is
read back into the window by address: a solid ink arrow from the ringed node to a
ringed red copy of it inside the window; a dashed green edge joins the copy to the
first green ring.

The series' look is meme 1's (memes/before-after/draw.py): its palette
T, its window chrome (a title bar with three dots) and its caption() lettering; written =
red solid nodes on solid lines; not yet written = green hollow rings with dashed
outlines on dashed lines; a read by address = a solid ink arrow with a head, the only
arrow in the picture.

Writes, beside this file (NAME = this folder's name): NAME-light.svg and NAME-dark.svg,
each rendered by rsvg-convert to a 2000-px-wide PNG of the same name in profile/memes/
(the README shows them from there), and alt.txt, the
alt text, which is also each SVG's <title> and <desc>.  No randomness: every coordinate
is computed from the constants below.  Needs rsvg-convert and the Fira Sans family (SIL
OFL): Fira Sans Condensed Heavy for the captions, Fira Sans SemiBold for the tag.

    python3 -I draw.py
"""
import math
import pathlib
import subprocess
import sys
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
NAME = HERE.name
PNGS = HERE.parent.parent / "profile" / "memes"   # the README shows the PNGs from there

ALT = ("Parts built apart do not fit. At the top, under MANY AGENTS AT ONCE, three "
       "windows of the same size stand side by side, and in each one an agent builds its "
       "own piece of one graph without seeing the other windows, so the three pieces come "
       "out in three different styles, red discs, red squares and red diamonds, at three "
       "different heights. Where two pieces should join, in the gap between their windows, "
       "each agent built its own half of the joint: the two heavy ends reach the middle of "
       "the gap from either side, one higher than the other, and do not meet. At the "
       "bottom, under ONE AGENT OVER TIME, one window of the same size sits at the growing "
       "end of one graph drawn in one style. The part already written, solid red discs on "
       "solid lines, runs outside the window to the left; the part not yet written, hollow "
       "green rings with dashed outlines on dashed lines, grows inside the window, joined "
       "to the red across its frame. A solid arrow marked by address reads one older red "
       "node back into the window as a ringed copy, and a dashed line joins the copy to "
       "the new green work.")

# ---- canvas -----------------------------------------------------------------
W = 2000
M = 44                      # outer margin
CAP = 150                   # caption band above each row
TB = 64                     # window title bar
CH = 320                    # window content height
WW = 500                    # window width: every window is the same size
WH = TB + CH
GAP = (W - 2 * M - 3 * WW) / 2            # between the top row's windows
ROWGAP = 40
BELOW = 136                 # under the bottom window: the arrow's dip and its tag
Y1 = M + CAP                              # top row: window top
Y2 = Y1 + WH + ROWGAP + CAP               # bottom row: window top
H = Y2 + WH + BELOW + M
XS = [M + i * (WW + GAP) for i in range(3)]

R = 19                      # node radius
S = 90                      # spine step
L = 62                      # branch level step
MID = CH / 2                # the spine's height in a window, when it is where it belongs

# meme 1's palette T, every key and value (its "title" colour is unused here: no
# window carries a title)
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

# strokes
RED_W = 7                   # a written edge
GREEN_W = 7                 # a not-yet-written edge, dashed
GREEN_DASH = "14 10"
RING_DASH_W = 6             # a not-yet-written node's dashed outline
RING_DASH = "7.5 5"
JOINT_W = 13                # a joint between two agents' pieces: heavier than any edge
END_SCALE = 1.5             # a joint's end node, in its piece's style, this much larger
JOINT_MISS = 84             # the two ends of a joint, flush at the middle of the gap, miss by this much
ADDR_R = R + 12             # the ink ring around a node read by address
ADDR_W = 5
ARROW_W = 7                 # the arrow's shaft
HEAD_L, HEAD_HW = 38, 19    # the arrow's head: length and half-width


# ---- the graphs (content coordinates of their window unless said otherwise) ---
def fishbone(x0, y0, n, first_up=True, step=S, level=L, bare=()):
    """A spine of n nodes; off each but the last a two-node branch, up and down in turn.

    Spine nodes listed in bare get no branch.
    Returns (nodes, edges, spine): spine[k] is the index of the k-th spine node."""
    nodes, edges, spine = [], [], []
    for k in range(n):
        nodes.append((x0 + k * step, y0))
        spine.append(len(nodes) - 1)
        if k:
            edges.append((spine[k - 1], spine[k]))
    for k in range(n - 1):
        if k in bare:
            continue
        sgn = -1 if (k % 2 == 0) == first_up else 1
        nodes.append((x0 + k * step + step / 2, y0 + sgn * level))
        nodes.append((x0 + (k + 1) * step, y0 + sgn * 2 * level))
        edges += [(spine[k], len(nodes) - 2), (len(nodes) - 2, len(nodes) - 1)]
    return nodes, edges, spine


def comb(x0, y0, n, step=S):
    """Agent 2's style: the spine high up, square nodes, teeth hanging straight down."""
    nodes, edges, spine = [], [], []
    for k in range(n):
        nodes.append((x0 + k * step, y0))
        spine.append(len(nodes) - 1)
        if k:
            edges.append((spine[k - 1], spine[k]))
        depth = 2 if k % 2 == 0 else 1
        prev = spine[k]
        for d in range(1, depth + 1):
            nodes.append((x0 + k * step, y0 + d * 80))
            edges.append((prev, len(nodes) - 1))
            prev = len(nodes) - 1
    return nodes, edges, spine


def backward(x0, y0, n, step=105):
    """Agent 3's style: the spine low down, bigger diamonds, branches leaning back."""
    nodes, edges, spine = [], [], []
    for k in range(n):
        nodes.append((x0 + k * step, y0))
        spine.append(len(nodes) - 1)
        if k:
            edges.append((spine[k - 1], spine[k]))
    for k in range(1, n):
        x = x0 + k * step
        nodes.append((x - 52, y0 - 72))
        edges.append((spine[k], len(nodes) - 1))
        if k % 2:
            nodes.append((x - 104, y0 - 144))
            edges.append((len(nodes) - 2, len(nodes) - 1))
    return nodes, edges, spine


PIECES = [  # (graph, node shape) per agent window, left to right
    (fishbone(50, MID, 5), "disc"),
    (comb(60, 56, 5), "square"),
    (backward(70, 256, 4, step=110), "diamond"),
]

# The bottom row: ONE graph.  The written part runs from the left margin to just
# outside the window; its last spine node sits one step before the window's first.
FIRST_GREEN_X = 60                                   # in the window
LAST_RED_X = XS[2] + FIRST_GREEN_X - S               # absolute
N_RED = int((LAST_RED_X - (M + 30)) // S) + 1
RED_X0 = LAST_RED_X - (N_RED - 1) * S
N_ALL = N_RED + 4                                    # 4 spine nodes inside the window
SOURCE_K = 3                                         # the branch read back by address
COPY_AT = (122, 74)          # the copy, from the window's left side and the spine: below
                             # and right of the first green ring, left of the next branch
ARRIVE_DEG = 64              # the arrow's last stretch rises this steeply into the window
ARROW_LOW = 170              # the arrow's dip: its first control point, this far below the window
ARROW_PULL = 240             # its last control point, this far back along the arrival
TAG_AT = (-20, 60)           # the tag: from the arrow's middle (x) and the window's bottom (y)


# ---- drawing ----------------------------------------------------------------
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def half_width(shape, scale=1.0):
    """How far a node of this shape reaches left and right of its centre."""
    return {"disc": R, "square": R + 2, "diamond": R + 9}[shape] * scale


def red_node(x, y, T, ring, shape="disc", scale=1.0, cls=None):
    """A solid red node; the ring is the colour of the surface under it."""
    common = f'fill="{T["red"]}" stroke="{ring}" stroke-width="3"'
    if cls:
        common = f'class="{cls}" ' + common
    h = half_width(shape, scale)
    if shape == "disc":
        return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(h)}" {common}/>'
    if shape == "square":
        return (f'<rect x="{f(x - h)}" y="{f(y - h)}" width="{f(2 * h)}" height="{f(2 * h)}" '
                f'{common}/>')
    if shape == "diamond":
        return (f'<polygon points="{f(x)},{f(y - h)} {f(x + h)},{f(y)} {f(x)},{f(y + h)} '
                f'{f(x - h)},{f(y)}" {common}/>')
    raise ValueError(f"red_node: shape {shape!r} is not one of disc, square, diamond")


def green_node(x, y, T):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{R}" fill="{T["content"]}" '
            f'stroke="{T["green"]}" stroke-width="{RING_DASH_W}" stroke-dasharray="{RING_DASH}"/>')


def red_edge(a, b, T, width=RED_W, cls=None):
    c = f'class="{cls}" ' if cls else ""
    return (f'<line {c}x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["red"]}" stroke-width="{width}" stroke-linecap="round"/>')


def green_edge(a, b, T, cls=None):
    c = f'class="{cls}" ' if cls else ""
    return (f'<line {c}x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{T["green"]}" stroke-width="{GREEN_W}" stroke-dasharray="{GREEN_DASH}"/>')


def window(x, y, T):
    out = [
        f'<rect x="{f(x)}" y="{f(y)}" width="{WW}" height="{WH}" rx="18" fill="{T["content"]}"/>',
        f'<path d="M{f(x)} {f(y + TB)} V{f(y + 18)} a18 18 0 0 1 18 -18 H{f(x + WW - 18)} '
        f'a18 18 0 0 1 18 18 V{f(y + TB)} Z" fill="{T["titlebar"]}"/>',
        f'<line x1="{f(x)}" y1="{f(y + TB)}" x2="{f(x + WW)}" y2="{f(y + TB)}" '
        f'stroke="{T["frame"]}" stroke-width="4"/>',
    ]
    for i in range(3):
        out.append(f'<circle cx="{f(x + 40 + 36 * i)}" cy="{f(y + TB / 2)}" r="12" fill="{T["dot"]}"/>')
    return out


def content_clip(cid, x, y, T):
    """The window's content area, in <defs> and filled with the content colour: QtSvg
    paints a clipPath it finds outside <defs> as a black shape over the window."""
    top, bot = y + TB, y + WH
    return (f'<defs><clipPath id="{cid}"><path d="M{f(x)} {f(top)} H{f(x + WW)} V{f(bot - 18)} '
            f'a18 18 0 0 1 -18 18 H{f(x + 18)} a18 18 0 0 1 -18 -18 Z" fill="{T["content"]}"/>'
            f'</clipPath></defs>')


def frame(x, y, T):
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{WW}" height="{WH}" rx="18" fill="none" '
            f'stroke="{T["frame"]}" stroke-width="5"/>')


def caption(text, cx, baseline, T, size=124):
    """meme 1's caption(): white Fira Sans Condensed Heavy, outlined in black."""
    common = (f'x="{f(cx)}" y="{f(baseline)}" text-anchor="middle" font-family="Fira Sans Condensed" '
              f'font-weight="900" font-size="{size}" letter-spacing="5"')
    return [
        f'<text {common} fill="{T["cap_stroke"]}" stroke="{T["cap_stroke"]}" stroke-width="18" '
        f'stroke-linejoin="round">{text}</text>',
        f'<text {common} fill="{T["cap_fill"]}">{text}</text>',
    ]


def label(text, x, y, T, size=64, anchor="middle", weight=600):
    return (f'<text class="tag" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="Fira Sans" '
            f'font-weight="{weight}" font-size="{size}" fill="{T["ink"]}">{text}</text>')


def cubic_arrow(p0, c1, c2, tip, T):
    """A solid ink arrow along a cubic Bezier; the head is laid along the end tangent."""
    tx, ty = tip[0] - c2[0], tip[1] - c2[1]
    n = math.hypot(tx, ty)
    ux, uy = tx / n, ty / n
    bx, by = tip[0] - ux * HEAD_L, tip[1] - uy * HEAD_L
    # stop the shaft inside the head so its round cap does not poke out of the tip
    sx, sy = tip[0] - ux * (HEAD_L - 6), tip[1] - uy * (HEAD_L - 6)
    head = (f"{f(tip[0])},{f(tip[1])} {f(bx - uy * HEAD_HW)},{f(by + ux * HEAD_HW)} "
            f"{f(bx + uy * HEAD_HW)},{f(by - ux * HEAD_HW)}")
    return [f'<path class="arrow" d="M{f(p0[0])} {f(p0[1])} C{f(c1[0])} {f(c1[1])} '
            f'{f(c2[0])} {f(c2[1])} {f(sx)} {f(sy)}" fill="none" stroke="{T["ink"]}" '
            f'stroke-width="{ARROW_W}" stroke-linecap="round"/>',
            f'<polygon class="arrow-head" points="{head}" fill="{T["ink"]}"/>']


def ring(x, y, T):
    return (f'<circle class="address-ring" cx="{f(x)}" cy="{f(y)}" r="{ADDR_R}" fill="none" '
            f'stroke="{T["ink"]}" stroke-width="{ADDR_W}"/>')


def build(T):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{f(H)}" '
           f'viewBox="0 0 {W} {f(H)}" role="img" aria-labelledby="title">',
           f'<title id="title">{escape(ALT)}</title>',
           f'<desc id="desc">{escape(ALT)}</desc>',
           f'<rect width="{W}" height="{f(H)}" rx="28" fill="{T["bg"]}"/>']

    # ---- MANY AGENTS AT ONCE: three windows, three pieces that do not join ----
    out += caption("MANY AGENTS AT ONCE", W / 2, Y1 - 30, T)
    ends = []                      # per piece: (first spine node, last spine node, shape)
    for i, ((nodes, edges, spine), shape) in enumerate(PIECES):
        wx = XS[i]
        P = lambda p, wx=wx: (wx + p[0], Y1 + TB + p[1])
        out += window(wx, Y1, T)
        out.append(content_clip(f"agent{i}", wx, Y1, T))
        out.append(f'<g class="piece" clip-path="url(#agent{i})">')
        for a, b in edges:
            out.append(red_edge(P(nodes[a]), P(nodes[b]), T))
        for p in nodes:
            out.append(red_node(*P(p), T, T["content"], shape))
        out.append('</g>')
        out.append(frame(wx, Y1, T))
        ends.append((P(nodes[spine[0]]), P(nodes[spine[-1]]), shape))
    # Where two pieces should meet, each agent built its half of the joint itself: heavy,
    # in its own style, aimed from its own height at the middle of the gap.  The two ends
    # arrive there face to face (flush at the middle), the higher piece's end still the
    # higher by JOINT_MISS, and nothing joins them.
    joints = []                    # (spine end, joint end, shape)
    for i in range(2):
        mid = XS[i] + WW + GAP / 2
        (_, left_end, left_shape), (right_end, _, right_shape) = ends[i], ends[i + 1]
        meet = (left_end[1] + right_end[1]) / 2
        sgn = 1 if left_end[1] > right_end[1] else -1          # +1: the left piece is the lower
        yl, yr = meet + sgn * JOINT_MISS / 2, meet - sgn * JOINT_MISS / 2
        joints.append((left_end, (mid - half_width(left_shape, END_SCALE), yl), left_shape))
        joints.append((right_end, (mid + half_width(right_shape, END_SCALE), yr), right_shape))
    for end, joint, shape in joints:
        out.append(red_edge(end, joint, T, width=JOINT_W, cls="joint"))
    for end, joint, shape in joints:
        out.append(red_node(*joint, T, T["bg"], shape, scale=END_SCALE, cls="joint-end"))

    # ---- ONE AGENT OVER TIME: one window, one graph, joined -----------------
    out += caption("ONE AGENT OVER TIME", W / 2, Y2 - 30, T)
    wx = XS[2]
    spine_y = Y2 + TB + MID
    # the last written spine node grows no branch: its branch would sit on the frame
    nodes, edges, spine = fishbone(RED_X0, spine_y, N_ALL, bare=(N_RED - 1,))
    written = lambda p: p[0] < wx                     # left of the window: written
    out += window(wx, Y2, T)

    # the older written node read back by address, and its copy inside the window
    tips = [n for n in nodes if abs(n[0] - (RED_X0 + (SOURCE_K + 1) * S)) < 1 and n[1] > spine_y + L]
    if len(tips) != 1:
        sys.exit(f"draw.py: SOURCE_K={SOURCE_K}: expected 1 lower branch tip at "
                 f"x={RED_X0 + (SOURCE_K + 1) * S}, found {len(tips)}; pick a k whose branch points down")
    src = tips[0]
    first_green = nodes[spine[N_RED]]
    copy = (wx + COPY_AT[0], spine_y + COPY_AT[1])

    # edges first, nodes on top; an edge with a node inside the window is not yet written
    for a, b in edges:
        if written(nodes[a]) and written(nodes[b]):
            out.append(red_edge(nodes[a], nodes[b], T))
    for a, b in edges:
        if not (written(nodes[a]) and written(nodes[b])):
            out.append(green_edge(nodes[a], nodes[b], T))
    # the copy's edge runs between the two rings' outer edges, not centre to centre: its
    # dash pattern starts at the copy's address ring, so the short span shows whole dashes
    span = math.dist(copy, first_green)
    v = ((first_green[0] - copy[0]) / span, (first_green[1] - copy[1]) / span)
    r_copy, r_green = ADDR_R + ADDR_W / 2, R + RING_DASH_W / 2
    out.append(green_edge((copy[0] + v[0] * r_copy, copy[1] + v[1] * r_copy),
                          (first_green[0] - v[0] * r_green, first_green[1] - v[1] * r_green), T, cls="copy-edge"))
    for p in nodes:
        out.append(red_node(*p, T, T["bg"]) if written(p) else green_node(*p, T))
    out.append(red_node(*copy, T, T["content"], cls="copy"))
    out.append(frame(wx, Y2, T))
    for a, b in edges:             # the joins cross the frame: draw them over it
        if written(nodes[a]) != written(nodes[b]):
            out.append(green_edge(nodes[a], nodes[b], T))
    for a, b in edges:             # then their two end nodes again, so the dashes stop at the nodes' outlines
        if written(nodes[a]) != written(nodes[b]):
            for p in (nodes[a], nodes[b]):
                out.append(red_node(*p, T, T["bg"]) if written(p) else green_node(*p, T))
    for p in nodes:
        if not written(p) and p[0] - R < wx + 8:
            out.append(green_node(*p, T))

    # the arrow dips under the written graph and rises into the window to the copy
    out.append(ring(*src, T))
    out.append(ring(*copy, T))
    a = math.radians(ARRIVE_DEG)
    u = (math.cos(a), -math.sin(a))
    reach = ADDR_R + ADDR_W / 2 + 3                       # the tip stops just short of the ring
    tip = (copy[0] - u[0] * reach, copy[1] - u[1] * reach)
    c1 = (src[0] + 20, Y2 + WH + ARROW_LOW)
    c2 = (tip[0] - u[0] * ARROW_PULL, tip[1] - u[1] * ARROW_PULL)
    out += cubic_arrow((src[0], src[1] + ADDR_R + ADDR_W / 2), c1, c2, tip, T)
    out.append(label("by address", (src[0] + tip[0]) / 2 + TAG_AT[0], Y2 + WH + TAG_AT[1], T))
    # the copy's ring and the arrow's head must sit inside the window's content, clear of
    # its frame (stroke 5, so its inner edge is 2.5 inside the window's outline)
    hx = tip[0] - u[0] * HEAD_L
    hy = tip[1] - u[1] * HEAD_L
    marks = {"copy ring": [(copy[0] + dx * (ADDR_R + ADDR_W / 2), copy[1] + dy * (ADDR_R + ADDR_W / 2))
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))],
             "arrow head": [tip, (hx - u[1] * HEAD_HW, hy + u[0] * HEAD_HW), (hx + u[1] * HEAD_HW, hy - u[0] * HEAD_HW)]}
    lo_x, hi_x, lo_y, hi_y = wx + 2.5 + 6, wx + WW - 2.5 - 6, Y2 + TB + 2 + 6, Y2 + WH - 2.5 - 6
    for what, pts in marks.items():
        bad = [(round(x, 1), round(y, 1)) for x, y in pts if not (lo_x <= x <= hi_x and lo_y <= y <= hi_y)]
        if bad:
            sys.exit(f"draw.py: the {what} reaches outside the window's content less a 6-px margin "
                     f"(x {lo_x}..{hi_x}, y {lo_y}..{hi_y}) at {bad}; COPY_AT={COPY_AT}, "
                     f"ARRIVE_DEG={ARRIVE_DEG}: move the copy or change the arrival angle")

    out.append("</svg>")
    return "\n".join(out) + "\n"


def render(svg_text, stem, folder):
    svg = folder / f"{stem}.svg"
    PNGS.mkdir(parents=True, exist_ok=True)
    png = PNGS / f"{stem}.png"
    svg.write_text(svg_text)
    subprocess.run(["rsvg-convert", "-w", str(W), "-o", str(png), str(svg)], check=True)
    print(f"{png}  {W}x{f(H)}")


def main():
    for theme, T in THEMES.items():
        render(build(T), f"{NAME}-{theme}", HERE)
    (HERE / "alt.txt").write_text(ALT + "\n")
    print(HERE / "alt.txt")


if __name__ == "__main__":
    sys.exit(main())
