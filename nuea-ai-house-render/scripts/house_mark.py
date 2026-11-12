# Reads the nuea.ai channel's mark that the nuea-ai-blender-house skill leaves in a .blend (its collection names:
# "<PROJ> STnn <name>" stages, or "<PROJ> Walls" + "<PROJ> Openings") and drafts the two files that are otherwise
# written by hand:
#   rooms.json   room rectangles found from the walls, named after the furniture in them, ids = the camera ids
#   groups.json  ID map groups for materials the built-in table leaves as "other", from the build stage that uses them
# Never saves the .blend, never overwrites a file that exists (writes rooms.mark.json / groups.mark.json beside it).
#   blender -b -Y house.blend [-S SCENE] --python-exit-code 1 --python house_mark.py -- <project_dir> [<cameras.json>] [--floor Z]
#   blender -b --factory-startup --python-exit-code 1 --python house_mark.py -- --selftest
# A model without the mark prints "MARK none" and writes nothing: list the rooms and write both files by hand as before.
import bpy, bmesh, sys, os, re, json, math
from collections import deque
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import cli, safe_id, group_of

STAGE = re.compile(r"(?:^|\s)ST(\d{2})[a-z]?(?:\s|$)")
STAGE_GROUP = {**dict.fromkeys(("00", "01", "02", "03", "04", "05"), "concrete"), "06": "wall", "07": "roof",
               "08": "ceiling", "09": "wall", "10": "wall", "11": "floor", "12": "metal", "13": "wall", "14": "frame",
               "15": "wall", "16": "metal", "17": "sanitary"}
KINDS = [  # first match wins, so a bathroom with a cabinet is still a bathroom
    ("bath", "ห้องน้ำ", ("bath", "toilet", "wc", "basin", "shower", "lavatory")),
    ("kitchen", "ห้องครัว", ("kitchen", "stove", "hob", "oven", "fridge", "refrigerator", "hood")),
    ("bed", "ห้องนอน", ("bed", "wardrobe")),
    ("dining", "ห้องทานข้าว", ("dining",)),
    ("living", "ห้องนั่งเล่น", ("sofa", "couch", "armchair", "tv")),
    ("work", "ห้องทำงาน", ("desk",)),
    ("porch", "เฉลียง", ("porch", "terrace")),
]


def name_from_id(cid, count):
    """'05_bed1' → 'ห้องนอน 1': camera ids usually name their room. An id without a number names it only when the house
    has one room of that kind; otherwise the numbered furniture name stays, so two baths read ห้องน้ำ 1 and ห้องน้ำ 2."""
    m = re.search(r"(bath|kitchen|bed|dining|living|work|porch)(\d*)", cid.lower())
    if not m or (not m.group(2) and count.get(m.group(1), 0) > 1):
        return None
    return next(th for k, th, _ in KINDS if k == m.group(1)) + (f" {m.group(2)}" if m.group(2) else "")
CELL = 0.05                  # plan grid, m
CUTS = tuple(round(2.1 + 0.1 * k, 1) for k in range(10))  # m above the floor, 2.1..3.0: a wall at any cut closes the
#   gap, so a door or a tall window open at one height is closed by the lintel or wall above it at another
MIN_AREA, MIN_SIDE = 1.0, 0.6  # smaller spaces are wall cores or shafts, not rooms


def stages_of(scene):
    """collection -> its build stage 'nn'; a child collection inherits its parent's stage."""
    out = {}

    def walk(c, s):
        m = STAGE.search(c.name)
        s = m.group(1) if m else s
        if s:
            out[c] = s
        for ch in c.children:
            walk(ch, s)
    for c in scene.collection.children:
        walk(c, None)
    return out


