# Autopilot: one episode a night, made locally, published after a human OK

Since 2026-11-20 Cult Pixel Reacts are made every night on this machine with **local generation only (0 USD)** and
published one a day. A person only does two things: watch the new cut and approve it. This page is the procedure for
everyone who runs it or connects a network to it. How each network is reached is in PUBLISHING.md; the episode format
is in REACTION_FORMAT.md.

## The cycle in one table
| When (Eastern / Bogota time) | What happens | Who | Where it is written |
|---|---|---|---|
| 22:30 every night | Scheduled task `cult-pixel-reacts-nightly` makes one new episode end to end (see "The night run") | Claude, unattended | `proyectos/rNN_<slug>/`, draft texts in `posts.md` and `_gen/posts_r09_r18.json` |
| Morning | Watch `proyectos/<slug>/<slug>_v1_pub.mp4` and read the draft caption | **the person** | — |
| Morning | Approve it: say "approved <slug>" to Claude, or add the queue row yourself (see "Approving") | **the person** | `_gen/cola_publicacion.json` |
| 19:00 every day | Scheduled task `cult-pixel-reacts-daily`: today's approved row goes out as an Instagram Reel; tomorrow's approved row is uploaded to YouTube, private with `publishAt` 10:00 and the AI label | Claude, unattended | the row's `instagram` / `youtube` fields, `posts.md` |
| Once a week, by hand | TikTok: schedule the approved cuts in TikTok Studio (PUBLISHING.md Part C) | the person, or Claude driving their Chrome | TikTok Studio → Posts |

Nothing is ever posted that the person has not watched. The night task never touches the queue; the publishing task
never posts a row whose `aprobado` is not `true`.

## What runs locally (and nothing else)
| Piece | Local tool | Notes |
|---|---|---|
| Script | Claude (the scheduled task) | from the research; claims attributed, the mystery left open |
| Research and footage | a research subagent + real archival media | `_gen/RESEARCH_FIRST_BRIEF.md`, `_gen/FOOTAGE_BRIEF.md`; 6+ sources beyond Wikipedia, every file credited |
| Narrator voice | Qwen3-TTS voice clone (`"motor_voz": "qwen3"`, pace 1.05); Applio RVC model `cultpixel_narrador` as an optional second pass | replaced ElevenLabs on 2026-11-19; speaker similarity 0.987–0.990, the same as the old voice |
| Narrator video | MiniMax H3 in the single ComfyUI (port 8188) | start frames, then clips, then cut-outs |
| Music | ACE-Step 1.5 | ducked under the voice |
| Edit and render | `_gen/planos.py` + `engine/reaccion.py` (`render_pub.sh`) | −14 LUFS, black-frame check |

Paid services (ElevenLabs, Kling, Seedance, Flora, fal, Replicate) are **not** part of the night run. If a step tries to
call one, the task stops that step and reports it. Model paths are in `D:\RUTAS_ACTUALES.md`; never install a second
ComfyUI or copy a model.

## The night run (what the task does, in order)
1. **Topic.** `cd brands/cult_pixel/proyectos/_gen && python temas.py --sync`, then the first `pendiente` row of
   `temas.json` → `python temas.py --check "<topic>"`. A topic that is the same case, object, place or event as one in
   `hechos` is marked `repetido` and skipped. The chosen one becomes `en_curso`.
2. **Research and footage** (subagent): `research.md`, `obras/_raw/` (22–35 real files with credits), `footage.md`.
   Fewer than ~15 usable files → the topic is marked `fallo` and the night stops.
3. **Script and project:** `_gen/rNN.json` (11 lines, ~65 s) → `python hacer_proyecto.py rNN.json`.
4. **Voice:** `bash voz_reacts.sh <slug>`; every line checked against the script (`qa_lineas.json`).
5. **GPU:** `bash gpu_reacts.sh <slug>` (H3 start frames and clips, cut-outs, ACE-Step music). One GPU job at a time.
6. **Edit:** `_gen/shots_rNN.json` → `python planos.py rNN` (always re-run after editing the shots) → `bash render_pub.sh <slug>`.
7. **QA** (up to 3 rounds): −14.0 LUFS, 0 black frames, `motion_qa.py` (70–85 JUMPs is the normal baseline from the
   word-by-word subtitles), a contact sheet looked at frame by frame, 55–80 s long.
