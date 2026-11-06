"""Seedance (ByteDance) video generation: text-to-video and image-to-video for b-roll and animated assets (never for the
presenter's talking lines: H3 keeps the lipsync and the face). Async task API: create a task, poll it, download the video.

Default request shape = BytePlus ModelArk / Volcengine Ark "contents/generations/tasks" (SEEDANCE_BASE_URL, e.g.
https://ark.ap-southeast.bytepluses.com/api/v3). Resellers (fal.ai and others) use other shapes: set config
"seedance": {"style": "ark" | "custom", ...} and adapt _crear/_estado. VERIFY the model id and fields against the provider's
current docs before the first paid run, and quote the cost in USD to the user first (house rule)."""
import json, time, urllib.request
from pathlib import Path

from comun import CFG, clave

C = CFG.get("seedance", {})
MODEL = C.get("model", "seedance-1-0-pro-250528")


def _req(method, url, body=None):
    r = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                               headers={"Authorization": f"Bearer {clave('SEEDANCE_API_KEY')}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=120))


def video(prompt, out, image=None, seconds=5, audio=None, ratio="9:16"):
    base = clave("SEEDANCE_BASE_URL").rstrip("/")
    content = [{"type": "text", "text": f"{prompt} --ratio {ratio} --duration {int(seconds)}"}]
    if image:
        content.append({"type": "image_url", "image_url": {"url": image}})   # a public URL or data: URI, per provider
    task = _req("POST", f"{base}/contents/generations/tasks", {"model": MODEL, "content": content})
    tid = task["id"]
    for _ in range(240):
        st = _req("GET", f"{base}/contents/generations/tasks/{tid}")
        if st.get("status") == "succeeded":
            url = st["content"]["video_url"]
            Path(out).write_bytes(urllib.request.urlopen(url, timeout=300).read())
            return Path(out)
        if st.get("status") in ("failed", "cancelled"):
            raise RuntimeError(f"seedance task {tid}: {st.get('error')}")
        time.sleep(5)
    raise TimeoutError(f"seedance task {tid} did not finish")
