"""Any asset API (image, video, 3D, upscale...) described in config instead of code, so a new service plugs in without a new
module. config/local.json:
  "generic_http": {"image": {"url": "{ASSETS_BASE_URL}/v1/images", "body": {"prompt": "{prompt}", "size": "{size}"},
                             "result": "data.0.url", "auth": "Bearer {ASSETS_API_KEY}"}}
Placeholders {NAME} come from the call arguments or the .env; "result" is a dotted path to the URL (or base64 with "b64:")
in the JSON response. For async APIs add "poll": {"url": "...{id}", "id": "id", "done": "status=succeeded"}."""
import base64, json, re, time, urllib.request
from pathlib import Path

from comun import CFG, clave


def _fill(x, vals):
    if isinstance(x, str):
        return re.sub(r"\{(\w+)\}", lambda m: str(vals[m.group(1)]) if m.group(1) in vals else clave(m.group(1)), x)
    if isinstance(x, dict):
        return {k: _fill(v, vals) for k, v in x.items()}
    if isinstance(x, list):
        return [_fill(v, vals) for v in x]
    return x


def _path(d, p):
    for k in p.split("."):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def _call(kind, out, **vals):
    c = CFG["generic_http"][kind]
    req = urllib.request.Request(_fill(c["url"], vals), data=json.dumps(_fill(c.get("body", {}), vals)).encode(),
                                 headers={"Authorization": _fill(c.get("auth", ""), vals), "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    if "poll" in c:
        p = c["poll"]; tid = _path(r, p["id"]); campo, valor = p["done"].split("=")
        for _ in range(240):
            r = json.load(urllib.request.urlopen(urllib.request.Request(_fill(p["url"], dict(vals, id=tid)),
                                                                        headers={"Authorization": _fill(c.get("auth", ""), vals)}), timeout=120))
            if str(_path(r, campo)) == valor:
                break
            time.sleep(5)
    res = c["result"]
    if res.startswith("b64:"):
        Path(out).write_bytes(base64.b64decode(_path(r, res[4:])))
    else:
        Path(out).write_bytes(urllib.request.urlopen(_path(r, res), timeout=300).read())
    return Path(out)


def image(prompt, refs, out, size="768x1344", seed=0):
    return _call("image", out, prompt=prompt, size=size, seed=seed)


def video(prompt, out, image=None, seconds=5, audio=None):
    return _call("video", out, prompt=prompt, image=image or "", seconds=seconds)
