"""M4: fetch the CC0 textures the style spec names, from Poly Haven (brief: "CC0 textures (Poly Haven, ambientCG)").

For each asset: the 1k JPG diffuse, OpenGL normal and roughness maps, checked against Poly Haven's MD5s, into
assets/textures/<id>/ (git-ignored: re-fetchable). assets/textures/sources.tsv (in git) records each file's URL, MD5
and licence. Usage: .venv/bin/python -I scripts/fetch_textures.py
"""
import hashlib
import json
import urllib.request
from pathlib import Path

ASSETS = {  # id: what it dresses (style/style_spec.md, "Materials")
    "asphalt_03": "the street",
    "concrete_pavement": "the sidewalks",
    "brick_4": "brick facades",
    "concrete_wall_003": "plastered facades, stained",
    "blue_plaster_weathered": "a weathered painted facade",
    "painted_metal_shutter": "the roll-down shutters",
    "plywood": "boarded windows (FOR LEASE)",
    "grass_ground": "the pocket park",
    "dry_ground_01": "the dug plots and the cemetery paths",
    "concrete": "headstones, the payphone post",
    "brown_floor_tiles": "the eatery's floor",
    "old_linoleum_flooring_01": "the Dev's shop floor",
}
MAPS = {"Diffuse": "diff", "nor_gl": "nor", "Rough": "rough"}
OUT = Path("assets/textures")


def get(url):
    # Poly Haven's API refuses urllib's default user agent (403); name the project instead
    req = urllib.request.Request(url, headers={"User-Agent": "read-only-music-video/0.1 (texture fetch)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    rows = ["asset\tmap\tfile\turl\tmd5\tlicence\tuse"]
    for aid, use in ASSETS.items():
        files = json.loads(get(f"https://api.polyhaven.com/files/{aid}"))
        d = OUT / aid
        d.mkdir(parents=True, exist_ok=True)
        for key, short in MAPS.items():
            f = files[key]["1k"]["jpg"]
            p = d / f"{short}.jpg"
            if not (p.exists() and hashlib.md5(p.read_bytes()).hexdigest() == f["md5"]):
                b = get(f["url"])
                assert hashlib.md5(b).hexdigest() == f["md5"], (aid, key)
                p.write_bytes(b)
            rows.append(f"{aid}\t{short}\t{p}\t{f['url']}\t{f['md5']}\tCC0 (Poly Haven)\t{use}")
        print(aid, "ok")
    (OUT / "sources.tsv").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
