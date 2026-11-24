#!/usr/bin/env python3
"""The World in One Day — newspaper front page for Tuesday 24 November 2026.

Draws a 1024x1024 newspaper front page summing up the real world news of
24 November 2026 and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Everything is drawn procedurally with the Python standard library only:
a hand-built 5x7 bitmap font, filled rectangles, circles and a tiny PNG
encoder (zlib). No assets, no network, no randomness — running main.py
twice produces a byte-identical file.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)   # warm newsprint
INK = (20, 20, 20)        # near-black ink
RED = (172, 32, 32)       # headline accent red
GREY = (110, 105, 95)     # secondary rules / captions
LIGHT = (232, 226, 210)   # light panel fill
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap glyphs, '#' = ink. Written by hand for this entry.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ";": (".....", "..#..", ".....", ".....", "..#..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": ("...##", "##..#", "#.#..", ".##.#", "..#.#", "#..##", "##..."),
}


def glyph(ch):
    """Uppercase-only font; anything unknown becomes '?'."""
    return FONT.get(ch.upper(), FONT["?"])


def text_width(text, scale):
    """Pixel width of text at the given scale (1px tracking per glyph)."""
    if not text:
        return 0
    return len(text) * (5 * scale + scale) - scale


def wrap_words(text, max_chars):
    """Greedy word wrap; returns a list of lines of at most max_chars."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
def new_canvas():
    buf = bytearray(W * H * 3)
    r, g, b = PAPER
    buf[0::3] = bytes([r]) * (W * H)
    buf[1::3] = bytes([g]) * (W * H)
    buf[2::3] = bytes([b]) * (W * H)
    return buf


