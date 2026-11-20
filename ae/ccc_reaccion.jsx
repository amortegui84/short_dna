// CCC reaction format (news) in After Effects: the delivered edit. Data from engine/build_reaccion_ae.py (the same
// reaccion.json as the Python preview engine/reaccion.py, so framing and timing match it).
// - footage full bleed ("full") or boxed over a blurred, darkened copy ("caja"); the preview's push-in sampled every 5 frames
// - the cut-out head small at the side, big for the hook and the verdict (Motion DNA SETTLE curve 0.3/0/0.1/1, 0.7 s), gone
//   in the "fuera" spans with a hard cut; on every clip it lands 9 % big and settles to 2 % in 4 frames (CCC "salto_avatar")
// - cards pop in with the template's pop (0 -> 105 -> 100 %), fade out in 0.2 s
// - captions Poppins SemiBold with a dark stroke, the spoken word amber; beside the small head a block of lines with the
//   words still to come dimmed
// Returns "ok N layers" and "CUE;t;sfx;gain;why" lines for Motion DNA sound.
// Rule for this file: comments always on their own line.
var REACCION = (function () {
    var c, D, W = 1080, H = 1920, FPS = 30, DUR, fold, cache = {}, CUES = [], WARN = [];
    var F_CAP = "Poppins-SemiBold", F_MONO = "InterTight-Medium", STROKE = "#000000";

    function rgb(h) { h = h.replace("#", ""); return [parseInt(h.substr(0, 2), 16) / 255, parseInt(h.substr(2, 2), 16) / 255, parseInt(h.substr(4, 2), 16) / 255]; }
    function imp(p) {
        if (!p) return null;
        if (cache[p] !== undefined) return cache[p];
        var f = new File(p);
        if (!f.exists) { WARN.push("WARN;missing file " + p); cache[p] = null; return null; }
        var it = app.project.importFile(new ImportOptions(f)); it.parentFolder = fold; cache[p] = it; return it;
    }
    function T(L) { return L.property("ADBE Transform Group"); }
    function O(L) { return T(L).property("ADBE Opacity"); }
    function P(L) { return T(L).property("ADBE Position"); }
    function S(L) { return T(L).property("ADBE Scale"); }
    function A(L) { return T(L).property("ADBE Anchor Point"); }
    function fx(L, m) { return L.property("ADBE Effect Parade").addProperty(m); }
    function vida(L, a, b) { L.inPoint = Math.max(0, a); L.outPoint = Math.min(L.containingComp.duration, b); return L; }
    function cue(t, sfx, gain, why) { if (t >= 0 && t < DUR) CUES.push("CUE;" + t.toFixed(3) + ";" + sfx + ";" + gain + ";" + why); }
    function easeAll(prop, inf) {
        var sp = prop.propertyValueType === PropertyValueType.TwoD_SPATIAL || prop.propertyValueType === PropertyValueType.ThreeD_SPATIAL;
        function avg(k0, k1, i) {
            var a = prop.keyValue(k0), b = prop.keyValue(k1), dt = Math.max(0.001, prop.keyTime(k1) - prop.keyTime(k0));
            if (!(a instanceof Array)) return Math.abs(b - a) / dt;
            if (sp) { var d = 0; for (var j = 0; j < a.length; j++) d += (b[j] - a[j]) * (b[j] - a[j]); return Math.sqrt(d) / dt; }
            return (b[i] - a[i]) / dt;
        }
        for (var k = 1; k <= prop.numKeys; k++) {
            var v = prop.keyValue(k), dims = (v instanceof Array) ? v.length : 1;
            var n = sp ? 1 : dims, ei = [], eo = [], x = inf[Math.min(k - 1, inf.length - 1)];
            for (var i = 0; i < n; i++) {
                var si = (x[2] && k > 1) ? x[2] * avg(k - 1, k, i) : 0, so = (x[3] && k < prop.numKeys) ? x[3] * avg(k, k + 1, i) : 0;
                ei.push(new KeyframeEase(si, Math.max(0.1, x[0]))); eo.push(new KeyframeEase(so, Math.max(0.1, x[1])));
            }
            prop.setTemporalEaseAtKey(k, ei, eo);
        }
    }
    function lineal(prop) { for (var k = 1; k <= prop.numKeys; k++) prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.LINEAR); }
    function keys(prop, ts, vs, inf) { for (var i = 0; i < ts.length; i++) prop.setValueAtTime(ts[i], vs[i]); if (inf) easeAll(prop, inf); return prop; }
    // template pop: scale 0 -> 105 % (0.28 s) -> 100 % (0.187 s), opacity in 0.133 s
    function pop(L, t0, sc) {
        keys(S(L), [t0, t0 + 0.28, t0 + 0.467], [[0, 0], [sc * 1.05, sc * 1.05], [sc, sc]], [[17, 12, 0, 7.5], [72, 30], [90, 17]]);
        keys(O(L), [t0, t0 + 0.133], [0, 100]);
    }

    // ---------------- footage
    function capaPlano(comp, it, p, dy) {
        var L = comp.layers.add(it); L.name = "FOOTAGE " + it.name; L.audioEnabled = p.audio !== null && p.audio !== undefined && !p.foto;
        if (!p.foto) {
            if (p.vel !== 1) L.stretch = 100 / p.vel;
            L.startTime = p.ini - p.desde / p.vel;
        }
        A(L).setValue([0, 0]);
        for (var i = 0; i < p.claves.length; i++) {
            var k = p.claves[i];
            S(L).setValueAtTime(k[0], [k[1], k[1]]); P(L).setValueAtTime(k[0], [k[2], k[3] + (dy || 0)]);
        }
        lineal(S(L)); lineal(P(L));
        if (L.audioEnabled) L.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([p.audio, p.audio]);
        return vida(L, p.ini, p.fin);
    }
    function plano(p) {
        var it = imp(p.src); if (!it) return;
        if (p.modo === "full") { capaPlano(c, it, p, 0); return; }
        // boxed: a blurred copy darkened to 45 % fills the 9:16; the clip in a W x ch window at y
        var Lb = c.layers.add(it); Lb.name = "FOOTAGE blur " + it.name; Lb.audioEnabled = false;
        if (!p.foto) { if (p.vel !== 1) Lb.stretch = 100 / p.vel; Lb.startTime = p.ini - p.desde / p.vel; }
        S(Lb).setValue([p.fondo_esc, p.fondo_esc]); P(Lb).setValue([W / 2, H / 2]);
        var bl = fx(Lb, "ADBE Gaussian Blur 2"); bl.property("ADBE Gaussian Blur 2-0001").setValue(60);
        try { bl.property("ADBE Gaussian Blur 2-0003").setValue(1); } catch (e) {}
        vida(Lb, p.ini, p.fin);
        var Ld = c.layers.addSolid([0, 0, 0], "FOOTAGE darken", W, H, 1, DUR); O(Ld).setValue(55); vida(Ld, p.ini, p.fin);
        var pc = app.project.items.addComp(D.comp + " box " + it.name + " " + p.ini.toFixed(2), W, p.ch, 1, DUR, FPS); pc.parentFolder = fold;
        capaPlano(pc, it, p, 0);
        var Lp = c.layers.add(pc); Lp.name = "FOOTAGE box " + it.name; P(Lp).setValue([W / 2, p.y + p.ch / 2]); vida(Lp, p.ini, p.fin);
        Lp.audioEnabled = pc.layer(1).audioEnabled;
    }

    // ---------------- host: a slider "g" (0 small .. 1 big) keyed on the SETTLE curve drives scale, x and the darkening
    function rigHost() {
        var N = c.layers.addNull(DUR); N.name = "HOST size (g)"; N.enabled = false;
        var g = fx(N, "ADBE Slider Control"); g.name = "g"; var sl = g.property(1), sw = D.sweep;
        sl.setValue(0);
        for (var i = 0; i < D.grande.length; i++) {
            var a = D.grande[i][0], b = D.grande[i][1];
            if (a - sw > 0) { sl.setValueAtTime(a - sw, 0); sl.setValueAtTime(a, 1); } else sl.setValueAtTime(Math.max(0, a), 1);
            sl.setValueAtTime(b, 1); if (b < DUR) sl.setValueAtTime(b + sw, 0);
        }
        if (sl.numKeys > 1) {
            var inf = []; for (var k = 1; k <= sl.numKeys; k++) inf.push(k % 2 ? [90, 30] : [90, 30]);
            easeAll(sl, inf);
            for (var k2 = 1; k2 <= sl.numKeys; k2++) {
                var v = sl.keyValue(k2), nx = k2 < sl.numKeys ? sl.keyValue(k2 + 1) : v;
                if (v === nx) sl.setInterpolationTypeAtKey(k2, sl.keyInInterpolationType(k2), KeyframeInterpolationType.HOLD);
            }
        }
        // big host: the footage behind darkens up to 55 %
        var Ld = c.layers.addSolid([0, 0, 0], "HOST darken behind (big)", W, H, 1, DUR);
        // ...only while the head is on screen: in a "fuera" span (a full plan, e.g. a generated concept shot) the ramp toward the
        // next big head darkened the end of the plan like a fade to black (review N04 minimax 2026-11-20)
        var fz = []; for (var f0 = 0; f0 < D.fuera.length; f0++) fz.push("[" + D.fuera[f0][0].toFixed(3) + "," + D.fuera[f0][1].toFixed(3) + "]");
        O(Ld).expression = 'var F = [' + fz.join(",") + ']; var v = 1; for (var i = 0; i < F.length; i++) if (time >= F[i][0] && time < F[i][1]) v = 0; thisComp.layer("HOST size (g)").effect("g")(1) * 55 * v;';
        var hayClip = []; for (var j = 0; j < D.clips.length; j++) hayClip.push(D.clips[j].ini.toFixed(3) + "," + D.clips[j].fin.toFixed(3));
        return Ld;
    }
    function host(cl, k) {
        var it = imp(cl.mate); if (!it) return null;
        var L = c.layers.add(it); L.name = "HOST " + it.name; L.audioEnabled = false; L.startTime = cl.ini - cl.desde;
        var bx = cl.caja[0], by = cl.caja[1], bw = cl.caja[2], bh = cl.caja[3];
        A(L).setValue([bx + bw / 2, by + bh]);
        // no scale pop on the cuts (review 2026-11-17: "un salto raro en el avatar"); a very soft floating drift instead
        var salto = "var e = 1.0;";
        var gx = 'var g = thisComp.layer("HOST size (g)").effect("g")(1);';
        // a generated clip whose head touches its own frame edges (MiniMax leans in: buns/ears cut by the clip) shows straight cut
        // lines when big (review N04 minimax 2026-11-20): big, it scales at least until the clip's edges sit on or past the video's
        var toca = bx <= 4 || bx + bw >= it.width - 4, smin = toca ? Math.max(W / it.width, (H + 4) / (by + bh)) * 101 : 0;
        S(L).expression = gx + salto + " var h = (" + D.alto_p + " + (" + D.alto_g + " - " + D.alto_p + ") * g) * e; var s = h / " + bh + " * 100; s = Math.max(s, " + smin.toFixed(2) + " * g); [s, s];";
        // floating: a slow, tiny drift (same seed on every clip, so a cut between clips does not jump): +-5 px, +-0.6 deg
        P(L).expression = gx + " seedRandom(7, true); var w = wiggle(0.35, 5) - value; [" + (W * D.host_x).toFixed(1) + " + (" + (W / 2) + " - " + (W * D.host_x).toFixed(1) + ") * g + w[0], " + H + " + 4 + w[1]];";
        T(L).property("ADBE Rotate Z").expression = "seedRandom(11, true); wiggle(0.25, 0.6);";
        // soft edge: choke the cut-out ~1 px so no dark rim shows on bright footage
        try { var ch = fx(L, "ADBE Simple Choker"); ch.property(2).setValue(1.0); } catch (e) {}
        vida(L, cl.ini, cl.fin);
        // hard cut out and back in the "fuera" spans
        for (var i = 0; i < D.fuera.length; i++) {
            var a = D.fuera[i][0], b = D.fuera[i][1];
            if (a < cl.fin && b > cl.ini) {
                O(L).setValueAtTime(Math.max(cl.ini, a), 0); if (b < cl.fin) O(L).setValueAtTime(b, 100);
                if (a > cl.ini) O(L).setValueAtTime(cl.ini, 100);
                for (var q = 1; q <= O(L).numKeys; q++) O(L).setInterpolationTypeAtKey(q, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
            }
        }
        L.motionBlur = true;
        return L;
    }

    // ---------------- captions
    function capText(L, words, tam, col, blk) {
        var p = L.property("ADBE Text Properties").property("ADBE Text Document"), d = p.value;
        d.resetCharStyle(); d.font = F_CAP; d.fontSize = tam; d.applyFill = true; d.fillColor = rgb(col);
        d.applyStroke = true; d.strokeColor = rgb(STROKE); d.strokeWidth = D.estilo.sub_borde * 2; d.strokeOverFill = false;
        d.justification = blk ? ParagraphJustification.LEFT_JUSTIFY : ParagraphJustification.CENTER_JUSTIFY; d.tracking = 0;
        if (blk) { try { d.autoLeading = false; d.leading = Math.round(tam * 1.18); } catch (e) {} }
        p.setValue(d);
    }
    function animador(L, nombre, S0, prop, val, cond) {
        var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"); an.name = nombre;
        an.property("ADBE Text Animator Properties").addProperty(prop).setValue(val);
        var sl = an.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sl.property("ADBE Text Range Type2").setValue(3);
        sl.property("ADBE Text Expressible Amount").expression = "var S=[" + S0.join(",") + "], cur=-1; for (var q=0;q<S.length;q++) if (time>=S[q]-0.02) cur=q; " + cond;
    }
    function subtitulos() {
        var E = D.estilo;
        for (var i = 0; i < D.subs.length; i++) {
            var s = D.subs[i], ws = [], S0 = [];
            for (var j = 0; j < s.words.length; j++) { ws.push(s.words[j].w); S0.push(s.words[j].s.toFixed(3)); }
            var blk = s.tipo === "bloque", L;
            // QA 2026-11-19: the block ended at x ~1040, outside the safe area; it never passes x = W - 90
            if (blk) { L = c.layers.addBoxText([Math.min(s.ancho, W - 90 - s.x), 600], ws.join(" ")); capText(L, ws, E.bloque_tam, E.sub_color, true); }
            else { L = c.layers.addText(ws.join(" ")); capText(L, ws, E.sub_tam, E.sub_color, false); }
            L.name = "CAP " + (i + 1) + (blk ? " block" : "");
            var r = L.sourceRectAtTime(s.ini, false);
            if (blk) { A(L).setValue([r.left, r.top + r.height / 2]); P(L).setValue([s.x, s.y]); }
            else {
                A(L).setValue([r.left + r.width / 2, r.top + r.height / 2]);
                var x = Math.min(Math.max(s.x, 40 + r.width / 2), W - 40 - r.width / 2);
                if (r.width > W - 80) { var k = (W - 80) / r.width * 100; S(L).setValue([k, k]); x = W / 2; }
                P(L).setValue([x, s.y]);
            }
            // the spoken word in amber (the chunk: the first word until the voice reaches it)
            animador(L, "spoken word", S0, "ADBE Text Fill Color", rgb(E.sub_activa), blk ? "(textIndex-1)===cur?100:0;" : "(textIndex-1)===Math.max(cur,0)?100:0;");
            // block: the words still to come dimmed to 37 %
            // QA 2026-11-19: whole-glyph opacity left the words unreadable on white footage; only the fill dims, the dark stroke stays
            if (blk) animador(L, "still to come", S0, "ADBE Text Fill Opacity", 40, "(textIndex-1)>cur?100:0;");
            // QA 2026-11-19 (triple QA: N04 Christie's 22-25 s, X01 court papers, N09 price card): over text-heavy stills the stroke
            // alone did not separate the captions; a soft dark shadow under them does, without a box
            try { var ds = L.property("ADBE Effect Parade").addProperty("ADBE Drop Shadow"); ds.property("ADBE Drop Shadow-0001").setValue([0, 0, 0, 1]); ds.property("ADBE Drop Shadow-0002").setValue(78); ds.property("ADBE Drop Shadow-0004").setValue(4); ds.property("ADBE Drop Shadow-0005").setValue(26); } catch (eS) {}
            vida(L, s.ini, s.fin);
        }
    }

    function build(datos) {
        D = datos; DUR = D.total; CUES = []; WARN = [];
        function hay(ps) { try { var f = app.fonts.getFontsByPostScriptName(ps); return f && f.length > 0; } catch (e) { return true; } }
        if (!hay(F_CAP)) { F_CAP = "InterTight-SemiBold"; WARN.push("WARN;Poppins not installed for all users: captions in Inter Tight"); }
        if (!hay(F_MONO)) { F_MONO = "Bahnschrift-Light"; WARN.push("WARN;Inter Tight Medium missing: credits in Bahnschrift"); }
        for (var i = app.project.numItems; i >= 1; i--) { var it0 = app.project.item(i); if ((it0 instanceof CompItem && it0.name.indexOf(D.comp) === 0) || (it0 instanceof FolderItem && it0.name === D.comp + " media") || (it0 instanceof FootageItem && it0.file && it0.file.fsName.indexOf("_mdna_sound") >= 0 && it0.file.fsName.indexOf(D.comp) >= 0)) it0.remove(); }
        fold = app.project.items.addFolder(D.comp + " media"); cache = {};
        c = app.project.items.addComp(D.comp, W, H, 1, DUR, FPS); c.motionBlur = true; c.shutterAngle = 180;
        c.layers.addSolid([11 / 255, 17 / 255, 22 / 255], "BG", W, H, 1, DUR);
        // 1. footage, in order (a later plan sits above an earlier one)
        for (i = 0; i < D.planos.length; i++) { plano(D.planos[i]); if (i) cue(D.planos[i].ini, "swish", -16, "cut"); }
        // 2. credit of the footage on screen
        for (i = 0; i < D.creditos.length; i++) {
            var cr = D.creditos[i], Lc = c.layers.addText(cr.txt), pc = Lc.property("ADBE Text Properties").property("ADBE Text Document"), dc = pc.value;
            dc.resetCharStyle(); dc.font = F_MONO; dc.fontSize = 32; dc.applyFill = true; dc.fillColor = rgb(D.estilo.papel);
            dc.applyStroke = true; dc.strokeColor = [0, 0, 0]; dc.strokeWidth = 6; dc.strokeOverFill = false; dc.tracking = 40; pc.setValue(dc);
            var rc = Lc.sourceRectAtTime(cr.ini, false);
            // a long credit shrinks to fit inside the safe area (Wikimedia credits with the licence)
            // a long credit breaks into lines at 32 px (greedy by measured character width), and only shrinks if a line still overflows
            if (rc.width > 960) {
                var cw = rc.width / cr.txt.length, por = Math.floor(940 / cw), pal = cr.txt.split(" "), lin = [], cur = "";
                for (var w = 0; w < pal.length; w++) { var t2 = cur ? cur + " " + pal[w] : pal[w]; if (t2.length > por && cur) { lin.push(cur); cur = pal[w]; } else cur = t2; }
                if (cur) lin.push(cur);
                dc = pc.value; dc.text = lin.join("\r"); pc.setValue(dc); rc = Lc.sourceRectAtTime(cr.ini, false);
                if (rc.width > 960) { dc = pc.value; dc.fontSize = Math.max(28, Math.floor(32 * 960 / rc.width)); pc.setValue(dc); rc = Lc.sourceRectAtTime(cr.ini, false); }
            }
            A(Lc).setValue([rc.left, rc.top]); P(Lc).setValue([56, 250]);
            Lc.name = "CREDIT " + cr.txt; vida(Lc, cr.ini, cr.fin);
            // a dark tab behind the credit so it reads on any footage
            var Lr = c.layers.addShape(); Lr.name = "CREDIT tab " + cr.txt;
            var gv = Lr.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group").property("ADBE Vectors Group");
            var re = gv.addProperty("ADBE Vector Shape - Rect"); re.property("ADBE Vector Rect Size").setValue([rc.width + 32, rc.height + 20]);
            gv.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(rgb("#1E1714"));
            P(Lr).setValue([40 + (rc.width + 32) / 2, 240 + (rc.height + 20) / 2]); O(Lr).setValue(85); vida(Lr, cr.ini, cr.fin); Lr.moveAfter(Lc);
        }
        // 3. host darkening + cut-out clips
        rigHost();
        for (i = 0; i < D.clips.length; i++) host(D.clips[i], i);
        for (i = 0; i < D.fuera.length; i++) { cue(D.fuera[i][0], "swish", -12, "head out"); if (D.fuera[i][1] < DUR) cue(D.fuera[i][1] - 0.1, "swish", -10, "head back"); }
        for (i = 0; i < D.grande.length; i++) { if (D.grande[i][0] > 0.1) cue(D.grande[i][0] - D.sweep, "whoosh", -12, "head big"); if (D.grande[i][1] < DUR - 0.5) cue(D.grande[i][1], "whoosh", -14, "head small"); }
        // 4. topic label and cards
        if (D.titulo) {
            var Lt = c.layers.add(imp(D.titulo.img)); Lt.name = "TOPIC"; P(Lt).setValue([W / 2, D.titulo.y]); vida(Lt, D.titulo.desde, D.titulo.hasta);
            var oc = []; for (var q = 0; q < D.tarjetas.length; q++) oc.push("[" + D.tarjetas[q].ini + "," + D.tarjetas[q].fin + "]");
            O(Lt).expression = "var C=[" + oc.join(",") + "]; var o=100; for (var i=0;i<C.length;i++) if (time>=C[i][0]&&time<C[i][1]) o=0; o;";
        }
        for (i = 0; i < D.tarjetas.length; i++) {
            var t = D.tarjetas[i], Lk = c.layers.add(imp(t.img)); Lk.name = "CARD " + (i + 1);
            P(Lk).setValue([W / 2, t.y + t.h / 2]); pop(Lk, t.ini, 100);
            O(Lk).setValueAtTime(t.fin - 0.2, 100); O(Lk).setValueAtTime(t.fin, 0);
            Lk.motionBlur = true; vida(Lk, t.ini, t.fin); cue(t.ini, "pop", -8, "card " + (i + 1));
        }
        // 5. captions
        subtitulos();
        // 6. audio: voice, music bed
        var V = c.layers.add(imp(D.voz)); V.name = "VOICE";
        if (D.musica) {
            var it = imp(D.musica);
            if (it) {
                var t0 = 0;
                while (t0 < DUR) { var Mu = c.layers.add(it); Mu.name = "MUSIC"; Mu.startTime = t0; Mu.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([D.musica_db, D.musica_db]); t0 += it.duration; }
            }
        }
        return "ok " + c.numLayers + " layers\n" + WARN.join("\n") + (WARN.length ? "\n" : "") + CUES.join("\n");
    }
    return { build: build };
})();
