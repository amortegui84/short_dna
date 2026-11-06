# Style: collage_v10c

Paper, tape and giant type around a presenter cut-out; public-domain artworks full-bleed and untouched. Data: `library/styles/collage_v10c.json`.
Code: `ae/collage.jsx` (After Effects, called by `engine/build_collage.py`). Techniques: `library/techniques/techniques.json`.

## Look
- Palette: ink `#191D1D`, paper `#F7F8F4`, teal `#6FAFA8`, mint `#3ECCB0`, magenta `#E6128F`, lime `#C1F157`, ochre `#B8945A`.
  Presenter backgrounds rotate `#2E6F66`, `#7A2550`, `#3D5A3A`.
- Type: Impact (labels, giant words, subtitles, quote), Instrument Serif Italic (titles, motto), Courier New Bold (dates, author).
- Texture everywhere: paper multiply 22 %, canvas 14 %, a paper overlay 8 % and grain 6 on top; registration marks in three corners.
- Kit (`library/kit/`): tape, plaster hand, three frames, painter's tools, halftone, craquelure, canvas, paper and concrete.

## Motion
- Board of spots (1400 x 2200 apart); a CAM null drifts slowly in each section and slides between spots (1.2 s; 0.55 s under stripes).
- Stripes: four diagonal bands in 0.8 s cover every presenter <-> artwork cut. Nothing else uses them.
- Artworks: full-bleed (1.12 x cover) with a slow drift (<= 70 px/s) and zoom (0.8 %/s), or on a passe-partout (lamina) when the
  image is small; cross-dissolve 0.9 s between artworks inside a line; never altered.
- Labels: capsule pop in 7 frames; CTA breathes. Cards: drop with a small bounce (`caer`).
- Subtitles: Impact 74 white on a rough ink bar at y 1400, the current word lime.

## Sound map (Motion DNA `add_sound`)
| Event | Sound | Gain |
|---|---|---|
| stripes (presenter change) | whoosh 0.6 s | -4 |
| board slide | whoosh 1.1 s + tick on arrival | -7 / -12 |
| artwork fills the frame | sub | -10 |
| into the hook's artwork | riser 1 s | -12 |
| label | pop | -6 |
| title card | swish | -9 |
| detail card | click | -8 |
| artist card | type (dates), shimmer (silhouette fills) | -11 / -8 |
| quote | chime | -12 |
| hook | hit at 0.38 s | -5 |

## Audio
Voice -20 LUFS, music -27 LUFS (0 dB in AE, fade out the last 1.8 s), master loudnorm -20 LUFS / -1.5 dBTP.