def put(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(buf, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = color


def hline(buf, x, y, w, color, thick=1):
    fill_rect(buf, x, y, w, thick, color)


def vline(buf, x, y, h, color, thick=1):
    fill_rect(buf, x, y, thick, h, color)


def frame(buf, x, y, w, h, color, thick=1):
    hline(buf, x, y, w, color, thick)
    hline(buf, x, y + h - thick, w, color, thick)
    vline(buf, x, y, h, color, thick)
    vline(buf, x + w - thick, y, h, color, thick)


def draw_text(buf, x, y, text, scale, color):
    """Draw text left-aligned; returns the pixel width drawn."""
    cx = x
    for ch in text:
        rows = glyph(ch)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "#":
                    fill_rect(buf, cx + rx * scale, y + ry * scale,
                              scale, scale, color)
        cx += 5 * scale + scale
    return cx - x - scale if text else 0


def draw_centered(buf, y, text, scale, color, cx=W // 2):
    w = text_width(text, scale)
    draw_text(buf, cx - w // 2, y, text, scale, color)


def draw_block(buf, x, y, text, scale, color, max_w, leading):
    """Wrapped paragraph; returns the y just below the last line."""
    max_chars = max(1, max_w // (5 * scale + scale))
    lines = wrap_words(text, max_chars)
    for i, line in enumerate(lines):
        draw_text(buf, x, y + i * leading, line, scale, color)
    return y + len(lines) * leading


def draw_circle(buf, cx, cy, r, color, filled=False):
    """Midpoint circle; filled scans horizontal chords."""
    x = 0
    yy = r
    d = 1 - r
    pts = set()
    while x <= yy:
        for sx, sy in ((x, yy), (yy, x), (-x, yy), (-yy, x),
                       (x, -yy), (yy, -x), (-x, -yy), (-yy, -x)):
            pts.add((cx + sx, cy + sy))
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - yy) + 5
            yy -= 1
        x += 1
    if filled:
        by_row = {}
        for px, py in pts:
            by_row.setdefault(py, []).append(px)
        for py, xs in by_row.items():
            fill_rect(buf, min(xs), py, max(xs) - min(xs) + 1, 1, color)
    else:
        for px, py in pts:
            put(buf, px, py, color)


def draw_line(buf, x0, y0, x1, y1, color):
    """Bresenham line."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        put(buf, x0, y0, color)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_globe(buf, cx, cy, r):
    """Simple wireframe globe: outline, equator, two meridians."""
    draw_circle(buf, cx, cy, r, INK)
    hline(buf, cx - r, cy, 2 * r + 1, INK)
    # vertical meridian (ellipse approximated by scaled circle points)
    for t in range(0, 360, 4):
        a = math.radians(t)
        px = cx + int(r * 0.45 * math.cos(a))
        py = cy + int(r * math.sin(a))
        put(buf, px, py, INK)
        px2 = cx + int(r * math.cos(a))
        py2 = cy + int(r * 0.45 * math.sin(a))
        put(buf, px2, py2, INK)
    # land hint: small filled block for a continent
    fill_rect(buf, cx - r // 2, cy - r // 3, r // 2, r // 4, RED)
    fill_rect(buf, cx + r // 6, cy + r // 5, r // 3, r // 5, RED)


def draw_flame(buf, x, y, s):
    """Stylised flame pictogram, s = pixel height."""
    w = s // 2
    pts_top = (x + w // 2, y)
    pts_left = (x, y + s)
    pts_right = (x + w, y + s)
    draw_line(buf, pts_top[0], pts_top[1], pts_left[0], pts_left[1], RED)
    draw_line(buf, pts_top[0], pts_top[1], pts_right[0], pts_right[1], RED)
    hline(buf, x, y + s, w + 1, RED)
    fill_rect(buf, x + w // 4, y + s // 2, w // 2, s // 2, RED)


def draw_flag(buf, x, y, s):
    """Chequered flag pictogram, s = square size."""
    for r in range(2):
        for c in range(4):
            if (r + c) % 2 == 0:
                fill_rect(buf, x + c * s, y + r * s, s, s, INK)
    frame(buf, x, y, 4 * s, 2 * s, INK)
    vline(buf, x - 2, y, 2 * s + 6, INK, 2)


# ---------------------------------------------------------------- png ------
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(buf, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- layout ----
MARGIN = 36
INNER = W - 2 * MARGIN  # 952


def story_box(buf, x, y, w, h, kicker, headline, body, accent=None):
    """A framed story box: red kicker, headline, wrapped body."""
    frame(buf, x, y, w, h, INK, 2)
    if accent is not None:
        fill_rect(buf, x + 2, y + 2, w - 4, 26, LIGHT)
        draw_text(buf, x + 12, y + 6, kicker, 2, RED)
        hy = y + 36
    else:
        draw_text(buf, x + 12, y + 10, kicker, 2, RED)
        hy = y + 34
    draw_text(buf, x + 12, hy, headline, 3, INK)
    by = hy + 3 * 7 + 14
    draw_block(buf, x + 12, by, body, 2, INK, w - 24, 18)
    return y + h


def build():
    buf = new_canvas()

    # ---- masthead ------------------------------------------------------
    draw_centered(buf, 34, "THE WORLD IN ONE DAY", 7, INK)
    hline(buf, MARGIN, 96, INNER, INK, 2)
    draw_centered(buf, 108, "TUESDAY, 24 NOVEMBER 2026  -  SELASA 24 NOVEMBER 2026",
                  2, INK)
    hline(buf, MARGIN, 132, INNER, INK, 4)
    hline(buf, MARGIN, 140, INNER, INK, 1)

    # ---- lead story: COP31 collapse ------------------------------------
    lx, ly, lw, lh = MARGIN, 154, INNER, 286
    frame(buf, lx, ly, lw, lh, INK, 3)
    fill_rect(buf, lx + 3, ly + 3, lw - 6, 28, LIGHT)
    draw_text(buf, lx + 14, ly + 9, "CLIMATE  -  ANTALYA, TURKIYE", 2, RED)
    draw_text(buf, lx + 14, ly + 46, "COP31 COLLAPSES", 6, INK)
    draw_text(buf, lx + 14, ly + 92, "NO CLIMATE DEAL", 6, RED)
    lead_body = (
        "After two weeks of talks, nearly 200 nations left Antalya with "
        "no pact. The final draft never named fossil fuels, and critics "
        "called the outcome a failure as the longest climate summit in "
        "history ended divided."
    )
    draw_block(buf, lx + 14, ly + 148, lead_body, 2, INK, 600, 18)
    draw_globe(buf, lx + 800, ly + 190, 72)
    draw_centered(buf, ly + lh - 24, "THE LONGEST COP IN HISTORY ENDS WITHOUT A DEAL",
                  1, GREY, cx=lx + 330)

    # ---- row 2: Banten fire / Kyiv drones ------------------------------
    y2 = 456
    box_w = (INNER - 24) // 2  # 464
    story_box(
        buf, MARGIN, y2, box_w, 176,
        "INDONESIA", "FACTORY FIRE",
        "At least 24 people are dead and about 30 missing after a fire "
        "tore through a factory in Banten. Rescue teams are still "
        "searching the site.",
        accent=True,
    )
    draw_flame(buf, MARGIN + box_w - 52, y2 + 44, 26)
    story_box(
        buf, MARGIN + box_w + 24, y2, box_w, 176,
        "UKRAINE WAR", "DRONES OVER KYIV",
        "Several people are missing after a Russian drone strike in the "
        "Kyiv region. A Russian cargo ship also caught fire off Finland "
        "after a reported attack.",
        accent=True,
    )

    # ---- row 3: Shenzhen summit / India-Nepal --------------------------
    y3 = 648
    story_box(
        buf, MARGIN, y3, box_w, 176,
        "APEC SUMMIT", "SHENZHEN SUMMIT",
        "Trump, Xi and Putin meet in Shenzhen. Trump also blamed "
        "Democrats after a US market sell-off wiped out about 1 "
        "trillion dollars.",
        accent=True,
    )
    story_box(
        buf, MARGIN + box_w + 24, y3, box_w, 176,
        "INDIA - NEPAL", "NEW EXPRESS LINE",
        "PM Modi and Nepal PM Balendra Shah flag off the Saryu-Kamala "
        "Express linking Ayodhya and Janakpur, with a 15,000 crore "
        "package and eight MoUs.",
        accent=True,
    )

    # ---- sport strip ----------------------------------------------------
    ys = 840
    fill_rect(buf, MARGIN, ys, INNER, 56, INK)
    draw_text(buf, MARGIN + 14, ys + 12, "SPORT", 3, RED)
    draw_text(buf, MARGIN + 118, ys + 20,
              "PANT HITS 128 IN DRAWN WELLINGTON TEST", 2, WHITE)
    draw_text(buf, MARGIN + 118, ys + 38,
              "VERSTAPPEN WINS THE LAS VEGAS GRAND PRIX", 2, WHITE)
    draw_flag(buf, MARGIN + INNER - 62, ys + 14, 10)

    # ---- markets strip ---------------------------------------------------
    ym = 908
    frame(buf, MARGIN, ym, INNER, 46, INK, 2)
    draw_text(buf, MARGIN + 12, ym + 14,
              "MARKETS: SENSEX -1,484 TO 82,435 - INDIA OIL IMPORT BILL UP 60%",
              2, INK)

    # ---- footer ----------------------------------------------------------
    draw_centered(buf, 972, "THE WORLD IN ONE DAY  -  TUESDAY, 24 NOVEMBER 2026",
                  2, GREY)
    hline(buf, MARGIN, 1002, INNER, INK, 1)

    return buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = save_png(build(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
