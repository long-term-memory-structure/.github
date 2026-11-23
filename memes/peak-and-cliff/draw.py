#!/usr/bin/env python3
"""Our version of the Karpathy Peak, for memory: a meme for the long-term-memory-structure
profile README.

It sits after the paragraph that ends: "That is the shape Thomas Jiralerspong drew for
productivity with AI, a peak and then a cliff, in Chasing the Karpathy Peak (and Falling Off
Slop Cliff)."  His post relabels xkcd #323's Ballmer Peak: a smooth climb to "Karpathy Peak",
then "Slop Cliff".  This is our own drawing of that shape, in the series' look, with credit to
him inside the picture.

The chart: two plain axes, across the memory grows, up the useful work the agent gets done.
A memory kept IN THE WINDOW climbs to a sharp summit, KARPATHY PEAK (the wiki at moderate
scale), then drops straight down CONTEXT CLIFF (the window is full: no room left for the work)
and stays near the floor.  A memory kept ON DISK starts with it, passes under the peak, and
keeps climbing past the peak's height to the right edge: no cliff.  The disk's tag sits at its
line's end; the window's beside the mountain's climb, with a plain pointer (its line's end, on
the floor, is under the cliff's name, and the two would read as one block).

The two lines are told apart by style and by their tags, never by colour: both are the
theme's ink.  The window's line is the thinner one and is the outline of a mountain, filled
with a light wash; the disk's line is heavier and runs over a band of the background, so it
reads as passing in front of the mountain where they cross.  Red and green, the series'
"written" and "not yet written", do not appear: nothing here is a record or its future.  No
read by address is drawn, so there is no solid arrow with a head anywhere: the axes end in
open chevrons, and the peak's pointer is a plain line.

The series' look is meme 1's (memes/before-after/draw.py): its palette T, every key and value,
and its caption() lettering, unchanged, for the two names.  The one colour not in T is the
mountain's wash: T's ink mixed into T's background at WASH.  No window is drawn, so its chrome
does not appear.

Writes, beside this file (NAME = this folder's name): NAME-light.svg and NAME-dark.svg, each
rendered by rsvg-convert to a 2000-px-wide PNG of the same name in profile/memes/ (the README
shows them from there), and alt.txt, the alt text,
which is also each SVG's <title> and <desc>.  No randomness: every coordinate is computed from
the constants below and written at one decimal.  Needs rsvg-convert and the Fira Sans family
(SIL OFL): Fira Sans Condensed Heavy for the names, Fira Sans SemiBold for the tags, Fira Sans
Book Italic for the credit.

    python3 -I draw.py
"""
import os
import pathlib
import subprocess
import sys
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
NAME = HERE.name
PNGS = HERE.parent.parent / "profile" / "memes"   # the README shows the PNGs from there

ALT = ("A chart, our version of Thomas Jiralerspong's Karpathy Peak chart, redrawn for memory. "
       "Across, the memory grows; up, the useful work. A thinner line, tagged in the window, is "
       "the outline of a shaded mountain: a memory kept in the context window climbs to a sharp "
       "summit named KARPATHY PEAK, then drops straight down a sheer cliff named CONTEXT CLIFF to "
       "almost nothing, and stays there as the memory keeps growing. A heavier line, tagged on "
       "disk, starts with it, passes under the peak in front of the mountain, and keeps climbing "
       "to the top right, past the height of the peak, with no cliff. A small credit reads: after "
       "Thomas Jiralerspong's Karpathy Peak.")
CREDIT = "after Thomas Jiralerspong’s Karpathy Peak"

# meme 1's palette T, every key and value (unused here: its window keys, "titlebar", "content",
# "dot" and "title"'s window role, as no window is drawn; and "red" and "green", as nothing here
# is written or not yet written.  "title" colours the credit, a second text tone)
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
WASH = 0.14                 # the mountain's fill: this much of T's ink over T's background

# ---- canvas -----------------------------------------------------------------
W = 2000
M = 44                      # outer margin
TEXT = 64                   # every tag, axis label and the credit: 64 px on the 2000-px canvas
NAME_SIZE = 112             # the two names, in caption() lettering
X0, Y0 = 170, 1000          # the axes' corner
Y_TOP = 116                 # the up axis ends here, in an open chevron
X_RIGHT = 1912              # the across axis ends here, in an open chevron
BELOW = 84                  # the axis label and the credit: their baseline this far under the axis
H = Y0 + BELOW + 20 + M     # 20: room for the descenders (y, p, g)
AXIS = 8                    # the axes and their chevrons
CHEVRON = (30, 24)          # an open chevron: its depth along the axis, its half-width across it

