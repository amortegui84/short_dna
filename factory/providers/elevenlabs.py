"""ElevenLabs: voice-over (text to speech, eleven_v3, stability 0.5 "Natural": Creative 0.0 made the intonation wobble) and
speech-to-speech (eleven_multilingual_sts_v2: keeps H3's timing, so the lipsync stays exact). The engine scripts tts.py and
sts.py already call it per project; these functions are for one-off assets. Key: ELEVENLABS_API_KEY in the .env."""
import base64, json, urllib.request, uuid
from pathlib import Path

from comun import clave

API = "https://api.elevenlabs.io/v1"


def voice(text, out, voice_id, model="eleven_v3", stability=0.5):
    body = {"text": text, "model_id": model, "voice_settings": {"stability": stability}}
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        f"{API}/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128", data=json.dumps(body).encode(),
        headers={"xi-api-key": clave("ELEVENLABS_API_KEY"), "Content-Type": "application/json"}), timeout=120))
    Path(out).write_bytes(base64.b64decode(r["audio_base64"]))
    return Path(out)


def voice_sts(audio_in, out, voice_id, stability=0.5, similarity=0.85, style=0.3):
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\neleven_multilingual_sts_v2\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"remove_background_noise\"\r\n\r\ntrue\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"voice_settings\"\r\n\r\n"
            + json.dumps({"stability": stability, "similarity_boost": similarity, "style": style}) + "\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"in.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode() \
        + Path(audio_in).read_bytes() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"{API}/speech-to-speech/{voice_id}?output_format=mp3_44100_128", data=body,
                                 headers={"xi-api-key": clave("ELEVENLABS_API_KEY"), "Content-Type": f"multipart/form-data; boundary={b}"})
    Path(out).write_bytes(urllib.request.urlopen(req, timeout=180).read())
    return Path(out)
