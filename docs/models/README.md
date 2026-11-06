# Models

Every model and service the factory uses or has tried, with what it does in the pipeline. Details, settings and measured limits are in
the file named in the first column. Licences marked "verify" were not recorded in the source notes; check the model card before a
commercial video. Status: **in use** (the factory calls it), **tested** (run here, not in the default path), **experimental**
(partial or failing tests), **planned** (adapter or idea only, never called).

| Model / service | Use in the pipeline | Local / API | Licence / commercial note | Status |
|---|---|---|---|---|
| [MiniMax H3](MINIMAX_H3.md) ref2va + Pika H3 Flex turbo + MiniDV LoRA | talking clips with native lipsync (`clips`) | local, ComfyUI 0.34 :8188 | MiniMax H3 Community License; Pika / MiniDV LoRA licences: verify | in use |
| H3 extend / Character Swap / Head Swap / SAM3 inpainting / pose | longer clips, person replacement | local | as above; swap LoRAs community-made | tested (not in the factory) |
| [Flux 3 Klein](FLUX_KLEIN.md) (distilled int8) | looks, start frames, props, key frames (`look`, `inicios`) | local, ComfyUI 0.41 :8189 | **non-commercial** (FLUX licence, gated BFL repo) | in use |
| [Z-Image Turbo](Z_IMAGE.md) | inventing a new master face from text | local, :8188 | inferred permissive: verify | tested (replaced by Klein for references) |
| [Qwen-Image-Layered](QWEN.md) | RGBA layers / cut-outs of artwork pieces | local, :8188 | inferred Apache-2.0: verify | tested |
| [QwenStudio style](QWEN.md) | illustrated reference for cartoon swaps | local app :7860 | verify | tested |
| [Qwen-Image 2.1 Edit](QWEN.md) | head/hair identity refinement on stills | local | inferred Apache-2.0: verify | experimental |
| [ACE-Step 1.5 XL turbo](ACE_STEP.md) | music bed (`musica`) | local, :8188 | inferred Apache-2.0: verify | in use |
| [MOSS-Image](OTHER_LOCAL.md#moss-image-text-to-image) | scenes and plates without faces | local, ComfyUI 0.42 :8190 | verify | tested |
| [Wan 2.2 Animate](OTHER_LOCAL.md#wan-22-animate) | motion transfer | local | inferred Apache-2.0 | experimental (broken) |
| [SAM3](OTHER_LOCAL.md#sam3-segmentation-and-tracking) | artwork pieces with alpha, inpainting masks | local, core node | Meta SAM licence: verify | tested |
| [Depth Anything V2 vitl](OTHER_LOCAL.md#depth-depth-anything-v2-vitl) | 2.5D depth maps of artworks | local | inferred CC-BY-NC-4.0 for vitl: verify | tested |
| [Contours](OTHER_LOCAL.md#contours) (OpenCV on depth) | pencil-traced outlines in AE | local, CPU | own code | tested |
| [InSPyReNet](OTHER_LOCAL.md#inspyrenet-mattes) | presenter and portrait cut-outs (`mates`, `retrato`) | local | MIT | in use |
| [ArcFace face check](OTHER_LOCAL.md#face-check-arcface) | likeness QA of looks, frames, clips | local, CPU | weights licence: verify | in use |
| [faster-whisper small](OTHER_LOCAL.md#whisper-qc-faster-whisper) | transcript QC, word timestamps (`voz`, `clips`, `montaje`, `qc`) | local, CPU | MIT | in use |
| [ElevenLabs](APIS.md#elevenlabs--in-use-voice) v3 TTS + STS | voice-over and one voice for the whole video (`voz`, `sts`) | API | paid plan for library voices and commercial use | in use |
| [Seedance](APIS.md#seedance--adapter-written-not-called) | b-roll and animated assets | API | per provider terms | planned (adapter, not called) |
| [Suno](APIS.md#suno--adapter-written-not-called) | alternative music | API (gateway) | commercial use needs a paid plan | planned (adapter, not called) |
| [Nano Banana (Gemini image)](APIS.md#google-nano-banana-gemini-image-generation--edit--planned) | reference-based still edits | API | Google terms | planned (tested via Flora in Motion DNA) |
| [Flora](APIS.md#flora--available-not-used-by-the-factory) | multi-model canvas | API / MCP | per model | tested in Motion DNA, not here |
| [Krea](APIS.md#krea--not-used-user-chose-local-only) | Krea images, Seedance reseller | API / MCP | per plan | not used (local only by choice) |
| [fal.ai](APIS.md#falai--reseller-seen-in-motion-dna) | reseller for Seedance, Kling, H3 Max, lipsync | API | per model | tested in Motion DNA, not here |

## Machine rules that apply to every local model
- RTX 5090 Laptop, 24 GB VRAM, 64 GB RAM: **one GPU job at a time.** H3 (0.34, :8188) and Klein (0.41, :8189) never together; QwenStudio and
  H3 together caused two blue screens. Switch with `tools/comfy_switch.ps1` and confirm VRAM dropped with `nvidia-smi`.
- Third-party nodes go through quarantine and an audit before installation; only `.safetensors` weights from official repos.
- Real people appear only with their consent; the factory's presenters are generated characters.
