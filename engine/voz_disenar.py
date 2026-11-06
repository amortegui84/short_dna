"""Voice Design (ElevenLabs): previews from a description, then save the chosen one as a voice in the account (uses a voice slot).
  python voz_disenar.py previews <brand> <character>        -> brands/<b>/music/voz_diseno/preview_N.mp3 + previews.json
  python voz_disenar.py guardar <brand> <character> <N>       -> creates the voice, writes its voice_id into character.json
The description comes from character.json "voz.descripcion"; the sample text from the brand's first episode hook if present.
Paid: preview generation and saving use ElevenLabs credits (quote first)."""
import base64, json, sys, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import buscar, clave, marca_dir  # noqa: E402

API = "https://api.elevenlabs.io/v1"
H = lambda: {"xi-api-key": clave("ELEVENLABS_API_KEY"), "Content-Type": "application/json"}
cmd, marca, pers = sys.argv[1], sys.argv[2], sys.argv[3]
cf = buscar("characters", pers, marca) / "character.json"; c = json.loads(cf.read_text(encoding="utf-8"))
d = marca_dir(marca, True) / "music" / "voz_diseno"; d.mkdir(parents=True, exist_ok=True)
TEXT = ("In 1983, a U.S. Army officer wrote a secret report on how to leave your body. One page stayed missing for decades. "
        "Tonight, I will tell you what was written on it... and what it asked of the people who read it. Close your eyes. Carefully.")


def post(url, body):
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(), headers=H()), timeout=300))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} {url}: {e.read().decode()[:400]}")


if cmd == "previews":
    desc = c["voz"]["descripcion"]
    try:
        r = post(f"{API}/text-to-voice/design", {"voice_description": desc, "model_id": "eleven_ttv_v3", "text": TEXT, "auto_generate_text": False})
    except SystemExit as e:
        print("design endpoint failed, trying create-previews:", e)
        r = post(f"{API}/text-to-voice/create-previews", {"voice_description": desc, "text": TEXT})
    out = []
    for i, p in enumerate(r.get("previews", []), 1):
        f = d / f"preview_{i}.mp3"; f.write_bytes(base64.b64decode(p["audio_base_64"]))
        out.append({"n": i, "file": f.name, "generated_voice_id": p["generated_voice_id"], "dur": p.get("duration_secs")})
    (d / "previews.json").write_text(json.dumps({"descripcion": desc, "texto": TEXT, "previews": out}, indent=1), encoding="utf-8")
    print(json.dumps(out))
else:
    n = int(sys.argv[4]); pv = json.loads((d / "previews.json").read_text(encoding="utf-8"))
    p = next(x for x in pv["previews"] if x["n"] == n)
    r = post(f"{API}/text-to-voice", {"voice_name": f"{marca} {pers}", "voice_description": pv["descripcion"], "generated_voice_id": p["generated_voice_id"]})
    c["voz"].update({"voice_id": r["voice_id"], "nombre": f"Voice Design '{marca} {pers}' (preview {n})", "tipo": "voice_design", "procesado": c["voz"].get("procesado")})
    cf.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
    print("saved", r["voice_id"])
