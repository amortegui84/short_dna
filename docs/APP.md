# The desktop app

`start_app.bat` (first time: `cd app && npm install`). Electron + the Claude Agent SDK: the app talks to Claude Code as logged in
on this machine, with this repo's skill, CLAUDE.md and docs, and gives it only the MCP servers in config `mcp` (Motion DNA for
After Effects, Motion DNA Blender, Figma). Tick **all my connectors** in the chat to also load the Claude account's connectors
(Krea, Flora...): heavier context, ~9x the cost of a message.

![Start](screens/app_home.jpg)

## Paths
| Path | You give | The app runs | Claude then |
|---|---|---|---|
| **Topic → Short** | topic, platforms, template, character + look, style, length, language | `factory.py new` | research with sources, hook per platform (library/hooks.json, library/platforms), script; stops for approval; then `factory.py run` |
| **Reference → Style** | a link (yt-dlp) or a video file | `engine/referencia.py`: cuts, pacing, motion energy, palette, one frame per shot | describes the style, writes a Motion DNA reference profile, runs match_reference, proposes a style file |
| **Brand → Kit** | the brand's website | `engine/marca.py`: logo candidates, colours, fonts, tagline, Motion DNA brand draft | checks it with you, creates the Motion DNA brand, builds components in AE (and Figma if asked) |
| **Characters** | pick one; describe one; or an idea to propose 3 | `engine/looks.py` for new looks | NEW_CHARACTER.md: character.json, master and scene candidates, your pick, looks |
| **Assets** | prompt, provider, size, refs, cut-out | `engine/assets.py` (Klein, Z-Image, Qwen style, Nano Banana, generic API) | Krea and Flora through MCP |
| **Platforms** | a channel topic and platforms | — | a series plan: pillars, episodes with hooks, length and CTA per platform, repurposing |
| **Projects** | — | `factory.py run` per project, with the cost estimate first | runs and reviews with the skill |
| **Publish** | the brand's accounts, once (YouTube channel, Instagram Business, Zapier, TikTok via PostWire, GitHub release) | `engine/publicar.py` (publish copy); you run `tools/publish_release.py` | writes title, caption and hashtags, uploads to YouTube and TikTok private with the AI label, and on your OK makes them public and posts the Instagram Reel ([PUBLISHING.md](PUBLISHING.md)) |

## Cost before anything paid
Every paid action shows a table (stage, provider, quantity, USD, whether the price was verified) and waits for **Accept**:
`engine/costo.py` with the prices in `library/costs.json` (edit them: they are marked unverified until you check them).
`factory.py run` refuses paid stages without `--yes`; the app passes it only after you accept. Paid MCP tools (Krea, Flora) are
flagged in the permission prompt, and Claude quotes USD before using them (CLAUDE.md).

## Connections
Claude (CLI version), After Effects (process), Motion DNA bridge (`bridge/outbox/_bridge_started.txt`), Blender, Figma (from
Claude's MCP list when a conversation starts), ComfyUI H3/ACE and Klein, QwenStudio, and the keys present in the `.env`
(presence only, never values). Every tool Claude wants to use that is not read-only waits for **Allow** in the chat panel.

## Self-test
`set SF_SNAPSHOT=<folder>` and start the app: it opens every view, saves a screenshot of each and the console errors, and quits.
