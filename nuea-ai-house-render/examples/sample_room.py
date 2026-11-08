# A small living room built from an empty Blender, to prove the scripts work before touching a real house.
# Writes <out_dir>/sample_room.blend, cameras.json and rooms.json (no AI credits involved).
#   blender -b --factory-startup --python-exit-code 1 -P sample_room.py -- <out_dir>
import bpy, sys, os, json, math

OUT = sys.argv[sys.argv.index("--") + 1]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = next(e for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE") if e in
                           [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items])

def mat(name, rgb, rough=0.6, glass=False, emit=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glass:
        b.inputs["Transmission Weight"].default_value = 1.0
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    return m

def box(name, size, loc, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name, o.scale = name, size; o.data.materials.append(m); return o

W, D, H = 4.0, 3.6, 2.7  # room inside: x 0..W, y 0..D, floor at z 0
wall, floor_, ceil = mat("Wall_Paint", (.92, .90, .86)), mat("Floor_Tile", (.85, .83, .80), .4), mat("Ceiling_Paint", (.95, .95, .95))
glass, frame = mat("Window_Glass", (.9, .95, 1.0), .05, glass=True), mat("Alu_Frame_Black", (.03, .03, .03), .4)
oak, linen, leaf = mat("Oak_Wood", (.55, .38, .22), .5), mat("Linen_Fabric", (.80, .76, .68), .9), mat("Plant_Leaf", (.15, .35, .12))
lamp = mat("Lamp_Paper", (1.0, .92, .75), emit=3)

box("Floor", (W, D, .1), (W / 2, D / 2, -.05), floor_)
box("Ceiling", (W, D, .1), (W / 2, D / 2, H + .05), ceil)
box("Wall_S", (W, .15, H), (W / 2, -.075, H / 2), wall)
box("Wall_E", (.15, D, H), (W + .075, D / 2, H / 2), wall)
box("Wall_W", (.15, D, H), (-.075, D / 2, H / 2), wall)
# north wall with a 1.6 x 1.2 m window
box("Wall_N_L", (1.2, .15, H), (.6, D + .075, H / 2), wall); box("Wall_N_R", (1.2, .15, H), (W - .6, D + .075, H / 2), wall)
box("Wall_N_Low", (1.6, .15, .9), (W / 2, D + .075, .45), wall); box("Wall_N_High", (1.6, .15, .6), (W / 2, D + .075, H - .3), wall)
box("Window_Glass", (1.6, .02, 1.2), (W / 2, D + .075, 1.5), glass)
for i, (sx, sz, x, z) in enumerate([(1.6, .05, W / 2, .925), (1.6, .05, W / 2, 2.075), (.05, 1.2, W / 2 - .8, 1.5), (.05, 1.2, W / 2 + .8, 1.5), (.04, 1.2, W / 2, 1.5)]):
    box(f"Window_Frame_{i}", (sx, .06, sz), (x, D + .075, z), frame)
# furniture as plain blocks: the AI turns them into real pieces
box("Sofa_Base", (2.1, .9, .45), (W / 2, D - .75, .225), linen); box("Sofa_Back", (2.1, .2, .45), (W / 2, D - .3, .65), linen)
box("Coffee_Table", (1.1, .6, .4), (W / 2, D - 1.75, .2), oak)
box("Rug", (2.4, 1.7, .01), (W / 2, D - 1.5, .005), linen)
bpy.ops.mesh.primitive_cylinder_add(radius=.18, depth=.4, location=(.45, D - .45, .2)); bpy.context.object.data.materials.append(oak)
bpy.ops.mesh.primitive_uv_sphere_add(radius=.35, location=(.45, D - .45, .75)); bpy.context.object.name = "Plant"; bpy.context.object.data.materials.append(leaf)
bpy.ops.mesh.primitive_cylinder_add(radius=.2, depth=.3, location=(W - .45, D - .45, 1.4)); bpy.context.object.name = "Lamp_Shade"; bpy.context.object.data.materials.append(lamp)

bpy.ops.object.light_add(type='SUN', location=(W / 2, D + 3, 4)); sun = bpy.context.object
sun.data.energy, sun.rotation_euler = 4, (math.radians(55), 0, math.radians(180))
bpy.ops.object.light_add(type='AREA', location=(W / 2, D / 2, H - .1)); bpy.context.object.data.energy = 250; bpy.context.object.data.size = 2
world = bpy.data.worlds.new("World"); world.use_nodes = True; scene.world = world
next(n for n in world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.6, .7, .85, 1)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "sample_room.blend"))
json.dump([{"id": "01_living", "eye": [W / 2, .35, 1.05], "look": [W / 2, D], "lens": 18}], open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
json.dump({"cut_z": 2.5, "rooms": [{"id": "01_living", "name": "ห้องนั่งเล่น", "rect": [0, W, 0, D]}]},
          open(os.path.join(OUT, "rooms.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("SAMPLE DONE", OUT)
