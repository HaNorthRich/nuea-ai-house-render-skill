# Camera rules: interior-photo angles

The walk-through camera of a 3D tour (14 mm, tilted down, 1.5 m high) makes AI images that look cheap, and it lets the
AI recompose the room. Interior photographers shoot differently; copy them.

## The rules
- **Level camera.** Rotation X = 90° exactly, so vertical lines stay vertical. To show more floor or ceiling, use
  `shift_y` (−0.1…+0.15), never tilt.
- **Lens 16–24 mm** for a 9:16 frame (16 for small rooms and bathrooms, 20–22 for bedrooms and living rooms, 24 for exteriors).
- **Eye 1.0–1.1 m above the floor** for rooms; 1.2 m for an exterior from the garden.
- **One hero per room**: the headboard wall, the sofa, the dining table leading to a view, the kitchen counter, the
  vanity. Frame it front-on (one-point, symmetric) or at 3/4 from a corner.
- **Clear foreground.** No wall edge, door leaf or door frame covering part of the frame: the AI deletes what blocks
  the view and invents a new room. Keep the camera outside every door-swing zone.
- **Depth** for the hook shot: a table or path leading the eye to an open door or window.

## How to find a good camera fast
1. Read the room bounds and the main furniture positions from the scene (bounding boxes of the largest meshes per room).
2. Propose two cameras per room (front-on + 3/4), render both at 40% with `cameras.py --percent 40`, and show the user
   a contact sheet.
3. A render that shows mostly a wall, or a camera inside furniture: move the eye 0.3–0.6 m away from the obstacle and
   re-render. Two rounds is normal.
4. The user picks one per room → that is the final `cameras.json` (render it at 100%).

## cameras.json
```json
[{"id": "02_living", "eye": [5.75, 3.45, 1.60], "look": [2.8, 3.45], "lens": 16, "shift_y": -0.05}]
```
`eye` = camera position (m), so its z = the room's floor level + 1.0–1.1 (this example's floor sits at +0.55),
`look` = the plan point it faces (only x, y: the camera stays level), ids are plain names (letters, digits, `_`, `-`) and sort in
walkthrough order. The same file drives the normal render, the clay pass and the Material ID map, so all three line
up pixel for pixel.
