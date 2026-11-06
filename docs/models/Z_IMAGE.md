# Z-Image Turbo (local, ComfyUI) — superseded by Flux Klein for references

Text-to-image only (no reference images). It was the first source of key frames and presenter faces, and is still the
best tool here for **inventing a new face from text** (masters). For anything that must keep a face, Flux Klein replaced it
on 2026-10-16 (see "Why Klein replaced it").

## Setup
- Runs in the H3 ComfyUI (0.34, port 8188); the Klein install (0.41, :8189) also has it. One GPU job at a time.
- Models: `z_image_turbo_bf16.safetensors` (`diffusion_models`), text encoder `qwen_3_4b.safetensors` (CLIPLoader type `lumina2`),
  VAE `ae.safetensors`. Negative = `ConditioningZeroOut` of the positive.
- Settings from the official Z-Image Turbo template: **9 steps, CFG 1, `ModelSamplingAuraFlow` shift 3**. The experiments used
  two sampler pairs: `euler` / `ddim_uniform` (`zimage_gen.py`) and `res_multistep` / `simple` (presenter pilot). Both worked;
  no A/B between them was recorded.
- Speed: ~6-7.5 s per image (1344×768 or 768×1344).
- Licence: not recorded in the sources (inferred Apache-2.0 from the publisher; verify before commercial use).
- Script (experiments): `zimage_gen.py -p "..." -o out.png [--size 1344x768] [--seed 7] [--lora FILE:strength ...]`,
  or `--spec items.json` for a batch (`{"out_dir", "items":[{"name","prompt","size","seed","lora"}]}`). Do not run QwenStudio at the same time.

## LoRA and character work
- A character LoRA of two real people (trained with their consent, trigger at the start of the prompt) was used to make series key frames.
  Result: fast, but **it cloned a third person in ~30-50 % of frames** (most in standing/wide poses and rooms). Mitigations that
  helped only partly: "Exactly two people in the frame, no third person", chest-up medium shot, the two together, 4 seeds and pick by eye.
  On one 10-frame series it failed 6/10.
- Same seed ≠ same person: a look and a master made with the same seed and profile were different faces. Identity is not fixed by
  Z-Image; fix it afterwards with a reference model (Klein) and check with ArcFace.

## Prompts and realism notes (presenter pilot, 2026-11-02)
- Z-Image gave the most natural skin and a believable age (~30) for a YouTube presenter; backgrounds a little clean and generic.
  Flux 3 on the same prompt: richer rooms and more skin texture, but faces read 35-40 and it opened necklines more than asked.
- Iterations that taught something (same seed per profile):
  - a hires pass + a "real video skin" block → reddened, tired faces (rejected);
  - "influencer" wording → too pretty; naming a softbox or ring light puts the lamp **in** the frame;
  - the middle ground (attractive but real, light make-up) was kept;
  - designer outfits produced fake lettering on garments (keep "no readable text" and check);
  - "no dark roots" fixed two-tone dyed hair;
  - small tattoos come out as outlines or vanish; hair can cover a buzzed side. Keep identity marks simple (a solid triangle, thin bands).
- Klein barely changes a **haircut** (a pixie came back long). To change the cut for real: generate with Z-Image, then fix the face with Klein.
- Non-human presenters (marble bust, robot, 3D animal, clay witch, painted portrait, hologram) were drafted with Z-Image for lipsync:
  frontal bust, big face, defined lips, mouth slightly open, nothing over the mouth. Characters without a mouth (skull, owl) were dropped.
  Fake text appeared on a robot; a hologram got stray hands. H3 lipsync on these characters is **untested**.

## Why Klein replaced it (2026-10-16)
| | Z-Image + character LoRA | Flux 3 Klein multi-reference |
|---|---|---|
| Two-person key frames | 4/10 usable on one series; third-person clones 30-50 % | 20/20 with exactly two people; 9/9 in the first test |
| Wardrobe between episodes | drifts | identical |
| Face from a photo | needs a trained LoRA | 2-10 reference images, no training |
| Time | ~6 s | ~15-24 s |
| Licence | inferred permissive | non-commercial (see FLUX_KLEIN.md) |

ArcFace likeness of presenter shots: 0.37-0.55 with Z-Image looks made without a reference, 0.90-0.94 when Klein used the Z-Image
master as its only reference.

## Where it fits in the pipeline now
1. New character: draft masters with Z-Image (several seeds), user picks one.
2. Everything else (base scene, looks, start frames) with Klein using that master (docs/NEW_CHARACTER.md).
3. Never as a source for a real person's face.
