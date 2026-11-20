# Cool Culture Club (CCC): read this first

This folder holds **everything about Cool Culture Club**: the bible, characters, kit, prompts, references, every episode
and all new generations. Two paths open it, and both are the same folder (a junction, not a copy):
- `D:\minimax\ccc` (open Claude here to work only on CCC)
- `D:\short_dna\brands\ccc` (where the engine looks for the brand)

Ignore `D:\minimax\CLAUDE.md` and the other files in `D:\minimax`: they belong to older projects (news avatars, H3 tests),
and their generation deadline is long past. This file is the only entry point for CCC.

Chat with the user in Spanish. Files written here are in English (the folder sits inside the `short_dna` repo).

## 1. Rules that never bend
- **CCC is a client project.** Never publish it from here: the Zapier, PostWire, YouTube and Instagram connections on this
  machine belong to Cult Pixel. Keep CCC out of commits, public pages and other brands' posts.
- **Commit or push only when the user asks.** WARNING (checked 2026-11-20): github.com/amortegui84/short_dna is
  **PUBLIC** (the API answers without login) and already holds ~113 CCC files. Push nothing of CCC until the user makes
  it private or picks a private destination.
- **Before any paid generation** (MiniMax H3 Max, Seedance or Kling on fal, GPT Image), quote the cost in USD and wait
  for an OK. Local MiniMax H3 is free; MiniMax on fal is USD 0.08/s at 768P. News process: `NEWS_PROCESS.md`. Costs are in `COSTOS_POR_VIDEO.md` and `COSTO_FULLHD.md`.
- **One GPU job at a time.** There is one ComfyUI only: `D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`
  on port 8188. Never install a second copy of anything; read `D:\RUTAS_ACTUALES.md` before downloading.
  No GPU while the user is on a call.
- **Every video is assembled in After Effects with Motion DNA, both formats (news/reaction and artist).** Python
  renders (`reaccion.py`) are internal previews only: they are named `*_PREVIEW_python.mp4` and are never delivered or
  called the edit. If AE cannot be used, say so first; never swap it for Python silently.
- **Audio QA before every delivery** (`engine/qa_audio.py`, run by `render_ae.py`): no line may end with speech in its
  last 80 ms and the voice track may not drop from speech to silence in one step. Claude cannot listen, so a video with
  a failing audio QA is never delivered. Line windows are cut by sound (`comun.fin_habla`), not only by Whisper.
- **Never close After Effects** (reopening asks for authorizations); never save the user's AE project unless a stage does it.
- **Never type personal or company data on a website**; consent banners get the most private option.
- **Artworks:** public domain or cleared only, never altered (no filters, no pieces cut out, nothing drawn on them).
  Every fact and every work has a source in `research.md`.
- **Every review note** from the user becomes a rule: the matching section of `BIBLE.md` (episode in italics) or
  `D:\short_dna\docs\REACTION_FORMAT.md`, and `D:\short_dna\docs\LEARNINGS.md` (symptom → cause → fix).
- Never print keys. `.env` here holds the brand's keys; the engine reads them with `comun.clave()`.

## 2. What CCC is
Short vertical videos (9:16, ~55-70 s, English) about art and art news, presented by a **floating 3D art-toy head**
(no body, no neck, no hands): sarcastic, confident, gossipy. Two hosts: `ccc_girl` (approved, orange cap, green
plate) and `ccc_guy` (no approved still yet). Look: modern bricolage (B/W photocopy cut-outs, tape, marker, stickers),
never vintage. Palette coral #FA5639, amber #E39336, magenta #CB2479, plum #651F77, teal #326055, cream #F0E8DD,
warm black #1E1714. Captions in Poppins SemiBold, cream, spoken word in amber.

Two formats:
| Format | What it is | Built with | Examples |
|---|---|---|---|
| **Artist short** | the original template (from the Bosch cut): host, work, host, work, 10 lines | After Effects (`build_collage.py`, `ae/ccc.jsx`) | `ejemplos/artista_bosch_referencia.mp4`, `artista_durer_v7.mp4`, `artista_blake_v2.mp4` |
| **News reaction** ("formato noticias") | the head to one side talking over real news footage, cards and comments | Python only (`engine/reaccion.py`), no AE | `ejemplos/noticias_banksy_v3.mp4`, `ejemplos/noticias_louvre_v2.mp4` (+ their `.reaccion.json`) |

