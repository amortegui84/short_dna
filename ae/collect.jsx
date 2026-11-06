// Scriptable "Collect Files": saves the open project as <dest>/ae/<name>.aep, removes unused footage, copies every footage file
// to <dest>/media/<its original path without the drive letter> (never flattened: many videos share names like L03.mov),
// relinks the footage to the copies and saves again. A file that already exists at the destination is not copied, only
// relinked (engine/collect.py puts light mattes there first).
// Usage (run_jsx): $.evalFile(".../ae/collect.jsx"); return COLLECT_FILES("D:/out/collect", "NAME");
// After it runs, the open project IS the collected copy.
function COLLECT_FILES(dest, nombre) {
    var out = new Folder(dest), n = 0, bytes = 0, fallos = [], hecho = {};
    function mk(p) { var f = new Folder(p); if (!f.exists) { mk(f.parent.fsName); f.create(); } }
    mk(out.fsName + "/ae");
    try { app.project.removeUnusedFootage(); } catch (e) {}
    var aep = new File(out.fsName + "/ae/" + nombre + ".aep"); app.project.save(aep);
    for (var i = 1; i <= app.project.numItems; i++) {
        var it = app.project.item(i); if (!(it instanceof FootageItem) || !it.file) continue;
        if (!it.file.exists) { fallos.push("missing " + it.file.fsName); continue; }
        var src = it.file.fsName, rel = "media/" + src.replace(/^[A-Za-z]:[\\\/]+/, "").replace(/^[\\\/]+/, "");
        var dst = new File(out.fsName + "/" + rel.replace(/\\/g, "/"));
        if (!hecho[src]) { mk(dst.parent.fsName); if (!dst.exists && !it.file.copy(dst.fsName)) { fallos.push("not copied " + src); continue; } hecho[src] = 1; n++; if (dst.exists) bytes += dst.length; }
        try { it.replace(dst); } catch (e2) { fallos.push(src + " (" + e2.toString() + ")"); }
    }
    app.project.save(aep);
    var fuera = 0; for (i = 1; i <= app.project.numItems; i++) { it = app.project.item(i); if (it instanceof FootageItem && it.file && (!it.file.exists || it.file.fsName.indexOf(out.fsName) !== 0)) fuera++; }
    return "collected " + n + " files, " + Math.round(bytes / 1e6) + " MB in " + out.fsName + " | outside or missing: " + fuera + (fallos.length ? "\nFAILED:\n" + fallos.join("\n") : "");
}
