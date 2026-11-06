---
name: shorts-factory
description: Make a vertical Short end to end with a generated presenter (research, script, character look, talking clips with exact lipsync, voice, music, After Effects build with Motion DNA, render, QA, collect). Use when the user asks for a new Short or episode ("a Short about Vermeer with the green-haired presenter", "another artist file"), a new character, look or style for the series, or to resume, fix or re-render a Short made with this pipeline.
---

# shorts-factory

The user says **who** (character + look), **how** (style) and **what** (topic). You run the rest with `factory.py` and the
libraries, and stop at the checkpoints. Read `docs/LEARNINGS.md` before working: every rule in it came from a review.

## 0. Set up the project
- Pick from the libraries (list them for the user if they did not choose): `library/characters/*/character.json` (and its `looks`),
  `library/styles/*.json`, `library/templates/*/template.json`.
- `python factory.py new <NN_slug> --topic "<topic>" --character <c> --look <look> --style <s> --template <t>`.
- New character or look? docs/NEW_CHARACTER.md (Klein candidates with `engine/looks.py`; the user picks; spread head angles).

## 1. Research (you, with web search)
Fill `research.md` from `docs/templates/research.md`: 6-10 surprising, verifiable facts with a source URL each, the artworks with
their Wikimedia Commons file URLs and public-domain status, one real quote with its source, dates. No fact without a source.

## 2. Script (you; the user approves)
Follow the template's section grammar (`template.json` › `estructura`) and `docs/templates/script.md`:
- 10 lines, ~55-65 s at natural pace. A = presenter talking (with an `accion` for hands and face), B = voice-over over artworks.
- `tts` text with ElevenLabs v3 tags; `texto` clean; no "..." in A lines (H3 invents words).
- `momentos_a`: what enters on which spoken word in each A line (`obra`, `etq`, `cta`); `obras_b`: the artwork of each B line on
  the word that names it; `titulos`; `cita` (+ `clave`); `juntas` (names a subtitle line must not split); `obras_descarga`.
- Show the script to the user before generating anything paid or long.

## 3. Design (optional)
If the user wants to see frames first: docs/FIGMA.md (Figma MCP with the style tokens; one frame per section).

## 4. Generate and build
`python factory.py run <slug>`; it stops at checkpoints and failed stages (see `factory.log`). Before paid providers
(Seedance, Suno, remote images) quote the cost in USD. One GPU job at a time.
Checkpoints to show the user: the start frames (`inicios/`), one talking clip, the music takes (`musica/`), key frames of the AE build.

## 5. QA before sending (docs/QA.md)
Look at frames of every cut, slide, card and the quote; `qa_render.json` must have 0 black frames and -20 ± 1.5 LUFS; explain every
motion jump that is not a subtitle change. Say plainly what you measured but did not watch or hear.

## 6. Review notes
Every note becomes a fix in the engine/style AND a line in `docs/LEARNINGS.md` (symptom → cause → fix); style rules also go in
`library/styles/<style>.json`. Re-run from the stage it affects: `python factory.py run <slug> --from ae --force`.

## 7. Deliver
`python factory.py run <slug> --only collect` → a light collect + zip (`work_dir/collects/<slug>`); tell the user where it is.
