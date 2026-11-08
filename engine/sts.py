"""Voz de los planos del avatar = el audio que genero H3 (labios perfectos), con el timbre cambiado a la voz del video
mediante ElevenLabs Speech-to-Speech (respeta ritmo, pausas y silabas de H3). Solo audio sintetico del guion.
Para cada linea A: recorta la ventana de habla del clip, la convierte y deja audio/<id>_sts.wav. La clave no se imprime.
Con --vo tambien convierte las lineas B (voz en off de TTS) con el mismo STS, para que cabeza y VO sean una sola voz:
toma la linea ya montada (audio/<id>_sinigualar.wav o audio/<id>.wav), guarda el original como audio/<id>_tts.wav y deja el
resultado en audio/<id>_sinigualar.wav (el STS respeta la duracion); despues correr igualar_voz.py.
Uso: python sts.py <carpeta> [--vo]"""
import json, shutil, sys, urllib.request, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import clave_eleven, palabras, proyecto, run  # noqa: E402

carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
aud = carpeta / "audio"
aud.mkdir(exist_ok=True)
KEY = clave_eleven()
# conversion settings: the character's voz.sts_ajustes if any (CCC: style 0.6, stability 0.35, a livelier read)
from comun import personaje  # noqa: E402
AJ = (personaje(pj).get("voz", {}) if pj.get("personaje") else {}).get("sts_ajustes", {"stability": 0.5, "similarity_boost": 0.85, "style": 0.3})


def convertir(src, nombre):
    """One speech-to-speech call (same model and settings as the host lines)."""
    b = uuid.uuid4().hex
    nl = chr(13) + chr(10)
    def campo(nombre_campo, valor):
        return f"--{b}{nl}Content-Disposition: form-data; name=\"{nombre_campo}\"{nl}{nl}{valor}{nl}"
    cuerpo = (campo("model_id", "eleven_multilingual_sts_v2") + campo("remove_background_noise", "true")
              + campo("voice_settings", json.dumps(AJ))
              + f"--{b}{nl}Content-Disposition: form-data; name=\"audio\"; filename=\"{nombre}.wav\"{nl}Content-Type: audio/wav{nl}{nl}").encode()         + src.read_bytes() + f"{nl}--{b}--{nl}".encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/speech-to-speech/{pj['voz']}?output_format=mp3_44100_128",
                                 data=cuerpo, headers={"xi-api-key": KEY, "Content-Type": f"multipart/form-data; boundary={b}"})
    return urllib.request.urlopen(req, timeout=180).read()


if "--vo" in sys.argv:
    for ln in [l for l in pj["lineas"] if l["tipo"] != "A"]:
        lid = ln["id"]
        tts = aud / f"{lid}_tts.wav"
        if tts.exists():
            continue
        base = aud / f"{lid}_sinigualar.wav"
        base = base if base.exists() else aud / f"{lid}.wav"
        shutil.copy2(base, tts)
        src = aud / f"_{lid}_in.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(tts), "-ac", "1", "-ar", "44100", str(src)])
        mp3 = aud / f"{lid}_sts.mp3"
        mp3.write_bytes(convertir(src, lid))
        src.unlink()
        # keep the montaged length exactly (STS can differ by a few ms): pad or trim to the TTS line
        run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-i", str(tts), "-filter_complex", "[0]apad[a];[a][1]amix=inputs=2:weights='1 0':duration=shortest", "-ar", "48000", str(aud / f"{lid}_sinigualar.wav")])
        print(lid, "VO convertida con STS", flush=True)
for ln in [l for l in pj["lineas"] if l["tipo"] == "A"]:
    lid = ln["id"]
    out = aud / f"{lid}_sts.mp3"
    if out.exists():
        continue
    clip = carpeta / "clips" / f"{lid}.mp4"
    ws = palabras(clip)
    t0, t1 = max(0.0, ws[0][1] - 0.12), ws[-1][2] + 0.18
    src = aud / f"{lid}_h3.wav"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", str(clip), "-vn", "-ac", "1", "-ar", "44100", str(src)])
    b = uuid.uuid4().hex
    cuerpo = (f"--{b}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\neleven_multilingual_sts_v2\r\n"
              f"--{b}\r\nContent-Disposition: form-data; name=\"remove_background_noise\"\r\n\r\ntrue\r\n"
              f"--{b}\r\nContent-Disposition: form-data; name=\"voice_settings\"\r\n\r\n"
              + json.dumps(AJ) + "\r\n"
              f"--{b}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"{lid}.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode() \
        + src.read_bytes() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/speech-to-speech/{pj['voz']}?output_format=mp3_44100_128",
                                 data=cuerpo, headers={"xi-api-key": KEY, "Content-Type": f"multipart/form-data; boundary={b}"})
    out.write_bytes(urllib.request.urlopen(req, timeout=180).read())
    (aud / f"{lid}_ventana.json").write_text(json.dumps({"t0": t0, "t1": t1}), encoding="utf-8")
    print(lid, f"{t1 - t0:.2f}s convertido", flush=True)
