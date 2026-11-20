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
| 10 | Render | **Delivered edit: After Effects with Motion DNA (rule).** Preview only: `python engine/reaccion.py <project>` -> `<slug>_PREVIEW_python.mp4` (~8 min for 60 s), then two-pass loudnorm to -14 LUFS, crf 22 -> `<slug>_pub.mp4` | ebur128 -14.0, `blackdetect=d=0.04` = 0, contact sheet, a sheet around one jump cut and one exit |
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

## Brand looks (reaccion.json "estilo")
The compositor defaults are Cult Pixel (VHS texture on the host, Impact captions, REC header). Any brand overrides them:
```json
"estilo": {"sub_fuente": "Poppins-SemiBold.ttf", "sub_tam": 58, "sub_mayus": false, "sub_color": [246,232,215],
           "sub_activa": [227,147,54], "sub_barra": null, "sub_borde": 5, "tinta": [30,23,20], "papel": [240,232,221],
           "acento": [227,147,54], "rojo": [250,86,57], "titular_fuente": "Poppins-Bold.ttf",
           "mono_fuente": "InterTight-Medium.ttf", "cita_fuente": "InstrumentSerif-Italic.ttf",
           "textura": false, "cabecera": false, "corte": "salto"}
```
`corte` "salto" = Cool Culture Club's cut: every new host clip lands 9 % big and settles to 2 % in 4 frames. "punch" =
every other clip 7 % bigger (Cult Pixel). CCC has no music in the export (it is added in the app).

## Host with a mouth (lip sync, Cool Culture Club)
- No TTS: `clips.py` makes H3 speak each line (up to 3 seeds, transcript QC), `sts.py` turns that speech into the series
  voice, `montaje.py` cuts each line's window (`t0`), `mates.py` cuts the head out.
- `reaccion_voz.py --slots` starts every clip exactly on its line from its `t0`, and when a clip ends more than 0.3 s
  before the next line, the host ducks out (`fuera`) instead of freezing with a still mouth. Manual spans go in
  `host.fuera_manual`.
- Read the transcript it prints: H3 sometimes inserts words ("the Pied of Thieves") or stutters a line with two options
  ("or best came at?"). Simplify the line and regenerate it (`CLIPS_SEEDS=31,32,33 clips.py <project> L08`), or trim a
  murmur after the last word with ffmpeg `-t`. Keep lines under ~18 words; a voice at 2.6 words/s cannot be sped up.
- Layout for a head (review 2026-11-15: "in the centre it does not work, it should be to one side so the video shows"):
  `"host": {"alto": 760, "x": 0.26, "pecho": 1.0}` with `"y_sub": 1300, "x_sub": 0.68` (captions beside the head) and
  cards at y ~835. Prefer `"modo": "caja"` for 16:9 news footage: the whole frame reads ("some shots are cuts where you
  cannot tell what it is"); crop to "full" only on a clear subject (a painting, a face), never on a corner of a frame.

## Haunted places (Cult Pixel; 2026-11-15)
The reaction layout with the narrator small in the bottom-left corner (`alto` 720, `x` 0.24, `pecho` 0.62), plus a map:
1. `python engine/mapa_capturas.py <project>/mapa <lat> <lng> --z 3 5 7 9 11 13 15 17 18` (Google Maps, no login, cookies
   rejected, UI hidden; one 1080x1920 screenshot per zoom, map and satellite).
2. A plan `{"tipo": "mapa", "ini", "fin", "z": [3, 18], "etiqueta": "ISLA DE LAS MUNECAS", "sub": "Xochimilco, Mexico City",
   "credito": "MAP DATA (C) GOOGLE", "capturas": [map z3..z9, satellite z11..z18]}` zooms continuously into the place and
   drops a red pin with the name. Give it 3.5-4 s; the satellite z3 has a side panel (start the satellite at z11).
3. Story beats: hook (what is there), where (map), who and when (real archive of the person), the legend, the detail that
   makes it worse, the date it ended, what nobody has proven, his idea, "it is still there", and "Would you go?".
4. `"juntar": [["Sochi", "milko", "Xochimilco"]]` fixes place names Whisper splits in the captions.

## Side host: text as a block beside the head (review 2026-11-16)
When the host sits to one side (CCC), one 3-word line under the footage read poorly; the user asked for "un bloque de
líneas al lado derecho de la cabeza". Set `"sub_bloque": {"x": 540, "y": 1440, "ancho": 480, "palabras": 9}` (and
`estilo.bloque_tam`): each phrase (up to 9 words, broken at sentence ends) wraps left-aligned beside the head, the word
being said in the accent, said words in the subtitle colour, words still to come dimmed. While the host is big or ducked
out the single centred line takes over. Misheard words: `cambiar` [[heard, right]] for one word, `juntar` for two.
Cult Pixel (corner narrator): no big host at the end; he stays small to the last frame (same review).

