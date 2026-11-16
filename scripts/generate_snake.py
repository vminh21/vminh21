"""Generate a snake animation SVG that eats a name drawn on a contribution-style grid.

Usage: python3 scripts/generate_snake.py
Writes assets/snake-light.svg and assets/snake-dark.svg.
"""
import random
from pathlib import Path

TEXT = "CLAUDE"
COLS, ROWS = 53, 7
CELL, GAP = 11, 4
PITCH = CELL + GAP
PAD = 6
STEP = 0.07  # seconds per cell
SNAKE_LEN = 5
REST_STEPS = 25  # pause with full grid before snake enters
ICON_W = 120  # space on the left for the bouncing spark icon
CRITTER_W = 120  # space on the right for the pixel critter

FONT = {
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
}

THEMES = {
    "light": {
        "empty": "#ebedf0",
        "levels": ["#f5cbb8", "#eba287", "#d97757", "#b4532f"],
        "snake": "#2b2a27",
        "spark": "#d97757",
        "eye": "#1f1e1d",
        "shadow": "#1f1e1d",
    },
    "dark": {
        "empty": "#161b22",
        "levels": ["#5a2d1c", "#9c4a2e", "#d97757", "#f0a07f"],
        "snake": "#f5f0e8",
        "spark": "#d97757",
        "eye": "#0d1117",
        "shadow": "#e6edf3",
    },
}


def food_cells():
    width = len(TEXT) * 6 - 1
    x0 = (COLS - width) // 2
    rng = random.Random(21)
    food = {}
    for i, ch in enumerate(TEXT):
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    food[(x0 + i * 6 + c, r)] = rng.randint(1, 3)
    return food


def snake_path():
    path = [(-k, 0) for k in range(SNAKE_LEN, 0, -1)]  # enter from the left
    for x in range(COLS):
        rows = range(ROWS) if x % 2 == 0 else range(ROWS - 1, -1, -1)
        path += [(x, y) for y in rows]
    last_y = path[-1][1]
    path += [(COLS + k, last_y) for k in range(SNAKE_LEN + 1)]  # exit right
    return path


def spark_svg(t, h):
    """Original orange starburst icon (not the official logo)."""
    cx, cy = ICON_W / 2 - 4, h / 2
    lengths = [34, 26, 31, 24, 35, 27, 30, 25, 33, 28, 32, 26]
    rays = []
    for i, L in enumerate(lengths):
        ang = i * 360 / len(lengths)
        rays.append(
            f'<rect x="{-3.5}" y="{-L}" width="7" height="{L}" rx="3.5" '
            f'transform="rotate({ang})" fill="{t["spark"]}"/>'
        )
    return (
        f'<g transform="translate({cx},{cy})"><g class="bounce"><g class="squash">'
        f'<g class="spin">{"".join(rays)}<circle r="9" fill="{t["spark"]}"/></g>'
        f"</g></g></g>"
    )


def spark_css():
    return (
        "@keyframes bounce{0%,100%{transform:translateY(8px)}"
        "45%{transform:translateY(-10px)}55%{transform:translateY(-10px)}}"
        ".bounce{animation:bounce 1.1s cubic-bezier(.45,0,.55,1) infinite}"
        "@keyframes squash{0%,100%{transform:scale(1.12,.86)}"
        "15%,85%{transform:scale(.95,1.06)}50%{transform:scale(1,1)}}"
        ".squash{animation:squash 1.1s ease-in-out infinite}"
        "@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}"
        ".spin{animation:spin 9s linear infinite}"
    )


CRITTER = [
    "..XXXXXXX..",
    "..XEXXXEX..",
    "XXXXXXXXXXX",
    "XXXXXXXXXXX",
    "..XXXXXXX..",
    "..X.X.X.X..",
]


def critter_svg(t, x0, h):
    """Small original pixel critter that hops and blinks."""
    px = 8
    cw, ch = len(CRITTER[0]) * px, len(CRITTER) * px
    ox = x0 + (CRITTER_W - cw) / 2 + 2
    oy = (h - ch) / 2 + 6
    body, eyes = [], []
    for r, row in enumerate(CRITTER):
        for c, v in enumerate(row):
            if v == ".":
                continue
            rect = f'<rect x="{c * px}" y="{r * px}" width="{px}" height="{px}"'
            if v == "E":
                eyes.append(rect + f' fill="{t["eye"]}"/>')
            else:
                body.append(rect + f' fill="{t["spark"]}"/>')
    shadow = (
        f'<ellipse class="shadow" cx="{ox + cw / 2}" cy="{oy + ch + 7}" rx="{cw / 2.4}" ry="3" '
        f'fill="{t["shadow"]}" opacity=".18"/>'
    )
    return (
        shadow
        + f'<g transform="translate({ox},{oy})"><g class="hop">'
        + "".join(body)
        + f'<g class="eyes">{"".join(eyes)}</g></g></g>'
    )


