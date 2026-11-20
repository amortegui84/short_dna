"""Hand insert for CCC (the host's hand, a 5 s Kling 4.0 reference-to-video clip, the hand as @Element1; never first/end frame).
Usage: python kling_mano.py <project> <M1|M2|M3> "<what the hand does>" <out name> [--dur 5] [--pagar]
The hand stills live in brands/ccc/characters/manos/ (Mx_x4.png + Mx_x4_close.png as the extra view). USD 0.157 a second at 720p."""
import base64, json, sys, time, urllib.error, urllib.request
from io import BytesIO
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from comun import marca_dir, proyecto  # noqa: E402

carpeta = Path(sys.argv[1]).resolve(); mano, accion, nombre = sys.argv[2], sys.argv[3], sys.argv[4]
DUR = int(sys.argv[sys.argv.index("--dur") + 1]) if "--dur" in sys.argv else 5
pj = proyecto(carpeta); M = marca_dir(pj["marca"]) / "characters" / "manos"
DESC = {"M1": "a stylized 3D art-toy hand with a black snake tattoo with stars and moons, orange-to-pink nails, a silver chain bracelet with a padlock",
        "M2": "a stylized 3D art-toy hand of a young Black man with bead and chain bracelets and a triangle ring",
        "M3": "a stylized 3D art-toy hand with black nails, silver rings and a pink scrunchie on the wrist"}[mano]
FONDO = {"M1": "teal", "M2": "magenta-red", "M3": "red-to-orange"}[mano]
prompt = (f"Vertical 9:16 shot of @Element1, {DESC}, exactly as in its reference images. Only the hand and wrist: no arm, no body, "
          f"no face. Smooth {FONDO} gradient studio background. Locked-off camera, no zoom. {accion} Clean hyperreal 3D render, "
          f"natural motion, sound of the action only, no voice, no music. Avoid: arm, body, face, extra fingers, morphing, text, logo.")
print(prompt, f"\n{DUR} s: USD {DUR * 0.157:.2f}")
if "--pagar" not in sys.argv:
    sys.exit()


def uri(p):
    from PIL import Image
    b = BytesIO(); Image.open(p).convert("RGB").save(b, "JPEG", quality=95)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


env = marca_dir(pj["marca"]) / ".env"
key = next(l.split("=", 1)[1].strip() for l in env.read_text(encoding="utf-8").splitlines() if l.startswith("FAL_KEY="))
H = {"Authorization": f"Key {key}", "Content-Type": "application/json"}


def fal(url, body=None):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers=H, method="POST" if body else "GET")
    try:
        return json.load(urllib.request.urlopen(r, timeout=300))
    except urllib.error.HTTPError as e:
        sys.exit(f"fal {e.code}: {e.read().decode(errors='replace')[:500]}")


sub = fal("https://queue.fal.run/kling/v4/reference-to-video", {
    "prompt": prompt, "duration": DUR, "resolution": "720p", "aspect_ratio": "9:16",
    "elements": [{"frontal_image_url": uri(M / f"{mano}_x4.png"), "reference_image_urls": [uri(M / f"{mano}_x4_close.png")]}]})
while fal(sub["status_url"]).get("status") != "COMPLETED":
    time.sleep(10)
res = fal(sub["response_url"])
out = carpeta / "clips" / f"{nombre}.mp4"
out.write_bytes(urllib.request.urlopen(res["video"]["url"], timeout=300).read())
log_p = carpeta / "costos.json"; log = json.loads(log_p.read_text(encoding="utf-8")) if log_p.exists() else {"clips": []}
log["clips"].append({"clip": nombre, "mano": mano, "pedido_s": DUR, "usd": round(DUR * 0.157, 3)})
log["total_usd"] = round(sum(c["usd"] for c in log["clips"]), 3); log_p.write_text(json.dumps(log, indent=1), encoding="utf-8")
print("ok", out)
