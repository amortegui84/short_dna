# Cool Culture Club: series bible

Read before writing an episode. What never changes, what changes with each artist, and the recipe to rebuild the Bosch
cut for anyone else. Detail lives in `brand.json`, `styles/ccc_bricolage.json` (curves, modules, timings),
`templates/ccc_artist_short/template.json` (the 10 lines), `prompts/PROMPTS.md` (character and Seedance prompts) and
`references/bosch_analysis.md` (the reference cut, shot by shot).

## 1. Constants
| Part | Rule |
|---|---|
| Host | One of two floating 3D art-toy heads (`ccc_girl`, `ccc_guy`): no body, no neck, no hands. Sarcastic, confident, unimpressed. |
| Voice | Young, quick (~2.6 words a second), gossipy, playful; Seedance voice for lip sync, converted to the series voice (to define). |
| Background | Host shots: the clip's own teal gradient; over it the COOL CULTURE CLUB wall recoloured coral, at 95% (a thin teal edge shows), at 1/1.34 speed, faded toward the bottom by a luma ramp (y 291 white -> y 1362 black). The coral-to-dark solid exists only behind the portrait and quote cards. Every AE value: `references/bosch_ae_rules.md`. |
| Look | Modern bricolage: B/W photocopy cutouts, tape, marker, stickers, acetate, hardware, all in the palette. Never vintage (no sepia, aged paper, newspaper, typewriter). |
| Palette | coral #FA5639, amber #E39336, magenta #CB2479, plum #651F77, teal #326055, deep teal #26483F, salmon #D7746E, cream #F0E8DD, warm black #1E1714. |
| Type | Poppins SemiBold 66 captions, cream with a 10 px dark stroke (no shadow), spoken word amber #E8C66A, y 1503 (1835 over the portrait card); Bahnschrift Light brand and attribution; Instrument Serif Italic quotes; SuisseIntlMono titles. Poppins must be installed for all users (this After Effects ignores per-user fonts). |
| Structure | 10 lines, ~140 words, ~56 s: hook (A), portrait card (B), look closely (A + magnifier), modern twist (B), "here's the thing" (A), quote card (B), patron/history (B), debate (A), "nobody knows" (B), question + comments + joke (A). |
| Works | Shown with the template's own modules, never re-invented: full-bleed crops with hard cuts, the detail zoom, and for runs of 3 s+ the 3D carousel, the desk scroll of framed prints, the slider or the strip (rotating per episode). |
| Edit | Hard cuts at phrase ends. The whole host plate (background included) lands big and settles in 4 frames: wide 109 -> 102, close 144 -> 134, medium 122 -> 114, scaled from the frame centre; no extra bob in AE. Artwork full bleed, always moving, and a hard cut to another crop every 1.2-2.4 s: never one framing held for 5 s. |
| Sound | Voice + code-made effects in the export; music added in the app. One voice: the VO lines go through the same speech-to-speech as the host lines (`sts.py --vo`), then `igualar_voz.py` (EQ to the host spectrum, every line at -20 LUFS). |
| Truth | Facts checked against a source before publishing; quotes with their source. |

## 2. Host behaviour
1. Every gesture is a face or head move: eyebrows, squints, eye darts, head tilts, laughs. Never hands.
2. More expressive than a person; back to the lens on every punchline; blinks every 2-4 s.
3. Each line ends on a neutral face for under a second: that is where the edit cuts.
4. Identity lines are pasted unchanged into every prompt (`characters/<host>/character.json`).

## 3. What changes with each artist
| Knob | How to choose it | Where |
|---|---|---|
| Host | girl (green plate) or guy (magenta plate); alternate episodes or match the artist's vibe | `presentador` |
| Hook | the strangest true detail, said like gossip | L01 |
| Portrait | public-domain or cleared portrait -> photocopy cutout (prompt in `prompts/subject_cutout.txt`) + name label on black tape | `retrato_recorte`, `etiqueta_nombre` |
| Works | 5-7 works: one famous whole, details to magnify, two for the debate | `obras` |
| Detail zoom | the 1-2 details the host names in L03 (focus x/y, magnify x2.2 and x6.5) | detail_zoom controls |
| Quote | a real quote with its source, 3-4 short lines | `cita` |
| Debate | two options that fit the artist ("saint or secret rebel", "genius or fraud") | L08, L10 |
| Kit pieces | always from the generic kit (`kit/bricolage/`); only the cutout and the name label are new | portrait layout |

