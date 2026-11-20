# QA before sending

Automatic (the `render` and `qc` stages write `qa_render.json` and `qc.json`):
- black frames: `ffmpeg -vf blackdetect=d=0.04` → 0 (one frame counts);
- loudness: -20 ± 1.5 LUFS integrated, true peak -1.5 dBTP;
- motion: Motion DNA `tools/motion_qa.py`: jumps at y ≈ 0.73 are subtitle changes; the artist card's colour blocks and the quote's slab
  sweep are intended; explain anything else;
- transcript: Whisper of the final video vs the script ≥ 0.85;
- layout: Motion DNA `check_layout` + the builder's own check with real sizes (labels in the safe area, away from the face boxes).

Reality (stage `realidad`, before `musica`; `engine/qa_realidad.py <project>`): a review sheet of every evidence image, start frame,
look and three frames of every clip, each card with what it must show. Check each against the checklist in the script's header
(doors per body type, wheels, windshield and steering wheel in front of the driver, five fingers, possible poses, nothing fused or
floating, no fake letters, no smoke or mist on the narrator, the story's year and object), then record `--ok ID...` or
`--mal ID "what and the fix"`. The stage passes only when every item is ok; a redrawn file is checked again.

By eye (`render_frame` in AE, or ffmpeg frames from the mp4):
1. every presenter <-> artwork cut is under the stripes, with no empty colour frames;
2. every slide shows both artworks moving, no pop on arrival, no overhang;
3. the same artwork is never split by a transition;
4. detail cards: on the side her hand opens to, above her, never over the face, ≥ 1.5 s visible;
5. the artist card never shows empty; the quote reads word by word with the voice;
6. no artwork altered; titles and dates right (research.md);
7. listen to the first line, one voice-over line, the music under the quote and the end.

Say plainly in the delivery what was measured but not watched or heard.

## Full bar, both CCC formats (re-QA of the 10 base edits, 2026-11-19)
Every tool finds the delivered render itself (`comun.ultimo_render`: the highest `<slug>_vN.mp4`). Run, per project:
`qa_audio.py`, `qc.py` (Whisper vs script + `qa_audio_render.py`, line by line in the final mix; silent `mudo` lines skipped),
`qa_cortes.py` (flashes < 0.5 s; news format: every plan >= 1.5 s, and a warning for an edit inside the source clip that
leaves a sliver), `qa_lectura.py` (captions merged across the reaction builder's per-frame layers; wpm), plus:
- **music present**: `datos_ae.json` `musica` not empty (the 5 artist v1 edits had none: `build_collage.py` now makes
  `musica/elegida.wav` from `proyecto.json` `musica`); silences under -45 dB inside the video = no music under a pause;
- **voice gaps**: no silence over ~0.4 s between lines (a host line played without its face drops its take's lead-in air;
  voice-over lines drop their trailing air);
- **plans of a news clip** go through `engine/planos_limpios.py <project> [--aplicar]` before the build: a range that crosses the
  source's own edit and leaves a piece under 1.5 s moves up to 3 s, plans under 1.5 s merge into a neighbour;
- **one sheet per video by eye** (every shot at start / middle / end): subject in frame for the whole shot (a bust's head, a
  person at the edge of a 16:9 source: set `foco`; artist works: `proyecto.json` `focos` {stem: [x, y]}), no burned-in text
  cut, no seam of a collage image, cards and captions never overlapping (the reaction builder drops the caption under a
  card; artist captions rise over the slider module's titles), captions never shrunk to a tiny single line (they break in
  two first), no file name shown as a title (`_h264` copies keep the work's title), a portrait card that shows a face
  (`retrato_bricolage.json` must describe the current png), the evidence clip's range shows what the line says.
- **music in the mix, not only in the data**: `qa_lectura`'s "LU under the voice" is computed from datos_ae.json; check the
  render itself (no silence under -45 dB mid-video). ccc.jsx never placed the music until 2026-11-19 (now ducked, levels per edit);
- **source cuts inside the visible 9:16 window**: `planos_limpios.py` also scans the cropped window (scene 0.15) and keeps
  0.06 s away from any cut at a plan's edge (one stray frame of another shot otherwise); after it, check that no two plans
  reuse the same source range;
- **burned-in text of the source** (BBC subtitles, CNN titles, TikTok captions) cut by the crop: pick another range;
- **captions of the news format come from Whisper**: fix misheard names and split numbers with `reaccion.json`
  `cambiar` / `juntar` (Sotheby's, Cattelan, "$100,000", "avant-garde");
- artist format: the host holds >= 1.5 s before a work; the video ends 0.3 s after the last word (`cola_final_s`);
  captions rise to y 1300 over the carousel and slider titles.
- **voice speed** (user, 2026-11-19): ~195 wpm of speech (`qa_lectura` `wpm_medio`) is the target; over ~205 the voice is slowed
  with `ritmo_b` = old × 195 / wpm and `estirar: "rubberband"` (Buns: TTS at 1.15 + montaje 1.08 ran ~275 wpm). Voices the
  user already approved are left as they are.
