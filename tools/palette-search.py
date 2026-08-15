#!/usr/bin/env python3
"""Pack 14 chromatic slots into a single orange hue band.

Hue is not a free variable: it is a fixed function of lightness, so the whole
palette rotates rust -> gold as it lightens. That leaves lightness and chroma
to carry every distinction, which is a constraint-satisfaction problem rather
than something to eyeball. Randomised search maximises the worst critical pair.
"""
import math, random, importlib.util, io, contextlib

spec = importlib.util.spec_from_file_location("p", "palette.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)

random.seed(20260815)

L_LO, L_HI = 0.50, 0.975
H_LO, H_HI = 22.0, 100.0


# Hue used to be a strict function of lightness (darker = redder). That rule
# cannot give a light slot an orange cast, so hue is now a free per-slot
# parameter inside the band, with green pinned near the accent by request.
ACCENT_H = 33.9
HUE_RANGE = {"green": (26.0, 52.0), "bright_green": (26.0, 52.0)}


def hue_window(name):
    return HUE_RANGE.get(name, (H_LO, H_HI))


YELLOW = (0xff, 0xb0, 0x00)   # site --updated, pinned
ACCENT = (0xff, 0x5a, 0x36)   # site --accent, pinned

# slot -> (chroma tier, lightness search window)
HOT, ASH, EARTH = "hot", "ash", "earth"
SLOTS = {
    "red":            (HOT, 0.50, 0.66),
    "bright_red":     (HOT, 0.60, 0.76),
    "magenta":        (HOT, 0.64, 0.82),
    "bright_magenta": (HOT, 0.70, 0.88),
    "bright_yellow":  (HOT, 0.84, 0.94),
    "green":          (HOT, 0.62, 0.90),
    "bright_green":   (HOT, 0.70, 0.88),
    "blue":           (ASH, 0.50, 0.68),
    "bright_blue":    (ASH, 0.60, 0.80),
    "cyan":           (ASH, 0.70, 0.88),
    "bright_cyan":    (ASH, 0.80, 0.95),
    "orange":         (HOT, 0.62, 0.80),
    "brown":          (EARTH, 0.44, 0.58),
}
C_RANGE = {HOT: (0.115, 0.215), ASH: (0.025, 0.085), EARTH: (0.06, 0.13)}

CHROMATIC = list(SLOTS) + ["yellow"]  # accent is UI chrome, never sits beside ANSI text
TWINS = [("red", "bright_red"), ("yellow", "bright_yellow"), ("green", "bright_green"),
         ("blue", "bright_blue"), ("cyan", "bright_cyan"), ("magenta", "bright_magenta")]
_tw = {frozenset(t) for t in TWINS}
# every pair that is not a bright twin must be tellable apart; a terminal palette
# with two interchangeable entries is a defect, not a stylistic choice
CRITICAL = [(a, b) for i, a in enumerate(CHROMATIC) for b in CHROMATIC[i + 1:]
            if frozenset((a, b)) not in _tw]
BG = (0x0d, 0x0b, 0x09)
# brown is decorative; everything else must clear AA as text
NEEDS_AA = set(SLOTS) - {"brown"}


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
    out = {"yellow": YELLOW, "accent": ACCENT}
    for name, (L, C, H) in params.items():
        out[name] = m.oklch_to_srgb(L, C, H)
    return out


def score(params):
    cols = build(params)
    # hard constraints first
    for a, b in TWINS:
        la = m.srgb_to_oklab(cols[a])[0]
        lb = m.srgb_to_oklab(cols[b])[0]
        if lb - la < 0.06:
            return -1, None
    for n in NEEDS_AA:
        if wcag(cols[n], BG) < 4.5:
            return -1, None
    if m.srgb_to_oklab(cols["red"])[1] ** 2 + m.srgb_to_oklab(cols["red"])[2] ** 2 < 0.145 ** 2:
        return -1, None
    # sRGB cannot hold a low-hue orange above L~0.86 - it clips toward peach and
    # the hue drifts up. Check the hue that actually came out, not the request.
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

# hill-climb the winner
step = 0.05
for _ in range(400000):
    p = {k: (max(SLOTS[k][1], min(SLOTS[k][2], v[0] + random.gauss(0, 0.012 * step * 20))),
             max(C_RANGE[SLOTS[k][0]][0], min(C_RANGE[SLOTS[k][0]][1],
                 v[1] + random.gauss(0, 0.008 * step * 20))),
             max(hue_window(k)[0], min(hue_window(k)[1],
                 v[2] + random.gauss(0, 2.5 * step * 20))))
         for k, v in best_p.items()}
    s, _ = score(p)
    if s > best:
        best, best_p = s, p

final, cols = score(best_p)
print(f"worst critical pair dE = {final:.4f}\n")
order = sorted(cols, key=lambda n: m.srgb_to_oklab(cols[n])[0])
for n in order:
    lab = m.srgb_to_oklab(cols[n])
    ch = math.hypot(lab[1], lab[2])
    hu = math.degrees(math.atan2(lab[2], lab[1])) % 360
    print(f'  {n:16s} "{m.hexs(cols[n])}"  L={lab[0]:.3f} C={ch:.3f} h={hu:5.1f}  '
          f'wcag={wcag(cols[n], BG):5.2f}')

print("\nworst pairs")
rows = []
for a, b in CRITICAL:
    d = min(m.de(cols[a], cols[b]),
            m.de(m.cvd(cols[a], "protan"), m.cvd(cols[b], "protan")),
            m.de(m.cvd(cols[a], "deutan"), m.cvd(cols[b], "deutan")))
    rows.append((d, a, b))
for d, a, b in sorted(rows)[:8]:
    print(f"  {a}/{b}".ljust(34) + f"{d:.4f}")
