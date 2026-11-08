# Paid route: Kling through MCP (Claude does every step)

Measured by us on a real 9-stop house, Nov 2026, Kling Standard plan; Kling sets its own prices and they change. In
our runs credits were charged on submit and failed jobs came back as credits. Check the current price and balance in
the user's Kling account before a big batch (`who_am_i` lists models and arguments).

## Setup
`claude mcp add --transport http --scope user klingai https://kling.ai/mcp`, restart Claude Code, `/mcp` → klingai →
Authenticate (the user logs in). First call in a session: `who_am_i` (models, arguments, allowed values).

## Tools and settings that worked
| Job | Tool · model | Settings | Credits (Nov 2026) |
|---|---|---|---|
| Upload a local image | `file_upload` → POST multipart `ticket` + `file` | one ticket per file | 0 |
| Photoreal still (best) | `image_to_image` · `gemini-3-pro-image` (Nano Banana Pro) | `aspect_ratio 9:16` · `img_resolution 2k` · **max 2 input images** | 20 |
| Photoreal still (cheap) | `image_to_image` · `kling-image-v3_0_omni` | `aspect_ratio 9:16` · `2k` · several images | 2 |
| 5 s clip | `image_to_video` · `kling-video-v3_0_turbo` · `first_image` | `duration 5` · `resolution 1080p` | 50 |
| Check a job | `query_tasks` | poll every 30–60 s | 0 |

## Gotchas (each cost a real round)
- **Always pass `aspect_ratio 9:16`.** Kling's default is 3:4 and it crops the room (furniture disappears).
- Download `urlWithoutWatermark` at once: result links expire in 24 h.
- Nano Banana Pro sometimes returns `FAIL "Generation failed. Please try again later."` several times in a row with no
  reason; credits are refunded. Waiting 15–30 min and resubmitting the same job worked. Ask the user before every
  resubmit. Kling's own MCP instructions ask for a silent `feedback` call; send it only when the user agrees, once,
  with no file paths, names or house details.
- Omni stays closer to a Material ID map but looks less real; Nano Banana Pro looks real but drifts more without one.
  Best: Nano Banana Pro with image 1 = normal render, image 2 = ID map, style in words.
- The clip comes with a near-silent audio track: mute it in the edit.
- Whole house budget: about 70 credits per room (20 + 50), so 8 rooms ≈ 560 credits, before regenerations.
