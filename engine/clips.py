"""Clips del avatar hablando (lineas tipo A) con H3 local, receta de RECETA_HISTORIAS_PERSONAS: turbo Pika H3 Flex a 6 pasos,
lcm + sigmas manuales, sin shift, --size 768x1344, MiniDV 0.9 sin disparador. Escena: humana streamer con microfono en brazo
(la que el usuario vio "mucho mas real"). QC: idioma en + >= 85 % del guion; hasta 3 semillas, se queda la mejor.
Uso: python clips.py <carpeta> [L01 L03 ...]"""
import difflib, json, os, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import H3, PY_PORTABLE, clip_roto, con_mesa, duracion, escena_de, palabras, personaje, proyecto, run  # noqa: E402

carpeta = Path(sys.argv[1])
pj = proyecto(carpeta)
PJE = personaje(pj)   # library/characters/<slug>/character.json: cara, escena base, looks y textos del prompt
# escena del look elegido para el video (o la escena base del personaje); rutas relativas a la carpeta del proyecto
ESCENA = escena_de(pj, carpeta)
MAESTRO = PJE["_dir"] / PJE["maestro"]
CLIPS = carpeta / "clips"
CLIPS.mkdir(exist_ok=True)
(carpeta / "prompts").mkdir(exist_ok=True)
PIKA = ["--turbo", "pika_h3_flex_ref2va_v1_bf16.safetensors", "--steps", "6", "--no-shift", "--size", "768x1344",
        "--lora", "minidv_lora_h3_v1.safetensors:0.9"]
ENV = dict(os.environ, H3_SAMPLER="lcm", H3_SIGMAS="1.0, 0.972973, 0.923077, 0.8, 0.571429, 0.333333, 0.0")
REJILLA = [4.46, 5.17, 5.875, 6.58, 7.29, 8.0, 8.71, 9.42]

# referencia de voz: 8 s de la voz elegida del propio video (para que el timbre del clip se parezca a la VO)
voz_ref = carpeta / "vo" / "voz_ref.wav"
if not voz_ref.exists():
    bs = [carpeta / "vo" / f"{l['id']}.mp3" for l in pj["lineas"] if l["tipo"] == "B"][:2]
    run(["ffmpeg", "-y", "-v", "error", "-i", str(bs[0]), "-i", str(bs[1]), "-filter_complex",
         "[0:a][1:a]concat=n=2:v=0:a=1,atrim=0:8", "-ac", "1", "-ar", "24000", str(voz_ref)])

ids = [a for a in sys.argv[2:] if a.startswith("L")] or [l["id"] for l in pj["lineas"] if l["tipo"] == "A"]
for ln in [l for l in pj["lineas"] if l["id"] in ids]:
    lid = ln["id"]
    out = CLIPS / f"{lid}.mp4"
    if out.exists():
        continue
    # version avatar: cada linea A puede arrancar de su propio cuadro (pj["inicios"][lid], ruta relativa a avatares_arte)
    escena = carpeta / pj["inicios"][lid] if lid in pj.get("inicios", {}) else ESCENA
    # sin puntos suspensivos (H3 inventa palabras en la pausa) y sin frases fuera de <d> (H3 las dice en voz alta)
    dialogo = ln["texto"].replace("...", ",").replace(",,", ",")
    seg = next((s for s in REJILLA if s >= len(dialogo.split()) / 2.7 + 0.8), REJILLA[-1])   # long line: longest clip, continuar extends it
    if PJE.get("sin_boca") and (carpeta / "vo" / f"{lid}.mp3").exists():   # sin boca: el clip dura lo que la voz dramatica (pausas incluidas)
        vd = duracion(carpeta / "vo" / f"{lid}.mp3") + 0.3
        seg = next((s for s in REJILLA if s >= vd), REJILLA[-1])
    prompt = PJE["prompt_clip"].format(artista=pj.get("artista", pj.get("tema", "")), accion=ln["accion"], dialogo=dialogo)
    prompt = con_mesa(prompt, pj)   # the episode's own props on the table instead of the candles
    pf = carpeta / "prompts" / f"{lid}.txt"
    pf.write_text(prompt, encoding="utf-8")
    esperado = re.sub(r"[^a-z ]", "", ln["texto"].lower()).split()
    mejor = (-1, None)
    for seed in (23, 24, 25):
        tmp = CLIPS / f"{lid}_s{seed}.mp4"
        subprocess.run([PY_PORTABLE, H3, "-p", str(pf), "--img", str(escena), str(MAESTRO), "--audio", str(voz_ref),
                        "--seconds", str(seg), *PIKA, "--gen-audio", "--seeds", str(seed), "-o", str(tmp)], check=True, env=ENV)
        oido = [re.sub(r"[^a-z]", "", w.lower()) for w, _, _ in palabras(tmp)]   # QC: Whisper sobre el audio que genero H3
        ratio = difflib.SequenceMatcher(None, esperado, [w for w in oido if w]).ratio()
        roto = clip_roto(tmp)   # a take that collapses mid-clip (dark, smeared) loses to any sound take
        if roto:
            ratio -= 1
        print(f"[{lid}] seed {seed}: ratio={ratio:.2f} oido={' '.join(oido)}" + (f" BROKEN: {roto}" if roto else ""), flush=True)
        if ratio > mejor[0]:
            mejor = (ratio, tmp)
        if ratio >= 0.85:
            break
    mejor[1].replace(out)
    print(f"[{lid}] elegido ratio={mejor[0]:.2f}", flush=True)
