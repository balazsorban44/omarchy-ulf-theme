# AGENTS.md

Working notes for changing these themes. The README is deliberately thin; this
is where the reasoning lives.

`ulf` (dark) and `ulf-light` are two repos, one theme each, because
`omarchy theme install` maps a repo to exactly one theme — it clones the repo
root into `~/.config/omarchy/themes/<name>`, where `<name>` is the repo name
with `omarchy-` and `-theme` stripped. Keep the theme at the root.

## The palette is searched, not chosen

Every chromatic slot sits in OKLCH hue **22–108**, so hue separates almost
nothing. Lightness and chroma carry every distinction, which makes slot
placement a constraint-satisfaction problem. **Do not hand-edit a colour** —
change the constraints in `tools/palette-search*.py` and re-run.

The search maximises the worst of **all 91 non-twin pairs**, scored as OKLab ΔE
under normal, protanopic and deuteranopic vision (Brettel/Viénot linear
approximations in `tools/palette.py`), subject to:

- bright twins need a lightness step ≥ 0.06 (same hue on purpose)
- `green` and `bright_green` pinned to hue 26–52, so they sit beside the accent
- `accent` `#ff5a36` pinned in both variants; dark also pins `yellow` `#ffb000`
- dark: every slot clears WCAG AA on the background except `brown` (3.20:1,
  decorative, held dark so it separates from red under protanopia)
- light: base ANSI slots clear AA, bright twins and decorative slots AA-large
- the **measured** hue is checked, not the requested one

Results: worst pair **0.0526** dark, **0.0423** light. Light scores lower
because AA on a near-white ground caps every slot below L≈0.55, compressing the
palette into rust and terracotta. The two variants share only the accent and
the hue band — the light palette is *not* the dark one recoloured.

Constraining all pairs rather than a hand-picked list matters: an earlier
hand-built palette had two interchangeable pairs (`orange`/`bright_red`,
`bright_green`/`bright_cyan`). Duplicate entries in a terminal palette are a
defect — `ls` colours and syntax highlighting silently lose a category.

### Gamut clipping will lie to you

Above L≈0.86 sRGB cannot hold a low-hue orange: the red channel saturates, the
colour clips toward peach and the hue drifts up. A search scoring the colour it
*asked for* rather than the one it *got* will happily place a "hue 45" slot that
renders at hue 74. That is why the light-slot hue check reads the produced sRGB
back. Same reason `bright_green` has a lightness ceiling.

### Things already tried that did not work

- **Light, contrast floor relaxed 4.5 → 4.0** (where flexoki-light and
  catppuccin-latte actually sit, to buy back vividness): scored **worse**,
  0.0344, and turned `red` into a brown-gold `#975d00`. Reverted.
- **Including `accent` in the all-pairs constraint**: drops the dark worst pair
  to 0.0472. Accent is UI chrome and never sits beside ANSI text, so it is
  excluded.
- **Hue as a fixed function of lightness** (darker = redder, lighter = golder).
  Elegant, but it cannot give a light slot an orange cast, so `green` came out
  gold. Hue is now free per slot within the band.

## Regenerating

Rendered by [Aether](https://github.com/omacom-io/aether) from
`source-colors.toml`, which it fetches over http:

```bash
cd <dir with source-colors.toml> && python3 -m http.server 8731 &
aether --handle-url 'aether://apply?colors=http://127.0.0.1:8731/source-colors.toml&as_omarchy_theme=ulf&silent=true'
tools/regenerate-patch.sh
```

`as_omarchy_theme` must match `[A-Za-z0-9][A-Za-z0-9_.-]*` — no spaces.

Aether owns every file it renders and overwrites them on each run, so all hand
corrections live in `tools/regenerate-patch.sh`, which is re-runnable and
idempotent. It exists mainly because Aether derives its own secondary accents:
it picks **ANSI blue** for window borders and magenta for mako/hyprlock/icons.
In these palettes blue is a near-neutral ash slot, so without the patch the
orange border comes out **grey**.

Three Aether behaviours to expect:

1. It sometimes reports success while writing a **stale** palette. Always read
   `colors.toml` back; do not trust its stdout. (Seen repeatedly.)
2. While its GUI is open it takes the Omarchy theme slot back — re-applying its
   own `aether` theme and repointing the background symlink into
   `~/.config/aether/theme/`. Close it before regenerating, and check
   `omarchy theme current` afterwards.
3. It may overwrite Chromium's seed colour with a neutral of its own.

## Light/dark is four separate signals

`omarchy theme set` touches none of them. `hooks/theme-set.d/gtk-appearance`
reads the active theme's `mode` and sets all four. Fixing one does not fix the
others:

| signal | read by |
|---|---|
| `gsettings color-scheme` | libadwaita, some GTK4 |
| `gsettings gtk-theme` | GTK3 |
| `gtk-{3,4}.0/gtk.css` | every GTK app — **overrides the two above** |
| `gtk-application-prefer-dark-theme` in `gtk-{3,4}.0/settings.ini` | Chromium's system-theme path only |

Each theme ships its own `gtk.css`; the hook swaps it on every theme change. A
stale one left from the other variant is exactly what makes apps render light
under a dark theme — and it beats both gsettings and the XDG portal, so it
looks like nothing you change has any effect.

Its `@blue`/`@cyan` references were repointed at `@accent`, because those slots
are near-neutrals here and GTK accents would otherwise render grey — the same
failure mode as the window border.

## Chromium

Chromium ignores all of the above for its own frame. Prefs live in
`~/.config/chromium/Default/Preferences` and must be written **while Chromium is
closed**, since it rewrites the file on exit.

| pref | value | why |
|---|---|---|
| `extensions.theme.system_theme` | `0` | Classic. Defaults to **GTK** on Linux, in which case Chromium draws its frame from the GTK theme and ignores its own colour prefs. This was the root cause of "Chromium won't go dark". |
| `browser.theme.user_color2` | `-42442` | SkColor `0xFFFF5A36` = `#ff5a36` |
| `browser.theme.color_variant2` | `3` | Vibrant; the default Tonal Spot deliberately desaturates the seed |
| `browser.theme.color_scheme2` | `0` | follow the system, so it tracks the theme switch |

Do **not** set `color_scheme2: 2` or `webkit.webprefs.force_dark_mode_enabled:
true` to force dark. Both break `prefers-color-scheme` for web content: the
first because Chromium ties the web media query to the browser colour scheme,
the second because it overrides every site regardless of what it asks for.

Chromium may replace `user_color2` with a neutral of its own; if the orange
drifts to grey, re-apply rather than assuming something else broke.

## Verifying changes

Environment-specific, but these cost real time to rediscover:

- **Check `omarchy theme current` first.** More than one "this is broken"
  symptom turned out to be the other variant being active, or Aether having
  stolen the slot.
- **kitty** does not pick up a new background from `omarchy restart terminal`
  alone; `pkill -USR1 -x kitty` reloads it.
- **`hyprctl dispatch`** takes Lua on Omarchy 4. Workspace switching is
  `hyprctl dispatch 'hl.dsp.focus({ workspace = "8" })'`; the bare
  `hyprctl dispatch "workspace 8"` form errors. Do not redirect the error away.
- **`grim`** captures the *active* workspace. Confirm the target window is on it
  before cropping, or you will measure the wrong window and believe it.
- Sample pixels rather than eyeballing screenshots — rendered-image perception
  is unreliable for near-black and near-white surfaces.
- zsh does not word-split unquoted expansions (`set -- $geo` keeps one arg), and
  `pkill -f <pattern>` will match the invoking shell if the pattern appears in
  its command line.