def critter_css():
    return (
        "@keyframes hop{0%,40%,100%{transform:translateY(0)}"
        "55%{transform:translateY(-16px)}70%{transform:translateY(0)}"
        "78%{transform:translateY(-5px)}86%{transform:translateY(0)}}"
        ".hop{animation:hop 1.8s ease-in-out infinite}"
        "@keyframes eyes{0%,90%,100%{transform:scaleY(1)}94%{transform:scaleY(.15)}}"
        ".eyes{transform-box:fill-box;transform-origin:center;animation:eyes 3.2s infinite}"
        "@keyframes shadow{0%,40%,70%,86%,100%{transform:scaleX(1);opacity:.18}"
        "55%{transform:scaleX(.6);opacity:.08}}"
        ".shadow{transform-box:fill-box;transform-origin:center;animation:shadow 1.8s ease-in-out infinite}"
    )


def render(theme):
    t = THEMES[theme]
    food = food_cells()
    path = snake_path()
    total_steps = len(path) + REST_STEPS
    dur = total_steps * STEP
    pct = lambda step: 100 * (step + REST_STEPS) / total_steps

    gw = COLS * PITCH - GAP + 2 * PAD
    h = ROWS * PITCH - GAP + 2 * PAD
    w = ICON_W + gw + CRITTER_W
    css, body = [], []
    css.append(f"rect.c{{width:{CELL}px;height:{CELL}px;rx:2px;ry:2px}}")
    css.append(
        "@keyframes blink{0%,100%{opacity:1}50%{opacity:.45}}"
        ".txt{animation:blink 1.6s ease-in-out infinite}"
    )

    eaten_at = {pos: i for i, pos in enumerate(path)}
    for (x, y), lvl in sorted(food.items()):
        k = eaten_at[(x, y)]
        name = f"f{x}_{y}"
        col = t["levels"][lvl]
        a = pct(k)
        css.append(
            f"@keyframes {name}{{0%,{a:.3f}%{{fill:{col}}}"
            f"{min(a + 0.01, 100):.3f}%,100%{{fill:{t['empty']}}}}}"
            f"#{name}{{animation:{name} {dur:.2f}s linear infinite}}"
        )

    body.append(f'<clipPath id="gc"><rect width="{gw}" height="{h}"/></clipPath>')
    body.append(f'<g transform="translate({ICON_W},0)" clip-path="url(#gc)">')
    for y in range(ROWS):
        for x in range(COLS):
            body.append(
                f'<rect class="c" x="{PAD + x * PITCH}" y="{PAD + y * PITCH}" fill="{t["empty"]}"/>'
            )
    body.append('<g class="txt">')
    for (x, y), lvl in sorted(food.items()):
        body.append(
            f'<rect class="c" id="f{x}_{y}" x="{PAD + x * PITCH}" y="{PAD + y * PITCH}" '
            f'fill="{t["levels"][lvl]}"/>'
        )
    body.append("</g>")

    for seg in range(SNAKE_LEN):
        frames = []
        start = path[0]
        frames.append(f"0%{{transform:translate({start[0] * PITCH}px,{start[1] * PITCH}px)}}")
        for i in range(len(path)):
            px, py = path[max(i - seg, 0)]
            frames.append(f"{pct(i):.3f}%{{transform:translate({px * PITCH}px,{py * PITCH}px)}}")
        css.append(f"@keyframes s{seg}{{{''.join(frames)}}}")
        size = CELL - seg * 1.2
        off = PAD + (CELL - size) / 2
        css.append(f"#s{seg}{{animation:s{seg} {dur:.2f}s linear infinite}}")
        body.append(
            f'<rect id="s{seg}" x="{off:.1f}" y="{off:.1f}" width="{size:.1f}" height="{size:.1f}" '
            f'rx="{min(3.5, size / 2):.1f}" fill="{t["snake"]}" opacity="{1 - seg * 0.12:.2f}"/>'
        )

    body.append("</g>")
    css.append(spark_css())
    body.append(spark_svg(t, h))
    css.append(critter_css())
    body.append(critter_svg(t, ICON_W + gw, h))

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
