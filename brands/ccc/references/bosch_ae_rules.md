# Bosch template: the After Effects rules, layer by layer

Read from `bosch_template/Cool-Culture-Club_template_Bosch.aep` with a full property dump (every modified property,
keyframe with its ease, expression, effect and font). These are the values `ae/ccc.jsx` uses. When a new episode looks
"cheaper" or "faster" than Bosch, compare against this list first. *(Dürer test v1 missed most of them: review 2026-11-07.)*

## 1. Host plate (`CCC Avatar Plate`, 24 fps, one per host clip)
Bottom to top:
1. **The host clip itself, full frame.** Its background comes from the generation: a teal gradient (#5FB191 top to #244038
   bottom). There is no coral solid behind the head.
2. **The type wall** (`kinetic_type_wall.mp4`, black on cream):
   - stretched to 134%, so it plays at 1/1.34 speed (about half the motion of the raw loop);
   - scaled to 95%, so a thin teal edge of the clip shows around it in the wide shots (the "mint border");
   - Lumetri with Faded Film 82 turns the cream into coral (#ED4F45) and keeps the letters near black.
3. **A luma track matte for the wall:** a Gradient Ramp running white at y 291 to black at y 1362. The wall is full at the
   top, fades out by the middle, and the teal shows below. This ramp is a *matte*, not a coloured layer.
4. **The head**, cut out with AE's Object Matte from the same clip.

**In the master**, each plate layer gets:
- Brightness & Contrast (+18 / +6);
- scale keys around the comp centre (not the eyes), 4 frames each, ease out 30, then in 90 and hold:
  - first cut, wide: 109 to 102;
  - first punch, close: 144 to 134;
  - next beat, medium: 122 to 114;
  - then close and medium in turn.
- The whole plate scales, background included. In the close shots the mint edge disappears.
- No extra bob or drift is added in AE: all head motion comes from the generation.

## 2. Artworks
- Always full bleed (cover). The comp has motion blur on (shutter 180).
- A shot lasts 1.2 to 2.4 s, then a **hard cut** to another crop of the same or another work. Long holds never happen.
- Moves are slow and linear (influence 17/17):
  - a scale push of about +10% (70 to 77%);
  - or an anchor-point pan across the work (532 to 915 px at 120%);
  - detail crops sit at 200 to 270%.
- The reveal (L04) zooms out from a detail at 200% to the whole work, anchor moving to the centre, ease 75/95, over about 6 s.

## 3. Detail zoom (`Detail Zoom`, 5.5 s)
- **Background:** the work full bleed, focus 50% / 45%, zoom 100%, push-in 4% over the module.
- **Card D1:** 780 x 1040, centred at (540, 960), rotation -1.5°, magnify x2.2 over the card's cover scale, in at 1.53 s.
- **Card D2:** 600 x 760, centred, rotation +2°, magnify x6.5, in at 4.1 s.
- **Card build:**
  - no paper border: the image sits straight in a rectangle matte;
  - it pops 6% in a few frames, with no fade;
  - shadow: black, Gaussian blur 40, 22 px down, 45%;
  - tape: a cream rectangle (#EDE6CC) 230 x 72 at the card's top edge, 88% opacity, rotated card +3° or -4°.

## 4. Bricolage portrait (`Bricolage Portrait`, 6 s)
- **Background:** a cream solid with the coral-to-deep-teal ramp at 91% over it (coral #FC604C at y 291 to #132019 at
  y 1362). This is the only place the coral solid is used.
- **Entry moves** (each piece lands, then holds with a 6 fps rotation wiggle from inPoint + 0.9 s):
  - **pop:** scale 0 to 105% in 0.28 s, then to 100% in 0.187 s; opacity in over 0.133 s;
  - **slide:** in from x 1360-1590 to its place in 0.7 s, hard ease out;
  - **drop:** falls 320 px, then bounces at 0.333, 0.5, 0.667, 0.767 and 0.867 s (y, -48, y, -14, y);
  - **wipe:** Linear Wipe 100 to 0 in 0.7 s, ease 50/85, angle 270 (left to right) or 0;
  - **grow:** scale 80% to 100% with a 12° turn in 0.467 s;
  - **spin:** a pop with a 180° turn.
- **Running order:**
  - 0.10 s: paper circle (540, 640);
  - 0.20-0.40 s: halftone patches and torn papers slide in;
  - 0.45 and 0.50 s: yellow and orange tapes wipe in;
  - 0.70 s: the **cutout drops** to (540, 1030), fitted in 720 x 1075;
  - 1.15-1.40 s: tape tabs, binder clip (drop), price tag (grow), screw (drop);
  - 1.45 s: pink tape at (520, 1640), -3°;
  - 1.60 s: the **name label** on black tape at (540, 1640), -3°;
  - 1.85-2.15 s: stickers, scribble, number 1, pink X, print texture.
- Captions move down to **y 1835** over this card; elsewhere they sit at y 1503.

## 5. Quote card (`Quote`, 6 s)
- Same background as the portrait card.
- **Lines:** Instrument Serif Italic 112, tracking -10, ink #1E1714.
  - Positions: (560, 800), (565, 960), (530, 1120), (560, 1280).
  - Rotations: -2.2°, 1.4°, -1.1°, 1.8°.
  - Each line sits on its own torn strip (`K_torn_paper_06`).
- **Timing:**
  - each strip wipes in over 0.7 s at 0.10, 0.88, 1.78 and 2.40 s; its line starts 0.15 s later;
  - Words Fade Up: range selector End 35, Offset -35 to 100 over 1.1 s, based on words, shape ramp up; each word rises
    24 px from opacity 0 and blur 8.
- **Quote mark:** Instrument Serif 520, cream, at (175, 690), -8°, pops in at 0.08 s.
- **Binder clip:** drops to (640, 690) at 0.5 s.
- **Attribution:** Bahnschrift Light 40, tracking 40, all caps, on black tape at (540, 1500), +1.5°, from about 2.6 s.

## 6. Captions
- Poppins SemiBold 66, cream #F6EBD9, a 10 px stroke in #1A1208, no drop shadow, centred.
- 2-4 words per caption, about 1 s each. The spoken word is amber #E8C66A (expression selector based on words).
- Position: y 1503, or y 1835 over the portrait card.

## 7. End button
- "Comment below" in Poppins / Inter Tight 50, on an amber pill (radius 999).
- The pill grows from the left, the text rises 50 px, and the button presses down 6% on the word.

## 8. What the generation carries (not AE)
- The magnifying glass on "look closely", the wink and the head bob are part of the Seedance clip.
- With H3, ask for them in the action line, or accept that they are missing.

## 9. Second audit (2026-11-07): curves, effects, transitions, timings
Inventory of the whole project:
- **Blend modes:** every layer is Normal except one Overlay paper-grain solid inside the unused Art Scroll module.
- **Track mattes:** 27 alpha mattes (cards, button, rectangles) and 2 luma mattes (the wall fade).
- **Transitions:** none in the master. Every cut is hard.

**Curves.** The template's bezier keys do not all start or stop at rest:
| Move | Key | Ease |
|---|---|---|
| pop | first key | out influence 12 at **7.5x** the segment's average speed (leaves fast) |
| pop | overshoot | in 72 / out 30 |
| pop | settle | in 90 |
| slide | start | out 12 at **7.5x** |
| slide | end | in 72 (hard stop) |
| drop | each landing | in 10 at **4x** (gravity), then out 30 |
| wipe | 100 to 0 | out 50 / in 85 |
| words fade up, grow, spin | | out 30 / in 90 |

- **Host plate:** the settle key is **Hold** (BH). The plate does not creep between beats.
- **Artworks:** pushes and pans use **linear** interpolation (LL 17/17).
- **Detail cards:** "Pop In (frames)" is 0, so a card is simply there on its word, with no pop.

**Timing.**
- The master cuts into the bricolage module **1.05 s after it starts** (module start 4.1, layer in 5.153). The first frame
  already has the papers in and the cutout landing.
- It leaves at module time 4.5.
- The quote and detail modules start at their first frame.
- The avatar plates run at **24 fps** (the clip's rate) inside the 30 fps master.

**Captions.** No captions while the quote card is on screen (caption 31 ends 30.60, quote 30.57-34.05, caption 32 starts
34.04).

**End button.** The pill starts as a thin cream line and grows from the left over 0.7 s (Reveal 0 to 100, ease 70/70). The
amber letters rise in (y +50, scale 118%, opacity 0), then the button is pressed: 6% smaller for 4 frames, and the pill turns
dark #1A1208.

**Unused modules in the template.** These are not in the Bosch cut; each is ready to port if a format calls for it:
- `Art Carousel`: cards swing in on Y rotation 45° to 0°, x 600 to 540, then leave to x 200 at -80°; ease 33/80 and 20/33;
  2.6 s per slide with title and date.
- `Art Scroll`: vertical scroll of framed works, dwell and tilt, paper grain in Overlay, drop shadow.
- `Art Slider`: horizontal slider with parallax, corner radius and Ken Burns.
- `Art Strip`: a strip of cards with one magnified.
- `Ken Burns Details`: start/end focus and zoom per painting, ease slider.
- `CCC · Kinetic Type`: the type wall's word-by-word variant.

## 10. Art modules in use and the voice (2026-11-07, review of Dürer v3)
*Review: "it isn't using the techniques we have to show images (3D moves, image over image) ... and the voice sometimes
sounds different between the head and the VO"; "the compositions show how images must be treated, don't invent".*

**Art modules.** `ae/ccc.jsx` imports the template, duplicates the module comp and replaces its "(swap me)" images and
titles. It keeps every rig, expression, 3D layer, frame and shadow as built.
- **When:** a run of consecutive works lasting 3 s or more becomes one module.
- **Rotation:** carousel, scroll, slider, strip. The rotation starts at episode number - 1, so episode 5 gets the carousel
  and the desk.
- **Each work in focus on the word that names it:**
  - carousel: each slide is stretched from its word to the next;
  - scroll: "Seconds per Artwork";
  - slider and strip: Progress keys (hold, then 0.8 s at 90/60, or 0.7 s at 85/55).
- **Pitfalls hit while porting:**
  - Slide comps must keep the name "Slide 0N ...": their expressions read N from `thisComp.name.substr(6,2)`.
  - Slide expressions read `comp("Art Carousel (9x16)")` by name, so point them at the duplicate.
  - Size each new work with the template's own "Image Size %" ratio (cover of the new picture / cover of the template
    picture).
  - SuisseIntlMono (commercial) is replaced by Cascadia Mono, which the template's font menu already lists.
  - Remove the template items the episode does not use.
- **No inventions:** the dim behind the magnifier cards, the minimum card zoom and the moved carousel titles were removed.
  The magnifiers use the template's x2.2 / x6.5. Light works only switch the slide's own "Text Color" control to ink.
- **Known overlap:** the carousel title sits at the template's y 1404 (z -380), behind the captions at y 1503.

**Voice.**
- **Symptom:** the head lines (speech-to-speech on the H3 voice) and the voice-over lines (straight text-to-speech) sounded
  like two voices.
- **Measured:** the speaker embeddings matched only 0.89 between the groups (0.95+ inside each), and the host lines carried
  about 4 dB more above 3 kHz.
- **Fix:**
  1. `engine/sts.py --vo` passes the VO lines through the same STS (same model and settings). It keeps each line's
     length.
  2. `engine/igualar_voz.py` EQs the VO toward the host's long-term spectrum and levels every line to -20 LUFS.
- **Result:** 0.974 between the groups.
- **Rule for CCC:** VO lines always go through STS too.
- **Cost:** about 31 s of STS (about 520 credits) per episode.

## 11. Portrait size and no half-started images (review of Dürer v4)
*Review: "is the artist's portrait like the reference, in size and position?"; "in one of the transitions you were about to
show another image and you cut: we must avoid that".*

**Portrait.** The template's cutout is a **bust**: top of the head at y 510, chin at y 1080, a straight cut across the chest at
y 1540 (A_bosch_cutout 1024 x 1529 at 70.31%, centred at (540, 1030)).
- `fotocopia.py` finds the face, cuts 0.8 head-heights below the chin and trims a wide figure to 0.95 face widths from the
  face centre.
- It writes `retrato_bricolage.json` with the head's top and chin.
- `ccc.jsx` scales and places the cutout so every artist's head has exactly Bosch's size and place. The cutout drops 320 px
  and bounces, as in the template.

**No image may start and be cut away.**
- Every work stays on screen for 1.2 s or more (the template's shortest shot is 1.17 s). A shorter work takes time from the
  portrait card before it, and the card keeps at least 3.45 s.
- **Desk scroll:** the template's scroll never rests, so it was already sliding to the next print at the cut. It is capped
  at the last work the voice names.
- **Carousel:** the last slide is stretched so its exit (at 2.3 / 2.6 of the slide) falls after the cut.
- **Slider and strip:** their Progress keys end on the last named work and hold.

## 12. Portrait height and the ending (review of Dürer v5)
*Review: "the artist's position should be higher, for the safe area"; "we cut it as if ending a sentence at the end".*
- **Portrait height:** the style sets `retrato_cabeza_y` [280, 850].
  - The head keeps Bosch's size (570 px from top to chin) but sits 230 px higher, on the paper circle (centre y 640).
  - The bust ends at y 1310, clear of the name label (1640) and of the bottom area the platform covers.
  - Bosch's own value, 510-1080, is the default for other brands.
- **The ending breathes:** the style sets `cola_final_s` 1.6.
  - Dürer v5 ended 0.3 s after the last word. Bosch holds about 2 s with the button and the host still alive.
  - The last host shot now runs to the end.
  - Past the end of the H3 clip, the last 0.3 s plays back and forth instead of freezing. That stretch is the closing
    smile with the mouth shut, so the host does not seem to talk without a voice.
  - The last caption leaves 0.5 s after its word; the button stays.