8. **Leave it for review:** draft title/caption/hashtags in `posts.md` and `_gen/posts_r09_r18.json`; the topic row
   becomes `hecho` and the episode is added to `hechos`; any new pitfall goes to LEARNINGS.md.
9. **Report** in 4–6 lines: path, duration, topic, QA numbers, what it could not fix.

The task is defined in `C:\Users\<user>\.claude\scheduled-tasks\cult-pixel-reacts-nightly\SKILL.md` (cron `30 22 * * *`).
The PC must be on and awake at 22:30, with ComfyUI able to start; After Effects is not needed and is never closed.

## The topic list (no repeats)
`brands/cult_pixel/proyectos/_gen/temas.json` is the only list:
- `hechos`: every topic already made, long episodes (`ep*`) and Reacts (`r*`), with slug, title and topic.
- `pendientes`: the backlog, in order, each with `estado`: `pendiente`, `en_curso`, `hecho`, `repetido` or `fallo`.

```
python temas.py                    # show done and pending
python temas.py --sync             # add any ep*/r* folder missing from "hechos"
python temas.py --check "Tunguska" # list done and pending topics that share key words with it
```
To add a topic, add `{"tema": "...", "estado": "pendiente"}` to `pendientes` after running `--check` on it; reorder the
list to change what comes next. `--check` matches words, so read its hits: "Oak Island" sharing "island" with the
Island of the Dolls is fine; the Max Headroom hijack matching episode 02 was a real repeat and was removed. When fewer
than 3 topics are pending, the night task adds 5 new ones, each checked first.

## Approving
Only a person approves, after watching the cut. Either tell Claude "approved <slug>" (it adds the row and records who
and when), or add the row to `_gen/cola_publicacion.json` yourself:
```json
{"fecha": "2026-12-07", "slug": "r27_example", "aprobado": true, "aprobado_por": "<name>, 2026-11-21",
 "youtube": null, "instagram": null, "tiktok": null}
```
- One row per day, the next free date after the last row.
- The video must be reachable at the public link before its date:
  `python tools/publish_release.py --user <github user> brands/cult_pixel/proyectos/<slug>/<slug>_v1_pub.mp4`
  (the daily task uploads it itself if the link does not answer).
- To hold an episode back, set `aprobado` to `false`; to drop it, remove the row. Rows already posted keep their ids.

## Checking that it is all running
| Check | How |
|---|---|
| Both tasks exist and are on | Claude app → Scheduled tasks: `cult-pixel-reacts-nightly` (22:30), `cult-pixel-reacts-daily` (19:00) |
| Last night's result | the task's run report, or the newest `proyectos/rNN_*` folder and its `*_v1_pub.mp4` |
| How far publishing is covered | the last row of `cola_publicacion.json` with `aprobado: true` |
| What is left to make | `python temas.py` |

## When something fails
| Symptom | Cause | Fix |
|---|---|---|
| No new episode in the morning | PC asleep or off at 22:30, or another render/GPU job was running (the task waits up to 60 min, then gives up) | Leave the PC on; run the task again from the Scheduled tasks list |
| The report says a topic `fallo` | Not enough real footage | Nothing to do; the next night takes the next topic. Remove or rephrase it in `pendientes` |
| A stage stalled | ComfyUI not answering, or a stage wrote nothing for 25 min | The task restarts that stage once; after a second failure it stops and says where. Start ComfyUI with `START_COMFY_H3_FAST.bat` and run again |
| A name is misspelled in the subtitles | Whisper heard it wrong | Add a `cambiar` pair in `shots_rNN.json`, run `planos.py` again, re-render |
| Instagram or YouTube did not post | Row not approved, Zapier's monthly tasks used up, or a throttled upload | See PUBLISHING.md › What can go wrong |
