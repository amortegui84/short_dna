# Learnings

Every item cost a review round or a failed run. Format: **symptom** → cause → fix. Add new ones at the end of their
section the moment a review note arrives.

## Character, looks and start frames
- **The new image is the old one** → `klein_gen.py` skips files that already exist → move old candidates to `descartados/` before regenerating.
- **Every look tilts the head the same way; in the channel grid the videos look like copies** → looks were made from one approved
  pose → spread the head angle across looks (upright, viewer's left, viewer's right) and say it explicitly: "toward the RIGHT side of
  the image (the viewer's right)". One look (denim) only obeyed when generated from a mirrored reference (the room is mirrored too).
- **Variants come out almost identical** → vague prompts ("a different pose") → name camera, head angle, expression and hands per variant
  (`character.json` › `inicios_variantes`).
- **Rejected outfits** → mesh or see-through clothing ("too much"); crossed or interlaced hands (fingers deform) → the character's `nunca` list.
- **Lines that don't look at the viewer feel off** → always add the gaze line: eyes to the lens whatever the head angle.
- **Likeness of start frames 0.68-0.86** (ArcFace vs master) is fine with the head turned; 0.90 is not reachable at three-quarter angles.
  The approved looks scored 0.84-0.90.

- **Smoke drifts across the narrator's mask** → "mist"/"fog" in his place or start frame; H3 animates it into puffs that cross his
  face (review 2026-11-12, ep09) → `comun.sin_niebla` strips mist, fog, smoke and haze from his places, start frames and sets, and
  the character prompts ask for "a warm, dry, still summer night" (naming "no breath vapour" made H3 draw breath puffs under the mask); evidence images keep their mist. The edit also laid a full-frame smoke loop (`humo_volutas`, 22 % screen) over every narrator section: the style flag `"humo_narrador": false` turns it off (Cult Pixel).
- **Cars that cannot exist** (a taxi with five doors and a seat in the door, a car with no windshield and a roof bending behind the
  driver, a "1970 two-door" drawn as a four-door 1980s sedan, a 2000s seat in a 1970 car) → generators drift on vehicles and the
  script's details → name the body ("two-door hardtop coupe, one long door on each side, no rear doors"), the seat ("a wide vinyl
  bench seat, no headrests") and the view; put a narrator in a car seen through the open front door, not through a missing windshield;
  check every frame with `qa_realidad.py` (stage `realidad`).
- **Fake letters on signs, papers and screens** ("1998" on a 1981 cabinet, "Spoal Town" headlines) → Z-Image writes gibberish →
  end the prompt with "no letters, numbers or words anywhere"; for a newspaper show the stack or the paper out of focus.
- **A shot inside the look's own place copies the look** (the dashboard frame became the look's car) → `"inicio_solo_maestro": true`
  on that line draws it from the master portrait alone; `inicios.py --solo L06 L08` redraws just those lines.

