# Flux 3 Klein (local, ComfyUI 0.41) — multi-reference images

The factory's default `image` provider (`comfy_klein`): character looks (`engine/looks.py`), one start frame per talking line
(`engine/inicios.py`), props and series key frames. It replaced Z-Image + LoRA on 2026-10-16 (Z_IMAGE.md).

## Setup
- **Separate install:** ComfyUI **0.41** at `D:\ComfyUI_QI21\ComfyUI_windows_portable`, port **8189**
  (`python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --port 8189`). Do not upgrade the 0.34 H3 install for it.
  Models are shared through `extra_model_paths`.
- Models: `flux3_image_klein_sd_int8_convrot.safetensors` (distilled, int8), encoder `qwen3vl_4b_int8_convrot.safetensors`
  (CLIPLoader type `flux3`), VAE `flux2-vae.safetensors`.
- **Licence: FLUX non-commercial ("FLUX Kommunity" in the notes).** The weights come from Black Forest Labs' gated Hugging Face repo,
  downloaded with the user's own HF session. Check the licence before any commercial video; `generic_http` is the swap-out route.
- Graph (`engine/klein_gen.py`): `CLIPTextEncode` → `ReferenceMultiLatent` (up to 10 images, each resized to 1 MP; negative =
  `ConditioningZeroOut`) → `EmptyFlux2LatentImage` → `KSampler` **16 steps, CFG 1, `euler` / `simple`, denoise 1.0**.
- Call: `klein_gen.py -p "text" --refs a.png b.png -o out.png [--size 768x1344] [--seed 7] [--steps 16]` or `--spec items.json`
  (`{"out_dir", "items":[{"name","prompt","refs","size","seed"}], "overwrite": false}`).
- Speed: ~12-15 s per image at 768×1344, ~20-24 s at 1344×768 (warm). The non-distilled Flux 3 Base was also tried: 50 steps, CFG 3.5, 50-80 s.
- **GPU:** never with H3 loaded. Switch with `tools/comfy_switch.ps1 klein|h3` and check with `nvidia-smi` that VRAM dropped.
  A 0.41 started with `--cpu` (to read nodes) silently generated on CPU for 30 min: close it before generating.

## The reference-order rule
**`<1>` = the scene / look (room, mic, outfit, framing, light), `<2>` = the face (master portrait).** The prompt talks about "the first
reference image" and "the second reference image" with those roles; the face sentence always points at the second.
- A full-body reference holds its background and pose too strongly (ArcFace 0.92-0.94 but the same picture). A **head crop** as the face
  reference frees the scene (0.72 sofa, 0.60 beach with a turn).
- Prompt = what changes, then the fixed blocks. `looks.py` builds `She now wears {outfit} {pose} {mirada} {identidad_fija}`;
  `inicios.py` builds `{variant} {inicios_mirada} {inicios_fijo}` (all texts in `character.json`).
- The fixed block names everything that must stay, from the first image (room, mic below the chin, LEDs, camera direction), then
  "Her face is identical to the second reference image: same eyes, eyebrows, nose, lips, jaw and skin, with …", the key light on the
  face, and "Realistic vertical 9:16 smartphone video frame."

## Prompt patterns that worked
- **Look (outfit + pose):** one outfit sentence ("She now wears a deep burgundy velvet blazer pinned with antique brooches over a black
  lace-trimmed camisole with a modest neckline."), one pose sentence with hands, camera shift and one room detail, then the gaze line.
- **Head angle:** say the side in image terms, twice: "her head now tilts toward the RIGHT side of the image (the viewer's right), the
  opposite way from the first reference". Klein resists tilting right (long hair falls left); one look only obeyed when generated from a
  **mirrored** reference (the room comes out mirrored too). For a second pass use the look as base: "Change only her head angle: …".
- **Gaze:** "Whatever the head angle, her eyes look straight into the camera lens, making direct eye contact with the viewer."
- **Start-frame variants** must be concrete (camera, head angle, expression, hands): frontal tight close-up; strong three-quarter left with
  the camera shifted right; three-quarter right with eyebrows raised; wider shot with one open palm near the shoulder; head tilted ~20°
  with a low camera and a warm accent light. "A different pose" gives near-copies.
- "Her mouth is relaxed and slightly open as if about to speak" helps the H3 clip start talking naturally.
- **Two people:** "Make a photograph of the man from the first image and the woman from the second image together: <scene and
  clothes>. Exactly two people in the frame, shown from the waist up, both looking toward the camera." → 9/9 and later 20/20 with
  exactly two people, identical wardrobe between episodes.
- **Stylised anchor** (3D/animated look of a person): "refined semi-realistic 3D, realistic proportions, eyes only slightly enlarged";
  avoid "large expressive eyes / smooth soft skin" (likeness collapses).
- Two-phase hybrids: Klein first makes one integrated still of the transformed character in a real place, then H3 animates that still.

## Results
- Presenter shots with the master as only reference: ArcFace 0.90-0.94; outfits 0.95-0.98; hairstyles 0.74-0.97 (fringe over the face is
  the worst). Start frames with the head turned: 0.68-0.86, accepted; 0.90 is not reachable at three-quarter angles. Approved looks: 0.84-0.90.
- Colour changes of hair work (lime, blue, violet, platinum …); **cuts barely change** (pixie and mullet come back long).

## Pitfalls
- `klein_gen.py` skips files that already exist: move old candidates to `descartados/` before regenerating.
- Expression stays similar across shots and "close-up" does not get very close: name it.
- Klein shrinks or drops small tattoos and can add a second one on the other side; keep marks simple and check.
- Klein's character *sheet* copied a face badly: for an H3 character anchor of a real person, a single H3 frame (`--seconds 0.21`) with the
  real photo worked better. Real faces in H3 always come from the real photo, never from a Klein image.
- Rejected by review (keep in `nunca`): mesh or see-through clothing; crossed or interlaced hands (fingers deform); anything over the face;
  the same head tilt in every look.
