"""Generate a snake animation SVG that eats text + a pixel mascot drawn on a contribution-style grid.

Usage: python3 scripts/generate_snake.py
Writes assets/snake-light.svg and assets/snake-dark.svg.
"""
import random
from pathlib import Path

TEXT = "CLAUDE"
COLS, ROWS = 58, 7
CELL, GAP = 11, 4
PITCH = CELL + GAP
PAD = 6
MARGIN = 12
STEP = 0.06  # seconds per cell
SNAKE_LEN = 5
REST_STEPS = 40  # pause with full grid before snake enters

FONT = {
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
}

# Pixel critter: O body, K eye, A left arm, B right arm, L left legs, R right legs.
MASCOT = [
    "..OOOOOOOOOO..",
    "..OKOOOOOOKO..",
    "..OKOOOOOOKO..",
    "AAOOOOOOOOOOBB",
    "AAOOOOOOOOOOBB",
    "..OOOOOOOOOO..",
    "..L.L....R.R..",
]
BODY_COLOR = "#d97757"
EYE_COLOR = "#1f1e1d"
PART = {"K": "eyes", "A": "larm", "B": "rarm", "L": "lleg", "R": "rleg"}  # else: body

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


def layout(t):
    """Return {part: {(x, y): color}} for text and mascot cells inside the grid."""
    text_w = len(TEXT) * 6 - 1
    m_w = len(MASCOT[0])
    rng = random.Random(21)
    parts = {"txt": {}, "body": {}, "eyes": {}, "larm": {}, "rarm": {}, "lleg": {}, "rleg": {}}

    x0 = (COLS - (text_w + 4 + m_w)) // 2
    for i, ch in enumerate(TEXT):
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    parts["txt"][(x0 + i * 6 + c, r)] = t["levels"][rng.randint(1, 3)]

    mx0, my0 = x0 + text_w + 4, ROWS - len(MASCOT)
    for r, row in enumerate(MASCOT):
        for c, v in enumerate(row):
            if v != ".":
                color = EYE_COLOR if v == "K" else BODY_COLOR
                parts[PART.get(v, "body")][(mx0 + c, my0 + r)] = color
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
    # text
    "@keyframes blink{0%,100%{opacity:1}50%{opacity:.45}}"
    ".txt{animation:blink 1.6s ease-in-out infinite}"
    # mascot idle loop: bob, waving arms, stepping legs, blinking eyes
    "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
    ".mascot{animation:bob 1s ease-in-out infinite}"
    "@keyframes larm{0%,100%{transform:translateY(0)}25%{transform:translateY(-6px)}50%{transform:translateY(0)}}"
    ".larm{animation:larm 1.2s ease-in-out infinite}"
    ".rarm{animation:larm 1.2s ease-in-out infinite .6s}"
    "@keyframes step{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
    ".lleg{animation:step .5s ease-in-out infinite}"
    ".rleg{animation:step .5s ease-in-out infinite .25s}"
    "@keyframes lid{0%,90%,100%{opacity:0}93%,96%{opacity:1}}"
    ".lid{animation:lid 3s infinite}"
    # clicking the mascot when the SVG is opened directly: big jump
    "@keyframes jump{0%{transform:translateY(0)}40%{transform:translateY(-20px) rotate(-6deg)}"
    "80%{transform:translateY(0) rotate(4deg)}100%{transform:translateY(0)}}"
    ".hit{cursor:pointer}.hit:active .mascot{animation:jump .45s ease-out infinite}"
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

    body.append(f'<clipPath id="gc"><rect y="-30" width="{gw}" height="{h + 30}"/></clipPath>')
    body.append(f'<g transform="translate({MARGIN},0)" clip-path="url(#gc)">')
    body.append(
        "".join(
            f'<rect class="c" x="{cx(x)}" y="{cx(y)}" fill="{t["empty"]}"/>'
            for y in range(ROWS)
            for x in range(COLS)
        )
    )
    body.append(f'<g class="txt">{cells(parts["txt"])}</g>')

    # eyelids: body-colored cells over the eyes that flash briefly; hidden once eaten
    lids = "".join(
        f'<g id="{eat_anim(pos, "o")}"><rect class="c lid" x="{cx(pos[0])}" y="{cx(pos[1])}" '
        f'fill="{BODY_COLOR}"/></g>'
        for pos in sorted(parts["eyes"])
    )
    body.append(
        '<g class="hit"><g class="mascot">'
        f'{cells(parts["body"])}{cells(parts["eyes"])}{lids}'
        + "".join(f'<g class="{p}">{cells(parts[p])}</g>' for p in ("larm", "rarm", "lleg", "rleg"))
        + "</g></g>"
    )

    for seg in range(SNAKE_LEN):
        frames = [f"0%{{transform:translate({path[0][0] * PITCH}px,{path[0][1] * PITCH}px)}}"]
        for i in range(len(path)):
            px, py = path[max(i - seg, 0)]
            frames.append(f"{pct(i):.3f}%{{transform:translate({px * PITCH}px,{py * PITCH}px)}}")
        css.append(f"@keyframes s{seg}{{{''.join(frames)}}}#s{seg}{{animation:s{seg} {dur:.2f}s linear infinite}}")
        size = CELL - seg * 1.2
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
