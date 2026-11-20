"""QC del video final de un artista: coincidencia con el guion (Whisper), loudness, duracion, brillo del avatar y hoja de contacto.
Escribe qc.json y hoja.jpg en la carpeta. Uso: python qc.py <carpeta>"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageStat

sys.path.insert(0, str(Path(__file__).parent))
from comun import duracion, parecido, proyecto, texto_oido, ultimo_render  # noqa: E402

carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
v = ultimo_render(carpeta, pj["slug"])
guion = " ".join(l["texto"] for l in pj["lineas"])
oido, lang = texto_oido(v)
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", str(v), "-af", "ebur128", "-f", "null", "-"],
                                                          capture_output=True, text=True).stderr)[-1]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vf", "fps=0.5,scale=160:-1,tile=11x3", "-frames:v", "1",
                str(carpeta / "hoja.jpg")], check=True)
tl = json.loads((carpeta / "timeline.json").read_text(encoding="utf-8"))
a = next(s for s in tl["segmentos"] if s["tipo"] == "A")
f = carpeta / "_brillo.png"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a["start"] + 1), "-i", str(v), "-frames:v", "1", str(f)], check=True)
brillo = round(sum(ImageStat.Stat(Image.open(f).convert("L")).mean), 1)
f.unlink()
r = {"video": v.name, "duracion_s": round(duracion(v), 1), "lufs": float(lufs), "idioma": lang,
     "coincidencia_guion": round(parecido(guion, oido), 2), "brillo_avatar": brillo}
# review 2026-11-14 (ep13 1:08): the overall match passed a render that lost the last word of two lines; listen line by line
from qa_audio_render import revisar as revisar_render  # noqa: E402
ar = revisar_render(carpeta, v)
r["audio_render"] = "ok" if ar["ok"] else ar["fallas"]
r["ok"] = r["coincidencia_guion"] >= 0.85 and lang == "en" and -21.5 <= r["lufs"] <= -18.5 and ar["ok"]
(carpeta / "qc.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(r, ensure_ascii=False))
sys.exit(0 if r["ok"] else 1)
