"""M8 recast: the approved Verse 4 keyframes (S41-S43) with another man in them, one per identity in config/recast.json
(the human, R1: "cuts rapidly between a number of different generated rappers of different ethnicities").

FLUX.2 [dev] reference editing as scripts/keyframes.py (its graph): reference 1 is the approved keyframe, reference 2
the identity's sheet. The sampler starts from the keyframe at partial denoise inside a feathered mask over the man's
head, neck and hands (SetLatentNoiseMask); outside it the keyframe's latent is kept, so the street, the light, the
pose and the costume stay the approved frame's. Outputs takes/keyframes/<shot>_<id>/<shot>_<id>_s<seed>.png and the
V size first frame (1280x704) beside it as <shot>_<id>_first.png; masks in takes/keyframes/recast_masks/; a review
grid per shot (takes/keyframes/review_<shot>_recast.png). One log row per generation.

Usage: .venv/bin/python scripts/recast.py [S41 S42 S43] [--ids b,c] [--seeds 2001] [--denoise 0.95]
       (ComfyUI must be running)
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import comfy_client as cc  # noqa: E402
from keyframes import graph  # noqa: E402
from stills import CFG as STILLS  # noqa: E402

CFG = json.load(open("config/recast.json"))
OUT = Path("takes/keyframes")
MASKS = OUT / "recast_masks"
PROMPTS = Path("log/prompts/keyframes")
LOG = Path("log/production_log.md")
V_SIZE = (1280, 704)


def mask(shot):
    spec = CFG["shots"][shot]
    p = MASKS / f"{shot}_mask.png"
    if not p.exists():
        MASKS.mkdir(parents=True, exist_ok=True)
        m = Image.new("L", tuple(CFG["size"]), 0)
        d = ImageDraw.Draw(m)
        for cx, cy, rx, ry in spec["ellipses"]:
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
        m.filter(ImageFilter.GaussianBlur(spec["feather"])).convert("RGB").save(p)
    return p


def review(shot, cells):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    tw = 480
    th = round(tw * CFG["size"][1] / CFG["size"][0])
    cols = 4
    rows = (len(cells) + cols - 1) // cols
    g = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 8) + 48), (16, 16, 18))
    d = ImageDraw.Draw(g)
    d.text((10, 10), f"{shot}: the recast (only head, neck and hands repainted)", fill=(255, 255, 255), font=font)
    for k, (label, p) in enumerate(cells):
        x, y = 8 + (k % cols) * (tw + 8), 40 + (k // cols) * (th + 8)
        g.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), label, fill=(255, 210, 0), font=font)
    out = OUT / f"review_{shot}_recast.png"
    g.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="*")
    ap.add_argument("--ids")
    ap.add_argument("--seeds")
    ap.add_argument("--denoise", type=float)
    a = ap.parse_args()
    shots = a.shots or list(CFG["shots"])
    ids = a.ids.split(",") if a.ids else [i for i in CFG["identities"] if i != "a"]
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else CFG["seeds"]
    dn = a.denoise if a.denoise is not None else CFG["denoise"]
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    w, h = CFG["size"]
    uploaded, rows = {}, []

    def up(p):
        if p not in uploaded:
            uploaded[p] = cc.upload_image(str(p))
        return uploaded[p]

    for shot in shots:
        spec = CFG["shots"][shot]
        mname = up(mask(shot))
        cells = [("a (approved)", spec["keyframe"])]
        for i in ids:
            ident = CFG["identities"][i]
            prompt = CFG["prompt"].format(desc=ident["desc"])
            stem = f"{shot}_{i}" + (f"_d{round(dn * 100)}" if a.denoise is not None else "")
            PROMPTS.mkdir(parents=True, exist_ok=True)
            for seed in seeds:
                dest = OUT / f"{shot}_{i}" / f"{stem}_s{seed}.png"
                if not dest.exists():
                    (PROMPTS / f"{stem}.txt").write_text(prompt + "\n")
                    names = [up(spec["keyframe"]), up(ident["sheet"])]
                    outputs, secs = cc.run(graph(prompt, names, seed, w, h, f"readonly/recast_{stem}_s{seed}", dn,
                                                 mname))
                    cc.download(outputs["9"]["images"][0], dest)
                    Image.open(dest).convert("RGB").resize(V_SIZE, Image.LANCZOS).save(
                        dest.with_name(f"{stem}_s{seed}_first.png"))
                    rows.append((stem, seed, dn, f"{spec['keyframe']}, {ident['sheet']}", str(dest), round(secs, 1)))
                    print(f"{stem} seed {seed}: {dest} ({secs:.1f} s)", flush=True)
                cells.append((f"{i} s{seed}", dest))
        print("review:", review(shot, cells), flush=True)
    if rows:
        m = STILLS["model"]
        with open(LOG, "a") as f:
            f.write(f"\n## {started} — M8: recast keyframes ({', '.join(shots)}; {', '.join(ids)})\n\n"
                    f"- **Model:** FLUX.2 [dev] `{m['unet']}`; {m['steps']} steps, guidance {m['guidance']}; reference "
                    f"editing from the approved keyframe inside a feathered mask (`takes/keyframes/recast_masks/`), "
                    f"{w}×{h}.\n"
                    f"- **Prompts:** `log/prompts/keyframes/<shot>_<id>.txt`. **Command:** `.venv/bin/python "
                    f"scripts/recast.py {' '.join(sys.argv[1:])}`\n\n"
                    f"| Shot | Seed | Denoise | Inputs | Output | Seconds | Status |\n"
                    f"| --- | --- | --- | --- | --- | --- | --- |\n")
            for stem, seed, d, refs, dest, secs in rows:
                f.write(f"| {stem} | {seed} | {d} | {refs} | `{dest}` | {secs} | pending (R1) |\n")


if __name__ == "__main__":
    main()
