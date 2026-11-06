# Qwen image models (local)

Three Qwen tools appear in the experiments. None is in the factory's default path today; they are optional helpers for cut-outs,
style transfer and face refinement. Qwen's VL encoders also sit inside other models here (H3 uses `qwen3vl_32b`, Klein uses
`qwen3vl_4b`, Z-Image uses `qwen_3_4b`): that is not a separate tool.

## 1. Qwen-Image-Layered — images with real alpha
- **What:** generates (or decomposes an existing image into) RGBA layers with a 4-channel VAE. Used to cut painted creatures and
  objects out of artworks for collage assets ("the painted creature cut out on a transparent background").
- **Setup:** H3 ComfyUI (0.34, :8188). Graph copied from the official template `image_qwen_image_layered.json`.
  Models: `qwen_image_layered_fp8mixed.safetensors`, encoder `qwen_2.5_vl_7b_fp8_scaled.safetensors` (type `qwen_image`),
  VAE `qwen_image_layered_vae.safetensors`; `ModelSamplingAuraFlow` shift 1.0, `euler` / `simple`.
- **Call:** `qwen_layered.py -p "text" -o out [--img in.png] [--layers 2] [--size 768] [--steps 20] [--cfg 2.5] [--seed 7]`
  → `out_0.png`, `out_1.png` … one RGBA per layer. With `--img` it decomposes that image; without it, it generates from text.
- **Results:** used in the art-asset batches; no quality measurements recorded. For people and artwork portraits the factory uses
  InSPyReNet mattes instead (OTHER_LOCAL.md).
- **Status:** tested.

## 2. QwenStudio style transfer (`/api/estilo`)
- **What:** redraws a photo in the style of another image, to make an *illustrated* reference before a swap on a cartoon source
  (e.g. a real face redrawn in the cartoon's style so the swap fits).
- **Setup:** a separate local app (QwenStudio) at `http://127.0.0.1:7860`, endpoints `/api/estado`, `/api/estilo`, `/api/desmontar`
  (unload). **Never load QwenStudio and ComfyUI H3 together on the 24 GB GPU: it caused two blue screens.** Stop ComfyUI first, call
  `/api/desmontar` afterwards.
- **Call:** `qwen_style.py photo.png style.png out.png --prompt "..." [--seed 7] [--negativo "..."]`. QwenStudio's default negative
  contains "beard"; the script passes its own.
- **Status:** tested once for an illustrated swap reference; not part of this pipeline.

## 3. Qwen-Image 2.1 Edit — localized identity refinement
- **What:** restores a master face/hair onto a generated scene (scene photo from MOSS, see OTHER_LOCAL.md) without touching the rest.
- **Setup:** Qwen-Image 2.1 int8 + `qwen3vl8b` int8 encoder + VAE 2.1 bf16, node `TextEncodeQwenImage21`, in the main ComfyUI install.
- **Recipe (accepted for stills, 2026-10-27):**
  - image 1 = the new scene, image 2 = the approved master; both into `TextEncodeQwenImage21`;
  - prompt states the roles: keep scene, pose, body, clothes and light from image 1; take eyes, nose, lips, jaw, hairline, eye and hair
    colour from image 2; do not add acne, do not smooth skin;
  - 40 steps, CFG 1, `euler` / `simple`, same resolution; `VAEEncode` of the base + `SetLatentNoiseMask` (head/hair ellipse from face
    detection, feathered 14 px), denoise 1.0; decode and composite only the masked area over the base.
  - Never chain results as identity references: every new scene goes in with the **same** approved master.
- **Results:** ArcFace vs master 0.61-0.67 → 0.87-0.89 on three seeds; pixels outside the mask identical (max diff 0); ~36-44 s per edit.
  Fine features, skin and expression still vary. A QA of 30 stills found Qwen did **not** improve identity consistently (14 up, 13 down,
  3 equal). **Strong profiles fail:** denoise 1.0 turns a side view into a three-quarter/frontal face (0.49 → 0.85 but no longer a
  profile); denoise 0.55 keeps the profile but not the identity (0.51).
- Direct Qwen 2.1 edits with the full original as reference: wardrobe 0.97, sofa 0.88, beach 0.93 (28-36 s); hair/contour closer,
  eyes/mouth/texture still vary; a requested head turn was not clearly obeyed.
- A CPU face-parsing model gave tighter face masks than the ellipse, but its card restricts it to non-commercial research: do not use
  it for commercial work without an alternative.
- **Status:** experimental. For the presenter, Klein with two references (FLUX_KLEIN.md) is the path in use.