## 3. Map of this folder
| Path | What |
|---|---|
| `BIBLE.md` | **the series bible**: constants, host behaviour, the 10-line structure, the variety system (hooks, orders, tones, endings, spent words), review notes, the pipeline recipe |
| `brand.json`, `styles/ccc_bricolage.json`, `templates/ccc_artist_short/` | brand values, curves/modules/timings, the 10-line template |
| `characters/ccc_girl/`, `characters/ccc_guy/` | `character.json` (identity lines pasted verbatim into every prompt), master stills |
| `prompts/PROMPTS.md` (+ `.txt`) | image, Seedance and cut-out prompts, verbatim from the handoff |
| `kit/bricolage/`, `kit/loops/`, `kit/sound/` | the generic kit (31 PNGs), the type-wall loop, code-made sound effects |
| `references/` | the Bosch reference cut, `bosch_analysis.md` (shot by shot), `bosch_ae_rules.md` (every AE value), the AE template, head mattes, voice samples |
| `episodios.json` | the variety choices of every episode (`qa_guion.py` reads it) |
| `GUIONES_REVISION.md` | scripts waiting for review (ep01 Hilma af Klint, ep04 Odilon Redon) |
| `proyectos/<slug>/` | one folder per episode: `proyecto.json`, `research.md`, `obras/_raw/` (downloads), `clips/`, `mates/`, `vo/`, `audio/`, `reaccion.json`, renders `CCC_<slug>_vN.mp4` |
| `ejemplos/` | the reference videos above (hard links: no extra disk space) |
| `figma/` | the board frames; Figma file `wtJ4aT1vMnifzVnsA9Bkqz`, page "CCC · Cool Culture Club" |
| `COSTOS_POR_VIDEO.md`, `COSTO_FULLHD.md` | cost per video and subscriptions |

