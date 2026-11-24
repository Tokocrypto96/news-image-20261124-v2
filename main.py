#!/usr/bin/env python3
"""THE DAILY GLOBE -- Tuesday, 24 November 2026.

A one-page newspaper front page summing up the world's news of
24 November 2026, drawn entirely with the Python standard library
(no third-party packages, no network, no randomness) and written to
/output/entry.png as a 1024x1024 PNG. Deterministic: two runs write
identical bytes.
"""
import hashlib
import math
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (253, 248, 236)
INK = (18, 18, 18)
RED = (178, 34, 34)
NAVY = (18, 42, 84)
BLUE = (30, 90, 160)
SKY = (120, 180, 220)
GREEN = (16, 120, 60)
GOLD = (198, 158, 40)
ORANGE = (222, 92, 20)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
LIGHT = (238, 232, 214)

# 5x7 bitmap font, uppercase + digits + punctuation.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "*": ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
}

# Pixel buffer, pre-filled with paper cream.
buf = bytearray(bytes(CREAM) * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(c)


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def border(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def ring(cx, cy, r, c, t=3):
    disc(cx, cy, r, c)
    disc(cx, cy, r - t, CREAM)


def poly(points, c):
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)


def text_w(s, sc):
    return len(s) * 6 * sc - sc if s else 0


def draw_text(x, y, s, sc, c):
    s = s.upper()
    for ci, ch in enumerate(s):
        g = FONT.get(ch, FONT[" "])
        ox = x + ci * 6 * sc
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == "1":
                    rect(ox + col * sc, y + r * sc, sc, sc, c)


def center_text(cx, y, s, sc, c):
    draw_text(cx - text_w(s, sc) // 2, y, s, sc, c)


def wrap(s, sc, max_w):
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, sc) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, sc, c, max_w, leading):
    for ln in wrap(s, sc, max_w):
        draw_text(x, y, ln, sc, c)
        y += leading
    return y


def kicker(x, y, s):
    draw_text(x, y, s, 2, RED)


def rule(y, t=2):
    hline(28, y, W - 56, INK, t)


# ---- Illustrations (all drawn with the primitives above) ----

def draw_chip(x, y, w, h):
    rect(x, y, w, h, NAVY)
    border(x, y, w, h, INK, 2)
    for i in range(6):
        rect(x - 8, y + 14 + i * 20, 8, 8, GOLD)
        rect(x + w, y + 14 + i * 20, 8, 8, GOLD)
    rect(x + 24, y + 18, w - 48, h - 36, (28, 64, 120))
    draw_text(x + 40, y + 30, "NVDA", 4, WHITE)
    draw_text(x + 40, y + 66, "+31%", 4, (120, 230, 140))
    pts = [(x + 30, y + h - 28), (x + 90, y + h - 48), (x + 150, y + h - 40),
           (x + 210, y + h - 66), (x + 280, y + h - 84), (x + w - 30, y + h - 108)]
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], (120, 230, 140))
        line(a[0], a[1] + 1, b[0], b[1] + 1, (120, 230, 140))
    line(pts[-1][0], pts[-1][1], pts[-1][0] - 16, pts[-1][1] + 2, (120, 230, 140))
    line(pts[-1][0], pts[-1][1], pts[-1][0] - 2, pts[-1][1] + 16, (120, 230, 140))


