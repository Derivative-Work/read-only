"""M8 recast: V for each identity's recast keyframe (scripts/recast.py), with the approved take's recipe: the same
control video, control type, guide and seed, and the approved prompt with the man's description swapped. So every
identity moves like the approved take and the edit's cuts between them match.

Outputs takes/v/<shot>_<id>/<shot>_<id>_s<seed>.mp4; prompts log/prompts/v/<shot>_<id>.txt; one log row each.

Usage: .venv/bin/python scripts/recast_v.py [S41 S42 S43] [--ids b,c] [--kseed 2001]   (ComfyUI must be running)
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

CFG = json.load(open("config/recast.json"))
LOG = Path("log/production_log.md")
APPROVED = {  # the approved takes' recipes (log: M5 S41, S42, S43 v4)
    "S41": {"control": "takes/v/S41/S41_depth.mp4", "type": "depth", "guide": 0.8, "seed": 2,
            "prompt": "log/prompts/v/S41_depth.txt", "man": "A man in a teal hoodie"},
    "S42": {"control": "takes/v/S42/S42_control.mp4", "type": "moge", "guide": 0.6, "seed": 2,
            "prompt": "log/prompts/v/S42_moge.txt", "man": "a real man with short black curly hair"},
    "S43": {"control": "takes/v/S43/S43_v4_control.mp4", "type": "moge", "guide": 0.6, "seed": 2,
            "prompt": "log/prompts/v/S43_moge_v4.txt", "man": "a real man with short black curly hair",
            # v2: the approved control (MoGe over the approved man's frame) put rings around the new heads; the
            # approved take's control was its own first frame pulled back, so each identity's is too
            "own_control": {"frames": 41, "zoom_to": 1 / 1.06}, "v": 2},
}


def own_control(first, out, spec):
    """The shot's pull-back from the identity's own first frame: frame 0 is the frame, zooming out linearly to
    zoom_to by the last, edges stretched (matches the approved S43_v4_control.mp4 to codec noise)."""
    import cv2
    import numpy as np
    img = cv2.imread(str(first))
    h, w = img.shape[:2]
    n = spec["frames"]
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                            "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for k in range(n):
        z = 1 - (1 - spec["zoom_to"]) * k / (n - 1)
        M = np.float32([[z, 0, w / 2 * (1 - z)], [0, z, h / 2 * (1 - z)]])
        enc.stdin.write(cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LANCZOS4,
                                       borderMode=cv2.BORDER_REPLICATE).tobytes())
    enc.stdin.close()
    enc.wait()


def bare(desc):
    return desc.split(" ", 1)[1]  # "an East Asian man ..." -> "East Asian man ..."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="*")
    ap.add_argument("--ids")
    ap.add_argument("--kseed", type=int, default=CFG["seeds"][0])
    a = ap.parse_args()
    shots = a.shots or list(APPROVED)
    ids = a.ids.split(",") if a.ids else [i for i in CFG["identities"] if i != "a"]
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    rows = []
    for shot in shots:
        r = APPROVED[shot]
        base = Path(r["prompt"]).read_text().strip()
        assert r["man"] in base, (shot, r["man"])
        for i in ids:
            desc = bare(CFG["identities"][i]["desc"])
            new = (f"A {desc}, in a teal hoodie" if shot == "S41" else f"a real {desc}")
            prompt = base.replace(r["man"], new)
            pf = Path("log/prompts/v") / f"{shot}_{i}.txt"
            pf.write_text(prompt + "\n")
            idn = CFG["identities"][i].get("denoise", CFG["denoise"])
            stem = f"{shot}_{i}" + (f"_d{round(idn * 100)}" if idn != CFG["denoise"] else "")
            first = Path("takes/keyframes") / f"{shot}_{i}" / f"{stem}_s{a.kseed}_first.png"
            vtag = f"_v{r['v']}" if r.get("v") else ""
            out = Path("takes/v") / f"{shot}_{i}" / f"{shot}_{i}{vtag}_s{r['seed']}.mp4"
            if out.exists():
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            control = r["control"]
            if r.get("own_control"):
                control = str(out.parent / f"{shot}_{i}_control.mp4")
                own_control(first, control, r["own_control"])
            res = subprocess.run([sys.executable, "scripts/ltx_v.py", control, str(first), str(out), "--prompt",
                                  prompt, "--seed", str(r["seed"]), "--control", r["type"], "--guide",
                                  str(r["guide"])], check=True, capture_output=True, text=True)
            info = json.loads(res.stdout.strip().splitlines()[-1])
            rows.append((shot, i, str(first), str(out), info.get("seconds")))
            print(shot, i, out, info.get("seconds"), flush=True)
    if rows:
        with open(LOG, "a") as f:
            f.write(f"\n## {started} — M8: recast V ({', '.join(shots)}; {', '.join(ids)})\n\n"
                    f"- **Recipe:** each approved take's (control, control type, guide, seed 2), the man's description "
                    f"swapped in its prompt (`log/prompts/v/<shot>_<id>.txt`). LTX-2.3 22B distilled fp8 + IC-LoRA "
                    f"union control, 1280×704. **Command:** `.venv/bin/python scripts/recast_v.py "
                    f"{' '.join(sys.argv[1:])}`\n\n"
                    f"| Shot | Identity | First frame | Output | Seconds | Status |\n| --- | --- | --- | --- | --- | --- |\n")
            for shot, i, first, out, secs in rows:
                f.write(f"| {shot} | {i} | `{first}` | `{out}` | {secs} | pending (R1) |\n")


if __name__ == "__main__":
    main()
