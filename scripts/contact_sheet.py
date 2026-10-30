"""Contact sheet of shot-anchor stills (M3 animatic, later renders): a grid with each shot's ID, start and cue.
From Not Yet's contact_sheet.py; it reads shot spans from scenes/blender/shots.py's order (pre-roll, song, post-roll)
via the anchor files present, and the cue from the timing map.

Usage: .venv/bin/python -I scripts/contact_sheet.py <dir with anchor_<ID>.png> <out.jpg> [columns] [ID ...]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAD, LABEL = 8, 40


def order():
    book = json.loads(Path("config/bookends.json").read_text())
    tm = json.loads(Path("timing/timing_map.json").read_text())
    cue = {s["id"]: (s["t"], s["cue"]) for s in tm["shots"]}
    ids = list(book["preroll"]) + [s["id"] for s in tm["shots"] if s["t"] is not None] + list(book["postroll"])
    seen = []
    for i in ids:
        if i not in seen:
            seen.append(i)
    return seen, cue


def main():
    src, out = Path(sys.argv[1]), sys.argv[2]
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    want = set(sys.argv[4:])
    ids, cue = order()
    ids = [i for i in ids if (src / f"anchor_{i}.png").exists() and (not want or i in want)]
    f_id = ImageFont.truetype("assets/fonts/JetBrainsMono-SemiBold-flat.ttf", 15)
    f_ln = ImageFont.truetype("assets/fonts/Inter-Medium-flat.ttf", 12)
    w, h = Image.open(src / f"anchor_{ids[0]}.png").size
    rows = (len(ids) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + PAD) + PAD, rows * (h + LABEL + PAD) + PAD), "#111318")
    d = ImageDraw.Draw(sheet)
    for k, i in enumerate(ids):
        x, y = PAD + (k % cols) * (w + PAD), PAD + (k // cols) * (h + LABEL + PAD)
        sheet.paste(Image.open(src / f"anchor_{i}.png").convert("RGB"), (x, y))
        t, c = cue.get(i, (None, ""))
        d.text((x, y + h + 3), f"{i}  {'' if t is None else f'{int(t // 60)}:{t % 60:05.2f}'}", font=f_id, fill="#9fe39a")
        d.text((x, y + h + 22), (c or "")[:74], font=f_ln, fill="#e8e4da")
    sheet.save(out, quality=86)
    print(out, len(ids), "stills")


if __name__ == "__main__":
    main()
