# misc-fixed-ttf

X.Org `font-misc-misc` 1.1.3 BDFs converted by nixpkgs Bits'N'Picas to
monospaced, pixel-outline TrueType (not embedded bitmaps), usable by kitty.
Source: https://xorg.freedesktop.org/releases/individual/font/font-misc-misc-1.1.3.tar.xz
(pinned SHA-256 in `package.nix`). Upstream COPYING says **“Public domain font.
Share and enjoy.”**; `meta.license = lib.licenses.publicDomain`.

```sh
nix build
nix flake check
```

Installs 16 files to `$out/share/fonts/truetype/MiscFixed-<cell>-<style>.ttf`
and the upstream licence to `$out/share/doc/misc-fixed-ttf/COPYING`.
Families: `Misc Fixed 6x13`, `Misc Fixed 7x13`, `Misc Fixed 7x14`,
**`Misc Fixed 8x13`** (chosen terminal font), `Misc Fixed 9x15`,
`Misc Fixed 9x18`, `Misc Fixed 10x20`. All have Regular; all except 10x20
have Bold; 6x13, 7x13 and 8x13 also have Oblique. No synthesized styles.
Each style retains exactly its own upstream coverage; e.g. 8x13 has
3703/1141/1295 encoded glyphs in Regular/Bold/Oblique respectively. Bold
and Oblique therefore lack some characters present in Regular (including
some box drawing); this is an upstream limitation, not conversion loss.

## Declarative use

Add this flake as `inputs.misc-fixed-ttf` (with `inputs.nixpkgs.follows =
"nixpkgs"`), then either use `inputs.misc-fixed-ttf.packages.x86_64-linux.default`
or add `inputs.misc-fixed-ttf.overlays.default` to `nixpkgs.overlays`, exposing
`pkgs.misc-fixed-ttf`. In NixOS:

```nix
fonts.packages = [ pkgs.misc-fixed-ttf ];
```

In Home Manager: `home.packages = [ pkgs.misc-fixed-ttf ];` and
`fonts.fontconfig.enable = true;`. Kitty:

```conf
font_family Misc Fixed 8x13
bold_font auto
italic_font auto
bold_italic_font auto
font_size 9.75
```

At **96 DPI**, 9.75 pt = 13 px, the crisp native size (8 px advance).
Use integer multiples, or adjust for the actual display DPI/scale. If blurry,
try `text_composition_strategy legacy` before extra antialiasing tweaks.
FreeType autohinting can move isolated accent pixels even at native size;
for literal bitmap fidelity disable hinting for these families in Fontconfig
(e.g. `hinting=false`, `autohint=false`). No global rendering changes or
Fontconfig rules are installed by this package.

## Verification

Build-time checks assert every BDF codepoint survives, uniform advances,
outline tables, family and style flags. Metadata normalization follows the
provided manual rename script, also setting `post.isFixedPitch` (the converter
leaves it unset) and stable timestamps.

`fc-scan` reports the expected 16 family/style pairs and spacing=100. With an
isolated `FONTCONFIG_FILE` containing only this output, `kitty +runpy` lists
8x13 Regular/Bold/Oblique as `MONO`, scalable outlines.

To repeat the rendering and discovery checks, build the original PCFs:

```sh
nix build --impure --expr '(import (builtins.getFlake (toString ./.)).inputs.nixpkgs { system = "x86_64-linux"; }).xorg.fontmiscmisc' --out-link result-pcf
nix develop --command python verify.py
```

`.work/sample-8x13.png` is the Regular sample; per-style TTF/PCF samples,
Fontconfig and kitty reports are also in `.work/`. ImageMagick at 13 px,
`+antialias -set type:hinting off`, produces **zero differing pixels for all
three styles** on ASCII, Latin-1, Latin Extended and box-drawing samples
(filtered to each BDF's actual coverage). With default autohinting some
accent pixels shift; outlines themselves preserve the bitmap geometry.
The live kitty renderer/session was not started or modified.
