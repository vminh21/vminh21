"""Generate a snake animation SVG that eats two pixel mascots and a word on a contribution-style grid.

Usage: python3 scripts/generate_snake.py
Writes assets/snake-light.svg and assets/snake-dark.svg.
"""
import random
from pathlib import Path

TEXT = "CLAUDE"
COLS, ROWS = 76, 9
CELL, GAP = 11, 4
PITCH = CELL + GAP
PAD = 6
MARGIN = 12
STEP = 0.05  # seconds per cell
SNAKE_LEN = 6
REST_STEPS = 50  # pause with full grid before snake enters
SPACING = 3  # empty columns between the three pieces

# Bold font: 2-cell-thick vertical strokes.
FONT = {
    "C": [".XXXX", "XX...", "XX...", "XX...", "XX...", "XX...", ".XXXX"],
    "L": ["XX...", "XX...", "XX...", "XX...", "XX...", "XXXXX", "XXXXX"],
    "A": [".XXX.", "XX.XX", "XX.XX", "XXXXX", "XX.XX", "XX.XX", "XX.XX"],
    "U": ["XX.XX", "XX.XX", "XX.XX", "XX.XX", "XX.XX", "XX.XX", ".XXX."],
    "D": ["XXXX.", "XX.XX", "XX.XX", "XX.XX", "XX.XX", "XX.XX", "XXXX."],
    "E": ["XXXXX", "XX...", "XX...", "XXXX.", "XX...", "XX...", "XXXXX"],
}

ORANGE = "#d97757"
DARK = "#1f1e1d"

# Left: startup critter. O body, K eye, A/B arms, L/R legs.
CRITTER = [
    "..OOOOOOOOOO..",
    "..OKOOOOOOKO..",
    "..OKOOOOOOKO..",
    "AAOOOOOOOOOOBB",
    "AAOOOOOOOOOOBB",
    "..OOOOOOOOOO..",
    "..L.L....R.R..",
]
CRITTER_PART = {"K": "c_eyes", "A": "c_larm", "B": "c_rarm", "L": "c_lleg", "R": "c_rleg"}

# Right: builder critter. Y hat, H brim, O body, K eye, W smile, G wrench, S/P screwdriver.
BUILDER = [
    "......YYY........",
    ".....YYYYY.....S.",
    "G.G.HHHHHHHHH..S.",
    "GGG.OOOOOOOOO..S.",
    ".G..OOKOOOKOO.PPP",
    ".G..OOOWWWOOO..P.",
    ".GOOOOOOOOOOOOOP.",
    ".G..OOOOOOOOO.PPP",
    "....O.O...O.O....",
]
BUILDER_PART = {"G": "b_wrench", "S": "b_driver", "P": "b_driver", "K": "b_eyes"}

COLORS = {
    "O": ORANGE, "A": ORANGE, "B": ORANGE, "L": ORANGE, "R": ORANGE, "K": DARK,
    "Y": "#f2cf4a", "H": "#d9ae2b", "W": "#ffffff", "G": "#7d8b99", "S": "#a7b1bc", "P": "#5b3fd1",
}

THEMES = {
    "light": {
        "empty": "#ebedf0",
        "levels": ["#f5cbb8", "#eba287", "#d97757", "#b4532f"],
        "snake": "#2b2a27",
    },
    "dark": {
        "empty": "#161b22",
        "levels": ["#5a2d1c", "#9c4a2e", "#d97757", "#f0a07f"],
        "snake": "#f5f0e8",
    },
}


def place(grid, x0, y0, part_map, default, parts):
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v != ".":
                parts.setdefault(part_map.get(v, default), {})[(x0 + c, y0 + r)] = COLORS[v]


def layout(t):
    """Return {part: {(x, y): color}} for every drawn cell inside the grid."""
    text_w = len(TEXT) * 6 - 1
    c_w, b_w = len(CRITTER[0]), len(BUILDER[0])
    x = (COLS - (c_w + SPACING + text_w + SPACING + b_w)) // 2
    parts = {}

    place(CRITTER, x, ROWS - len(CRITTER), CRITTER_PART, "c_body", parts)
    x += c_w + SPACING

    rng = random.Random(21)
    y0 = (ROWS - 7) // 2
    for i, ch in enumerate(TEXT):
        for r, row in enumerate(FONT[ch]):
            for c, v in enumerate(row):
                if v == "X":
                    parts.setdefault("txt", {})[(x + i * 6 + c, y0 + r)] = t["levels"][rng.randint(2, 3)]
    x += text_w + SPACING

    place(BUILDER, x, ROWS - len(BUILDER), BUILDER_PART, "b_body", parts)
    return parts


def snake_path():
    path = [(-k, 0) for k in range(SNAKE_LEN, 0, -1)]  # enter from the left
    for x in range(COLS):
        rows = range(ROWS) if x % 2 == 0 else range(ROWS - 1, -1, -1)
        path += [(x, y) for y in rows]
    last_y = path[-1][1]
    path += [(COLS + k, last_y) for k in range(SNAKE_LEN + 1)]  # exit right
    return path


