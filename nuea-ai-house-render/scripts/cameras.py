# Render each camera in cameras.json: the normal render (EEVEE, the model's own materials) or a clay pass.
# Cameras are created in memory only; the .blend is never saved.
#   blender -b -Y house.blend [-S SCENE] --python-exit-code 1 --python cameras.py -- <out_dir> <cameras.json> [--clay] [--percent 100] [--frame N] [--only id,id]
# cameras.json: [{"id": "living", "eye": [x, y, z], "look": [x, y], "lens": 18, "shift_y": 0}, ...]
#   eye = camera position in metres · look = the point on plan it faces · the camera is always LEVEL (verticals stay straight)
# Output: <id>.png (normal) or <id>_clay.png (--clay), 1080x1920 at --percent.
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import cli, safe_id, prepare, level_camera, render

args, opt, scene = cli()
OUT, CAMS = args[0], json.load(open(args[1], encoding="utf-8"))
CLAY, ONLY = "--clay" in args, set(opt("--only", "").split(",")) - {""}
for c in CAMS:
    safe_id(c["id"])
os.makedirs(OUT, exist_ok=True)

r = prepare(scene, (1080, 1920), "EEVEE")
r.resolution_percentage = int(opt("--percent", 100))
if CLAY:  # one matte warm-grey material over everything ("ดินน้ำมัน"); it covers window glass too, so sun-lit rooms render darker
    clay = bpy.data.materials.new("Clay"); clay.use_nodes = True
    b = next(n for n in clay.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.80, 0.77, 0.73, 1); b.inputs["Roughness"].default_value = 0.6
    for vl in scene.view_layers:
        vl.material_override = clay

for c in CAMS:
    if ONLY and c["id"] not in ONLY:
        continue
    level_camera(scene, c, "CAM_")
    render(r, os.path.join(OUT, f'{c["id"]}{"_clay" if CLAY else ""}.png'))
