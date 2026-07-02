#!/usr/bin/env python3
"""
Urchin keymap -> SVG renderer.

Reads the physical layout (key positions + thumb rotation) and draws one layer
as an SVG that can be embedded in Markdown.

Usage:
    from render_keymap import render
    svg = render(labels)      # labels: list of 34 strings, matrix order
    open("layer.svg","w").write(svg)

Matrix order of `labels` (34 keys):
    row0: 0..9      (left 0-4, right 5-9)
    row1: 10..19
    row2: 20..29
    thumbs: 30,31 (left)  32,33 (right)

A label may contain "\\n" to render a two-line key (e.g. hold\\ntap).
"""
import math

# Physical layout from urchin.json (x,y in key units; thumbs carry rotation).
LAYOUT = [
    {"x": -2, "y": 0.75}, {"x": -1, "y": 0}, {"x": 0, "y": -0.25}, {"x": 1, "y": 0}, {"x": 2, "y": 0.25},
    {"x": 6, "y": 0.25}, {"x": 7, "y": 0}, {"x": 8, "y": -0.25}, {"x": 9, "y": 0}, {"x": 10, "y": 0.5},
    {"x": -2, "y": 1.75}, {"x": -1, "y": 1}, {"x": 0, "y": 0.75}, {"x": 1, "y": 1}, {"x": 2, "y": 1.25},
    {"x": 6, "y": 1.25}, {"x": 7, "y": 1}, {"x": 8, "y": 0.75}, {"x": 9, "y": 1}, {"x": 10, "y": 1.5},
    {"x": -2, "y": 2.75}, {"x": -1, "y": 2}, {"x": 0, "y": 1.75}, {"x": 1, "y": 2}, {"x": 2, "y": 2.25},
    {"x": 6, "y": 2.25}, {"x": 7, "y": 2}, {"x": 8, "y": 1.75}, {"x": 9, "y": 2}, {"x": 10, "y": 2.5},
    {"x": 0.5,  "y": 3.75, "r": 15,  "rx": 2.98, "ry": 8.395},
    {"x": 0.75, "y": 3.5,  "r": 30,  "rx": 1.73, "ry": 7.895},
    {"x": 7.75, "y": 4,    "r": -30, "rx": 6.48, "ry": 9.145},
    {"x": 7.5,  "y": 3.57, "r": -15, "rx": 6.73, "ry": 8.395},
]

U = 64          # px per key unit
GAP = 6         # gap between keys
PAD = 12        # outer margin
KEY = U - GAP
RAD = 7         # corner radius

# Theme (works on both light and dark READMEs)
KEY_FILL = "#825cf5"
KEY_STROKE = "#8d8d8d"
TEXT_FILL = "#ffffff"


def _rot(px, py, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def _corners(k):
    x0, y0 = k["x"] * U, k["y"] * U
    pts = [(x0, y0), (x0 + U, y0), (x0 + U, y0 + U), (x0, y0 + U)]
    if "r" in k:
        cx, cy = k["rx"] * U, k["ry"] * U
        pts = [_rot(px, py, cx, cy, k["r"]) for px, py in pts]
    return pts


def render(labels, key_fill=KEY_FILL, key_stroke=KEY_STROKE, text_fill=TEXT_FILL):
    assert len(labels) == len(LAYOUT), f"need {len(LAYOUT)} labels, got {len(labels)}"

    # bounds over all (possibly rotated) corners
    xs, ys = [], []
    for k in LAYOUT:
        for px, py in _corners(k):
            xs.append(px); ys.append(py)
    minx, miny, maxx, maxy = min(xs), min(ys), max(xs), max(ys)
    W = (maxx - minx) + 2 * PAD
    H = (maxy - miny) + 2 * PAD
    ox, oy = PAD - minx, PAD - miny

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
           f'width="{W:.0f}" font-family="ui-sans-serif,system-ui,sans-serif">']

    for k, label in zip(LAYOUT, labels):
        x, y = k["x"] * U + ox, k["y"] * U + oy
        g_open, g_close = "", ""
        if "r" in k:
            cx, cy = k["rx"] * U + ox, k["ry"] * U + oy
            g_open = f'<g transform="rotate({k["r"]} {cx:.2f} {cy:.2f})">'
            g_close = "</g>"
        rx_, ry_ = x + GAP / 2, y + GAP / 2
        cxx, cyy = x + U / 2, y + U / 2
        lines = label.split("\n")
        if len(lines) == 1:
            txt = (f'<text x="{cxx:.1f}" y="{cyy:.1f}" text-anchor="middle" '
                   f'dominant-baseline="central" font-size="16" font-weight="600" '
                   f'fill="{text_fill}">{esc(lines[0])}</text>')
        else:
            txt = (f'<text x="{cxx:.1f}" y="{cyy - 8:.1f}" text-anchor="middle" '
                   f'dominant-baseline="central" font-size="10" fill="{text_fill}" '
                   f'opacity="0.7">{esc(lines[0])}</text>'
                   f'<text x="{cxx:.1f}" y="{cyy + 8:.1f}" text-anchor="middle" '
                   f'dominant-baseline="central" font-size="15" font-weight="600" '
                   f'fill="{text_fill}">{esc(lines[1])}</text>')
        out.append(
            f'{g_open}<rect x="{rx_:.1f}" y="{ry_:.1f}" width="{KEY}" height="{KEY}" '
            f'rx="{RAD}" fill="{key_fill}" stroke="{key_stroke}" stroke-width="1.5"/>'
            f'{txt}{g_close}')

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    # idx = [str(i) for i in range(34)]
    # open("./assets/urchin-index.svg", "w").write(render(idx))

    base = [
        "Q","W","E","R","T", "Y","U","I","O","P",
        "A","S","D","F","G", "H","J","K","L",";",
        "Z","X","C","V","B", "B","N","M",",",".",
        "L2\n⌘","^","⇧\n␣","L3\nKo/En",
    ]
    open("./assets/urchin-base.svg", "w").write(render(base))

    game = [
        "ESC","Q","W","E","R", "3","4","5","6","7",
        "⇧","A","S","D","F", "2","K","⬆","L","⇧",
        "^","Z","X","C","V", "1","⬅","⬇","⮕","^",
        "L2","␣","J","L3",
    ]
    open("./assets/urchin-game.svg", "w").write(render(game))

    mod = [
        "ESC","⬅WS","F2","WS⮕","TAB", "🔅","↖","↘","🔆","⌫",
        "⌘","⌥","Auto Shift\n⇧","^","⌦", "⬅","⬇","⬆","⮕","⏎",
        "⇪","F3","F4","F5","⎙", "🔉","⤓","⤒","🔊","⌦",
        "","","","",
    ]
    open("./assets/urchin-mod.svg", "w").write(render(mod))

    symbol = [
        "*","1","2","3","+", "^","@","#","$","⌫",
        "/","4","5","6","-", "!","|","&","=","⏎",
        ".","7","8","9","`", "_","%","~","?","⌦",
        "0","","","",
    ]
    open("./assets/urchin-symbol.svg", "w").write(render(symbol))

    print("wrote urchin-base.svg, urchin-game.svg, urchin-mod.svg, urchin-symbol.svg")