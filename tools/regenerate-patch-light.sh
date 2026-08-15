#!/usr/bin/env bash
# Re-runnable patch over Aether's render of the "ulf-light" theme.
# Aether derives secondary accents (blue borders, magenta chrome) from the
# palette; omarchyplugins.com uses a single orange accent (#ff5a36) instead.
# Run this again after any `aether --handle-url ...as_omarchy_theme=ulf-light`.
set -euo pipefail

T="$HOME/.config/omarchy/themes/ulf-light"
[[ -d $T ]] || { echo "theme dir missing: $T" >&2; exit 1; }

ACCENT="ff5a36"   # --accent
AMBER="ffb000"    # --updated
LINE="e6ded8"     # lighter_background
LINE_SOFT="1c1c20"
MUTED="4d4642"
FAINT="9d9792"

# Hyprland window borders: accent orange, not Aether's blue.
cat >"$T/hyprland.conf" <<EOF
# This file is not a full hyprland configuration.
# It is intended to be included in your main hyprland.conf.

\$activeBorderColor = rgb($ACCENT)
\$inactiveBorderColor = rgb($LINE)

general {
    col.active_border = \$activeBorderColor
    col.inactive_border = \$inactiveBorderColor
}

group {
    col.border_active = \$activeBorderColor
    col.border_inactive = \$inactiveBorderColor
}
EOF

# hyprlock: orange ring, amber check state.
sed -i \
  -e "s/^\$outer_color = .*/\$outer_color = rgba(255, 90, 54, 1)/" \
  -e "s/^\$check_color = .*/\$check_color = rgba(255, 176, 0, 1)/" \
  "$T/hyprlock.conf"

# mako notifications: orange border.
sed -i "s/^border-color=.*/border-color=#$ACCENT/" "$T/mako.ini"

# swayosd: hairline border like the site's --line, orange progress.
cat >"$T/swayosd.css" <<EOF
@define-color background-color #faf6f3;
@define-color border-color #$LINE;
@define-color label #221c18;
@define-color image #221c18;
@define-color progress #$ACCENT;
EOF

# Icon theme: red-dark is the closest Yaru hue to the orange accent.
printf 'Yaru-red' >"$T/icons.theme"

# colors.toml: restore the site's own grey ramp over Aether's derived one.
sed -i \
  -e "s/^lighter_bg = .*/lighter_bg = \"#$LINE\"/" \
  -e "s/^dark_bg = .*/dark_bg = \"#f1ece8\"/" \
  -e "s/^darker_bg = .*/darker_bg = \"#e3dcd8\"/" \
  -e "s/^light_fg = .*/light_fg = \"#$MUTED\"/" \
  -e "s/^dark_fg = .*/dark_fg = \"#$FAINT\"/" \
  -e "s/^bright_fg = .*/bright_fg = \"#0f0a07\"/" \
  -e "s/^selection = .*/selection = \"#cfc1ba\"/" \
  -e "s/^selection_background = .*/selection_background = \"#$LINE\"/" \
  -e "s/^selection_foreground = .*/selection_foreground = \"#221c18\"/" \
  -e "s/^orange = .*/orange = \"#8c3e0a\"/" \
  -e "s/^brown = .*/brown = \"#684f35\"/" \
  "$T/colors.toml"

# Terminals: match the subtle grey selection instead of the inverted default.
python3 - "$T" "$LINE" <<'PY'
import pathlib, re, sys
t, line = pathlib.Path(sys.argv[1]), sys.argv[2]

a = t / "alacritty.toml"
s = a.read_text()
if "[colors.selection]" not in s:
    s = s.rstrip() + f'\n\n[colors.selection]\ntext = "#221c18"\nbackground = "#{line}"\n'
a.write_text(s)

f = t / "foot.ini"
s = f.read_text()
s = re.sub(r"^selection-foreground=.*$", "selection-foreground=221c18", s, flags=re.M)
s = re.sub(r"^selection-background=.*$", f"selection-background={line}", s, flags=re.M)
f.write_text(s)

k = t / "kitty.conf"
s = k.read_text()
if "selection_background" not in s:
    s = s.rstrip() + f"\nselection_foreground #221c18\nselection_background #{line}\n"
k.write_text(s)

g = t / "ghostty.conf"
s = g.read_text()
if "selection-background" not in s:
    s = s.rstrip() + f"\nselection-foreground = #221c18\nselection-background = #{line}\n"
g.write_text(s)
PY

echo "patched $T"
