# Reference analysis: Hieronymus Bosch (Cool Culture Club, 56 s)

Source: `bosch_final_v1.mp4` (1080x1920, 30 fps, -17.2 LUFS integrated) and the AE project in `bosch_template/`
(20 comps; full layer dump in `aep_dump.json`, control values in `aep_controls.txt`).

## Pace
- 141 words in 54.8 s of speech: **2.6 words a second** (Cult Pixel runs ~2.0). Pauses between lines are 0.2-1.2 s.
- 16 picture changes: a new shot every **~3.3 s**. The avatar is on screen about 45% of the time, in 5 blocks.
- 55 caption groups of 2-4 words, about 1 s each, the spoken word in amber.

## Shot list (master comp)
| Time | Line | Shot | Motion |
|---|---|---|---|
| 0.00-5.15 | L01 A | avatar plate (girl) | cut-in 109->102% in 4 frames; punch-in 144->134% at 3.5 s on "years ago" |
| 5.15-8.60 | L02 B | bricolage portrait: cutout, name label, tapes, stickers | pieces pop in 0.1-2.15 s, then stop-motion jitter |
| 8.60-11.47 | L02 B | Garden of Earthly Delights, whole | Ken Burns 188->193% (linear) |
| 10.50-12.23 | L03 A | avatar (squints, magnifier look) | settle + punch-in |
| 12.23-17.63 | L03 A/B | detail zoom on the hell panel: two magnifier cards with tape | cards enter on their words (1.5 s, 4.1 s) |
| 17.60-24.20 | L04 B | hell panel details (butt music, instruments) then zoom out to the whole panel | 200->240% soft push; 200->61% reveal (ease 75/95) |
| 24.17-30.60 | L05 A | avatar ("and here's the thing") | settle + 2 punch-ins |
| 30.57-34.05 | L06 B | quote card: torn cream strips, Instrument Serif, binder clip, tape | strips wipe left to right every 0.35 s, words fade up |
| 34.05-38.81 | L07 B | Haywain, then Temptation of St Anthony | Ken Burns down 246->181% / up 72->79% |
| 38.81-41.89 | L08 A | avatar (plate B) | settle + punch-in |
| 41.89-47.88 | L08-L09 B | hell (sin) / paradise (dream) / ship of fools / hell detail | slow anchor pans, Ken Burns |
| 47.87-56.00 | L10 A | avatar: "So, saint? Secret rebel? Tell me in the comments. I'm going to go play that song." | punch-ins; CTA pill "Comment below" at 53.8 s |

## Avatar plate
Seedance 2.5 image-to-video clip (two long clips: A = L01+L03+L05, B = L08+L10). In AE: Object Matte roto of the head,
the kinetic type wall behind it (Lumetri-graded to black type on coral), a gradient solid behind that. The head never
moves position; all camera energy is the settle-and-punch scale keys.

## Curves used (influence in/out, count across the project)
- Linear 16.7/16.7 (94 keys): artwork drifts, scrolls.
- 90/16.7 (44) and 85/16.7, 72/16.7: soft landing after a fast start (settles, pops).
- 16.7/30, 16.7/50: gentle starts.
- 75/95 on detail pushes and the reveal: very soft both ends.

## Type
Poppins SemiBold 66 (captions, 110 layers), Bahnschrift Light 240 (type wall), SuisseIntlMono (artwork titles),
Instrument Serif Italic (quote), Inter Tight Bold (CTA).

## Sound
Voice-over + code-made sound effects (one `_mdna_sound.wav` per comp, made with Motion DNA `add_sound`). Music is added
inside each app (creator account), not in the export.

## What makes it this brand (vs. Cult Pixel)
| | Cool Culture Club | Cult Pixel |
|---|---|---|
| Host | sarcastic 3D art-toy head, no body, no hands | masked narrator, hands do everything |
| Energy | fast (2.6 w/s, shot every 3.3 s), funny | slow, grave, documentary |
| Picture | warm coral-to-teal, bricolage craft materials, clean digital | VHS grain, red/blue light, CRT |
| Cuts | hard cuts with a settle; no glitch | hard cuts hidden by a tracking glitch |
| Captions | Poppins, cream, spoken word amber | mono, typed, key words red |
| Ending | question + comments pill + joke | the narrator's signature ending |
