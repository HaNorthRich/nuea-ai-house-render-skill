---
name: nuea-ai-house-render
description: >-
  ทำภาพและคลิปบ้านให้สมจริงจากโมเดล Blender โดยคงผนัง ประตู หน้าต่างไว้ที่เดิม: จัดมุมกล้องแบบภาพถ่ายตกแต่งภายใน ·
  ภาพดินน้ำมัน + Material ID map บอกวัสดุด้วยสี · ภาพสมจริงผ่าน Kling MCP (เสียเงิน) หรือ Google Flow (มีโควตาฟรีรายวัน) ·
  ซ้อนเส้นตรวจว่าเป็นบ้านหลังเดิม · คลิป 5 วิ · หน้าเว็บแผนที่แบบเกม (walkthrough) Triggers: 'render บ้านให้สมจริง',
  'ทำภาพ interior จาก Blender', 'Material ID map', 'color ID map', 'ทำคลิปเดินชมบ้าน', 'walkthrough แผนที่แบบเกม',
  'Kling', 'Google Flow', photoreal render from Blender
---

# nuea.ai House Render

Turns a furnished Blender house into photoreal stills, 5 s clips and a game-style map page, without the AI moving the
walls. Distilled from a real 9-stop house (Nov 2026); every rule in `references/` cost at least one wasted
generation. Reply in the user's language; file and object names in English. Generated images are AI images: say so.

**The model file is the user's.** Scripts create cameras and materials in memory and never save the `.blend`.
All work goes into a project folder next to it (`<house>_render/`).

## Files
| File | What |
|---|---|
| `scripts/cameras.py` | normal render (`<id>.png`) or clay pass (`--clay` → `<id>_clay.png`) for every camera in `cameras.json` |
| `scripts/idmap.py` | Material ID map (`<id>_idmap.png`) + `legend.json`: one flat colour per material group |
| `scripts/plan_map.py` | top view `media/plan_top.png` + `plan.js` (rooms and walking path) for the walkthrough page |
| `scripts/overlay.sh` | red Blender edges over an AI image (ffmpeg; run with `bash`) |
| `scripts/_common.py` | shared by the three Blender scripts: arguments, id check, render settings, level camera |
| `walkthrough/index.html` | the game-map page: click a room → the map opens, a point walks the path, the clip plays; hold **B** = the Blender view |
| `examples/sample_room.py` | builds a test room from an empty Blender (install proof) |

References (read when the step says so): `references/camera-rules.md` · `references/prompts.md` ·
`references/route-kling.md` · `references/route-google-flow.md` · `references/checking.md`.

All Blender scripts run headless:
`"<BLENDER>" -b -Y "<house.blend>" --python-exit-code 1 --python <script> -- <args>`. Add `-S <scene>` right after the
file name when it has several scenes, and `--frame N` after `--` for animated doors (open doors look better). `-Y` keeps
scripts stored inside the .blend from running. A non-zero exit code means the script failed: stop and show the user the
traceback.

**Paid jobs (Kling):** before each batch, tell the user the number of jobs × the credit price (`who_am_i`) and wait for
a yes. No trial jobs. Call Kling's `feedback` tool only when the user agrees, and send no file paths, names or house details.

## Steps

### 1. Setup and route
Check: the `.blend` opens, Blender MCP answers (`get_scene_info`) or headless Blender runs, `ffmpeg -version` works.
Ask the user which route makes the images: **Kling** (paid, Claude runs it through MCP: `route-kling.md`) or
**Google Flow** (free daily quota, the user clicks on the website: `route-google-flow.md`). Ask for a style photo they
have the right to use, or a style in words.
**Done when** the route is chosen and the project folder exists.

### 2. Cameras like interior photos
Read `references/camera-rules.md`. List the rooms with their bounds and hero furniture, propose two cameras per room,
render them small (`cameras.py … --percent 40`), and show a contact sheet. Iterate until the user picks one per room.
**Done when** `cameras.json` holds one approved camera per room and every room renders at 100% with a clear foreground.

### 3. Three passes per camera
```
cameras.py  <out>/renders <cameras.json>            # <id>.png        normal render
cameras.py  <out>/renders <cameras.json> --clay     # <id>_clay.png   clay ("ดินน้ำมัน") for the cover / before-after
idmap.py    <out>/renders <cameras.json>            # <id>_idmap.png  + legend.json
```
Open `legend.json`: if a large surface fell into `other` or the wrong group, write `groups.json` next to
`cameras.json` (`{"wall": ["myplaster", …]}`; its keywords win over the built-in table) and run `idmap.py` again. Materials
under `unrecoloured` are linked from another .blend and kept their own colour: tell the user which objects they are.
The clay pass also covers window glass, so a room lit only by the sun renders darker; that is expected.
**Done when** every camera has all three images and no large surface is grey (`other`).

### 4. Photoreal stills first
Build one prompt per room from `references/prompts.md`: legend lines only for the colours present in that room, the
KEEP list from the scene, the placeholders to replace, the decor. Run the chosen route: Kling submits (price first,
see **Paid jobs**); Flow gets an upload pack per room. One room first, show the user, then the rest.
**Done when** every room has `<id>_real.png` the user approved.

### 5. Same house check
`bash "<skill>/scripts/overlay.sh" <id>.png <id>_real.png <id>_overlay.png` for every still; read
`references/checking.md`. Regenerate a room that fails with the matching fix (price first, see **Paid jobs**).
**Done when** every room passes or the user accepts the listed change.

### 6. Clips
One 5 s clip per approved still, a different move per room (`prompts.md`; on Kling, price first, see **Paid jobs**).
Make a contact sheet of each clip and look for warping.
**Done when** every clip is downloaded as `<id>.mp4` and its contact sheet shows nothing appearing, vanishing or bending.

### 7. Walkthrough page
Copy `walkthrough/` into the project. Write `rooms.json`: room ids = the camera ids, rectangles in plan metres in
walkthrough order, optional `path` through the doors, `cut_z` just under the ceiling (one floor per run), and the
optional `clip` / `spot` / `at` fields described at the top of `plan_map.py`. Run `plan_map.py <project>/walkthrough
rooms.json`, then fill `walkthrough/media/`: `<id>.mp4`, and the two stills as JPEG
(`ffmpeg -v error -y -i <id>_real.png -q:v 2 media/<id>_real.jpg`, the same for `<id>.png` → `media/<id>_blender.jpg`).
Open `index.html` in Chrome and click every room; hold B once.
**Done when** every room's clip plays from the map and the point lands inside its room.

Hand over: the folder tree, one line per room (pass / what changed), and what is left for the user (posting with the
AI label, comparing against the plans before showing clients).
