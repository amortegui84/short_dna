# Reaction format ("Cult Pixel Reacts")

The narrator, cut out with no background, talks to the lens like someone who films himself hands-free (the TikTok
"green screen" video), while the real news footage plays behind him. About 60 s, 9:16, mostly real video, one open mystery.
First episode: `brands/cult_pixel/proyectos/r01_sky_jellyfish` (Reacts 01, published 2026-11-15). Three versions were
reviewed; every rule below comes from those reviews or from the research on the genre (sources at the end).

## The five rules that make it work
1. **Keep the mystery open** (BIBLE rule 15). The official explanation is quoted as someone's claim and answered by what
   escapes it: the witness, the silence of an institution, what nobody has shown. No debunk footage, no "most of them are
   kites", no verdict that closes it. The ending is a question. Facts stay true: never deny or invent an answer.
2. **He looks self-recorded.** Selfie framing (head and chest), a small lavalier mic clipped to the robe, talking to the
   lens the whole time, hands that react. New narrator clips every episode (never reuse footage).
3. **Video first, he never covers it.** What we talk about sits in the upper half; cards between it and his head;
   subtitles just above the hood.
4. **Cuts, not fades.** Hard cuts between his clips, every other one punched in 7 %. Where a cut would jar (and on the
   "look at this" beats), he ducks out of the frame, the footage plays alone, and he comes back up. Never a cross-dissolve
   between two narrator clips (it shows two masks at once).
5. **Credit everything on screen** and keep each third-party excerpt short.

