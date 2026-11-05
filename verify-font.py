"""Fail the build if conversion loses encoded glyphs, monospacing or styles."""
import sys
from fontTools.ttLib import TTFont

bdf, ttf, family, style = sys.argv[1:5]
encoded = set()
with open(bdf, encoding="ascii") as source:
    for line in source:
        if line.startswith("ENCODING "):
            codepoint = int(line.split()[1])
            if codepoint >= 0:
                encoded.add(codepoint)
font = TTFont(ttf)
cmap = font.getBestCmap()
missing = encoded - cmap.keys()
assert not missing, f"{bdf}: missing codepoints: {sorted(missing)}"
assert font["name"].getDebugName(1) == family
assert font["name"].getDebugName(2) == style
assert font["post"].isFixedPitch
assert len({font["hmtx"][glyph][0] for glyph in cmap.values()}) == 1
assert font["OS/2"].usWeightClass == (700 if style == "Bold" else 400)
assert bool(font["OS/2"].fsSelection & 1) == (style == "Oblique")
assert bool(font["head"].macStyle & 2) == (style == "Oblique")
assert "glyf" in font and "EBDT" not in font
print(f"verified {bdf}: {len(encoded)} encoded glyphs, monospaced {style} outlines")
