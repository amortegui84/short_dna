"""Suno music. Suno has no official public API; teams use a gateway (self-hosted or a paid reseller). This adapter speaks the
common gateway shape: POST {SUNO_BASE_URL}/generate {prompt|tags, make_instrumental, ...} -> ids, then poll
GET {SUNO_BASE_URL}/get?ids=... until audio_url. Set config "suno": {"generate": "/api/custom_generate", "get": "/api/get"} if
yours differs, and check its terms (commercial use needs a paid Suno plan). Output: an mp3, then engine/musica.py --elegir style
normalisation (-27 LUFS) applies to it the same way."""
import json, time, urllib.request
from pathlib import Path

from comun import CFG, clave

C = CFG.get("suno", {})


def _req(method, path, body=None):
    url = clave("SUNO_BASE_URL").rstrip("/") + path
    r = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                               headers={"Authorization": f"Bearer {clave('SUNO_API_KEY')}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=120))


def music(tags, out, seconds=80, bpm=None, key=None):
    body = {"tags": tags, "prompt": "", "make_instrumental": True, "title": Path(out).stem}
    res = _req("POST", C.get("generate", "/api/custom_generate"), body)
    ids = ",".join(x["id"] for x in (res if isinstance(res, list) else res.get("data", [])))
    for _ in range(120):
        items = _req("GET", C.get("get", "/api/get") + f"?ids={ids}")
        items = items if isinstance(items, list) else items.get("data", [])
        listos = [x for x in items if x.get("audio_url") and x.get("status") in ("complete", "streaming", "succeeded")]
        if listos:
            Path(out).write_bytes(urllib.request.urlopen(listos[0]["audio_url"], timeout=300).read())
            return Path(out)
        time.sleep(5)
    raise TimeoutError("suno did not return audio")
