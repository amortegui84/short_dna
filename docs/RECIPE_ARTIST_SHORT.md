# Recipe: artist Short (template `artist_short`, style `collage_v10c`)

What the two examples were made with, step by step, with the commands and what to look at. Times are for one RTX GPU.

| # | Step | Command | Look at | Time |
|---|---|---|---|---|
| 1 | Project | `python factory.py new 04_redon --topic "Odilon Redon" --look 05_corse_camisa` | `proyecto.json` | — |
| 2 | Research | Claude + web search → `research.md` | every fact has a source | 15 min |
| 3 | Script | Claude → `proyecto.json` (lines, moments, artworks, titles, quote) | read it aloud: 55-65 s | 20 min |
| 4 | Artworks | `factory.py run 04_redon --only obras` | `obras/` (Wikimedia 429 → it retries) | 1 min |
| 5 | Portrait | `--only retrato` | `retrato_recorte.png` clean edges | 1 min |
| 6 | Start frames | `--only inicios` (Klein) | 5 different poses, eyes to lens, `qa_cara.py` ≥ 0.68 | 5 min |
| 7 | Voice | `--only voz` (ElevenLabs) | 3 takes max per line, Whisper ≥ 0.85 | 3 min |
| 8 | Clips | `--only clips` (H3, up to 3 seeds per line) | transcript 87-100 %; watch one clip | 30-60 min |
| 9 | One voice | `--only sts` then `--only montaje` | timeline total; absolute wav paths | 3 min |
| 10 | Cut-outs | `--only mates` | boom mic kept, hair edges | 10 min |
| 11 | Music | `--only musica` (2 takes) | listen; swap with `engine/musica.py <p> --elegir 2` | 4 min |
| 12 | Build | `--only ae` (AE open, Motion DNA bridge on) | check_layout warnings explained; frames of each cut | 10 min |
| 13 | Render | `--only render` | `qa_render.json`: 0 black, -20 LUFS, jumps explained | 6 min |
| 14 | QC | `--only qc` | `qc.json` ok, `hoja.jpg` | 1 min |
| 15 | Collect | `--only collect` | ~470 MB, 0 missing | 3 min |

## The format, section by section
1. **Hook (A)**: presenter big and centred, the hook as a capsule label at the top; the artwork she names enters as a ~2.4 s full-bleed
   insert under stripes (riser before), then she closes the sentence.
2. **Artist card (B)**: cut-out portrait filling with colour blocks and painter's tools, the name card fading in (name, dates, motto).
3. **Talking lines (A)**: giant key words behind her; when she names an artwork, stripes cover the cut to it full-bleed; labels pop
   on their words; the following voice-over continues on that artwork (no transition) and its title card appears.
4. **Voice-over (B)**: artwork full-bleed, slow drift, title card, holds 1.2 s after the line; between artworks a 1.2 s board slide.
5. **Quote (B)**: kinetic quote on the ragged magenta slab (docs/STYLE_COLLAGE.md).
6. **Closing (A)**: a two-option question; each option's detail card appears on the side her hand opens to; "Drop your answer" CTA.

## Where it goes wrong (and the fix): docs/LEARNINGS.md
