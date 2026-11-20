"""Makes a collected AE project (collect_ae.py) light without touching the .aep: every file keeps its name, duration and frame rate,
so After Effects relinks it as it was.
  - footage with alpha (the host cut-outs, ProRes 4444 12-bit) -> ProRes 4444 10-bit qscale 9 (about 4x lighter, alpha kept);
  - video without alpha -> H.264 CRF 18; the seconds no layer uses (ranges read from the .aep, +-0.5 s) become black, which costs
    almost nothing; a file used through time-remap or stretch keeps all its frames.
  python optimizar_collect.py <collect folder> [<collect folder> ...]      (writes optimizar.json in each)"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, r"D:\motion category ai library\tools\mcp")
import ss_motion_mcp as M  # noqa: E402


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


for d in [Path(x).resolve() for x in sys.argv[1:]]:
    aep = next(d.glob("*.aep")).as_posix()
    r = M.run_jsx(f"""app.beginSuppressDialogs();try{{app.open(new File("{aep}"));var out={{}};
for(var i=1;i<=app.project.numItems;i++){{var c=app.project.item(i);if(!(c instanceof CompItem))continue;
 for(var l=1;l<=c.numLayers;l++){{var L=c.layer(l);if(!(L.source instanceof FootageItem)||!L.source.file)continue;var s=L.source,k=decodeURI(s.file.name);
  if(!out[k])out[k]={{alpha:s.mainSource.hasAlpha,still:s.mainSource.isStill,dur:s.duration,rangos:[],todo:false}};
  if(L.timeRemapEnabled||Math.abs(L.stretch-100)>0.01){{out[k].todo=true;continue;}}
  out[k].rangos.push([Math.max(0,L.inPoint-L.startTime),Math.min(s.duration,L.outPoint-L.startTime)]);}}}}
app.newProject();return JSON.stringify(out);}}finally{{app.endSuppressDialogs(false);}}""", timeout=300)
    U = json.loads(r[r.index("{"):r.rindex("}") + 1])
    fd = d / "(Footage)"; log = []
    for nom, u in U.items():
        f = fd / nom
        if not f.exists() or u["still"] or f.suffix.lower() in (".wav", ".mp3", ".aif", ".png", ".jpg"):
            continue
        antes = f.stat().st_size; tmp = f.with_name("_tmp_" + f.name); d0 = dur(f)
        if u["alpha"]:
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(f), "-map", "0:v", "-c:v", "prores_ks", "-profile:v", "4", "-qscale:v", "9",
                   "-pix_fmt", "yuva444p10le", "-vendor", "apl0", "-fps_mode", "passthrough", str(tmp.with_suffix(".mov"))]
            tmp = tmp.with_suffix(".mov")
        else:
            rg = sorted([max(0, a - 0.5), min(d0, b + 0.5)] for a, b in u["rangos"])
            junt = []
            for a, b in rg:
                if junt and a <= junt[-1][1]:
                    junt[-1][1] = max(junt[-1][1], b)
                else:
                    junt.append([a, b])
            vf = []
            if not u["todo"] and junt:
                usa = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in junt)
                vf = ["-vf", f"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='not({usa})'"]
            tiene_audio = bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(f)],
                                              capture_output=True, text=True).stdout.strip())
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(f)] + vf + ["-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                   "-fps_mode", "passthrough"] + (["-c:a", "aac", "-b:a", "160k"] if tiene_audio else ["-an"]) + [str(tmp.with_suffix(f.suffix if f.suffix.lower() in (".mp4", ".mov") else ".mp4"))]
            tmp = tmp.with_suffix(f.suffix if f.suffix.lower() in (".mp4", ".mov") else ".mp4")
        subprocess.run(cmd, check=True)
        d1 = dur(tmp)
        if abs(d1 - d0) > 0.1 or tmp.stat().st_size >= antes:
            log.append({"file": nom, "kept": True, "why": f"dur {d0:.2f}->{d1:.2f}" if abs(d1 - d0) > 0.1 else "not smaller"}); tmp.unlink(); continue
        tmp.replace(f)
        log.append({"file": nom, "mb": [round(antes / 1e6), round(f.stat().st_size / 1e6)], "black_outside": None if u["alpha"] or u["todo"] else len(junt)})
        print(d.name, nom, log[-1]["mb"], flush=True)
    (d / "optimizar.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
