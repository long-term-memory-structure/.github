#!/usr/bin/env python3
"""Many agents at once, or one agent over time: the swarm picture for the
long-term-memory-structure profile README (his recording 05, "to swarm or not
to swarm"); his pick, A, the committee.  It sits beside the README's sentence
"Between agents, it says, you "often lose details in the back and forth"; one
agent that has seen each earlier step can connect them."

One task, one graph, in the first meme's language: red solid discs on solid
lines are the part already written; green hollow rings with dashed outlines, on
dashed lines, the part not yet written.  A context window is a framed app
window.  A solid ink arrow with a head is a read by address, and nothing else
in the picture is one.

HORIZONTAL, many agents at once: four context windows side by side, a
committee (orchestrator, architect, coder, tester).  The task's graph is cut
into four pieces, one per window, and every agent is mid-work at the same
moment: each window holds a written head and a not-yet-written tail.  Messages
(envelopes, no arrows) fly over the gaps between neighbouring windows, back and
forth; the steps that fall between two windows drop through the gaps and pile
up, lost.

VERTICAL, one agent over time: the same graph, whole, running down the page in
time, and one window at its end, where the work is now.  What the agent wrote
stays outside the window, on disk, and it reads one written node back into the
window by its address.  The node it reads is the very one that, in the
committee, fell through the first gap.  (A first draft drew the window's
earlier places as faint frames along the graph; they read as one tall window
around the written part, the opposite of "outside the window", and were cut.)

The look is the series': the first meme's (memes/before-after/draw.py) palette,
window chrome and caption lettering, its values copied here; check.py compares
them with before-after/draw.py's.  Edges are cut at the window frames here, in the script,
not clipped by the renderer: QtSvg (behind KDE's file previews) ignores the
clip, and the graph then ran across the gaps between the windows.  No clipPath.

Writes, next to this file, <name>-light.svg and <name>-dark.svg (<name> = this
folder's name), each rendered to a 2000-px-wide PNG with rsvg-convert in
profile/memes/ (the README shows them from there), and alt.txt, the alt text (also each SVG's <title> and <desc>, as the README's
assembler, tools/assemble.mjs, expects); and checks/same-colour.svg/.png,
the light picture with red and green in one grey (if the two still read apart
there, shape and line carry the difference, not hue).  Deterministic: no
randomness.  Refuses to write when a label touches a node, an envelope or an
arrow, or leaves the canvas; or when a node or an edge crosses a window frame.

Needs: rsvg-convert and fc-match; Pillow (to measure the text with the font
files fontconfig picks, the ones rsvg-convert draws with); Fira Sans SemiBold
and Fira Sans Condensed Heavy (SIL OFL).

    python3 -I draw.py
"""
import math
import subprocess
import sys
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
NAME = HERE.name
PNGS = HERE.parent.parent / "profile" / "memes"   # the README shows the PNGs from there
CHECKS = HERE / "checks"

# ---- fonts: measured with the files fontconfig hands rsvg-convert -------------------
# (family, CSS weight) -> (fontconfig pattern, the style it must resolve to)
FONTS = {("Fira Sans", 600): ("Fira Sans:weight=180", "SemiBold"),
         ("Fira Sans Condensed", 900): ("Fira Sans Condensed:weight=210", "Heavy")}
_FONT_FILES = {}


def font(family, weight, size):
    key = (family, weight)
    if key not in _FONT_FILES:
        pattern, style = FONTS[key]
        got = subprocess.run(["fc-match", "-f", "%{file}|%{family}|%{style}", pattern],
                             capture_output=True, text=True, check=True).stdout
        path, fams, styles = got.split("|")
        if family not in fams.split(",") or style not in styles.split(","):
            sys.exit(f"draw.py: fc-match {pattern!r} gave {path} ({fams}; {styles}), not "
                     f"{family} {style}: install the Fira Sans family, then run python3 -I draw.py")
        _FONT_FILES[key] = path
    return ImageFont.truetype(_FONT_FILES[key], size)


TAG_FONT = ("Fira Sans", 600)
TAG_SIZE = 64             # every word >= 64 px on the 2000-px canvas: 12.8 px on a 400-px phone
CAP_FONT = ("Fira Sans Condensed", 900)
CAP_SIZE = 124            # before-after/draw.py's caption(): size, letter-spacing, stroke
CAP_SPACING = 5
CAP_STROKE = 18