def read_mark(scene):
    """(kind, wall objects, column objects, collection -> ID map group) · kind is 'construction', 'sales' or None."""
    st = stages_of(scene)
    if st:
        pick = lambda nn: {o for c, s in st.items() if s == nn for o in c.all_objects}
        return "construction", pick("06"), pick("05"), {c: STAGE_GROUP.get(s) for c, s in st.items()}
    cols = scene.collection.children_recursive
    walls = {c.name[:-len(" Walls")]: c for c in cols if c.name.endswith(" Walls")}
    opens = {c.name[:-len(" Openings")]: c for c in cols if c.name.endswith(" Openings")}
    proj = sorted(set(walls) & set(opens))
    if not proj:
        return None, set(), set(), {}
    return ("sales", {o for p in proj for o in walls[p].all_objects}, set(),
            {**{walls[p]: "wall" for p in proj}, **{opens[p]: "frame" for p in proj}})


def wall_segments(objs, dg, heights):
    """Plan segments where the objects' surfaces cross each height (world space, modifiers applied)."""
    segs = []
    for o in objs:
        if o.type != "MESH" or o.hide_render:
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        vs = [o.matrix_world @ v.co for v in me.vertices]
        for t in me.loop_triangles:
            p = [vs[i] for i in t.vertices]
            for h in heights:
                d = [q.z - h for q in p]
                x = [p[i].lerp(p[j], d[i] / (d[i] - d[j])) for i, j in ((0, 1), (1, 2), (2, 0)) if (d[i] < 0) != (d[j] < 0)]
                if len(x) == 2:
                    segs.append((x[0].x, x[0].y, x[1].x, x[1].y))
        ev.to_mesh_clear()
    return segs


