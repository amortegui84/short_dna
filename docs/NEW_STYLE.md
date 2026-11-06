# Adding a style or a template

## Style
A style = data + a builder.
1. `library/styles/<slug>.json`: tokens, type, safe area, timings, rules (write them as the user would review them), sound map, music.
2. A builder that turns `datos_ae.json` into an After Effects comp. Start from `ae/collage.jsx` (its sections, board camera, stripes,
   slides, cards, quote and subtitles are reusable: `library/techniques/techniques.json` says where each lives) or from Motion DNA
   presets and kit pieces (`list_presets`, `list_kit`, `apply_pack`, `suggest_mix` through its MCP).
3. Point `engine/build_collage.py` (or a sibling builder) at it; render one example; go through docs/QA.md; add it to `ejemplos`.
4. Every review note → the style's `reglas` and docs/LEARNINGS.md.

## Template (another kind of video)
`library/templates/<slug>/template.json`: `estructura` (sections with their line type and rule), `proyecto_base` (empty project with
the fields that template needs), `campo_tema`. Examples of other templates worth adding: product explainer (presenter + UI
screens), history story (presenter + archive photos), news recap (presenter + headlines). Reuse the character, voice, clip, mattes,
music and render stages; only the script grammar and the builder's section types change.