# the data: u (the memory, 0..1) across, v (the useful work, 0..1) up
XD0, XD1 = X0 + 24, 1600    # where the two lines start and end
YD0, YD1 = Y0 - 10, 176     # v = 0 and v = 1
N = 240                     # samples along u

WINDOW_LINE = 12            # the window's line: the mountain's outline
DISK_LINE = 20              # the disk's line, heavier
CASING = 8                  # the band of background along each side of the disk's line
LEADER = 7                  # the two pointers (the peak's name, the window's tag): plain lines, no head
CLIFF_NAME_HALF = 377       # half of CONTEXT CLIFF's width at NAME_SIZE (753 px: the font's advance
                            # widths plus the letter-spacing), so its left edge stands 44 px right of the cliff

V_START = 0.06              # both lines start here
V_END = 0.93                # the disk's line ends here
SLOPE_START, SLOPE_END = 0.55, 0.85   # the disk's line: its slope (in u, v) at the start and the end
U_SPLIT = 0.10              # the window's line leaves the disk's here,
U_PEAK = 0.44               # and reaches its summit here,
LIFT = 0.19                 # this far above the disk's line,
BEND = 2.2                  # bending up ever more steeply (the power of the lift's rise)
V_FLOOR = 0.045             # under the cliff: almost nothing, to the right edge
U_TAG = 0.37                # the window's tag points at its line here,
TAG_REACH = 24              # its pointer stopping this far short of the line's centre


def fail(msg):
    sys.exit(f"draw.py: {msg}")


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def mix(a, b, t):
    """The colour t of the way from a to b (hex, sRGB values mixed as they are)."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


# ---- the two curves -----------------------------------------------------------
def hermite(u, s0, s1):
    """From (0, 0) to (1, 1), slope s0 at the start and s1 at the end."""
    return (s0 * (u ** 3 - 2 * u ** 2 + u) + (-2 * u ** 3 + 3 * u ** 2) + s1 * (u ** 3 - u ** 2))


def disk_v(u):
    return V_START + (V_END - V_START) * hermite(u, SLOPE_START, SLOPE_END)


def window_v(u):
    """The disk's line, plus a lift that starts flat at U_SPLIT and rises ever more steeply
    to LIFT at the summit."""
    if u <= U_SPLIT:
        return disk_v(u)
    return disk_v(u) + LIFT * ((u - U_SPLIT) / (U_PEAK - U_SPLIT)) ** BEND


def at(u, v):
    return (XD0 + u * (XD1 - XD0), YD0 - v * (YD0 - YD1))


def curves():
    us = [i / N for i in range(N + 1)]
    disk = [at(u, disk_v(u)) for u in us]
    climb = [at(u, window_v(u)) for u in us if u < U_PEAK] + [at(U_PEAK, window_v(U_PEAK))]
    summit = climb[-1]
    foot = at(U_PEAK, V_FLOOR)
    floor_end = at(1.0, V_FLOOR)
    window = climb + [foot, floor_end]
    return disk, window, summit, foot, floor_end


def disk_y_at(disk, x):
    """The disk's line's height at canvas x (linear between samples)."""
    for (xa, ya), (xb, yb) in zip(disk, disk[1:]):
        if xa <= x <= xb:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    fail(f"x={x:.1f} is outside the disk's line ({disk[0][0]:.1f}..{disk[-1][0]:.1f})")


# ---- drawing ----------------------------------------------------------------
def points(pts):
    return " ".join(f"{f(x)},{f(y)}" for x, y in pts)


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
            f'font-weight="600" font-size="{TEXT}" fill="{T["ink"]}">{escape(text)}</text>')


def credit(x, y, T):
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="start" font-family="Fira Sans" '
            f'font-weight="400" font-style="italic" font-size="{TEXT}" fill="{T["title"]}">{escape(CREDIT)}</text>')


def leader(x1, y1, x2, y2, T):
    """A label's pointer: a plain line, no head."""
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{T["ink"]}" '
            f'stroke-width="{LEADER}" stroke-linecap="round"/>')


def axes(T):
    """Two plain axes, each ending in an open chevron (two strokes, no fill)."""
    d, half = CHEVRON
    s = (f'fill="none" stroke="{T["frame"]}" stroke-width="{AXIS}" stroke-linecap="round" '
         f'stroke-linejoin="round"')
    return [f'<path d="M{X0} {Y_TOP} V{Y0} H{X_RIGHT}" {s}/>',
            f'<path d="M{X0 - half} {Y_TOP + d} L{X0} {Y_TOP} L{X0 + half} {Y_TOP + d}" {s}/>',
            f'<path d="M{X_RIGHT - d} {Y0 - half} L{X_RIGHT} {Y0} L{X_RIGHT - d} {Y0 + half}" {s}/>']


