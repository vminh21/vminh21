"""Generate a snake animation SVG that eats a name drawn on a contribution-style grid.

Usage: python3 scripts/generate_snake.py
Writes assets/snake-light.svg and assets/snake-dark.svg.
"""
import random
from pathlib import Path

TEXT = "VMINH21"
COLS, ROWS = 53, 7
CELL, GAP = 11, 4
PITCH = CELL + GAP
PAD = 6
STEP = 0.07  # seconds per cell
SNAKE_LEN = 5
REST_STEPS = 25  # pause with full grid before snake enters

FONT = {
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
}

THEMES = {
    "light": {
        "empty": "#ebedf0",
        "levels": ["#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "snake": "#8250df",
    },
    "dark": {
        "empty": "#161b22",
        "levels": ["#0e4429", "#006d32", "#26a641", "#39d353"],
        "snake": "#a371f7",
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


def render(theme):
    t = THEMES[theme]
    food = food_cells()
    path = snake_path()
    total_steps = len(path) + REST_STEPS
    dur = total_steps * STEP
    pct = lambda step: 100 * (step + REST_STEPS) / total_steps

    w = COLS * PITCH - GAP + 2 * PAD
    h = ROWS * PITCH - GAP + 2 * PAD
    css, body = [], []
    css.append(f"rect.c{{width:{CELL}px;height:{CELL}px;rx:2px;ry:2px}}")

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

    for y in range(ROWS):
        for x in range(COLS):
            fill = t["empty"]
            attrs = ""
            if (x, y) in food:
                fill = t["levels"][food[(x, y)]]
                attrs = f' id="f{x}_{y}"'
            body.append(
                f'<rect class="c"{attrs} x="{PAD + x * PITCH}" y="{PAD + y * PITCH}" fill="{fill}"/>'
            )

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