# ---- palette: before-after/draw.py's THEMES, copied (check.py compares them with before-after/draw.py's) ------
THEMES = {
    "light": dict(bg="#f3f0e8", frame="#1d1d1f", titlebar="#e4e0d6", content="#ffffff",
                  dot="#b3ada1", title="#4d4a44", ink="#1d1d1f",
                  red="#b81d24", green="#23a55a",
                  cap_fill="#ffffff", cap_stroke="#000000"),
    "dark": dict(bg="#16191e", frame="#aab2bd", titlebar="#2a3038", content="#0f1217",
                 dot="#5d6670", title="#c3cad3", ink="#e8ebef",
                 red="#d93a42", green="#4cc777",
                 cap_fill="#ffffff", cap_stroke="#000000"),
}
THEMES["same-colour"] = dict(THEMES["light"], red="#6e7781", green="#6e7781")
# The grey of the motion lines (behind what falls and what flies) and of the
# divider between the panels: before-after/draw.py has no such marks; its quiet grey is the
# title bar's dots.
SOFT = "dot"
# That grey is lighter than the motion lines' first grey (1.96:1 on the light
# canvas, against 3.16:1), so the lines are thicker than their first 5 px, to
# stay visible on a 400-px phone.
MOTION_W = 7

# ---- canvas and panels ------------------------------------------------------------
W, H = 2000, 1300
M = 36                    # outer margin
DIVIDER_X = 1264          # between the two panels
DIVIDER_W = 5
LEFT = (M, DIVIDER_X - 24)
RIGHT = (DIVIDER_X + 24, W - M)
TITLE_BASE = 160          # the captions' baseline

# ---- the context window: the same size in both panels; before-after/draw.py's chrome --------------
WW = 232                  # width
TB = 72                   # title bar (72, as meme 1's was before its title grew)
CONTENT = 270
WH = TB + CONTENT
CORNER = 18               # before-after/draw.py: rx 18
FRAME_W = 5               # before-after/draw.py: the frame's stroke
BAR_LINE_W = 4            # before-after/draw.py: the line under the title bar
DOT_R, DOT_X0, DOT_DX = 12, 40, 36     # before-after/draw.py: three dots, r 12, at 40 + 36 i

# ---- the graph --------------------------------------------------------------------
R = 15                    # node radius
EDGE_W = 7
RING_W = 6                # outline of a not-yet-written ring
RING_DASH = "7.5 5"
EDGE_DASH = "14 10"
# Edges must stay long enough between two discs to read as lines, not dashes
# (dashes mean "not yet written"): at least ~20 px of red between the discs.
BRANCH_STEP = 54          # a branch node's distance from the spine, per level
LEAN = 12                 # ... and how far it leans forward in time, per level

# The task: 15 steps in time along a spine.  Each step has short branches on
# its two sides; side -1 is up in the row and right in the column, side +1 down
# in the row and left in the column.
# Limits: a window's third step keeps its branches to one level (the row's
# right frame), and so do steps 12-14 (the column's window is too narrow for a
# second level on either side); step 12 has nothing on side -1, where the
# column's window keeps the node read back by its address.
BRANCHES = [(2, 1), (1, 2), (1, 0), (1, 1),
            (1, 2), (2, 1), (0, 1), (1, 1),
            (2, 0), (1, 2), (1, 1), (1, 1),
            (0, 1), (1, 1), (1, 0)]
STEPS = len(BRANCHES)
# VERTICAL, one agent over time: steps 0..11 are written, 12..14 not yet.
WRITTEN = 12
# HORIZONTAL: each window holds three steps and the fourth falls in the gap
# after it: steps 3, 7 and 11.
FELL = [3, 7, 11]

# ---- HORIZONTAL: the row -------------------------------------------------------------
GAP = 84
SX = (WW + GAP) / 4       # spine spacing: three steps per window, one per gap
ROW_W = 4 * WW + 3 * GAP
ROW_X0 = LEFT[0] + (LEFT[1] - LEFT[0] - ROW_W) / 2
ROW_Y = 352               # top of the windows
ROW_YC = ROW_Y + TB + CONTENT / 2
SPINE_X0 = ROW_X0 + (WW - 2 * SX) / 2
ENV_W, ENV_H = 76, 52     # an envelope
ENV_Y = ROW_Y - 66        # the envelopes' centres: over the gaps, above the windows
# The messages, back and forth: (gap, direction of flight): window 1 -> 2,
# 3 -> 2, 3 -> 4 (counting from the left).
MESSAGES = [(0, 1), (1, -1), (2, 1)]

# ---- VERTICAL: the column -------------------------------------------------------------
COL_X0 = RIGHT[0] + 12
COL_SPINE_X = COL_X0 + WW / 2
NOW_TOP = H - M - WH      # the window, where it is now
NOW_STEP0_Y = NOW_TOP + TB + 62      # step 12, the first not yet written
NOW_SY = 70
PAST_LAST_Y = NOW_TOP - 50           # step 11, the last written: just above the window
PAST_SY = 57


# =====================================================================================
# the graph's nodes and edges, and their two layouts
# =====================================================================================
def nodes():
    out = []
    for t, lengths in enumerate(BRANCHES):
        out.append(("s", t))
        for side, n in zip((-1, 1), lengths):
            out += [("b", t, side, k) for k in range(1, n + 1)]
    return out


