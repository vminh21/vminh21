"""Generate a snake animation SVG that eats text + a pixel mascot drawn on a contribution-style grid.

Usage: python3 scripts/generate_snake.py
Writes assets/snake-light.svg and assets/snake-dark.svg.
"""
import random
from pathlib import Path

TEXT = "CLAUDE"
COLS, ROWS = 60, 9
CELL, GAP = 11, 4
PITCH = CELL + GAP
PAD = 6
STEP = 0.055  # seconds per cell
SNAKE_LEN = 6
REST_STEPS = 40  # pause with full grid before snake enters
ICON_W = 120  # space on the left for the bouncing spark icon

FONT = {
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
}

# Builder critter: Y hat, H hat brim, O body, K eye, W smile,
# G wrench, S screwdriver shaft, P screwdriver handle.
MASCOT = [
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
MASCOT_COLORS = {
    "Y": "#f2cf4a",
    "H": "#d9ae2b",
    "O": "#d97757",
    "K": "#1f1e1d",
    "W": "#ffffff",
    "G": "#7d8b99",
    "S": "#a7b1bc",
    "P": "#5b3fd1",
}
PART = {"G": "wrench", "S": "driver", "P": "driver", "K": "eyes"}  # everything else: body

THEMES = {
    "light": {
        "empty": "#ebedf0",
        "levels": ["#f5cbb8", "#eba287", "#d97757", "#b4532f"],
        "snake": "#2b2a27",
        "spark": "#d97757",
    },
    "dark": {
        "empty": "#161b22",
        "levels": ["#5a2d1c", "#9c4a2e", "#d97757", "#f0a07f"],
        "snake": "#f5f0e8",
        "spark": "#d97757",
    },
}


def layout(t):
    """Return {part: {(x, y): color}} for text and mascot cells inside the grid."""
    text_w = len(TEXT) * 6 - 1
    m_w = len(MASCOT[0])
    x0 = (COLS - (text_w + 3 + m_w)) // 2
    y0 = (ROWS - 7) // 2
    rng = random.Random(21)
    parts = {"txt": {}, "body": {}, "eyes": {}, "wrench": {}, "driver": {}}
    for i, ch in enumerate(TEXT):
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    parts["txt"][(x0 + i * 6 + c, y0 + r)] = t["levels"][rng.randint(1, 3)]
    mx0, my0 = x0 + text_w + 3, ROWS - len(MASCOT)
    for r, row in enumerate(MASCOT):
        for c, v in enumerate(row):
            if v != ".":
                parts[PART.get(v, "body")][(mx0 + c, my0 + r)] = MASCOT_COLORS[v]
    return parts


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
    rays = "".join(
        f'<rect x="-3.5" y="{-L}" width="7" height="{L}" rx="3.5" '
        f'transform="rotate({i * 360 / len(lengths)})" fill="{t["spark"]}"/>'
        for i, L in enumerate(lengths)
    )
    return (
        f'<g transform="translate({cx},{cy})"><g class="bounce"><g class="squash">'
        f'<g class="spin">{rays}<circle r="9" fill="{t["spark"]}"/></g></g></g></g>'
    )


CSS_ANIM = (
    # spark
    "@keyframes bounce{0%,100%{transform:translateY(8px)}45%,55%{transform:translateY(-10px)}}"
    ".bounce{animation:bounce 1.1s cubic-bezier(.45,0,.55,1) infinite}"
    "@keyframes squash{0%,100%{transform:scale(1.12,.86)}15%,85%{transform:scale(.95,1.06)}50%{transform:scale(1)}}"
    ".squash{animation:squash 1.1s ease-in-out infinite}"
    "@keyframes spin{to{transform:rotate(360deg)}}"
    ".spin{animation:spin 9s linear infinite}"
    # text
    "@keyframes blink{0%,100%{opacity:1}50%{opacity:.45}}"
    ".txt{animation:blink 1.6s ease-in-out infinite}"
    # mascot: bob, tool wiggle, eye blink
    "@keyframes bob{0%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}"
    "50%{transform:translateY(0)}62%{transform:translateY(-2px)}74%{transform:translateY(0)}}"
    ".mascot{animation:bob 1.2s ease-in-out infinite}"
    "@keyframes wrench{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(14deg)}}"
    ".wrench{transform-box:fill-box;transform-origin:50% 100%;animation:wrench .6s ease-in-out infinite}"
    "@keyframes driver{0%,100%{transform:rotate(12deg)}50%{transform:rotate(-12deg)}}"
    ".driver{transform-box:fill-box;transform-origin:50% 100%;animation:driver .6s ease-in-out infinite .3s}"
    "@keyframes lid{0%,92%,100%{opacity:0}95%{opacity:1}}"
    ".lid{animation:lid 3s infinite}"
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
    w = ICON_W + gw + 12
    cx = lambda x: PAD + x * PITCH
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
        out = []
        for pos, color in sorted(cells_dict.items()):
            name = eat_anim(pos)
            out.append(f'<rect class="c" id="{name}" x="{cx(pos[0])}" y="{cx(pos[1])}" fill="{color}"/>')
        return "".join(out)

    body.append(f'<clipPath id="gc"><rect width="{gw}" height="{h}"/></clipPath>')
    body.append(f'<g transform="translate({ICON_W},0)" clip-path="url(#gc)">')
    body.append(
        "".join(
            f'<rect class="c" x="{cx(x)}" y="{cx(y)}" fill="{t["empty"]}"/>'
            for y in range(ROWS)
            for x in range(COLS)
        )
    )
    body.append(f'<g class="txt">{cells(parts["txt"])}</g>')

    # mascot: eyelids are body-colored cells over the eyes that flash briefly; hidden once eaten
    lids = []
    for pos in sorted(parts["eyes"]):
        gone = eat_anim(pos, "o")
        lids.append(
            f'<g id="{gone}"><rect class="c lid" x="{cx(pos[0])}" y="{cx(pos[1])}" '
            f'fill="{MASCOT_COLORS["O"]}"/></g>'
        )
    body.append(
        '<g class="mascot">'
        f'{cells(parts["body"])}{cells(parts["eyes"])}{"".join(lids)}'
        f'<g class="wrench">{cells(parts["wrench"])}</g>'
        f'<g class="driver">{cells(parts["driver"])}</g>'
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
    body.append(spark_svg(t, h))

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
