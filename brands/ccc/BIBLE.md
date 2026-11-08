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
| 01, 02, 04, 05 | Hilma af Klint, William Blake, Odilon Redon, Albrecht Durer | — | scripts exist in the source project, not here yet |

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
