# MiniMax H3 (local, ComfyUI)

The talking-clip engine (`clips` stage, provider `comfy_h3`). One model generates **video and audio together**: the presenter
speaks the line with native lipsync. Everything below comes from months of measured local tests; "inferred" marks the rest.

## What it is
- Two diffusion transformers: `ref2va` (reference images / videos / audio → video + audio) and `fl2va` (text or first/last
  frame → video + audio). `h3.py` picks `ref2va` whenever any reference is passed, `fl2va` otherwise.
- Guidance-free: there is no CFG to tune. The only model-side strength lever is `MiniMaxH3SigmaShift` (12.0 video / 3.0 audio).
- Native output ≈ 1 MP at 24 fps: 1344×768 or 768×1344 (`--size WxH` for other multiples of 32). Landscape decodes to 1344×756: read real sizes with ffprobe.
- Licence: MiniMax H3 Community License (recorded for the swap LoRA; verify the base model's terms before commercial use).

## Install
- **ComfyUI portable 0.34.0** at `D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`, port **8188**, listening on
  127.0.0.1 only. H3 and SAM3 nodes are core (`comfy_extras.nodes_minimax_h3`, `nodes_sam3`): if missing, update ComfyUI.
- Always use the portable's `python_embeded\python.exe`. Known good: torch 2.12.0+cu130, CUDA 13.0, Python 3.13.
  `int8_convrot` weights are the cu130 variant; `fp8_scaled` is for cu12x.
- Models (Hugging Face `Comfy-Org/MiniMax-H3`, ~60 GB):

| File | Folder | Size |
|---|---|---|
| `minimax_h3_ref2va_pruned_int8_convrot` / `minimax_h3_fl2va_pruned_int8_convrot` | `diffusion_models` | 21 GB each |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` (text encoder) | `text_encoders` | 15.7 GB |
| `minimax_h3_video_vae_fp16`, `minimax_h3_audio_vae_fp32` | `vae` | |
| turbo LoRAs: `minimax_h3_ref2v_turbo_4step_v0.1`, `minimax_h3_fl2v_turbo_4step_v1.1`, `minimax_h3_turbo_v4_step600_ema_pruned_comfyui`, `pika_h3_flex_ref2va_v1_bf16` / `pika_h3_flex_fl2va_v1_bf16` (1.8 GB), DMAD `dmad_minimax_h3_4step_full_critic_comfyui` | `loras` | |
| style LoRA `minidv_lora_h3_v1` (Civitai; licence not recorded) | `loras` | |
| `sam3.1_multiplex_fp16` | `checkpoints` | 1.75 GB |

- Custom nodes only for side routes: `comfyui-videohelpersuite` (any video reference), `ComfyUI-NKD-Basic-Tools` +
  `MaskVidExperiments` (inpainting), `ComfyUI-H3-FunControl` + `comfyui_controlnet_aux` (pose). Check what really loaded via
  `/object_info`, not by folder. Rule from the experiments: third-party node code is cloned to a quarantine folder and audited
  (network, exec, pickle, installers) before it goes into ComfyUI; only `.safetensors` weights.
- Launch with `START_COMFY_H3_FAST.bat` (full path): `--use-sage-attention` (1.62× faster, same quality),
  `--fast fp16_accumulation cublas_ops`, `--cache-ram 40` (keeps the text encoder resident), `--vram-headroom 2`.
  Do not use `fp8_matrix_mult` or `--high-ram`. Cold load ≈ 3-5 min. ComfyUI drops every few hours under load (not diagnosed): relaunch.
- Machine: RTX 5090 Laptop, 24 GB VRAM, 64 GB RAM; only ComfyUI's dynamic weight offload makes 21 GB + 15.7 GB fit.
  **One GPU job at a time**: H3 (0.34, :8188) and Klein (0.41, :8189) never together (`tools/comfy_switch.ps1`).

## How the factory runs it
`engine/clips.py` calls `h3.py` in the portable's `h3\` folder (config `comfy_h3.h3_script`). **That copy reads `H3_SAMPLER` and
`H3_SIGMAS` from the environment; the older copy in the experiments folder ignores them** (it always uses `res_multistep`).

```
set H3_SAMPLER=lcm
set H3_SIGMAS=1.0, 0.972973, 0.923077, 0.8, 0.571429, 0.333333, 0.0
python h3.py -p L03.txt --img look.png master.jpg --audio voz_ref.wav --seconds 5.875 ^
  --turbo pika_h3_flex_ref2va_v1_bf16.safetensors --steps 6 --no-shift --size 768x1344 ^
  --lora minidv_lora_h3_v1.safetensors:0.9 --gen-audio --seeds 23 -o L03_s23.mp4
```

| Flag | Meaning |
|---|---|
| `--img A B` | reference images → `<Picture 1>`, `<Picture 2>` (factory: 1 = look/start frame, 2 = master face) |
| `--audio F` | voice reference → `<Audio j>` (trimmed to 15 s, loudnorm −18, mono 48 kHz). Factory: 8 s of the video's ElevenLabs voice |
| `--video F --video-audio --video-seconds S` | video reference(s) `<Video k>`; its soundtrack takes its `<Audio j>` *before* the video's label |
| `--gen-audio` | keep H3's generated speech (default with `--video` is to put the original audio back) |
| `--turbo FILE` | replaces the default turbo LoRA. Pika H3 Flex: 6 steps, `lcm`, CFG 1, manual sigmas above, `--no-shift`, no other turbo |
| `--steps N` / `--quality` | default 10 with turbo; `--quality` = 20 steps, no turbo (3-4× slower) |
| `--no-shift` | drops `MiniMaxH3SigmaShift` (required with Pika and the FaceSwap author's flow) |
| `--lora F:s` | extra LoRAs chained after the turbo. MiniDV at 0.9, **without** its trigger `y2km1n1dv` (the trigger prints a date stamp) |
| `--size WxH` | multiples of 32, always equal to the target (without it a vertical job comes out horizontal) |
| `--ref-size match\|max` | `max` = better identity on small faces, slower |
| `--seeds N…` | one file per seed |
| `--upscale`, `--context`, `--spectrum` | latent upscaler (broken, below), context windows (H3 does not support them), Spectrum (−17 to −23 % time, changes composition) |

Label order is wiring order: images → videos (each video's audio label before its video label) → standalone audios.
Change the number of references and you must renumber the prompt.

## Prompt structure (character.json › `prompt_clip`)
```
subject_definitions:
<Subject 1> is the woman from <Picture 1>, ...; her face matches <Picture 2> exactly. <Audio 1> is her voice.
summary:
[reference-to-video generation + audio generation]
A vertical YouTube Shorts clip: she talks straight to the camera about {artista}.
retention_analysis:
<Subject 1>: fully_preserved (face, hair, tattoos, outfit, body proportions)
detailed_description:
<camera, framing, room, light> ... While speaking {accion}.
<Subject 1> (S1) says in a warm, natural, conversational American voice: <d>[English] {dialogo}</d>
overall_soundscape:
Quiet room tone. Only her voice, clear and close to the microphone.
non_diegetic_music:
N/A
```
- `(S1)` must be the same subject as `<Subject 1>`; a mismatch put one person's voice in the other's mouth.
- The language tag drives accent: `[Spanish]` pushed toward a generic accent; the real accent comes from the voice reference.
- Always write the sound sections. Without them H3 invents a loud soundtrack (measured −22.9 dB mean, peaks −1.9 dB).
- Name the light **in the reference image**, not only in the prompt: references pass their lighting on (studio photo → ad look).

## What works and what fails
- **Lipsync is native and driven by the audio in the latent**, not by who is speaking. Anyone on screen mouths it. There is no
  "ignore audio" mode. Listening shots need silent audio in inpainting; in recreation there is no fix.
- **Ellipses make H3 invent words in the pause** → `clips.py` replaces `...` with commas.
- **Text outside `<d>…</d>` can be spoken aloud** (stage directions) → keep all directions outside the dialogue tag and the dialogue
  only inside it; one experiment added "She says nothing else."
- **Duration grid: 17k+5 frames at 24 fps** (4.46, 5.17, 5.875, 6.58, 7.29, 8.0, 8.71, 9.42 s …). Off-grid values are rounded and
  rounding down clips the end. `clips.py` takes the first grid value ≥ words / 2.7 + 0.8 s. To hit an exact length: pad by
  cloning the last frame, generate, trim.
- **≤ 8 s per pass.** 192 frames = 9-12 min; 226 frames (9.4 s) = 50 min. 10 s is the hard ceiling with a video reference (16 s hangs).
- **Seeds:** the seed dominates (n=1 benches are noisy). Re-roll before re-engineering; change one thing at a time. The factory tries
  seeds 23, 24, 25 and keeps the first with Whisper transcript match ≥ 0.85 (language must be `en`), else the best.
  If four seeds mis-say a word, change the word, not the seed.
- Medium / close framing only; wide shots deform faces. Give the subject an action (a static "state" prompt opens on ~0.7 s of an
  invented shot). Name wardrobe and hair in every prompt of a series, or they drift in close-ups. Do not name what must not appear.
- Ghost third person with two face references: re-seed and do not open on that shot.
- **Latent upscaler (`--upscale`) does not work here**: three set-ups gave unchanged or colour-noise output; a 2 MP pass took ~2500 s
  and drops a cloned voice. Generate at 1344×768 / 768×1344 and upscale afterwards (untested here).

## Extend, swap, pose: real limits
- **Extend** (`extend_clip.py`): next chunk is guided by the last 22 frames (0.92 s) of the current one (`--guide`), same refs,
  size and seed, LAB colour match, 22-frame blend, 0.25 s audio crossfade. Measured 8 → 15.08 s (1 extension) and 22.17 s
  (2 extensions) with no visible identity drift; ~9 min per extension; audio comes out 32 kHz at about −33 dB (normalise).
  Each chunk must be one continuous shot ("one single continuous shot with no cuts"): `[Shot N]` cuts inside a chunk become hard jumps.
  4+ chunks not measured.
- **Swaps** (for reference; the factory's presenter is generated, real people only with consent):
  Character Swap LoRA `h3_character_swap_pro4500_1000` @1.0 (akatz-ai, after the turbo, 10 steps, `--ref-size max`) keeps the plate
  but replaces a *type*, not a face: works when original and replacement look very different. Head Swap LoRA
  `minimax_h3_head_swap_v1.0_r32` with the clip as `--guide`, 4-5 s windows. FaceSwap LoRA barely changed identity.
  SAM3 inpainting (`h3_swap.py`): `--denoise 0.85` keeps lips (1.0 destroys lipsync), silently does nothing above ~124 frames,
  one person per pass, put the neck in the detection text.
- **Pose transfer** (`h3_pose.py`: DWPose skeleton → `H3FunControlApply`): runs, but recreation with `--video` was measured better.
- RefMod (`ComfyUI-MiniMaxH3Mod`, stored references) does not transfer the voice; the Director-Enhanced timeline node is installed but adds
  little over cutting in the edit.

## Timings (RTX 5090 Laptop 24 GB, 8 s unless noted)
| Config | Time |
|---|---|
| turbo ref2v v0.1, 10 steps, 1344×768 | 8.2 min |
| turbo v4 EMA, 8 steps | 7.3 min (−11 %), cleaner; candidate default for new people, not for swaps |
| DMAD 4 steps (bench) | 242 s vs 437 s, slightly better fidelity |
| Pika H3 Flex 6 steps, ref2va | 11 min with a cold load |
| Factory talking clip (Pika, 768×1344, ~5-6 s) | ~6.5 min each |
| Character Swap, 8 s, 10 steps | ~12 min |
| SAM3 inpainting shot | 2-3 min |

## Lipsync pipeline decision (the important one)
Keep H3's own speech (perfect lips) and change its timbre to the video's voice with ElevenLabs speech-to-speech (`sts.py`):
0 ms offset, correlation 0.92-0.95. Muting H3 and stretching the ElevenLabs voice-over on top made the lips miss and "the voice isn't hers".
