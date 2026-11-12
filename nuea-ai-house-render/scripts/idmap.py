# Material ID map: every surface becomes one flat colour per material group, plus a legend (colour -> what the surface is).
# The AI gets this next to the normal render, so it knows which surface is wall, floor, wood, fabric, glass...
# Never saves the .blend. Run headless:
#   blender -b -Y house.blend [-S SCENE] --python-exit-code 1 --python idmap.py -- <out_dir> <cameras.json> [--frame N]
# cameras.json: [{"id": "living", "eye": [x, y, z], "look": [x, y], "lens": 18, "shift_y": 0}, ...]
#   (same camera spec as cameras.py, so the ID map lines up pixel for pixel with the normal render)
# Optional groups.json next to cameras.json: {"wall": ["plaster", "paint"], ...}; its keywords win over the built-in
# table (GROUPS / KEYWORDS in _common.py). For a nuea-ai-blender-house model, house_mark.py drafts groups.json.
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import cli, safe_id, prepare, level_camera, render, GROUPS, group_of

args, opt, scene = cli()
OUT, CAMS = args[0], json.load(open(args[1], encoding="utf-8"))
for c in CAMS:
    safe_id(c["id"])
os.makedirs(OUT, exist_ok=True)

gpath = os.path.join(os.path.dirname(os.path.abspath(args[1])), "groups.json")
USER = json.load(open(gpath, encoding="utf-8")) if os.path.exists(gpath) else {}
if set(USER) - set(GROUPS):
    sys.exit(f"groups.json: unknown group {sorted(set(USER) - set(GROUPS))}; use one of {list(GROUPS)}")
if not all(isinstance(v, list) for v in USER.values()):
    sys.exit('groups.json: every value must be a list of words, e.g. {"wall": ["plaster"]}')

def rgb(hexs):  # sRGB hex -> linear float (Workbench + Standard view shows it back as the same hex)
    c = [int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]

# A surface without a material renders Blender's default light grey, which reads as white ceramic: give it "other".
OTHER = bpy.data.materials.new("ID_other")
for o in bpy.data.objects:
    if o.library is None and o.data is not None and o.data.library is None and hasattr(o.data, "materials"):
        if not o.material_slots:
            o.data.materials.append(OTHER)
        for sl in o.material_slots:
            if sl.material is None:
                sl.material = OTHER

# Materials as rendered: the evaluated instances (collection-instance furniture, geometry nodes) plus a plain scan,
# because the depsgraph here is the viewport one and skips objects hidden in viewports that still render
dg = bpy.context.evaluated_depsgraph_get()
used = {sl.material.original for inst in dg.object_instances if not inst.object.original.hide_render
        for sl in inst.object.material_slots if sl.material}
for o in scene.objects:
    if not o.hide_render:
        for x in [o, *(o.instance_collection.all_objects if o.instance_collection else [])]:
            used |= {sl.material for sl in x.material_slots if sl.material}
legend, missed = {}, []
for m in sorted(used, key=lambda m: m.name):
    g = "other" if m == OTHER else group_of(m.name, USER)
    try:
        m.diffuse_color = (*rgb(GROUPS[g][0]), 1.0)  # viewport colour only; never saved
    except (AttributeError, TypeError):  # linked from another .blend: read-only, keeps its own colour
        missed.append(m.name)
        continue
    legend.setdefault(g, {"color": GROUPS[g][0], "surface": GROUPS[g][1], "materials": []})["materials"].append(m.name)
if missed:
    legend["unrecoloured"] = {"color": None, "surface": "linked from another .blend: kept its own colour", "materials": missed}
    print("WARN materials linked from another file kept their own colour:", missed)

r = prepare(scene, (1080, 1920), 'BLENDER_WORKBENCH')
sh = scene.display.shading
sh.light, sh.color_type = 'FLAT', 'MATERIAL'
sh.show_shadows = sh.show_cavity = sh.show_object_outline = sh.show_specular_highlight = False
sh.background_type, sh.background_color = 'VIEWPORT', rgb("#202020")
vs = scene.view_settings  # exact hex out: no look, exposure, gamma, curves or dither from the user's file
vs.view_transform, vs.look, vs.exposure, vs.gamma, vs.use_curve_mapping = 'Standard', 'None', 0, 1, False
scene.display_settings.display_device = 'sRGB'
r.dither_intensity = 0
r.image_settings.color_depth = '8'
if hasattr(r.image_settings, "color_management"):
    r.image_settings.color_management = 'FOLLOW_SCENE'

for c in CAMS:
    level_camera(scene, c, "IDMAP_")
    render(r, os.path.join(OUT, f'{c["id"]}_idmap.png'))

json.dump(dict(sorted(legend.items())), open(os.path.join(OUT, "legend.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("LEGEND", {g: v["color"] for g, v in legend.items()})
