"""Providers: one small interface per capability, so a stage never cares who makes the asset.

    image(prompt, refs, out, size="768x1344", seed=0)        -> Path   (looks, start frames, props, backgrounds)
    video(prompt, out, image=None, seconds=5, audio=None)    -> Path   (talking clips, b-roll, animated assets)
    voice(text, out, voice_id, **settings)                   -> Path   (voice-over; speech-to-speech in voice_sts)
    music(tags, out, seconds=80, bpm=None, key=None)         -> Path

config/local.json "providers" picks one per capability, e.g. {"image": "comfy_klein", "video_broll": "seedance", "music": "suno"}.
Add a provider = add a module here with the functions it supports and register it in PROVIDERS. docs/PROVIDERS.md explains each.
Keys come from the .env named in config (comun.clave), never from code or the repo."""
import importlib

PROVIDERS = {
    "comfy_klein": "factory.providers.comfy_local",   # image (Flux Klein, 2-10 reference images)
    "comfy_h3": "factory.providers.comfy_local",      # talking video with lipsync (MiniMax H3)
    "comfy_ace": "factory.providers.comfy_local",     # music (ACE-Step 1.5)
    "elevenlabs": "factory.providers.elevenlabs",     # voice, speech-to-speech
    "seedance": "factory.providers.seedance",         # video (text/image to video): b-roll, animated assets
    "suno": "factory.providers.suno",                 # music (via a gateway; Suno has no official public API)
    "generic_http": "factory.providers.generic_http", # any image/video/asset API described in config
}


def get(capability):
    """The module configured for a capability ("image", "video_talking", "video_broll", "voice", "music")."""
    from comun import CFG
    name = CFG.get("providers", {}).get(capability)
    if not name:
        raise KeyError(f"no provider configured for '{capability}' in config/local.json")
    return importlib.import_module(PROVIDERS[name]), name
