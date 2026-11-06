# Adding a character or a look

## A new look for an existing character
`python engine/looks.py green_hair_presenter "<outfit, one sentence>" "<pose; head angle toward the viewer's left/right or upright>" --name 07_trench`
Candidates land in `library/characters/<c>/looks/_candidatos/`. Show them; the user picks one; move it to `looks/<name>.jpg` and add
`looks.<name>` in `character.json` with `imagen`, `ropa`, `pose`. Check the face: `qa_cara.py --ref master.jpg <look>` (≥ 0.84 was the
bar for approved looks). Spread head angles across looks.

## A new character
1. **Sheet first** (consistency pipeline): master portrait (frontal, even light, 1024 px), base scene (where they talk: room, mic,
   framing, 768 x 1344), 3-5 looks. Generate with Klein from a description or from user-supplied references (generated people only,
   or real people with their consent).
2. `library/characters/<slug>/character.json`: copy `green_hair_presenter` and change `descripcion`, `identidad_fija`, `mirada`,
   `nunca`, `voz` (pick or design an ElevenLabs voice), `looks`, `inicios_variantes`, `prompt_clip` (keep the H3 structure:
   subject_definitions with `<Picture 1>` scene and `<Picture 2>` face, `<Audio 1>` voice, `<d>[English] {dialogo}</d>`),
   `encuadre_ae` (where the cut-out sits in the frame).
3. Test: one start frame, one 6-second talking clip, face check, lipsync by ear. Record anything new in docs/LEARNINGS.md.
