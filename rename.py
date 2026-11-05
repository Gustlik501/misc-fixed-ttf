"""Normalize family/style metadata after Bits'N'Picas conversion."""
import sys
from fontTools.ttLib import TTFont

src, dst, family, style = sys.argv[1:5]
font = TTFont(src)
# Stable timestamps, independent of the build date.
font.recalcTimestamp = False
font["head"].created = font["head"].modified = 2082844800
name = font["name"]
full = family if style == "Regular" else f"{family} {style}"
ps = family.replace(" ", "") + "-" + style.replace(" ", "")
for nid in (1, 2, 3, 4, 6, 16, 17, 21, 22):
    name.removeNames(nameID=nid)
for nid, value in {1: family, 2: style, 3: ps, 4: full, 6: ps}.items():
    name.setName(value, nid, 3, 1, 0x409)
    name.setName(value, nid, 1, 0, 0)
os2, head = font["OS/2"], font["head"]
bold, italic = "Bold" in style, "Oblique" in style or "Italic" in style
os2.usWeightClass = 700 if bold else 400
selection = (1 if italic else 0) | (32 if bold else 0) | (64 if not (bold or italic) else 0)
os2.fsSelection = (os2.fsSelection & ~0b1100001) | selection
head.macStyle = (1 if bold else 0) | (2 if italic else 0)
# Bits'N'Picas leaves this unset even when every advance is identical.
font["post"].isFixedPitch = 1
font["post"].italicAngle = -12.0 if italic else 0.0
font.save(dst)
print(f"wrote {dst} -> {full}")
