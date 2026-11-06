# QA before sending

Automatic (the `render` and `qc` stages write `qa_render.json` and `qc.json`):
- black frames: `ffmpeg -vf blackdetect=d=0.04` → 0 (one frame counts);
- loudness: -20 ± 1.5 LUFS integrated, true peak -1.5 dBTP;
- motion: Motion DNA `tools/motion_qa.py`: jumps at y ≈ 0.73 are subtitle changes; the artist card's colour blocks and the quote's slab
  sweep are intended; explain anything else;
- transcript: Whisper of the final video vs the script ≥ 0.85;
- layout: Motion DNA `check_layout` + the builder's own check with real sizes (labels in the safe area, away from the face boxes).

By eye (`render_frame` in AE, or ffmpeg frames from the mp4):
1. every presenter <-> artwork cut is under the stripes, with no empty colour frames;
2. every slide shows both artworks moving, no pop on arrival, no overhang;
3. the same artwork is never split by a transition;
4. detail cards: on the side her hand opens to, above her, never over the face, ≥ 1.5 s visible;
5. the artist card never shows empty; the quote reads word by word with the voice;
6. no artwork altered; titles and dates right (research.md);
7. listen to the first line, one voice-over line, the music under the quote and the end.

Say plainly in the delivery what was measured but not watched or heard.