def edges():
    out = [(("s", t - 1), ("s", t)) for t in range(1, STEPS)]
    for t, lengths in enumerate(BRANCHES):
        for side, n in zip((-1, 1), lengths):
            prev = ("s", t)
            for k in range(1, n + 1):
                out.append((prev, ("b", t, side, k)))
                prev = ("b", t, side, k)
    return out


def step(node):
    return node[1]


def col_written(node):
    """VERTICAL: one agent over time."""
    return step(node) < WRITTEN


def row_written(node):
    """HORIZONTAL: every agent mid-work at the same moment.  In each window the
    first step and the spine node of the second are written, the red head; the
    second step's branches and the third step are not yet, the green tail.  The
    step in the gap after a window was written, and falls."""
    i = step(node) % 4
    return i in (0, 3) or (i == 1 and node[0] == "s")


def row_xy(node):
    t = step(node)
    x, y = SPINE_X0 + t * SX, ROW_YC
    if node[0] == "b":
        _, _, side, k = node
        x, y = x + k * LEAN, y + side * k * BRANCH_STEP
    return x, y


def col_spine_y(t):
    if t < WRITTEN:
        return PAST_LAST_Y - (WRITTEN - 1 - t) * PAST_SY
    return NOW_STEP0_Y + (t - WRITTEN) * NOW_SY


def col_xy(node):
    t = step(node)
    x, y = COL_SPINE_X, col_spine_y(t)
    if node[0] == "b":
        _, _, side, k = node
        x, y = x - side * k * BRANCH_STEP, y + k * LEAN
    return x, y


def row_place(node):
    """('win', k) for a step inside window k, ('gap', k) for one in the gap after it."""
    t = step(node)
    return ("gap", t // 4) if t % 4 == 3 else ("win", t // 4)


def window_x(k):
    return ROW_X0 + k * (WW + GAP)


def gap_x(k):
    """The middle of the gap after window k."""
    return window_x(k) + WW + GAP / 2


def outer_box(x, y):
    return (x, y, x + WW, y + WH)


def content_box(x, y):
    return (x, y + TB, x + WW, y + WH)


WINDOWS = [("row", k, window_x(k), ROW_Y) for k in range(4)] + [("now", 0, COL_X0, NOW_TOP)]


def clip(p, q, box):
    """Liang-Barsky: the parameters (t0, t1) of the part of the segment pq inside
    box, or None when no part of it is."""
    x0, y0, x1, y1 = box
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pk == 0:
            if qk < 0:
                return None
            continue
        r = qk / pk
        if pk < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
    return (t0, t1) if t0 <= t1 else None


def at(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


# =====================================================================================
# SVG pieces
# =====================================================================================
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# What is placed, for the layout checks: text ink boxes, node discs (and where
# they are: inside which window, or outside all), graph segments (likewise),
# and the boxes of other marks a label must not touch.
PLACED_TEXT = []     # (text, (x0, y0, x1, y1))
DRAWN_NODES = []     # (x, y, r, where)
DRAWN_SEGMENTS = []  # (p, q, half width, where, cut)
DRAWN_MARKS = []     # (what, (x0, y0, x1, y1))
WORDS = []
OUT = None           # where: None = outside every window; else (panel, k)


def text(x, y, s, size, fill, anchor="middle"):
    fnt = font(*TAG_FONT, size)
    l, t, r, b = fnt.getbbox(s, anchor="ls")
    adv = fnt.getlength(s)
    shift = {"start": 0, "middle": -adv / 2, "end": -adv}[anchor]
    PLACED_TEXT.append((s, (x + shift + l, y + t, x + shift + r, y + b)))
    WORDS.extend(s.split())
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="{TAG_FONT[0]}" font-size="{size}" '
            f'font-weight="{TAG_FONT[1]}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


def caption(s, cx, baseline, th):
    """before-after/draw.py's caption(): Fira Sans Condensed 900, white over a black stroke."""
    fnt = font(*CAP_FONT, CAP_SIZE)
    l, t, r, b = fnt.getbbox(s, anchor="ls")
    adv = fnt.getlength(s) + CAP_SPACING * len(s)
    pad = CAP_STROKE / 2
    PLACED_TEXT.append((s, (cx - adv / 2 + l - pad, baseline + t - pad,
                            cx + adv / 2 + pad, baseline + b + pad)))
    WORDS.extend(s.split())
    common = (f'x="{f(cx)}" y="{f(baseline)}" text-anchor="middle" font-family="{CAP_FONT[0]}" '
              f'font-weight="{CAP_FONT[1]}" font-size="{CAP_SIZE}" letter-spacing="{CAP_SPACING}"')
    return [f'<text {common} fill="{th["cap_stroke"]}" stroke="{th["cap_stroke"]}" '
            f'stroke-width="{CAP_STROKE}" stroke-linejoin="round">{esc(s)}</text>',
            f'<text {common} fill="{th["cap_fill"]}">{esc(s)}</text>']


def red_node(x, y, th, surface, where=OUT):
    DRAWN_NODES.append((x, y, R + 1.5, where))
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{R}" fill="{th["red"]}" '
            f'stroke="{surface}" stroke-width="3"/>')


def green_node(x, y, th, surface, where=OUT):
    DRAWN_NODES.append((x, y, R, where))
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(R - RING_W / 2)}" fill="{surface}" '
            f'stroke="{th["green"]}" stroke-width="{RING_W}" stroke-dasharray="{RING_DASH}"/>')


