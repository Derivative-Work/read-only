"""M4 detail pass: fetch the CC0 models that dress the set, from Poly Haven (as scripts/fetch_textures.py does for the
textures; the brief: "stylized Blender with CC0 textures").

For each asset: the 1k glTF (the .gltf, its .bin and its 1k JPG maps), checked against Poly Haven's MD5s, into
assets/models/<id>/ (git-ignored: re-fetchable). assets/models/sources.tsv (in git) records each file's URL, MD5 and
licence. Each one is looked at in a contact render before it goes on screen: no brand names or logos.

Usage: .venv/bin/python -I scripts/fetch_models.py [--sizes]   (--sizes: print each asset's download size only)
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ASSETS = {  # id: what it dresses
    # the street
    "fire_hydrant": "hydrants on the sidewalks", "metal_trash_can": "the street's bins", "trashbag": "bag piles",
    "water_manhole_cover": "manholes", "utility_box_01": "utility boxes", "utility_box_02": "utility boxes",
    "security_camera_01": "cameras on the tower (the recording theme)", "cardboard_box_01": "boxes, the shops' stock",
    "plastic_crate_01": "milk crates", "plastic_crate_02": "crates", "hand_truck": "S28's sidewalk auction",
    "old_tyre": "the lot", "modular_street_seating": "the tower's plaza seating", "street_lamp_02": "the park's lamp",
    # the Dev's shop (Third-Party App Repair)
    "steel_frame_shelves_01": "the Dev's stock shelves", "metal_office_desk": "the Dev's workbench",
    "tool_cart": "the Dev's tool cart", "metal_toolbox": "the bench", "retro_multimeter": "the bench",
    "circuit_board": "the bench", "classic_laptop": "the bench", "desk_lamp_arm_01": "the bench lamp",
    "wall_clock": "the Dev's shop and the eatery", "mounted_fluorescent_lights": "shop ceilings",
    "screwdrivers_02": "the bench", "pliers": "the bench", "vintage_stapler": "S09's eviction notice",
    "CashRegister_01": "the Dev's counter", "office_notepads": "the counter",
    # the eatery (turo-turo)
    "plastic_monobloc_chair_01": "the eatery's chairs", "ceiling_fan": "the eatery", "pot_enamel_01": "the eatery's pots",
    "Television_01": "the eatery's TV, the pawn shop", "potted_plant_01": "the eatery, the lobby",
    # the pawn shop and the other shops
    "Ukulele_01": "the pawn shop", "Camera_01": "the pawn shop", "vintage_video_camera": "the pawn shop",
    "gaming_console": "the pawn shop", "alarm_clock_01": "the pawn shop", "mantel_clock_01": "the pawn shop",
    "chess_set": "r/Chess, r/BoardGames", "wooden_display_shelves_01": "the shops' shelves",
    "steel_frame_shelves_02": "the shops' shelves", "brass_pan_01": "r/Cooking", "wooden_cutting_board": "r/Cooking",
    "hamburger_buns": "r/Sourdough", "croissant": "r/Sourdough", "wicker_basket_01": "r/Sourdough, r/Knitting",
    "wicker_basket_02": "r/Knitting, r/Crochet", "spinning_wheel_01": "r/Knitting", "potted_plant_02": "r/Gardening",
    "potted_plant_04": "r/Houseplants", "planter_box_01": "r/Gardening", "watering_can_metal_01": "r/Gardening",
    "hand_plane_no4": "r/Woodworking", "handsaw_wood": "r/Woodworking", "wooden_hammer_01": "r/Woodworking",
    "book_encyclopedia_set_01": "r/AskHistorians", "decorative_book_set_01": "r/AskHistorians",
    "marble_bust_01": "r/AskHistorians", "CoffeeCart_01": "r/Coffee", "tea_set_01": "r/Coffee",
    "rubber_boots": "r/Running's window",
    # the tower's lobby
    "modern_arm_chair_01": "the lobby", "modern_coffee_table_01": "the lobby", "sofa_03": "the lobby",
    # the gags
    "boombox": "S12's boombox on the curb", "magnifying_glass_01": "S13's magnifying glass",
    "Lantern_01": "the good bots' lanterns (S34, S37)", "rusted_spade_01": "S39e's shovel", "wooden_broom": "the mods' brooms",
    # the park
    "shrub_01": "the park", "shrub_02": "the park", "shrub_04": "the park", "tree_small_02": "the park, the street",
    "painted_wooden_bench": "the park", "grass_medium_01": "the park", "weed_plant_02": "the park, the cracks",
}
OUT = Path("assets/models")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "read-only-music-video/0.1 (model fetch)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def fetch(path, url, md5):
    if path.exists() and (md5 is None or hashlib.md5(path.read_bytes()).hexdigest() == md5):
        return
    b = get(url)
    assert md5 is None or hashlib.md5(b).hexdigest() == md5, (path, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b)


def main():
    sizes = "--sizes" in sys.argv
    rows = ["asset\tfile\turl\tmd5\tlicence\tuse"]
    total = 0
    for aid, use in ASSETS.items():
        files = json.loads(get(f"https://api.polyhaven.com/files/{aid}"))
        if "gltf" not in files:
            print(f"{aid:32s} no glTF; skipped")
            continue
        g = files["gltf"]["1k"]["gltf"]
        n = g["size"] + sum(f["size"] for f in g["include"].values())
        total += n
        if sizes:
            print(f"{aid:32s} {n / 1e6:7.1f} MB")
            continue
        d = OUT / aid
        fetch(d / f"{aid}.gltf", g["url"], g["md5"])
        rows.append(f"{aid}\t{d / (aid + '.gltf')}\t{g['url']}\t{g['md5']}\tCC0 (Poly Haven)\t{use}")
        for rel, f in g["include"].items():
            fetch(d / rel, f["url"], f["md5"])
            rows.append(f"{aid}\t{d / rel}\t{f['url']}\t{f['md5']}\tCC0 (Poly Haven)\t{use}")
        print(aid, "ok", flush=True)
    print(f"total {total / 1e6:.0f} MB")
    if not sizes:
        (OUT / "sources.tsv").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