## 4. The recipe (how the Bosch cut was made)
1. Research and script (10 lines) against the template; mark names with pronunciation guides.
2. Host clips: two Seedance 2.5 image-to-video clips from the approved still (A = L01+L03+L05, B = L08+L10), beats timestamped, `Avoid:` line last. Paid: quote first.
3. Voice: speech-to-speech on the host clips; ElevenLabs v3 for the B lines.
4. Portrait: cutout + name label, graded to the palette (`ccc_grade.py`), composed on the kit, animated in AE (timings in the style file).
5. Quote card: torn strips per line, words fade up.
6. AE: duplicate the template comps (`references/bosch_template/`), swap media, retime to the voice; captions word by word.
7. Checks: `check_layout`, render, look at the key beats, loudness, black frames.
8. Export voice + effects; add the song in each app.

## 5. Episodes
| Ep | Artist | Host | Status |
|---|---|---|---|
| 03 | Hieronymus Bosch | girl | reference cut done (`references/bosch_final_v1.mp4`) |
| 05 | Albrecht Dürer | girl | test cut v7 (H3 local) |
| 02 | William Blake | girl | test cut v2 (Seedance 480p) |
| 01, 04 | Hilma af Klint, Odilon Redon | girl / guy | scripts for review (first episodes with the variety system, §9) |

The variety choices of every episode live in `episodios.json`; `engine/qa_guion.py` reads it.

## 9. Variety between episodes (review 2026-11-09)
*Review: "the template works, but the videos look the same from one to the next: we need another hook, another order,
other dialogue, another ending, so each video feels worked from the script."*

The template stays: host, work, host, work, told the same way. **Within it, every episode picks one option per row
below.** Its combination (hook + order + tone + ending) may not repeat any of the last 4 episodes, and its hook type and
ending type must differ from the previous episode's. Before writing, Claude proposes 3 combinations (one line each); the person
picks one; then the script is written, `qa_guion.py` checks it, and only then is anything generated.

### 9.1 Hooks (L01)
| Type | Key | What it is | Example |
|---|---|---|---|
| Impossible number | `numero` | one hard number that sounds wrong | "He painted 193 paintings nobody was allowed to see for 20 years." |
| Order to the viewer | `orden` | tell them where to look, right now | "Pause on the bottom left corner. See the eye?" |
| The artist speaks | `voz_artista` | open on the artist's own words, said as a confession | "'I want to paint like a madman,' he wrote. He meant it." |
| Uncomfortable question | `pregunta` | a question about the viewer | "Would you hide your best work until you're dead?" |
| The mistake | `error` | something wrong in the work, on purpose | "There's a mistake in this painting. It's on purpose." |
| Cold open | `en_frio` | L01 is a B line: 2 s of the work in silence, then the voice over it; the host enters on L02 | (silence on the work) "This was painted by a woman who talked to spirits." |

### 9.2 Order of the beats (the alternation stays)
| Order | Key | Sequence | Engine |
|---|---|---|---|
| Classic (Bosch) | `clasico` | hook, portrait card, look closer, twist, quote, story, debate, unknown, close | default |
| Reveal | `revelacion` | hook, the work, detail, story, ... and only late the portrait card: "who made it?" | `ficha_en`: a late B line |
| Quote first | `cita_primero` | the quote card right after the hook, then portrait, story, detail, close | the `__cita__` line placed second |
| Detail first | `detalle_primero` | the magnifier cards on the hook's work first, then portrait, story, quote, close | `detalles` on L01's work, words in L01-L03 |

### 9.3 Tone (the host acts it; it writes every `accion`)
| Tone | Key | How she speaks and moves |
|---|---|---|
| Gossip | `chisme` | leaning in, eyes darting, "you did NOT hear this from me" energy (the Bosch tone) |
| Detective | `detective` | slow, narrowed eyes, pieces laid one by one, the answer held back to the end |
| Deadpan | `seco` | flat face, short sentences, the joke in what she does not say |
| Awe | `asombro` | wide eyes, slower, real wonder, one whispered line |
| Defender | `defensa` | indignant on the artist's behalf: "and people called her crazy?" |

