"""A labelled 2-column contact sheet of the t_*.png stills in a directory (the look tests).
Usage: .venv/bin/python -I scripts/look_sheet.py <dir> <out.jpg> [label ...]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
d, out = Path(sys.argv[1]), sys.argv[2]
labels = sys.argv[3:]
fs = sorted(d.glob("t_*.png"))
w, h = 960, 540
font = ImageFont.truetype("assets/fonts/Inter-Medium-flat.ttf", 20)
sheet = Image.new("RGB", (2 * w, ((len(fs) + 1) // 2) * (h + 30)), "#111318")
for k, f in enumerate(fs):
    im = Image.open(f).convert("RGB").resize((w, h))
    x, y = (k % 2) * w, (k // 2) * (h + 30)
    sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text((x + 6, y + h + 4), labels[k] if k < len(labels) else f.stem, font=font, fill="#e8e8e8")
sheet.save(out, quality=90)
