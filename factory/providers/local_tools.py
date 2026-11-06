"""Other local image tools, called through the scripts/servers already on this machine (config paths, nothing hardcoded):
- zimage: Z-Image Turbo in ComfyUI (config "zimage": {"script": ".../zimage_gen.py"}): 9 steps, cfg 1, optional LoRA. Fast single
  images without references (props, backgrounds, styles); character identity is better with Klein references. docs/models/Z_IMAGE.md
- qwen_style: QwenStudio style transfer (config "qwen": {"url": "http://127.0.0.1:7860"}): redraws an image in the style of another.
  Never load QwenStudio and H3 at the same time on a 24 GB GPU (two blue screens). docs/models/QWEN.md"""
import base64, json, mimetypes, subprocess, sys, urllib.request
from pathlib import Path

from comun import CFG


def image(prompt, refs, out, size="768x1344", seed=0, tool="zimage"):
    if tool == "zimage":
        subprocess.run([sys.executable, CFG["zimage"]["script"], "-p", prompt, "-o", str(out), "--size", size, "--seed", str(seed)], check=True)
        return Path(out)
    if tool == "qwen_style":   # refs = [photo, style]
        du = lambda p: "data:%s;base64,%s" % (mimetypes.guess_type(str(p))[0] or "image/png", base64.b64encode(Path(p).read_bytes()).decode())
        body = {"imagen": du(refs[0]), "estilo": du(refs[1]), "prompt": prompt, "seed": seed}
        r = json.load(urllib.request.urlopen(urllib.request.Request(CFG["qwen"]["url"] + "/api/estilo", data=json.dumps(body).encode(),
                                                                    headers={"Content-Type": "application/json"}), timeout=600))
        img = r.get("imagen") or r.get("image")
        Path(out).write_bytes(base64.b64decode(img.split(",", 1)[1]))
        return Path(out)
    raise ValueError(tool)
