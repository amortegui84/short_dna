"""After Effects "Collect Files" for a project, done by script: opens <project>/ae/<slug>.aep, copies every footage file it uses
into <dest>/<slug>/(Footage)/, relinks each item to its copy, saves <dest>/<slug>/<slug>.aep and writes a report. The original
.aep and media are not touched (the collected project is a new file). AE stays open.
Usage: python collect_ae.py <dest folder> <project> [<project> ...]"""
import json, sys
from pathlib import Path

sys.path.insert(0, r"D:\motion category ai library\tools\mcp")
import ss_motion_mcp as M  # noqa: E402

dest = Path(sys.argv[1]).resolve()
for proj in sys.argv[2:]:
    carpeta = Path(proj).resolve(); slug = carpeta.name
    aep = (carpeta / "ae" / f"{slug}.aep").as_posix()
    out = (dest / slug).as_posix()
    jsx = f"""app.beginSuppressDialogs();
try {{
var f = new File("{aep}");
if (app.project.dirty && app.project.file) app.project.save();
app.open(f);
var D = new Folder("{out}"); D.create(); var FD = new Folder("{out}/(Footage)"); FD.create();
var usados = {{}}, n = 0, faltan = [], bytes = 0;
for (var i = 1; i <= app.project.numItems; i++) {{
    var it = app.project.item(i);
    if (!(it instanceof FootageItem) || !it.file) continue;
    var src = it.file;
    if (!src.exists) {{ faltan.push(src.fsName); continue; }}
    var nom = src.name, k = 1;
    while (usados[nom.toLowerCase()] && usados[nom.toLowerCase()] !== src.fsName) {{ nom = k + "_" + src.name; k++; }}
    usados[nom.toLowerCase()] = src.fsName;
    var dst = new File(FD.fsName + "/" + nom);
    if (!dst.exists) {{ if (!src.copy(dst.fsName)) {{ faltan.push("copy failed " + src.fsName); continue; }} }}
    bytes += dst.length;
    it.replace(dst); n++;
}}
app.project.save(new File("{out}/{slug}.aep"));
return JSON.stringify({{copiados: n, mb: Math.round(bytes / 1048576), faltan: faltan, aep: app.project.file.fsName}});
}} finally {{ app.endSuppressDialogs(false); }}"""
    r = M.run_jsx(jsx, timeout=1800)
    print(slug, r, flush=True)