def edge(p, q, th, is_written, where=OUT, cut=False):
    """An edge of the graph.  cut: one end lies on a window's frame, so the line
    ends square there (a round cap would poke out past the frame)."""
    DRAWN_SEGMENTS.append((p, q, EDGE_W / 2, where, cut))
    if is_written:
        return (f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
                f'stroke="{th["red"]}" stroke-width="{EDGE_W}" '
                f'stroke-linecap="{"butt" if cut else "round"}"/>')
    return (f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
            f'stroke="{th["green"]}" stroke-width="{EDGE_W}" stroke-dasharray="{EDGE_DASH}"/>')


def window_body(x, y, th):
    """before-after/draw.py's window: the content, and the title bar with its rounded top."""
    c = CORNER
    return [f'<rect x="{f(x)}" y="{f(y)}" width="{WW}" height="{WH}" rx="{c}" fill="{th["content"]}"/>',
            f'<path d="M{f(x)} {f(y + TB)} V{f(y + c)} a{c} {c} 0 0 1 {c} -{c} H{f(x + WW - c)} '
            f'a{c} {c} 0 0 1 {c} {c} V{f(y + TB)} Z" fill="{th["titlebar"]}"/>']


def window_chrome(x, y, th):
    """before-after/draw.py's chrome, drawn over the content: the title bar's line, the three
    dots, the frame."""
    out = [f'<line x1="{f(x)}" y1="{f(y + TB)}" x2="{f(x + WW)}" y2="{f(y + TB)}" '
           f'stroke="{th["frame"]}" stroke-width="{BAR_LINE_W}"/>']
    for i in range(3):
        out.append(f'<circle cx="{f(x + DOT_X0 + DOT_DX * i)}" cy="{f(y + TB / 2)}" r="{DOT_R}" '
                   f'fill="{th["dot"]}"/>')
    out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{WW}" height="{WH}" rx="{CORNER}" fill="none" '
               f'stroke="{th["frame"]}" stroke-width="{FRAME_W}"/>')
    return out


def bezier(p, t):
    """A point on the cubic Bezier with control points p[0..3]."""
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                 for a, b, c, d in zip(*p))


def arrow(p, th, width, head_len, head_w, stop=0.0, what="arrow"):
    """A solid ink arrow along the cubic p[0..3], its tip `stop` short of p[3]."""
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if math.dist(bezier(p, mid), p[3]) > stop:
            lo = mid
        else:
            hi = mid
    pts = [bezier(p, lo * i / 80) for i in range(81)]
    tip, before = pts[-1], pts[-4]
    ang = math.atan2(tip[1] - before[1], tip[0] - before[0])
    shaft = [q for q in pts if math.dist(q, tip) > head_len * 0.7]
    for q in pts[::4]:
        DRAWN_MARKS.append((what, (q[0] - width, q[1] - width, q[0] + width, q[1] + width)))
    bx, by = tip[0] - head_len * math.cos(ang), tip[1] - head_len * math.sin(ang)
    lx, ly = bx + head_w * math.sin(ang), by - head_w * math.cos(ang)
    rx, ry = bx - head_w * math.sin(ang), by + head_w * math.cos(ang)
    DRAWN_MARKS.append((what + " head", (min(tip[0], lx, rx), min(tip[1], ly, ry),
                                         max(tip[0], lx, rx), max(tip[1], ly, ry))))
    return [f'<path d="M{" L".join(f"{f(x)},{f(y)}" for x, y in shaft)}" fill="none" '
            f'stroke="{th["ink"]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="M{f(tip[0])},{f(tip[1])} L{f(lx)},{f(ly)} L{f(rx)},{f(ry)} Z" fill="{th["ink"]}"/>']


