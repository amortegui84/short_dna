"""Music bed for one video with ElevenLabs Music (instrumental, made for the video; never a real song or artist's audio).
Usage: python musica_eleven.py <project> "<style prompt>" [--dur 70] [--n 2]
Writes <project>/musica/eleven_<n>.mp3. Key: the brand's .env (ELEVENLABS_API_KEY), never printed. Paid in credits."""
import json, sys, urllib.error, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from comun import clave_eleven, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); estilo = sys.argv[2]
dur = float(sys.argv[sys.argv.index("--dur") + 1]) if "--dur" in sys.argv else 70
n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 2
pj = proyecto(carpeta); key = clave_eleven(pj)
(carpeta / "musica").mkdir(exist_ok=True)
for i in range(1, n + 1):
    body = {"prompt": estilo + " Instrumental only, no vocals. It sits under a fast spoken voice-over: no lead melody in the "
                               "voice range, steady energy, clean ending.",
            "music_length_ms": int(dur * 1000), "force_instrumental": True}
    r = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", data=json.dumps(body).encode(),
                               headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        data = urllib.request.urlopen(r, timeout=600).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs music {e.code}: {e.read().decode(errors='replace')[:500]}")
    out = carpeta / "musica" / f"eleven_{i}.mp3"; out.write_bytes(data); print("ok", out, flush=True)
(carpeta / "musica" / "prompt.txt").write_text(estilo, encoding="utf-8")
