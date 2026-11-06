"""Path "assets": one command to make an image asset with any provider (local or paid), for a project or for the library.
  python assets.py --provider comfy_klein|qwen_layered|zimage|qwen_style|nano_banana|generic_http --prompt "..." [--refs a.png b.png]
                   --out <file.png> [--size 768x1344] [--seed 7] [--cutout]
--cutout removes the background afterwards (Motion DNA video_matte.py) for props and stickers.
Paid providers: the app shows the estimated cost and asks before running (house rule: quote USD first).
Remote MCP providers (Krea, Flora) are used by Claude directly from the app's chat, not from here."""
import argparse, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent))
from comun import MOTION_DNA, PY_PORTABLE  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--provider", required=True); ap.add_argument("--prompt", required=True); ap.add_argument("--refs", nargs="*", default=[])
ap.add_argument("--out", required=True); ap.add_argument("--size", default="768x1344"); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--cutout", action="store_true")
a = ap.parse_args()
out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
if a.provider in ("zimage", "qwen_style", "qwen_layered"):
    from factory.providers import local_tools as P
    res = P.image(a.prompt, a.refs, out, a.size, a.seed, tool=a.provider)
else:
    import importlib
    from factory.providers import PROVIDERS
    res = importlib.import_module(PROVIDERS[a.provider]).image(a.prompt, a.refs, out, a.size, a.seed)
if a.cutout:
    cut = Path(res).with_name(Path(res).stem + "_cutout.png")
    subprocess.run([PY_PORTABLE, str(MOTION_DNA / "tools" / "video_matte.py"), str(res), str(cut)], check=True)
    res = cut
print(res)
