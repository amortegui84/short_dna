"""Google "Nano Banana" (Gemini image generation and editing) for assets: props, backgrounds, character sheets, edits of a
reference ("same character, now holding a book"). Up to several reference images per call; good at keeping identity and text.
Gemini API generateContent: POST {base}/models/{model}:generateContent with header x-goog-api-key; parts = text + inline_data
images; the answer's parts carry inline_data (base64 PNG). Model id in config "nano_banana": {"model": "..."} (the family has
several versions; default below). Key: GEMINI_API_KEY in the .env. Paid: quote USD before batches. Generated images carry
Google's SynthID watermark; disclose AI content where the platform asks (docs/PLATFORMS.md)."""
import base64, json, mimetypes, urllib.request
from pathlib import Path

from comun import CFG, clave

C = CFG.get("nano_banana", {})
BASE = C.get("base", "https://generativelanguage.googleapis.com/v1beta")
MODEL = C.get("model", "gemini-2.5-flash-image")


def image(prompt, refs, out, size="768x1344", seed=0):
    w, h = (int(x) for x in size.split("x"))
    parts = [{"text": f"{prompt}\nAspect ratio {w}:{h} (vertical)" if h > w else prompt}]
    for r in refs or []:
        parts.append({"inline_data": {"mime_type": mimetypes.guess_type(str(r))[0] or "image/png", "data": base64.b64encode(Path(r).read_bytes()).decode()}})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    req = urllib.request.Request(f"{BASE}/models/{MODEL}:generateContent", data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": clave("GEMINI_API_KEY"), "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    for p in r["candidates"][0]["content"]["parts"]:
        d = p.get("inline_data") or p.get("inlineData")
        if d:
            Path(out).write_bytes(base64.b64decode(d["data"]))
            return Path(out)
    raise RuntimeError("no image in the answer: " + json.dumps(r)[:300])
