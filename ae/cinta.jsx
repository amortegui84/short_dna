// CINTA: the "Night Transmission" format (found-footage tape). Builds the edit from the same data as COLLAGE (datos_ae.json)
// but with its own look: the narrator whole in his room, evidence on a CRT inset, mono type, one red, hard cuts behind
// tracking glitches, a viewfinder HUD and the self-destruct ending. Called by engine/build_collage.py when the style has
// "builder": "cinta". Returns "ok N layers" and one "CUE;t;sfx;gain;why" line per sound cue.
// Rule for this file: comments always on their own line (a comment after code once swallowed the code that followed it).
var CINTA = (function () {
    var c, D, W = 1080, H = 1920, FPS = 30, DUR, fold, cache = {}, CUES = [];
    var BG = "#05080B", PH = "#D9F2E6", DIM = "#7F9A8E", RED = "#E0263C";
    var F_TIT = "Unispace-Bold", F_MONO = "CascadiaMonoRoman-Bold", F_FINO = "CascadiaMonoRoman-SemiLight";

    function rgb(h) { h = h.replace("#", ""); return [parseInt(h.substr(0, 2), 16) / 255, parseInt(h.substr(2, 2), 16) / 255, parseInt(h.substr(4, 2), 16) / 255]; }
    function imp(p) {
        if (!p) return null;
        if (cache[p] !== undefined) return cache[p];
        var f = new File(p);
        if (!f.exists) { cache[p] = null; return null; }
        var it = app.project.importFile(new ImportOptions(f)); it.parentFolder = fold; cache[p] = it; return it;
    }
    function T(L) { return L.property("ADBE Transform Group"); }
    function O(L) { return T(L).property("ADBE Opacity"); }
    function P(L) { return T(L).property("ADBE Position"); }
    function S(L) { return T(L).property("ADBE Scale"); }
    function A(L) { return T(L).property("ADBE Anchor Point"); }
    function fx(L, m) { return L.property("ADBE Effect Parade").addProperty(m); }
    function vida(L, a, b) { L.inPoint = Math.max(0, a); L.outPoint = Math.min(DUR, b); return L; }
    function cue(t, sfx, gain, why) { if (t >= 0 && t < DUR) CUES.push("CUE;" + t.toFixed(3) + ";" + sfx + ";" + gain + ";" + why); }
    function shp(n) { var L = c.layers.addShape(); L.name = n; return L; }
    function grp(L, n) { var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); g.name = n; return g.property("ADBE Vectors Group"); }
    function rect(g, w, h) { var r = g.addProperty("ADBE Vector Shape - Rect"); r.property("ADBE Vector Rect Size").setValue([w, h]); return r; }
    function linea(g, pts) { var p = g.addProperty("ADBE Vector Shape - Group"), s = new Shape(); s.vertices = pts; s.closed = false; p.property("ADBE Vector Shape").setValue(s); return p; }
    function fill(g, col, op) { var f = g.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(rgb(col)); if (op !== undefined) f.property("ADBE Vector Fill Opacity").setValue(op); return f; }
    function stroke(g, col, w) { var s = g.addProperty("ADBE Vector Graphic - Stroke"); s.property("ADBE Vector Stroke Color").setValue(rgb(col)); s.property("ADBE Vector Stroke Width").setValue(w); s.property("ADBE Vector Stroke Line Cap").setValue(1); return s; }
    function trim(g) { return g.addProperty("ADBE Vector Filter - Trim"); }
    function caja(n, x, y, w, h, col, op) { var L = shp(n), g = grp(L, "r"); rect(g, w, h); fill(g, col, op); P(L).setValue([x, y]); return L; }
    function marco(n, x, y, w, h, col, sw) { var L = shp(n), g = grp(L, "r"); rect(g, w, h); stroke(g, col, sw); P(L).setValue([x, y]); return L; }
    function texto(s, font, size, col, just, track) {
        var L = c.layers.addText(s), p = L.property("ADBE Text Properties").property("ADBE Text Document"), d = p.value;
        d.resetCharStyle(); d.font = font; d.fontSize = size; d.applyFill = true; d.fillColor = rgb(col); d.applyStroke = false;
        d.justification = just || ParagraphJustification.LEFT_JUSTIFY; d.tracking = track || 0; p.setValue(d); return L;
    }
    // anchor at the text's left edge, vertical centre (left texts) or at its centre (centred texts)
    function anclar(L, centro) { var r = L.sourceRectAtTime(0, false); A(L).setValue([centro ? r.left + r.width / 2 : r.left, r.top + r.height / 2]); return r; }
    // typed on: characters appear from a to a+dur
    function teclear(L, a, dur, base) {
        var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
        an.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(base || 0);
        an.property("ADBE Text Selectors").addProperty("ADBE Text Selector").property("ADBE Text Percent Start").expression = "linear(time," + a.toFixed(3) + "," + (a + dur).toFixed(3) + ",0,100);";
    }
    // given words (0-based) turn red
    function rojas(L, idx) {
        if (!idx.length) return;
        var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
        an.property("ADBE Text Animator Properties").addProperty("ADBE Text Fill Color").setValue(rgb(RED));
        var sl = an.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sl.property("ADBE Text Range Type2").setValue(3);
        sl.property("ADBE Text Expressible Amount").expression = "var K=[" + idx.join(",") + "]; var r=0; for (var i=0;i<K.length;i++) if (textIndex-1==K[i]) r=100; r;";
    }
    function limpia(w) { return w.toLowerCase().replace(/[^a-z0-9']/g, ""); }
    function esClave(w) { var k = D.claves || [], x = limpia(w); for (var i = 0; i < k.length; i++) if (x && x === limpia(k[i])) return true; return false; }
    // never ping-pong (review 2026-11-06: the narrator rewinding looked broken): engine/continuar.py generates new footage for a long
    // section; if a clip is still short, it holds on its last frame
    function ping(L) { L.timeRemapEnabled = true; L.property("ADBE Time Remapping").expression = "Math.min(Math.max(0, time - thisLayer.startTime), source.duration - 0.05);"; return L; }
    // ambient layers (the faint smoke) loop forward, never backward
    function bucle(L) { L.timeRemapEnabled = true; L.property("ADBE Time Remapping").expression = "Math.max(0, time - thisLayer.startTime) % (source.duration - 0.05);"; return L; }
    function partir(s, n) {
        var ws = s.split(/\s+/), out = [], cur = "";
        for (var i = 0; i < ws.length; i++) { if (cur && (cur + " " + ws[i]).length > n) { out.push(cur); cur = ws[i]; } else cur = cur ? cur + " " + ws[i] : ws[i]; }
        if (cur) out.push(cur); return out;
    }
    function ajustar(L, maxW) { var r = L.sourceRectAtTime(0, false); if (r.width > maxW) { var k = maxW / r.width * 100; S(L).setValue([k, k]); } return L; }

    // ---------------- pieces
    // tracking glitch that hides a hard cut at t: the picture rolls, the colour splits and a static burst flashes (5 frames)
    function glitch(t, why) {
        var a = Math.max(0, t - 0.07), b = Math.min(DUR, t + 0.13);
        var ad = c.layers.addSolid([0, 0, 0], "glitch " + why, W, H, 1, DUR); ad.adjustmentLayer = true; vida(ad, a, b);
        var of = fx(ad, "ADBE Offset"); of.property(1).expression = "posterizeTime(30); seedRandom(" + Math.round(t * 100) + ",false); [540+random(-60,60), 960+random(-420,420)];";
        try { var cs = fx(ad, "ADBE Channel Blur"); cs.property(1).setValue(40); cs.property(3).setValue(30); cs.property(5).setValue(2); } catch (e) {}
        var st = imp(D.fx_estatica) || imp(D.estatica);
        if (st) { var L = c.layers.add(st); L.name = "static burst"; S(L).setValue([W / st.width * 104, H / st.height * 104]); P(L).setValue([W / 2, H / 2]); L.blendingMode = BlendingMode.SCREEN; L.audioEnabled = false;
            O(L).expression = "posterizeTime(30); 30+random(45);"; if (st.duration > 0.5) L.startTime = a - (t * 7.3) % Math.max(0.1, st.duration - 0.5); vida(L, a, b); }
        cue(a, "glitch", -6, why);
    }
    function narrador(sec) {
        var clip = sec.clip || (sec.mate || "").replace("/mates/", "/clips/").replace(/\.mov$/, ".mp4"), it = imp(clip);
        if (!it) return null;
        var L = c.layers.add(it); L.name = "NARRADOR " + sec.id; L.audioEnabled = false; L.startTime = sec.ini; ping(L);
        var k = Math.max(W / it.width, H / it.height) * 100 * 1.02;
        S(L).setValueAtTime(sec.ini, [k, k]); S(L).setValueAtTime(sec.fin, [k * 1.08, k * 1.08]);
        P(L).setValue([W / 2, H / 2]); P(L).expression = "value + [wiggle(0.6,7)[0]-value[0], wiggle(0.5,5)[1]-value[1]];";
        vida(L, sec.ini, sec.fin);
        // smoke drifting in the room (MiniMax fx clip on black, Screen)
        var hu = imp(D.fx_humo);
        if (hu) { var Hm = c.layers.add(hu); Hm.name = "smoke " + sec.id; Hm.audioEnabled = false; Hm.startTime = sec.ini; bucle(Hm); var kh = Math.max(W / hu.width, H / hu.height) * 100; S(Hm).setValue([kh, kh]); P(Hm).setValue([W / 2, H / 2]); Hm.blendingMode = BlendingMode.SCREEN; O(Hm).setValue(22); vida(Hm, sec.ini, sec.fin); }
        return L;
    }
    // evidence on the CRT inset
    var SX = 540, SY = 690, SW = 900, SH = 1020, nEv = 0;
    function evidencia(img, t0, t1, stem, conFondo) {
        var it = imp(img); if (!it) return null; nEv++;
        if (conFondo) { vida(caja("CRT fondo", W / 2, H / 2, W, H, BG, 100), t0, t1); paralaje(t0, t1, 3 + nEv); }
        var hum = caja("CRT glow", SX, SY, SW + 60, SH + 60, PH, 6); vida(hum, t0, t1);
        try { fx(hum, "ADBE Gaussian Blur 2").property(1).setValue(40); } catch (e) {}
        var bk = caja("CRT negro", SX, SY, SW, SH, "#000000", 100); vida(bk, t0, t1);
        var L = c.layers.add(it); L.name = "EVIDENCE " + nEv + " " + (stem || ""); L.audioEnabled = false;
        var marcas = D.marcas_docs && stem ? D.marcas_docs[stem] : null;
        var k = Math.max(SW / it.width, SH / it.height) * 100;
        P(L).setValue([SX, SY]);
        if (marcas && marcas.length) {
            // documents: push to the first marked line (anchor travels to it while the scale grows)
            var m = marcas[0].rect, mx = (m[0] + m[2]) / 2 * it.width, my = (m[1] + m[3]) / 2 * it.height;
            A(L).setValueAtTime(t0 + 0.3, [it.width / 2, it.height / 2]); A(L).setValueAtTime(Math.min(t1, t0 + 2.2), [it.width / 2 + (mx - it.width / 2) * 0.8, it.height / 2 + (my - it.height / 2) * 0.8]);
            S(L).setValueAtTime(t0 + 0.3, [k, k]); S(L).setValueAtTime(Math.min(t1, t0 + 2.2), [k * 1.2, k * 1.2]);
            for (var i = 0; i < marcas.length; i++) {
                var mk = marcas[i], r = mk.rect, ti = t0 + (mk.t || (1.0 + i * 1.0));
                if (ti > t1 - 0.4) break;
                var x0 = r[0] * it.width, y0 = r[1] * it.height, x1 = r[2] * it.width, y1 = r[3] * it.height;
                var bx = shp("red bracket " + i), g = grp(bx, "b"), hw = (x1 - x0) / 2 + 14, hh = Math.max(14, (y1 - y0) / 2 + 10);
                linea(g, [[-hw + 30, -hh], [-hw, -hh], [-hw, hh], [-hw + 30, hh]]); stroke(g, RED, 5);
                var g2 = grp(bx, "b2"); linea(g2, [[hw - 30, -hh], [hw, -hh], [hw, hh], [hw - 30, hh]]); stroke(g2, RED, 5);
                var g3 = grp(bx, "f"); rect(g3, hw * 2, hh * 2); fill(g3, RED, 18);
                bx.parent = L; P(bx).setValue([(x0 + x1) / 2, (y0 + y1) / 2]); S(bx).setValue([100, 100]);
                O(bx).expression = "posterizeTime(15); time<" + (ti + 0.25).toFixed(2) + "?(random()>0.5?100:0):100;"; vida(bx, ti, t1);
                cue(ti, "click", -8, "bracket");
                if (mk.nota) {
                    var nt = texto(("> " + mk.nota).toUpperCase(), F_MONO, 34, "#FFFFFF"); anclar(nt, false);
                    var rn = nt.sourceRectAtTime(0, false), tg = caja("note tag", 0, 0, rn.width + 28, rn.height + 20, RED, 100);
                    var ny = Math.max(SY - SH / 2 + 120, Math.min(SY + SH / 2 - 80, SY + 140 + i * 90)), nx = SX - SW / 2 + 40;
                    nt.moveBefore(tg); P(tg).setValue([nx + (rn.width + 28) / 2, ny]); P(nt).setValue([nx + 14, ny]); teclear(nt, ti + 0.3, 0.5);
                    O(tg).setValueAtTime(ti + 0.25, 0); O(tg).setValueAtTime(ti + 0.3, 100); vida(tg, ti + 0.25, t1); vida(nt, ti + 0.25, t1);
                }
            }
        } else {
            S(L).setValueAtTime(t0, [k * 1.02, k * 1.02]); S(L).setValueAtTime(t1, [k * 1.12, k * 1.12]);
        }
        vida(L, t0, t1);
        try { var oc = fx(L, "ADBE Optics Compensation"); oc.property(1).setValue(28); oc.property(3).setValue(1); } catch (e) {}
        var mt = caja("CRT mask", SX, SY, SW, SH, "#FFFFFF", 100); mt.moveBefore(L); vida(mt, t0, t1);
        try { L.setTrackMatte(mt, TrackMatteType.ALPHA); } catch (e) { mt.enabled = false; }
        // CRT phosphor line pattern and frame
        var sl = shp("CRT lines"); for (var j = 0; j < 51; j++) { var gl = grp(sl, "l" + j); var rr = rect(gl, SW, 3); rr.property("ADBE Vector Rect Position").setValue([0, -SH / 2 + j * 20 + 10]); fill(gl, "#000000"); }
        P(sl).setValue([SX, SY]); O(sl).setValue(14); vida(sl, t0, t1);
        vida(marco("CRT frame", SX, SY, SW, SH, PH, 3), t0, t1);
        var et = texto("EVIDENCE " + (nEv < 10 ? "0" : "") + nEv, F_MONO, 30, "#FFFFFF", null, 60); anclar(et, false);
        var re = et.sourceRectAtTime(0, false), tg2 = caja("EVIDENCE tag", 0, 0, re.width + 30, re.height + 18, RED, 100); et.moveBefore(tg2);
        P(tg2).setValue([SX - SW / 2 + 24 + (re.width + 30) / 2, SY - SH / 2 + 40]); P(et).setValue([SX - SW / 2 + 39, SY - SH / 2 + 40]); vida(tg2, t0, t1); vida(et, t0, t1);
        var ti2 = (D.titulos && stem && D.titulos[stem]) || null;
        if (ti2) {
            var tt = texto(String(ti2[0]).toUpperCase(), F_TIT, 46, PH); anclar(tt, false); ajustar(tt, SW); P(tt).setValue([SX - SW / 2, SY + SH / 2 + 50]); teclear(tt, t0 + 0.15, 0.6); vida(tt, t0, t1);
            if (ti2[1]) { var tf = texto(String(ti2[1]), F_FINO, 30, DIM); anclar(tf, false); ajustar(tf, SW); P(tf).setValue([SX - SW / 2, SY + SH / 2 + 100]); teclear(tf, t0 + 0.6, 0.5); vida(tf, t0, t1); }
            cue(t0 + 0.15, "type", -12, "evidence title");
        }
        return L;
    }
    // parallax textures over a black plate: three depths drifting up at different speeds (fog far, CRT grid mid,
    // tape dust near and soft) plus one shared sway scaled by depth, so the black reads as a deep room, not a flat card.
    // k varies the seed and sway phase per section.
    function paralaje(t0, t1, k) {
        var ph = (k * 1.7).toFixed(2);
        // far: slow phosphor fog
        var f = c.layers.addSolid([0, 0, 0], "parallax fog", W, H, 1, DUR); vida(f, t0, t1);
        try {
            var fn = fx(f, "ADBE Fractal Noise"); fn.property("Contrast").setValue(160); fn.property("Brightness").setValue(-42);
            fn.property("Uniform Scaling").setValue(0); fn.property("Scale Width").setValue(900); fn.property("Scale Height").setValue(520); fn.property("Complexity").setValue(4);
            fn.property("Offset Turbulence").expression = "[540+Math.sin(time*0.5+" + ph + ")*30, 960+time*22+" + (k * 300) + "];";
            fn.property("Evolution").expression = "time*18;";
            var tn = fx(f, "ADBE Tint"); tn.property(1).setValue(rgb(BG)); tn.property(2).setValue(rgb(DIM));
        } catch (e) {}
        f.blendingMode = BlendingMode.SCREEN; O(f).setValue(k === 1 ? 12 : 20);
        // mid: CRT measuring grid with + marks, wraps every cell
        var cell = 135, gd = shp("parallax grid"), gg = grp(gd, "g");
        for (var x = -W / 2; x <= W / 2; x += cell) linea(gg, [[x, -H / 2 - cell], [x, H / 2 + cell]]);
        for (var y = -H / 2 - cell; y <= H / 2 + cell; y += cell) linea(gg, [[-W / 2, y], [W / 2, y]]);
        stroke(gg, DIM, 1);
        var gp = grp(gd, "p");
        for (x = -W / 2 + cell; x < W / 2; x += cell * 2) for (y = -H / 2 - cell; y <= H / 2 + cell; y += cell * 2) { linea(gp, [[x - 9, y], [x + 9, y]]); linea(gp, [[x, y - 9], [x, y + 9]]); }
        stroke(gp, PH, 2);
        P(gd).setValue([W / 2, H / 2]); P(gd).expression = "[540+Math.sin(time*0.5+" + ph + ")*14, 960-(time*45)%" + cell + "];"; O(gd).setValue(6); gd.blendingMode = BlendingMode.ADD; vida(gd, t0, t1);
        // near: tape dust, two stacked copies so the drift wraps seamlessly, slightly out of focus
        var du = shp("parallax dust"), dg = grp(du, "d"), s = 7919 + k * 104729;
        function rnd() { s = (s * 16807) % 2147483647; return s / 2147483647; }
        for (var i = 0; i < 46; i++) {
            var px = (rnd() - 0.5) * W, py = (rnd() - 0.5) * H, sz = 2 + rnd() * 5;
            for (var cp = 0; cp < 2; cp++) { var e = dg.addProperty("ADBE Vector Shape - Ellipse"); e.property("ADBE Vector Ellipse Size").setValue([sz, sz]); e.property("ADBE Vector Ellipse Position").setValue([px, py + cp * H]); }
        }
        fill(dg, PH, 100);
        P(du).setValue([W / 2, H / 2]); P(du).expression = "[540+Math.sin(time*0.5+" + ph + ")*40, 960-(time*120+" + (k * 400) + ")%" + H + "];";
        O(du).expression = "posterizeTime(12); 22+random(10);"; du.blendingMode = BlendingMode.ADD; vida(du, t0, t1);
        try { fx(du, "ADBE Box Blur2").property(1).setValue(2); } catch (e2) {}
    }
    function casoTitulo(sec) {
        var t0 = sec.ini, t1 = sec.fin;
        vida(caja("case black", W / 2, H / 2, W, H, BG, 100), t0, t1); paralaje(t0, t1, 1);
        var bgI = imp(sec.img);
        if (bgI) { var B = c.layers.add(bgI); B.name = "case doc faint"; var k = Math.max(W / bgI.width, H / bgI.height) * 100; S(B).setValueAtTime(t0, [k, k]); S(B).setValueAtTime(t1, [k * 1.06, k * 1.06]); P(B).setValue([W / 2, H / 2]); O(B).setValue(24); try { fx(B, "ADBE Gaussian Blur 2").property(1).setValue(6); } catch (e) {} vida(B, t0, t1); }
        var x = 110, y = 520;
        var dot = caja("case dot", x + 14, y, 28, 28, RED, 100); vida(dot, t0, t1); O(dot).expression = "posterizeTime(4); Math.floor(time*2)%2?100:0;";
        var cf = texto("CASE FILE " + D.numero, F_MONO, 40, RED, null, 120); anclar(cf, false); P(cf).setValue([x + 50, y]); teclear(cf, t0 + 0.05, 0.3); vida(cf, t0, t1);
        var lineas = partir(String(D.artista).toUpperCase(), 13), yy = y + 140;
        for (var i = 0; i < lineas.length; i++) { var L = texto(lineas[i], F_TIT, 104, PH); anclar(L, false); ajustar(L, 860); P(L).setValue([x, yy]); teclear(L, t0 + 0.1 + i * 0.25, 0.45, 18); vida(L, t0, t1); yy += 118; }
        var ru = shp("case rule"), gr = grp(ru, "r"); linea(gr, [[0, 0], [860, 0]]); stroke(gr, PH, 3); var tr = trim(gr); tr.property("ADBE Vector Trim End").setValueAtTime(t0 + 0.5, 0); tr.property("ADBE Vector Trim End").setValueAtTime(t0 + 0.9, 100);
        P(ru).setValue([x, yy - 20]); vida(ru, t0, t1);
        var fe = texto(String(D.fechas), F_MONO, 40, DIM); anclar(fe, false); ajustar(fe, 860); P(fe).setValue([x, yy + 40]); teclear(fe, t0 + 0.7, 0.4); vida(fe, t0, t1);
        var le = partir(String(D.lema), 30);
        for (i = 0; i < le.length; i++) { var Ll = texto(le[i], F_FINO, 40, PH); anclar(Ll, false); P(Ll).setValue([x, yy + 120 + i * 54]); teclear(Ll, t0 + 0.9 + i * 0.2, 0.5); vida(Ll, t0, t1); }
        cue(t0 + 0.05, "type", -10, "case file");
    }
    function teletexto(sec) {
        var t0 = sec.ini, t1 = sec.fin;
        vida(caja("quote black", W / 2, H / 2, W, H, BG, 100), t0, t1); paralaje(t0, t1, 2);
        var st = imp(D.estatica);
        if (st) { var Sx = c.layers.add(st); S(Sx).setValue([W / st.width * 104, H / st.height * 104]); P(Sx).setValue([W / 2, H / 2]); Sx.blendingMode = BlendingMode.SCREEN; O(Sx).expression = "posterizeTime(12); 8+random(6);"; vida(Sx, t0, t1); }
        var ws = sec.cita.join(" ").replace(/[“”"]/g, "").split(/\s+/), pw = sec.palabras || [], TW = [];
        for (var i = 0; i < ws.length; i++) TW.push(pw.length === ws.length ? pw[i][1] : t0 + 0.2 + i * 0.3);
        var lin = partir(ws.join(" ").toUpperCase(), 11), x = 130, lh = 112, y0 = 960 - lin.length * lh / 2, n = 0, clave = limpia(sec.clave || "");
        var bar = caja("quote bar", 82, 960, 12, lin.length * lh + 40, RED, 100); S(bar).setValueAtTime(t0, [100, 40]); S(bar).setValueAtTime(t0 + 0.3, [100, 100]); vida(bar, t0, t1);
        for (i = 0; i < lin.length; i++) {
            var L = texto(lin[i], F_TIT, 92, PH); anclar(L, false); ajustar(L, 860); P(L).setValue([x, y0 + i * lh + lh / 2]); vida(L, t0, t1);
            var lw = lin[i].split(" "), St = [], K = [];
            for (var j = 0; j < lw.length; j++) { St.push(TW[n + j].toFixed(3)); if (clave && limpia(lw[j]) === clave) K.push(j); }
            // teletext: every word is there dimmed from the cut (no near-black frame) and lights up when it is said
            var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"); an.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(16);
            var sl = an.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sl.property("ADBE Text Range Type2").setValue(3);
            sl.property("ADBE Text Expressible Amount").expression = "var S=[" + St.join(",") + "]; time<S[textIndex-1]?100:0;";
            rojas(L, K);
            if (K.length) { var r = L.sourceRectAtTime(0, false); var kt = TW[n + K[0]]; var ul = caja("quote key block", x + r.width / 2, y0 + i * lh + lh - 6, r.width, 10, RED, 100); S(ul).setValueAtTime(kt, [0, 100]); S(ul).setValueAtTime(kt + 0.25, [100, 100]); vida(ul, kt, t1); cue(kt, "hit", -10, "key word"); }
            n += lw.length;
        }
        var au = texto(String(sec.autor || "").replace(/^[—\-\s]+/, "").toUpperCase(), F_FINO, 30, DIM); anclar(au, false); ajustar(au, 860); P(au).setValue([x, y0 + lin.length * lh + 50]);
        var ta = TW[TW.length - 1] + 0.25; teclear(au, ta, 0.6); vida(au, ta, t1);
        cue(t0, "type", -11, "teletext");
    }
    function subtitulos() {
        var y = (D.estilo && D.estilo.formato && D.estilo.formato.y_subtitulos) || 1430;
        for (var i = 0; i < D.subs.length; i++) {
            var s = D.subs[i], ws = [], K = [];
            for (var j = 0; j < s.words.length; j++) { ws.push(s.words[j].w.toUpperCase()); if (esClave(s.words[j].w)) K.push(j); }
            var L = texto(ws.join(" "), F_MONO, 52, PH, ParagraphJustification.CENTER_JUSTIFY); L.name = "caption " + (i + 1); anclar(L, true); ajustar(L, 900); P(L).setValue([W / 2, y]);
            var sh = fx(L, "ADBE Drop Shadow"); sh.property("Opacity").setValue(230); sh.property("Distance").setValue(3); sh.property("Softness").setValue(10);
            teclear(L, s.ini, Math.min(0.25, (s.fin - s.ini) * 0.5)); rojas(L, K); vida(L, s.ini, s.fin);
        }
    }
    function hud() {
        var g, L = shp("HUD brackets"), m = 56, top = 96, bot = H - 96, len = 70;
        var esq = [[m, top, 1, 1], [W - m, top, -1, 1], [m, bot, 1, -1], [W - m, bot, -1, -1]];
        for (var i = 0; i < 4; i++) { var e = esq[i]; g = grp(L, "c" + i); linea(g, [[e[0], e[1] + e[3] * len], [e[0], e[1]], [e[0] + e[2] * len, e[1]]]); stroke(g, PH, 4); }
        P(L).setValue([0, 0]); O(L).setValue(70);
        var dot = shp("REC dot"); g = grp(dot, "d"); var el = g.addProperty("ADBE Vector Shape - Ellipse"); el.property("ADBE Vector Ellipse Size").setValue([24, 24]); fill(g, RED);
        P(dot).setValue([m + 44, top + 44]); O(dot).expression = "Math.floor(time*1.6)%2?100:15;";
        var rec = texto("REC", F_MONO, 32, PH, null, 80); anclar(rec, false); P(rec).setValue([m + 70, top + 44]);
        var tc = texto("00:00:00:00", F_MONO, 32, PH, ParagraphJustification.RIGHT_JUSTIFY); var rt = tc.sourceRectAtTime(0, false); A(tc).setValue([rt.left + rt.width, rt.top + rt.height / 2]); P(tc).setValue([W - m - 30, top + 44]);
        tc.property("ADBE Text Properties").property("ADBE Text Document").expression = "var f=Math.floor(time*30), s=Math.floor(f/30); function p(n){return ('0'+n).slice(-2);} '00:'+p(Math.floor(s/60))+':'+p(s%60)+':'+p(f%30);";
        var tp = texto("TAPE " + D.numero + "  SP", F_MONO, 28, DIM, null, 60); anclar(tp, false); P(tp).setValue([m + 30, bot - 40]);
        if (D.handle) { var hd = texto(D.handle, F_MONO, 28, DIM, ParagraphJustification.RIGHT_JUSTIFY); var rh = hd.sourceRectAtTime(0, false); A(hd).setValue([rh.left + rh.width, rh.top + rh.height / 2]); P(hd).setValue([W - m - 30, bot - 40]); }
    }
    function vhs() {
        var ad = c.layers.addSolid([0, 0, 0], "VHS grade", W, H, 1, DUR); ad.adjustmentLayer = true;
        try { var ch = fx(ad, "ADBE Channel Blur"); ch.property(1).setValue(6); ch.property(3).setValue(4); ch.property(5).setValue(2); } catch (e) {}
        try { var tn = fx(ad, "ADBE Tint"); tn.property(1).setValue(rgb(BG)); tn.property(2).setValue(rgb(PH)); tn.property(3).setValue(28); } catch (e) {}
        try { var nz = fx(ad, "ADBE Noise"); nz.property(1).setValue(7); } catch (e) {}
        var sl = shp("VHS scanlines"); for (var i = 0; i < 64; i++) { var g = grp(sl, "l" + i); var r = rect(g, W, 2); r.property("ADBE Vector Rect Position").setValue([0, -H / 2 + i * 30 + 15]); fill(g, "#000000"); }
        P(sl).setValue([W / 2, H / 2]); P(sl).expression = "value+[0,(time*90)%30];"; O(sl).setValue(18); sl.blendingMode = BlendingMode.MULTIPLY;
        var tb = c.layers.addSolid([0.5, 0.5, 0.5], "VHS tracking", W, 60, 1, DUR), fn = fx(tb, "ADBE Fractal Noise");
        fn.property("Contrast").setValue(260); fn.property("Uniform Scaling").setValue(0); fn.property("Scale Width").setValue(900); fn.property("Scale Height").setValue(10); fn.property("Evolution").expression = "time*1400;";
        tb.blendingMode = BlendingMode.SCREEN; P(tb).expression = "var p=(time%9.1)/1.4; [540, p<1? -60+p*(1920+120) : -200];"; O(tb).expression = "posterizeTime(12); 20+random(16);";
        var vg = c.layers.addSolid([0, 0, 0], "VHS vignette", W, H, 1, DUR), mk = vg.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"), sh = new Shape(), K = 0.5523, hw = W * 0.64, hh = H * 0.6;
        sh.vertices = [[540, 960 - hh], [540 + hw, 960], [540, 960 + hh], [540 - hw, 960]]; sh.inTangents = [[-hw * K, 0], [0, -hh * K], [hw * K, 0], [0, hh * K]]; sh.outTangents = [[hw * K, 0], [0, hh * K], [-hw * K, 0], [0, -hh * K]]; sh.closed = true;
        mk.property("ADBE Mask Shape").setValue(sh); mk.inverted = true; mk.property("ADBE Mask Feather").setValue([360, 360]); O(vg).setValue(60);
    }
    // the signature ending: the narrator self-destructs (type per episode), then END OF TAPE over static
    function autodestruir(L, tipo) {
        var t0 = DUR - 1.8, t1 = DUR - 0.35, op = O(L);
        if (L.outPoint < DUR) L.outPoint = DUR;
        try {
            if (tipo === "static_dissolve" || tipo === "glitch_out") {
                var td = fx(L, "ADBE Turbulent Displace"); td.property("Amount").setValueAtTime(t0, 0); td.property("Amount").setValueAtTime(t1, 260); td.property("Size").setValue(18); td.property("Evolution").expression = "time*900;";
                var nz = fx(L, "ADBE Noise"); nz.property(1).setValueAtTime(t0, 0); nz.property(1).setValueAtTime(t1, 100);
                op.expression = "time<" + t0 + "?value: (posterizeTime(15), Math.max(0, 1-Math.max(0,time-" + (t0 + 0.5) + ")/" + (t1 - t0 - 0.5) + ")*(random()>0.25?100:40));";
            } else if (tipo === "melt") {
                var sc = S(L), v = sc.valueAtTime(t0, false); sc.setValueAtTime(t0, v); sc.setValueAtTime(t1, [v[0] * 1.06, v[1] * 1.35]);
                var tm = fx(L, "ADBE Turbulent Displace"); tm.property("Amount").setValueAtTime(t0, 0); tm.property("Amount").setValueAtTime(t1, 180); tm.property("Size").setValue(60);
                op.setValueAtTime(t1 - 0.4, 100); op.setValueAtTime(t1, 0);
            } else if (tipo === "burn") {
                var bf = fx(L, "CC Burn Film"); bf.property("Evolution").setValueAtTime(t0, 0); bf.property("Evolution").setValueAtTime(t1, 110);
            } else if (tipo === "sparks") {
                var pw = fx(L, "CC Particle World"); pw.property("Birth Rate").setValueAtTime(t0, 0); pw.property("Birth Rate").setValueAtTime(t0 + 0.2, 8); pw.property("Birth Rate").setValueAtTime(t1, 0);
                op.expression = "time<" + t0 + "?value: (posterizeTime(20), Math.max(0, 1-(time-" + t0 + ")/" + (t1 - t0) + ")*(random()>0.4?100:0));";
            } else if (tipo === "smoke") {
                var fb = fx(L, "ADBE Fast Box Blur"); fb.property(1).setValueAtTime(t0, 0); fb.property(1).setValueAtTime(t1, 40);
                var ts = fx(L, "ADBE Turbulent Displace"); ts.property("Amount").setValueAtTime(t0, 0); ts.property("Amount").setValueAtTime(t1, 140); ts.property("Size").setValue(120);
                op.setValueAtTime(t0, 100); op.setValueAtTime(t1, 0);
            }
        } catch (e) { op.setValueAtTime(t0, 100); op.setValueAtTime(t1, 0); }
        var st = imp(D.estatica);
        if (st) { var S2 = c.layers.add(st); S2.name = "end static"; S(S2).setValue([W / st.width * 105, H / st.height * 105]); P(S2).setValue([W / 2, H / 2]); S2.blendingMode = BlendingMode.SCREEN; O(S2).setValueAtTime(t0 + 0.4, 0); O(S2).setValueAtTime(t1, 85); vida(S2, t0 + 0.4, DUR); }
        var et = texto("END OF TAPE", F_TIT, 64, PH, ParagraphJustification.CENTER_JUSTIFY, 80); anclar(et, true); P(et).setValue([W / 2, 900]); teclear(et, t1 - 0.25, 0.3); vida(et, t1 - 0.25, DUR);
        cue(t0, "glitch", -4, "self-destruct"); cue(t0 + 0.5, "sub", -6, "self-destruct");
    }

    // the generated ending (engine/final.py, H3 from his last frame): cut to it behind a glitch, its own sound, then END OF TAPE
    function finalGenerado(it, ts) {
        var L = c.layers.add(it); L.name = "SELF-DESTRUCT (H3)"; L.startTime = ts;
        var k = Math.max(W / it.width, H / it.height) * 100 * 1.02; S(L).setValueAtTime(ts, [k, k]); S(L).setValueAtTime(ts + it.duration, [k * 1.05, k * 1.05]); P(L).setValue([W / 2, H / 2]);
        vida(L, ts, Math.min(DUR, ts + it.duration));
        var te = ts + it.duration - 0.1, st = imp(D.estatica);
        if (st) { var S2 = c.layers.add(st); S2.name = "end static"; S(S2).setValue([W / st.width * 105, H / st.height * 105]); P(S2).setValue([W / 2, H / 2]); S2.blendingMode = BlendingMode.SCREEN; O(S2).expression = "posterizeTime(15); 30+random(30);"; vida(S2, te, DUR); }
        var et = texto("END OF TAPE", F_TIT, 64, PH, ParagraphJustification.CENTER_JUSTIFY, 80); anclar(et, true); P(et).setValue([W / 2, 900]); teclear(et, te + 0.05, 0.3); vida(et, te, DUR);
        cue(te, "glitch", -6, "end of tape");
    }
    function build(datos) {
        D = datos; DUR = D.total; CUES = []; nEv = 0;
        var FIN = D.final_clip ? new File(D.final_clip) : null, finDur = FIN && FIN.exists ? (D.final_dur || 5.17) : 0;
        if (finDur) DUR = D.total + finDur + 0.9;
        var tk = (D.estilo && D.estilo.tokens) || {}; BG = tk.fondo || BG; PH = tk.fosforo || PH; DIM = tk.fosforo_tenue || DIM; RED = tk.rojo || RED;
        var ty = (D.estilo && D.estilo.tipografia) || {}; F_TIT = ty.titulares || F_TIT; F_MONO = ty.mono || F_MONO; F_FINO = ty.mono_fino || F_FINO;
        for (var i = app.project.numItems; i >= 1; i--) { var it0 = app.project.item(i); if ((it0 instanceof CompItem && it0.name.indexOf(D.comp) === 0) || (it0 instanceof FolderItem && it0.name === D.comp + " media") || (it0 instanceof FootageItem && it0.file && it0.file.fsName.indexOf(D.comp) >= 0 && it0.file.fsName.indexOf("_mdna_sound") >= 0)) it0.remove(); }
        fold = app.project.items.addFolder(D.comp + " media"); cache = {};
        c = app.project.items.addComp(D.comp, W, H, 1, DUR, FPS);
        caja("background", W / 2, H / 2, W, H, BG, 100);
        var S0 = D.secciones, ultimo = null, GL = [];
        for (i = 0; i < S0.length; i++) {
            var s = S0[i];
            if (i) GL.push([s.ini, "cut to " + s.tipo]);
            if (s.tipo === "gancho" || s.tipo === "cabeza") {
                var L = narrador(s); if (L) ultimo = L;
                // evidence named while he talks: cut to the CRT and back (at least 2.4 s, never past the line)
                var ob = s.obras || [];
                for (var j = 0; j < ob.length; j++) {
                    var a = Math.max(s.ini + 0.6, ob[j].t), b = Math.min(s.fin - 0.5, a + 2.8, j + 1 < ob.length ? Math.max(ob[j + 1].t, a + 2.4) : 1e9);
                    if (b - a < 1.6) continue;
                    evidencia(ob[j].img, a, b, ob[j].stem, true); GL.push([a, "evidence in"]); GL.push([b, "evidence out"]);
                }
            } else if (s.tipo === "ficha") casoTitulo(s);
            else if (s.tipo === "cita") teletexto(s);
            else if (s.img) evidencia(s.img, s.ini, s.fin, s.stem, true);
        }
        if (finDur) { var fi = imp(D.final_clip); if (fi) { finalGenerado(fi, D.total - 0.05); GL.push([D.total - 0.05, "self-destruct"]); } }
        else if (D.autodestruccion && ultimo) autodestruir(ultimo, D.autodestruccion);
        subtitulos();
        hud();
        vhs();
        // glitches last: an adjustment layer only touches what is below it
        for (i = 0; i < GL.length; i++) glitch(GL[i][0], GL[i][1]);
        for (i = 0; i < D.voces.length; i++) { var V = c.layers.add(imp(D.voces[i].wav)); V.name = D.voces[i].id + " voice"; V.startTime = D.voces[i].start; }
        if (D.musica) { var mu = c.layers.add(imp(D.musica)); mu.name = "Music"; mu.outPoint = DUR; var nv = D.musica.indexOf("elegida") >= 0 ? 0 : -13.2, al = mu.property("Audio").property("Audio Levels"); al.setValueAtTime(0, [nv, nv]); al.setValueAtTime(Math.max(0, D.total - 0.3), [nv, nv]); if (finDur) al.setValueAtTime(D.total + 0.4, [nv - 10, nv - 10]); al.setValueAtTime(DUR, [-48, -48]); }
        return "ok " + c.numLayers + " layers\n" + CUES.join("\n");
    }
    return { build: build };
})();
