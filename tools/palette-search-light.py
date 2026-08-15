#!/usr/bin/env python3
"""Pack the ulf-light chromatic slots into the same orange hue band.

Light mode inverts the binding constraint. On a near-white background every
slot must be dark enough to read, so the whole palette is squeezed into a much
narrower lightness range than the dark variant had - which leaves chroma doing
most of the separating. Same method as palette-search.py: randomised search
plus hill-climbing, maximising the worst of all non-twin pairs under normal,
protanopic and deuteranopic vision.
"""
import math, random, importlib.util, io, contextlib

spec = importlib.util.spec_from_file_location("p", "palette.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)

random.seed(20260815)

H_LO, H_HI = 22.0, 108.0
BG = (0xfa, 0xf6, 0xf3)          # ulf-light background
ACCENT = (0xff, 0x5a, 0x36)      # kept from the dark theme by request

# green stays beside the accent, as in the dark variant
HUE_RANGE = {"green": (26.0, 52.0), "bright_green": (26.0, 52.0),
             "yellow": (68.0, 92.0), "bright_yellow": (68.0, 95.0)}


def hue_window(name):
    return HUE_RANGE.get(name, (H_LO, H_HI))


HOT, ASH, EARTH = "hot", "ash", "earth"
SLOTS = {
    "red":            (HOT, 0.34, 0.56),
    "bright_red":     (HOT, 0.40, 0.64),
    "magenta":        (HOT, 0.36, 0.62),
    "bright_magenta": (HOT, 0.42, 0.68),
    "yellow":         (HOT, 0.44, 0.64),
    "bright_yellow":  (HOT, 0.50, 0.70),
    "green":          (HOT, 0.34, 0.60),
    "bright_green":   (HOT, 0.40, 0.66),
    "blue":           (ASH, 0.30, 0.56),
    "bright_blue":    (ASH, 0.36, 0.62),
    "cyan":           (ASH, 0.34, 0.60),
    "bright_cyan":    (ASH, 0.40, 0.66),
    "orange":         (HOT, 0.40, 0.66),
    "brown":          (EARTH, 0.28, 0.50),
}
C_RANGE = {HOT: (0.10, 0.20), ASH: (0.020, 0.070), EARTH: (0.05, 0.12)}

CHROMATIC = list(SLOTS)
TWINS = [("red", "bright_red"), ("yellow", "bright_yellow"), ("green", "bright_green"),
         ("blue", "bright_blue"), ("cyan", "bright_cyan"), ("magenta", "bright_magenta")]
_tw = {frozenset(t) for t in TWINS}
CRITICAL = [(a, b) for i, a in enumerate(CHROMATIC) for b in CHROMATIC[i + 1:]
            if frozenset((a, b)) not in _tw]

# base ANSI slots carry meaning and must clear AA as body text; the bright
# twins and the decorative slots only owe AA-large.
NEEDS_AA = {"red", "green", "yellow", "blue", "magenta", "cyan"}
NEEDS_AA_LARGE = set(SLOTS) - NEEDS_AA


def wcag(a, b):
    def rl(rgb):
        def lin(c):
            c /= 255
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, bb = (lin(x) for x in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * bb
    x, y = sorted((rl(a), rl(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def build(params):
    out = {}
    for name, (L, C, H) in params.items():
        out[name] = m.oklch_to_srgb(L, C, H)
    return out


def score(params):
    cols = build(params)
    for a, b in TWINS:
        # on a light ground "bright" still means lighter, but not so light it
        # stops reading against the background - the AA-large floor covers that
        if m.srgb_to_oklab(cols[b])[0] - m.srgb_to_oklab(cols[a])[0] < 0.06:
            return -1, None
    for n in NEEDS_AA:
        if wcag(cols[n], BG) < 4.5:
            return -1, None
    for n in NEEDS_AA_LARGE:
        if wcag(cols[n], BG) < 3.0:
            return -1, None
    if m.srgb_to_oklab(cols["red"])[1] ** 2 + m.srgb_to_oklab(cols["red"])[2] ** 2 < 0.115 ** 2:
        return -1, None
    for name, (h_lo, h_hi) in HUE_RANGE.items():
        lab = m.srgb_to_oklab(cols[name])
        hu = math.degrees(math.atan2(lab[2], lab[1])) % 360
        if not (h_lo - 2 <= hu <= h_hi + 2):
            return -1, None
    worst = 9.0
    for a, b in CRITICAL:
        for kind in ("normal", "protan", "deutan"):
            f = (lambda c: c) if kind == "normal" else (lambda c: m.cvd(c, kind))
            worst = min(worst, m.de(f(cols[a]), f(cols[b])))
    return worst, cols


def sample():
    p = {}
    for name, (tier, lo, hi) in SLOTS.items():
        c_lo, c_hi = C_RANGE[tier]
        h_lo, h_hi = hue_window(name)
        p[name] = (random.uniform(lo, hi), random.uniform(c_lo, c_hi),
                   random.uniform(h_lo, h_hi))
    return p


best, best_p = -1, None
for _ in range(600000):
    p = sample()
    s, _ = score(p)
    if s > best:
        best, best_p = s, p

if best_p is None:
    raise SystemExit("no feasible palette - relax the constraints")

for _ in range(400000):
    p = {k: (max(SLOTS[k][1], min(SLOTS[k][2], v[0] + random.gauss(0, 0.012))),
             max(C_RANGE[SLOTS[k][0]][0], min(C_RANGE[SLOTS[k][0]][1],
                 v[1] + random.gauss(0, 0.008))),
             max(hue_window(k)[0], min(hue_window(k)[1], v[2] + random.gauss(0, 2.5))))
         for k, v in best_p.items()}
    s, _ = score(p)
    if s > best:
        best, best_p = s, p

final, cols = score(best_p)
print(f"worst critical pair dE = {final:.4f}\n")
for n in sorted(cols, key=lambda n: m.srgb_to_oklab(cols[n])[0]):
    lab = m.srgb_to_oklab(cols[n])
    ch = math.hypot(lab[1], lab[2])
    hu = math.degrees(math.atan2(lab[2], lab[1])) % 360
    print(f'  {n:16s} "{m.hexs(cols[n])}"  L={lab[0]:.3f} C={ch:.3f} h={hu:5.1f}  '
          f'wcag={wcag(cols[n], BG):5.2f}')
print(f'  {"accent":16s} "{m.hexs(ACCENT)}"  wcag={wcag(ACCENT, BG):5.2f}  (kept from ulf)')

print("\nworst pairs")
rows = [(min(m.de(cols[a], cols[b]),
             m.de(m.cvd(cols[a], "protan"), m.cvd(cols[b], "protan")),
             m.de(m.cvd(cols[a], "deutan"), m.cvd(cols[b], "deutan"))), a, b)
        for a, b in CRITICAL]
for d, a, b in sorted(rows)[:8]:
    print(f"  {a}/{b}".ljust(34) + f"{d:.4f}")