def envelope(cx, cy, th):
    w, h = ENV_W, ENV_H
    DRAWN_MARKS.append(("envelope", (cx - w / 2 - 3, cy - h / 2 - 3, cx + w / 2 + 3, cy + h / 2 + 3)))
    return [f'<g transform="translate({f(cx)} {f(cy)})">',
            f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="5" fill="{th["content"]}" '
            f'stroke="{th["ink"]}" stroke-width="5"/>',
            f'<path d="M{-w / 2 + 3},{-h / 2 + 3} L0,{h / 2 - 20} L{w / 2 - 3},{-h / 2 + 3}" fill="none" '
            f'stroke="{th["ink"]}" stroke-width="4.5" stroke-linejoin="round"/>',
            '</g>']


def ring(x, y, th):
    r = R + 11
    DRAWN_MARKS.append(("ring", (x - r - 3, y - r - 3, x + r + 3, y + r + 3)))
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="none" stroke="{th["ink"]}" stroke-width="5"/>'


def motion_lines(back, direction, th, lengths=(46, 70, 40), spread=22, what="motion lines"):
    """Short strokes behind something moving: `back` is its trailing edge, on
    the line of motion; `direction` the unit vector of the motion."""
    dx, dy = direction
    nx, ny = dy, -dx
    out = []
    for i, n in enumerate(lengths):
        ex = back[0] - dx * 14 + nx * (i - 1) * spread
        ey = back[1] - dy * 14 + ny * (i - 1) * spread
        sx, sy = ex - dx * n, ey - dy * n
        DRAWN_MARKS.append((what, (min(sx, ex) - MOTION_W / 2, min(sy, ey) - MOTION_W / 2, max(sx, ex) + MOTION_W / 2, max(sy, ey) + MOTION_W / 2)))
        out.append(f'<line x1="{f(sx)}" y1="{f(sy)}" x2="{f(ex)}" y2="{f(ey)}" '
                   f'stroke="{th[SOFT]}" stroke-width="{MOTION_W}" stroke-linecap="round"/>')
    return out


# =====================================================================================
# HORIZONTAL
# =====================================================================================
# What falls from each gap: pieces of the step that lay in it.  Each piece is
# (its nodes, the node placed at `at`, its turn in degrees, at = (dx from the
# gap's centre, y)).
# The first piece out of each gap is still between the two windows, just
# under the cut, so it is seen to drop out of the graph.
FALLING = {
    0: [(["A1", "s", "B1"], "s", 14, (-8, 640))],
    1: [(["A1", "s"], "s", -30, (2, 760)), (["B1"], "B1", 0, (-6, 930))],
    2: [(["s", "B1"], "s", 40, (8, 650)), (["A1"], "A1", 0, (6, 870))],
}
# Below them, details lost at earlier hand-offs, still falling: a single node
# ("one") or two joined by an edge ("pair"), as (gap, shape, turn, at).
RAIN = [(0, "one", 0, (6, 875)), (0, "pair", -50, (-4, 1050)),
        (1, "one", 0, (8, 1090)), (2, "pair", 35, (-6, 1045))]
RAIN_SHAPES = {"one": ({"a": (0, 0)}, []),
               "pair": ({"a": (0, 0), "b": (LEAN, BRANCH_STEP)}, [("a", "b")])}
# What lies at the bottom: details lost before these.  (dx, dy) from the gap's
# centre at the floor.
HEAPS = {
    0: [(-30, 0), (6, -2), (40, 1), (-12, -32)],
    1: [(-36, 1), (-2, -1), (32, 0), (16, -32), (-20, -31)],
    2: [(-24, 0), (12, -1), (-6, -32)],
}
FLOOR_Y = H - M - 40


def step_piece(gap, names):
    """The named nodes (s, A1, B1) of the step that fell in this gap, where the
    row would have put them, and the edges among them."""
    t = FELL[gap]
    full = {"s": ("s", t), "A1": ("b", t, -1, 1), "B1": ("b", t, 1, 1)}
    links = [(a, b) for a, b in (("s", "A1"), ("s", "B1")) if a in names and b in names]
    return {k: row_xy(full[k]) for k in names}, links


def fallen_piece(gap, pos, links, anchor, angle, where, th):
    names = sorted(pos)
    ax, ay = pos[anchor]
    tx, ty = gap_x(gap) + where[0], where[1]
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    placed = {k: (tx + (x - ax) * c - (y - ay) * s, ty + (x - ax) * s + (y - ay) * c)
              for k, (x, y) in pos.items()}
    # beside the windows, a piece must stay inside its gap, clear of both frames
    inner_l = window_x(gap) + WW + FRAME_W / 2 + 4
    inner_r = window_x(gap + 1) - FRAME_W / 2 - 4
    for k, (x, y) in placed.items():
        if y - R < ROW_Y + WH + 10 and not (inner_l <= x - R - 1.5 and x + R + 1.5 <= inner_r):
            sys.exit(f"draw.py: the falling piece {names} of gap {gap} has its node {k} at "
                     f"({x:.0f},{y:.0f}), outside the gap {inner_l:.0f}..{inner_r:.0f}; "
                     f"change its turn or dx in FALLING or RAIN")
    out = [edge(placed[a], placed[b], th, True) for a, b in links]
    for k, p in placed.items():
        out.append(red_node(*p, th, th["bg"]))
    top = min(p[1] for p in placed.values()) - R
    xs = [p[0] for p in placed.values()]
    trail = (46, 70, 40) if len(placed) > 1 else (34, 52, 30)
    out = motion_lines(((min(xs) + max(xs)) / 2, top), (0, 1), th, trail) + out
    return out