### 9.4 Endings (L10)
| Type | Key | What it is | Example |
|---|---|---|---|
| Twist | `giro` | a last fact that reframes the video | "...and she asked for it all to stay hidden. We didn't listen." |
| Callback | `callback` | close the hook's loop with its own words | hook "See the eye?" -> close "Now you can't unsee it." |
| Challenge | `reto` | a task in the work | "Find the second face. First one in the comments wins." |
| Cliffhanger | `cliffhanger` | point to the next artist | "Next: the man who painted his own funeral." |
| About you | `sobre_ti` | a question about the viewer's own life | "Would you have kept them hidden?" |
| Silent | `mudo` | no spoken call to action: a look to the lens, the button only | (a look, the button) |

### 9.5 Words that are spent (never in a new script)
They were in every early episode, so they now make the videos sound alike:
- "here's the thing"
- "look closely"
- "so scholars still argue" / "so people still argue"
- "tell me in the comments"
- "I'm off to"
- "genius or ..."
- "nobody knows"

Say the same idea another way each time ("wait for it", "zoom in on her left hand", "historians are split", "your call").

### 9.6 Visual variety (inside the template's look, never invented)
- Host: alternate the girl and the guy between episodes (`presentador`).
- Art modules: which module carries which beat (carousel, desk scroll, slider, strip, Ken Burns) changes per episode; the
  rotation already starts at a different module each episode.
- Punch-in pattern and the quote's position follow the chosen order.

### 9.7 In the project
`proyecto.json` carries `"variacion": {"gancho", "orden", "tono", "final", "presentador"}`. The engine reads `ficha_en` (the line
that carries the portrait card) for the reveal order; the other orders are just the order of the lines. `episodios.json` gets
one entry per episode when its script is approved.

## 6. Known pitfalls (from the handoff)
- Wipe Reveal reveals right to left by default: set the angle to 270 for left to right, 0 for drips.
- Crops of real paintings with nudity are blocked by OpenAI's filter (and still charged): crop locally.
- Artist-specific stickers were rejected: the kit stays generic.
- `check_layout` flags text on the cream strips as low contrast: those warnings can stay; fix the real ones.
- Tracking Settle on the quote spread the text past the frame: use Words Fade Up.

## 6b. Review notes
- *(ep05 Dürer v1)* "The animation lacks the original's details; the font changed; it feels faster." Cause: the builder was
  written from timings, not from the AE file. The wall ran at full speed over a coral-to-black solid, the head bobbed, works
  were held 5-16 s on a paper card, the cards had paper borders, and the captions were Inter Tight with a shadow. Fix: read
  every module from the .aep (`references/bosch_ae_rules.md`) and rebuild with those values. Rule: **before building a
  new brand's edit, dump its template project in full (values, keyframes, eases, expressions, fonts), not only the names.**

## 7. Adding a rule
Every review note becomes a line in the matching section with the episode in *(italics)*.

## 8. The recipe in the pipeline (tested 2026-11-07, episode 05 Albrecht Dürer, all local)
| Step | Command | Notes |
|---|---|---|
| Research + script | `proyectos/<ep>/research.md`, `proyecto.json` | `plantilla` ccc_artist_short; `inicios` point every A line to `../../characters/ccc_girl/master.png`; `detalles` {work: [{palabra, foco [x,y], x}]} for the magnifier cards; `etiqueta_nombre`; `gancho` |
| Works | public domain from Wikimedia Commons | use the API thumburl (1920 px): other widths answer 400, fast downloads 429 |
| Voice | `engine/tts.py` | Brielle (v3), Whisper QC |
| Host clips | `engine/clips.py` | MiniMax H3 local, no LoRA (`h3.lora: null`), the clip's own voice drives the lips |
| Series voice | `engine/sts.py` then `engine/montaje.py` | speech-to-speech keeps the timing exactly |
| Head cut-out | `engine/mates.py` | InSPyReNet alpha, head boxes for the punch-ins |
| Portrait | `engine/retrato.py` then `engine/fotocopia.py` | cut-out + local photocopy (B/W, halftone, hand-cut border); replaces the paid GPT Image edit for a first pass |
| Edit | `engine/build_collage.py` (style builder `ccc` -> `ae/ccc.jsx`) | host over the type wall, bricolage card, quote strips, works always moving, magnifier cards, captions, CTA pill |
| Render + QA | `engine/render_ae.py`, `engine/qc.py`, `motion_qa.py` | Dürer: 65 s, transcript 0.91, -19.8 LUFS, no black frames |
Cost of the test: ElevenLabs characters only (~1,100 for voice-over and speech-to-speech); everything else local.
Open: Poppins is not installed on this machine (captions use Inter Tight SemiBold as stand-in); the guy host has no approved still yet.
