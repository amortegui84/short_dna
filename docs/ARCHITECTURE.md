# Architecture

## Idea
A video is **data** (a project folder with `proyecto.json`) run through **stages** (scripts in `engine/`) that read three
**libraries** (character, style, template) and call **providers** (who makes images, video, voice and music). Claude does
the creative stages with the skill; the machine does the rest; the user approves at checkpoints.

```
library/                         work_dir/<slug>/                       providers (config "providers")
  characters/<c>/character.json    proyecto.json   <- template + Claude   image  : comfy_klein | generic_http
  styles/<s>.json                  research.md     <- Claude (sources)    video  : comfy_h3 (talking) | seedance (b-roll)
  templates/<t>/template.json      obras/ inicios/ vo/ clips/ audio/      voice  : elevenlabs
  techniques/techniques.json       mates/ musica/ ae/ datos_ae.json       music  : comfy_ace | suno
  kit/ (collage assets)            <slug>.mp4  qa_render.json  qc.json    research: claude (web search + sources)
```

## Stages (`python factory.py stages`)
| Stage | Who | In → out |
|---|---|---|
| research | Claude | topic → `research.md` (facts with sources, artworks with public-domain links, a real quote) |
| script | Claude + user | research → `proyecto.json` lines (A talking / B voice-over), moments, artworks per line, titles, quote |
| design | Claude (optional) | script → storyboard frames in Figma with the style tokens (docs/FIGMA.md) |
| obras | engine | URLs → `obras/*.jpg` + credits |
| retrato | engine (GPU) | portrait artwork → `retrato_recorte.png` |
| look | check / looks.py | the character look exists, or generate candidates with the user |
| inicios | engine (Klein) | look + master → one start frame per talking line |
| voz | ElevenLabs | lines → `vo/*.mp3` |
| clips | H3 | start frame + master + voice reference → talking clips with lipsync |
| sts | ElevenLabs | H3 speech → the video's voice, same timing |
| montaje | engine | voice files → `timeline.json` (pace, holds, word times) |
| mates | engine (GPU) | clips → cut-outs + face boxes |
| musica | ACE-Step / Suno | style tags → `musica/elegida.wav` |
| ae | After Effects + Motion DNA | everything → comp built by `ae/collage.jsx`, sound, layout QA |
| render | aerender | comp → `<slug>.mp4` + QA |
| qc | engine | transcript match, loudness, contact sheet |
| collect | AE | light collect + zip for handoff |

## Libraries
- **Character** (`library/characters/<slug>/`): `character.json` with identity text, the never-list, voice (provider + id), looks
  (image + outfit/pose/head prompts), start-frame variants, the clip prompt template (`{artista}`, `{accion}`, `{dialogo}`), H3 settings
  and the framing in AE. Add one: docs/NEW_CHARACTER.md.
- **Style** (`library/styles/<slug>.json`): tokens, type, safe area, timings, rules, sound map, default music. The style's code is
  its After Effects builder (`ae/collage.jsx` for `collage_v10c`). A new style = a new JSON + builder (docs/NEW_STYLE.md).
- **Template** (`library/templates/<slug>/template.json`): the section grammar (which line does what) and the empty project.
- **Techniques** (`library/techniques/techniques.json`): every animation technique with where it lives and how it works, so a new
  style can reuse them. Motion DNA's own library (moves, curves, kit pieces) is available through its MCP tools.

## Providers
`factory/providers/`: one interface per capability; config picks the provider. Local ComfyUI is the default (no cost). Remote
providers read keys from the `.env` named in config. Adding one = a module + an entry in `PROVIDERS` (docs/PROVIDERS.md).

## Machine
- Windows, Python 3.11+ (engine), ffmpeg on PATH.
- After Effects 2026 + Motion DNA (panel, bridge, MCP `motion-dna`): the AE stages talk to AE through Motion DNA's file bridge.
- ComfyUI 0.34 with MiniMax H3 (talking clips) and ACE-Step 1.5 (music); ComfyUI 0.41 with Flux 3 Klein (images). One GPU job at a
  time; `tools/comfy_switch.ps1` switches them (set config `comfy_switch` to its path to let the factory do it).
- Face check: ArcFace (`faceid.py`, onnxruntime CPU) in the ComfyUI portable python.

## What is deliberately not in git
Projects, clips, mattes, voice, music, renders, AE projects (all in `work_dir`), keys, `config/local.json`. Everything heavy can be
regenerated from its project file; a finished video travels as a collect (engine/collect.py).
