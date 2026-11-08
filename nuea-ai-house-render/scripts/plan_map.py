# Top-view map for the walkthrough page: an orthographic section render from above + plan.js with every room
# rectangle and the walking path in 0..1 coordinates of that image. Never saves the .blend.
#   blender -b -Y house.blend [-S SCENE] --python-exit-code 1 --python plan_map.py -- <walkthrough_dir> <rooms.json> [--frame N]
# rooms.json (metres, plan coordinates):
#   {"cut_z": 2.4,        section height: everything above it (roof, ceilings, upper floor) is cut away; one floor per run
#    "rooms": [{"id": "02_living", "name": "ห้องนั่งเล่น", "rect": [x0, x1, y0, y1]}, ...],
#              in walkthrough order; id = the camera id (the page loads media/<id>.mp4, <id>_real.jpg, <id>_blender.jpg)
#              optional per room: "clip": false   on the map, dimmed and not clickable (a room with no clip)
#                                 "spot": [x, y]  where the point stops for a room off the walking path (e.g. a carport)
#                                 "at": n         index of the path point the room joins (default: the nearest one)
#    "path":  [[x, y], ...]}  optional walking route through the doors; default = centres of the clip rooms in order
# Writes <walkthrough_dir>/media/plan_top.png and <walkthrough_dir>/plan.js.
import bpy, sys, os, json
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import cli, safe_id, prepare, render

args, opt, scene = cli()
OUT, SPEC = args[0], json.load(open(args[1], encoding="utf-8"))
rooms = [{**r, "rect": sorted(r["rect"][:2]) + sorted(r["rect"][2:])} for r in SPEC["rooms"]]
for rm in rooms:
    safe_id(rm["id"])
os.makedirs(os.path.join(OUT, "media"), exist_ok=True)

xs = [v for rm in rooms for v in rm["rect"][:2]]; ys = [v for rm in rooms for v in rm["rect"][2:]]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
size = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.12  # square view with a small margin

cut = SPEC.get("cut_z", 2.4)
for o in scene.objects:  # whatever sits wholly above the cut casts no shadow on the plan either
    if o.type in {'MESH', 'CURVE'} and not o.hide_render:
        if min((o.matrix_world @ Vector(c)).z for c in o.bound_box) > cut:
            o.hide_render = True

# The camera sits at the cut and looks down: a true section, even when walls and roof are one joined mesh
cd = bpy.data.cameras.new("PLAN"); cd.type, cd.ortho_scale, cd.clip_start, cd.clip_end = 'ORTHO', size, 0.001, cut + 100
cam = bpy.data.objects.new("PLAN", cd); scene.collection.objects.link(cam)
cam.location, cam.rotation_euler = (cx, cy, cut), (0, 0, 0)
scene.camera = cam
r = prepare(scene, (1080, 1080), "EEVEE")
render(r, os.path.join(OUT, "media", "plan_top.png"))

uv = lambda x, y: [round(0.5 + (x - cx) / size, 4), round(0.5 - (y - cy) / size, 4)]
centre = lambda rm: ((rm["rect"][0] + rm["rect"][1]) / 2, (rm["rect"][2] + rm["rect"][3]) / 2)
name = lambda rm: rm.get("name", rm["id"])
tour = [rm for rm in rooms if rm.get("clip", True)]
path = SPEC.get("path") or [list(centre(rm)) for rm in tour]
entry = lambda rm: {"id": rm["id"], "key": rm["id"], "name": name(rm),
                    **({"spot": uv(*rm["spot"])} if "spot" in rm else {}), **({"at": rm["at"]} if "at" in rm else {})}
plan = {
    "path": [uv(*p) for p in path],
    "rooms": {rm["id"]: [uv(rm["rect"][0], rm["rect"][3]), uv(rm["rect"][1], rm["rect"][2])] for rm in rooms},  # top-left, bottom-right
    "list": [entry(rm) for rm in tour],
    "off": {rm["id"]: name(rm) for rm in rooms if not rm.get("clip", True)},
}
with open(os.path.join(OUT, "plan.js"), "w", encoding="utf-8") as f:
    f.write("// Written by plan_map.py: room rectangles and walking path in 0..1 coordinates of media/plan_top.png\n")
    f.write("window.PLAN = " + json.dumps(plan, ensure_ascii=False) + ";\n")
print("PLAN", len(tour), "rooms with clips ·", len(plan["off"]), "without ·", len(path), "path points")
