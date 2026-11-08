# Install guide for Claude

The user sent you this repository and asked you to install the skill. Work through the steps in order. Each step
ends on a check: run it, read its output, and tell the user the result in their language.

- Before each step, tell the user in one line what you will run and why.
- Ask the user first before you install software (git, ffmpeg, Blender) or replace a copy of the skill already installed.
- A check that fails, or a "no" from the user: stop there, show the user the step and its output, and ask how they
  want to go on. A step starts only after the step before it passed its check.
- Your shell forgets variables between commands: write the real paths into every command, in double quotes (Blender
  paths often contain spaces), and run each code block below as one command.
- Steps marked **user** need the user's hands: say exactly what to click, then wait for their answer.

## 0. A shell and git

This skill needs Claude Code (the terminal app, the Code tab of the Claude desktop app, or an IDE extension),
because it installs files and runs Blender. Claude Code comes with the paid Claude plans (Pro and up) or an API key.

- No shell available (a chat-only Claude): tell the user to open Claude Code and paste
  `ลง Skill นี้ให้หน่อย https://github.com/HaNorthRich/nuea-ai-house-render-skill`, then stop.
- Run `git --version`. Without git, step 3 downloads a tarball with `curl` instead (no install needed).
- **Check:** a shell runs commands, and you know whether git is there.

## 1. Blender 4.2 or newer

| OS | Usual path |
|---|---|
| macOS | `/Applications/Blender.app/Contents/MacOS/Blender` |
| Windows (Git Bash) | `/c/Program Files/Blender Foundation/Blender <version>/blender.exe`, or `where blender` |
| Linux | `command -v blender`; snap `/snap/bin/blender`; flatpak `flatpak run org.blender.Blender` |

This guide calls that path BLENDER. If Blender is missing or older than 4.2, ask the user to install the current
release from https://www.blender.org/download/ and wait for them to say it is done.

- **Check:** `"<BLENDER>" --version` prints `Blender 4.2` or newer.

## 2. ffmpeg

Used to check AI images against the model and to look at clips. Run `ffmpeg -version`. If missing, ask, then install:
macOS `brew install ffmpeg`, Windows `winget install --id=Gyan.FFmpeg -e`, Linux the distribution package (`sudo apt
install ffmpeg`).

- **Check:** `ffmpeg -version` prints a version.

## 3. The skill

If `~/.claude/skills/nuea-ai-house-render` already exists, this is an update. Ask; on no, keep it and go to step 4. On
yes, fetch first, then move the old copy out and copy the new one in, as one command:

```bash
SRC="$(mktemp -d)" && git clone --depth 1 https://github.com/HaNorthRich/nuea-ai-house-render-skill.git "$SRC/repo" && mv ~/.claude/skills/nuea-ai-house-render ~/.claude/nuea-ai-house-render.bak-$(date +%Y%m%d%H%M%S) && cp -R "$SRC/repo/nuea-ai-house-render" ~/.claude/skills/
```

A first install (with git):

```bash
[ ! -e ~/.claude/skills/nuea-ai-house-render ] && SRC="$(mktemp -d)" && git clone --depth 1 https://github.com/HaNorthRich/nuea-ai-house-render-skill.git "$SRC/repo" && mkdir -p ~/.claude/skills && cp -R "$SRC/repo/nuea-ai-house-render" ~/.claude/skills/
```

Without git:

```bash
[ ! -e ~/.claude/skills/nuea-ai-house-render ] && SRC="$(mktemp -d)" && curl -fsSL https://github.com/HaNorthRich/nuea-ai-house-render-skill/archive/refs/heads/main.tar.gz | tar -xz -C "$SRC" && mkdir -p ~/.claude/skills && cp -R "$SRC/nuea-ai-house-render-skill-main/nuea-ai-house-render" ~/.claude/skills/
```

- **Check:** `head -3 ~/.claude/skills/nuea-ai-house-render/SKILL.md` shows `name: nuea-ai-house-render`.

## 4. Blender MCP (optional, recommended)

The scripts run headless without it; with it, Claude can look at the scene live while choosing cameras. Run
`claude mcp list`. A server running `mcp-for-blender` (or its old name `blender-mcp`) is already set up: keep it.
Otherwise ask, then (needs `uvx`: macOS `brew install uv`, others https://docs.astral.sh/uv/):

```bash
uvx mcp-for-blender@2.2.4 install-addon && claude mcp add --scope user blender "$(command -v uvx)" mcp-for-blender@2.2.4
```

- **Check:** `claude mcp list` lists `blender` running `mcp-for-blender@2.2.4`, or the user chose to skip it.

## 5. Image route

Ask the user which route they want; both can be added later.

- **Kling (paid, automatic):** they need a Kling paid plan. Register Kling's official MCP:
  `claude mcp add --transport http --scope user klingai https://kling.ai/mcp`. Logging in is step 7.
- **Google Flow (free daily quota, by hand):** nothing to install; they need a Google account (18+).

- **Check:** the route is noted, and `claude mcp list` shows `klingai` if they chose Kling.

## 6. Proof that it works (about 1 minute, no AI credits)

Build the sample room, then render its three passes and its map:

```bash
OUT="$HOME/nuea_render_sample" && SK="$HOME/.claude/skills/nuea-ai-house-render" && "<BLENDER>" -b --factory-startup --python-exit-code 1 -P "$SK/examples/sample_room.py" -- "$OUT" && "<BLENDER>" -b "$OUT/sample_room.blend" --python-exit-code 1 --python "$SK/scripts/cameras.py" -- "$OUT/renders" "$OUT/cameras.json" && "<BLENDER>" -b "$OUT/sample_room.blend" --python-exit-code 1 --python "$SK/scripts/cameras.py" -- "$OUT/renders" "$OUT/cameras.json" --clay && "<BLENDER>" -b "$OUT/sample_room.blend" --python-exit-code 1 --python "$SK/scripts/idmap.py" -- "$OUT/renders" "$OUT/cameras.json" && mkdir -p "$OUT/walkthrough" && cp -R "$SK/walkthrough/." "$OUT/walkthrough/" && "<BLENDER>" -b "$OUT/sample_room.blend" --python-exit-code 1 --python "$SK/scripts/plan_map.py" -- "$OUT/walkthrough" "$OUT/rooms.json"
```

- **Check:** exit code 0; `$OUT/renders` holds `01_living.png`, `01_living_clay.png`, `01_living_idmap.png`,
  `legend.json`; `$OUT/walkthrough/plan.js` exists. Show the user the three images.

## 7. Hand over (**user**)

1. If Blender MCP was added: in Blender, **Edit → Preferences → Add-ons**, enable **MCP for Blender**, press **N** in
   the 3D viewport → **MCP for Blender** tab → **Start MCP Server**.
2. Quit Claude Code completely and open it again: skills and MCP servers load when a session starts.
3. If Kling was added: type `/mcp` → **klingai** → **Authenticate**, and log in to Kling.
4. Then try: `ทำภาพบ้านหลังนี้ให้สมจริง จัดมุมกล้องแบบภาพ Pinterest ทุกห้อง <path ของไฟล์ .blend>`.

**Done when** the user has the steps above and every check in steps 0–6 passed (step 4/5 may be skipped by choice).
