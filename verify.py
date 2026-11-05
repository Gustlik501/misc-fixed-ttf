"""Run inside `nix develop --command python verify.py`; touches only .work/.

Build the reference first:
nix build --impure --expr '(import (builtins.getFlake (toString ./.)).inputs.nixpkgs { system = "x86_64-linux"; }).xorg.fontmiscmisc' --out-link result-pcf
"""
import gzip
import os
from pathlib import Path
import subprocess
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parent
os.chdir(root)
work = root / ".work"
work.mkdir(exist_ok=True)
fonts = root / "result/share/fonts/truetype"
(work / "fonts.conf").write_text(f'''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig><dir>{fonts}</dir><cachedir>{work}/fontconfig-cache</cachedir></fontconfig>
''')
env = dict(os.environ, FONTCONFIG_FILE=str(work / "fonts.conf"))
scan = subprocess.check_output(["fc-scan", "--format", "%{family} | %{style} | spacing=%{spacing}\\n", *map(str, sorted(fonts.glob("*.ttf")))], env=env, text=True)
(work / "fc-scan.txt").write_text(scan)
print(scan)
kitty_code = '''from kitty.fonts.common import all_fonts_map
fs = all_fonts_map()["family_map"]["misc fixed 8x13"]
assert {f["style"] for f in fs} == {"Regular", "Bold", "Oblique"}
assert all(f["spacing"] == "MONO" and f["outline"] for f in fs)
for f in fs: print(f["family"], f["style"], f["spacing"])
'''
kitty = subprocess.check_output(["kitty", "+runpy", kitty_code], env=env, text=True)
(work / "kitty-8x13.txt").write_text(kitty)
print(kitty)
rows = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
    "ÀÁÂÃÄÅ ÆÇÈÉÊËÌÍÎÏ ÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß àáâãäå æçèéêëìíîï",
    "ĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚě ĞğİıŁłŒœŠšŸŽž",
    "┌────────┬────────┐ ╔════════╦════════╗ ░▒▓█ ←↑→↓ ±÷µ £¥©®",
    "│ fixed  │ 8 x 13 │ ║ tty    ║ pixels ║ !@#$%^&*()_+-=[]{}",
]
for style, source in (("Regular", "8x13"), ("Bold", "8x13B"), ("Oblique", "8x13O")):
    ttf = fonts / f"MiscFixed-8x13-{style}.ttf"
    cmap = TTFont(ttf).getBestCmap()
    # Bold and Oblique have less coverage upstream; do not invoke fallback.
    supported_rows = ["".join(c if ord(c) in cmap else " " for c in row) for row in rows]
    pcf = work / f"{source}.pcf"
    pcf.write_bytes(gzip.decompress((root / f"result-pcf/share/fonts/X11/misc/{source}.pcf.gz").read_bytes()))
    for kind, font in (("ttf", ttf), ("pcf", pcf)):
        args = ["magick", "-size", "720x100", "xc:white", "-fill", "black", "-font", str(font), "-density", "72", "-pointsize", "13", "+antialias", "-set", "type:hinting", "off"]
        for y, row in zip((18, 34, 50, 66, 82), supported_rows):
            args += ["-annotate", f"+8+{y}", row.replace("%", "%%")]
        subprocess.run([*args, str(work / f"sample-8x13-{style}-{kind}.png")], check=True)
    comparison = subprocess.run(["magick", "compare", "-metric", "AE", str(work / f"sample-8x13-{style}-ttf.png"), str(work / f"sample-8x13-{style}-pcf.png"), str(work / f"diff-{style}.png")], capture_output=True, text=True)
    print(f"{style}: {comparison.stderr.strip()} differing pixels")
    assert comparison.returncode == 0, comparison.stderr
(work / "sample-8x13.png").write_bytes((work / "sample-8x13-Regular-ttf.png").read_bytes())