CSS_ANIM = (
    # text: a bright wave sweeping left to right
    "@keyframes wave{0%,100%{opacity:1;transform:translateY(0)}"
    "10%{opacity:.35;transform:translateY(-3px)}20%{opacity:1;transform:translateY(0)}}"
    ".wv{animation:wave 2.4s ease-in-out infinite}"
    # left critter: bob, waving arms, stepping legs
    "@keyframes cbob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
    ".critter{animation:cbob 1s ease-in-out infinite}"
    "@keyframes arm{0%,100%{transform:translateY(0)}25%{transform:translateY(-6px)}50%{transform:translateY(0)}}"
    ".c_larm{animation:arm 1.2s ease-in-out infinite}"
    ".c_rarm{animation:arm 1.2s ease-in-out infinite .6s}"
    "@keyframes step{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
    ".c_lleg{animation:step .5s ease-in-out infinite}"
    ".c_rleg{animation:step .5s ease-in-out infinite .25s}"
    # right builder: hop, tool wiggle
    "@keyframes bbob{0%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}"
    "50%{transform:translateY(0)}62%{transform:translateY(-2px)}74%{transform:translateY(0)}}"
    ".builder{animation:bbob 1.2s ease-in-out infinite}"
    "@keyframes wrench{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(14deg)}}"
    ".b_wrench{transform-box:fill-box;transform-origin:50% 100%;animation:wrench .6s ease-in-out infinite}"
    "@keyframes driver{0%,100%{transform:rotate(12deg)}50%{transform:rotate(-12deg)}}"
    ".b_driver{transform-box:fill-box;transform-origin:50% 100%;animation:driver .6s ease-in-out infinite .3s}"
    # eye blink (eyelids)
    "@keyframes lid{0%,90%,100%{opacity:0}93%,96%{opacity:1}}"
    ".lid{animation:lid 3s infinite}.lid2{animation:lid 3s infinite 1.4s}"
)


def render(theme):
    t = THEMES[theme]
    parts = layout(t)
    path = snake_path()
    total_steps = len(path) + REST_STEPS
    dur = total_steps * STEP
    pct = lambda step: 100 * (step + REST_STEPS) / total_steps
    eaten_at = {pos: i for i, pos in enumerate(path)}

    gw = COLS * PITCH - GAP + 2 * PAD
    h = ROWS * PITCH - GAP + 2 * PAD
    w = gw + 2 * MARGIN
    cx = lambda v: PAD + v * PITCH
    css = [f"rect.c{{width:{CELL}px;height:{CELL}px;rx:2px;ry:2px}}", CSS_ANIM]
    body = []

    def eat_anim(pos, suffix=""):
        """Keyframes that hide an element the moment the snake head reaches pos."""
        a = pct(eaten_at[pos])
        name = f"e{pos[0]}_{pos[1]}{suffix}"
        css.append(
            f"@keyframes {name}{{0%,{a:.3f}%{{opacity:1}}{min(a + 0.01, 100):.3f}%,100%{{opacity:0}}}}"
            f"#{name}{{animation:{name} {dur:.2f}s linear infinite}}"
        )
        return name

    def cells(cells_dict):
        return "".join(
            f'<rect class="c" id="{eat_anim(pos)}" x="{cx(pos[0])}" y="{cx(pos[1])}" fill="{color}"/>'
            for pos, color in sorted(cells_dict.items())
        )

    def lids(eyes, cls):
        return "".join(
            f'<g id="{eat_anim(pos, "o")}"><rect class="c {cls}" x="{cx(pos[0])}" y="{cx(pos[1])}" '
            f'fill="{ORANGE}"/></g>'
            for pos in sorted(eyes)
        )

    body.append(f'<clipPath id="gc"><rect y="-30" width="{gw}" height="{h + 30}"/></clipPath>')
    body.append(f'<g transform="translate({MARGIN},0)" clip-path="url(#gc)">')
    body.append(
        "".join(
            f'<rect class="c" x="{cx(x)}" y="{cx(y)}" fill="{t["empty"]}"/>'
            for y in range(ROWS)
            for x in range(COLS)
        )
    )

    # text, grouped by column so the wave can sweep across
    cols = sorted({x for x, _ in parts["txt"]})
    x_min = cols[0]
    for x in cols:
        col_cells = {p: c for p, c in parts["txt"].items() if p[0] == x}
        body.append(f'<g class="wv" style="animation-delay:{(x - x_min) * 0.04:.2f}s">{cells(col_cells)}</g>')

    body.append(
        '<g class="critter">'
        f'{cells(parts["c_body"])}{cells(parts["c_eyes"])}{lids(parts["c_eyes"], "lid")}'
        + "".join(f'<g class="{p}">{cells(parts[p])}</g>' for p in ("c_larm", "c_rarm", "c_lleg", "c_rleg"))
        + "</g>"
    )
    body.append(
        '<g class="builder">'
        f'{cells(parts["b_body"])}{cells(parts["b_eyes"])}{lids(parts["b_eyes"], "lid2")}'
        f'<g class="b_wrench">{cells(parts["b_wrench"])}</g>'
        f'<g class="b_driver">{cells(parts["b_driver"])}</g>'
        "</g>"
    )

    for seg in range(SNAKE_LEN):
        frames = [f"0%{{transform:translate({path[0][0] * PITCH}px,{path[0][1] * PITCH}px)}}"]
        for i in range(len(path)):
            px, py = path[max(i - seg, 0)]
            frames.append(f"{pct(i):.3f}%{{transform:translate({px * PITCH}px,{py * PITCH}px)}}")
        css.append(f"@keyframes s{seg}{{{''.join(frames)}}}#s{seg}{{animation:s{seg} {dur:.2f}s linear infinite}}")
        size = CELL - seg * 1.1
        off = PAD + (CELL - size) / 2
        body.append(
            f'<rect id="s{seg}" x="{off:.1f}" y="{off:.1f}" width="{size:.1f}" height="{size:.1f}" '
            f'rx="{min(3.5, size / 2):.1f}" fill="{t["snake"]}" opacity="{1 - seg * 0.12:.2f}"/>'
        )
    body.append("</g>")

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f"<style>{''.join(css)}</style>{''.join(body)}</svg>\n"
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        (out / f"snake-{theme}.svg").write_text(render(theme))
        print(f"wrote {out / f'snake-{theme}.svg'}")
