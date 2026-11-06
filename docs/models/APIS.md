# Paid and remote APIs

Keys live in the `.env` named by config `env_file` (template `config/.env.example`); code reads them with `comun.clave("NAME")` and never
prints them. Only env var **names** appear here. Costs marked "Motion DNA" come from its `docs/LEARNINGS.md` §8 (same team, same accounts);
the rest come from the local experiments. **Quote USD to the user before any paid generation** and record the real cost in docs/LEARNINGS.md.
Real-looking or real faces: only with consent, and some services refuse them (below).

## ElevenLabs — in use (voice)
- **For:** the voice-over (line type B), the timbre of the talking clips (speech-to-speech over H3's own speech), voice design.
- **Auth:** `ELEVENLABS_API_KEY`, header `xi-api-key`. Base `https://api.elevenlabs.io/v1`.
- **TTS** (`engine/tts.py`): `POST /text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128`, body
  `{"text", "model_id": "eleven_v3", "voice_settings": {"stability": 0.5}}` → JSON with `audio_base64` (+ character timings).
  Stability 0.5 = "Natural"; "Creative" (0.0) made the intonation wobble. Three takes per line, keep the best by Whisper (≥ 0.85).
  v3 tags work (`[pause]`, tone tags in brackets); v3 can insert long pauses: `silenceremove`, and if a slot is tight `atempo` ≤ 1.2.
  Expressive audio drives H3's acting; a later model with tags and ellipses was tried for that (result not recorded).
- **Speech-to-speech** (`engine/sts.py`): `POST /speech-to-speech/{voice_id}?output_format=mp3_44100_128`, multipart: `model_id =
  eleven_multilingual_sts_v2`, `remove_background_noise = true`, `voice_settings = {"stability":0.5,"similarity_boost":0.85,"style":0.3}`,
  `audio` = the speech window of the H3 clip (first word −0.12 s to last word +0.18 s). Keeps rhythm and syllables: 0 ms offset,
  correlation 0.92-0.95 with the clip.
- **Voice design / library:** a designed voice needs a free voice slot (the account was at 3/3: the chosen design is waiting for a slot).
  The **free plan cannot use library voices through the API (HTTP 402)**; a premade voice worked. Swap a voice by changing `voice_id` in the
  character / project and deleting `vo/` + the stage marks; H3 clips do not need regenerating.
- **Cost:** ~300 characters per short story VO; one month on the free tier left ~1,900 characters after a 1-minute test.
  Motion DNA: v3 line via Flora ≈ USD 0.121; via fal `fal-ai/elevenlabs/tts/eleven-v3` list price USD 0.10 / 1k characters.

## Flora — available, not used by the factory
- **For:** a node-canvas service that fronts many models (Nano Banana, Seedance, Kling, MiniMax H3 Max, ElevenLabs).
- **Auth:** `FLORA_API_KEY` (in `.env.example`); in Claude sessions it is usually the Flora MCP connector instead.
- **Known behaviour (Motion DNA):** a two-image MiniMax "mixed" request is routed to first/last frame (the second image becomes the
  ending, not an identity reference); runs with real-looking faces were refused with a workspace usage-limit error (no charge).
- **Cost (Motion DNA):** Nano Banana 2.1 still 2K ≈ 0.053, 4K ≈ 0.079; Nano Banana Pro 2K ≈ 0.18; MiniMax H3 Max 5-6 s 768p ≈ 0.48-0.58;
  Kling 3.0 Pro 5 s 1080p ≈ 0.71; ElevenLabs Music 20-26 s ≈ 0.36.
- **Status:** verify before first paid run from this repo (no adapter yet; `generic_http` could describe it).

## Krea — not used (user chose local only)
- **For:** Krea's own image models and a reseller of Seedance 2.5. Krea 3 was checked as an option for identity edits, but the user chose
  local only and **no portraits were uploaded**.
- **Auth:** account MCP connector (`https://api.krea.ai/mcp`), no env var in this repo.
- **Known behaviour (Motion DNA):** Krea's Seedance 2.5 accepted references with real-looking faces that fal rejected; `generate_video` with
  `preflight: true` returns the exact cost in compute units for free.
- **Status:** untested here; verify before first paid run.

## Seedance — adapter written, not called
- **For:** b-roll and animated assets (provider `video_broll`), never the presenter (H3 keeps the lipsync and the face).
- **Auth:** `SEEDANCE_API_KEY` (Bearer) and `SEEDANCE_BASE_URL`.
- **Request shape** (`factory/providers/seedance.py`, BytePlus ModelArk / Volcengine Ark): `POST {base}/contents/generations/tasks` with
  `model` and `content` (text, optional image) → poll `GET .../tasks/{id}` until `succeeded` → download `content.video_url`.
  Resellers differ: set config `seedance.model` and adapt `_req`.
- **Cost (Motion DNA, Seedance 2.5):** 5 s 1080p = USD 6.05 (the estimate said 2.48); r2v 15 s 720p with 6-9 references ≈ 7.33;
  r2v 8 s 1080p with 4 references ≈ 9.65. Quotes were close for r2v, far off for the 1080p i2v run.
- **Known behaviour:** may add its own cut inside a 4 s clip; one multi-shot generation with timed shots keeps props consistent better than
  separate clips; `reference_audios` gave the character's voice without speech-to-speech.
- **Status:** **verify fields and price before the first paid run.**

## Suno — adapter written, not called
- **For:** alternative music provider. No official public API: the adapter speaks the common gateway shape
  (`POST {SUNO_BASE_URL}/api/custom_generate` → ids, poll `/api/get?ids=` until `audio_url`); paths set in config `suno.generate` / `suno.get`.
- **Auth:** `SUNO_API_KEY` (Bearer), `SUNO_BASE_URL`.
- **Notes:** commercial use needs a paid Suno plan; instrumental only; normalise to −27 LUFS like ACE-Step.
- **Status:** **verify before first paid run.**

## Google "Nano Banana" (Gemini image generation / edit) — planned
- **For (planned):** reference-based image edits when Klein's non-commercial licence or quality is a problem: colourise a reference,
  fix a start frame, keep a character across stills from sheets.
- **Known results (Motion DNA, via Flora):** Nano Banana 2.1 image-to-image kept likeness better than Nano Banana Pro, even with glasses,
  ~USD 0.05 per image; "colorize, change nothing else, plain light grey background" ≈ 0.035; black-and-white references come out grey
  in video models, so colourise first. Sheets first (character, location, props), then every keyframe from those references.
- **Auth (inferred, not in `.env.example` yet):** a Google AI key, e.g. `GEMINI_API_KEY`. **Model id must be configurable** (Google renames
  preview models); request shape (inferred): `generateContent` with text + inline image parts, image returned as inline data.
- **Status:** not implemented; **verify model id, request shape and price before the first paid run.**

## fal.ai — reseller, seen in Motion DNA
- **For:** pay-per-call access to Seedance, Kling, ElevenLabs, MiniMax H3 Max, lipsync and voice conversion. The repo names fal as a
  possible Seedance reseller (`SEEDANCE_BASE_URL`).
- **Auth:** `FAL_KEY` (Motion DNA's name; not in this repo's `.env.example`). Request shape differs from Ark (inferred: fal queue API,
  `Authorization: Key …`): needs its own adapter or a `generic_http` entry.
- **Cost (Motion DNA, list prices):** `minimax/h3-max/reference-to-video` 1080p USD 0.05/s (a clip came back 2.2 s);
  `fal-ai/kling-video/v3/pro/image-to-video` 4 s ≈ 0.56; `fal-ai/sync-lipsync/v2` 5 s ≈ 0.25;
  `resemble-ai/chatterboxhd/speech-to-speech` 0.02/min; `elevenlabs/music/v2.5` 0.60/min; ElevenLabs sound effects 0.002/s.
- **Known behaviour:** fal's Seedance 2.5 r2v rejected 4 of 6 shots for "likeness of real people" (no charge).
- **Status:** **verify before first paid run.**
