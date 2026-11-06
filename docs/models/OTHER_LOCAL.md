# Other local models and tools

One section each: what it is for, how to call it, status. All run on this machine at no cost; one GPU job at a time.

## MOSS-Image (text-to-image)
- **For:** scenes, places, creatures, objects and montage plates with dense detail. Text only: **no reference images, never for faces**.
- **Setup:** its own ComfyUI **0.42** at `D:\ComfyUI_MOSS`, port **8190** (`comfy_switch.ps1 moss`), custom nodes disabled, shared model paths.
  Models in the recorded recipe: MOSS SFT bf16, Qwen3.5-9B encoder int8, FLUX2 VAE; LoRAs Canon UltraReal (0.6) and a beauty LoRA (0.5),
  trigger `c2n0n`. Licence not recorded: verify on the model card.
- **Call:** `moss_gen.py -p "text" -o out.png [--size 768x1344] [--seed 7] [--preset calidad|equilibrado|rapido] [--estilo grano]`
  or `--spec items.json` (same interface as `klein_gen.py`; `refs` are ignored). Sizes: multiples of 16, 1-2 MP.
- **Settings that were accepted:** 768×1344, 25 steps, CFG 3, ER-SDE / simple, SLG 22/24 from 0.1 to 0.7. ~22 s per image (balanced
  preset), ~40 s (quality).
- **Prompting:** English, natural language; say who takes the photo and what happens; one coherent camera (e.g. 35 mm, 1.5 m, eye height,
  f/5.6, recognisable background); one physical light with a shadowed side; body through weight, posture and fabric folds; subtle skin,
  no "8k / perfect skin / masterpiece". MOSS sometimes draws readable text (prices): keep "no readable text" and check.
- **Status:** tested. Same quality as Klein on scene prompts, more density. Not in the factory path.

## Wan 2.2 Animate
- **For:** animating a character with the motion of a source video; character and pose enter by separate paths with separate strengths.
- **Setup:** H3 ComfyUI; `Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ`, `umt5_xxl_fp8_e4m3fn_scaled`, `wan_2.1_vae`, `clip_vision_h`,
  `WanAnimate_relight_lora_fp16`. 16 fps, frames = 4k+1.
- **Call:** `wan_animate.py --video dance.mp4 --img character.png -p prompt.txt --seconds 5`.
- **Status:** **broken**, kept for reference (cause not recorded). Use H3 recreation (`h3.py --video`) for motion transfer.

## SAM3 (segmentation and tracking)
- **For:** (a) H3 inpainting masks (`SAM3_VideoTrack`, `SAM3_TrackToMask`, core in ComfyUI 0.34; `sam3.1_multiplex_fp16` in `checkpoints`);
  (b) cutting every piece of one kind out of an artwork (birds, fish, owls) for swarms and flocks in the collage.
- **Call:** `sam3_piezas.py artwork.jpg "bird" out_dir [--umbral 0.5] [--min 900] [--max 40] [--prefijo name]` (node `SAM3Segment`;
  touching pieces split by connected components; each saved as a cropped PNG with alpha). Before an inpainting run:
  `probe_tracks.py --video shot.mp4 --detect "the face of a person"`. Its "empty" label lies on small subjects (2 % of frame area
  threshold): look at the visual map.
- **Status:** in use for artwork pieces (tested); inpainting is a side route. Licence: Meta's SAM licence (verify terms).

## Depth (Depth Anything V2, vitl)
- **For:** a grey depth map of an artwork (light = near) for After Effects Displacement Map (2.5D push) or Luma Key plane separation.
- **Call:** `profundidad.py artwork.jpg out.png [--res 1024]` (node `DepthAnythingV2Preprocessor`, H3 ComfyUI).
- **Status:** tested. Licence (inferred): the Large/vitl checkpoint is CC-BY-NC-4.0; the Small model is Apache-2.0. Verify.

## Contours
- **For:** the longest figure outlines of an artwork as AE shape paths (a pencil traces them with Trim Paths). Uses the depth map: depth
  jumps are cleaner silhouettes than painted edges.
- **Call:** with the portable python (has cv2): `contornos.py artwork.jpg depth.png out.json [--n 6] [--puntos 60]` → N simplified lines
  in 0..1 fractions of the artwork.
- **Status:** tested (used in the collage builds).

## InSPyReNet mattes
- **For:** the presenter cut-out of every talking clip (`engine/mates.py`) and the artist portrait cut-out (`engine/retrato.py`).
- **How:** Motion DNA `tools/video_matte.py` in the ComfyUI embedded python (`transparent-background` + CUDA); checkpoint
  `models/RMBG/INSPYRENET/inspyrenet.safetensors`, converted once to `.pth`. Video → ProRes 4444 with alpha (factory: 1080×1920, 24 fps,
  `mates/Lxx.mov`); still → PNG with alpha. The boom mic stays in the cut-out. `cajas.py` then writes face boxes so labels avoid the face.
- **Collect tip:** re-encode mattes with `prores_ks -profile:v 4 -qscale:v 11` (~6× lighter, alpha SSIM 0.99997).
- **Status:** in use. Licence MIT.

## Face check (ArcFace)
- **For:** likeness QA of looks, start frames and clips against the master.
- **How:** `engine/qa_cara.py --ref master.jpg files… [--fps 2] [--json out.json] [--panels 3 sheet.png]`, portable python
  (cv2 + onnxruntime on **CPU**, no GPU). Detector + recogniser from `faceid.py` (folder in config `face_check.faceid_dir`).
  Measures presence (% frames with a face), likeness (cosine of the face **most similar** to the reference, not the biggest),
  face size and minimum likeness. Reading: > 0.55 almost certainly the same person, 0.35-0.55 plausible, < 0.30 someone else.
  PASS = presence ≥ 0.80, mean ≥ 0.45, min ≥ 0.20.
- Bars used here: approved looks 0.84-0.90; start frames with the head turned 0.68-0.86; clips 0.76-0.82 (min 0.69).
  ArcFace is a helper, not a percentage of identity: always look at the frames.
- **Status:** in use. Licence of the ArcFace weights not recorded (common InsightFace packs are non-commercial research): verify.

## Whisper QC (faster-whisper)
- **For:** transcript match of voice-over takes and H3 clips, word timestamps for the timeline, final QC.
- **How:** `faster_whisper` model `small`, CPU, int8 (`engine/comun.py`: `palabras()` with word timestamps, `texto_oido()` with language
  detection; match = `difflib` ratio on normalised words). Runs in the engine's Python (config `python_tools`): the ComfyUI embedded python
  does not have it; call it without `PYTHON*` variables set.
- **Rules:** require detected language `en` (forcing English accepted mis-spoken words); keep ≥ 0.85, else the best of 3 takes/seeds
  (Whisper mis-hears proper names, so never discard everything); cut dialogue windows from word times with ~0.3 s margin; re-check the
  final mix with Whisper.
- **Status:** in use. Licence MIT.
