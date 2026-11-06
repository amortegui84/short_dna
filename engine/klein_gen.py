#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
klein_gen.py - FLUX 3 Image Klein (distilado, int8) con hasta 10 imagenes de referencia, por la API del ComfyUI 0.41 paralelo (puerto 8189).
Sirve para fotogramas clave y looks de personajes. Las referencias dan la identidad; el prompt describe la escena completa.

  python klein_gen.py -p "texto" --refs a.png b.png -o salida.png [--size 1344x768] [--seed 7] [--steps 16]
  python klein_gen.py --spec items.json        # {"out_dir": "...", "items": [{"name","prompt","refs":[...],"size","seed"}]}

Instalacion: D:\ComfyUI_QI21 (ComfyUI 0.41, NO tocar el 0.34 de MiniMax). Arrancar: python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --port 8189
Modelos (compartidos por extra_model_paths): flux3_image_klein_sd_int8_convrot, qwen3vl_4b_int8_convrot (tipo flux3), flux2-vae.
Los modelos de Black Forest Labs estan en un repositorio restringido: se bajan con la sesion de Hugging Face del usuario (licencia FLUX Kommunity, no comercial).
"""
import argparse, json, os, shutil, sys, time, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CFG  # noqa: E402
SERVER = CFG["comfy_klein"]["url"]
COMFY = CFG["comfy_klein"]["comfy_dir"]


def post(path, payload):
    req = urllib.request.Request(SERVER + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=60).read().decode()


def get(path):
    return json.loads(urllib.request.urlopen(SERVER + path, timeout=60).read().decode())


def graph(prompt, refs, w, h, seed, steps, prefix):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux3_image_klein_sd_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_int8_convrot.safetensors", "type": "flux3", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "32": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "44": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
    }
    rm = {"positive": ["4", 0], "negative": ["32", 0], "vae": ["3", 0], "resolution": "resize", "resolution.megapixels": 1.0}
    for i, name in enumerate(refs):
        nid = str(100 + i)
        g[nid] = {"class_type": "LoadImage", "inputs": {"image": name}}
        rm["images.image%d" % i] = [nid, 0]
    g["17"] = {"class_type": "ReferenceMultiLatent", "inputs": rm}
    g["7"] = {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["17", 0], "negative": ["17", 1], "latent_image": ["44", 0],
                                                   "seed": seed, "steps": steps, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}}
    g["8"] = {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}}
    g["9"] = {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}}
    return g


def run(prompt, refs, size, seed, steps, out):
    w, h = (int(x) for x in size.lower().split("x"))
    inp = os.path.join(COMFY, "input")
    names = []
    for r in refs:
        n = "kl_" + os.path.basename(r)
        shutil.copy(r, os.path.join(inp, n))
        names.append(n)
    g = graph(prompt, names, w, h, seed, steps, "klein/" + os.path.splitext(os.path.basename(out))[0])
    r = json.loads(post("/prompt", {"prompt": g, "client_id": str(uuid.uuid4())}))
    pid = r["prompt_id"]
    t0 = time.time()
    while True:
        time.sleep(3)
        try:
            hist = get("/history/" + pid)
        except Exception:
            continue
        if hist:
            v = list(hist.values())[0]
            st = v.get("status", {})
            if st.get("status_str") != "success":
                for m in st.get("messages", []):
                    if "error" in str(m[0]):
                        print("  ERROR:", str(m[1].get("exception_message", ""))[:500])
                return False
            im = v["outputs"]["9"]["images"][0]
            src = os.path.join(COMFY, "output", im.get("subfolder", ""), im["filename"])
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            shutil.copy(src, out)
            print("  listo en %.1f s -> %s" % (time.time() - t0, out), flush=True)
            return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prompt"); ap.add_argument("--refs", nargs="*", default=[]); ap.add_argument("-o", "--out")
    ap.add_argument("--size", default="1344x768"); ap.add_argument("--seed", type=int, default=7); ap.add_argument("--steps", type=int, default=16)
    ap.add_argument("--spec")
    a = ap.parse_args()
    try:
        get("/system_stats")
    except Exception:
        sys.exit("ComfyUI 0.41 no responde en %s" % SERVER)
    if a.spec:
        spec = json.load(open(a.spec, encoding="utf-8-sig"))
        for it in spec["items"]:
            out = os.path.join(spec["out_dir"], it["name"] + ".png")
            if os.path.exists(out) and not spec.get("overwrite"):
                print("[%s] ya existe" % it["name"]); continue
            print("[%s]" % it["name"], flush=True)
            run(it["prompt"], it["refs"], it.get("size", a.size), int(it.get("seed", a.seed)), int(it.get("steps", a.steps)), out)
    else:
        run(a.prompt, a.refs, a.size, a.seed, a.steps, a.out)


if __name__ == "__main__":
    main()
