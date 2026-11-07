"""Looks of a character (outfit + pose + head angle) with Flux Klein: two references, <1> the character's base scene (room, mic,
framing) and <2> the master portrait (face). Only the outfit, the pose and the head angle change; the face, the room and the
gaze to the lens stay. Rules learned in review (docs/LEARNINGS.md #character): no mesh or see-through clothing, no crossed hands,
eyes to the lens, and spread the head tilt (left, right, upright) so a channel grid shows no pattern.

  python looks.py <character_slug> [--brand <brand>] "<outfit>" "<pose and head angle>" --name 07_trench [--seeds 2]
Writes library/characters/<slug>/looks/_candidatos/<name>_sN.jpg; pick one, move it to looks/<name>.jpg and add it to
character.json "looks" (the skill does this with the user)."""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comun import LIB, buscar, con_mesa  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("personaje"); ap.add_argument("ropa"); ap.add_argument("pose"); ap.add_argument("--name", required=True)
ap.add_argument("--seeds", type=int, default=2); ap.add_argument("--base", help="look image to start from instead of the base scene")
ap.add_argument("--brand", help="brand folder that holds the character (brands/<brand>/characters)")
ap.add_argument("--mesa", help="props on the table instead of the candles of the character's scene (see comun.con_mesa)")
ap.add_argument("--lugar", help="a new place instead of the character's room, e.g. a jungle at night (comun.con_mesa \"escenario\")")
a = ap.parse_args()
d = buscar("characters", a.personaje, a.brand)
c = json.loads((d / "character.json").read_text(encoding="utf-8"))
out = d / "looks" / "_candidatos"; out.mkdir(parents=True, exist_ok=True)
base = str(d / (a.base or c["escena_base"]))
items = [{"name": f"{a.name}_s{k + 1}", "refs": [base, str(d / c["maestro"])], "seed": 51000 + k, "size": "768x1344",
          "prompt": f"The character now wears {a.ropa} {a.pose} {c['mirada']} {con_mesa(c['identidad_fija'], {'mesa': a.mesa, **({'escenario': {'lugar': a.lugar}} if a.lugar else {})})}"} for k in range(a.seeds)]
spec = out / f"{a.name}_spec.json"
spec.write_text(json.dumps({"out_dir": str(out), "items": items}, indent=2), encoding="utf-8")
subprocess.run([sys.executable, str(Path(__file__).parent / "klein_gen.py"), "--spec", str(spec)], check=True)
print("candidates in", out)
