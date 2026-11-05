"""Stills at 3x the final size (5760x3240), in the final look, without motion blur, for thumbnails (a tight crop of a
1080p frame is too soft: the good bot in S39a is about 300 px wide there).

Usage: blender -b --factory-startup --python scenes/blender/stills3x.py -- OUT_DIR FRAME [FRAME ...]
       ->  OUT_DIR/s_<video frame>.png
"""
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "lib"), str(HERE / "sets"), str(HERE)]
import animatic  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
out, frames = Path(argv[0]), [int(x) for x in argv[1:]]
out.mkdir(parents=True, exist_ok=True)
sc, SP = animatic.build((5760, 3240), 64, "final", 1)
sc.render.use_motion_blur = False
sc.render.image_settings.file_format = "PNG"
for f in frames:
    sc.frame_set(f)
    sc.render.filepath = str(out / f"s_{f:05d}.png")
    bpy.ops.render.render(write_still=True)
