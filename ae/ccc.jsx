// CCC: the Cool Culture Club format ("Bricolage Pop", brands/ccc/styles/ccc_bricolage.json). Builds the edit from the same data
// as COLLAGE and CINTA (datos_ae.json). Every value below is read from the Bosch template project
// (brands/ccc/references/bosch_template/, rules in brands/ccc/references/bosch_ae_rules.md):
// - host plate: teal gradient, the COOL CULTURE CLUB wall recoloured coral at 95% (its edges show the teal), played at 1/1.34
//   speed, faded toward the bottom by a luma ramp (white at y 291, black at y 1362); the cut-out head on top; brightness +18,
//   contrast +6; the whole plate lands big and settles on every cut (wide 109->102, close 144->134, medium 122->114 in 4 frames)
// - artworks full bleed, always moving, a hard cut to another crop every ~1.2-2.4 s; motion blur on
// - detail zoom: the work full bleed with a 4% push, magnifier cards centred (780x1040, 600x760), cream tape, soft shadow
// - bricolage portrait and quote card: the template's own positions, scales, entry moves and timings
// - captions Poppins SemiBold 66, cream with a 10 px dark stroke, the spoken word amber, y 1503 (1835 over the portrait card)
// Called by engine/build_collage.py when the style has "builder": "ccc". Returns "ok N layers" and "CUE;t;sfx;gain;why" lines.
// Rule for this file: comments always on their own line.
var CCC = (function () {
    var c, D, W = 1080, H = 1920, FPS = 30, DUR, fold, cache = {}, CUES = [];
    var TOP = "#FC604C", BOT = "#132019", CREAM = "#F6EBD9", AMBER = "#E8C66A", INK = "#1E1714", PAPER = "#F0E8DD", BGCREAM = "#F0E8DD";
    var TEAL_TOP = "#5FB191", TEAL_BOT = "#244038", WALL_CORAL = "#ED4F45", TAPE = "#EDE6CC", STROKE = "#1A1208";
    var F_CAP = "Poppins-SemiBold", F_QUOTE = "InstrumentSerif-Italic", F_BRAND = "Bahnschrift-Light", F_CTA = "Poppins-SemiBold", F_LABEL = "Poppins-Bold";

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
    function R(L) { return T(L).property("ADBE Rotate Z"); }
    function A(L) { return T(L).property("ADBE Anchor Point"); }
    function fx(L, m) { return L.property("ADBE Effect Parade").addProperty(m); }
    function vida(L, a, b) { L.inPoint = Math.max(0, a); L.outPoint = Math.min(L.containingComp.duration, b); return L; }
    function cue(t, sfx, gain, why) { if (t >= 0 && t < DUR) CUES.push("CUE;" + t.toFixed(3) + ";" + sfx + ";" + gain + ";" + why); }
    function shp(n) { var L = c.layers.addShape(); L.name = n; return L; }
    function grp(L, n) { var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); g.name = n; return g.property("ADBE Vectors Group"); }
    function rect(g, w, h, r) { var e = g.addProperty("ADBE Vector Shape - Rect"); e.property("ADBE Vector Rect Size").setValue([w, h]); e.property("ADBE Vector Rect Roundness").setValue(r || 0); return e; }
    function fill(g, col, op) { var f = g.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(rgb(col)); if (op !== undefined) f.property("ADBE Vector Fill Opacity").setValue(op); return f; }
    function texto(s, font, size, col, just, track) {
        var L = c.layers.addText(s), p = L.property("ADBE Text Properties").property("ADBE Text Document"), d = p.value;
        d.resetCharStyle(); d.font = font; d.fontSize = size; d.applyFill = true; d.fillColor = rgb(col); d.applyStroke = false;
        d.justification = just || ParagraphJustification.LEFT_JUSTIFY; d.tracking = track || 0; p.setValue(d); return L;
    }
    function centrar(L) { var r = L.sourceRectAtTime(0, false); A(L).setValue([r.left + r.width / 2, r.top + r.height / 2]); return r; }
    function cover(it, w, h) { return Math.max((w || W) / it.width, (h || H) / it.height) * 100; }
    // temporal ease on every key: inf[k] = [in influence, out influence, in speed x, out speed x]. Speeds are multiples of the
    // average speed of the neighbouring segment: the template's snappy keys leave or land fast (pop/slide leave at 7.5x,
    // a drop lands at 4x); 0 = start or stop at rest
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
    function keys(prop, ts, vs, inf) {
        for (var i = 0; i < ts.length; i++) prop.setValueAtTime(ts[i], vs[i]);
        if (inf) easeAll(prop, inf);
        return prop;
    }
    // stop-motion hold once a piece has landed: 6 fps rotation wiggle (template: inPoint + 0.9 s)
    function jitter(L, t0, amp, seed) {
        R(L).expression = "if (time < " + t0.toFixed(3) + ") value; else { posterizeTime(6); seedRandom(" + (seed || L.index) + ", true); value + (wiggle(1, " + amp + ") - value); }";
    }
    function rampa(L, y0, c0, y1, c1) {
        var g = fx(L, "ADBE Ramp");
        g.property("ADBE Ramp-0001").setValue([540, y0]); g.property("ADBE Ramp-0002").setValue(c0.concat([1]));
        g.property("ADBE Ramp-0003").setValue([540, y1]); g.property("ADBE Ramp-0004").setValue(c1.concat([1]));
        return g;
    }
    // background of the bricolage and quote modules: cream, with the coral-to-deep-teal ramp at 91% over it
    function fondo(a, b) {
        var Lc = c.layers.addSolid(rgb(BGCREAM), "BG cream", W, H, 1, DUR); vida(Lc, a, b);
        var L = c.layers.addSolid([0, 0, 0], "BG gradient", W, H, 1, DUR); rampa(L, 291, rgb(TOP), 1362, rgb(BOT)); O(L).setValue(91);
        return vida(L, a, b);
    }
    // ---------------- template entry moves (measured curves)
    // pop: scale 0 -> 105% (0.28 s) -> 100% (0.187 s), opacity in 0.133 s
    function pop(L, t0, sc) {
        keys(S(L), [t0, t0 + 0.28, t0 + 0.467], [[0, 0], [sc * 1.05, sc * 1.05], [sc, sc]], [[17, 12, 0, 7.5], [72, 30], [90, 17]]);
        keys(O(L), [t0, t0 + 0.133], [0, 100]);
    }
    // slide: in from the right edge in 0.7 s, a hard ease out
    function slide(L, t0, x0, x, y) { keys(P(L), [t0, t0 + 0.7], [[x0, y], [x, y]], [[17, 12, 0, 7.5], [72, 17]]); }
    // drop: falls in and bounces twice (template position keys)
    function drop(L, t0, x, y, from) {
        var y0 = from === undefined ? y - 320 : from;
        keys(P(L), [t0, t0 + 0.333, t0 + 0.5, t0 + 0.667, t0 + 0.767, t0 + 0.867], [[x, y0], [x, y], [x, y - 48], [x, y], [x, y - 14], [x, y]],
            [[17, 55], [10, 30, 4, 0], [90, 55], [10, 30, 4, 0], [90, 55], [10, 17, 4, 0]]);
        keys(O(L), [t0, t0 + 0.133], [0, 100]);
    }
    // wipe: linear wipe 100 -> 0 in 0.7 s (ease 50/85)
    function wipe(L, t0, ang) {
        var lw = fx(L, "ADBE Linear Wipe"); lw.property(2).setValue(ang === undefined ? 270 : ang); lw.property(3).setValue(10);
        keys(lw.property(1), [t0, t0 + 0.7], [100, 0], [[17, 50], [85, 17]]);
    }
    // grow: scale 80% -> 100% with a turn, 0.467 s
    function grow(L, t0, sc, r0, r1) {
        keys(S(L), [t0, t0 + 0.467], [[sc * 0.8, sc * 0.8], [sc, sc]], [[17, 30], [90, 17]]);
        keys(R(L), [t0, t0 + 0.467], [r0, r1], [[17, 30], [90, 17]]);
        keys(O(L), [t0, t0 + 0.2], [0, 100]);
    }
    function spin(L, t0, sc, rot) { pop(L, t0, sc); keys(R(L), [t0, t0 + 0.467], [rot - 180, rot], [[17, 30], [90, 17]]); }
    // ---------------- the host plate (one precomp per host line)
    function placa(sec) {
        var a = sec.ini, b = sec.fin, dur = b - a;
        var hi = imp(sec.mate || sec.clip), pc = app.project.items.addComp(D.comp + " plate " + (sec.id || a.toFixed(1)), W, H, 1, dur, (hi && hi.frameRate) ? hi.frameRate : 24); pc.parentFolder = fold;
        var bg = pc.layers.addSolid([0, 0, 0], "teal gradient", W, H, 1, dur); rampa(bg, 0, rgb(TEAL_TOP), 1920, rgb(TEAL_BOT));
        var tw = imp(D.type_wall);
        if (tw) {
            var Wl = pc.layers.add(tw); Wl.name = "type wall"; Wl.audioEnabled = false;
            S(Wl).setValue([95, 95]);
            Wl.timeRemapEnabled = true; Wl.property("ADBE Time Remapping").expression = "((time + " + a.toFixed(3) + ") / 1.34) % (source.duration - 0.05);";
            Wl.outPoint = dur;
            var ti = fx(Wl, "ADBE Tint"); ti.property(1).setValue([0.02, 0.02, 0.02, 1]); ti.property(2).setValue(rgb(WALL_CORAL).concat([1])); ti.property(3).setValue(100);
            var mt = pc.layers.addSolid([0, 0, 0], "wall fade (luma)", W, H, 1, dur); rampa(mt, 291, [1, 1, 1], 1362, [0, 0, 0]);
            mt.moveBefore(Wl); Wl.setTrackMatte(mt, TrackMatteType.LUMA);
        }
        var it = imp(sec.mate || sec.clip);
        if (it) {
            var L = pc.layers.add(it); L.name = "HEAD " + sec.id; L.audioEnabled = false;
            var off = a - (sec.t0base !== undefined ? sec.t0base : a);
            // past the end of the clip (the ending tail) the last 0.3 s (the closing smile, mouth shut) plays back and forth instead of freezing
            L.timeRemapEnabled = true; L.property("ADBE Time Remapping").expression = "var d = source.duration - 0.05, t = Math.max(0, time + " + off.toFixed(3) + "); if (t > d) { var k = (t - d) % (2 * Math.min(d, 0.3)); t = k < Math.min(d, 0.3) ? d - k : d - 2 * Math.min(d, 0.3) + k; } t;";
            L.outPoint = dur;
            // H3 renders the head ~14% smaller and lower than the Seedance plate: scale it around (540, 640)
            var k = cover(it), hk = (D.estilo && D.estilo.cabeza && D.estilo.cabeza.escala_h3) || 1.06, kk = k / 100;
            A(L).setValue([it.width / 2, it.height / 2 + (640 - H / 2) / kk]); P(L).setValue([W / 2, 640]); S(L).setValue([k * hk, k * hk]);
        }
        return pc;
    }
    // end time of the spoken word that starts near t (captions' word timings)
    function finPalabra(t) {
        var best = null;
        for (var i = 0; i < D.subs.length; i++) for (var j = 0; j < D.subs[i].words.length; j++) {
            var w = D.subs[i].words[j]; if (Math.abs(w.s - t) < 0.4 && (!best || Math.abs(w.s - t) < Math.abs(best.s - t))) best = w;
        }
        return best ? best.e : t;
    }
    // times where the host is cut away (works inside host lines), so a punch-in never lands just before a cut
    function cortesDe(sec) {
        var out = [sec.fin], ob = sec.obras || [];
        if (sec.tipo === "gancho") return out;
        for (var j = 0; j < ob.length; j++) out.push(Math.max(sec.ini + 1.2, finPalabra(ob[j].t) + 0.05));
        return out;
    }
    // the head's background without the head (teal gradient + coral type wall faded by its luma ramp): it replaces every black
    // background (the template modules' "BG black", the master background) so a transition never flashes black
    function fondoCabeza(dur, t0, nombre) {
        var fc = app.project.items.addComp(nombre || (D.comp + " head background"), W, H, 1, Math.max(0.1, dur), FPS); fc.parentFolder = fold;
        var bg = fc.layers.addSolid([0, 0, 0], "teal gradient", W, H, 1, fc.duration); rampa(bg, 0, rgb(TEAL_TOP), 1920, rgb(TEAL_BOT));
        var tw = imp(D.type_wall);
        if (tw) {
            var Wl = fc.layers.add(tw); Wl.name = "type wall"; Wl.audioEnabled = false; S(Wl).setValue([95, 95]);
            Wl.timeRemapEnabled = true; Wl.property("ADBE Time Remapping").expression = "((time + " + t0.toFixed(3) + ") / 1.34) % (source.duration - 0.05);";
            Wl.outPoint = fc.duration;
            var ti = fx(Wl, "ADBE Tint"); ti.property(1).setValue([0.02, 0.02, 0.02, 1]); ti.property(2).setValue(rgb(WALL_CORAL).concat([1])); ti.property(3).setValue(100);
            var mt = fc.layers.addSolid([0, 0, 0], "wall fade (luma)", W, H, 1, fc.duration); rampa(mt, 291, [1, 1, 1], 1362, [0, 0, 0]);
            mt.moveBefore(Wl); Wl.setTrackMatte(mt, TrackMatteType.LUMA);
        }
        return fc;
    }
    function anfitrion(sec) {
        var a = sec.ini, b = sec.fin, pc = placa(sec);
        var L = c.layers.add(pc); L.name = "HOST " + sec.id; L.startTime = a; vida(L, a, b);
        var bc = fx(L, "ADBE Brightness & Contrast 2"); bc.property(1).setValue(18); bc.property(2).setValue(6);
        // wide (109->102), then close (144->134) and medium (122->114) in turn, 4 frames each, ease out 30 / in 90 then hold
        var sl0 = sec.saltos || [[a, 1.0]], sc = S(L), f4 = 4 / FPS, LV = [[109, 102], [144, 134], [122, 114]], sl = [], ct = cortesDe(sec);
        // drop a punch that would last less than 1 s before the host is cut away (Blake v1: a 4-frame close-up before "angels")
        for (var q0 = 0; q0 < sl0.length; q0++) { var ok = true; for (var c0 = 0; c0 < ct.length; c0++) if (q0 > 0 && ct[c0] > sl0[q0][0] && ct[c0] - sl0[q0][0] < 1.0) ok = false; if (ok) sl.push(sl0[q0]); }
        for (var q = 0; q < sl.length; q++) {
            var t = Math.max(a, sl[q][0]), lv = q === 0 ? LV[0] : (q % 2 === 1 ? LV[1] : LV[2]);
            sc.setValueAtTime(t, [lv[0], lv[0]]); sc.setValueAtTime(Math.min(b, t + f4), [lv[1], lv[1]]);
            if (q) cue(t, "swish", -12, "punch " + sec.id);
        }
        var inf = []; for (var z = 0; z < sc.numKeys; z++) inf.push(z % 2 === 0 ? [17, 30] : [90, 17]);
        if (sc.numKeys) easeAll(sc, inf);
        // the settle key holds until the next beat (template: BH keys): the plate never creeps between cuts
        for (var z2 = 2; z2 <= sc.numKeys; z2 += 2) sc.setInterpolationTypeAtKey(z2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.HOLD);
        return L;
    }
    // ---------------- artworks: full bleed, always moving; long holds become crops with hard cuts (~2.2 s each)
    function plano(it, a, b, z0, z1, f0, f1) {
        var L = c.layers.add(it); L.name = "ARTWORK " + it.name; L.audioEnabled = false; L.motionBlur = true;
        var k = cover(it);
        P(L).setValue([W / 2, H / 2]); f0 = dentro(it, z0, f0); f1 = dentro(it, z1, f1);
        if (f0[0] !== f1[0] || f0[1] !== f1[1]) keys(A(L), [a, b], [[f0[0] * it.width, f0[1] * it.height], [f1[0] * it.width, f1[1] * it.height]]);
        else A(L).setValue([f0[0] * it.width, f0[1] * it.height]);
        keys(S(L), [a, b], [[k * z0, k * z0], [k * z1, k * z1]]);
        // slow linear moves (template: LL 17/17)
        lineal(S(L)); if (A(L).numKeys) lineal(A(L));
        vida(L, a, b);
        return L;
    }
    // keep the frame inside the work at zoom z
    function dentro(it, z, f) {
        var k = cover(it) * z / 100, hw = W / 2 / k / it.width, hh = H / 2 / k / it.height;
        return [Math.min(1 - hw, Math.max(hw, f[0])), Math.min(1 - hh, Math.max(hh, f[1]))];
    }
    function obra(img, a, b, modo, foco) {
        var it = imp(img); if (!it || b - a < 0.2) return null;
        var dur = b - a, land = it.width / it.height > W / H * 1.15;
        if (modo === "revelado") {
            // zoom out from a detail to the whole work (template: 200% -> fit, anchor to the centre, ease 75/95)
            var L = plano(it, a, b, 2.0, 1.0, dentro(it, 2, foco || [0.5, 0.45]), [0.5, 0.5]);
            easeAll(S(L), [[17, 75], [95, 17]]); if (A(L).numKeys) easeAll(A(L), [[17, 75], [95, 17]]);
            return L;
        }
        var n = dur > 2.8 ? Math.ceil(dur / 2.2) : 1, seg = dur / n, out = null;
        for (var i = 0; i < n; i++) {
            var s0 = a + i * seg, s1 = (i === n - 1) ? b : s0 + seg;
            if (i === 0) out = plano(it, s0, s1, 1.0, 1.08, [0.5, 0.5], [0.5, 0.5]);
            else {
                // crops on alternate sides, 1.9x then 1.5x, panning 12% (landscape works sideways, tall ones downward)
                var z = i % 2 ? 1.9 : 1.5, side = i % 2 ? 0.3 : 0.7, d = 0.12 * (i % 2 ? 1 : -1);
                var fa = land ? [side, 0.45] : [0.5, side], fb = land ? [side + d, 0.45] : [0.5, side + d];
                if (foco && i === 1) { fa = foco; fb = land ? [foco[0] + d, foco[1]] : [foco[0], foco[1] + d]; }
                plano(it, s0, s1, z, z * 1.04, dentro(it, z, fa), dentro(it, z * 1.04, fb));
                cue(s0, "tick", -18, "crop");
            }
        }
        return out;
    }
    // (a slide comp must keep the name "Slide 0N ...": its expressions read N from thisComp.name.substr(6, 2))
    // ---------------- the template's art modules, reused as built (3D carousel, desk scroll of framed prints, slider, strip,
    // Ken Burns): the module comp is imported from the Bosch template, duplicated, its "(swap me)" images and titles replaced
    // with this artist's works, and its own timing control (Progress keys, Seconds per Artwork, slide keys) retimed so each work
    // is in focus when the voice names it. Kinds rotate across the episode so no two runs look the same.
    var TPLF = null, nMod = 0, CLARA = {};
    function plantilla() {
        if (TPLF) return TPLF;
        var f = new File(D.plantilla_aep || D.kit.replace(/kit[\/\\]bricolage[\/\\]?$/, "references/bosch_template/Cool-Culture-Club_template_Bosch.aep"));
        if (!f.exists) return null;
        TPLF = app.project.importFile(new ImportOptions(f)); TPLF.name = D.comp + " template"; TPLF.parentFolder = fold;
        return TPLF;
    }
    function enCarpeta(it, F) { var p = it.parentFolder; while (p && p !== app.project.rootFolder) { if (p === F) return true; p = p.parentFolder; } return false; }
    function compTpl(nombre) {
        var F = plantilla(); if (!F) return null;
        for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i); if (it instanceof CompItem && it.name === nombre && enCarpeta(it, F)) return it; }
        return null;
    }
    function capa(comp, re) { for (var i = 1; i <= comp.numLayers; i++) if (re.test(comp.layer(i).name)) return comp.layer(i); return null; }
    function setTexto(L, txt) { if (!L) return; var p = L.property("ADBE Text Properties").property("ADBE Text Document"), d = p.value; d.text = txt; p.setValue(d); }
    function sinSonido(comp) { for (var i = comp.numLayers; i >= 1; i--) { var L = comp.layer(i); if (/Motion DNA sound/.test(L.name)) L.remove(); } }
    function titulo(img) {
        var stem = String(img).replace(/^.*[\/\\]/, "").replace(/\.[^.]+$/, ""), t = (D.titulos || {})[stem];
        return t ? [String(t[0]).toUpperCase(), String(t[1]).toUpperCase()] : [stem.toUpperCase(), ""];
    }
    function dos(i) { return (i < 10 ? "0" : "") + i; }
    // rewrite every expression in a comp that names another comp (the template's rigs read their controls by comp name)
    function reapuntar(comp, viejo, nuevo) {
        function walk(g) {
            for (var i = 1; i <= g.numProperties; i++) {
                var p = g.property(i); if (!p) continue;
                if (p.propertyType === PropertyType.PROPERTY) { try { if (p.canSetExpression && p.expression && p.expression.indexOf(viejo) >= 0) p.expression = p.expression.split(viejo).join(nuevo); } catch (e) {} }
                else walk(p);
            }
        }
        for (var i = 1; i <= comp.numLayers; i++) walk(comp.layer(i));
    }
    // SuisseIntlMono (the template's title font) is commercial and not installed: Cascadia Mono, which the template's own font
    // menu already lists, takes its place in every text layer and font expression of a module
    function mono(comp) {
        var MONO = "CascadiaMono-Roman";
        for (var i = 1; i <= comp.numLayers; i++) {
            var tp = comp.layer(i).property("ADBE Text Properties"); if (!tp) continue;
            var st = tp.property("ADBE Text Document");
            if (st.expression && /SuisseIntlMono/.test(st.expression)) st.expression = st.expression.replace(/SuisseIntlMono-(Regular|Bold)/g, MONO);
            var d = st.value; if (/SuisseIntlMono/.test(d.font)) { d.font = MONO; st.setValue(d); }
        }
    }
    function efecto(L, nombre) { return L.property("ADBE Effect Parade").property(nombre).property(1); }
    function modulo(kind, works, marks, a, b) {
        var nombres = { carrusel: "Art Carousel (9x16)", scroll: "Art Scroll (9x16)", slider: "Art Slider (9x16)", tira: "Art Strip (9x16)", kenburns: "Ken Burns Details (9x16)" };
        var src = compTpl(nombres[kind]); if (!src) return null;
        nMod++;
        var m = src.duplicate(); m.name = D.comp + " module " + nMod + " " + kind; m.parentFolder = fold; sinSonido(m); mono(m);
        var dur = b - a, anio = String(D.fechas || "").match(/(\d{3,4})(?!.*\d{3,4})/), artista = String(D.artista || "").toUpperCase() + (anio ? " · C. " + anio[1] : "");
        // the cards: the named works first, then the artist's other works so the neighbours are never empty
        var lista = works.slice(0), otras = (D.obrasArtista || []).slice(0), dir = String(works[0]).replace(/[\/\\][^\/\\]*$/, "");
        for (var st in (D.titulos || {})) otras.push(dir + "/" + st + ".jpg");
        for (var o = 0; o < otras.length; o++) { var ya = false; for (var q = 0; q < lista.length; q++) if (lista[q] === otras[o]) ya = true; if (!ya) lista.push(otras[o]); }
        if (kind === "tira") lista.unshift(lista[lista.length - 1]);
        function foto(i) { return imp(lista[(i - 1) % lista.length]); }
        if (kind === "carrusel") {
            // 3D: each slide swings in on Y (45 -> 0 deg, x 600 -> 540) and leaves to x 200 at -80 deg; one slide per named work
            var n = Math.min(5, Math.max(2, works.length));
            for (var i = 5; i >= 1; i--) {
                var L = capa(m, new RegExp("^Slide " + dos(i)));
                if (!L) continue;
                if (i > n) { L.remove(); continue; }
                var sd = L.source.duplicate(); sd.name = "Slide " + dos(i) + " · " + D.comp + " m" + nMod; sd.parentFolder = fold; L.replaceSource(sd, false); mono(sd);
                // the slide expressions read comp("Art Carousel (9x16)") by name: point them at this module
                reapuntar(sd, "Art Carousel (9x16)", m.name);
                var ft = foto(i), T2 = titulo(lista[(i - 1) % lista.length]);
                var art = capa(sd, /ARTWORK/);
                if (art && ft) {
                    art.replaceSource(ft, false);
                    // the template tuned each slide's "Image Size %" so its picture covers the frame: keep the same cover ratio
                    // for the new work (template pictures: garden 1920x1093, hell 1778x4324, haywain 1920x1263, temptation
                    // 1920x2683, ship 1540x2874)
                    var TW = [[1920, 1093], [1778, 4324], [1920, 1263], [1920, 2683], [1540, 2874]][i - 1], TS0 = [194, 128, 189, 113, 100][i - 1];
                    var cov = function (w, h) { return Math.max(1080 / w, 1920 / h); };
                    efecto(capa(m, /CAROUSEL CONTROLS/), dos(i) + " Image Size %").setValue(TS0 * cov(ft.width, ft.height) / cov(TW[0], TW[1]));
                }
                // light works take the template's own per-slide "Text Color" control set to ink
                if (CLARA[lista[(i - 1) % lista.length]]) efecto(capa(m, /CAROUSEL CONTROLS/), dos(i) + " Text Color").setValue(rgb(INK).concat([1]));
                setTexto(capa(sd, /^TITLE/), T2[0]); setTexto(capa(sd, /ARTIST/), T2[1] ? artista.replace(/·.*$/, "· " + T2[1]) : artista);
                // each slide lasts from its word to the next one: stretch the slide (its keys scale with it)
                // the last slide must not start its exit before the cut: its exit begins at 2.3 / 2.6 of the slide
                var t0 = i === 1 ? 0 : marks[i - 1], t1 = i < n ? marks[i] : t0 + (dur - t0) * 2.6 / 2.3 + 0.1, len = Math.max(0.8, t1 - t0);
                // the slide's keys are relative to its own start (template: start = in point)
                L.stretch = len / 2.6 * 100; L.startTime = t0; L.inPoint = t0; L.outPoint = t0 + len;
            }
        } else if (kind === "scroll") {
            // the desk: framed prints (cream border 26, shadow); the work in focus grows to 92%, the rest sit at 42%, tilted
            for (var i = 1; i <= 7; i++) {
                var im = capa(m, new RegExp("^Card " + dos(i) + " image")), ft = foto(i); if (im && ft) im.replaceSource(ft, false);
                setTexto(capa(m, new RegExp("^Card " + dos(i) + " title")), titulo(lista[(i - 1) % lista.length])[0]);
                var fr = capa(m, new RegExp("^Card " + dos(i) + " frame"));
                if (!im || !fr) continue;
                // the frame and title expressions were written for the template's pictures: size them to the new image
                var fit = Math.min(940 / im.source.width, 1420 / im.source.height), w = im.source.width * fit, h = im.source.height * fit;
                fr.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").expression =
                    "var b=thisComp.layer(\"SCROLL CONTROLS\").effect(\"Frame Border\")(\"Slider\"); [" + w.toFixed(1) + "+2*b, " + h.toFixed(1) + "+2*b];";
                var tl = capa(m, new RegExp("^Card " + dos(i) + " title"));
                if (tl) T(tl).property("ADBE Position").expression = "var b=thisComp.layer(\"SCROLL CONTROLS\").effect(\"Frame Border\")(\"Slider\"); [0, " + (h / 2).toFixed(1) + "+b+64, -1];";
            }
            efecto(capa(m, /SCROLL CONTROLS/), "Seconds per Artwork").setValue(works.length > 1 ? Math.max(1.2, marks[1] - 0.4) : 2.2);
            // stop on the last named work: the template's scroll never rests, so at the cut it was already sliding toward the next
            // print (a new image starting and cut away). Cap the scroll at the last work the voice names
            var sp = capa(m, /SCROLL CONTROLS/).property("ADBE Effect Parade").property("Scroll").property(1);
            sp.expression = sp.expression.replace(/Math\.min\(([^;]*), 6\)/, "Math.min($1, " + (works.length - 1) + ")");
        } else if (kind === "slider" || kind === "tira") {
            var maxc = kind === "slider" ? 5 : 7;
            for (var i = 1; i <= maxc; i++) {
                var L2 = capa(m, new RegExp("^Card " + dos(i) + " image")), ft2 = foto(i); if (L2 && ft2) L2.replaceSource(ft2, false);
                if (kind === "slider") { var TT = titulo(lista[(i - 1) % lista.length]); setTexto(capa(m, new RegExp("^Card " + dos(i) + " title")), TT[0]); setTexto(capa(m, new RegExp("^Card " + dos(i) + " date")), TT[1] || artista); }
            }
            // every card lives the whole module (the template trimmed them to its own timing)
            for (var i2 = 1; i2 <= m.numLayers; i2++) { var Lx = m.layer(i2); if (/^Card \d\d /.test(Lx.name)) { Lx.inPoint = 0; Lx.outPoint = m.duration; } }
            // Progress: hold on a card, then move to the next one, landing on the word that names it
            // (slider: 0.8 s, ease 90/60; strip: 0.7 s, ease 85/55)
            var pg = efecto(capa(m, /(SLIDER|STRIP) CONTROLS/), "Progress"), mv = kind === "slider" ? 0.8 : 0.7, p0 = kind === "slider" ? 0 : 1;
            while (pg.numKeys) pg.removeKey(1);
            var ts = [0], vs = [p0];
            for (var j = 1; j < works.length; j++) { var tm = Math.max(ts[ts.length - 1] + 0.2, marks[j] - mv); ts.push(tm, marks[j]); vs.push(p0 + j - 1, p0 + j); }
            if (ts.length === 1) { ts.push(Math.max(0.5, dur - mv), dur); vs.push(p0, p0 + 1); }
            keys(pg, ts, vs, kind === "slider" ? [[90, 60]] : [[85, 55]]);
        } else if (kind === "kenburns") {
            for (var i = 1; i <= 4; i++) { var L3 = capa(m, new RegExp("^" + dos(i) + " PAINTING")), ft3 = foto(i); if (L3 && ft3) L3.replaceSource(ft3, false); }
            efecto(capa(m, /KEN BURNS CONTROLS/), "Seconds per Painting").setValue(works.length > 1 ? marks[1] : dur);
        }
        // the template's black background becomes the head's background (review Blake v1: "the black background in those
        // transitions: shouldn't it be the head's background?")
        var bk = capa(m, /^BG black/);
        if (bk) { var fcm = fondoCabeza(m.duration, a, D.comp + " module " + nMod + " background"); var Lf = m.layers.add(fcm); Lf.moveAfter(bk); bk.remove(); }
        var Lm = c.layers.add(m); Lm.name = "MODULE " + kind; Lm.startTime = a; vida(Lm, a, b);
        cue(a, "swish", -10, "module " + kind);
        for (var k = 1; k < marks.length; k++) cue(a + marks[k], "tick", -14, "next work");
        return Lm;
    }
    // magnifier cards (template "Detail Zoom"): centred, the image covers the card then magnifies; pops 6% in 4 frames;
    // cream tape at the top edge (88%); black shadow blur 40, 22 px down, 45%
    var nCard = 0;
    function tarjeta(img, foco, mag, t, b, rot, w, h, minRel) {
        var it = imp(img); if (!it || b - t < 0.6) return;
        nCard++;
        var cx = W / 2, cy = H / 2, f4 = 4 / FPS;
        var sh = shp("card shadow " + nCard), gs = grp(sh, "s"); rect(gs, w, h, 0); fill(gs, "#000000");
        P(sh).setValue([cx, cy + 22]); R(sh).setValue(rot); O(sh).setValue(45); try { fx(sh, "ADBE Gaussian Blur 2").property(1).setValue(40); } catch (e) {}
        var L = c.layers.add(it); L.name = "CARD " + nCard; L.audioEnabled = false;
        // template: the image covers the card, then "Magnify x"
        var k = cover(it, w, h) * mag;
        A(L).setValue([foco[0] * it.width, foco[1] * it.height]); P(L).setValue([cx, cy]); R(L).setValue(rot);
        var m = shp("card matte " + nCard), gm = grp(m, "m"); rect(gm, w, h, 0); fill(gm, "#FFFFFF"); P(m).setValue([cx, cy]); R(m).setValue(rot);
        m.moveBefore(L); L.setTrackMatte(m, TrackMatteType.ALPHA);
        var tp = shp("card tape " + nCard), gt = grp(tp, "t"); rect(gt, 230, 72, 0); fill(gt, TAPE); O(tp).setValue(88);
        var ar = rot * Math.PI / 180, vy = -h / 2 + 6;
        P(tp).setValue([cx - vy * Math.sin(ar), cy + vy * Math.cos(ar)]); R(tp).setValue(rot + (rot < 0 ? -4 : 3));
        var grupo = [sh, L, m, tp];
        for (var i = 0; i < grupo.length; i++) {
            var G = grupo[i]; vida(G, t, b);
            // template "Pop In (frames)" = 0: the card is simply there on its word, no scale pop
            S(G).setValue(G === L ? [k, k] : [100, 100]);
        }
        cue(t, "pop", -8, "magnifier card");
    }
    function detalle(img, det, a, b, te) {
        // the work full bleed behind the cards (focus 50/45, 4% push); after the cards a reveal, then crops
        var it = imp(img); if (!it) return;
        plano(it, a, te, 1.0, 1.04, [0.5, 0.45], [0.5, 0.45]);
        for (var d = 0; d < det.length; d++) {
            var td = Math.max(a + 0.3, det[d].t || a + 0.4 + d * 1.6);
            tarjeta(img, det[d].foco, det[d].x, td, te, d % 2 ? 2 : -1.5, d % 2 ? 600 : 780, d % 2 ? 760 : 1040);
        }
        if (b - te > 0.4) {
            var tr = Math.min(b, te + 2.6);
            obra(img, te, tr, "revelado", det[det.length - 1].foco); cue(te, "swish", -10, "detail reveal");
            if (b - tr > 0.6) { obra(img, tr, b, "deriva", det[0].foco); cue(tr, "swish", -12, "crop"); }
        }
    }
    // ---------------- bricolage portrait card (template "Bricolage Portrait": positions, scales, moves and timings as built)
    function bricolage(sec) {
        var b = sec.fin, K = D.kit + "/", seed = 100;
        fondo(sec.ini, b);
        // the master cuts in 1.05 s into the module (template: start 4.1, in 5.153): papers already in, the cutout landing
        var a = sec.ini - 1.05;
        function cb(t, x, g, w) { if (t >= sec.ini - 0.01) cue(t, x, g, w); }
        function vb(L, t, e) { return vida(L, Math.max(t, sec.ini), e); }
        function pieza(file, x, y, sc, rot, t, modo, amp, extra) {
            var it = imp(K + file); if (!it) return null;
            var L = c.layers.add(it); L.name = "kit " + file.replace(".png", ""); P(L).setValue([x, y]); S(L).setValue([sc, sc]); R(L).setValue(rot);
            var t0 = a + t;
            if (modo === "pop") pop(L, t0, sc);
            else if (modo === "slide") slide(L, t0, extra, x, y);
            else if (modo === "drop") drop(L, t0, x, y, extra);
            else if (modo === "wipe") wipe(L, t0, extra);
            else if (modo === "grow") grow(L, t0, sc, extra, rot);
            else if (modo === "spin") spin(L, t0, sc, rot);
            vb(L, t0, b); jitter(L, t0 + 0.9, amp, seed++);
            if (modo === "drop") cb(t0 + 0.333, "hit", -6, "drop");
            else if (modo === "wipe") cb(t0, "tick", -14, "tape");
            else if (modo !== "slide") cb(t0, "pop", -14, "piece");
            return L;
        }
        pieza("J_paper_shapes_01.png", 540, 640, 223.5, 0, 0.10, "pop", 0.4);
        pieza("N_print_textures_03.png", 180, 360, 63.87, 10, 0.20, "slide", 0.6, 1581);
        pieza("N_print_textures_01.png", 880, 300, 80.43, -6, 0.25, "slide", 0.6, 1453);
        pieza("K_torn_paper_03.png", 820, 1260, 101.96, -8, 0.30, "slide", 0.6, 1590);
        pieza("J_paper_shapes_07.png", 230, 1180, 127.66, 6, 0.35, "slide", 0.5, 1362);
        pieza("K_torn_paper_05.png", 250, 1560, 75.16, -5, 0.40, "slide", 0.6, 1559);
        pieza("B_tape_yellow.png", 320, 260, 55.56, 18, 0.45, "wipe", 0.4, 270);
        pieza("B_tape_orange_creased.png", 930, 820, 75.61, -84, 0.50, "wipe", 0.4, 90);
        
        // the artist: photocopy bust placed like the template's (A_bosch_cutout 720 x 1075 at (540, 1030)): the head runs from
        // y 510 (top) to y 1080 (chin), so every artist's head has Bosch's size whatever the width of the figure.
        // The cutout drops 320 px into place at 0.70 s and bounces
        var ret = imp(D.retrato_bricolage);
        if (ret) {
            var Rt = c.layers.add(ret); Rt.name = "ARTIST CUTOUT";
            var kr = Math.min(720 / ret.width, 1075 / ret.height) * 100, yc = 1030, meta = null;
            try { var fm = new File(String(D.retrato_bricolage).replace(/\.png$/i, ".json")); if (fm.exists) { fm.open("r"); meta = eval("(" + fm.read() + ")"); fm.close(); } } catch (eM) {}
            // head size from the template (570 px top to chin); its height from the style ("retrato_cabeza_y", default Bosch's 510-1080):
            // CCC raises it to 280-850 so the bust sits on the paper circle and clears the social safe area
            var hy = (D.estilo && D.estilo.retrato_cabeza_y) || [510, 1080];
            if (meta && meta.chin > meta.head_top) { kr = (hy[1] - hy[0]) / (meta.chin - meta.head_top) * 100; yc = hy[0] + (ret.height / 2 - meta.head_top) * kr / 100; }
            S(Rt).setValue([kr, kr]); drop(Rt, a + 0.7, 540, yc, yc - 320); vb(Rt, a + 0.7, b); jitter(Rt, a + 1.6, 0.3, 77); cb(a + 1.03, "hit", -4, "cutout lands");
        }
        pieza("G_tape_tabs_01.png", 215, 1250, 52.2, -38, 1.15, "pop", 1);
        pieza("G_tape_tabs_07.png", 880, 1270, 33.19, 0, 1.20, "pop", 1);
        pieza("M_hardware_01.png", 860, 170, 37.46, 8, 1.25, "drop", 0.8, -150);
        pieza("F_price_tag.png", 300, 1470, 47.52, -18, 1.30, "grow", 1.4, -30);
        pieza("M_hardware_05.png", 250, 1400, 40.23, -10, 1.40, "drop", 0.8, 1080);
        // the name label: pink tape, then black tape with the name in cream caps, both wiping left to right at -3 degrees
        pieza("B_tape_pink_long.png", 520, 1640, 99.89, -3, 1.45, "wipe", 0.4, 270);
        var tb = imp(K + "B_tape_black.png");
        if (tb) {
            var nm = texto(String(D.etiqueta || D.artista).toUpperCase(), F_LABEL, 70, CREAM, ParagraphJustification.CENTER_JUSTIFY, 10); nm.name = "label name"; var rr = centrar(nm);
            var kn = Math.min(100, 640 / rr.width * 100); S(nm).setValue([kn, kn]);
            var Lb = c.layers.add(tb); Lb.name = "label tape"; S(Lb).setValue([(rr.width * kn / 100 + 140) / tb.width * 100, 130 / tb.height * 100]);
            P(Lb).setValue([540, 1640]); R(Lb).setValue(-3); Lb.moveAfter(nm);
            wipe(Lb, a + 1.6, 270); vb(Lb, a + 1.6, b); jitter(Lb, a + 2.5, 0.4, 55);
            P(nm).setValue([540, 1640]); R(nm).setValue(-3); wipe(nm, a + 1.68, 270); vb(nm, a + 1.68, b); jitter(nm, a + 2.5, 0.4, 55);
            cb(a + 1.6, "tick", -10, "name label");
        }
        pieza("L_stickers_02.png", 960, 1490, 32.26, 0, 1.85, "pop", 1.2);
        pieza("L_stickers_14.png", 130, 1790, 43.86, 8, 1.90, "spin", 1.4);
        var st = pieza("L_stickers_16.png", 930, 1800, 55.71, 0, 1.95, "pop", 1.2);
        if (st) slide(st, a + 1.95, 510, 930, 1800);
        pieza("H_marker_scribbles_12.png", 880, 570, 42.06, 0, 2.00, "pop", 2);
        pieza("D_mark_num1.png", 95, 150, 26.63, 0, 2.05, "pop", 2);
        pieza("D_mark_x_pink.png", 965, 140, 28.57, 0, 2.10, "pop", 2);
        pieza("N_print_textures_07.png", 540, 1880, 25.89, 0, 2.15, "pop", 1.5);
    }
    // ---------------- quote card (template "Quote"): torn strips wipe left to right, words fade up (blur 8, 24 px), ~0.8 s per line
    function cita(sec) {
        var a = sec.ini, b = sec.fin, lin = sec.cita || [], K = D.kit + "/", seed = 400;
        fondo(a, b);
        function pieza(file, x, y, sc, rot, t, modo, amp, extra) {
            var it = imp(K + file); if (!it) return null;
            var L = c.layers.add(it); L.name = "quote " + file.replace(".png", ""); P(L).setValue([x, y]); S(L).setValue([sc, sc]); R(L).setValue(rot);
            var t0 = a + t;
            if (modo === "pop") pop(L, t0, sc); else if (modo === "slide") slide(L, t0, extra, x, y); else if (modo === "drop") drop(L, t0, x, y, extra);
            else if (modo === "wipe") wipe(L, t0, 270); else if (modo === "grow") grow(L, t0, sc, -12, rot); else if (modo === "spin") spin(L, t0, sc, rot);
            vida(L, t0, b); jitter(L, t0 + 0.9, amp, seed++); return L;
        }
        pieza("J_paper_shapes_01.png", 900, 330, 160.46, 0, 0.0, "pop", 0.4);
        pieza("N_print_textures_01.png", 210, 300, 96.5, -6, 0.02, "slide", 0.6, 1453);
        pieza("B_tape_yellow.png", 520, 500, 75.4, -12, 0.04, "wipe", 0.4);
        pieza("H_marker_scribbles_05.png", 930, 640, 39.9, 0, 0.06, "grow", 1.6);
        var qm = texto("“", F_QUOTE, 520, PAPER); qm.name = "quote mark"; centrar(qm); P(qm).setValue([175, 690]); R(qm).setValue(-8);
        pop(qm, a + 0.08, 100); vida(qm, a + 0.08, b); jitter(qm, a + 0.98, 0.6, seed++); cue(a + 0.08, "pop", -10, "quote mark");
        pieza("G_tape_tabs_01.png", 150, 770, 37.36, 40, 0.3, "pop", 1);
        pieza("M_hardware_01.png", 640, 690, 34.58, 6, 0.5, "drop", 0.8, 370);
        var Y = [800, 960, 1120, 1280], X = [560, 565, 530, 560], ROT = [-2.2, 1.4, -1.1, 1.8], TS = [0.1, 0.88, 1.78, 2.4];
        var n = Math.min(lin.length, 4), span = b - a, k1 = span < 5.5 ? Math.max(0.5, (span - 1.8) / 2.4) : 1;
        for (var i = 0; i < n; i++) {
            var ty = a + TS[i] * k1, y = Y[i];
            var L = texto(lin[i], F_QUOTE, 112, INK, ParagraphJustification.CENTER_JUSTIFY, -10); L.name = "quote line " + (i + 1); var r = centrar(L);
            var kq = Math.min(100, 900 / r.width * 100); S(L).setValue([kq, kq]); P(L).setValue([X[i], y]); R(L).setValue(ROT[i]);
            var st = imp(K + "K_torn_paper_06.png");
            if (st) {
                var Sx = c.layers.add(st); Sx.name = "paper strip " + (i + 1);
                S(Sx).setValue([(r.width * kq / 100 + 110) / st.width * 100, 155 / st.height * 100]); P(Sx).setValue([X[i], y + 6]); R(Sx).setValue(ROT[i]); Sx.moveAfter(L);
                wipe(Sx, ty, 270); vida(Sx, ty, b); jitter(Sx, ty + 0.9, 0.5, 500 + i);
            }
            vida(L, ty + 0.15, b); jitter(L, ty + 0.9, 0.5, 500 + i);
            var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"); an.name = "words fade up";
            var pr = an.property("ADBE Text Animator Properties");
            pr.addProperty("ADBE Text Position 3D").setValue([0, 24, 0]); pr.addProperty("ADBE Text Opacity").setValue(0); pr.addProperty("ADBE Text Blur").setValue([8, 8]);
            var sl = an.property("ADBE Text Selectors").addProperty("ADBE Text Selector"), adv = sl.property("ADBE Text Range Advanced");
            adv.property("ADBE Text Range Type2").setValue(3); adv.property("ADBE Text Range Shape").setValue(2);
            sl.property("ADBE Text Percent End").setValue(35);
            keys(sl.property("ADBE Text Percent Offset"), [ty + 0.15, ty + 0.15 + 1.1 * k1], [-35, 100], [[17, 30], [90, 17]]);
            cue(ty, "tick", -14, "strip");
        }
        var ya = 1500, tt = a + 2.55 * k1;
        var au = texto(String(sec.autor || "").replace(/^[—\-\s�]+/, "— ").toUpperCase(), F_BRAND, 40, PAPER, ParagraphJustification.CENTER_JUSTIFY, 40); au.name = "attribution";
        var ra = centrar(au), ka = Math.min(100, 860 / ra.width * 100); S(au).setValue([ka, ka]);
        var tb = imp(K + "B_tape_black.png");
        if (tb) { var Tb = c.layers.add(tb); Tb.name = "attribution tape"; S(Tb).setValue([(ra.width * ka / 100 + 120) / tb.width * 100, 89.9]); P(Tb).setValue([540, ya]); R(Tb).setValue(1.5); Tb.moveAfter(au); wipe(Tb, tt, 270); vida(Tb, tt, b); jitter(Tb, tt + 0.9, 0.4, 600); }
        P(au).setValue([540, ya]); R(au).setValue(1.5); vida(au, tt + 0.1, b); keys(O(au), [tt + 0.1, tt + 0.4], [0, 100]);
        pieza("L_stickers_06.png", 870, 1330, 67.4, -14, tt - a - 0.05, "spin", 1.6);
        pieza("L_stickers_14.png", 160, 1760, 43.86, -8, tt - a + 0.2, "spin", 1.4);
        pieza("L_stickers_02.png", 930, 1700, 32.26, 0, tt - a + 0.3, "pop", 1.2);
    }
    // ---------------- captions: 2-4 words, Poppins SemiBold 66, cream with a 10 px dark stroke, the spoken word amber
    function subtitulos(fichas, citas) {
        for (var i = 0; i < D.subs.length; i++) {
            var s = D.subs[i], ws = [], S0 = [];
            for (var j = 0; j < s.words.length; j++) { ws.push(s.words[j].w); S0.push(s.words[j].s.toFixed(3)); }
            var L = c.layers.addText(ws.join(" ")), p = L.property("ADBE Text Properties").property("ADBE Text Document"), d = p.value;
            d.resetCharStyle(); d.font = F_CAP; d.fontSize = 66; d.applyFill = true; d.fillColor = rgb(CREAM);
            d.applyStroke = true; d.strokeColor = rgb(STROKE); d.strokeWidth = 10; d.strokeOverFill = false;
            d.justification = ParagraphJustification.CENTER_JUSTIFY; d.tracking = 0; p.setValue(d);
            L.name = "CAP " + (i + 1); centrar(L);
            var r = L.sourceRectAtTime(0, false); if (r.width > 940) { var k = 940 / r.width * 100; S(L).setValue([k, k]); }
            var y = 1503;
            for (var f = 0; f < fichas.length; f++) if (s.ini >= fichas[f][0] - 0.05 && s.ini < fichas[f][1]) y = 1835;
            P(L).setValue([W / 2, y]);
            var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            an.name = "highlight"; an.property("ADBE Text Animator Properties").addProperty("ADBE Text Fill Color").setValue(rgb(AMBER));
            var sl = an.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sl.property("ADBE Text Range Type2").setValue(3);
            sl.property("ADBE Text Expressible Amount").expression = "var S=[" + S0.join(",") + "], cur=-1; for (var q=0;q<S.length;q++) if (time>=S[q]) cur=q; (textIndex-1)===cur?100:0;";
            // no captions over the quote card (template: the captions stop while the quote is on screen)
            var fin = s.fin, ini = s.ini;
            for (var q2 = 0; q2 < citas.length; q2++) { if (ini < citas[q2][0] && fin > citas[q2][0]) fin = citas[q2][0]; if (ini >= citas[q2][0] && ini < citas[q2][1]) fin = ini; }
            if (fin - ini < 0.1) { L.remove(); continue; }
            vida(L, ini, fin);
        }
    }
    // ---------------- "Comment below" button (template EL button): a cream pill grows from the left in 0.7 s (ease 70/70) while the
    // amber letters rise in (y +50, scale 118%, opacity 0); 1 s later it is pressed (6% smaller for 4 frames) and turns dark
    function boton(t) {
        if (!t || t > DUR - 0.5) return;
        var y = 1641, L = texto("Comment below", F_CTA, 50, AMBER, ParagraphJustification.CENTER_JUSTIFY, -10); L.name = "CTA text"; var r = centrar(L);
        var w = r.width + 56, h = r.height + 32, tp = t + 1.26;
        var pill = shp("CTA pill"), g = grp(pill, "p"), re = rect(g, w, h, 999), fl = fill(g, CREAM);
        P(pill).setValue([W / 2, y]); P(L).setValue([W / 2, y]);
        // adding the fill invalidated the earlier references: fetch them again
        var vg = pill.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group");
        re = vg.property("ADBE Vector Shape - Rect"); fl = vg.property("ADBE Vector Graphic - Fill");
        keys(re.property("ADBE Vector Rect Size"), [t, t + 0.7], [[0, h], [w, h]], [[17, 70], [70, 17]]);
        keys(re.property("ADBE Vector Rect Position"), [t, t + 0.7], [[-w / 2, 0], [0, 0]], [[17, 70], [70, 17]]);
        fl.property("ADBE Vector Fill Color").setValueAtTime(t, rgb(CREAM)); fl.property("ADBE Vector Fill Color").setValueAtTime(tp, rgb(STROKE));
        fl.property("ADBE Vector Fill Color").setInterpolationTypeAtKey(1, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"); an.name = "chars rise";
        var pr = an.property("ADBE Text Animator Properties");
        pr.addProperty("ADBE Text Position 3D").setValue([0, 50, 0]); pr.addProperty("ADBE Text Scale 3D").setValue([118, 118, 100]); pr.addProperty("ADBE Text Opacity").setValue(0);
        var sl = an.property("ADBE Text Selectors").addProperty("ADBE Text Selector"), adv = sl.property("ADBE Text Range Advanced"); adv.property("ADBE Text Range Shape").setValue(2);
        sl.property("ADBE Text Percent End").setValue(30);
        keys(sl.property("ADBE Text Percent Offset"), [t + 0.1, t + 0.8], [-30, 100], [[17, 30], [90, 17]]);
        var grupo = [pill, L];
        for (var i = 0; i < grupo.length; i++) { keys(S(grupo[i]), [tp - 0.133, tp, tp + 0.007, tp + 0.307], [[100, 100], [94, 94], [94, 94], [100, 100]]); vida(grupo[i], t, DUR); }
        pill.moveAfter(L); pill.motionBlur = true; L.motionBlur = true;
        cue(t, "swish", -14, "CTA in"); cue(tp, "click", -8, "CTA press");
    }
    function build(datos) {
        D = datos; DUR = D.total; CUES = []; nCard = 0; nMod = 0; TPLF = null;
        var tk = (D.estilo && D.estilo.tokens) || {}; CREAM = tk.texto || CREAM; AMBER = tk.acento || AMBER;
        // Poppins is the template font; this After Effects reads only fonts installed for all users, so fall back to Inter Tight
        function hay(ps) { try { var f = app.fonts.getFontsByPostScriptName(ps); return f && f.length > 0; } catch (e) { return true; } }
        if (!hay(F_CAP)) { F_CAP = "InterTight-SemiBold"; F_CTA = "InterTight-Bold"; F_LABEL = "InterTight-ExtraBold"; CUES.push("WARN;Poppins not installed for all users: captions in Inter Tight"); }
        for (var i = app.project.numItems; i >= 1; i--) { var it0 = app.project.item(i); if ((it0 instanceof CompItem && it0.name.indexOf(D.comp) === 0) || (it0 instanceof FolderItem && it0.name === D.comp + " media") || (it0 instanceof FootageItem && it0.file && it0.file.fsName.indexOf(D.comp) >= 0 && it0.file.fsName.indexOf("_mdna_sound") >= 0)) it0.remove(); }
        fold = app.project.items.addFolder(D.comp + " media"); cache = {};
        c = app.project.items.addComp(D.comp, W, H, 1, DUR, FPS); c.motionBlur = true; c.shutterAngle = 180;
        // under everything: the head's background, never black
        var Lbg = c.layers.add(fondoCabeza(DUR, 0, D.comp + " background")); Lbg.name = "Background";
        var S0 = D.secciones, ctaT = null, ultDet = null, fichas = [], citas = [], nRun = 0;
        var MODS = (D.estilo && D.estilo.modulos_obra) || ["carrusel", "scroll", "slider", "tira"];
        // the ending tail: the last host shot runs to the end of the video
        var ult = S0[S0.length - 1]; if (ult && (ult.tipo === "cabeza" || ult.tipo === "gancho")) ult.fin = DUR;
        CLARA = {}; for (var zc = 0; zc < S0.length; zc++) if (S0[zc].img && S0[zc].clara) CLARA[S0[zc].img] = true;
        // no work on screen for less than 1.2 s (the template's shortest shot is 1.17 s): a shorter work takes time from the
        // portrait card before it (kept at 3.45 s or more, the template's on-screen time) so it never flashes and cuts away
        for (var zs = 1; zs < S0.length; zs++) {
            var sw = S0[zs], pv = S0[zs - 1];
            if (sw.img && sw.tipo === "obra" && sw.fin - sw.ini < 1.2 && pv.tipo === "ficha") {
                var nb = Math.max(pv.ini + 3.45, Math.min(sw.ini, sw.fin - 2.2));
                if (nb < sw.ini) { pv.fin = nb; sw.ini = nb; }
            }
        }
        for (i = 0; i < S0.length; i++) {
            var s = S0[i];
            if (i) cue(s.ini, "swish", -10, "cut to " + s.tipo);
            if (s.tipo === "gancho" || s.tipo === "cabeza") {
                anfitrion(s);
                // works named while she talks: cut to them (magnifier cards when the project marks details), then back
                var ob = s.obras || [];
                for (var j = 0; j < ob.length; j++) {
                    // cut to the work when the word that names it ENDS (Blake v1: "Look closely" was cut before "closely"), and keep
                    // at least 1.2 s of the host first
                    var a = Math.max(s.ini + 1.2, finPalabra(ob[j].t) + 0.05), b = Math.min(s.fin - 0.4, j + 1 < ob.length ? ob[j + 1].t : 1e9);
                    var det = (D.detalles || {})[ob[j].stem];
                    if (det && det.length) {
                        b = s.fin;
                        if (b - a < 1.6) continue;
                        var tl = 0; for (var d0 = 0; d0 < det.length; d0++) tl = Math.max(tl, det[d0].t || 0);
                        var te = Math.min(b, Math.max(a + 2.5, tl + 2.6));
                        detalle(ob[j].img, det, a, b, te);
                        cue(a, "swish", -10, "detail zoom"); ultDet = ob[j].stem;
                    } else if (s.tipo === "gancho") {
                        continue;
                    } else {
                        if (b - a < 1.2) continue;
                        obra(ob[j].img, a, Math.min(b, a + 2.4), "deriva"); cue(a, "swish", -10, "work in");
                    }
                }
                if (i === S0.length - 1) {
                    for (var u = 0; u < D.subs.length && ctaT === null; u++) for (var w = 0; w < D.subs[u].words.length; w++) { var ww = D.subs[u].words[w]; if (ww.s >= s.ini && /comment/i.test(ww.w)) { ctaT = ww.s; break; } }
                    if (ctaT === null) ctaT = Math.max(s.ini, s.fin - 2.5);
                }
            } else if (s.tipo === "ficha") { bricolage(s); fichas.push([s.ini, s.fin]); }
            else if (s.tipo === "cita") { cita(s); citas.push([s.ini, s.fin]); }
            else if (s.img) {
                if (s.revelado || (ultDet && s.stem === ultDet)) { obra(s.img, s.ini, s.fin, "revelado"); ultDet = null; continue; }
                // a run of consecutive works becomes one of the template's art modules when it lasts 3 s or more
                var run = [s], j2 = i + 1;
                while (j2 < S0.length && S0[j2].img && S0[j2].tipo === "obra" && !S0[j2].revelado && S0[j2].ini - S0[j2 - 1].fin < 0.05) { run.push(S0[j2]); j2++; }
                var rd = run[run.length - 1].fin - run[0].ini;
                if (rd >= 3 && MODS.length) {
                    var kind = MODS[(nRun++ + Math.max(0, (parseInt(D.numero, 10) || 1) - 1)) % MODS.length], ws = [], mk = [];
                    for (var r = 0; r < run.length; r++) { ws.push(run[r].img); mk.push(run[r].ini - run[0].ini); }
                    if (!modulo(kind, ws, mk, run[0].ini, run[run.length - 1].fin)) for (var r2 = 0; r2 < run.length; r2++) obra(run[r2].img, run[r2].ini, run[r2].fin, "deriva");
                    i = j2 - 1;
                } else obra(s.img, s.ini, s.fin, "deriva");
            }
        }
        // drop what the episode does not use from the imported template (its own comps keep the commercial font and old footage)
        if (TPLF) {
            for (var pas = 0; pas < 6; pas++) {
                var quito = 0;
                for (var z = app.project.numItems; z >= 1; z--) { var itz = app.project.item(z); if (!(itz instanceof FolderItem) && enCarpeta(itz, TPLF) && itz.usedIn.length === 0) { itz.remove(); quito++; } }
                if (!quito) break;
            }
            for (var z2 = app.project.numItems; z2 >= 1; z2--) { var fz = app.project.item(z2); if (fz instanceof FolderItem && enCarpeta(fz, TPLF) && fz.numItems === 0) fz.remove(); }
        }
        // motion blur on every layer that moves (kit pieces, cutout, strips, cards, works, modules, host plate jumps); not on the
        // captions (they swap, they don't move), the solids or the audio. Shutter 180, as the template's art modules
        for (var zb = 1; zb <= c.numLayers; zb++) {
            var lb = c.layer(zb);
            if (!lb.hasVideo || /^(Background|BG )/.test(lb.name)) continue;
            try { if (lb.source && lb.source.mainSource instanceof SolidSource) continue; } catch (eB) {}
            try { lb.motionBlur = true; } catch (eB2) {}
        }
        subtitulos(fichas, citas);
        boton(ctaT);
        for (i = 0; i < D.voces.length; i++) { var V = c.layers.add(imp(D.voces[i].wav)); V.name = D.voces[i].id + " voice"; V.startTime = D.voces[i].start; }
        return "ok " + c.numLayers + " layers\n" + CUES.join("\n");
    }
    return { build: build };
})();
