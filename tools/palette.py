#!/usr/bin/env python3
"""Build the ulf palette in OKLCH and audit it for distinguishability.

Design rule: the warm family is allowed to be crowded in hue as long as every
adjacent pair separates on lightness; the semantically loaded pairs (ANSI
red/green/yellow/blue and their bright twins) must stay apart in normal vision
AND under protanopia/deuteranopia.
"""
import math

# ---------- OKLCH -> sRGB ----------

def oklch_to_srgb(L, C, h_deg):
    h = math.radians(h_deg)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(_encode(v) for v in (r, g, bl))


def _encode(v):
    v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return max(0, min(255, round(v * 255)))


def srgb_to_oklab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def hexs(rgb):
    return "#%02x%02x%02x" % rgb


def de(c1, c2):
    """OKLab dE, lightness weighted a little down so hue/chroma drive the score."""
    a, b = srgb_to_oklab(c1), srgb_to_oklab(c2)
    return math.hypot(math.hypot((a[0] - b[0]) * 0.8, a[1] - b[1]), a[2] - b[2])


# ---------- colour-vision simulation (Brettel/Vienot linear approximations) ----------

def cvd(rgb, kind):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    # linear sRGB -> LMS
    L = 0.31399022 * r + 0.63951294 * g + 0.04649755 * b
    M = 0.15537241 * r + 0.75789446 * g + 0.08670142 * b
    S = 0.01775239 * r + 0.10944209 * g + 0.87256922 * b
    if kind == "protan":
        L = 1.05118294 * M - 0.05116099 * S
    elif kind == "deutan":
        M = 0.9513092 * L + 0.04866992 * S
    r2 = 5.47221206 * L - 4.6419601 * M + 0.16963708 * S
    g2 = -1.1252419 * L + 2.29317094 * M - 0.1678952 * S
    b2 = 0.02980165 * L - 0.19318073 * M + 1.16364789 * S
    return tuple(_encode(v) for v in (r2, g2, b2))


# ---------- the palette ----------
# name: (L, C, h) in OKLCH, or a literal hex to pin a colour taken from the site.
# Monochrome orange: every chromatic slot sits in hue 25-98. Hue can no longer
# separate anything meaningfully, so each slot is placed on a lightness ladder
# and split into two chroma tiers - "hot" (C ~.17-.20) and "ash" (C ~.05-.06).
SPEC = {
    "accent":         "#ff5a36",
    # hot tier - the loud slots
    "red":            (0.560, 0.195, 25.0),
    "bright_red":     (0.645, 0.175, 28.0),
    "magenta":        (0.720, 0.190, 36.0),
    "bright_magenta": (0.755, 0.165, 42.0),
    "yellow":         "#ffb000",
    "bright_yellow":  (0.885, 0.150, 88.0),
    "green":          (0.940, 0.090, 98.0),
    "bright_green":   (0.975, 0.060, 98.0),
    # ash tier - low chroma, separated from the hot tier by chroma alone
    "blue":           (0.620, 0.055, 58.0),
    "bright_blue":    (0.710, 0.050, 58.0),
    "cyan":           (0.780, 0.060, 64.0),
    "bright_cyan":    (0.865, 0.050, 64.0),
    "orange":         (0.710, 0.180, 53.0),
    "brown":          (0.500, 0.100, 68.0),
    # neutrals
    "bg":             (0.150, 0.006, 60.0),
    "lighter_bg":     (0.280, 0.014, 55.0),
    "selection":      (0.370, 0.016, 48.0),
    "muted":          (0.590, 0.010, 60.0),
    "light_fg":       (0.720, 0.008, 60.0),
    "fg":             (0.870, 0.006, 60.0),
    "bright_fg":      (0.940, 0.005, 60.0),
}

TWINS = [("red", "bright_red"), ("yellow", "bright_yellow"), ("green", "bright_green"),
         ("blue", "bright_blue"), ("cyan", "bright_cyan"), ("magenta", "bright_magenta")]

RESOLVED = {}
for name, v in SPEC.items():
    if isinstance(v, str):
        RESOLVED[name] = tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
    else:
        RESOLVED[name] = oklch_to_srgb(*v)

BG = (0x0d, 0x0b, 0x09)

# Pairs that must never be confused, and the vision types they must survive.
CRITICAL = [
    # tier 1 - diff, errors, warnings, info. these must never blur.
    ("red", "green"), ("red", "yellow"), ("red", "blue"), ("green", "yellow"),
    ("green", "blue"), ("yellow", "blue"),
    # tier 2
    ("red", "magenta"), ("green", "cyan"), ("cyan", "blue"), ("magenta", "yellow"),
    ("magenta", "cyan"), ("magenta", "blue"),
    # brights against neighbouring bases
    ("bright_red", "magenta"), ("bright_magenta", "yellow"),
    ("bright_yellow", "green"), ("bright_cyan", "green"), ("bright_blue", "cyan"),
    ("bright_blue", "magenta"), ("bright_red", "blue"),
]
THRESHOLD = 0.055

print("palette")
for n, rgb in RESOLVED.items():
    lab = srgb_to_oklab(rgb)
    ch = math.hypot(lab[1], lab[2])
    hu = math.degrees(math.atan2(lab[2], lab[1])) % 360
    print(f"  {n:16s} {hexs(rgb)}  L={lab[0]:.3f} C={ch:.3f} h={hu:6.1f}")

print("\ncontrast on background #0b0b0d (WCAG)")


def wcag(rgb1, rgb2):
    def rl(rgb):
        def lin(c):
            c /= 255
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (lin(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    a, b = sorted((rl(rgb1), rl(rgb2)), reverse=True)
    return (a + 0.05) / (b + 0.05)


SURFACES = {"bg", "lighter_bg", "selection"}
for n, rgb in RESOLVED.items():
    if n in SURFACES:
        continue
    r = wcag(rgb, BG)
    print(f"  {n:16s} {r:5.2f}:1  {'AA ' if r >= 4.5 else 'FAIL (decorative)'}")

print("\ncritical pairs (dE >= %.3f required)" % THRESHOLD)
worst = []
for a, b in CRITICAL:
    row = [f"  {a}/{b}".ljust(28)]
    ok = True
    for kind in ("normal", "protan", "deutan"):
        ca = RESOLVED[a] if kind == "normal" else cvd(RESOLVED[a], kind)
        cb = RESOLVED[b] if kind == "normal" else cvd(RESOLVED[b], kind)
        d = de(ca, cb)
        ok &= d >= THRESHOLD
        row.append(f"{kind}={d:.3f}")
    row.append("OK" if ok else "<-- TOO CLOSE")
    if not ok:
        worst.append((a, b))
    print(" ".join(row))

print("\n%d critical pair(s) too close" % len(worst))

print("\nbright twins (same hue on purpose; need a lightness step >= 0.06)")
for a, b in TWINS:
    la, lb = srgb_to_oklab(RESOLVED[a])[0], srgb_to_oklab(RESOLVED[b])[0]
    d = abs(la - lb)
    print(f"  {a}/{b}".ljust(30) + f"dL={d:.3f} " + ("OK" if d >= 0.06 else "<-- FLAT"))
