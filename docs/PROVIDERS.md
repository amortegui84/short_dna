# Providers

`config/local.json` › `providers` picks one per capability. Keys live in the `.env` named by `env_file` (template:
`config/.env.example`); code reads them with `comun.clave("NAME")` and never prints them.

| Capability | Default | Alternatives | Used by |
|---|---|---|---|
| image | `comfy_klein` (Flux 3 Klein, 2-10 refs, local) | `generic_http` (any image API) | looks, start frames, props |
| video_talking | `comfy_h3` (MiniMax H3, local, speech + lips) | — (keep H3: lipsync and face) | talking clips |
| video_broll | `seedance` | `generic_http` | b-roll, animated assets (not the presenter) |
| voice | `elevenlabs` (v3 TTS + speech-to-speech) | — | voice-over, one voice for the whole video |
| music | `comfy_ace` (ACE-Step 1.5, local) | `suno` | music bed |
| research | `claude` (web search, sources in research.md) | — | facts, artworks, quotes |

## ElevenLabs (in use)
TTS `eleven_v3`, stability 0.5 (Natural), `/with-timestamps`; STS `eleven_multilingual_sts_v2` with noise removal, stability 0.5,
similarity 0.85, style 0.3. The character's `voz.voice_id`; a designed voice needs a free slot in the account.

## Seedance (adapter ready, not yet called)
Async tasks: `POST {SEEDANCE_BASE_URL}/contents/generations/tasks` with `model` and `content` (text, optional image), poll
`GET .../tasks/{id}` until `succeeded`, download `content.video_url` (BytePlus ModelArk / Volcengine Ark shape). Resellers differ:
set config `seedance.model` and adapt `_req` if needed. **Verify fields and price before the first run; quote USD to the user.**
Use for b-roll and asset animation; for consistent characters pass references (sheet first, then shots: see the character library).

## Suno (adapter ready, not yet called)
No official public API. The adapter speaks the usual gateway shape (`/api/custom_generate`, `/api/get?ids=`); set config
`suno.generate` / `suno.get` for yours. Commercial use needs a paid Suno plan. Instrumental only; then normalise like ACE (-27 LUFS).

## generic_http (any other asset service)
Describe the API in config instead of writing a module: URL, body with `{placeholders}`, auth header, dotted path to the result,
optional polling. Works for most image/video/3D/upscale services. Example in `factory/providers/generic_http.py`.

## Adding a provider
1. `factory/providers/<name>.py` with the functions it supports (`image`, `video`, `voice`, `music`).
2. Register it in `PROVIDERS` (`factory/providers/__init__.py`), its key names in `config/.env.example`, its notes here.
3. Run it once on a throwaway prompt, record cost and quirks in `docs/LEARNINGS.md`.