## Hiding the head on a shot (review 2026-11-16)
"La cabeza no todo el tiempo: en algunos casos esconderla y en otros sacarla." Put `"cabeza": false` on a plan: the host
ducks out when that plan starts and comes back when it ends; touching hidden plans (and `host.fuera` spans) merge into one
exit, so the head never pops up between them. Hide it where the shot is the story (the object, the witness clip, a replay,
a freeze); show it for the hook, reactions, jokes, the verdict and the question.

## The talking-head news voice (three reference Shorts, review 2026-11-16)
The user sent three Spanish talking-head Shorts (CIA astral-projection guide, the Ark guardian of Aksum, the "dinosauroid")
and asked us to learn how they tell the news and how they are cut. What carries them:
1. **A dare in the first line.** "Are you sure X doesn't exist? Stay, this will blow your mind." / "OK, this one is going
   to blow your mind: the Ark of the Covenant." The topic is named in the first 3 s.
2. **Receipts, shown and named.** The official source on screen (the cia.gov page, the document title, the scientist and
   the year) and said aloud: "straight from the CIA's own website, so it's not a hoax". He reads one line out ("I'll read
   it to you") while the text is on screen.
3. **An escalation ladder.** Each beat raises the stakes with a spoken hinge: "and here's the wildest part", "and what
   finishes blowing my mind". The strangest detail is saved for the last third (the guardians' cataracts).
4. **The ending opens it wider.** The last idea zooms out ("if dinosaurs could have become us... why not somewhere else?"),
   then a direct question: "Did you know this? Tell me in the comments."
5. **Images that land on the idea.** Each image appears exactly on the word it proves (the document when he says
   "document", the diagram when he says "diagrams"), stays 2-3 s, and the strangest one fills the screen alone.
**Our own layout stays** (user, same day: "el nuestro funciona"): borrow the storytelling and the image timing, not
their cut. The optional `"titulo"` label exists in reaccion.json but is not part of the Cult Pixel look.
Keep Cult Pixel's own voice (calm, ominous, the masked narrator) and rule 15 (open mystery): borrow the structure, not the
catchphrases or the sign-off.

## Less rational, more open (review 2026-11-16, Reacts 03 v1)
"No ser tan racionales: preguntas abiertas, que realmente nos indique que algo podría suceder." Lines like "Not proof of
anything, just a reminder" or "Maybe it's just age" deflate the story. Replace the hedge with a question that leans toward
the possibility ("What if the mystics weren't imagining it? What if they saw it coming?", "What if it isn't age?") and
end on something that could still happen ("the sun is waking up again"). Facts stay true; claims stay claims.

## Hard cuts and variety (review 2026-11-16, Reacts 03 v1)
- "Nuestro personaje se va de una forma rara, debería ser un corte seco": the host now leaves and comes back on a hard cut
  (default `estilo.salida` = "corte"); the old slide down/up is `"salida": "deslizar"`.
- "Que no sea tan monótono": the v1 cut used one candle photo six times and one eclipse clip five times. Aim for 20-28
  shots a minute, 1.5-3 s each, no asset more than twice, moving footage over stills, and a wider b-roll hunt (blackouts,
  engravings, archive TV) before planning.

## CCC news (N01 test, 2026-11-17): rules from the review
- **Assembled in After Effects with Motion DNA**: `engine/build_reaccion_ae.py <project> --render` (`ae/ccc_reaccion.jsx`).
  `reaccion.py` only makes `*_PREVIEW_python.mp4`, never delivered.
- **Footage is always 9:16 full screen** ("todavía es 16:9"): every plan `"modo": "full"` with a `foco` chosen per shot
  (where the subject is), `"subir": false`. No boxed 16:9 over a blurred copy.
- **No burned-in text cut by the crop**: a news clip with captions or lower thirds (BBC, Guardian, Global News, France 3,
  tweets) is pushed in from the top (`"foco": [x, 0.0], "y_obj": 0.0`, zoom 1.18 for a lower third at the very bottom,
  1.36 for captions at ~80 % height). Check every plan on a still before building.
- **VP9/AV1 footage** gets an H.264 copy for AE automatically (AE imports them as audio only).
- **The head stays to the end of its line** ("se va la cabeza antes de cerrar la escena"): host slots follow the voice
  (`reaccion_voz.py --slots`), the last clip runs to the end of the video, no duck-out at the close.
- **Audio QA is mandatory** (`qa_audio.py`, inside `render_ae.py`): no line ends in speech, no hard drop in the voice
  track. Line windows and Kling per-line cuts are found by sound (`comun.fin_habla`, `inicio_habla`, `inicio_real`);
  re-cut existing takes for free with `kling.py <project> --recortar`.
- **After a line changes length**, every time in reaccion.json moves with the words (map old -> new word times), never
  by hand.
- **Rhythm** ("muchos vacíos y silencios"): `proyecto.json` `"reaccion_hueco": 0.05` between lines; voice-over lines lose
  their leading/trailing air (`reaccion_voz.py`); a long pause inside a host line is cut with `"reaccion_recortes":
  {"L09": [[a, b]]}` (line seconds) and the host clip is split there. Consecutive host lines from the same Kling take join
  with `"reaccion_huecos": {"L02": -0.05}` so the take plays on without a jump. No shot under 1.5 s.
- **Every shot shows its subject from start to end**: check each plan at its start, middle and end on the 9:16 crop
  (a news clip has its own edits inside: a range can start on an empty wall or a ceiling). Pick `desde` and `foco` per
  plan from a sheet of candidate moments.
- **The head never pops**: no scale "landing" on the cuts; a very soft float instead (position wiggle 0.35 Hz / 5 px,
  rotation 0.25 Hz / 0.6 deg, same seed on every clip). Per-line Kling cuts snap to Kling's own camera cuts
  (`kling.py`, scene detection) so a clip never shows 2-10 frames of the other framing; the sound runs on to the end of
  the last syllable over the held frame.
- **The video ends on the head**: the last host clip closes the video (no duck-out at the end).
- Open (asked 2026-11-17): ~28 s of voice-over without the head felt long; whether the head stays (listening) during B
  lines or the scripts spread the A lines more is the user's call.

## MiniMax heads (CCC, 2026-11-20): rules from the review
Full process: `brands/ccc/NEWS_PROCESS.md`. Tool: `engine/minimax_cabeza.py <project> [--pagar] [--solo L02] [--montar]`,
direction in `<project>/minimax.json` ({"acting": {"L01": "..."}, "concepto": {"linea", "ref", "prompt"}}).
- **One MiniMax generation per host line with our voice pinned** (`target_audio_url`); the prompt has the exact words,
  the delivery and the acting. Lines up to 6 s: reference-to-video; longer: lip-sync (longer reference-to-video clips
  change scene).
- **The head never touches the clip sides** ("cortas las orejas", N06 33 s, N09 7 s): first frame = the head alone at
  68 % on its own gradient; every clip is checked (sides, background, scene cuts) and retried, then lip-sync; after the
  cut-out, every small-head span is checked on the alpha before delivery.
- **Big head with clip edges**: scaled until the clip's edges sit on the video's (no straight cut lines).
- **Darkening behind the big head only while the head is on screen**: the ramp toward the next big head darkened the end
  of the concept shot like a fade to black.
- **No slivers around an inserted shot**: a piece under 1.2 s goes to its neighbour.
- **No jump between two plans of the same subject** (N04 13 s: two Picasso-dog shots from different moments): one
  continuous plan inside one source shot.
- **A re-recorded voice gets a new file name for AE** (`voz_reaccion_ae_<size>_<mtime>.wav`): AE kept the old, shorter
  length of a same-path wav and cut the last line.
- After the voice changes, `fuera` is rebuilt from `fuera_manual` (it kept the old times in N04/N09).
