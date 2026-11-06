"""Voz unica del video con ElevenLabs v3 en modo Natural (stability 0.5: el modo Creative 0.0 hacia oscilar la entonacion).
Una linea por llamada -> vo/<id>.mp3. QC con Whisper contra el guion; hasta 3 tomas y se queda la MEJOR (los nombres propios
como "Hilma af Klint" Whisper los oye mal aunque esten bien dichos, asi que nunca se borra todo). La clave no se imprime.
Uso: python tts.py <carpeta>"""
import base64, json, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import clave_eleven, parecido, personaje, proyecto, texto_oido  # noqa: E402

carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
vo = carpeta / "vo"
vo.mkdir(exist_ok=True)
H = {"xi-api-key": clave_eleven(), "Content-Type": "application/json"}
VOZ = personaje(pj).get("voz", {}) if pj.get("personaje") else {}
for ln in pj["lineas"]:
    mp3 = vo / f"{ln['id']}.mp3"
    if mp3.exists():
        continue
    tomas = []
    for intento in range(3):
        toma = vo / f"{ln['id']}_t{intento}.mp3"
        body = {"text": ln.get("tts", ln["texto"]), "model_id": "eleven_v3", "voice_settings": {"stability": 0.5}}
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{pj['voz']}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(body).encode(), headers=H), timeout=120))
        toma.write_bytes(base64.b64decode(r["audio_base64"]))
        oido, lang = texto_oido(toma)
        p = parecido(ln["texto"], oido) if lang == "en" else 0.0
        print(f"{ln['id']} toma {intento} {p:.2f} {lang} | {oido}", flush=True)
        tomas.append((p, toma))
        if p >= 0.85:
            break
    mejor = max(tomas)[1]
    mejor.replace(mp3)
    if VOZ.get("procesado") == "ultratumba":   # personaje "de ultratumba": tono mas bajo, cripta, eco (voz_ultratumba.py)
        from voz_ultratumba import procesar
        crudo = mp3.with_name(mp3.stem + "_crudo.mp3"); mp3.replace(crudo); procesar(crudo, mp3, VOZ.get("semitonos", 2.0))
    for _, t in tomas:
        t.unlink(missing_ok=True)
