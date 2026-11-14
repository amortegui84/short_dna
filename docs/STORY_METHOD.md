# Story method: combine, don't template

Why: YouTube's "inauthentic content" rule (15 Jul 2025) demonetises mass-produced, near-identical videos, and the whole channel
can be hit. The narrator, voice and look stay fixed; the structure, hook, ending, shots and edit vary inside measured ranges.

## Evidence (2026-11-12)
- 7 top story Shorts (2-8 M views) measured beat by beat: the reveal lands at **74-82%** of the runtime in all of them; the
  first sentence carries a name, place or time plus an anomaly; each uses a number that doesn't add up and an odd physical
  detail; one re-hook per ~60 s; 2-2.5 facts per 10 s; closes are unresolved or reversed, never summaries.
- 10 reference Shorts (0.5-324 M views) measured shot by shot: median shot 2.1 s; quick cutaways in the setup, the longest hold
  on the reveal; a prop pushed to the lens is the most common energiser and opens 4 of 10; 7 of 10 move in frame 1.
- Voice: references move pitch 4.4-9.9 semitones and loudness 1.9-6.6 LU, and either talk fast (190-255 wpm) or slow with long
  held pauses; our narrator moved 1.5-2.5 st, ~1 LU, slow without pauses. Causes found: ElevenLabs v2 (tags stripped), the
  voice sped up twice (1.2x in TTS and 1.15-1.2x in the edit), one call per line (every sentence fell the same way).

## Pieces
- `library/historia/historia.json`: 17 hooks, 13 structures (beats in % of runtime, energy per beat), 11 tones (voice tags),
  12 endings, 14 reveal devices, 6 edit patterns, defaults per story nature, the viral ranges, the anti-repetition rules.
- `library/tomas/tomas.json`: 66 narrator shots in 10 categories (camera handling, gestures, angles, objects, transitions,
  impossible poses, environment, details, crowds, documentary), each with start frame, one action, energy, beats and the
  AI-video risk. Regenerate it with `python library/tomas/make_tomas.py` (edit that file, never the JSON).
  Crowd shots (`multitud`, `gente: true`) put him in a busy public place tied to the story (a station, a city crossing, a
  market, a carriage of the story's year, e.g. a Manhattan crossing at rush hour): he is the still or odd point and nobody
  notices him. Documentary shots (`documental`) borrow observational camera grammar: a long-lens zoom from far away into
  him talking to the lens, a security camera, following him from behind, across a street through traffic, an interview
  chair, a drone pull-back, a rack focus, a snap zoom.
- `engine/plan_episodio.py` (combiner), `engine/tomas_lib.py` (shot expansion and variety check), `engine/qa_guion.py`,
  `engine/qa_lectura.py`, `engine/qa_voz.py`, `engine/qa_realidad.py`, `engine/obras.py` (real images and archival video).
- Skill: `.claude/skills/episode-planner/SKILL.md`.

## Viral ranges (the episode gate)
Duration 60-80 s · hook ≤ 2.5 s / ≤ 12 words · anomaly on screen ≤ 1.5 s · context ≤ 8 s · 160-195 wpm natural (never sped up)
· shot 1.8-3.5 s on evidence, 3-6 s on the narrator, nothing static > 6 s · re-hook every 18-25 s · 1.5-2.5 facts per 10 s ·
reveal at 72-82% · narrator on screen 20-35% · 0.4-1.2 s of silence before the reveal · 3-5 devices, one key, at most one big ·
no "and then" between beats · no unverified fact said as true.

Calibrate after publishing: viewed-vs-swiped (target ≥ 70%), average % viewed and the dips in the retention curve feed the
weights of the library items. The numbers above are starting points, not platform facts.
