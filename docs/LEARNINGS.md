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
