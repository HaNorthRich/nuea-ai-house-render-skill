# Checking that it is still the same house

AI images look real enough that viewers and clients will ask "is this the same house?". Prove it before showing
anyone: `bash "<skill>/scripts/overlay.sh" <normal render> <AI image> <out.png>` (needs ffmpeg) draws the Blender edges in red over
the AI image.

## Reading the overlay
- Red lines sitting on wall corners, the tile grid, window and door frames, the bed, table and sofa edges = **pass**.
- Red lines floating in empty space, or AI edges with no red line on them = something moved, was added or removed.
- Small furniture or decor without red lines is expected: decor is added on purpose.
- Report per room in one line: pass, or what changed. When the user will show the images to clients, every room needs a pass.

## What the AI changed in a real house, and the fix that worked
| Seen | Fix in the prompt |
|---|---|
| Image came back 3:4 and cropped, furniture gone | `aspect_ratio 9:16` (Kling defaults to 3:4) |
| A wall edge or door leaf in the foreground → the AI deleted it and invented a new view | move the camera so nothing blocks the frame (camera-rules.md) |
| An arched window added on a solid wall | say how many windows there are and which wall is solid |
| The camera moved and the floor changed in a small bathroom | send the Material ID map + "do not zoom, do not rotate, do not recompose" + the floor colour in KEEP |
| Roof colour changed (dark grey → terracotta) | name the roof colour in KEEP |
| A range hood and upper cabinets added in the kitchen | list what must not be added, or accept it as decor and say so |
| Blocky toilet / shower / car copied as boxes | describe each placeholder and its real replacement |

## Wording rules when presenting
- Call them "ภาพสมจริง" / "AI images", not real photos; turn on the platform's AI label when posting.
- They help a client picture the design; they are not construction drawings. Compare against the plans room by room.
- A style photo from the internet stays out of anything published (and blur it in screen recordings).
- For property ads: anything that is not in the plans must be removed from the image, not disclaimed; put
  "ภาพจำลองจาก AI" on the image itself.