## Step by step (one project folder, like any episode)
| # | Step | How | Check |
|---|---|---|---|
| 1 | Research | `research.md`: the story; every clip with date, place, who filmed it, licence and URL; 3-6 real public comments (exact text under 25 words, URL, likes; never a private person's handle); the official statements | at least one public-domain or CC source besides the viral clip |
| 2 | Download | `obras/_raw/` with `engine/descargar.py` (yt-dlp `--impersonate chrome`, `-f "bv*[height<=1080]+ba/b"` for YouTube or it falls to 360p; gallery-dl for posts; Wikimedia/DVIDS direct) | contact sheet of every clip with timestamps; note where the object is (x, y as fractions) and which seconds carry watermarks, logos or news tickers |
| 3 | Original sound | Whisper on each clip (`comun.palabras`) | pick 1-2 witness phrases to play alone (e.g. "It's moving very weirdly") |
| 4 | Script | `proyecto.json`: `"formato": "reaccion"`, all lines type A, `tts` with v3 tags, `accion` = gesture + "small black lavalier microphone ... keeps talking to the lens the whole time", 2+ lines `"idea": true` | `python engine/qa_guion.py <project>`: 140-155 words, ideas check, no failures |
| 5 | Voice | `tts.py` then `montaje.py` (same voice settings as the episodes: v3 by blocks, rubberband 1.6x) | `qa_lineas` ok |
| 6 | Voice track | set `"reaccion_huecos"` (silence before a line, for the original sound or the replay), then `python engine/reaccion_voz.py <project> --slots` | it prints line starts and every word's time; read the WARNINGs about slots longer than a clip |
| 7 | Narrator | `inicios.py` (start frames from `"inicios_variantes"`, each with the lav mic), `vo/voz_ref.wav` (8 s of the voice), `CLIPS_SEEDS=23 clips.py`, `mates.py` | look at the start-frame sheet and the clip sheet: same mask, facing the lens, mic visible, no table edge in the chest crop |
| 8 | Plan | `reaccion.json` (schema below): footage cut on the words, cards, `grande` and `fuera` spans | stills: `python engine/reaccion.py <project> --cuadro <s> out.png` at every cut and card |
| 9 | Music | `musica.py <project> --dur 70` (local ACE-Step); `"musica": "musica/elegida.wav", "musica_db": -10` | voice clearly above it on a phone speaker |
| 10 | Render | `python engine/reaccion.py <project>` (~8 min for 60 s), then two-pass loudnorm to -14 LUFS, crf 22 -> `<slug>_pub.mp4` | ebur128 -14.0, `blackdetect=d=0.04` = 0, contact sheet, a sheet around one jump cut and one exit |
| 11 | Publish | `tools/publish_release.py`, posts.md entry (caption with credits + "the narrator is AI-generated"), IG Reel + IG Story, YouTube (AI label), TikTok | only after the user saw the cut or said to publish it |

## reaccion.json
```json
{"slug": "...", "voz": "vo/voz_reaccion.wav", "duracion": 60.4, "cinta": "TAPE R01 - CULT PIXEL REACTS",
 "musica": "musica/elegida.wav", "musica_db": -10, "y_sub": 915,
 "host": {"clips": [{"mate": "mates/L01.mov", "ini": 0, "fin": 6.09}],   // from reaccion_voz.py --slots
          "alto": 960, "x": 0.34, "pecho": 0.62, "alto_grande": 1500,
          "grande": [[0, 2.0], [52.2, 56.0]],     // he fills the frame: the hook and the verdict
          "fuera": [[14.0, 16.6], [46.9, 52.1]]},  // he ducks out (0.3 s) and comes back (0.4 s)
 "planos": [{"src": "obras/_raw/clip.mp4", "ini": 0, "fin": 2.4, "desde": 21.0,
             "modo": "full|caja", "zoom": [2.0, 2.3], "foco": [0.86, 0.78], "foco_fin": [0.83, 0.75],
             "y_obj": 0.22, "subir": true, "vel": 0.5, "congelar": 0.0, "audio": 0,
             "credito": "VIDEO: ...", "marcas": [{"tipo": "circulo", "x": 760, "y": 545, "r": 150, "t": 16.2, "hasta": 19.3}]}],
 "tarjetas": [{"tipo": "titular|cita|comentario", "texto": "...", "autor": "...", "fuente": "...", "ini": 2.6, "fin": 5.8, "y": 440}]}
```
- `foco` is where the subject is in the source (fractions); `y_obj` where it lands on screen (0.22 = upper part).
- `modo` "full" fills the frame (vertical clips, or a 16:9 clip cropped to its subject); "caja" shows a 16:9 clip whole,
  full width around y 540, over a dark blurred copy (thermal/military footage, wide launches).
- `subir` (default on): a vertical clip that cannot pan its subject up is lifted, the strip behind the host is filled.
  Turn it off for 16:9 sources cropped to "full" (the subject went off the top).
- `audio`: dB of the clip's own sound (null = muted). Use 0 only in a voice gap, for the witness's own words.
- `congelar`: seconds into the plan where it freezes (with a 4-frame flash). `vel` 0.5 = slow-motion replay.
- Cards: `titular` (headline, Impact on paper with a dark source bar), `cita` (serif quote on ink), `comentario` (mono on
  paper, red rule). Default y 560; tall headlines at ~440.

## Layout (1080x1920)
- Clean area for every text: x 65-888, y 288-1248 (the Shorts/Reels UI covers the bottom 672 px and the right 192 px).
- Host: head and chest only, ~960 px tall, x 0.34, cut by the bottom edge; big = 1500 px centred, footage darkened 55 %,
  subtitles drop to y 1560. Size changes are a 0.7 s Settle move, never a cut. A small corner host (720 px) was rejected.
- Tape texture only inside his silhouette (alpha-masked) and on the frame edges; cut-out edge choked 1 px, feathered 2 px.
  Real footage is never filtered.
- Subtitles Impact 78, bone white, current word mask-yellow, black bar, y 915; a chunk never ends on a small word.
- Credit of the footage: Courier, top-left, y 250; tape header "REC ... counter" at y 205.

## Beats (~60 s, 140-155 words, 143 wpm)
| Time | Beat | Notes |
|---|---|---|
| 0-2 s | Hook, host big, over the strangest frame | an open question or a fact nobody can explain |
| 2-15 s | What happened, when and where (year + place in the first lines), the moment it appears | headline card with its outlet and date |
| 14-21 s | "Look at this": the witness's own sound alone, a punch-in, a slow-motion replay | host ducks out here |
| 21-40 s | The claims: official explanation quoted, answered by the witness / the silence; a second case | quote cards side by side |
| 40-52 s | His idea (lines marked "idea"): what doesn't add up | real comments as cards |
| 52-56 s | Verdict, host big: a doubt, not an answer | |
| 56-60 s | A question that loops to the first line | |
A visual change every 2-4 s (cut, card, zoom, freeze, exit, resize): 18-25 a minute.

## Audio
Voice lines at -20 LUFS before mastering; the witness's original sound at 0 dB only inside a voice gap; music -10 dB from
its -27 LUFS file; master -14 LUFS, -1.5 dBTP. Strip any broadcast music from news clips.

## Third-party footage (practical rules, not legal advice)
- He narrates over at least 80 % of the runtime; each excerpt 2-6 s (10 s at most); third-party footage under ~40 % in
  total if possible (Reacts 01 was ~50 %, because the viral clip is the subject); never an outlet's whole segment.
- Transform (crop, punch-in, freeze, circle, speed) and credit on screen. Prefer public-domain footage (AARO/DVIDS, NASA)
  and CC (Wikimedia, with licence and author in the credit).
- Viral clips sold through agencies (Storyful, ViralHog, Jukin) can get Content ID claims: expect it, keep excerpts short.
- Avoid news tickers and channel logos in frame (crop them out with `zoom`/`foco`); avoid AI-generated "versions" of a
  case (the TMZ jellyfish was flagged as AI on Metabunk).
- The caption says the narrator is AI-generated and lists every source.

## Pitfalls already paid for
| Symptom | Cause | Fix |
|---|---|---|
| Dark box with scanlines around him | texture on his whole bounding box | alpha-masked texture (`textura(..., mascara)`) |
| Two masks on screen at a cut | 5-frame cross-dissolve between clips | hard cut + 7 % punch-in, or a `fuera` span |
| Subtitles on the mask | host 1080 px tall, subtitles at 860 | host 960 px, subtitles 915, cards 560 |
| Object hidden behind him | subject centred in a vertical clip | `y_obj` 0.22 + `subir` |
| The script killed the mystery | "fair counter-explanation" beat from generic guides | BIBLE rule 15 |
| Footage of buildings instead of the object | the viral clip pans away in its last seconds | check the contact sheet before picking `desde` |
| YouTube download at 360p | `best[ext=mp4]` picks the progressive stream | `-f "bv*[height<=1080]+ba/b" --merge-output-format mp4` |
| A slot longer than its clip | H3 clips are 9.44 s at most | `reaccion_voz.py --slots` warns; move the boundary or hide it with `fuera` |
| YouTube "throttled" | about 5 uploads a day through Zapier | upload the next day (scheduled task) |

Sources of the genre research (2026-11-15): YouTube reused-content and Shorts help pages; Instagram original-content
updates (2025-2026); vidIQ and CapCut reaction guides; Shorts/Reels safe-zone specs. Numbers are working defaults: tune them
with retention data.
