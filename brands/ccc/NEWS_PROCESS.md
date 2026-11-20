# Cool Culture Club: how news videos are made (and artists told as news)

Agreed with the user on 2026-11-20 after the first five news videos (N01, N04, N06, N09, X01) were delivered.
This is the process from now on. Detailed rules live in `D:\short_dna\docs\REACTION_FORMAT.md` (section "MiniMax heads");
symptoms and fixes in `D:\short_dna\docs\LEARNINGS.md`.

## 1. What a news video is
- 9:16, ~45-60 s, English. A floating 3D head (Cap, Locs or Buns) reacts to a real story over real video footage.
- Structure: head big on the hook (A lines 1-2), the footage carries the story with the head off screen (B lines 3-7),
  the head comes back for the punchline and the challenge (A lines 8-10), big again on the last line.
- One **concept shot** per video: the head *inside* the story, made with MiniMax (N04 Buns' head on a Beeple robot dog,
  N01 Cap taped to the Sotheby's wall like the banana, N06 Locs inside the Mona Lisa's frame behind the caked glass,
  N09 Buns painted into Leporskaya's Three Figures, X01 Cap inside the Wu-Tang silver box). It replaces one A line
  (not the first, not the last) and is edited as a full-screen plan, credit `AI-GENERATED`.
- **Some painters are told as news**: when an artist's story has real video (documentaries, museum footage, news
  reports), it is made in this format instead of the collage board. The material search (section 3) decides it.

## 2. Order of work (edit first, generate last)
1. **Script** from `SCRIPTS_20.md` (or a new one with the same blocks). Facts and sources in the project's `research.md`.
2. **Material**: video footage per line in `material/<ID>/footage` with a `.txt` source note each (`MATERIAL_RESEARCH.md`).
3. **Voice** (ElevenLabs, inside the plan): the whole script in one block (`bloques_voz`); pace about 195 wpm max.
   **Never stretch a voice** (rubberband made Buns "sound odd"): set the speed at generation (`character.json` /
   `proyecto.json "voz_ajustes"`, Buns 0.9).
4. **Edit with a still head**: `reaccion_voz.py --slots`, plans in `reaccion.json`, build in After Effects
   (`build_reaccion_ae.py --render`). The user reviews this edit.
5. **Only when the edit is OK**: write `minimax.json` (acting per line + the concept shot) and generate the heads:
   `engine/minimax_cabeza.py <project>` (dry run, prints the cost) → quote it → `--pagar` → `--montar`.
6. **QA** (all mandatory): audio in the render (`qa_audio.py`, `qa_audio_render.py`), cuts/flashes/black
   (`qa_cortes.py`), reading pace (`qa_lectura.py`), a contact sheet of every 2 s, the small-head edge check (section 4).
7. Video to `revision/<date>/`; after the user approves, to `entregas/<date>/`, plus the After Effects collect
   (section 6).

## 3. Finding material
- Real video first (news reports, museum walkthroughs, court/CCTV, auction footage); photos only where no video exists.
- Each clip: source, URL, licence note, line it covers. Credit on screen (`VIDEO: <SOURCE>`).
- A story without usable video for most B lines is not a news video: it goes to the artist (collage) format.

## 4. MiniMax heads on fal (2026-11-20)
- Model: MiniMax H3 Max on fal. USD 0.08 a second at 768P (fal price page). Paid: quote before generating.
- **One generation per host line**, our ElevenLabs voice pinned (`target_audio_url`). The prompt carries the exact
  words, the delivery and the acting (MiniMax gives the acting from the words + the direction).
- Lines up to 6 s: `reference-to-video` (acting). Longer lines: `lip-sync/image-to-video` (holds the look, less acting).
  Longer than ~6 s reference-to-video changes scene (a body, a jacket, a robot) and is rejected.
- **The first frame is the head alone at 68 % on its own gradient** (alpha from `placeholder_head.png`), never the full
  master: MiniMax leans in during a clip, and a full-size head left the frame and showed cut ears when small
  (N06 33 s, N09 7 s). Pasting the whole master made a visible rectangle that MiniMax copied.
- Every clip is checked: no scene cut, background unchanged, head never touching the clip sides; a failed check retries
  once, then falls back to lip-sync.
- Concept shot: reference-to-video with **no first frame**, Image 1 = head master, Image 2 = a frame of the real
  footage, 9:16, structured prompt (`subject_definitions / summary / detailed_description / avoid: cuts, scene changes`).
  One line, under ~6 s.
- In the edit: a big head whose clip touches its frame edges is scaled until those edges sit on the video's edges (no
  visible cut lines); the background darkens behind the big head only while the head is on screen (never over a
  concept shot); slivers under 1.2 s left around an inserted shot go to the neighbour plan.

## 5. Real cost (first five, 2026-11-20)
| Video | Seconds on screen | Cost on screen | Real cost (with retries) |
|---|---|---|---|
| N01 | 31.7 s | 2.54 | 2.97 |
| N04 | 46 s incl. tests | 3.69 | 4.89 |
| N06 | 23.2 s | 1.86 | 5.76 |
| N09 | 21.4 s | 1.71 | 4.15 |
| X01 | 28.9 s | 2.31 | 2.31 |
| **Total** | | **12.11** | **20.08** |
The N06/N09 overrun was the cut-ears fix. With the margin first frame a news video should cost about USD 2-3.50.
ElevenLabs voices are inside the plan; editing, cut-outs, renders and collects are local.

## 6. Folders and delivery
- `proyectos/<id>/`: everything of a video (`minimax/`, `mates/mm_*.mov`, `reaccion.json`, `reaccion.minimax.json`).
- `revision/<date>/`: videos waiting for the user's review. `entregas/<date>/`: approved videos only.
- `entregas/<date>/collect/<id>/`: After Effects Collect Files of each approved video, cleaned and made light:
  `engine/collect_ae.py` (copy + relink), reduce to the main comp, remove never-visible layers, then
  `engine/optimizar_collect.py` (alpha cut-outs to ProRes 4444 10-bit q9, footage to H.264 with unused seconds black).
  Verified by rendering the collect and comparing with the delivered video (PSNR > 44 dB on every frame).
  WebM is not used: this After Effects does not import it.

## 7. Plan (2026-11-20)
1. The six news left from `SCRIPTS_20.md`: N02 (soup on the Sunflowers), N03 (Salvator Mundi), N05 (gold toilet),
   N07 (AI picture wins the State Fair), N08 (King Charles's red portrait), N10 (child breaks the 3,500-year-old jar).
   Edit first (still head); MiniMax heads only after the user approves each edit.
2. Then ten new news stories (new scripts + material search), including painters whose story has real video.
