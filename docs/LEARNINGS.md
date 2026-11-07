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
- **The ending starts from the wrong pose** (ep05 v3): stage `final` runs before `continuar`, so when the last section was
  extended the ending began from the short clip's end. Fix: `continuar` compares the extended clip's last frame with
  `final/inicio.png` and remakes the ending when they differ.

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

## App and Claude
- **A one-word reply cost $0.70** → the Agent SDK loaded every connector of the account (~80 MCP servers) → strict MCP config with only
  Motion DNA, Blender and Figma: $0.08; the account's connectors only when the user ticks them.

## Voice for narrators (Cult Pixel, 2026-11-05)
- **"Inaudible because of the effect"** → crypt chain (pitch down, long echo, low-pass) hid the words → keep the voice clean (presence boost, firm compression); mood from the voice and the music.
- **"Too slow for a 1-minute story"** → ElevenLabs v3 ignores `speed`, and designed voices speak ~95 wpm; tags like [slowly]/[long pause] slow it more → use `eleven_multilingual_v2` with `speed` 1.2 (~120 wpm, natural) + 1.1x, pauses capped at 0.4 s. v2 reads [tags] aloud: tts.py strips them for non-v3 models.
- **Dramatic pauses were deleted** → montaje's silenceremove cut every silence > 0.3 s → `conservar_pausas` + `pausa_max` keep pauses up to N s.
- A mouthless narrator needs no speech-to-speech: the line lasts as long as the voice, and the clip ping-pongs if the voice is longer.
