# Shared by cameras.py, idmap.py, plan_map.py and house_mark.py (Blender headless). Nothing here saves the .blend.
import bpy, sys, re, math

# Material ID map groups: group -> (hex colour, what to tell the AI). First keyword match wins, so put specific words first.
GROUPS = {
    "glass":    ("#1e88e5", "window glass / mirror"),
    "frame":    ("#3949ab", "window and door frames, aluminium, steel doors"),
    "ceiling":  ("#4dd0e1", "ceiling"),
    "walltile": ("#f48fb1", "wall tiles"),
    "floor":    ("#fdd835", "floor tiles / floor finish"),
    "wall":     ("#e53935", "painted / plastered walls"),
    "roof":     ("#8e24aa", "roof, fascia, flashing"),
    "wood":     ("#43a047", "wood: furniture, cabinets, doors, slats"),
    "fabric":   ("#aed581", "fabric: sofa, bedding, curtains, rugs"),
    "sanitary": ("#fafafa", "ceramic: toilet, basin"),
    "stone":    ("#a1887f", "stone / granite counters"),
    "metal":    ("#616161", "metal and black fittings, appliances"),
    "plant":    ("#76ff03", "plants"),
    "lamp":     ("#fff59d", "lamps, light shades"),
    "ground":   ("#827717", "lawn, garden, ground"),
    "concrete": ("#fb8c00", "concrete: steps, columns, slabs, paving"),
    "other":    ("#9e9e9e", "everything else"),
}
KEYWORDS = {
    "glass": ["glass", "mirror"], "frame": ["alu", "door_steel", "frame", "trim"], "ceiling": ["ceiling"],
    "walltile": ["tile_p", "wall_tile", "tilewall"], "floor": ["tile_fl", "floor", "screed", "vinyl", "tilebed"],
    "wall": ["wall", "plaster", "paint", "primer", "brick", "smartboard"], "roof": ["roof", "fascia", "flashing", "metalsheet"],
    "wood": ["oak", "walnut", "teak", "wood", "rattan", "wpc", "plank"], "fabric": ["linen", "wool", "rug", "fabric", "sage", "cloth"],
    "sanitary": ["ceramic", "china", "porcelain"], "stone": ["stone", "granite", "marble"],
    "metal": ["chrome", "stainless", "steel", "metal", "black", "charcoal", "fitting", "valve", "device"],
    "plant": ["leaf", "plant", "foliage"], "lamp": ["lamp", "paper", "glow"], "ground": ["lawn", "grass", "sand", "ground"],
    "concrete": ["concrete"],
}


def group_of(name, user=None):
    """The ID map group of a material name: the user's groups.json keywords first, then the built-in table."""
    n = name.lower()
    for table in (user or {}, KEYWORDS):
        g = next((g for g, words in table.items() if any(w.lower() in n for w in words)), None)
        if g:
            return g
    return "other"


def cli():
    """Arguments after '--', an option reader, and the scene. Pick a scene with Blender's own -S NAME (before --python)."""
    a = sys.argv[sys.argv.index("--") + 1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    scene = bpy.context.scene
    if opt("--frame"):
        scene.frame_set(int(opt("--frame")))
    return a, opt, scene


def safe_id(i):
    """Ids become file names: plain names only, so nothing is written outside the output folder."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", str(i)):
        sys.exit(f"bad id {i!r}: use letters, digits, _ and - only")
    return i


def prepare(scene, size, engine):
    """Our frame whatever the user's file had: engine, size, no render region, VSE, compositor or transparent film."""
    r = scene.render
    if engine == "EEVEE":  # the file's engine may be Cycles at thousands of samples
        ids = [e.identifier for e in r.bl_rna.properties["engine"].enum_items]
        r.engine = next(e for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE") if e in ids)
        scene.eevee.taa_render_samples = 64
    else:
        r.engine = engine
    r.resolution_x, r.resolution_y = size
    r.resolution_percentage = 100
    r.use_border = r.use_sequencer = r.film_transparent = False
    r.pixel_aspect_x = r.pixel_aspect_y = 1
    if hasattr(r, "use_compositing"):
        r.use_compositing = False
    r.image_settings.file_format = 'PNG'
    return r


def level_camera(scene, c, prefix):
    """A level camera (verticals stay straight) at c['eye'] facing the plan point c['look']."""
    eye, (tx, ty) = c["eye"], c["look"]
    cd = bpy.data.cameras.new(prefix + c["id"])
    cd.lens, cd.shift_y, cd.clip_start = c.get("lens", 20), c.get("shift_y", 0), 0.05
    cam = bpy.data.objects.new(prefix + c["id"], cd)
    scene.collection.objects.link(cam)
    cam.location = eye
    cam.rotation_euler = (math.radians(90), 0, math.atan2(-(tx - eye[0]), ty - eye[1]))
    scene.camera = cam


def render(r, path):
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)
