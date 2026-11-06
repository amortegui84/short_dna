# CLAUDE.md

You are working in **shorts-factory**: a pipeline that turns a brief into a finished vertical Short with a generated
presenter, built in After Effects with Motion DNA. Read `.claude/skills/shorts-factory/SKILL.md` first; it has the order
of work. Then `docs/LEARNINGS.md` before touching any stage (every rule there cost a review round).

## Rules
- Everything in the repo is English (the engine's code comments are Spanish, legacy; new code in English). Chat in the user's language.
- Never commit keys, `config/local.json`, `.env` files, heavy media or client/company names. Keys are read with `comun.clave()`.
- Real people only with their consent; the characters here are generated and fictional. Brands and names on screen are fictional.
- Artworks: public domain only, never altered (no filters, no cut-out pieces, nothing drawn on them). Record the source of every fact and artwork.
- Quote the cost in USD before any paid generation (Seedance, Suno, remote image APIs) unless the user approved the spend.
- One GPU job at a time. Do not force-close After Effects. Never save the user's AE project unless the stage does it.
- Before calling a render done: QA in `docs/QA.md` (stripes cover cuts, no empty frames, layout, motion, black frames, loudness), and look at frames.
- Every review note from the user becomes a rule: in `docs/LEARNINGS.md` (symptom, cause, fix) and, if it is a style rule, in `library/styles/<style>.json`.
- Commit or push only when the user asks.
