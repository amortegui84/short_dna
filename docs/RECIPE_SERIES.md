# Recipe: a series of narrator Shorts at volume (Cult Pixel as the reference)

What it takes to turn a topic into a published episode, how much of it is automatic, what it costs in time, and what
still stops it from running at volume. Written after Tapes 01-05 of Cult Pixel (2026-11-05 → 11-07), three review rounds on
Tape 05 included. The brand's identity and per-topic choices are in its bible (`brands/cult_pixel/BIBLE.md`); this file is
the production line around it.

## 1. The line, step by step
| # | Step | Who | Input → output | Time (Tape 04 / 05) |
|---|---|---|---|---|
| 1 | Topic | person | one line ("La Llorona") | — |
| 2 | Research | Claude + web | `research.md`: 8-13 facts with sources, reported vs verified, what to leave out | 10-20 min |
| 3 | Script | Claude, against the bible | `proyecto.json`: 10 lines, `accion` per A line, `continuacion`, place, props, start frames, ending | 10-20 min |
| 4 | Start frames | GPU (Klein) | 5 frames with the episode's props and framing | 1.5 min |
| 5 | Voice | API (ElevenLabs) | 10 lines, Whisper QC | 0.5 min |
| 6 | Reconstructions | GPU | archive + generated stills with place/year titles | 2 min |
| 7 | Talking clips | GPU (H3) | 5 clips, up to 3 seeds each | 26-29 min |
| 8 | Edit timeline + mattes | CPU + GPU | `timeline.json`, cut-outs, head boxes | 7 min |
| 9 | Ending | GPU (H3) | the signature ending from the narrator's last frame | 4-5 min |
| 10 | Music | GPU (ACE-Step) | drone bed | 1 min |
| 11 | After Effects build | AE | Night Transmission comp, zoom jumps, sound | 2-5 min |
| 12 | Continuations | GPU (H3) | new narrator footage wherever voice-over sits on him | 16-66 min |
| 13 | Render + QC | AE + CPU | MP4, transcript match, loudness, black frames | 4-6 min |
| 14 | Visual QA | Claude | contact sheets: no pointing, props stable, head in frame, ending right | 5 min |
| 15 | Review | person | approve or notes (notes → bible rules) | — |
| 16 | Publish | Claude | YouTube (Zapier), Instagram (Graph API), TikTok (PostWire); `publicado.json` | 10 min |

Machine time: about 1.1 h for a 70 s episode (Tape 04), about 2.1 h for a 105 s one (Tape 05). GPU stages run one at a time,
so one machine makes roughly 8-10 episodes a day if nothing has to be redone. Steps 2-3 and 14-15 are the human-speed part.

Command: `python factory.py run <brand>/<slug> --yes` runs steps 4-13 in order and switches ComfyUI between Klein and H3.

## 2. Is it a recipe for volume? Where it stands (2026-11-07)
**Ready:**
- Identity is fixed and written down (bible §1-3): narrator, voice, VHS look, edit, structure, truth rules.
- Variation is a short list of knobs derived from the topic (bible §4): place, light, props, look, ending, survives, folk rule.
- Every generation is local (Klein, H3, ACE-Step): the only per-episode spend is ElevenLabs characters.
- Every review note so far is a rule in the bible, the script guide or the character prompt, so it is not repeated.
- Publishing is a proven route to three networks with the AI label.

**Fixed 2026-11-07 (each one cost a manual rerun on Tape 05):**
1. **Stage order.** `final` runs before `continuar`, so an extended last section left the ending starting from the short
   clip's end. Now `continuar` compares the extended clip's last frame with `final/inicio.png` and remakes the ending when
   they differ (the old one is kept as `autodestruccion_previo.mp4`).
2. **Broken generations.** One continuation collapsed (dark, smeared) and every QC passed it. Now `comun.clip_roto` checks
   each take at a quarter of the resolution (sharpness and brightness against the first frame); `clips`, `continuar` and
   endings where he survives re-seed a broken take, up to 3 tries.

**Still open:**
1. **Review rounds.** Tape 05 took three rounds (hands, reframing, ending). With the bible those notes are now rules; the aim
   is one round per episode.
2. **Interrupting a run** can leave ComfyUI stopped; re-running a single script by hand needs
   `tools/comfy_switch.ps1 h3` first (the factory does it on its own).

**Limits outside the machine:**
| Limit | Value | Episodes / month |
|---|---|---|
| PostWire free plan (TikTok) | 10 posts | ~10 |
| Zapier free plan (YouTube + Instagram) | ~100 tasks, ~12 per episode | ~8 |
| GPU, one machine | ~1-2 h per episode | ~200+ |

So today the line is reliable at about one episode a day with one person reviewing. Volume beyond ~8 a month needs paid
publishing plans (PostWire Starter, Zapier) or posting part of it by hand; beyond one a day a batch can now run overnight; the visual QA in the morning is still a person's (or Claude's) look.

## 3. Running a batch
1. Write 5-7 topics. For each: research + script against the bible (Claude), the person reads the scripts together.
2. Queue them overnight: `factory.py run` for each, one after another (GPU stages never in parallel).
3. Morning: Claude runs the visual QA per episode and sends the cuts; the person reviews them together.
4. Notes → bible rules → the affected episodes re-run from the stage the note touches (`--from <stage>`).
5. Publish on a schedule, within the plan limits.

## 4. Checklist per episode (the review notes so far)
- [ ] He faces the lens; no looking back until the ending.
- [ ] Calm hands, no pointing; the prop from the place stays the same object all clip.
- [ ] Close and medium start frames; zoom jumps keep the whole head in frame.
- [ ] No narrator footage reused (no loop, no reverse).
- [ ] The ending matches the story (and survives when the story is a warning).
- [ ] Every fact sourced; reports said as reports; AI label on every platform.
- [ ] No black frames; loudness checked; captions readable in the safe area.
