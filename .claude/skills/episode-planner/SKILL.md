---
name: episode-planner
description: Plan and write a story Short (mystery, true case, legend) that stays inside proven viral ranges without repeating the channel's last episodes — deep research with real archival media, a story plan combined from the story library (hook, structure, tone, ending, reveal devices, edit pattern, music), dynamic narrator shots from the shot library (camera grab, prop to the lens, odd angles, coffee or props tied to the story), and a storyteller voice text. Use before writing any new episode script for a brand made with shorts-factory (Cult Pixel and others), when the user asks for "a new episode", "more dynamism", "make it go viral", "better storytelling", "vary the videos", or to pick a viral topic.
---

# episode-planner

Built 2026-11-12 from a director's audit of Tapes 09-12 and three studies: 7 top story Shorts measured beat by beat, 10 reference
Shorts measured shot by shot (median shot 2.1 s, the longest hold on the reveal, prop-to-lens the top energiser), and the voice of
both (references move pitch 4-10 semitones; ours moved 1.5-2.5). Method: `docs/STORY_METHOD.md`. Libraries:
`library/historia/historia.json` (stories) and `library/tomas/tomas.json` (shots). Every step has a check; run them twice.

## 1. Pick the topic
Prefer a case with a news hook (an anniversary within two weeks, new evidence, a new documentary) **and** real public-domain media
(FBI Vault, NARA, NASA, Library of Congress, Wikimedia Commons). Avoid recent victims, children and living private people. Search
for the angle nobody has used: popular cases are saturated with look-alike AI channels.

## 2. Research deep (`research.md`, template `docs/templates/research.md`)
- 5+ sources from 3+ sites, at least one primary or contemporary (a report, a file, a newspaper of the time). A subagent with
  WebSearch/WebFetch does it well; ask it for license-checked media (Commons API `extmetadata`).
- Score facts: surprise 0-3 + concrete 0-2 + verifiable 0-2 + causal weight 0-2. Top 3 = hook, re-hook, reveal.
- Real media: images go in `obras_descarga` as `{"url", "licencia", "credito", "pagina"}`; archival **video** as
  `{"video": true, "url", "desde", "hasta", "recorte"?}` (`recorte`: an ffmpeg crop that drops a burned-in timestamp or logo; direct file or a page yt-dlp understands; only Public Domain, CC0, CC BY/BY-SA or US
  government work). At least 40% of the evidence is real; reconstructions say "reconstruction".
- Look past Wikipedia (user, 2026-11-13): footage first, from Internet Archive, NASA/NSF/NOAA/NARA, university and state
  archives, observatories, CC BY YouTube uploads (check the licence line), Pexels/Pixabay for generic places; forums
  (Reddit, Hacker News, specialist boards) for little-known details, kept only when a primary or reputable source confirms
  them. Never sign up, log in or fill a form, and downloads carry a generic User-Agent: no name, email or company anywhere
  (headers, credits, captions, descriptions).

## 3. Plan
Set `proyecto.json` `"historia": {"naturaleza", "estado", "flags"}` and run `python engine/plan_episodio.py <project> [--seed N]`.
It picks hook × structure × tone × ending × devices × edit × music for the story's nature, keeps a distance of 4+ axes from every
recent episode, and writes the beats in seconds with their energy. Try two or three seeds and choose the one that serves the
story; you may override an item if the facts call for it (write why in research.md).

## 4. Write the script to the plan
- Hook ≤ 12 words / 2.5 s; the first anomaly on screen by 1.5 s; who/when/where by 8 s; 1.5-2.5 facts per 10 s; one re-hook
  ("But here's the part nobody explains...") every 18-25 s; the reveal at 72-82% of the runtime; links read "but/therefore",
  never "and then"; the ending from the plan (loop, last fact, unanswered part...).
- 150-200 words for 60-80 s at the voice's natural speed (never sped up afterwards).
- **Voice text (`tts`)** as a storyteller: sentences of mixed length (long, long, short); fragments joined in tense runs; one
  CAPS word per sentence at most; `[whispers]` on 1-2 lines (the quote, the line before the reveal); `[pause]` or "..." before the
  reveal noun; a direct "you" question about every 10 s; quoted words in another tag so they sound like someone else.
- `bloques_voz`: 3-4 blocks by beat (hook+context, escalation, reveal, close) so the intonation flows across lines.

## 5. Shots for the narrator lines
Each talking line gets `"toma_lib": {"id", "lugar", "prop", "prop_corto", "sonido"}` from `python engine/tomas_lib.py --list`:
match the beat's energy (plan beats list the fitting categories), use props tied to the story, 4+ categories, never the same
category twice in a row, the first talking shot energy 3+. Then `python engine/tomas_lib.py <project>` expands them into start
frame, camera and action. Avoid the H-risk shots unless the edit can cut on the risky frame (snap, camera grab, polaroid).
Crowd shots (`multitud`) need a `lugar` that is a busy public place of the story's place and year (`lugar_tipo` says which);
use at most two per episode, on context or eerie beats. Documentary shots (`documental`) suit hooks (DO01 long-lens zoom),
evidence (DO02 security camera, DO07 rack focus) and endings (DO06 drone pull-back).

## 6. Checks (twice: once after writing, once after reading the expanded prompts aloud)
- `python engine/qa_guion.py <project>`: variety, sources, sourced numbers, year+place early, real media share, shot variety,
  whispers and CAPS.
- Read every expanded `inicio` and `accion`: does each one make physical sense in its place (a template can say "ceiling lamp"
  on a beach — fix the template, not just the line)?
- After generation: `qa_realidad.py` (every image and clip), `qa_voz.py --proyecto` (voice movement), `qa_lectura.py` (captions,
  cards, wpm, music ducking, Whisper).
- Record every review note as a rule in the brand's BIBLE.md and, if general, in docs/LEARNINGS.md.
