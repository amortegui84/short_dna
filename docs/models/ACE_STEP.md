# ACE-Step 1.5 (local music)

The default `music` provider (`comfy_ace`, `engine/musica.py`): an instrumental bed for each video, made on the local GPU at no cost.

## Setup
- Runs in the **H3 ComfyUI** (0.34, port 8188, config `comfy_h3`); any ComfyUI with the ACE models works. One GPU job at a time.
- Models: `acestep_v1.5_xl_turbo_bf16.safetensors` (UNETLoader), `DualCLIPLoader` with `qwen_0.6b_ace15.safetensors` +
  `qwen_4b_ace15.safetensors` (type `ace`), VAE `ace_1.5_vae.safetensors`.
- Licence: not recorded in the sources (inferred Apache-2.0 for ACE-Step; verify for the 1.5 XL weights before commercial use).

## Workflow (nodes)
| Node | Settings |
|---|---|
| `TextEncodeAceStepAudio1.5` | `tags`, `lyrics: "[Instrumental]"`, `bpm`, `duration`, `timesignature: "4"`, `language: "unknown"`, `keyscale` (e.g. `D minor`), `generate_audio_codes: true`, `cfg_scale 2.0`, `temperature 0.85`, `top_p 0.9`, `top_k 0`, `min_p 0.0`, `seed` |
| `ConditioningZeroOut` | negative |
| `EmptyAceStep1.5LatentAudio` | `seconds` = duration |
| `ModelSamplingAuraFlow` | shift 3.0 |
| `KSampler` | 8 steps, CFG 1.0, `euler` / `simple`, denoise 1.0 |
| `VAEDecodeAudio` → `SaveAudioMP3` | quality V0, prefix `audio/<slug>_musica_N` |

- Graph is posted to `/prompt`; the script polls `/history/<id>` (3 s, up to ~20 min).
- **Output folder:** ComfyUI's `output/audio/` of the instance that ran it (config `comfy_h3.comfy_dir`); `musica.py` copies the takes to
  `<project>/musica/toma_1.mp3`, `toma_2.mp3` (seeds 101 and 202).
- The chosen take is normalised to **−27 LUFS** (`loudnorm=I=-27:TP=-3:LRA=9`, 48 kHz stereo) as `musica/elegida.wav`; the builder puts
  it under a −20 LUFS voice and fades it out. Swap takes: `python engine/musica.py <project> --elegir 2`.
- Duration: default 80 s (`--dur`). A 118 s cue was generated for a longer story (whether the structure followed the tags was not measured).

## Tags, bpm, key
- Source: `proyecto.json` › `musica {tags, bpm, key}` or the style file (`library/styles/<style>.json` › `musica`).
- Collage style default (approved):
  `dark cinematic documentary score, low cello drone, sparse felt piano, deep pulsing synth bass, subtle ticking percussion,
  mysterious, elegant, modern, serious, slow build, no vocals` — 88 bpm, D minor.
- A tense story cue that worked: "low tense start, rising dread …, no vocals".
- Always end the tags with "no vocals" and keep lyrics `[Instrumental]`.

## The "not childish" lesson
Review note (2026-11-05): *"the song is childish"*. Cause: tags with **lute, recorder (flute), celesta, glockenspiel, pizzicato**, which
read as a children's programme under an art documentary. Fix: cinematic, restrained tags (cello drone, sparse piano, synth pulse,
subtle percussion) and a style-level `evitar` list so no project brings those timbres back. The rejected beds were kept as
`elegida_v1_infantil.wav` for comparison.

## Mixing notes from the experiments
- Music around 0.22 (linear gain) under dialogue, master at −20 LUFS; verify the final mix with Whisper (dialogue must still be heard).
- Ducking under dialogue helped; ducking under the voice-over was still pending.
- Sound effects need their own cue per visual event; a single quiet hit under music is not heard.

## Alternative
Suno through a gateway (`suno` provider, APIS.md): not called yet; commercial use needs a paid Suno plan; normalise the same way (−27 LUFS).

## Status
In use (two finished videos and the art series).
