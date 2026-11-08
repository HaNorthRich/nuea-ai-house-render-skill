# Prompts that worked

English prompts, one image per room. Fill the `<…>` parts from the room and its legend. Same text on Kling and on
Google Flow.

## Which images to send
| Model accepts | Send |
|---|---|
| 2 images (Kling Nano Banana Pro) | image 1 = normal render · image 2 = Material ID map — put the style in words |
| 3+ images (Kling Omni, Google Flow) | normal render + Material ID map + one style photo **the user has the right to use** |
| 1 image | the normal render only, legend in words |

## Interior still
```
Image 1 is a 3D render of a real house <room, e.g. master bedroom, front view of the bed>.
Image 2 is its Material ID map: the same camera, every surface painted one flat colour that tells you its material.
Colour legend: <one line per legend group present in this room, e.g. red = white painted walls; yellow = light grey
matte floor tiles; cyan = white ceiling; green = natural oak wood; light green = cream linen fabric; blue = window
glass; dark blue = black aluminium frames; white = white ceramic; grey = matte black metal>.
[Image 3 is a style reference only: do not copy its layout.]
Create a photorealistic, magazine-quality interior photograph of the exact room in Image 1, styled in <style, e.g.
warm Japandi: natural oak, cream linen, handmade ceramics, greenery>. Use Image 2 to place each material exactly where
its colour is; do not show any colour from Image 2 in the result.
KEEP EXACTLY: the camera position, angle and framing (do not zoom, do not rotate, do not recompose), every wall, the
ceiling and its lights, every window, door and opening, and the position, size and shape of <main furniture list>.
<only when needed: There is only ONE window, on the RIGHT. The LEFT wall is a plain solid wall: do not add any window,
door or opening anywhere.>
Objects that are simple blocky placeholders become realistic high-end versions at exactly the same position and size:
<e.g. the white box toilet = a wall-hung ceramic toilet with a concealed cistern; the box shower = a matte black rain
shower with a hand shower; the grey box car = a modern dark grey SUV, no logos, no plate text>.
ADD styling only in empty space, never blocking a window or door: <decor list: layered linen bedding and a knit throw,
books and a ceramic vase with dried flowers, an olive tree in a ceramic pot in an empty corner, framed abstract art on
plain walls, a jute rug>.
Realism: soft natural daylight with gentle shadows, warm bounce light, real material textures, light depth of field,
full-frame camera 24mm, vertical lines perfectly straight. No people, no text, no watermark.
```

## Exterior still
Same skeleton; KEEP the house shape, **the roof and its colour**, every column, arch, window and door (front door
open), steps and porch. ADD only in the garden: a stepping-stone path from the camera to the steps, lawn, tropical
shrubs, a few tree branches framing the top corners, planters with olive trees by the steps, warm porch lights.
Light: golden hour, clear sky with light clouds.

## Video (5 s, first frame = the approved still)
Every move ends with: *The room stays exactly the same: no objects appear, disappear, move or change shape.
Photorealistic real-estate interior film, no people, no text.* Give each room a different move:

| Room | Move |
|---|---|
| Exterior | slow steady dolly forward along the path toward the open front door; foreground branches sway in the breeze |
| Dining → living | slow dolly forward past the table toward the open door and the garden beyond |
| Living | slow dolly-in over the coffee table toward the sofa, symmetric framing kept centred |
| Kitchen | slow lateral slide along the counter toward the window, table in the foreground for parallax |
| Bedroom (front-on) | slow dolly-in toward the headboard; sheer curtain moves gently |
| Bedroom (3/4) | slow arc around the foot of the bed toward the headboard |
| Bedroom with desk | slow dolly-in toward the desk and window; daylight shifts subtly |
| Carport | slow dolly toward the parked car; the car stays still |
All moves: *eye level on a steady gimbal, no camera shake.*