The original source the brand was built from (Gian's handoff, AE template, final Bosch video) is
`D:\minimax\Cool-Culture-Club_template_Bosch folder` (+ its `.zip`). Leave it as it is.

## 4. How it runs (the engine)
The engine is `D:\short_dna` (repo shorts-factory; read `D:\short_dna\CLAUDE.md` and
`D:\short_dna\.claude\skills\shorts-factory\SKILL.md` for the full stage order). Run every command **from
`D:\short_dna`** with the project as `brands/ccc/proyectos/<slug>`; outputs land in this folder.

| Need | Where |
|---|---|
| Stage order, project schema | `D:\short_dna\docs\PROJECT_SCHEMA.md`, `RECIPE_ARTIST_SHORT.md`, `STYLE_COLLAGE.md` |
| News reaction format (full recipe, `reaccion.json` schema, layout, audio, footage rules) | `D:\short_dna\docs\REACTION_FORMAT.md` |
| QA before a render is "done" | `D:\short_dna\docs\QA.md` |
| Everything already learned | `D:\short_dna\docs\LEARNINGS.md` (sections "Cool Culture Club" and "CCC reaction") |
| H3 (local video model) know-how | `D:\minimax\01-setup.md` … `11-routes-and-configs.md`, `LECCIONES_H3.md`, `LECCIONES_MINIMAX_DIRECTOR.md`; skill `minimax-h3` |

### 4.1 Artist short (BIBLE §8)
research + script (`research.md`, `proyecto.json`, `plantilla` ccc_artist_short; propose 3 variety combinations first,
the user picks one; `python engine/qa_guion.py <project>`) → works from Wikimedia Commons (API `thumburl` at 1920 px) →
`tts.py` (Brielle) → `clips.py` (H3 local, no LoRA) or `seedance.py` (paid, quote first) → `sts.py` + `montaje.py` →
`mates.py` → `retrato.py` + `fotocopia.py` → `build_collage.py` (builder `ccc`) → `render_ae.py`, `qc.py`, `motion_qa.py`.

### 4.2 News reaction (what we did for Banksy and the Louvre)
1. `research.md`: the story with dates and sources, every clip (who filmed it, licence, URL), 3-6 real public comments
   (exact text under 25 words, likes; never a private person's handle), official statements.
2. Download into `obras/_raw/` (section 5).
3. Script in `proyecto.json`: `"formato": "reaccion"`, `"marca": "ccc"`, `"personaje": "ccc_girl"`, 10 lines of under
   ~18 words (H3 improvises on long lines and on "X or Y?" questions), `variacion` from the BIBLE, `reaccion_huecos`.
   `python engine/qa_guion.py <project>`.
4. The head speaks: `clips.py` (H3 makes the head say each line, up to 3 seeds, transcript QC; reseed with
   `CLIPS_SEEDS=31,32,33 python engine/clips.py <project> L08`), `sts.py` (series voice), `montaje.py`, `mates.py`.
5. `python engine/reaccion_voz.py <project> --slots`: places each clip on its line, prints every word's time and adds a
   `fuera` span where a clip ends early. **Read the transcript it prints** for invented words.
6. `reaccion.json`: footage plans cut on the words, cards, head spans (section 6). CCC look:
   `"estilo"` block of the examples (Poppins, no tape texture, `"corte": "salto"`), host `{"alto": 760, "x": 0.26,
   "pecho": 1.0}`, text block beside the head `"sub_bloque": {"x": 540, "y": 1440, "ancho": 480, "palabras": 9}`.
   Copy `ejemplos/noticias_louvre_v2.reaccion.json` as the starting point.
7. Stills at every cut and card: `python engine/reaccion.py <project> --cuadro <s> out.png`, and look at them.
8. Render `python engine/reaccion.py <project>` (~8 min a minute), loudnorm to -14 LUFS, `blackdetect=d=0.04` = 0,
   contact sheet. No music in the CCC export (it is added in the app). Name it `CCC_<slug>_vN.mp4`.

## 5. Scraping and research (how we get real footage)
`D:\short_dna\engine\descargar.py` (used by `obras.py`, entries in `proyecto.json` `obras_descarga`) chains:
| Tool (open source) | For | Notes |
|---|---|---|
| yt-dlp (github.com/yt-dlp/yt-dlp) | videos: YouTube, news sites, X, Instagram, TikTok | `--impersonate chrome --sleep-requests 1`; YouTube needs `-f "bv*[height<=1080]+ba/b" --merge-output-format mp4` or it falls to 360p |
| gallery-dl (github.com/mikf/gallery-dl) | images or files inside a post | entry `"galeria": N` = the N-th file |
| curl_cffi (github.com/lexiforest/curl_cffi) | pages that answer 403/401 to Python (Wikimedia originals, Daily Mail) | a real Chrome TLS fingerprint |
| Playwright (github.com/microsoft/playwright-python) | galleries that load images with JavaScript | entry `"de_pagina": N` = the N-th biggest image |
| Wayback Machine (`id_` copy) | the last fallback (Reuters 401 worked this way) | |
| Wikimedia Commons API, DVIDS, NASA | public-domain works and footage, downloaded directly | use the API `thumburl` (1920 px): other widths answer 400, fast downloads 429 |

Rules: a descriptive User-Agent; a 429 waits for `Retry-After`; cookies only from the user's own browser and only when
asked (`SHORTS_COOKIES_BROWSER`); **never** CAPTCHA solvers, other people's accounts or proxy pools. A challenge wall is
reported to the user for a manual download. Research goes beyond Wikipedia: news archives, forums, the real footage,
5+ sources, generic search queries with no personal data.

Footage rules: each third-party excerpt 2-6 s (10 at most), the head talks over at least 80 % of the runtime, transform
it (crop, punch-in, freeze, circle, speed), credit every clip on screen (`credito`), crop out tickers and channel logos,
prefer public domain and CC. 16:9 news goes in `"modo": "caja"` (whole frame readable); `"full"` only on a clear subject
(a painting, a face, an object), never on a corner of a frame. Check a contact sheet of every clip before picking `desde`.

## 6. The head: on screen, big, or hidden
The head should not be on screen all the time. In `reaccion.json`:
| Want | How |
|---|---|
| Head small to the side (default) | `host.alto` 760, `host.x` 0.26; text block beside it |
| Head big (fills the frame) | `host.grande`: `[[ini, fin], ...]`, e.g. the hook `[0, 2.0]` and the ending; 0.7 s Settle move |
| **Head hidden over one shot** | `"cabeza": false` on that plan in `planos` (new 2026-11-16): she ducks out (0.3 s) when the plan starts and comes back up (0.4 s) when it ends; touching hidden plans merge into one exit |
| Head hidden over any span | `host.fuera`: `[[ini, fin], ...]` (also `host.fuera_manual`; `reaccion_voz.py --slots` adds spans where a clip ends early) |
While the head is big or hidden, the text block gives way to a single centred caption line.

When to hide her: the shot is the story (the crown, the shredded painting, the witness clip), a strong full-frame image,
a "look at this" beat, a replay or freeze, the witness's own sound, or where a cut between two head clips would jar.
When to show her: the hook, reactions, opinions, jokes, the verdict and the closing question. Aim for a visual change
every 2-4 s.

## 7. Where things stand (2026-11-16)
| Item | State |
|---|---|
| r01 Banksy shredder (news) | v3 rendered (head to the side, text block beside the head); waiting for the user's review |
| r02 Louvre heist (news) | v2 rendered (same layout); waiting for the user's review |
| ep05 Dürer, ep02 Blake (artist) | test cuts (v7 H3 local, v2 Seedance 480p) |
| ep01 Hilma af Klint, ep04 Odilon Redon | scripts in `GUIONES_REVISION.md`, waiting for review; nothing generated |
| ep03 Bosch | the reference cut from the client |

## 8. To do
- [ ] Get the user's review of Banksy v3 and Louvre v2; turn every note into a rule (BIBLE / REACTION_FORMAT / LEARNINGS).
- [ ] Use `"cabeza": false` in the next news cut on the shots that carry the story, and show the user the result.
- [ ] Text block over bright footage is hard to read (Louvre ~28 s, the sapphire tiara): add a soft dark backing or
      move the block when the plan behind it is light.
- [ ] Approve a still for `ccc_guy` (no approved image yet), then alternate hosts between episodes.
- [ ] Install Poppins for all users (admin) so After Effects stops falling back to Inter Tight (artist format).
- [ ] Review the ep01 and ep04 scripts, register approved episodes in `episodios.json`, then generate.
- [ ] Decide per episode: H3 local (free, ~30 min of host) or Seedance on fal (quote in USD first).
- [ ] Hand the approved cuts to the client; CCC is never published from this machine.
