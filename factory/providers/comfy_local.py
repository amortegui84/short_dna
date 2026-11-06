"""Local ComfyUI providers (no cost, one GPU job at a time):
- image: Flux 3 Klein through engine/klein_gen.py (ComfyUI 0.41, config comfy_klein). References carry identity: <1> scene/look,
  <2> master portrait. Non-commercial model licence (FLUX Kommunity): check before client work.
- video (talking): MiniMax H3 through engine/clips.py (ComfyUI config comfy_h3): reference image + voice reference -> clip with audio.
- music: ACE-Step 1.5 through engine/musica.py."""
import json, subprocess, sys, tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[2] / "engine"


def image(prompt, refs, out, size="768x1344", seed=0):
    out = Path(out)
    spec = {"out_dir": str(out.parent), "items": [{"name": out.stem, "prompt": prompt, "refs": [str(r) for r in refs], "size": size, "seed": seed}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(spec, f)
    subprocess.run([sys.executable, str(ENGINE / "klein_gen.py"), "--spec", f.name], check=True)
    return out.with_suffix(".png")


def video(prompt, out, image=None, seconds=5, audio=None):
    raise NotImplementedError("talking clips go through engine/clips.py (per project line); b-roll: use the 'seedance' provider")


def music(tags, out, seconds=80, bpm=None, key=None):
    raise NotImplementedError("per project: engine/musica.py <project> (reads proyecto.json 'musica' or the style's default)")
