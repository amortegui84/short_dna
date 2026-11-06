"""A "from beyond the grave" voice for a character without a designed voice yet: ElevenLabs premade voices (no voice slot needed)
+ local processing: pitch down (default 2 semitones, tempo kept), a crypt reverb (multi-tap echo), low-pass air and a touch of
saturation. Used two ways:
  python voz_ultratumba.py pruebas <brand> "<line>" <voice_id:name> ...   -> brands/<b>/music/voz_pruebas/<name>.mp3 (+ _proc.wav)
  python voz_ultratumba.py procesar <in> <out> [--semitonos 2]             -> the same chain on any file (vo/ lines of a project)
Paid: ElevenLabs characters (quote first; ~$0.30 per 1000 characters on pay-as-you-go, library/costs.json)."""
import json, subprocess, sys, urllib.request, base64
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import clave, marca_dir  # noqa: E402


def cadena(semitonos=2.0):
    r = 2 ** (-semitonos / 12)
    return (f"asetrate=44100*{r:.4f},aresample=44100,atempo={1 / r:.4f},"
            "equalizer=f=120:t=q:w=1:g=3,lowpass=f=7500,"
            "aecho=0.8:0.6:60|143|251:0.30|0.18|0.10,"
            "acompressor=threshold=-18dB:ratio=3:attack=10:release=200,loudnorm=I=-20:TP=-2:LRA=7")


def procesar(src, dst, semitonos=2.0):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", cadena(semitonos), "-ar", "44100", str(dst)], check=True)
    return dst


if __name__ == "__main__":
    if sys.argv[1] == "procesar":
        st = float(sys.argv[sys.argv.index("--semitonos") + 1]) if "--semitonos" in sys.argv else 2.0
        procesar(sys.argv[2], sys.argv[3], st); print(sys.argv[3])
    else:
        marca, linea = sys.argv[2], sys.argv[3]
        d = marca_dir(marca, True) / "music" / "voz_pruebas"; d.mkdir(parents=True, exist_ok=True)
        for vn in sys.argv[4:]:
            vid, name = vn.split(":")
            body = {"text": linea, "model_id": "eleven_v3", "voice_settings": {"stability": 0.5}}
            r = json.load(urllib.request.urlopen(urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128", data=json.dumps(body).encode(),
                headers={"xi-api-key": clave("ELEVENLABS_API_KEY"), "Content-Type": "application/json"}), timeout=120))
            mp3 = d / f"{name}.mp3"; mp3.write_bytes(base64.b64decode(r["audio_base64"]))
            procesar(mp3, d / f"{name}_ultratumba.wav"); print(name, "ok", flush=True)