def build(theme):
    T = THEMES[theme]
    disk, window, summit, foot, floor_end = curves()

    # ---- guards: the shape says what it must ---------------------------------
    if any(b[1] >= a[1] for a, b in zip(disk, disk[1:])):
        fail("the disk's line must rise all the way (canvas y falling at every step)")
    tail = (disk[-1][1] - disk[-11][1]) / (disk[-1][0] - disk[-11][0])
    if tail > -0.25:
        fail(f"the disk's line flattens at the end (slope {-tail:.2f} up per px across); keep it climbing")
    if not disk[-1][1] < summit[1] - 120:
        fail(f"the disk's line must end well above the peak: it ends at y={disk[-1][1]:.1f}, the summit is at {summit[1]:.1f}")
    under = disk_y_at(disk, summit[0]) - summit[1]
    if under < 2 * (DISK_LINE / 2 + CASING) + WINDOW_LINE:
        fail(f"the summit stands only {under:.1f} px above the disk's line; raise LIFT")
    if min(y for _, y in disk + window) < Y_TOP + CHEVRON[0] or max(x for x, _ in disk + window) > X_RIGHT - 60:
        fail("a line leaves the plot")
    if foot[1] > Y0 - (AXIS / 2 + WINDOW_LINE / 2 + 20):
        fail(f"the floor (y={foot[1]:.1f}) must stay clear of the across axis (y={Y0})")

    wash = mix(T["bg"], T["ink"], WASH)
    body = []
    body += axes(T)
    # the mountain: its wash, then its outline (the window's line: climb, cliff, floor)
    area = [(XD0, Y0 - AXIS / 2)] + window + [(floor_end[0], Y0 - AXIS / 2)]
    body.append(f'<polygon points="{points(area)}" fill="{wash}"/>')
    body.append(f'<polyline points="{points(window)}" fill="none" stroke="{T["ink"]}" '
                f'stroke-width="{WINDOW_LINE}" stroke-linejoin="round" stroke-linecap="round"/>')
    # the disk's line, over a band of the background
    body.append(f'<polyline points="{points(disk)}" fill="none" stroke="{T["bg"]}" '
                f'stroke-width="{DISK_LINE + 2 * CASING}" stroke-linejoin="round" stroke-linecap="round"/>')
    body.append(f'<polyline points="{points(disk)}" fill="none" stroke="{T["ink"]}" '
                f'stroke-width="{DISK_LINE}" stroke-linejoin="round" stroke-linecap="round"/>')

    # the names, in caption() lettering
    px, py = summit
    body += caption("KARPATHY PEAK", px - 130, py - 122, T, size=NAME_SIZE)
    body.append(leader(px - 66, py - 96, px - 12, py - 22, T))
    cliff_mid = (summit[1] + foot[1]) / 2
    body += caption("CONTEXT CLIFF", px + 44 + CLIFF_NAME_HALF, cliff_mid + 76, T, size=NAME_SIZE)
    # the tags: the disk's at its line's right end; the window's beside the mountain's climb,
    # where it stands clear of the disk's line, with a plain pointer to it (as meme 1's "written —")
    end = disk[-1]
    body.append(label("on disk", end[0] + 32, end[1] + 22, T, anchor="start"))
    tx, ty = at(U_TAG, window_v(U_TAG))
    body.append(label("in the window", tx - 70, ty + 17, T, anchor="end"))
    body.append(leader(tx - 58, ty, tx - TAG_REACH, ty, T))
    # the axes' labels and the credit
    body.append(label("useful work", X0 + 46, Y_TOP + 42, T, anchor="start"))
    body.append(label("memory", X_RIGHT, Y0 + BELOW, T, anchor="end"))
    body.append(credit(X0 - 6, Y0 + BELOW, T))

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(ALT)}</title>',
           f'<desc id="desc">{escape(ALT)}</desc>',
           f'<rect width="{W}" height="{H}" rx="28" fill="{T["bg"]}"/>']
    out += body
    out.append("</svg>")
    info = dict(summit=(round(px, 1), round(py, 1)), summit_above_disk=round(under, 1),
                disk_end=(round(end[0], 1), round(end[1], 1)), floor=round(foot[1], 1), wash=wash, height=H)
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