def heap(gap, th):
    gx = gap_x(gap)
    return [red_node(gx + dx, FLOOR_Y + dy, th, th["bg"]) for dx, dy in HEAPS[gap]]


def horizontal(th):
    out = caption("HORIZONTAL", (LEFT[0] + LEFT[1]) / 2, TITLE_BASE, th)
    all_nodes, all_edges = nodes(), edges()
    for k in range(4):
        x = window_x(k)
        inside = ("row", k)
        box = content_box(x, ROW_Y)
        out += window_body(x, ROW_Y, th)
        for a, b in all_edges:
            pa, pb = row_place(a), row_place(b)
            if ("win", k) not in (pa, pb):
                continue
            is_written = row_written(a) and row_written(b)
            p, q = row_xy(a), row_xy(b)
            if pa == pb:
                out.append(edge(p, q, th, is_written, inside))
                continue
            # one end in this window, the other in a gap: cut at the frame
            if pb == ("win", k):
                p, q = q, p
            t0, t1 = clip(p, q, box)
            out.append(edge(p, at(p, q, t1), th, is_written, inside, cut=True))
        for n in all_nodes:
            if row_place(n) == ("win", k):
                draw = red_node if row_written(n) else green_node
                out.append(draw(*row_xy(n), th, th["content"], inside))
        out += window_chrome(x, ROW_Y, th)
    for gap, pieces in FALLING.items():
        for names, anchor, angle, where in pieces:
            pos, links = step_piece(gap, names)
            out += fallen_piece(gap, pos, links, anchor, angle, where, th)
        out += heap(gap, th)
    for gap, shape, angle, where in RAIN:
        pos, links = RAIN_SHAPES[shape]
        out += fallen_piece(gap, pos, links, "a", angle, where, th)
    out.append(text(gap_x(0) - 62 - 20, FLOOR_Y + 22, "lost", TAG_SIZE, th["ink"], anchor="end"))
    # messages, back and forth: an envelope in flight over each gap, motion
    # lines behind it; no arrow (a solid arrow with a head is a read by address)
    for gap, d in MESSAGES:
        cx = gap_x(gap)
        out += motion_lines((cx - d * ENV_W / 2, ENV_Y), (d, 0), th, (40, 62, 34), 17,
                            what="message lines")
        out += envelope(cx, ENV_Y, th)
    return out


# =====================================================================================
# VERTICAL
# =====================================================================================
def vertical(th):
    out = caption("VERTICAL", (RIGHT[0] + RIGHT[1]) / 2, TITLE_BASE, th)
    all_nodes, all_edges = nodes(), edges()
    inside = ("now", 0)
    outer, box = outer_box(COL_X0, NOW_TOP), content_box(COL_X0, NOW_TOP)
    # what is written: on disk, outside the window
    for a, b in all_edges:
        if col_written(a) and col_written(b):
            out.append(edge(col_xy(a), col_xy(b), th, True))
    for n in all_nodes:
        if col_written(n):
            out.append(red_node(*col_xy(n), th, th["bg"]))
    # the spine runs on into the window: cut at the window's top, hidden by the
    # title bar, and on again from the top of the content.  The first part
    # starts at the last written disc's lower edge (R + 1.5: the disc and its
    # surface ring), not its centre: drawn after the disc, a dash from the
    # centre lay on it.
    p, q = col_xy(("s", WRITTEN - 1)), col_xy(("s", WRITTEN))
    out.append(edge((p[0], p[1] + R + 1.5), at(p, q, clip(p, q, outer)[0]), th, False, cut=True))
    out += window_body(COL_X0, NOW_TOP, th)
    out.append(edge(at(p, q, clip(p, q, box)[0]), q, th, False, inside, cut=True))
    for a, b in all_edges:
        if not col_written(a):                # both ends not yet written
            out.append(edge(col_xy(a), col_xy(b), th, False, inside))
    for n in all_nodes:
        if not col_written(n):
            out.append(green_node(*col_xy(n), th, th["content"], inside))
    # the node read back by its address: the tip of step 3's right branch, the
    # one that fell through the first gap in HORIZONTAL; its copy, in the
    # window, joined to the green work by a dashed green edge
    src = col_xy(("b", FELL[0], -1, 1))
    first = col_xy(("s", WRITTEN))
    copy = (first[0] + 60, first[1])
    # the join starts at step 12's ring's outer edge (R), not its centre: drawn
    # after the ring, a dash from the centre ran through its hole
    out.append(edge((first[0] + R, first[1]), copy, th, False, inside))
    out.append(red_node(*copy, th, th["content"], inside))
    out += window_chrome(COL_X0, NOW_TOP, th)
    out.append(ring(*src, th))
    out.append(ring(*copy, th))
    run_x = COL_X0 + WW + 84
    p = ((src[0] + R + 13, src[1]), (run_x + 40, src[1] + 40), (run_x + 40, copy[1] - 30), (copy[0], copy[1]))
    out += arrow(p, th, 8, 40, 22, stop=R + 15, what="by-address arrow")
    out.append(text(run_x + 22, (src[1] + copy[1]) / 2 + 150, "by address", TAG_SIZE, th["ink"],
                    anchor="start"))
    out.append(text(COL_SPINE_X + 2 * BRANCH_STEP + R + 30, col_spine_y(0) + 22, "on disk", TAG_SIZE,
                    th["ink"], anchor="start"))
    return out