- **The narrator sounds flat and rushed** → three causes found 2026-11-12: ElevenLabs multilingual_v2 (tts.py strips [whispers]/[pause]
  tags for v2), the voice sped up twice (speed 1.2 in TTS and atempo 1.15-1.2 in the edit, ~1.4x), one TTS call per line (every
  sentence starts fresh and falls the same way) → eleven_v3, `bloques_voz` (3-4 blocks by beat, cut back per line with Whisper),
  storyteller text (mixed sentence length, one CAPS word, whispers on 1-2 lines, a pause before the reveal), and the speed-up done
  with rubberband (`estirar: rubberband`, 1.6x = 143 wpm, the user's choice): v3 renders this designed voice at ~90 wpm and ignores
  its speed setting; atempo smears a gravelly voice. Measure with `qa_voz.py`.
- **Library shots come out as the same frontal pose** → with the look image as reference, Klein copies the look's composition and
  ignores the framing → library shots are drawn from the master portrait alone and the prompt leads with the framing in capitals
  ("SELFIE FRAMING:", "WORM'S-EYE VIEW:"); never name an object in the place text that should not be drawn ("the phone lies on the
  sand" drew a modern phone in 1980).

- **Archival footage cut in the wrong place** (a burnt-out cockpit shot instead of the F-89 in flight) → a researcher's timestamps are
  guesses → scan the reel before choosing: grab one frame every 6 s over HTTP (`ffmpeg -ss T -i URL -frames:v 1`), tile them, pick the
  stretch, then set `desde`/`hasta`; obras.py reads only that stretch of a remote file.
- **Z-Image draws a "radar scope" as a dish antenna with digital screens** → name the object physically: "the circular green phosphor
  screen of a 1950s cathode-ray-tube radar display, flush in a steel panel; not a dish antenna, no digital displays".
- **A renamed evidence stem breaks the edit** (`salto_noche.jpg` missing) → when replacing an evidence image, rename it in
  momentos_a / obras_b / titulos / visuales / obras_descarga together (load the JSON, never a text replace).

## Talking clips, voice, lipsync
- **H3 invents words in pauses** → "..." in the dialogue → replace with commas. **H3 says stage directions aloud** → text outside `<d>`.
- **Lips don't match and "the voice isn't hers"** → H3 audio muted and the ElevenLabs voice-over stretched with atempo on top →
  keep H3's speech (perfect lips) and change its timbre with ElevenLabs speech-to-speech (`sts.py`): 0 ms offset, correlation 0.92-0.95.
- **Intonation wobbles** → ElevenLabs v3 "Creative" (stability 0) → "Natural" (0.5). Three takes per line, keep the best by Whisper.
- **Whisper mis-hears proper names ("Hilma af Klint")** → never discard every take; keep the best ratio.
- **The narrator "rewinds": his clip plays forward, backward, forward** (review 2026-11-06, Cult Pixel ep04) → a narrator section
  of the edit (his line plus the B lines read over him) lasted 13-14 s while his talking clip lasted 5 s, and `ae/cinta.jsx`
  filled it with a ping-pong time-remap → stage `continuar` (`engine/continuar.py`, after `ae`): new H3 footage from the clip's
  last frame, the narrator silently acting out what the voice says, joined to the clip; then matte and comp again. A section
  still short holds its last frame. Never reuse footage backward; ambient layers (smoke) loop forward only.
- **The narrator looks the same in every episode** → candles and the same poses each time → per episode a new look (pose + prop),
  `proyecto.json` › `mesa` (props on the table instead of candles, in start frames, clips and ending: `comun.con_mesa`) and
  `inicios_variantes` (the episode's own poses).
- **A book appears in the narrator's hands** (ep04 L08 continuation) → the move said he "mimes holding an open book"; H3 draws
  whatever object a prompt names, mimed or not → describe only hand motions and say the hands stay empty (no book, paper, object);
  look at a contact sheet of every `_full` clip before the edit goes out.
- **After Effects: "add ... null" importing the voice** → `montaje.py` run with a relative folder wrote relative wav paths → always pass absolute folders (the factory does).

- **A generated clip collapses mid-take and QC passes it** (ep05 L10_cont1, 2026-11-07): the picture went dark and smeared
  halfway; transcript, loudness and black-frame checks all passed. Cause: H3 drift; nothing measured the picture itself.
  Fix: `comun.clip_roto` (sharpness at 1/4 resolution so VHS grain does not count, plus brightness, both against the first
  frame; broken 0.49-0.60, good never below 0.90); `clips`, `continuar` and survivor endings re-seed a broken take.
- **The smear check rejects good moving-camera takes** (ep14 L02, ep15 L02, 2026-11-13): a walking selfie and a camera
  turned from a bright chart to the dark mask scored 0.43-0.67 and burned four seeds each. Cause: the first frame is not
  the same picture as the rest, so sharpness against it means nothing. Fix: every shot whose framing changes (CH01-CH07,
  push-ins, angles) carries `acerca: true` in `library/tomas/tomas.json` and gets the looser threshold; look at a contact
  sheet before re-seeding a take the check calls smeared.
- **The ending starts from the wrong pose** (ep05 v3): stage `final` runs before `continuar`, so when the last section was
  extended the ending began from the short clip's end. Fix: `continuar` compares the extended clip's last frame with
  `final/inicio.png` and remakes the ending when they differ.

- **"Can not set expression ... property is hidden" on a text Range Selector** (ae/ccc.jsx, 2026-11-07): Units and Based On live
  in the selector's "ADBE Text Range Advanced" group, and setting Units to index hides Percent Start. Fix: leave Units in
  percent, set Based On through the Advanced group, drive Percent Start with an expression.
- **Voice layers fail to import ("add ... null")**: montaje.py stores the wav paths as given on the command line, so a relative
  project path gives relative paths After Effects cannot open. Fix: build_collage.py resolves the voice paths to absolute.
- **Wikimedia downloads: 429 and 400**: full-size originals in a row hit the rate limit, and a hand-built thumbnail width
  (2000 px) answers 400. Fix: ask the Commons API for `thumburl` with `iiurlwidth=1920`, pause between files.

- **Out of ElevenLabs credit (HTTP 401 on R22, 2026-11-19)** → local clone: `"motor_voz": "qwen3"` (engine/tts_local.py, Qwen3-TTS
  0.6B Base from an 18 s reference in brands/<brand>/voces/<voice id>.wav + .txt). Speaker similarity matched real ElevenLabs lines
  (0.99). Three things to know: ALL-CAPS emphasis words are spelled out ("EGYPT" came out as "Ichi Buiti") → tts_local lowercases them;
  it runs a block's lines together with no pause, so a cut fell inside "preaching" → blocks are ElevenLabs-only; it speaks at
  ~150 wpm, so `ritmo_a`/`ritmo_b` must be 1.05, not the 1.6 used for v3 (1.6 gave 220 wpm, a 53 s episode).

- **Two night queues rendered the same episode at once** (R25, 2026-11-20): both chains ran `render_pub.sh r25`, and one
  failed on `PermissionError` deleting `_reaccion_video.mp4` held by the other. Cause: each queue script owned the render.
  Fix: one queue owns each render; before re-rendering, check no `reaccion.py` runs on that project.
- **Editing shots_<key>.json changes nothing until planos.py runs again**: `render_pub.sh` reads the plan planos.py wrote.
  After a subtitle (`cambiar`) or card fix, run `python planos.py <key>` then `render_pub.sh <slug>`.
- **Card credits wider than ~34 characters run off the card** (R22, R25): shorten the `autor` ("NDRE radar expert (1984)").
- **Applio on the embedded ComfyUI Python**: its training and index subprocesses could not import `data_utils`/`faiss`
  (the ._pth file ignores the script folder and PYTHONPATH). Fix: `applio/run_script.py` wraps every `python <script>` call
  from core.py. Its tensorboard 2.21 clashed with ComfyUI's protobuf 5.29: use ComfyUI's tensorboard 2.20.
  A/B on R22: Qwen3 clone alone 0.987 speaker similarity, + RVC 0.989; Whisper equal. RVC adds little over the clone.

## After Effects build (collage style)
- **~5 frames of empty green before an artwork** → the presenter's colour background lived until cut + 0.4 s above the artwork → end it at cut + 0.02.
- **"The same painting split by a transition"** → a voice-over line was its own section with a camera move and stripes, although the
  artwork was the one she had just named → fold the voice-over into the talking section: same artwork continues; a different one
  cross-dissolves 0.9 s; if the last artwork would be seen < 1.8 s, it continues instead of changing.
- **"Fast jumps between artworks"** → full-bleed artworks panned up to 1100 px/s → cap at 70 px/s (x) and 50 px/s (y), zoom 0.8 %/s.
- **"They come in as a cut although you slide"** → the incoming artwork was created at arrival (ini + 0.02), so the slide showed empty paper
  and then a pop → the artwork exists from the start of the 1.2 s slide; each artwork is clipped to its 1080x1920 frame, otherwise a
  landscape artwork overhangs onto its neighbour during the slide.
- **The artwork drifts ~100 px just before the camera move, and looks blurry** → spatial auto-bezier on the CAM position keys overshoots →
  linear spatial tangents on every key.
- **A framed (lamina) artwork gets cut at the edge in a long section** → camera drift proportional to section length (~120 px) → cap drift at 5 s of travel; laminas at 940 px wide.
- **Empty paper for ~1 s before each change** (after adding holds) → sections ended when the voice ended, but the next one starts after the hold → every section lasts until the next starts.
- **A cut from artwork to presenter had no stripes** → stripes were decided by section type; a talking section with a cut *ends on an artwork* → decide by how the previous section ends.
- **Detail cards hidden behind the presenter** → they were created before the heads were moved to the top → move the cards above the heads at the end of the build.
- **"The black appears on the other side from where she points"** → fixed left/right order → put each card on the side her hand opens to (look at the clip), lower, near the hands; never over the face.
- **Cards barely visible** → they appeared 0.25 s before the camera left → show them at least 1.5 s before the section ends.
- **A glitch when the artist is presented** → the name card showed empty for 3 frames, then the text popped → name, dates and motto fade in with the card.
- **"The quote is too basic"** → a static card → kinetic quote (word by word on the voice timestamps, giant type). **"Now it's flat"** →
  it lost the collage details → ragged slab, halftone and paper inside it, tape, paper hand, pencil stroke on the key word, typed author.
- **A magenta slab turns almost black** → Multiply blend on a dark background → normal blend.
- **A grey box appears** → a halftone PNG in Multiply on dark → use it only inside the slab, as a track-matted layer.
- **ExtendScript error "Function found where a Number... is needed"** → a local `var T = []` shadowed the helper `T(L)` → never reuse helper names.
- **Labels out of the safe area** → the safe area for Shorts is x 40-950, y 150-1330, subtitles at y 1400; `check_layout` + the builder's own check with real measurements.
- **A rebuilt brand edit looks cheaper and "faster" than its reference** → the builder was written from a dump of layer names only, so every value was a guess → run `ae/aep_dump.jsx` on a copy of the template (every modified, keyed or expression-driven property, with eases and fonts), write the values to `references/<x>_ae_rules.md`, build from them (CCC Dürer v1, 2026-11-07).
- **A gradient in a template is not always a colour** → in CCC the host ramp is a luma track matte that fades the type wall toward the bottom, and the coral is the wall recoloured by Lumetri → check a solid's role (`IS_MATTE`, disabled) before copying it.
- **A brand font draws as the fallback** → this After Effects reads only `C:\Windows\Fonts`, not per-user fonts → install brand fonts for all users (admin); the CCC builder falls back to Inter Tight and prints a WARN line.
- **An evidence insert on a narrator line never shows** (ep16 L08/L10, 2026-11-13: the Arecibo collapse on "arecibo", the
  flare on "flare") → `momentos_a` keys the insert to a spoken word, and both words came at the very end of the line, so the
  narrator cut ended before the insert could hold → key an insert to a word in the first half of the line, and look at the
  render at that word before calling it done.
- **The voice seems to cut out a few seconds in** (ep13, review 2026-11-13: "14 to 17 s se corta") → `build_collage.py` put
  1.8 s of silence (`FZ`) before the first B line so the title card plays alone; after a fast narrator line that reads as a
  drop-out → `proyecto.json` `ficha_pausa` (Cult Pixel 0.4 s, template default) and the card stays 2.6 s in all (the tagline finishes typing), over the
  first words of the line.
- **The first word of the video sounds cut** (ep13-16, review 2026-11-13: "el de Cooper se corta el audio al inicio") → 
  `montaje.py` strips leading silence (silenceremove) and the first line started on frame 0; players and phones swallow
  the first ~100 ms → the first line now gets a 0.35 s lead-in (`ENTRADA`), words and captions shifted with it.
- **Captions too fast to read on a quick storyteller line** (ep15, 2026-11-13: 6 groups at 22-28 characters per second, one on
  screen 0.36 s) → the merge rule only joined captions under 0.6 s with a gap under 0.35 s → `build_collage.py` also joins a
  caption over 20 cps with the next when the pair fits 40 characters and reads slower, and `cinta.jsx` shows it as two lines
  (`br`), never shrunk.

## Music and sound
- **"The song is childish"** → lute, recorder, celesta, glockenspiel, pizzicato tags → cinematic tags (cello drone, sparse piano, synth pulse), restrained; the style file keeps the default.
- **Sound effects nobody hears** → too few and too quiet under music → a cue for every visual event (`docs/STYLE_COLLAGE.md` › sound), music at -27 LUFS under a -20 LUFS voice.
- ACE-Step saves to the ComfyUI `output/audio/` folder of the instance that ran it (config `comfy_h3.comfy_dir`).

## Bridge, After Effects, render
- **The bridge stops taking jobs after relaunching it** → `ss_bridge.jsx` is a toggle: running it again turns it OFF → check
  `bridge/outbox/_bridge_started.txt` first; run it again only to turn it back on.
- **"No answer from After Effects"** during a long build → AE is still building the previous job (a 340-layer build takes ~10 min) → wait;
  don't queue more jobs or relaunch.
- **A second After Effects launch exits** → the previous instance was still closing → wait until no AfterFX.exe is left, then start it.
- Render with aerender **from a copy** of the project so the original stays editable; encode H.264 CRF 19, AAC 192k, loudnorm -20 LUFS / -1.5 dBTP.

## Collect and handoff
- **Collects of 3.5 GB** → the presenter mattes (ProRes 4444 XQ, ~330 MB per line) → one collect per video with `reduceProject`, mattes
  re-encoded with `prores_ks -profile:v 4 -qscale:v 11` (~6x lighter, alpha SSIM 0.99997): 470 MB per video.
- Never flatten names when collecting (many `L03.mov`): keep the original path under `media/`.

## QA that must pass (docs/QA.md)
- `blackdetect=d=0.04` → 0; loudness -20 ± 1.5 LUFS; Motion DNA `motion_qa.py`: jumps at y ≈ 0.73 are subtitle changes, the rest must be explained.
- Look at frames of every cut, slide, card and the quote before sending.

## Platforms (docs/PLATFORMS.md, with sources)
- **Subtitles at y 1400 may sit under the bottom UI** of YouTube Shorts and Reels (overlays from about y 1248); clear on TikTok. Check in
  each platform's preview before changing the approved style; the union of safe margins is about x 65-888, y 288-1248 (unverified px).
- **TikTok pays Creator Rewards only for originals over 1 minute** → keep TikTok cuts at 61 s or more.
- **Templated AI series risk "inauthentic content"** (YouTube, July 2025) and repost demotion (Meta) → every episode its own script, argument and visuals.
- **Facebook demotes engagement bait, even spoken** ("comment YES") → ask for an opinion ("Genius or fraud?"), never "comment 1 or 2".

- **Wikimedia thumbnail URL returns 400 "Use thumbnail sizes listed"** (ep16, 2026-11-13: `1600px-...svg.png`) → Commons now
  serves only fixed thumbnail widths → `obras.py` rewrites any `/thumb/.../<n>px-` to 1280 or 1920 before downloading.

- **The night runner cannot bring ComfyUI back** (ep16, 2026-11-13 06:30): the 15-hour-old ComfyUI process stayed alive but
  stopped listening on 8188, so the runner's `.bat` relaunch exited at once → stop only that `main.py` process (never AE, never a
  tree) and relaunch the central `START_COMFY_H3_FAST.bat`; restart ComfyUI before a long unattended run.

## App and Claude
- **A one-word reply cost $0.70** → the Agent SDK loaded every connector of the account (~80 MCP servers) → strict MCP config with only
  Motion DNA, Blender and Figma: $0.08; the account's connectors only when the user ticks them.

## Voice for narrators (Cult Pixel, 2026-11-05)
- **"Inaudible because of the effect"** → crypt chain (pitch down, long echo, low-pass) hid the words → keep the voice clean (presence boost, firm compression); mood from the voice and the music.
- **"Too slow for a 1-minute story"** → ElevenLabs v3 ignores `speed`, and designed voices speak ~95 wpm; tags like [slowly]/[long pause] slow it more → use `eleven_multilingual_v2` with `speed` 1.2 (~120 wpm, natural) + 1.1x, pauses capped at 0.4 s. v2 reads [tags] aloud: tts.py strips them for non-v3 models.
- **Dramatic pauses were deleted** → montaje's silenceremove cut every silence > 0.3 s → `conservar_pausas` + `pausa_max` keep pauses up to N s.
- A mouthless narrator needs no speech-to-speech: the line lasts as long as the voice, and the clip ping-pongs if the voice is longer.

## Cool Culture Club: template fidelity, voice, Seedance (2026-11-07)
- **The edit felt cheaper and faster than the reference** → the builder was written from layer names, not values → `ae/aep_dump.jsx`
  dumps every modified, keyed or expression-driven property with its ease; build from those values (brands/<b>/references/*_ae_rules.md).
- **Entries floated** → every key was eased from rest → the template's pop/slide leave at 7.5x the segment's average speed and a drop
  lands at 4x: `easeAll` takes speed multipliers; host settles are Hold keys, art moves are linear.
- **Template art modules (3D carousel, desk scroll, slider, strip)** → reuse them as built: import the .aep, duplicate the module,
  swap the "(swap me)" images, retime its own control. Slide comps must keep the name "Slide 0N" (their expressions read N from the
  comp name) and expressions that name the source comp are re-pointed; unused template items are removed after the build.
- **Black flashes in image transitions** → the template modules' "BG black" and the master background showed between pieces → the
  head's background (teal gradient + coral wall) replaces every black background.
- **A 4-frame close-up before a cut / the host cut before finishing a word** → a punch-in landed 0.13 s before a cut to a work, and the
  cut to the work used the word's start → cut when the naming word ends, keep the host 1.2 s, drop punches less than 1 s before a cut.
- **No image may start and be cut away** → every work stays 1.2 s or more; the template's scroll never rests (cap it at the last named
  work); the carousel's last slide exits after the cut.
- **Head and VO sounded like two voices** → STS lines (host) vs straight TTS (VO): speaker similarity 0.89 between groups →
  `sts.py --vo` passes the VO through the same STS and `igualar_voz.py` EQs it to the host spectrum and levels every line (0.974).
- **The ending looped (ping-pong) and looked odd** → the last host section now runs to the end (style `cola_final_s`) and
  `continuar.py` generates real footage for it with the character's own prompt (`prompt_continuacion`); with Seedance the last clip
  already ends on a generated closing smile.
- **Seedance 2.5 on fal** (`engine/seedance.py`): image-to-video from the approved still, the host lines in two long clips, one clip per
  line cut back out by aligning Whisper's words. Billing = width x height x seconds x 24 / 1024 tokens at USD 0.0214 per 1,000
  (audio included): 9:16 costs ~USD 0.21/s at 480p, 0.46/s at 720p, 1.04/s at 1080p. Each clip took 264 s. With Seedance there is no
  TTS for host lines (montaje skips the missing file).
- **Deep cut QA before every delivery** → `engine/qa_cortes.py`: flashes (a shot < 0.5 s between isolated cuts), flat black areas,
  host shots under 1.2 s, the type wall's motion against the reference.
- **Fonts**: this After Effects reads only `C:\Windows\Fonts` (install brand fonts for all users); a font AE once failed to find stays in
  `app.fonts.missingOrSubstitutedFonts` for the session (check_layout STOP) even after no layer uses it: verify the layers.

### Voice lines silent or cut after the block cut (2026-11-13)
- Symptom: after the new block voice, every line that does not open its block came out silent (ep13 L05/L06, 91 dB down) and
  montaje crashed on an empty Whisper list; before that, words were clipped at 2, 14 and 35 s.
- Cause: the per-line cut used output seeking (`-i take -ss a`), so `afade=t=out:st=...` was read on the take's clock and muted
  the whole line; the valley search window (±0.12 s) was narrower than Whisper's word-time error, so a cut could land inside
  "Then"; eleven_v3 sometimes skips the first words of a line ("His price?") and the block still scored 0.89.
- Fix: input seeking (`-ss a -to b -i take`); valley window ±0.25 s; a join with no recognised word splits by word share; and a
  gate, `engine/qa_lineas.py`, run by tts.py (each line: not silent, edges 15 dB under speech, first and last words heard,
  Whisper match ≥ 0.80 with numbers ignored) that asks the failing block again up to 4 more rounds, then stops the stage;
  montaje runs it again on the cleaned, sped-up lines and stops before After Effects if a line was cut.

### After Effects kept the old length of a re-made voice file (2026-11-14)
- Symptom: ep13 at 1:08, "what he left behind" lost "behind"; L01 lost the tail of its last word too. Every line gate and the
  overall transcript match (0.97) passed.
- Cause: the voice was re-made under the same path (audio/L11.wav) while After Effects stayed open; AE kept the previous,
  shorter file's duration (old take 6.5 s, new 7.4 s) and ended the layer there. The line files were fine; only the render was cut.
- Fix: build_collage hands AE a copy named by content (`ae/voz/L11_<md5>.wav`); collage.jsx reloads every import, checks each
  voice layer's length against the disk and stops if it differs; and `engine/qa_audio_render.py` (run by qc) listens to the
  final MP4 line by line: each wav is located by envelope correlation and every speaking 10 ms frame must be loud in the render
  (12 dB drop for ≥ 0.10 s = cut, words named), plus Whisper on the render against what Whisper heard in each line's own file.
  A gate on the parts is not a gate on the render: always check the file the viewer gets.

### A caption over the narrator's mask during a move (2026-11-14)
- Symptom: ep19 1:13, the narrator lifts the phone and rises through the caption line; for 0.7 s the caption sat on the mask.
- Cause: VHS captions are always at y 1430 (cinta.jsx); a shot that starts low crosses that line.
- Fix: `proyecto.json` `"subs_y": [[t0, t1, y]]` moves every caption starting in that window (y 330 = top, clear of the HUD).
  Check the contact sheet of shots that start low or rise ("grabs the camera", "stands up") before rendering.

### B-line images belong in "obras_b", not in the line's "obras" (2026-11-14)
- Symptom: build_collage crashed "cannot use 'list' as a dict key" at the ae stage (ep17-19).
- Cause: the script builder put `[["stem", "keyword"]]` pairs in the B line's own `obras` list; montaje copies that list into
  timeline.json and build_collage expects plain stems there (or "__cita__").
- Fix: pairs go in `proyecto.json` `"obras_b": {"L03": [["stem", "keyword"]]}`; a line's `obras` holds only "__cita__".
  After fixing it, montaje must run again (timeline.json keeps the old list).

### The hook line needs an image (2026-11-14)
- Symptom: ep17 opened on 2.6 s of black with only captions (blackdetect 1.4-4.0 s).
- Cause: L01 (a B line) had no `obras_b` entry, so the collage had nothing to show under the hook.
- Fix: every B line, and always L01, gets an `obras_b` image; run blackdetect on the render before sending.

### Over-the-shoulder with no prop makes a second person (2026-11-14)
- Symptom: ep23 L10 showed a second hooded figure with a bare hand across the table for the whole clip.
- Cause: shot AN05 ("over his right shoulder... {prop} glowing") got an empty prop ("nothing in his hands"), so the model drew the shoulder as another person.
- Fix: give AN05 a real prop (screen, microfilm reader) or use a plain medium shot from across the table; check every clip for extra people in qa_realidad.

### Props with writing get fake letters when pushed to the lens (2026-11-14)
- Symptom: ep22 L08, the Soviet stamp pushed to the lens carried invented words ("EAOI DCTSSCUE AROA").
- Cause: a printed object filling the frame; the model writes gibberish no matter what the prompt says.
- Fix: hold printed props with their blank back to the lens and let the real document appear as the evidence card.

### aerender hangs when ComfyUI holds the VRAM (2026-11-14)
- Symptom: ep23 render stage sat 40 min with aerender.exe at 0 CPU and an empty _aerender.log; twice.
- Cause: ComfyUI kept the H3 models in VRAM (21 of 24 GB) for the next episode's clips; aerender stalls at GPU init.
- Fix: render_ae.py now waits for ComfyUI's queue to be empty and POSTs /free (unload models) before aerender. Also purge After Effects caches between renders (its disk cache had reached 101 GB).

- **A seated figure seen from behind gets its feet facing the camera** (2026-11-15, ep21 L10 on a cliff edge: back view, yet both boots pointed at the lens instead of hanging over the drop; the user caught it after publishing). Cause: the model draws a front-facing lower body under a back-facing torso. Fix: never frame a seated narrator from behind; use a side profile with the legs hidden below the edge and say in the start frame that chest, knees and feet all face the same way. Check feet and knees in every back or three-quarter view on the reality sheet.
- **aerender hangs before "Launching After Effects" when the -comp name has an apostrophe** (2026-11-15, ep23 "Byrd's": hours at 0 CPU, log with only the version line; ep21 rendered fine at the same time). Fix: build_collage.py strips apostrophes from comp names; render_ae.py waits only 5 min for ComfyUI (the VRAM was not the cause).

### Pages that block the downloader (2026-11-15)
- Symptom: real media failed with 403/401 (Wikimedia originals, Daily Mail, Reuters), JS-only galleries came back empty, social
  posts could not be fetched at all.
- Cause: the old User-Agent read as a script and Python's TLS fingerprint is flagged by bot walls; galleries load images with
  JavaScript; X/Instagram/Reddit need their own extractors.
- Fix: `engine/descargar.py` (used by `obras.py`): plain HTTP with a descriptive UA, then curl_cffi with a Chrome fingerprint,
  then the Wayback copy (`id_`); a 429 waits for `Retry-After`. yt-dlp runs with `--impersonate chrome --sleep-requests 1`;
  `obras_descarga` entries take `"galeria": N` (gallery-dl, N-th file of a post) or `"de_pagina": N` (Playwright, N-th biggest
  image of a JS page). A direct video that blocks ffmpeg is downloaded whole and cut locally. Cookies only from the user's own
  browser, opt-in (`SHORTS_COOKIES_BROWSER`). Tested: Wikimedia 403 -> ok, Daily Mail 403 -> ok, Reuters 401 -> Wayback ok.
- Never: CAPTCHA solvers, other people's accounts, proxy pools. A challenge wall is reported for a manual download; a page
  that only has a reCAPTCHA in a form is not a wall (match the title, not the word "captcha").

### Reaction format: a dark box around the narrator (2026-11-15)
Symptom: a darker rectangle with scanlines around the cut-out narrator. Cause: the tape texture (scanlines + noise) was applied
to his whole bounding box, not to his silhouette. Fix: `reaccion.py` masks the texture with the cut-out alpha, and chokes the
alpha by 1 px and feathers it 2 px (`borde_suave`) so no rim shows on bright footage.

### Reaction format: jump cuts between narrator clips felt abrupt (2026-11-15)
Symptom: every new narrator clip popped in. Fix: the narrator wears a small lavalier mic and talks to the lens the whole time
(reads as one self-recorded take, like a vlogger), every other clip is punched in 7 %, and where a cut would jar he ducks
out of the frame while the footage plays ("fuera"). A 5-frame cross-dissolve was tried and rejected: it shows two masks. A small corner host (720 px) read as weak; the selfie framing (head and chest, ~960 px, lower half) is the format.

### Reaction format: the script debunked its own mystery (2026-11-15)
Symptom: "maybe it really was a kite, most of them are" plus kite comparison footage closed the case. Cause: the "fair
counter-explanation" beat of generic commentary guides. Fix for Cult Pixel: the explanation is quoted as a claim and answered
by the witness or the silence (BIBLE rule 15); no debunk footage; end on a question.

### CCC reaction: host in the centre hid the video, some shots unreadable (2026-11-15)
Symptom: "it does not work in the centre, it should be to one side so you can see the video"; "some shots are cuts where you
cannot tell what it is". Cause: a 960 px head centred over full-frame crops of 16:9 news footage (a corner of a frame, a
blurred crowd). Fix: head at x 0.26, 760 px, captions beside it (x_sub 0.68); 16:9 footage shown whole ("caja"); full crops
only on a clear subject; check a contact sheet of every plan before rendering (docs/REACTION_FORMAT.md).

### H3 lip-sync lines that invent words (2026-11-15)
Symptom: a line says "the Pied of Thieves" or "or best came at?" that is not in the script. Cause: H3 improvises on long
lines and on "X or Y?" questions. Fix: read the transcript `reaccion_voz.py` prints, simplify the line (shorter, one "or"),
regenerate with new seeds, or trim a trailing murmur.

## Kling 4.0 reference-to-video, first two CCC videos (2026-11-17: n01_comedian, a08_messerschmidt)
| Symptom | Cause | Fix |
|---|---|---|
| fal 422 "An element needs either frontal_image_url with reference_image_urls, or video_url" | an element needs 1-3 extra views | `referencias_episodio` (other accessory seeds or a crop of the head) |
| Name mangled ("Moatseo Cat-to-Lail-End") | the TTS respelling sent to Kling | Kling gets the plain name (`tts` without respelling for A lines); it said "Cattelan" right |
| An extra phrase inserted / a phrase repeated at the end ("after he died. After he died.") | Kling pads to the requested duration | prompt "said exactly as written, nothing added or repeated"; a silent line is cut from the last word + mute audio |
| The camera punches in at the second line of a clip, top of the head cropped | Kling's own shot change between lines | prompt "camera never zooms"; it still happens at line changes, where the edit cuts anyway (reads as the CCC jump) |
| Hand insert starts with a raised middle finger | the board's hand still (H1_hand) is a middle finger, not an index | use the clip after 2 s; ask the user for an index-finger hand still |
| Accessory edit with two mirrors | Qwen-Image-Edit doubles props | "ONE single ..., only one in the whole image"; 3 seeds, pick one |

## 2026-11-17 · CCC news format in After Effects
- Symptom: N01 was delivered as a Python render (reaccion.py). Cause: the reaction recipe only had a Python renderer. Fix: `engine/build_reaccion_ae.py` + `ae/ccc_reaccion.jsx` build the same reaccion.json in AE with Motion DNA (sound cues, check_layout); reaccion.py now writes `*_PREVIEW_python.mp4` only.
- Symptom: a footage layer in AE showed nothing (hasVideo false). Cause: VP9 and AV1 files import as audio only. Fix: the builder makes an H.264 copy in `ae/media/footage/` (original untouched).
- Symptom: A08 showed ~8 s of empty background (31-39 s). Cause: the quote line was not marked, so B works merged into one long art-module run longer than the template module. Fix: the quote line needs `"obras": ["__cita__"]` in timeline.json (and proyecto.json), which also brings the quote card in.
- Symptom: the voice was cut at 12 s ("...thousand dollars") and 47 s ("reporters") in N01. Cause: line windows and Kling per-line cuts ended at Whisper's last word end (Whisper ends trailing words early) and a phantom early "and" moved the next cut forward. Fix: `comun.fin_habla` / `inicio_habla` (by sound) in sts.py, montaje.py and kling.py (`--recortar` re-cuts existing takes for free); `engine/qa_audio.py` is mandatory in render_ae.py.
- Symptom: one frame with the background and no head right before a cut to a work (A08 v4 at 4.13 s). Cause: the host plate is a 24 fps precomp; AE rounds its duration down to whole frames, so the last 30 fps frame of the section fell past its end. Fix: `placa()` pads the plate by 0.1 s (the layer in the main comp is still trimmed to the section).
- Symptom: run_jsx gets no answer though AE is open and responding (no dialog). The bridge stopped reading `bridge/inbox` (a request waits there). Deleting `outbox/_bridge_started.txt` makes the next call restart the bridge; if AE still does not answer, it is busy (one core at 100 %): ask the user to look at AE, never close it.

## 2026-11-20 · CCC: voices, MiniMax heads, collects
- Symptom: Buns' voices "suenan raro" (A04, N04, N09). Cause: multilingual_v2 at speed 1.15, then a 22-25 % rubberband stretch down to ~195 wpm. Fix: generate at speed 0.9 (`character.json`, per video `proyecto.json "voz_ajustes"`), ritmo_b 1.0, no `estirar`. Never fix pace with a stretch.
- Symptom: a block's first line failed qa_lineas "cut at start" 5 times with the word whole ("Nine"). Cause: the take voices its first consonant from sample 0. Fix: tts.py puts 60 ms of air in front of a block's first line.
- Symptom: N04/N09 renders lost the last line. Cause: AE kept the duration of the previous, shorter voz_reaccion.wav (same path). Fix: build_reaccion_ae.py hands AE a copy named after size+mtime.
- Symptom: MiniMax reference-to-video cut to a new scene after ~1-4.5 s (a body, a leather jacket, a robot body). Cause: long clips and literal concept words ("robot dog") in a head prompt. Fix: one line per clip (≤ 6 s), structured prompt with "avoid: cuts, scene changes", longer lines through lip-sync.
- Symptom: small head with cut ears/locks (N06 33 s, N09 7 s). Cause: MiniMax leans in during a clip, out of its own frame; the clip check only looked at the background. Fix: first frame with the head at 68 % (head pasted alone, no rectangle), side check on every clip, alpha edge check on every small-head span after the cut-out.
- Symptom: the concept shot darkened at its end like a fade to black. Cause: the big-head darkening ramp started before the head was back. Fix: the darkening is 0 inside `fuera` spans.
- Symptom: 0.4 s flash before N01's concept shot. Cause: inserting the shot left a sliver of the old plan. Fix: slivers under 1.2 s go to the neighbour plan.
- Symptom: deleting "unused" files from a collect removed the sound track. Cause: AE returns file names URI-encoded (`%20`). Fix: compare `decodeURI(file.name)`; verify every collect by opening it and rendering it.
- Symptom: WebM cut-outs (2 MB instead of 130) could not be used. Cause: this After Effects does not import WebM. Fix: ProRes 4444 10-bit qscale 9 (alpha lossless, colour ~54 dB, 2-4x lighter).
