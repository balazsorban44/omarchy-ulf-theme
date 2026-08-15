# ulf

![ulf](screenshots/ulf-dark.png)

## Install

```bash
omarchy theme install git@github.com:balazsorban44/omarchy-ulf-theme.git
```

Light variant: [balazsorban44/omarchy-ulf-light-theme](https://github.com/balazsorban44/omarchy-ulf-light-theme)

To make the desktop's light/dark setting follow the active theme, install the
hook once:

```bash
omarchy hook install theme-set hooks/theme-set.d/gtk-appearance
```

## Palette

Every colour sits in one warm hue band — no blue, no green, no magenta. The
ANSI names stay because they are positional, not descriptive.

| | dark | light |
|---|---|---|
| background | `#0d0b09` | `#faf6f3` |
| foreground | `#d7d3d0` | `#221c18` |
| accent | `#ff5a36` | `#ff5a36` |
| red | `#dc4506` | `#720000` |
| green | `#d57059` | `#7e2913` |
| yellow | `#ffb000` | `#8b6000` |
| blue | `#7d7969` | `#3c342b` |
| magenta | `#f06400` | `#ad4e44` |
| cyan | `#b7a993` | `#564241` |

Edit `source-colors.toml`, then run `tools/regenerate-patch.sh` after
re-rendering. See `AGENTS.md`.

## Credits

Palette from [omarchyplugins.com](https://omarchyplugins.com). Wallpaper from
[wallhaven](https://wallhaven.cc) (`3kx5gd`) — check its licence before
redistributing.
