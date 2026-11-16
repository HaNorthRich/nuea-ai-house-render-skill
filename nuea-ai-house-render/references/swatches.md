# Real-material swatches (optional, step 4)

A swatch is one close-up image of a real material (made with AI as below, or a photo you took or have the right to
use), sent with the render and the Material ID map so the AI copies a real texture instead of guessing one. Use it when a surface still looks CG or plastic in the stills, or must be one
exact product (a roof tile, a ventilation block, a floor tile). Otherwise skip it: the Material ID map already says
where each material goes.

Tested on 16 Nov 2026 on a single-storey house exterior (GPT Image 2.6, the clay pass as image 1, the normal render as
image 2, four swatches and one clay crop; three rounds). The Material ID map was not in that test, so the image order
below is untested as a whole, and nothing here is tested yet on this skill's Kling and Flow routes: check how many
images your model accepts, and check every still with the overlay (step 5) as usual.

## Make the swatches

At most four, one per main surface (roof, walls, floor or driveway, one product). Square 1:1. Make them once per house
and reuse them for every camera. Free on Google Flow's image quota; on Kling every swatch, redo and spot fix is a paid
job: price first (SKILL.md **Paid jobs**).

```
extreme macro photograph of real <material> filling the whole frame edge to edge, <colour>, <texture>, <wear>, even daylight, sharp focus, real texture, no text
```

Each rule below cost a failed generation:

1. **The swatch's wear lands on the house.** A roof swatch with "a few lichen spots" gave a new house a lichen-stained
   roof. For a new or unbuilt house describe a new, clean surface with at most a little light dust.
2. **Never name a defect, not even with "no".** "no cracks, no stains" drew a crack.
3. **Never name a process.** "very faint paint-roller texture" drew a painted patch of roller strokes.
4. **Keep the opening `extreme macro photograph of real …`** and write `neutral` in greys. "close-up photograph of …
   just laid on a new house" turned charcoal tiles brown with white streaks.
5. **Read each product off the clay pass at 100 % before writing its swatch.** A ventilation block that looked like
   "round holes" in a small render was square blocks with four round holes and a small four-point star each.
6. Look at every swatch before you use it and redo the bad ones.

Wording that worked:
- `new concrete roof tiles in dark neutral charcoal grey, wave double-roman profile, matte even colour, fine sand texture, clean surface, a little light dust in the overlaps`
- `smooth cement plaster wall painted off-white, light dust`
- `light grey broom-finished concrete driveway, fine sand grain, faint tyre marks and dust`

## Send them

Images 1 and 2 stay the normal render and the Material ID map (`prompts.md`). Then the swatches, then a clay crop if
there is one, and the style photo last. Number every line by the order you send the images: with k swatches they are
images 3 to 2+k, the crop is the next number, and the style line from `prompts.md` takes the last number. A model that
takes three images: the one swatch that matters most, or none. A model that takes two images: no swatches.

| Image | Line in the prompt, after the legend |
|---|---|
| a swatch | `Image <n> is a close-up of the real <material> for the <colour> surfaces: copy its texture and colour.` |
| a repeating product (ventilation blocks, lattice, louvres) | crop that part of `<id>_clay.png`, enlarge it, send it as its own image: `Image <n> is a close-up of the <panel> in the design model: copy its block design exactly. Keep the number, size and rows of blocks exactly as in image 1: the front panel is <rows> rows of <count> blocks.` |

A count in words alone fails: the AI drew 3 × 6 and then 3 × 7 blocks for "4 rows of 11". With the clay crop sent
in the same generation, the count and the design came out right the first time.

## In the rest of the prompt

- A new house: `a brand-new house on the day it was handed over` and keep wear to `crisp clean edges, fresh paint, a
  little dust on the driveway`. The aged wording made the house look years old.
- A car that is a real car model in the scene (not a placeholder box): `the car stays exactly as in image 1, same
  shape and position`. "A plain unbranded silver SUV" made the AI swap it for another car.
- An ordinary photo beats a dramatic one: `plain midday daylight, natural unsaturated colours, slight noise, not
  cinematic`. The stranger the house, the plainer the photo.

## Fixing one spot afterwards

On Kling this is a paid job: price first. Send the approved still as image 1 (plus a reference for the spot, if any)
with `Edit only <one thing> and keep every
other part of image 1 exactly as it is: the same sky, roof, walls, …`. It kept the rest of the photo almost identical
and removed a car badge in one go. It cannot set a count: stop after two tries and make the generation again with the
right references instead.
