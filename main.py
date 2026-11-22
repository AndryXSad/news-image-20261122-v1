#!/usr/bin/env python3
"""The Daily Globe — Sunday 22 November 2026.
A single self-contained PIL program that draws a 1024x1024 front page
summing up the world's news of 22 November 2026. Deterministic:
seeded Random only, no timestamps, no network, stdlib + PIL only.
Writes entry.png into MAKEFUN_OUTPUT_DIR (default: next to main.py).
If PIL is unavailable, it copies the pre-rendered entry.png shipped
in this repository instead, so the output is identical either way.
"""

import os
import random
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:  # grader container without PIL: fall back to the copy
    HAVE_PIL = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "entry.png"

W, H = 1024, 1024
SEED = 20261122

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
PAPER2 = (238, 230, 211)
INK = (18, 18, 18)
MUTED = (90, 84, 70)
RED = (163, 18, 18)
DARKRED = (120, 10, 10)
GOLD = (176, 132, 16)
GOLD_LT = (212, 175, 55)
NAVY = (28, 47, 74)
NAVY_DK = (16, 32, 52)
TEAL = (14, 94, 90)
OCEAN = (22, 48, 74)
LAND = (217, 201, 163)
LAND_DK = (198, 178, 132)
SKY = (214, 232, 240)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DJ = "/usr/share/fonts/truetype/dejavu/"
SERIF = DJ + "DejaVuSerif-Bold.ttf"
SERIF_R = DJ + "DejaVuSerif.ttf"
SANS = DJ + "DejaVuSans.ttf"
SANS_B = DJ + "DejaVuSans-Bold.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(text, font, width):
    """Greedy word wrap; returns a list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, font, fill, leading=None):
    if leading is None:
        leading = int(font.size * 1.18)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def fit_lines(text, font, width, max_lines):
    """Wrap and hard-truncate to max_lines (last line gets an ellipsis)."""
    lines = wrap(text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and font.getlength(lines[-1] + "...") > width:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


# ---------------------------------------------------------------- map data
# Simplified continent outlines in (lon, lat). Drawn for this edition.
NORTH_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
                 (-135, 57), (-130, 54), (-125, 49), (-124, 42), (-120, 34),
                 (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17),
                 (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-79, 9),
                 (-81, 13), (-84, 16), (-87, 21), (-90, 21), (-91, 19),
                 (-94, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
                 (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
                 (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52),
                 (-64, 58), (-68, 58), (-72, 62), (-78, 62), (-85, 66),
                 (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
                 (-155, 71), (-165, 68), (-168, 66)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
             (-22, 70), (-20, 74), (-25, 78), (-35, 80), (-50, 80),
             (-58, 76), (-60, 70), (-58, 64)]
SOUTH_AMERICA = [(-77, 7), (-72, 11), (-64, 10), (-60, 8), (-52, 5),
                 (-50, 0), (-44, -3), (-35, -8), (-38, -15), (-40, -22),
                 (-48, -28), (-52, -33), (-58, -38), (-62, -41), (-65, -45),
                 (-68, -50), (-70, -54), (-73, -50), (-73, -44), (-72, -37),
                 (-71, -30), (-70, -20), (-70, -18), (-75, -15), (-77, -12),
                 (-80, -6), (-81, -3), (-80, 1), (-77, 4), (-77, 7)]
AFRICA = [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-5, 35), (0, 36),
          (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (35, 28),
          (37, 22), (39, 18), (43, 12), (48, 11), (51, 10), (46, 5),
          (41, 0), (40, -5), (40, -10), (36, -18), (33, -26), (28, -33),
          (20, -35), (17, -32), (15, -27), (12, -18), (13, -12), (12, -6),
          (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 12), (-17, 15)]
EURASIA = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
           (-2, 49), (0, 51), (3, 53), (8, 57), (5, 60), (10, 62),
           (12, 65), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68),
           (45, 68), (50, 69), (55, 68), (60, 69), (68, 73), (75, 73),
           (80, 73), (90, 75), (100, 77), (110, 76), (120, 73), (130, 72),
           (140, 72), (150, 70), (160, 70), (170, 67), (178, 65), (178, 62),
           (170, 60), (162, 60), (158, 55), (162, 52), (156, 50), (150, 45),
           (142, 45), (140, 40), (135, 35), (130, 33), (127, 35), (122, 38),
           (120, 32), (118, 25), (110, 20), (108, 15), (105, 10), (103, 7),
           (100, 8), (98, 12), (95, 16), (92, 21), (90, 22), (86, 20),
           (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (65, 25),
           (61, 25), (57, 26), (54, 27), (51, 28), (50, 26), (48, 29),
           (48, 24), (44, 20), (43, 16), (40, 15), (38, 20), (35, 28),
           (34, 31), (30, 36), (27, 37), (23, 36), (22, 37), (19, 40),
           (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
           (-6, 36), (-10, 36)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
           (1, 51), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
         (141, 41), (142, 44), (144, 44), (141, 40), (139, 37), (137, 34),
         (133, 34), (130, 31)]
INDONESIA = [(95, 5), (98, 5), (100, 0), (102, -3), (105, -5), (108, -7),
             (110, -7), (112, -8), (114, -9), (116, -9), (118, -10),
             (120, -10), (122, -8), (124, -10), (127, -8), (129, -5),
             (130, -2), (128, 0), (126, 1), (124, 0), (122, 0), (120, 0),
             (117, 2), (114, 3), (110, 1), (107, 0), (104, 1), (101, 3),
             (98, 5), (95, 5)]
AUSTRALIA = [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (138, -12), (136, -15),
             (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20), (113, -22)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
              (45, -25), (43, -22), (43, -18), (44, -16)]
NEW_ZEALAND = [(167, -45), (169, -43), (171, -41), (174, -39), (176, -38),
               (178, -37), (177, -39), (175, -41), (174, -43), (171, -45),
               (168, -46), (167, -45)]

LAND_POLYS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              BRITAIN, JAPAN, INDONESIA, AUSTRALIA, MADAGASCAR, NEW_ZEALAND]


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)):
            xinters = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xinters:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(point_in_poly(lon, lat, p) for p in LAND_POLYS)


# ---------------------------------------------------------------- lead art
# Each art function draws on its own layer (local coords, clipped to the
# box) and returns the finished image, so nothing can escape the frame.
def art_cop31(w, h, rng):
    """Antalya: warming globe, thermometer, 'FOSSIL FUELS: 0'."""
    img = Image.new("RGB", (w, h), (232, 214, 170))
    d = ImageDraw.Draw(img)
    for i in range(h):
        t = i / max(1, h - 1)
        d.line([(0, i), (w, i)],
               fill=(int(232 - 60 * t), int(214 - 40 * t), int(170 - 30 * t)))
    # small sun, top left
    d.ellipse([8, 6, 34, 32], fill=(240, 200, 90))
    d.ellipse([13, 11, 29, 27], fill=(250, 222, 130))
    # globe
    cx, cy, r = 82, h // 2 + 2, 40
    d.ellipse([cx - r - 3, cy - r + 2, cx + r + 3, cy + r + 6],
              fill=(120, 90, 40))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 118, 158))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 330, fill=(190, 225, 240),
          width=3)
    d.ellipse([cx - 26, cy - 18, cx - 2, cy + 2], fill=(96, 140, 70))
    d.ellipse([cx + 2, cy - 6, cx + 24, cy + 16], fill=(120, 150, 80))
    d.ellipse([cx - 14, cy + 10, cx + 8, cy + 26], fill=(140, 160, 90))
    d.ellipse([cx + 12, cy - 24, cx + 28, cy - 8], fill=(96, 140, 70))
    for (ox, oy, ow) in [(-30, -26, 26), (6, 18, 30), (14, -30, 22)]:
        d.arc([cx + ox, cy + oy, cx + ox + ow, cy + oy + 10], 180, 360,
              fill=(235, 245, 250), width=2)
    # thermometer, right side
    tx = w - 96
    d.rounded_rectangle([tx, 8, tx + 16, h - 26], radius=8,
                        outline=INK, width=2, fill=(250, 250, 250))
    for yy in range(16, h - 34, 10):
        d.line([(tx + 16, yy), (tx + 22, yy)], fill=INK, width=1)
    d.rounded_rectangle([tx + 4, h - 52, tx + 12, h - 30], radius=3,
                        fill=RED)
    d.ellipse([tx - 3, h - 34, tx + 19, h - 12], fill=RED)
    d.ellipse([tx - 3, h - 34, tx + 19, h - 12], outline=INK, width=2)
    d.text((tx + 26, 10), "OVERTIME", font=F(SANS_B, 10), fill=INK)
    d.text((tx + 26, 24), "DAY 3", font=F(SANS_B, 10), fill=MUTED)
    # bottom caption: label + big zero, measured so they never collide
    lab = "FOSSIL FUELS NAMED:"
    lf = F(SANS_B, 10)
    d.text((8, h - 20), lab, font=lf, fill=DARKRED)
    d.text((8 + lf.getlength(lab) + 6, h - 26), "0", font=F(SERIF, 22),
           fill=DARKRED)
    return img


def art_ukraine(w, h, rng):
    """Kyiv overnight: night sky, drones, explosions over a skyline."""
    import math
    img = Image.new("RGB", (w, h), (12, 20, 38))
    d = ImageDraw.Draw(img)
    for _ in range(46):
        sx = rng.randint(2, w - 3)
        sy = rng.randint(2, h // 2)
        d.point((sx, sy), fill=(200, 210, 230))
    d.ellipse([w - 46, 8, w - 18, 36], fill=(232, 230, 210))
    d.ellipse([w - 40, 14, w - 30, 24], fill=(200, 198, 178))
    base = h - 16
    heights = [34, 52, 44, 62, 38, 56, 48, 66, 40, 54, 36]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = i * bw
        d.rectangle([bx + 1, base - hh, bx + bw - 1, base], fill=(6, 10, 20))
        for wy in range(base - hh + 6, base - 6, 9):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rng.random() < 0.45:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(240, 200, 90))
    for (ex, ey, er) in [(58, 26, 13), (210, 18, 16), (150, 38, 10)]:
        for k in range(10):
            ang = k * 36
            dx = math.cos(math.radians(ang)) * er
            dy = math.sin(math.radians(ang)) * er * 0.7
            d.line([(ex, ey), (ex + dx, ey + dy)], fill=(255, 150, 40),
                   width=3)
        d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(255, 200, 80))
        d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 240, 180))
    for (dx, dy) in [(96, 14), (178, 44), (262, 30), (36, 48), (238, 58)]:
        d.line([(dx - 7, dy - 3), (dx + 7, dy + 3)], fill=(220, 220, 220),
               width=2)
        d.line([(dx - 7, dy + 3), (dx + 7, dy - 3)], fill=(220, 220, 220),
               width=2)
        d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=RED)
    # caption bar so the text never sits on the buildings
    d.rectangle([0, h - 16, w, h], fill=(12, 20, 38))
    cap = "148 DRONES  ·  3 MISSILES  ·  OVERNIGHT"
    cf = F(SANS_B, 10)
    d.text(((w - cf.getlength(cap)) / 2, h - 14), cap, font=cf,
           fill=(255, 210, 120))
    return img


def art_gulf(w, h, rng):
    """Hormuz: tanker at sea, smoke plume, flames, strait label."""
    img = Image.new("RGB", (w, h), (40, 90, 120))
    d = ImageDraw.Draw(img)
    for i in range(h // 2):
        t = i / max(1, h // 2 - 1)
        d.line([(0, i), (w, i)],
               fill=(int(250 - 30 * t), int(220 - 20 * t), int(180 - 10 * t)))
    d.ellipse([18, 10, 48, 40], fill=(245, 190, 90))
    for i in range(h // 2, h):
        t = (i - h // 2) / max(1, h // 2 - 1)
        d.line([(0, i), (w, i)],
               fill=(int(40 - 12 * t), int(90 - 20 * t), int(120 - 20 * t)))
    for i in range(6):
        wy = h // 2 + 8 + i * 9
        d.line([(6 + (i % 2) * 20, wy), (w - 10, wy)],
               fill=(140, 180, 200), width=1)
    # tanker: hull top at h-44, so funnel + plume stay inside the frame
    hx, hy = 30, h - 44
    d.polygon([(hx, hy), (hx + 190, hy), (hx + 178, hy + 22),
               (hx + 8, hy + 22)], fill=(30, 30, 34))
    d.rectangle([hx + 150, hy - 26, hx + 182, hy], fill=(30, 30, 34))
    d.rectangle([hx + 156, hy - 20, hx + 176, hy - 12], fill=(240, 200, 90))
    d.rectangle([hx + 40, hy - 26, hx + 52, hy], fill=(150, 30, 30))
    d.rectangle([hx + 40, hy - 32, hx + 52, hy - 26], fill=(60, 60, 64))
    for (fx, fy, fr) in [(hx + 90, hy - 6, 10), (hx + 120, hy - 4, 8)]:
        d.polygon([(fx - fr, fy), (fx, fy - fr * 2), (fx + fr, fy)],
                  fill=(255, 140, 30))
        d.polygon([(fx - fr // 2, fy), (fx, fy - fr), (fx + fr // 2, fy)],
                  fill=(255, 220, 90))
    for i, (sx, sy, sr) in enumerate([(hx + 46, hy - 38, 7),
                                      (hx + 40, hy - 48, 9),
                                      (hx + 48, hy - 56, 8)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(70, 70, 74) if i % 2 == 0 else (95, 95, 100))
    d.rectangle([0, h - 16, w, h], fill=(20, 50, 70))
    cap = "STRAIT OF HORMUZ — 2 TANKERS HIT"
    cf = F(SANS_B, 10)
    d.text(((w - cf.getlength(cap)) / 2, h - 14), cap, font=cf,
           fill=(255, 230, 160))
    return img


# ---------------------------------------------------------------- page
def build():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 88], fill=PAPER)
    # small globe mark, left
    gx, gy, gr = 52, 44, 26
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=NAVY)
    d.ellipse([gx - gr + 4, gy - gr + 4, gx + gr - 4, gy + gr - 4],
              fill=(52, 118, 158))
    d.ellipse([gx - 14, gy - 12, gx + 2, gy + 2], fill=(96, 140, 70))
    d.ellipse([gx + 4, gy + 2, gx + 18, gy + 16], fill=(120, 150, 80))
    d.arc([gx - gr + 4, gy - gr + 4, gx + gr - 4, gy + gr - 4], 200, 330,
          fill=(190, 225, 240), width=2)
    title = "THE DAILY GLOBE"
    tf = F(SERIF, 52)
    tw = tf.getlength(title)
    d.text(((W - tw) / 2, 16), title, font=tf, fill=INK)
    d.text((W - 208, 18), "SUNDAY", font=F(SANS_B, 15), fill=RED)
    d.text((W - 208, 38), "22 NOVEMBER 2026", font=F(SANS_B, 15), fill=INK)
    d.text((W - 208, 58), "No. 327  ·  PRICE FREE", font=F(SANS, 10),
           fill=MUTED)
    d.rectangle([0, 88, W, 91], fill=GOLD)
    d.rectangle([0, 92, W, 93], fill=INK)

    # ---- standfirst strip
    d.text((10, 100), "THE WORLD IN ONE DAY",
           font=F(SANS_B, 12), fill=RED)
    mid = "45 STORIES  ·  8 PLACES  ·  7 REGIONS"
    mf = F(SANS_B, 12)
    d.text(((W - mf.getlength(mid)) / 2, 100), mid, font=mf, fill=INK)
    dc = "DATE-CHECKED: ALL STORIES 22 NOV 2026"
    df = F(SANS_B, 11)
    d.text((W - 10 - df.getlength(dc), 101), dc, font=df, fill=TEAL)

    # ---- leads
    leads = [
        dict(kicker="CLIMATE  ·  ANTALYA", art=art_cop31,
             head="COP31 nears a deal at last",
             deck="After three days of overtime, the presidency tables a new "
                  "package — but fossil fuels are still not named. Delegates "
                  "reconvene at 06:00 GMT to approve it.",
             credit="ANTALYA — Reuters / AP"),
        dict(kicker="WAR  ·  UKRAINE", art=art_ukraine,
             head="Kyiv hit again overnight",
             deck="Russia fires 148 drones and 3 ballistic missiles across "
                  "Ukraine. Two killed, 83 hurt; Kryvyi Rih takes the worst "
                  "of it, a child and a paramedic among the dead.",
             credit="KYIV — Kyiv Independent"),
        dict(kicker="WAR  ·  THE GULF", art=art_gulf,
             head="Iran strikes Bahrain",
             deck="Bahrain says an industrial site is ablaze and two tankers "
                  "are hit off Hormuz. Tehran claims two US bases hit.",
             credit="MANAMA — Reuters / FMT"),
    ]
    lx = [8, 348, 688]
    for i, lead in enumerate(leads):
        x = lx[i]
        w = 328
        d.text((x, 118), lead["kicker"], font=F(SANS_B, 11), fill=RED)
        img.paste(lead["art"](w, 104, rng), (x, 136))
        d.rectangle([x, 136, x + w, 240], outline=INK, width=1)
        y = 248
        for ln in fit_lines(lead["head"], F(SERIF, 20), w, 2):
            d.text((x, y), ln, font=F(SERIF, 20), fill=INK)
            y += 24
        y += 2
        y = draw_lines(d, x, y,
                       fit_lines(lead["deck"], F(SANS, 12), w, 3),
                       F(SANS, 12), INK, leading=15)
        d.text((x, min(y + 2, 330)), lead["credit"], font=F(SANS_B, 9),
               fill=MUTED)

    # ---- map + timeline
    mx, my, mw, mh = 8, 336, 636, 220
    d.rectangle([mx, my, mx + mw, my + mh], fill=OCEAN)
    d.rectangle([mx, my, mx + mw, my + mh], outline=INK, width=1)
    # title bar inside map
    d.rectangle([mx, my, mx + mw, my + 22], fill=NAVY_DK)
    d.text((mx + 8, my + 4), "THE WORLD AT A GLANCE",
           font=F(SANS_B, 12), fill=WHITE)
    d.text((mx + mw - 8 - F(SANS, 10).getlength("8 PINS — ALL ON LAND"),
            my + 6), "8 PINS — ALL ON LAND", font=F(SANS, 10),
           fill=(190, 210, 230))

    def proj(lon, lat):
        px = mx + 8 + (lon + 180.0) / 360.0 * (mw - 16)
        py = my + 26 + (75.0 - lat) / 135.0 * (mh - 30)
        return (px, py)

    # graticule
    for lon in range(-150, 181, 30):
        x0, _ = proj(lon, 75)
        x1, _ = proj(lon, -60)
        d.line([(x0, my + 22), (x0, my + mh)], fill=(60, 95, 125), width=1)
    for lat in [60, 30, 0, -30]:
        _, y0 = proj(0, lat)
        d.line([(mx, y0), (mx + mw, y0)], fill=(60, 95, 125), width=1)
    # land
    for poly in LAND_POLYS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=(120, 100, 60))
    # land speckles (on-land only)
    for _ in range(500):
        lon = rng.uniform(-170, 180)
        lat = rng.uniform(-55, 72)
        if on_land(lon, lat):
            px, py = proj(lon, lat)
            d.point((px, py), fill=LAND_DK)
    # ocean stipple
    for _ in range(1200):
        lon = rng.uniform(-180, 180)
        lat = rng.uniform(-58, 74)
        if not on_land(lon, lat):
            px, py = proj(lon, lat)
            if mx + 2 < px < mx + mw - 2 and my + 24 < py < my + mh - 2:
                d.point((px, py), fill=(90, 130, 160))
    # ocean labels (centred; drawn after the land so no label hides
    # behind a continent)
    for (txt, lon, lat) in [("ATLANTIC", -30, 5), ("PACIFIC", -150, 5),
                            ("PACIFIC", 155, -25), ("INDIAN", 80, -28)]:
        tx, ty = proj(lon, lat)
        of = F(SANS_B, 10)
        d.text((tx - of.getlength(txt) / 2, ty), txt, font=of,
               fill=(110, 150, 180))
    # pins: (lon, lat, label, dx, dy) — coords verified on-land
    pins = [
        (36.9, 30.7, "ANTALYA", -52, 12),
        (30.5, 50.4, "KYIV", -34, -16),
        (49.8, 26.8, "MANAMA", 10, -4),
        (114.0, 23.0, "HONG KONG", -72, 12),
        (175.0, -40.8, "WELLINGTON", -78, -8),
        (-115.1, 36.2, "LAS VEGAS", 10, -8),
        (7.7, 45.1, "TURIN", 10, 10),
        (93.9, 24.8, "IMPHAL", 10, -10),
    ]
    for (lon, lat, label, dx, dy) in pins:
        px, py = proj(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=WHITE, width=2)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=WHITE)
        lf = F(SANS_B, 9)
        lx2 = max(mx + 2, min(px + dx, mx + mw - 2 - lf.getlength(label)))
        ly2 = max(my + 24, min(py + dy, my + mh - 12))
        d.rectangle([lx2 - 2, ly2 - 1, lx2 + lf.getlength(label) + 2,
                     ly2 + 11], fill=(10, 20, 32))
        d.text((lx2, ly2), label, font=lf, fill=WHITE)

    # timeline, right of map
    tx, ty, tw, th = 656, 336, 360, 220
    d.rectangle([tx, ty, tx + tw, ty + th], fill=PAPER2)
    d.rectangle([tx, ty, tx + tw, ty + th], outline=INK, width=1)
    d.text((tx + 10, ty + 6), "22 NOVEMBER — HOUR BY HOUR (UTC)",
           font=F(SANS_B, 12), fill=RED)
    d.line([(tx + 10, ty + 26), (tx + tw - 10, ty + 26)], fill=GOLD, width=2)
    moments = [
        ("00:00", "Explosions in Kyiv as a drone alert sounds across the "
                  "capital."),
        ("00:41", "Reuters: India 629/6 at lunch in Wellington, lead 261."),
        ("01:00", "Hong Kong polls open — 856 candidates, 723 seats."),
        ("03:00", "COP31 objection deadline on the new climate package."),
        ("06:00", "COP31 reconvenes in Antalya to approve the deal."),
    ]
    yy = ty + 36
    spine_x = tx + 52
    d.line([(spine_x, yy + 4), (spine_x, ty + th - 12)], fill=MUTED, width=2)
    for (t, txt) in moments:
        d.ellipse([spine_x - 4, yy + 2, spine_x + 4, yy + 10], fill=RED,
                  outline=WHITE, width=1)
        d.text((tx + 10, yy), t, font=F(SANS_B, 11), fill=RED)
        yy = draw_lines(d, tx + 66, yy,
                        fit_lines(txt, F(SANS, 11), tw - 76, 2),
                        F(SANS, 11), INK, leading=14)
        yy += 8

    # ---- day in figures
    fx, fy, fw, fh = 8, 562, 162, 74
    figures = [
        ("148", "Russian drones fired\nat Ukraine overnight", "zig"),
        ("83", "people injured in the\novernight attack", "bars"),
        ("720/9", "India declare in\nWellington — a record", "arrow"),
        ("856", "candidates in Hong\nKong's polls", "bars"),
        ("69.6%", "Hong Kong turnout\nby 11 am", "gauge"),
        ("11", "dead in Manipur\nafter toxic alcohol", "flat"),
    ]
    for i, (num, lab, kind) in enumerate(figures):
        x = fx + i * (fw + 8)
        d.rectangle([x, fy, x + fw, fy + fh], fill=WHITE, outline=INK,
                    width=1)
        d.text((x + 8, fy + 5), num, font=F(SERIF, 24), fill=RED)
        # mini chart, right of the number
        cx0, cy0, cw, chh = x + fw - 52, fy + 8, 44, 20
        if kind == "zig":
            pts = [(cx0, cy0 + 14), (cx0 + 11, cy0 + 4), (cx0 + 22, cy0 + 16),
                   (cx0 + 33, cy0 + 6), (cx0 + 44, cy0 + 2)]
            d.line(pts, fill=NAVY, width=2)
        elif kind == "bars":
            for j, bh in enumerate([6, 10, 8, 14, 18]):
                d.rectangle([cx0 + j * 9, cy0 + 20 - bh, cx0 + j * 9 + 6,
                             cy0 + 20], fill=NAVY)
        elif kind == "arrow":
            d.line([(cx0, cy0 + 16), (cx0 + 44, cy0 + 2)], fill=TEAL,
                   width=2)
            d.polygon([(cx0 + 44, cy0 + 2), (cx0 + 36, cy0 + 2),
                       (cx0 + 44, cy0 + 10)], fill=TEAL)
        elif kind == "gauge":
            d.arc([cx0, cy0, cx0 + 44, cy0 + 30], 180, 360, fill=MUTED,
                  width=3)
            d.arc([cx0, cy0, cx0 + 44, cy0 + 30], 180, 270, fill=RED,
                  width=3)
        else:  # flat
            d.line([(cx0, cy0 + 10), (cx0 + 44, cy0 + 10)], fill=MUTED,
                   width=2)
            d.ellipse([cx0 + 38, cy0 + 6, cx0 + 46, cy0 + 14], fill=RED)
        draw_lines(d, x + 8, fy + 38, lab.split("\n"), F(SANS, 10), MUTED,
                   leading=12)

    # ---- regions
    d.text((10, 644), "AROUND THE WORLD", font=F(SANS_B, 13), fill=INK)
    d.line([(10, 662), (W - 10, 662)], fill=GOLD, width=2)
    regions = [
        ("MIDDLE EAST", "Bahrain ablaze",
         "Iran claims two US bases hit."),
        ("EUROPE", "COP31 into overtime",
         "Spain extends bank levy; snap poll 29 Nov."),
        ("ASIA-PACIFIC", "Hong Kong votes",
         "856 vie for 723 seats; turnout 69.6%."),
        ("SOUTH ASIA", "Toxic alcohol kills 11",
         "180+ in hospital; 1 crore HPV jabs done."),
        ("AMERICAS", "Verstappen on pole",
         "Las Vegas GP runs; Florida floods record."),
        ("SPORT", "Pant powers India",
         "720/9 dec in Wellington; ATP final tonight."),
        ("MARKETS", "S&P's worst week",
         "Fed hike near-certain; oil near $93."),
    ]
    rw = 140
    for i, (name, head, body) in enumerate(regions):
        x = 10 + i * (rw + 6)
        d.text((x, 670), name, font=F(SANS_B, 10), fill=RED)
        y = 686
        y = draw_lines(d, x, y, fit_lines(head, F(SANS_B, 11), rw, 2),
                       F(SANS_B, 11), INK, leading=13)
        draw_lines(d, x, y + 2, fit_lines(body, F(SANS, 10), rw, 2),
                   F(SANS, 10), MUTED, leading=12)
        if i < 6:
            d.line([(x + rw + 3, 670), (x + rw + 3, 752)], fill=(200, 190,
                                                                165), width=1)

    # ---- grid: the day in brief
    d.text((10, 760), "THE DAY IN BRIEF", font=F(SANS_B, 13), fill=INK)
    d.line([(10, 778), (W - 10, 778)], fill=GOLD, width=2)
    grid = [
        ("ANTALYA", "COP31 package tabled; approval at 06:00 GMT."),
        ("KYIV", "148 drones, 3 missiles; 2 dead, 83 hurt."),
        ("MANAMA", "Iran hits industrial site; no injuries."),
        ("MUSCAT", "Two tankers hit off Hormuz; none hurt."),
        ("TEHRAN", "IRGC claims US bases hit; US denies F-16."),
        ("RIYADH", "Coalition stops 3 Houthi missiles."),
        ("HONG KONG", "856 vie for 723 seats; turnout 69.6%."),
        ("WELLINGTON", "India declare 720/9, a record total in NZ."),
        ("LAS VEGAS", "Verstappen on pole; GP under way 04:00 UTC."),
        ("TURIN", "Alcaraz v Zverev for the ATP Finals title."),
        ("IMPHAL", "Toxic alcohol kills 11; 180+ in hospital."),
        ("NEW DELHI", "India passes 1 crore HPV vaccine doses."),
        ("MADRID", "Spain extends bank levy; snap poll 29 Nov."),
        ("COCOA", "St Johns River breaks 73-year flood record."),
        ("MINNA", "Gunmen kill chief and four in Niger State."),
        ("DHAKA", "90 guard platoons deployed as arson flares."),
        ("SEOUL", "SoftBank's Son weighed $1tn SK Hynix deal."),
        ("NEW YORK", "S&P suffers worst week since April 2025."),
        ("WASHINGTON", "Fed hike near-certain for Dec; oil near $93."),
        ("LONDON", "Blair: rejoin EU only if UK innovates on tech."),
        ("WARSAW", "Rutte: NATO will defend every inch of Poland."),
        ("BOURNEMOUTH", "Evanilson scores in a sixth straight game."),
        ("MOSCOW", "Russia revives pre-2022 NATO rollback demands."),
        ("COVENTRY", "McNeil own goal gives Coventry 3-2 win."),
    ]
    gw, gh = 248, 28
    for i, (place, txt) in enumerate(grid):
        col, row = i % 4, i // 4
        x = 10 + col * (gw + 4)
        y = 786 + row * gh
        pf, tf = F(SANS_B, 10), F(SANS, 10)
        one_line = place + "  " + txt
        if pf.getlength(place) + 5 + tf.getlength(txt) <= gw:
            d.text((x, y), place, font=pf, fill=RED)
            d.text((x + pf.getlength(place) + 5, y), txt, font=tf, fill=INK)
        else:
            # two lines, decided before anything is drawn: no erasing
            d.text((x, y), place + " —", font=pf, fill=RED)
            draw_lines(d, x, y + 12, fit_lines(txt, tf, gw, 1), tf, INK,
                       leading=12)

    # ---- ticker
    d.rectangle([0, 952, W, 976], fill=BLACK)
    tick = ("ALSO TODAY  ·  Alcaraz v Zverev in Turin tonight"
            "  ·  Spain votes 29 Nov  ·  Fed decision looms in Dec")
    tf2 = F(SANS_B, 11)
    d.text(((W - tf2.getlength(tick)) / 2, 959), tick, font=tf2, fill=WHITE)

    # ---- footer
    src = ("SOURCES: REUTERS  ·  AP  ·  KYIV INDEPENDENT  ·  UKRAINE MONITOR"
           "  ·  CHINA DAILY  ·  BBC  ·  AL JAZEERA  ·  SUPERSPORT"
           "  ·  CAREERINDIA  ·  FREE MALAYSIA TODAY")
    sf = F(SANS, 9)
    d.text(((W - sf.getlength(src)) / 2, 984), src, font=sf, fill=MUTED)
    foot = "THE DAILY GLOBE  ·  SUNDAY 22 NOVEMBER 2026  ·  45 STORIES FROM 10 NEWSROOMS  ·  DRAWN, NOT PHOTOGRAPHED"
    ff = F(SANS_B, 10)
    d.text(((W - ff.getlength(foot)) / 2, 1000), foot, font=ff, fill=INK)

    # ---- paper grain (seeded, faint)
    grain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grain)
    for _ in range(9000):
        gx = rng.randint(0, W - 1)
        gy = rng.randint(0, H - 1)
        gd.point((gx, gy), fill=(120, 100, 60, 14))
    img = Image.alpha_composite(img.convert("RGBA"), grain).convert("RGB")
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or HERE
    out_path = os.path.join(outdir, OUT_NAME)
    if HAVE_PIL:
        os.makedirs(outdir, exist_ok=True)
        img = build()
        img.save(out_path, format="PNG", optimize=True)
        return 0
    # No PIL in this container: ship the pre-rendered image instead.
    src = os.path.join(HERE, OUT_NAME)
    if not os.path.exists(src):
        print("PIL is not available and no pre-rendered entry.png exists",
              file=sys.stderr)
        return 1
    if os.path.abspath(src) != os.path.abspath(out_path):
        os.makedirs(outdir, exist_ok=True)
        shutil.copyfile(src, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