# =====================================================================================
# The alt text: written to alt.txt (the README's <img alt>, through
# tools/assemble.mjs) and, the same text, into each SVG's <title> and <desc>.
ALT = ("Two panels. HORIZONTAL, many agents at once: four context windows stand side by side, "
       "each holding a piece of one task's graph, and every one is mid-work at the same moment: "
       "the first part of each piece is written, solid red dots on solid lines, and the rest is "
       "not yet written, dashed green rings on dashed lines. Envelopes fly back and forth between "
       "neighbouring windows, while pieces of the graph fall through the gaps between the windows "
       "into heaps marked lost. VERTICAL, one agent over time: the same graph, whole, runs down "
       "the page on disk into one context window at its end, and that window reads an early "
       "node back by its address: an arrow runs from the node to a copy of it inside the window.")


def build(theme):
    th = THEMES[theme]
    for store in (PLACED_TEXT, DRAWN_NODES, DRAWN_SEGMENTS, DRAWN_MARKS, WORDS):
        store.clear()
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-labelledby="t">',
           f'<title id="t">{esc(ALT)}</title>',
           f'<desc id="d">{esc(ALT)}</desc>',
           f'<rect width="{W}" height="{H}" rx="28" fill="{th["bg"]}"/>',
           f'<line x1="{DIVIDER_X}" y1="{M + 30}" x2="{DIVIDER_X}" y2="{H - M - 30}" '
           f'stroke="{th[SOFT]}" stroke-width="{DIVIDER_W}" stroke-linecap="round"/>']
    DRAWN_MARKS.append(("divider", (DIVIDER_X - DIVIDER_W, M + 30 - DIVIDER_W,
                                    DIVIDER_X + DIVIDER_W, H - M - 30 + DIVIDER_W)))
    out += horizontal(th)
    out += vertical(th)
    out.append("</svg>")
    return "\n".join(out) + "\n"


# =====================================================================================
# checks, before anything is written
# =====================================================================================
def touches_disc(cx, cy, r, box, margin):
    x0, y0, x1, y1 = box
    nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
    return math.dist((cx, cy), (nx, ny)) < r + margin


def overlap(a, b, margin):
    return not (a[2] + margin <= b[0] or b[2] + margin <= a[0] or a[3] + margin <= b[1] or b[3] + margin <= a[1])


def check_layout(margin=10):
    hits = []
    for s, box in PLACED_TEXT:
        if box[0] < M or box[2] > W - M or box[1] < M or box[3] > H - M:
            hits.append(f"label {s!r} box {tuple(round(v) for v in box)} leaves the canvas margin {M}")
        for cx, cy, r, _ in DRAWN_NODES:
            if touches_disc(cx, cy, r, box, margin):
                hits.append(f"label {s!r} touches the node at ({cx:.0f},{cy:.0f})")
        for what, mbox in DRAWN_MARKS:
            if overlap(box, mbox, margin):
                hits.append(f"label {s!r} touches a {what} near ({mbox[0]:.0f},{mbox[1]:.0f})")
        for _, k, x, y in WINDOWS:
            if overlap(box, outer_box(x, y), margin):
                hits.append(f"label {s!r} touches the window at ({x:.0f},{y:.0f})")
    return hits


def in_window(where):
    for panel, k, x, y in WINDOWS:
        if where == (panel, k):
            return x, y
    raise KeyError(where)


