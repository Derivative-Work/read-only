"""The detail pass (M4; the human's note: "pretty much all of the scenes need more detail"). The final look only.

Each area is its own module with build(S) (set dressing, called at the end of block.build()) or build(S, SP) (the gag
props, called after shots.stage(), since they dress objects the shots make):
  city       the world around the block: the night sky's city glow, the blocks and streets beyond, the rooftops
  street     street furniture, parked cars, markings, street trees, the tower's plaza
  interiors  the Dev's shop, the eatery, the pawn shop, the other shops, the tower's lobby
  parkdress  the pocket park and the cemetery
  props      the gags' props, modelled (the shots' grey-box boxes take the models' meshes; their keys stay)

DETAIL_ONLY=city,street (environment) builds only those areas: for test stills of one area.
"""
import importlib
import os

SET = ("city", "street", "interiors", "parkdress")
STAGED = ("props",)


def sky(world):
    """The city glow in the night sky (city.sky), called by shots.light() once it has made the world."""
    only = os.environ.get("DETAIL_ONLY")
    if not only or "city" in only.split(","):
        importlib.import_module("city").sky(world)


def run(names, *args):
    only = os.environ.get("DETAIL_ONLY")
    for n in names:
        if only and n not in only.split(","):
            continue
        importlib.import_module(n).build(*args)
