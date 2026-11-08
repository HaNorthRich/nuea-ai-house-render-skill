# Free route: Google Flow on the website (the user clicks, Claude prepares everything)

Facts read on 8 Nov 2026. Credits, video, resolution, busy hours and retirement dates come from Google's Flow help
pages. The image limits and "images do not use credits" come from third-party blogs only; Google has not published
them. Free limits change often: tell the user to trust what Flow shows on the Generate button over these numbers,
and never present these numbers as Google's promise.

| | Free (no subscription) |
|---|---|
| Who | Google account, age 18+; Thailand is a supported country (VPN does not work) |
| Images | currently appear not to use the daily credits (third-party tests, not on Google's pages) · Nano Banana Pro about 20 per day, lighter Nano Banana models about 400 per day (one second-hand source) · the free default model is Nano Banana 2 Lite |
| Video | 50 credits per day for every account, reset at the first generation of the day, not carried over |
| 5 s clip | **Frames to Video** with the still as the start frame · 9:16 · model **Omni Flash 1.2** at 720p ≈ 15 credits (≈ 3 rooms a day) · or **Veo 3.1 Lite** 4/6/8 s ≈ 10 credits (trim to 5 s) |
| Resolution | video downloads up to 720p on the free plan |
| Busy hours | about 14:00–17:00 UTC (21:00–24:00 Thai time) free users may be blocked from video; images still work |
| Watermark | SynthID on everything; a visible mark in some countries (check the user's own account) |
| Retiring | Veo 3.1 Fast / Quality and Omni Flash 1.1 end on 5 Dec 2026: use Omni Flash 1.2 or Veo 3.1 Lite |

Paid alternative inside Google: Google AI Plus/Pro/Ultra plans unlock 1080p and more credits (Google help page, 8 Nov 2026).

## What Claude prepares: one upload pack per room
```
flow_pack/<id>/
  1_render.png      normal render (1080x1920)
  2_idmap.png       Material ID map, same camera
  3_style.jpg       the user's style photo (only if they gave one they have the rights to)
  prompt_image.txt  the still prompt from prompts.md, legend filled in
  prompt_video.txt  the move for this room from prompts.md
```
Then give the user these steps, one room at a time:
1. Open https://labs.google/flow → New project.
2. **Image**: choose Nano Banana Pro (or Nano Banana 2.1 when Pro is used up) · portrait 9:16 · add the images in
   order 1, 2, (3) · paste `prompt_image.txt` · Generate → download the best one as `<id>_real.png` into the room's
   folder. Two or three tries per room is normal.
3. Send the downloaded file back to Claude for the line check (step 5 of SKILL.md) before making video.
4. **Video**: Frames to Video · start frame = `<id>_real.png` · 9:16 · Omni Flash 1.2 · 5 s · 720p · paste
   `prompt_video.txt` · read the credit cost on the Generate button first · download as `<id>.mp4`.