def largest_rect(cells, nx):
    """The biggest axis-aligned rectangle of the room's cells (row histograms): an L-shaped room keeps its main part,
    so neighbouring rooms' rectangles never overlap on the map. Returns cell bounds [a, c) x [b, d)."""
    xs, ys = [c % nx for c in cells], [c // nx for c in cells]
    i0, j0, w = min(xs), min(ys), max(xs) - min(xs) + 1
    inside = {(c % nx - i0, c // nx - j0) for c in cells}
    best, hist = (0, 0, 0, 0, 0), [0] * w
    for j in range(max(ys) - j0 + 1):
        hist = [hist[i] + 1 if (i, j) in inside else 0 for i in range(w)]
        stack = []
        for i in range(w + 1):
            cur, start = (hist[i] if i < w else 0), i
            while stack and stack[-1][1] >= cur:
                start, hh = stack.pop()
                if hh * (i - start) > best[0]:
                    best = (hh * (i - start), start, j - hh + 1, i, j + 1)
            stack.append((start, cur))
    _, a, b, c, d = best
    return i0 + a, j0 + b, i0 + c, j0 + d


class Plan:
    """The walls rasterised on a CELL grid; spaces the outside can't reach are rooms."""

    def __init__(self, segs):
        xs = [v for s in segs for v in (s[0], s[2])]
        ys = [v for s in segs for v in (s[1], s[3])]
        self.x0, self.y0 = min(xs) - 1.0, min(ys) - 1.0  # 1 m margin: the border ring is outside and connected
        self.nx = int((max(xs) + 1.0 - self.x0) / CELL) + 1
        self.ny = int((max(ys) + 1.0 - self.y0) / CELL) + 1
        self.label = [0] * (self.nx * self.ny)  # 0 free · -1 wall · -2 outside · n room n
        for ax, ay, bx, by in segs:  # samples every half cell: the line is 8-connected, so a 4-connected fill can't cross it
            n = int(math.hypot(bx - ax, by - ay) / (CELL / 2)) + 1
            for k in range(n + 1):
                self.label[self.cell(ax + (bx - ax) * k / n, ay + (by - ay) * k / n)] = -1
        self.fill(0, -2)
        self.rooms = []
        for i in range(len(self.label)):
            if self.label[i] == 0:
                cells = self.fill(i, len(self.rooms) + 1)
                cx, cy = [c % self.nx for c in cells], [c // self.nx for c in cells]
                w, h, area = (max(cx) - min(cx) + 1) * CELL, (max(cy) - min(cy) + 1) * CELL, len(cells) * CELL * CELL
                a, b, c, d = largest_rect(cells, self.nx)
                rect = [self.x0 + a * CELL, self.x0 + c * CELL, self.y0 + b * CELL, self.y0 + d * CELL]
                # judged on the inscribed rectangle: the core of a wall that is one long mesh has a big bounding box
                keep = area >= MIN_AREA and min(c - a, d - b) * CELL >= MIN_SIDE
                self.rooms.append(dict(n=len(self.rooms) + 1, rect=[round(v, 2) for v in rect], area=round(area, 2),
                                       fill=round(area / (w * h), 2), keep=keep))

    def cell(self, x, y):
        i, j = int((x - self.x0) / CELL), int((y - self.y0) / CELL)
        return j * self.nx + i if 0 <= i < self.nx and 0 <= j < self.ny else None

    def label_at(self, x, y):
        c = self.cell(x, y)
        return self.label[c] if c is not None else -2  # beyond the grid is outside

    def room_at(self, x, y):
        n = self.label_at(x, y)
        return self.rooms[n - 1] if n > 0 and self.rooms[n - 1]["keep"] else None

    def fill(self, start, tag):
        out, q = [start], deque([start])
        self.label[start] = tag
        while q:
            c = q.popleft()
            i = c % self.nx
            for d in ((-1 if i > 0 else None), (1 if i < self.nx - 1 else None), -self.nx, self.nx):
                if d is not None and 0 <= c + d < len(self.label) and self.label[c + d] == 0:
                    self.label[c + d] = tag
                    out.append(c + d)
                    q.append(c + d)
        return out


def furniture(scene, colgroup, walls):
    """(kind, object name, x, y) for each furniture piece that names a room; build-stage parts are skipped except
    sanitary ware (ST17), so a tile bed called FT_bath_Bed is not a bed."""
    out = []
    for o in scene.objects:  # children too: fixtures often hang under one parent empty
        if o.hide_render or o in walls or not (o.type == "MESH" or (o.type == "EMPTY" and o.instance_collection)):
            continue
        if any(c in colgroup and colgroup[c] != "sanitary" for c in o.users_collection):
            continue
        text = " ".join(filter(None, (o.name, o.instance_collection and o.instance_collection.name,
                                      o.data and getattr(o.data, "name", None)))).lower()
        kind = next((k for k, _, words in KINDS if any(w in text for w in words)), None)
        if kind:
            p = sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector((0, 0, 0))) / 8 \
                if o.type == "MESH" else o.matrix_world.translation
            root = o
            while root.parent:
                root = root.parent
            label = root.name if root is not o and any(w in root.name.lower() for _, _, ws in KINDS for w in ws) else o.name
            out.append((kind, label, p.x, p.y))  # label: the piece of furniture (FUR_Living_Sofa), not its leg
    return out


def mark_groups(scene, colgroup):
    """Materials the built-in table calls 'other' → the group of the stage that holds most of the objects using them.
    A material used mostly outside the build stages (furniture, placed assets) stays 'other'. Returns (groups, skipped):
    idmap matches groups.json words as substrings, so a name that would also recolour another material is skipped."""
    votes, used = {}, set()
    users = [(o, next((colgroup[c] for c in o.users_collection if colgroup.get(c)), None)) for o in scene.objects
             if not o.hide_render]
    users += [(x, g) for o, g in users if o.type == "EMPTY" and o.instance_collection
              for x in o.instance_collection.all_objects]  # a placed asset votes for its placer's stage (None = furniture)
    for o, g in users:
        for sl in (o.material_slots if o.type == "MESH" else ()):
            m = sl.material
            if m and not m.library:
                used.add(m.name)
                if group_of(m.name) == "other" and not re.fullmatch(r"Material(\.\d+)?", m.name):
                    v = votes.setdefault(m.name, {})
                    v[g] = v.get(g, 0) + 1
    draft = {}
    for name, v in sorted(votes.items()):
        best = max(((g, n) for g, n in v.items() if g), key=lambda gn: gn[1], default=None)
        if best and best[1] * 2 > sum(v.values()):
            draft[name] = best[0]
    out, skipped = {}, []
    for name, g in draft.items():
        clash = next((m for m in sorted(used) if m != name and name.lower() in m.lower()
                      and draft.get(m, group_of(m)) != g), None)
        if clash:
            skipped.append((name, clash))
        else:
            out.setdefault(g, []).append(name)
    return out, skipped


def analyse(scene, cams, floor=None):
    kind, walls, columns, colgroup = read_mark(scene)
    res = dict(kind=kind, rooms=[], outside=[], shared=[], groups={}, cut_z=None, floor=None, notes=[])
    if not kind:
        return res
    res["groups"], skipped = mark_groups(scene, colgroup)
    res["notes"] += [f"GROUP skip {a}: as a groups.json word it would also recolour {b}" for a, b in skipped]
    vis = lambda objs: [o for o in objs if o.type == "MESH" and not o.hide_render]
    if not vis(walls):
        res["notes"].append("NO WALLS: the mark is there but no wall (ST06 / Walls) mesh renders; groups.json is still written")
        return res
    zs = lambda o: [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    # the floor is where most wall pieces start; columns and a few corner pieces start lower, on the footings
    fl = floor if floor is not None else sorted(min(zs(o)) for o in vis(walls))[len(vis(walls)) // 2]
    res["floor"] = round(fl, 3)
    walls = walls | columns  # columns close the gaps where walls stop at their faces
    segs = wall_segments(vis(walls), bpy.context.evaluated_depsgraph_get(), [fl + h for h in CUTS])
    if not segs:
        res["notes"].append(f"NO WALLS at z {fl + CUTS[0]:.2f}–{fl + CUTS[-1]:.2f}: check --floor (the walls may stop "
                            f"lower in an unfinished model); groups.json is still written")
        return res
    plan = Plan(segs)
    rooms = [r for r in plan.rooms if r["keep"]]
    for k, name, x, y in furniture(scene, colgroup, walls):
        r = plan.room_at(x, y)
        if r:
            r.setdefault("things", []).append((k, name))
    count = {}
    for r in sorted(rooms, key=lambda r: (-round((r["rect"][2] + r["rect"][3]) / 2), r["rect"][0])):
        kinds = {k for k, _ in r.get("things", [])}
        r["kind"], r["name"] = next(((k, th) for k, th, _ in KINDS if k in kinds), ("room", "ห้อง"))
        count[r["kind"]] = count.get(r["kind"], 0) + 1
        r["i"] = count[r["kind"]]
    for r in rooms:
        if count[r["kind"]] > 1 or r["kind"] == "room":
            r["name"] += f" {r['i']}"
    # cameras: one standing outside is outside, whatever it faces; else the room its look point falls in (look sets
    # only the direction, so it may lie anywhere), else the room it stands in
    by_room = {}
    for c in sorted(cams, key=lambda c: c["id"]):
        out = plan.label_at(*c["eye"][:2]) == -2
        r = None if out else plan.room_at(*c["look"][:2]) or plan.room_at(*c["eye"][:2])
        if r:
            by_room.setdefault(r["n"], []).append(c["id"])
        else:
            res["outside"].append(c["id"])
    order = sorted(rooms, key=lambda r: (by_room.get(r["n"], ["~"])[0], -r["rect"][2], r["rect"][0]))
    taken = {c["id"] for c in cams}
    for k, r in enumerate(order, 1):
        ids = by_room.get(r["n"])
        if ids and len(ids) > 1:
            res["shared"].append(ids)
        for cid in ids or [None]:
            n = 1 + max([int(m.group()) for i in taken if (m := re.match(r"\d+", i))], default=0)  # after the cameras
            rid = cid or next(i for i in (f"{n:02d}_{r['kind']}{'' if j == 0 else j}" for j in range(99)) if i not in taken)
            taken.add(rid)
            res["rooms"].append({"id": rid, "name": (cid and name_from_id(cid, count)) or r["name"], "rect": r["rect"],
                                 **({} if cid else {"clip": False}),
                                 "_area": r["area"], "_fill": r["fill"],
                                 "_things": list(dict.fromkeys(n for _, n in r.get("things", [])))[:6]})
    ceil = [min(zs(o)) for o in scene.objects if o.type == "MESH" and not o.hide_render
            and (any(colgroup.get(c) == "ceiling" for c in o.users_collection) or "ceiling" in o.name.lower())]
    ceil = [z for z in ceil if z > fl + 1.8]
    res["cut_z"] = round(min(ceil) - 0.05 if ceil else fl + 2.4, 2)
    return res


def write(path, data):
    if os.path.exists(path):
        try:
            if json.load(open(path, encoding="utf-8")) == data:
                print("UNCHANGED", path)
                return
        except (OSError, ValueError):
            pass  # unreadable or not JSON: leave it alone and write the draft beside it
        path = path[:-len(".json")] + ".mark.json"  # never overwrite what the user or Claude wrote
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("WROTE", path)


def report(res):
    if not res["kind"]:
        print("MARK none: not made with nuea-ai-blender-house; list the rooms and write rooms.json / groups.json by hand")
        return
    print(f"MARK {res['kind']} model from nuea-ai-blender-house · floor z={res['floor']} · cut_z={res['cut_z']}")
    for r in res["rooms"]:
        shape = "" if r["_fill"] >= 0.85 else " · L-shaped or irregular: rect is its biggest rectangle"
        cam = "" if r.get("clip", True) else " · no camera (clip false)"
        print(f"ROOM {r['id']} {r['name']} rect {r['rect']} {r['_area']} m2{shape}{cam} · {', '.join(r['_things']) or '-'}")
    for ids in res["shared"]:
        print(f"SHARED {' '.join(ids)}: one space, the same rectangle twice; split it at the line between the two views")
    for cid in res["outside"]:
        print(f"OUTSIDE {cid}: not inside a room (exterior, porch, carport); add it by hand with a \"spot\" if it has a clip")
    for g, ms in res["groups"].items():
        print(f"GROUP {g}: {', '.join(ms)}")
    for n in res["notes"]:
        print(n)


def selftest():
    """Two rooms 8 x 5 m: a bed room and a bath, a door in the wall between them, a window whose head reaches the
    first cut, a corner closed only by a column (ST05), a tile bed named like a bed, and stage materials."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc = bpy.context.scene
    cols = {}

    def col(name):
        if name not in cols:
            cols[name] = bpy.data.collections.new(name)
            sc.collection.children.link(cols[name])
        return cols[name]

    def obj(name, boxes, c, mat=None):
        bm = bmesh.new()
        for x0, y0, z0, x1, y1, z1 in boxes:
            g = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=g["verts"])
            bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=g["verts"])
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        if mat:
            me.materials.append(bpy.data.materials.get(mat) or bpy.data.materials.new(mat))
        o = bpy.data.objects.new(name, me)
        col(c).objects.link(o)
        return o

    t, W = 0.075, "T ST06 Walls"
    obj("WL_S", [(-t, -t, 0, 1, t, 3), (2, -t, 0, 8 + t, t, 3), (1, -t, 0, 2, t, 1.0), (1, -t, 2.3, 2, t, 3)], W, "M_Brick")
    obj("WL_N", [(-t, 5 - t, 0, 7.6, 5 + t, 3)], W)
    obj("WL_W", [(-t, t, 0, t, 5 - t, 3)], W)
    obj("WL_E", [(8 - t, t, 0, 8 + t, 4.8, 3)], W)
    obj("WL_Mid", [(4 - t, t, 0, 4 + t, 2, 3), (4 - t, 3, 0, 4 + t, 5 - t, 3), (4 - t, 2, 2.1, 4 + t, 3, 3)], W)
    obj("Str_Col_C4", [(7.6, 4.8, 0, 8 + t, 5 + t, 3)], "T ST05 Columns")  # a corner notch: the bath is not a rectangle
    obj("Ceiling_All", [(0, 0, 2.8, 8, 5, 2.81)], "T ST08 Ceiling", "M_Gypsum")
    obj("Door_D1", [(3.9, 2, 0, 4.1, 3, 2.1)], "T ST14 Doors Windows", "M_PVC_White")
    obj("FT_bath_Bed", [(5, 0.5, 0, 6, 1.5, 0.02)], "T ST11 Tiles", "M_TileAdhesive")
    obj("Bed_Double", [(1, 1.5, 0, 2.6, 3.5, 0.5)], "T Interior", "INT_white")
    obj("Toilet_01", [(6.5, 4, 0, 7, 4.6, 0.4)], "T ST17 Fixtures", "M_Ceramic_WC")
    obj("Switch_Box", [(0.08, 2, 1.2, 0.1, 2.1, 1.3)], "T ST12 Electrical", "M_Box")        # M_Box is in M_Box_Oak ...
    obj("Cabinet", [(0.2, 4, 0, 0.8, 4.6, 0.8)], "T Interior", "M_Box_Oak")                # ... which is wood
    obj("Ceiling_Trim", [(0, 0, 2.8, 8, 0.05, 2.81)], "T ST08 Ceiling", "Material.001")   # a default name: never a word
    cams = [{"id": "02_bed", "eye": [3.5, 0.5, 1.6], "look": [1, 4]}, {"id": "03_bath", "eye": [7.5, 0.5, 1.6], "look": [5, 4.5]},
            {"id": "01_ext", "eye": [4, -4, 1.2], "look": [4, 0]},
            {"id": "09_ext2", "eye": [4, -4, 1.2], "look": [2, 2.5]}]  # outside, facing into the bed room
    res = analyse(sc, cams)
    rooms = {r["id"]: r for r in res["rooms"]}
    assert res["kind"] == "construction" and set(rooms) == {"02_bed", "03_bath"}, res
    close = lambda a, b: all(abs(p - q) <= 0.06 for p, q in zip(a, b))
    assert close(rooms["02_bed"]["rect"], [t, 4 - t, t, 5 - t]), rooms["02_bed"]
    assert close(rooms["03_bath"]["rect"], [4 + t, 8 - t, t, 4.8]), rooms["03_bath"]  # biggest rectangle under the notch
    assert rooms["02_bed"]["name"] == "ห้องนอน" and rooms["03_bath"]["name"] == "ห้องน้ำ", rooms
    assert res["outside"] == ["01_ext", "09_ext2"] and not res["shared"], res
    assert res["groups"] == {"ceiling": ["M_Gypsum"], "floor": ["M_TileAdhesive"], "frame": ["M_PVC_White"]}, res["groups"]
    assert any(n.startswith("GROUP skip M_Box: ") and "M_Box_Oak" in n for n in res["notes"]), res["notes"]
    assert res["cut_z"] == 2.75, res["cut_z"]
    assert name_from_id("08_bath", {"bath": 2}) is None and name_from_id("05_bed1", {"bed": 3}) == "ห้องนอน 1"
    high = analyse(sc, [], floor=10)  # no wall at the cuts: no rooms, a note, and the groups still come out
    assert not high["rooms"] and high["groups"] and any(n.startswith("NO WALLS") for n in high["notes"]), high
    alone = analyse(sc, [])
    assert [r["id"] for r in alone["rooms"]] == ["01_bed", "02_bath"], alone["rooms"]
    assert all(r["clip"] is False for r in alone["rooms"]), alone["rooms"]
    both = analyse(sc, cams[:1] + [{"id": "04_bed_b", "eye": [3, 4, 1.6], "look": [2, 1]}])
    assert both["shared"] == [["02_bed", "04_bed_b"]], both["shared"]
    assert both["rooms"][-1] == {**both["rooms"][-1], "id": "05_bath", "clip": False}, both["rooms"]
    named = analyse(sc, [{"id": "05_living2", "eye": [3.5, 0.5, 1.6], "look": [1, 4]}])["rooms"][0]
    assert named["name"] == "ห้องนั่งเล่น 2", named  # the camera id names the room before the furniture does
    bpy.data.objects.remove(bpy.data.objects["Str_Col_C4"])
    assert len(analyse(sc, [])["rooms"]) == 1, "the column closed the bath's corner"
    for c in list(cols.values()):
        c.name = c.name.replace(" ST", " X")
    assert analyse(sc, [])["kind"] is None
    # a wall that is one ring mesh: its core is a long thin free strip with a house-sized bounding box, not a room
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    bm, O, I = bmesh.new(), [(0, 0), (6, 0), (6, 4), (0, 4)], [(0.2, 0.2), (5.8, 0.2), (5.8, 3.8), (0.2, 3.8)]
    v = {(k, z, r): bm.verts.new((*(O if r else I)[k], z)) for k in range(4) for z in (0, 3) for r in (0, 1)}
    for k in range(4):
        j = (k + 1) % 4
        for q in ((k, 0, 1), (j, 0, 1), (j, 3, 1), (k, 3, 1)), ((k, 0, 0), (k, 3, 0), (j, 3, 0), (j, 0, 0)), \
                 ((k, 3, 1), (j, 3, 1), (j, 3, 0), (k, 3, 0)), ((k, 0, 1), (k, 0, 0), (j, 0, 0), (j, 0, 1)):
            bm.faces.new([v[x] for x in q])
    me = bpy.data.meshes.new("WL_Ring")
    bm.to_mesh(me)
    col("R ST06 Walls").objects.link(bpy.data.objects.new("WL_Ring", me))
    ring = analyse(sc, [])["rooms"]
    assert len(ring) == 1 and close(ring[0]["rect"], [0.2, 5.8, 0.2, 3.8]), ring
    print("SELFTEST OK")


USAGE = "usage: house_mark.py -- <project_dir> [<cameras.json>] [--floor Z]   or   house_mark.py -- --selftest"

if __name__ == "__main__":
    args, opt, scene = cli()
    if "--selftest" in args:
        selftest()
    else:
        pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] not in ("--floor", "--frame"))]
        if not pos:
            sys.exit(USAGE)
        try:
            floor = float(opt("--floor")) if "--floor" in args else None
        except (IndexError, ValueError):
            sys.exit("--floor needs a level in metres, e.g. --floor 3.2\n" + USAGE)
        out = pos[0]
        cams = json.load(open(pos[1], encoding="utf-8")) if len(pos) > 1 else []
        for c in cams:
            safe_id(c["id"])
        res = analyse(scene, cams, floor)
        report(res)
        if res["kind"]:
            os.makedirs(out, exist_ok=True)
            if res["rooms"] and cams:  # without cameras the ids can't match them yet: the ROOM lines are enough for step 2
                write(os.path.join(out, "rooms.json"), {"cut_z": res["cut_z"], "rooms": [
                    {k: v for k, v in r.items() if not k.startswith("_")} for r in res["rooms"]]})
            elif res["rooms"]:
                print("rooms.json is written when cameras.json is given (step 7): run again then")
            if res["groups"]:
                write(os.path.join(out, "groups.json"), res["groups"])