def draw_globe(x, y, w, h):
    cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 2 - 4
    disc(cx, cy, r, SKY)
    ring(cx, cy, r, NAVY, 3)
    for k in (-1, 0, 1):
        for dy in range(-r + 6, r - 5):
            dx = int(math.sqrt(max(0, r * r - dy * dy))) if k == 0 else int(
                math.sqrt(max(0, r * r - dy * dy)) * (0.55 if k else 1))
            if k == 0:
                px(cx, cy + dy, NAVY)
            else:
                px(cx + k * dx // 2, cy + dy, NAVY)
    hline(cx - r + 4, cy, 2 * r - 8, NAVY, 2)
    line(cx - 6, cy - r + 8, cx + 10, cy - 8, RED)
    line(cx + 10, cy - 8, cx - 4, cy + 12, RED)
    line(cx - 4, cy + 12, cx + 12, cy + r - 10, RED)


def draw_ball(x, y, w, h):
    cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 2 - 4
    disc(cx, cy, r, WHITE)
    ring(cx, cy, r, INK, 3)
    disc(cx, cy, r // 3, INK)
    for ang in range(0, 360, 72):
        a = math.radians(ang - 90)
        ex = int(cx + math.cos(a) * (r - 4))
        ey = int(cy + math.sin(a) * (r - 4))
        line(cx + int(math.cos(a) * r // 3), cy + int(math.sin(a) * r // 3), ex, ey, INK)


def draw_ship(x, y, w, h):
    poly([(x + 20, y + 26), (x + w - 20, y + 26), (x + w - 46, y + 44),
          (x + 44, y + 44)], NAVY)
    rect(x + 60, y + 6, 10, 20, INK)
    rect(x + 120, y + 12, 10, 14, INK)
    poly([(x + w - 100, y + 26), (x + w - 86, y + 10), (x + w - 108, y + 14)], ORANGE)
    poly([(x + w - 96, y + 26), (x + w - 86, y + 16), (x + w - 102, y + 18)], GOLD)
    rect(x + 8, y + 46, w - 16, 3, SKY)
    rect(x + 30, y + 49, w - 60, 2, SKY)


def draw_factory(x, y, w, h):
    rect(x + 10, y + 28, w - 20, 20, (150, 120, 90))
    poly([(x + 10, y + 28), (x + 60, y + 10), (x + 110, y + 28)], (120, 90, 60))
    poly([(x + 110, y + 28), (x + 160, y + 10), (x + 210, y + 28)], (120, 90, 60))
    rect(x + w - 34, y + 2, 16, 26, INK)
    poly([(x + w - 60, y + 2), (x + w - 44, y + 18), (x + w - 64, y + 20),
          (x + w - 70, y + 8)], ORANGE)
    poly([(x + w - 54, y + 8), (x + w - 44, y + 18), (x + w - 58, y + 20)], GOLD)
    for i in range(3):
        rect(x + 30 + i * 44, y + 34, 22, 12, NAVY)
    disc(x + 40, y + 6, 5, GREY)
    disc(x + 56, y + 2, 4, GREY)


def draw_chess(x, y, w, h):
    s = (h - 8) // 8
    bx, by = x + (w - s * 8) // 2, y + 4
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 0:
                rect(bx + c * s, by + r * s, s, s, WHITE)
            else:
                rect(bx + c * s, by + r * s, s, s, INK)
    border(bx, by, s * 8, s * 8, INK, 2)
    disc(bx + 2 * s + s // 2, by + 1 * s + s // 2, s // 2 - 1, WHITE)
    rect(bx + 2 * s + s // 2 - 1, by + 1 * s + 2, 2, s - 4, INK)
    disc(bx + 5 * s + s // 2, by + 6 * s + s // 2, s // 2 - 1, RED)
    rect(bx + 5 * s + s // 2 - 1, by + 6 * s + 2, 2, s - 4, WHITE)


def build():
    # Dateline
    draw_text(28, 32, "TUESDAY, 24 NOVEMBER 2026", 2, INK)
    draw_text(W - 28 - text_w("ONE DAY - ONE PAGE", 2), 32, "ONE DAY - ONE PAGE", 2, GREY)
    rule(58)
    # Masthead
    center_text(W // 2, 70, "THE DAILY GLOBE", 8, INK)
    center_text(W // 2, 136, "THE WORLD'S NEWS - TUESDAY 24 NOVEMBER 2026", 2, RED)
    hline(28, 160, W - 56, INK, 3)
    hline(28, 166, W - 56, INK, 1)

    # Lead story: Huang is back
    kicker(28, 184, "TECH - MARKETS")
    draw_text(28, 206, "HUANG IS BACK", 7, INK)
    draw_para(28, 262, "NVIDIA REINSTATES JENSEN HUANG AS CEO - SHARES "
              "JUMP 31% AS NASDAQ SOARS 6.5%", 3, INK, 570, 26)
    draw_chip(620, 184, 376, 154)
    rule(352)

    # Row 2: COP31 and World Cup
    kicker(28, 368, "CLIMATE - COP31")
    draw_para(28, 390, "COP31 COLLAPSES", 4, INK, 468, 30)
    draw_para(28, 452, "ANTALYA TALKS END WITH NO DEAL AS FOSSIL-FUEL "
              "LANGUAGE IS DROPPED", 3, INK, 468, 24)
    draw_globe(28, 528, 468, 72)
    kicker(528, 368, "FOOTBALL - WORLD CUP")
    draw_para(528, 390, "WORLD CUP HOSTS NAMED", 4, INK, 468, 30)
    draw_para(528, 452, "2031: USA, MEXICO, COSTA RICA, JAMAICA - 2035: "
              "ENGLAND, SCOTLAND, WALES, N. IRELAND", 3, INK, 468, 24)
    draw_ball(528, 528, 468, 72)
    rule(616)

    # Row 3: ship, factory fire, chess
    cols = [(28, "SHIP AFIRE, TOWED HOME", "RUSSIAN SHIP SPARTA II HIT BY "
             "DRONE IN THE GULF OF FINLAND - TOWED TO ST PETERSBURG AS "
             "KYIV IS HIT AGAIN", draw_ship),
            (360, "24 DEAD IN FACTORY FIRE", "CANDY FACTORY BLAZE IN BANTEN "
             "- ABOUT 30 STILL MISSING", draw_factory),
            (692, "CHESS CROWN ON THE LINE", "GUKESH FACES SINDAROV AS THE "
             "WORLD CHAMPIONSHIP OPENS IN GENEVA", draw_chess)]
    for x, head, sub, art in cols:
        kicker(x, 632, "WORLD")
        draw_para(x, 652, head, 3, INK, 304, 24)
        draw_para(x, 702, sub, 2, INK, 304, 18)
        art(x, 780, 304, 50)
    rule(846)

    # In brief
    draw_text(28, 856, "IN BRIEF", 3, RED)
    brief = [("INDIA-NEPAL: SARYU-KAMALA EXPRESS", "LISBON: COST-OF-LIVING PROTEST"),
             ("ALCARAZ WINS THE ATP FINALS", "VERSTAPPEN WINS LAS VEGAS GP"),
             ("INDIA-NZ TEST ENDS IN A DRAW", "US: APPEALS COURT UPHOLDS HUSH-MONEY CONVICTION")]
    yy = 888
    for left, right in brief:
        draw_text(28, yy, "- " + left, 2, INK)
        draw_para(528, yy, "- " + right, 2, INK, 468, 18)
        yy += 28
    center_text(W // 2, 980, "24 NOVEMBER 2026 - THE DAILY GLOBE", 2, GREY)


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    build()
    data = png_bytes()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes",
          "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
