"""The signature ending (stage "final"): the narrator self-destructs in a way tied to the story, generated with MiniMax H3
(local) from his own last frame, with its own sound. The edit cuts to it after the last line and ends on END OF TAPE.
proyecto.json "autodestruccion": {"tipo": ..., "porque": ..., "prompt": "what happens to him, tied to the story"}.
Takes the last frame of the last talking clip as the start picture (plus the character master for identity).
Writes final/autodestruccion.mp4 (+ final/inicio.png, final/prompt.txt). Skips if it exists.
Usage: python final.py <project>"""
import os, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import H3, PY_PORTABLE, con_mesa, personaje, proyecto, run  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); pj = proyecto(carpeta)
ad = pj.get("autodestruccion") or {}
if not ad.get("prompt"):
    sys.exit("final: no autodestruccion.prompt in proyecto.json (write what happens to him, tied to the story)")
F = carpeta / "final"; F.mkdir(exist_ok=True)
out = F / "autodestruccion.mp4"
if out.exists():
    print("final: exists", out); sys.exit()
PJE = personaje(pj)
ultimo = [l["id"] for l in pj["lineas"] if l["tipo"] == "A"][-1]
inicio = F / "inicio.png"
run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.15", "-i", str(carpeta / "clips" / f"{ultimo}.mp4"), "-frames:v", "1", "-update", "1", str(inicio)])
prompt = f"""subject_definitions:
<Subject 1> is the hooded storyteller from <Picture 1>: black hood and robe, a smooth pale-yellow oval mask with no mouth and a single painted black eye, black gloves; his look matches <Picture 2> exactly.

summary:
[reference-to-video generation + audio generation]
The ending of a horror-storytelling Short: the masked narrator self-destructs, his signature farewell.

retention_analysis:
<Subject 1>: fully_preserved at the start (mask, hood, robe, gloves, room), then he is destroyed

detailed_description:
A realistic, grainy vertical 9:16 video, static camera at eye level, medium shot, continuing exactly from <Picture 1>: <Subject 1> sits in his dark ritual room, CRT televisions with static behind him, clear plastic sheeting, melted candles, red light from one side and cold blue CRT glow from the other. He stays still for a moment, then: {ad['prompt']} He does not speak. The mask never gets a mouth.

overall_soundscape:
{ad.get('sonido', 'Low room tone and CRT hum, then the sound of his destruction, close and detailed, ending in silence.')}

non_diegetic_music:
N/A
"""
prompt = con_mesa(prompt, pj)   # the episode's own props on the table instead of the candles
(F / "prompt.txt").write_text(prompt, encoding="utf-8")
PIKA = ["--turbo", "pika_h3_flex_ref2va_v1_bf16.safetensors", "--steps", "6", "--no-shift", "--size", "768x1344",
        "--lora", "minidv_lora_h3_v1.safetensors:0.9"]
ENV = dict(os.environ, H3_SAMPLER="lcm", H3_SIGMAS="1.0, 0.972973, 0.923077, 0.8, 0.571429, 0.333333, 0.0")
subprocess.run([PY_PORTABLE, H3, "-p", str(F / "prompt.txt"), "--img", str(inicio), str(PJE["_dir"] / PJE["maestro"]),
                "--seconds", str(ad.get("segundos", 5.17)), *PIKA, "--gen-audio", "--seeds", str(ad.get("seed", 31)), "-o", str(out)], check=True, env=ENV)
print("final:", out)