def check_frames():
    """Every node and every edge either inside one window's content, clear of
    its frame and title bar, or outside every window; an edge cut at a frame
    ends on it.  This replaces the renderer's clip."""
    hits = []
    half_frame = FRAME_W / 2
    for cx, cy, r, where in DRAWN_NODES:
        if where is OUT:
            for _, k, x, y in WINDOWS:
                x0, y0, x1, y1 = outer_box(x, y)
                if touches_disc(cx, cy, r, (x0 - half_frame, y0 - half_frame, x1 + half_frame, y1 + half_frame), 0):
                    hits.append(f"the node at ({cx:.0f},{cy:.0f}) outside the windows touches the window at ({x:.0f},{y:.0f})")
            continue
        x, y = in_window(where)
        x0, y0, x1, y1 = content_box(x, y)
        if not (x0 + half_frame <= cx - r and cx + r <= x1 - half_frame and
                y0 + BAR_LINE_W / 2 <= cy - r and cy + r <= y1 - half_frame):
            hits.append(f"the node at ({cx:.0f},{cy:.0f}) in window {where} crosses its frame or title bar")
        for ccx in (x0 + CORNER, x1 - CORNER):     # the rounded bottom corners
            ccy = y1 - CORNER
            if (cx - ccx) * (ccx - (x0 + x1) / 2) > 0 and cy > ccy and \
                    math.dist((cx, cy), (ccx, ccy)) + r > CORNER - half_frame:
                hits.append(f"the node at ({cx:.0f},{cy:.0f}) in window {where} crosses a rounded corner")
    for p, q, hw, where, cut in DRAWN_SEGMENTS:
        n = max(2, int(math.dist(p, q) / 2))
        pts = [at(p, q, i / n) for i in range(n + 1)]
        if where is OUT:
            for _, k, x, y in WINDOWS:
                x0, y0, x1, y1 = outer_box(x, y)
                inner = [pt for pt in pts if x0 < pt[0] < x1 and y0 < pt[1] < y1]
                if inner:
                    hits.append(f"the edge {tuple(round(v) for v in p)}-{tuple(round(v) for v in q)} outside "
                                f"the windows enters the window at ({x:.0f},{y:.0f})")
            continue
        x, y = in_window(where)
        x0, y0, x1, y1 = content_box(x, y)
        eps = 1e-6
        if not all(x0 - eps <= pt[0] <= x1 + eps and y0 - eps <= pt[1] <= y1 + eps for pt in pts):
            hits.append(f"the edge {tuple(round(v) for v in p)}-{tuple(round(v) for v in q)} in window "
                        f"{where} leaves its content")
        on_frame = [pt for pt in (p, q) if min(abs(pt[0] - x0), abs(pt[0] - x1), abs(pt[1] - y0)) < eps]
        if cut and not on_frame:
            hits.append(f"the cut edge {tuple(round(v) for v in p)}-{tuple(round(v) for v in q)} "
                        f"does not end on the frame of window {where}")
        for pt in on_frame:
            if pt[1] > y1 - CORNER:
                hits.append(f"the cut edge ends at ({pt[0]:.0f},{pt[1]:.0f}), on window {where}'s rounded corner")
    for what, (mx0, my0, mx1, my1) in DRAWN_MARKS:
        if what in ("motion lines", "message lines", "envelope"):
            for _, k, x, y in WINDOWS:
                if overlap((mx0, my0, mx1, my1), outer_box(x, y), 0):
                    hits.append(f"a {what} near ({mx0:.0f},{my0:.0f}) touches the window at ({x:.0f},{y:.0f})")
    return hits


def render(theme, svg, png):
    body = build(theme)
    hits = check_layout() + check_frames()
    if hits:
        sys.exit(f"draw.py: {len(hits)} layout collisions in the {theme} picture, nothing written:\n  "
                 + "\n  ".join(hits))
    svg.parent.mkdir(exist_ok=True)
    tmp = svg.with_name(svg.name + ".tmp")
    tmp.write_text(body)
    tmp.replace(svg)
    ptmp = png.with_name(png.name + ".tmp")
    subprocess.run(["rsvg-convert", "-w", str(W), "-o", str(ptmp), str(svg)], check=True)
    ptmp.replace(png)
    cuts = sum(1 for *_, cut in DRAWN_SEGMENTS if cut)
    print(f"{theme}: {png.name} ({W}x{H}); {len(PLACED_TEXT)} labels x {len(DRAWN_NODES)} nodes and "
          f"{len(DRAWN_MARKS)} marks: 0 collisions; {len(DRAWN_SEGMENTS)} edges, {cuts} cut at a frame, "
          f"0 crossing one")


def main():
    PNGS.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        render(theme, HERE / f"{NAME}-{theme}.svg", PNGS / f"{NAME}-{theme}.png")
    render("same-colour", CHECKS / "same-colour.svg", CHECKS / "same-colour.png")
    alt = HERE / "alt.txt"
    tmp = alt.with_name(alt.name + ".tmp")
    tmp.write_text(ALT + "\n")
    tmp.replace(alt)
    print("words: " + " ".join(WORDS))


if __name__ == "__main__":
    sys.exit(main())
