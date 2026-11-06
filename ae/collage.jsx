// Art-collage Short in After Effects (style collage_v10c). Called by engine/build_collage.py with the data of one video
// (datos_ae.json): COLLAGE.build(datos). Comments are in Spanish (the language it was built in); docs/STYLE_COLLAGE.md explains the
// style and docs/LEARNINGS.md every rule that came from a review.
// v9: obras en la palabra que las nombra y con tiempo para verse; la cabeza sale con corte tapado por franjas; sonido.
// Base v8: la obra entra cuando ella la nombra; obras sin intervenir; cabeza hasta el final; transiciones suaves; direcciones variadas.
// Base v7: proporcion y balance (ejemplo del usuario): la cabeza enorme con la palabra gigante detras; la obra a sangre con un acento.
// Base v6: cabeza al centro con la obra grande detras; obras grandes en marco, circulo o pincelada; ficha con silueta; cita en oscuro.
// Base: v5 del collage con cabeza flotante: la cabeza solo cuando habla; en la voz en off la obra es la protagonista, con movimiento ambiente
// medido contra el referente (corrientes, capsula viva, lapiz que redibuja, empuje 2.5D, pigmento, reordenar, franjas). Datos de build_collage5.py.
// Un tablero de puntos (uno por seccion) recorrido por la camara CAM; cada capa se coloca en coordenadas de pantalla de su punto y
// tab() la mueve con la camara (parallax solo en los latigos). Ver assets_motion_health_care/tests_ae/tratamientos2/RECETAS_tratamientos2.md.
var COLLAGE = (function () {
    var ROOT = "", G = "";   // carpeta del kit (library/kit/), la pone build() desde los datos
    var W = 1080, H = 1920, FPS = 30, DUR = 10;
    var INK = "#191D1D", PAPEL = "#F7F8F4", TEAL = "#6FAFA8", MINT = "#3ECCB0", MAG = "#E6128F", LIME = "#C1F157", OCRE = "#B8945A", SLATE = "#9FB5AE";
    var cache = {}, fold, c, D, MC, MG, nLupa = 0, nObra = 0, FONDOS = ["#2E6F66", "#7A2550", "#3D5A3A"];
    function rgb(h) { h = h.replace("#", ""); return [parseInt(h.substr(0, 2), 16) / 255, parseInt(h.substr(2, 2), 16) / 255, parseInt(h.substr(4, 2), 16) / 255]; }
    function imp(p, recta) {
        if (cache[p] !== undefined) return cache[p];
        var f = new File(p.indexOf(":") > 0 ? p : ROOT + p);
        if (!f.exists) { cache[p] = null; return null; }
        var it = app.project.importFile(new ImportOptions(f)); it.parentFolder = fold;
        if (recta && it.mainSource.hasAlpha) it.mainSource.alphaMode = AlphaMode.STRAIGHT;
        cache[p] = it; return it;
    }
    function T(L) { return L.property("ADBE Transform Group"); }
    function P(L) { return T(L).property("ADBE Position"); }
    function S(L) { return T(L).property("ADBE Scale"); }
    function R(L) { return T(L).property("ADBE Rotate Z"); }
    function O(L) { return T(L).property("ADBE Opacity"); }
    function fx(L, n) { return L.property("ADBE Effect Parade").addProperty(n); }
    function vec(g) { return g.property("ADBE Vectors Group"); }
    function shp(n) { var L = c.layers.addShape(); L.name = n; return L; }
    function grp(L, n) { var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); g.name = n; return g; }
    function ell(g, w, h) { vec(g).addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([w, h]); }
    function rect(g, w, h, r) { var e = vec(g).addProperty("ADBE Vector Shape - Rect"); e.property("ADBE Vector Rect Size").setValue([w, h]); e.property("ADBE Vector Rect Roundness").setValue(r || 0); return e; }
    function fill(g, col) { vec(g).addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(rgb(col)); }
    function stroke(g, col, w) { var s = vec(g).addProperty("ADBE Vector Graphic - Stroke"); s.property("ADBE Vector Stroke Color").setValue(rgb(col)); s.property("ADBE Vector Stroke Width").setValue(w); return s; }
    function linea(g, pts, cerrada) { var p = vec(g).addProperty("ADBE Vector Shape - Group"), s = new Shape(); s.vertices = pts; s.closed = !!cerrada; p.property("ADBE Vector Shape").setValue(s); }
    function trim(g) { return vec(g).addProperty("ADBE Vector Filter - Trim"); }
    function mult(L, op) { L.blendingMode = BlendingMode.MULTIPLY; if (op !== undefined) O(L).setValue(op); return L; }
    function vida(L, a, b) { L.inPoint = Math.max(0, a); L.outPoint = Math.min(DUR, b); return L; }
    function foto(L, con, neg, cla) { var t = fx(L, "ADBE Tint"); t.property(1).setValue(rgb(neg || "#000000")); t.property(2).setValue(rgb(cla || "#FFFFFF")); fx(L, "ADBE Brightness & Contrast 2").property(2).setValue(con === undefined ? 60 : con); return L; }
    function aspero(L, b, esc, f) { var r = fx(L, "ADBE Roughen Edges"); r.property("Border").setValue(b); r.property("Scale").setValue(esc || 60); r.property("Evolution").expression = "posterizeTime(" + (f || 8) + "); time*360;"; return L; }
    function hervor(L, f, amp) { R(L).expression = "posterizeTime(" + (f || 6) + "); seedRandom(" + L.index + ",false); value+random(-" + (amp || 1.5) + "," + (amp || 1.5) + ");"; return L; }
    // ExtendScript falla al pasar a texto algunos decimales y los Array: siempre numeros sueltos y redondeados
    function kf(k) { return (Math.round(((k || 1) - 1) * 1000) / 1000).toFixed(3); }
    function sp(s) { return D.secciones[s].spot[0] + "," + D.secciones[s].spot[1]; }
    // base puede traer sentencias ("var u=...; [x, y]"): van fuera del parentesis; dentro fallaban y la capa se quedaba en su valor (v4/v5, LEARNINGS)
    function exprTab(s, k, base) {
        var i = base.lastIndexOf(";"), pre = i >= 0 ? base.substr(0, i + 1) + " " : "", val = i >= 0 ? base.substr(i + 1) : base;
        return "var d=thisComp.layer('CAM').transform.position-[" + W / 2 + "," + H / 2 + "]; var sp=[" + sp(s) + "]; " + pre + "var b=(" + val + "); b+sp-d-(d-sp)*(" + kf(k) + ");";
    }
    function tab(L, x, y, s, k) {
        var o = D.secciones[s].spot; P(L).setValue([x + o[0], y + o[1]]);
        P(L).expression = "var d=thisComp.layer('CAM').transform.position-[" + W / 2 + "," + H / 2 + "]; var s=[" + sp(s) + "]; value-d-(d-s)*(" + kf(k) + ");";
        L.motionBlur = true; return L;
    }
    function sat(L, v) { var h = fx(L, "ADBE HUE SATURATION"); try { h.property("Master Saturation").setValue(v); } catch (e) { h.property(4).setValue(v); } return h; }
    function nulo(n) { var L = c.layers.addNull(); L.name = n; T(L).property("ADBE Anchor Point").setValue([0, 0]); return L; }
    // vida de una seccion: medio segundo antes y despues; con los puntos a 1400 x 2200 px nada se ve desde otro punto
    var DERIVA = [[12, 9], [-12, 7], [10, -8], [-9, -9]];   // v8: la deriva cambia de direccion en cada seccion
    // personaje sin boca: si la voz dura mas que el clip, el clip va y vuelve (ping-pong) en vez de congelarse
    function vaiven(L) { L.timeRemapEnabled = true; L.property("ADBE Time Remapping").expression = "var d=source.duration-0.05, t=Math.max(0,time-thisLayer.startTime), n=Math.floor(t/d), r=t%d; (n%2)? d-r : r;"; return L; }
    function congelar(L) { L.timeRemapEnabled = true; L.property("ADBE Time Remapping").expression = "Math.min(time - thisLayer.startTime, source.duration - 0.05);"; return L; }
    // entrada suave de una obra: aparece y se asienta (sin el golpe de escala)
    function suave(L, t, d) { var o = O(L), v0 = o.numKeys ? 100 : o.value; o.setValueAtTime(t, 0); o.setValueAtTime(t + (d || 0.4), v0); if (L.inPoint < t) L.inPoint = t; return L; }
    function viva(s) { var q = D.secciones[s]; return [Math.max(0, q.ini - 1.25), Math.min(DUR, q.fin + 0.1)]; }   // v10c: vive desde que empieza el deslizamiento (1.2 s) y se va al llegar a la siguiente   // v10b: 0.8 s (antes 0.45) para que el paso de camara sea mas lento
    function pon(p, s, x, y, ancho, k, rot, recta) {
        var it = imp(p, recta !== false); if (!it) return null;
        var L = c.layers.add(it); var e = ancho / it.width * 100; S(L).setValue([e, e]); if (rot) R(L).setValue(rot);
        tab(L, x, y, s, k); var v = viva(s); vida(L, v[0], v[1]); return L;
    }
    function vivo(n, quieto, s, x, y, ancho, k, rot) {
        var it = imp(G + "animados3/mate_" + n + ".mov", true) || imp(G + "animados/mate_" + n + ".mov", true);
        if (!it) { var q = imp(G + "alfa3/" + quieto + ".png", true) ? G + "alfa3/" + quieto + ".png" : G + "alfa/" + quieto + ".png"; return pon(q, s, x, y, ancho, k, rot); }
        var L = c.layers.add(it), e = ancho * 1.25 / it.width * 100; S(L).setValue([e, e]); if (rot) R(L).setValue(rot); tab(L, x, y, s, k);
        L.timeRemapEnabled = true; L.property("ADBE Time Remapping").expression = "posterizeTime(8); time % (source.duration - 0.1);";
        var v = viva(s); vida(L, v[0], v[1]); return L;
    }
    function caer(L, t) { var e = S(L), v = e.value; e.setValueAtTime(t, [v[0] * 0.6, v[1] * 0.6]); e.setValueAtTime(t + 4 / FPS, [v[0] * 1.08, v[1] * 1.08]); e.setValueAtTime(t + 7 / FPS, [v[0], v[1]]); if (L.inPoint < t) L.inPoint = t; return L; }
    function texto(str, font, size, col, just) {
        var L = c.layers.addText(str), pr = L.property("ADBE Text Properties").property("ADBE Text Document"), d = pr.value;
        d.resetCharStyle(); d.font = font; d.fontSize = size; d.applyFill = true; d.fillColor = rgb(col); d.applyStroke = false;
        d.justification = just || ParagraphJustification.CENTER_JUSTIFY; pr.setValue(d); return L;
    }
    function centrar(L) { var r = L.sourceRectAtTime(0, false); T(L).property("ADBE Anchor Point").setValue([r.left + r.width / 2, r.top + r.height / 2]); return r; }
    function medir(que, s, t, x, y, w, h, rot) { D.medidas.push(que + "|" + s + "|" + t + "|" + x + "|" + y + "|" + Math.round(w) + "|" + Math.round(h) + "|" + (rot || 0)); }

    // ---------- piezas
    function etiqueta(s, x, y, str, t, rot, size, cta, fin) {
        var v = viva(s); if (fin) v = [v[0], fin];   // v10b: fin propio (en una linea unida a la voz en off se va antes)
        var nul = nulo("etiqueta " + str); tab(nul, x, y, s, 1.02); vida(nul, t, v[1]);
        var tl = texto(str.toUpperCase(), "Impact", size || 58, cta ? INK : "#FFFFFF"), r = centrar(tl);
        var w = r.width + 70, h = r.height + 40;
        var bar = shp("barra etiqueta"), bg = grp(bar, "b"); linea(bg, [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2 - 14, h / 2], [-w / 2 - 14, h / 2]], true); fill(bg, cta ? LIME : INK);
        var cap = shp("capsula etiqueta"), cg = grp(cap, "c"); rect(cg, w + 34, h + 30, (h + 30) / 2); stroke(cg, INK, 12); fill(cg, PAPEL);
        cap.parent = nul; bar.parent = nul; tl.parent = nul; P(cap).setValue([0, 0]); P(bar).setValue([0, 0]); P(tl).setValue([0, 0]);
        vida(cap, t, v[1]); vida(bar, t, v[1]); vida(tl, t, v[1]); cap.moveAfter(bar); tl.moveBefore(bar);
        R(nul).setValue(rot || 0); S(nul).setValueAtTime(t, [0, 0]); S(nul).setValueAtTime(t + 4 / FPS, [110, 110]); S(nul).setValueAtTime(t + 7 / FPS, [100, 100]);
        if (cta) S(nul).expression = "var b=Math.max(0,time-" + (t + 0.4) + "); var p=1+0.04*Math.sin(b*6)*(b>0?1:0); value*p;";
        medir("etiqueta " + str, s, t, x, y, w + 34, h + 30, rot);
        return nul;
    }
    function cartela(s, x, y, titulo, lineas, t, rot) {
        var v = viva(s), nul = nulo("cartela"); tab(nul, x, y, s, 1); vida(nul, t, v[1]);
        if (titulo.length > 22) { var cu = titulo.lastIndexOf(" ", Math.ceil(titulo.length / 2) + 3); if (cu > 0) titulo = titulo.substr(0, cu) + "\r" + titulo.substr(cu + 1); }
        var tt = texto(titulo, "InstrumentSerif-Italic", 46, INK, ParagraphJustification.LEFT_JUSTIFY), lt = texto(lineas.join("\r"), "CourierNewPS-BoldMT", 34, INK, ParagraphJustification.LEFT_JUSTIFY);
        var d = lt.property("ADBE Text Properties").property("ADBE Text Document").value; d.autoLeading = false; d.leading = 42; lt.property("ADBE Text Properties").property("ADBE Text Document").setValue(d);
        var r1 = tt.sourceRectAtTime(0, false), r2 = lt.sourceRectAtTime(0, false);
        var w = Math.max(r1.width, r2.width) + 64, h = r1.height + r2.height + 22 + 56;
        if (x - w / 2 < 52) { x = 52 + w / 2; P(nul).setValue([x + D.secciones[s].spot[0], y + D.secciones[s].spot[1]]); }   // pegada al margen izquierdo, nunca fuera
        if (y + h / 2 > 1322) { y = 1322 - h / 2; P(nul).setValue([x + D.secciones[s].spot[0], y + D.secciones[s].spot[1]]); }
        var hoja = shp("hoja cartela"), hg = grp(hoja, "h"); rect(hg, w, h, 4); fill(hg, "#FBFBF6"); stroke(hg, INK, 2);
        hoja.parent = nul; P(hoja).setValue([0, 0]);
        tt.parent = nul; P(tt).setValue([-w / 2 + 32 - r1.left, -h / 2 + 28 - r1.top]);
        lt.parent = nul; P(lt).setValue([-w / 2 + 32 - r2.left, -h / 2 + 28 + r1.height + 22 - r2.top]);
        vida(hoja, t, v[1]); vida(tt, t, v[1]); vida(lt, t, v[1]); tt.moveBefore(hoja); lt.moveBefore(hoja);
        var pin = imp(G + "alfa3/cinta.png", true);
        if (pin) for (var i = 0; i < 2; i++) { var pl = c.layers.add(pin); pl.parent = nul; S(pl).setValue([96 / pin.width * 100, 96 / pin.width * 100]); P(pl).setValue([(i ? 1 : -1) * (w / 2 - 10), -h / 2 + 4]); R(pl).setValue(i ? 38 : -34); mult(pl, 85); vida(pl, t + 0.1, v[1]); }
        R(nul).setValue(rot || 0); S(nul).setValueAtTime(t, [92, 92]); S(nul).setValueAtTime(t + 5 / FPS, [100, 100]);
        medir("cartela " + titulo, s, t, x, y, w, h, rot);
        return { nul: nul, w: w, h: h };
    }
    function mascara(L, cx, cy, hw, hh, oval) {
        var mk = L.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"), sh = new Shape(), K = 0.5523;
        if (oval) { sh.vertices = [[cx, cy - hh], [cx + hw, cy], [cx, cy + hh], [cx - hw, cy]]; sh.inTangents = [[-hw * K, 0], [0, -hh * K], [hw * K, 0], [0, hh * K]]; sh.outTangents = [[hw * K, 0], [0, hh * K], [-hw * K, 0], [0, -hh * K]]; }
        else sh.vertices = [[cx - hw, cy - hh], [cx + hw, cy - hh], [cx + hw, cy + hh], [cx - hw, cy + hh]];
        sh.closed = true; mk.property("ADBE Mask Shape").setValue(sh); return mk;
    }
    // obra dentro de un marco recortado (la obra cubre la abertura medida del marco)
    function enMarco(s, img, marco, x, y, ancho, rot, k, t) {
        var mi = imp(G + "alfa3/" + marco + ".png", true), m = D.marcos[marco]; if (!mi || !m) return null;
        var esc = ancho / mi.width, ow = (m[2] - m[0]) * mi.width * esc + 24, oh = (m[3] - m[1]) * mi.height * esc + 24;
        var cx = x + ((m[0] + m[2]) / 2 - 0.5) * ancho, cy = y + ((m[1] + m[3]) / 2 - 0.5) * mi.height * esc;
        var oi = imp(img, false), ob = c.layers.add(oi), e = Math.max(ow / oi.width, oh / oi.height) * 100; ob.name = "obra " + s + " " + (++nObra); S(ob).setValue([e, e]); tab(ob, cx, cy, s, k);   // nombre unico: lupa, craquelado y reflectografia la buscan por nombre
        mascara(ob, oi.width / 2, oi.height / 2, ow / 2 / (e / 100), oh / 2 / (e / 100), marco === "marco_oval");
        var fr = c.layers.add(mi); S(fr).setValue([esc * 100, esc * 100]); tab(fr, x, y, s, k); foto(fr, 25, "#2A2418", "#F1E7CF");
        if (rot) { R(ob).setValue(rot); R(fr).setValue(rot); }
        var v = viva(s); vida(ob, t, v[1]); vida(fr, t, v[1]); caer(fr, t); caer(ob, t);
        return { obra: ob, cx: cx, cy: cy, esc: e, w: ow, h: oh, rot: rot || 0, oval: marco === "marco_oval" };
    }
    // lamina: obra apaisada sobre un paspartu blanco con filete y cinta (un marco la recortaria demasiado)
    function lamina(s, img, x, y, maxW, maxH, rot, k, t) {
        var oi = imp(img, false), e = Math.min(maxW / oi.width, maxH / oi.height), w = oi.width * e, h = oi.height * e;
        var pp = shp("paspartu"), pg = grp(pp, "p"); rect(pg, w + 56, h + 56, 2); fill(pg, "#FBFBF6"); stroke(pg, INK, 3); tab(pp, x, y, s, k);
        var ob = c.layers.add(oi); ob.name = "obra " + s + " " + (++nObra); S(ob).setValue([e * 100, e * 100]); tab(ob, x, y, s, k);
        if (rot) { R(pp).setValue(rot); R(ob).setValue(rot); }
        var v = viva(s); vida(pp, t, v[1]); vida(ob, t, v[1]); caer(pp, t); caer(ob, t);
        var ci = imp(G + "alfa3/cinta.png", true);
        if (ci) for (var i = 0; i < 2; i++) { var cl = pon(G + "alfa3/cinta.png", s, x + (i ? 1 : -1) * (w / 2 + 6), y - h / 2 - 10, 110, k, i ? 36 : -32); if (cl) { mult(cl, 85); caer(cl, t + 0.08); } }
        return { obra: ob, cx: x, cy: y, esc: e * 100, w: w, h: h, rot: rot || 0, oval: false };
    }
    function colocaObra(s, img, x, y, ancho, alto, marco, rot, k, t, aspecto) {
        if (aspecto > 1.25 || !marco) return lamina(s, img, x, y, ancho, alto, rot, k, t);
        return enMarco(s, img, marco, x, y, ancho, rot, k, t);
    }
    function lupa(s, ob, t) {
        nLupa++;
        var v = viva(s), nm = "MATE lupa " + nLupa;
        var lm = shp(nm), lmg = grp(lm, "l"); ell(lmg, 210, 210); fill(lmg, "#FFFFFF"); lm.motionBlur = true; lm.enabled = false;
        P(lm).expression = "posterizeTime(8); var a=time*1.7; var b=[" + Math.round(ob.cx) + "+Math.sin(a)*" + Math.round(ob.w * 0.25) + "," + Math.round(ob.cy) + "+Math.cos(a*0.8)*" + Math.round(ob.h * 0.25) + "]; " + exprTab(s, 0.98, "b");
        var mag = c.layers.add(ob.obra.source); var me = ob.esc * 2.4; S(mag).setValue([me, me]); R(mag).setValue(ob.rot); mag.motionBlur = true;
        P(mag).expression = "var L=thisComp.layer('" + nm + "').transform.position; var O=thisComp.layer('" + ob.obra.name + "').transform.position; L+(O-L)*2.4;";
        mag.setTrackMatte(lm, TrackMatteType.ALPHA); vida(mag, t, v[1]); vida(lm, v[0], v[1]);
        var ar = shp("aro lupa"), arg = grp(ar, "a"); ell(arg, 216, 216); stroke(arg, OCRE, 15); var mg2 = grp(ar, "m"); linea(mg2, [[78, 78], [176, 176]]); stroke(mg2, INK, 24);
        ar.motionBlur = true; P(ar).expression = "thisComp.layer('" + nm + "').transform.position;"; vida(ar, t, v[1]); aspero(ar, 3, 40, 8);
    }
    function reflecto(s, ob, t) {   // el "dibujo de debajo": Find Edges + Tint, y un barrido descubre el color
        var rf = c.layers.add(ob.obra.source); S(rf).setValue([ob.esc, ob.esc]); R(rf).setValue(ob.rot); rf.motionBlur = true;
        P(rf).expression = "thisComp.layer('" + ob.obra.name + "').transform.position;";
        var mp = ob.obra.property("ADBE Mask Parade"); if (mp.numProperties) rf.property("ADBE Mask Parade").addProperty("ADBE Mask Atom").property("ADBE Mask Shape").setValue(mp.property(1).property("ADBE Mask Shape").value);
        fx(rf, "ADBE Find Edges"); foto(rf, 50, "#1E2A33", "#E9EEF0");
        var rw = fx(rf, "ADBE Linear Wipe"); rw.property(2).setValue(0); rw.property(3).setValue(60); rw.property(1).setValueAtTime(t + 0.7, 0); rw.property(1).setValueAtTime(t + 1.2, 100);
        var v = viva(s); vida(rf, t, v[1]); rf.moveBefore(ob.obra); caer(rf, t);
    }
    function craquelar(s, ob, t) {
        var cq = imp(G + "texturas3/craquelado.png", false); if (!cq) return;
        var L = c.layers.add(cq), e = Math.max(ob.w / cq.width, ob.h / cq.height) * 100; S(L).setValue([e, e]); R(L).setValue(ob.rot);
        P(L).expression = "thisComp.layer('" + ob.obra.name + "').transform.position;"; L.motionBlur = true;
        mascara(L, cq.width / 2, cq.height / 2, ob.w / 2 / (e / 100), ob.h / 2 / (e / 100), ob.oval);
        mult(L, 55); var v = viva(s); vida(L, t, v[1]); L.moveBefore(ob.obra);
    }
    function elipseLapiz(s, x, y, a, b, t) {
        var L = shp("lapiz elipse"), g = grp(L, "e"); ell(g, a, b); stroke(g, INK, 4); var tr = trim(g);
        tr.property("ADBE Vector Trim End").expression = "posterizeTime(8); Math.min(100,Math.max(0,(time-" + t + ")*220));";
        tab(L, x, y, s, 1.03); R(L).setValue(-8); aspero(L, 1.5, 40, 8); var v = viva(s); vida(L, t, v[1]);
    }
    function flechaLapiz(s, x, y, rot, t) {
        var L = shp("lapiz flecha"), g = grp(L, "f"); linea(g, [[-110, 0], [-40, -10], [30, 6], [110, 0]]); stroke(g, INK, 5); var tr = trim(g);
        tr.property("ADBE Vector Trim End").expression = "posterizeTime(8); Math.min(100,Math.max(0,(time-" + t + ")*300));";
        var g2 = grp(L, "p"); linea(g2, [[80, -26], [114, 0], [80, 26]]); stroke(g2, INK, 5);
        tab(L, x, y, s, 1.05); R(L).setValue(rot); aspero(L, 1.5, 40, 8); var v = viva(s); vida(L, t, v[1]);
        O(L).expression = "time<" + (t + 0.3) + "?0:100;";
    }
    function muestras(s, cols, x0, y, dx, t) {
        for (var i = 0; i < cols.length; i++) {
            var m = shp("muestra"), g = grp(m, "c"); ell(g, 44, 44); fill(g, cols[i]); stroke(g, INK, 3);
            var hl = grp(m, "hilo"); linea(hl, [[0, 22], [-14 + i * 9, 70]]); stroke(hl, INK, 2);
            tab(m, x0 + i * dx, y, s, 1.08); var v = viva(s); vida(m, t + i * 0.08, v[1]); hervor(m, 6, 4);
        }
    }
    function registro(s) {
        var pos = [[70, 170], [1000, 170], [70, 1320]];
        for (var i = 0; i < pos.length; i++) {
            var L = shp("registro"), g = grp(L, "x"); ell(g, 34, 34); linea(g, [[-28, 0], [28, 0]]); stroke(g, INK, 2.5);
            var g2 = grp(L, "y"); linea(g2, [[0, -28], [0, 28]]); stroke(g2, INK, 2.5);
            tab(L, pos[i][0], pos[i][1], s, 1); var v = viva(s); vida(L, v[0], v[1]); O(L).expression = "posterizeTime(6); seedRandom(" + (s * 10 + i) + ",true); random()>0.12?100:30;";
        }
    }
    function hoja(s, x, y, w, h, col, op, rot, matte) {
        var L = shp("hoja"), g = grp(L, "h"); rect(g, w, h, 0); fill(g, col); R(L).setValue(rot || 0); tab(L, x, y, s, 0.9); mult(L, op);
        L.setTrackMatte(matte || MC, TrackMatteType.LUMA); var v = viva(s); vida(L, v[0], v[1]); return L;
    }
    function decos(s, lista) {
        for (var i = 0; i < (lista || []).length; i++) {
            var q = lista[i], L = pon(q.p, s, q.x, q.y, q.w, q.k, q.rot);
            if (!L) continue;
            if (q.p.indexOf("lum3/") >= 0) mult(L, 90);
            hervor(L, 6, 1.5); caer(L, Math.max(q.t, viva(s)[0]));
        }
    }

    // ---------- movimiento ambiente (v5)
    // corriente: piezas de la obra que cruzan una franja una y otra vez, a velocidades distintas
    function corriente(s, lista, y0, y1, k, n, tam) {
        var v = viva(s);
        for (var i = 0; i < Math.min(n, lista.length); i++) {
            var it = imp(lista[i], true); if (!it) continue;
            var L = c.layers.add(it), ancho = tam[0] + (i * 37) % (tam[1] - tam[0]), e = ancho / it.width * 100, dir = i % 2 ? -1 : 1, vel = 260 + (i * 71) % 260, y = y0 + (i * 211) % Math.max(1, y1 - y0);
            S(L).setValue([e * dir, e]); L.motionBlur = true; L.name = "corriente";
            P(L).expression = exprTab(s, k, "var u=((time*" + vel + "+" + (i * 260) + ")%" + (W + 360) + ")-180; [" + (dir > 0 ? "u" : (W + "-u")) + "," + y + "+Math.sin(time*" + (2 + i % 3) + ")*" + (10 + i % 4 * 4) + "]");
            R(L).expression = "Math.sin(time*" + (3 + i % 2) + ")*6;"; vida(L, v[0], v[1]);
        }
    }
    // pigmento: motas con los colores de la obra que suben despacio y respiran
    function pigmento(s, cols, n, zona) {
        if (!cols || !cols.length) return; var v = viva(s), cl = [];
        for (var q = 0; q < cols.length; q++) { var r0 = rgb(cols[q]); if (0.3 * r0[0] + 0.59 * r0[1] + 0.11 * r0[2] > 0.45) cl.push(cols[q]); }
        cols = cl.length ? cl : [TEAL, LIME, MAG];   // nada de motas oscuras: sobre la pintura parecen manchas
        for (var i = 0; i < n; i++) {
            var L = shp("pigmento"), g = grp(L, "m"), d = 10 + (i * 13) % 26; ell(g, d, d * (0.8 + (i % 3) * 0.12)); fill(g, cols[i % cols.length]);
            var x = zona[0] + (i * 173) % (zona[2] - zona[0]), y = zona[1] + (i * 97) % (zona[3] - zona[1]);
            P(L).expression = exprTab(s, 1.06, "[" + x + "+Math.sin(time*0.7+" + i + ")*30," + zona[3] + "-((time*" + (18 + i % 5 * 6) + "+" + (y - zona[1]) + ")%" + (zona[3] - zona[1]) + ")]");
            L.motionBlur = true; aspero(L, 2, 20, 6); vida(L, v[0], v[1]);
            O(L).expression = "70*Math.min(1, (0.5+0.5*Math.sin(time*1.3+" + i + ")) * 1.6);";
        }
    }
    // lapiz que recorre el contorno de una figura de la obra: dibuja, aguanta y se va; vuelve a empezar
    function contornoLapiz(s, ob, lineas, clara, t) {
        if (!ob || !lineas || !lineas.length) return; var v = viva(s), src = ob.obra.source, sc = ob.esc / 100;
        for (var i = 0; i < lineas.length; i++) {
            var L = shp("lapiz contorno"), g = grp(L, "c"), pts = [];
            for (var j = 0; j < lineas[i].pts.length; j++) pts.push([lineas[i].pts[j][0] * src.width, lineas[i].pts[j][1] * src.height]);
            linea(g, pts); stroke(g, clara ? INK : "#F4F1E6", Math.max(1.5, 3 / sc)); O(L).setValue(70);
            var tr = trim(g), ciclo = 3.4, fase = i * 0.8;
            tr.property("ADBE Vector Trim End").expression = "posterizeTime(12); var u=((time-" + t + "+" + fase + ")%" + ciclo + ")/" + ciclo + "; u<0?0: Math.min(100, u/0.45*100);";
            tr.property("ADBE Vector Trim Start").expression = "posterizeTime(12); var u=((time-" + t + "+" + fase + ")%" + ciclo + ")/" + ciclo + "; u<0.7?0: Math.min(100,(u-0.7)/0.3*100);";
            L.parent = ob.obra; P(L).setValue([0, 0]); R(L).setValue(0); S(L).setValue([100, 100]); vida(L, t, v[1]); aspero(L, 1.2 / sc, 30, 8);
        }
    }
    // capsula viva: una ventana redondeada con un detalle de la obra que se mueve y piezas que flotan dentro
    function capsulaViva(s, ob, x, y, w, h, foco, lista, t) {
        if (!ob) return; var v = viva(s), src = ob.obra.source, nm = "MATE capsula " + s;
        var m = shp(nm), mg = grp(m, "m"); rect(mg, w, h, h / 2); fill(mg, "#FFFFFF"); tab(m, x, y, s, 1.04); m.enabled = false; vida(m, v[0], v[1]);
        var det = c.layers.add(src), sc = ob.esc * 2.3 / 100; S(det).setValue([sc * 100, sc * 100]); det.name = "detalle capsula";
        var fx0 = foco[0] * src.width - src.width / 2, fy0 = foco[1] * src.height - src.height / 2;
        P(det).expression = exprTab(s, 1.04, "[" + x + "-(" + Math.round(fx0 * sc) + ")+Math.sin(time*0.9)*90," + y + "-(" + Math.round(fy0 * sc) + ")+Math.cos(time*0.7)*60]");
        det.motionBlur = true; det.setTrackMatte(m, TrackMatteType.ALPHA); vida(det, t, v[1]);
        for (var i = 0; i < Math.min(4, (lista || []).length); i++) {
            var it = imp(lista[i], true); if (!it) continue;
            var L = c.layers.add(it), e = (110 + i * 22) / Math.max(it.width, it.height) * 100; S(L).setValue([e, e]); L.name = "enjambre";
            P(L).expression = exprTab(s, 1.04, "[" + (x - w / 2 + 60 + i * (w - 120) / 3) + "+Math.sin(time*" + (1.6 + i * 0.4) + ")*" + Math.round(w * 0.3) + "," + y + "+Math.cos(time*" + (0.9 + i * 0.4) + ")*" + Math.round(h * 0.22) + "]");
            R(L).expression = "Math.sin(time*" + (1.5 + i) + ")*14;"; L.motionBlur = true; L.setTrackMatte(m, TrackMatteType.ALPHA); vida(L, t + 0.1, v[1]);
        }
        var fr = shp("marco capsula"), fg = grp(fr, "f"); rect(fg, w + 20, h + 20, (h + 20) / 2); stroke(fg, TEAL, 16); tab(fr, x, y, s, 1.04); aspero(fr, 6, 30, 6); vida(fr, t, v[1]); caer(fr, t);
    }
    // obra viva: las figuras recortadas de la propia obra se ponen encima de su sitio y se mueven alli (balanceo a 8 fps)
    function obraViva(s, ob, lista, t) {
        if (!ob || !lista || !lista.length) return 0; var v = viva(s), n = 0;
        for (var i = 0; i < lista.length; i++) {
            var q = lista[i], it = imp(q.png, true); if (!it) continue;
            var L = c.layers.add(it); L.name = "viva " + s + " " + i; L.parent = ob.obra;
            P(L).setValue([(q.caja[0] + q.caja[2]) / 2, (q.caja[1] + q.caja[3]) / 2]); S(L).setValue([100, 100]); R(L).setValue(0);
            var f = 0.8 + (i % 4) * 0.35;
            R(L).expression = "posterizeTime(8); Math.sin(time*" + f + "*3+" + i + ")*" + (4 + i % 3 * 2) + ";";
            P(L).expression = "posterizeTime(8); value+[Math.sin(time*" + f + "+" + i + ")*" + (6 + i % 3 * 3) + ", Math.cos(time*" + (f * 1.7) + "+" + i + ")*" + (5 + i % 2 * 4) + "];";
            S(L).expression = "posterizeTime(8); var k=1+0.04*Math.sin(time*" + (f * 2.2) + "+" + i + "); [value[0]*k, value[1]*k];";
            vida(L, t + i * 0.12, v[1]); n++;
        }
        return n;
    }
    // grupo que se reordena: tubos y pinceles que cambian de sitio a saltos (franja baja, sin texto)
    function reordenar(s, lista, y) {
        var v = viva(s), n = Math.min(5, (lista || []).length);
        for (var i = 0; i < n; i++) {
            var it = imp(lista[i], true); if (!it) continue;
            var L = c.layers.add(it), e = 150 / Math.max(it.width, it.height) * 100; S(L).setValue([e, e]); L.name = "reordenar"; mult(L, 92);
            P(L).expression = exprTab(s, 1.05, "posterizeTime(6); var k=(" + i + "+Math.floor(time*1.6))%" + n + "; [150+k*190," + y + "+(k%2)*24]");
            R(L).expression = "posterizeTime(6); var k=(" + i + "+Math.floor(time*1.6))%" + n + "; [-18,12,-6,20,-12][k];"; vida(L, v[0], v[1]);
        }
    }
    // barritas de color que entran, parpadean y se van, junto a un titulo
    function barritas(s, x, y) {
        var v = viva(s), cols = [LIME, TEAL, MAG];
        for (var i = 0; i < 3; i++) {
            var L = shp("barrita"), g = grp(L, "b"); rect(g, 110 - i * 22, 13, 0); fill(g, cols[i]); R(L).setValue(-12);
            P(L).expression = exprTab(s, 1.08, "posterizeTime(8); [" + x + "+((time*" + (60 + i * 25) + ")%160)," + (y + i * 30) + "]");
            O(L).expression = "posterizeTime(6); seedRandom(" + (s * 7 + i) + ",true); random()>0.2?100:0;"; vida(L, v[0], v[1]);
        }
    }
    // franjas diagonales que barren el cuadro en cada cambio de momento (cabeza <-> obra); tapan el latigo
    function franjas(t) {
        var cols = [TEAL, MAG, "#BFCBC6", INK];
        for (var i = 0; i < 4; i++) {
            var L = shp("franja"), g = grp(L, "f"); linea(g, [[-170, -1500], [170, -1500], [530, 1500], [190, 1500]], true); fill(g, cols[i]);
            var t0 = t - 0.5 + i * 0.06; P(L).setValueAtTime(t0, [-700 - i * 260, H / 2]); P(L).setValueAtTime(t0 + 0.8, [W + 900 + i * 120, H / 2]);
            var es = new KeyframeEase(0, 60); P(L).setTemporalEaseAtKey(1, [es], [es]); P(L).setTemporalEaseAtKey(2, [es], [es]);
            L.motionBlur = true; vida(L, t0, t0 + 0.82); if (i === 3) mult(L, 70);   // v8: 0.8 s con curva suave, antes 0.38
        }
    }

    // ---------- piezas v6
    // obra grande arriba, detras de la cabeza (centro dominante): ocupa el ancho y la mitad de arriba; cede color para que mande la cabeza
    function obraArriba(s, o, t, fin) {
        var oi = imp(o.img, false); if (!oi) return null; var v = viva(s);
        var Wv = 1000, Hv = 1060, k = Math.max(Wv / oi.width, Hv / oi.height), ob = c.layers.add(oi); ob.name = "obra " + s + " " + (++nObra);
        S(ob).setValue([k * 100, k * 100]); var ancla = Math.min(oi.height - Hv / 2 / k, Math.max(Hv / 2 / k, oi.height * 0.36));
        T(ob).property("ADBE Anchor Point").setValue([oi.width / 2, ancla]); tab(ob, 540, 120 + Hv / 2, s, 0.97);
        mascara(ob, oi.width / 2, ancla, Wv / 2 / k, Hv / 2 / k, false);
        sat(ob, -30); fx(ob, "ADBE Brightness & Contrast 2").property(1).setValue(22);
        S(ob).expression = "var b=Math.max(0,time-" + t + "); value*(1+0.01*b);";
        var fr = shp("filete obra"), fg = grp(fr, "f"); rect(fg, Wv + 6, Hv + 6, 0); stroke(fg, INK, 4); tab(fr, 540, 120 + Hv / 2, s, 0.97);
        vida(ob, t, fin || v[1]); vida(fr, t, fin || v[1]); caer(ob, t, 0.9); caer(fr, t, 0.9);
        var r = { obra: ob, cx: 540, cy: 120 + Hv / 2, esc: k * 100, w: Wv, h: Hv, rot: 0, oval: false, vis: [oi.width / 2 - Wv / 2 / k, ancla - Hv / 2 / k, oi.width / 2 + Wv / 2 / k, ancla + Hv / 2 / k] };
        // figuras vivas y lapiz solo donde se ve la obra
        var vv = []; for (var i = 0; i < (o.vivas || []).length; i++) { var q = o.vivas[i], cx = (q.caja[0] + q.caja[2]) / 2, cy = (q.caja[1] + q.caja[3]) / 2; if (cx > r.vis[0] && cx < r.vis[2] && cy > r.vis[1] && cy < r.vis[3]) vv.push(q); }
        obraViva(s, r, vv.slice(0, 6), t + 0.3);
        var ll = []; for (i = 0; i < (o.contornos || []).length; i++) { var p0 = o.contornos[i].pts[0]; if (p0[1] * oi.height > r.vis[1] && p0[1] * oi.height < r.vis[3]) ll.push(o.contornos[i]); }
        contornoLapiz(s, r, ll.slice(0, 2), o.clara, t + 0.4);
        return r;
    }
    // circulo con anillo que nace pequeno y crece, la obra dentro, marcas que giran, rayos que estallan y manos que entran (referente 31-36 s)
    function circuloObra(s, q, t) {
        var v = viva(s), D0 = 900, cx = 540, cy = 700, nm = "MATE circulo " + s;
        var m = shp(nm), mg = grp(m, "c"); ell(mg, D0, D0); fill(mg, "#FFFFFF"); tab(m, cx, cy, s, 1); m.enabled = false; vida(m, v[0], v[1]);
        S(m).setValueAtTime(t, [18, 18]); S(m).setValueAtTime(t + 0.4, [106, 106]); S(m).setValueAtTime(t + 0.6, [100, 100]);
        var oi = imp(q.img, false), k = Math.max(D0 / oi.width, D0 / oi.height) * 1.05, ob = c.layers.add(oi); ob.name = "obra " + s + " " + (++nObra);
        S(ob).setValue([k * 100, k * 100]); tab(ob, cx, cy, s, 1); ob.setTrackMatte(m, TrackMatteType.ALPHA); vida(ob, t, v[1]);
        S(ob).expression = "var b=Math.max(0,time-" + t + "); value*(1+0.012*b);";
        var an = shp("anillo"), ag = grp(an, "a"); ell(ag, D0 + 40, D0 + 40); stroke(ag, LIME, 26); tab(an, cx, cy, s, 1.02); aspero(an, 4, 30, 8);
        S(an).setValueAtTime(t - 0.05, [15, 15]); S(an).setValueAtTime(t + 0.4, [108, 108]); S(an).setValueAtTime(t + 0.62, [100, 100]); vida(an, t - 0.05, v[1]);
        var mk = shp("marcas"), mkg = grp(mk, "m"); ell(mkg, D0 + 150, D0 + 150); var st = stroke(mkg, TEAL, 18), dsh = st.property("ADBE Vector Stroke Dashes");
        dsh.addProperty("ADBE Vector Stroke Dash 1").setValue(14); dsh.addProperty("ADBE Vector Stroke Gap 1").setValue(70); tab(mk, cx, cy, s, 1.03); R(mk).expression = "time*30;"; vida(mk, t + 0.4, v[1]); caer(mk, t + 0.4);
        var ry = shp("rayos"); for (var i = 0; i < 30; i++) { var g = grp(ry, "r" + i), a = i / 30 * Math.PI * 2, r0 = D0 / 2 + 60, r1 = r0 + 80 + (i % 3) * 50; linea(g, [[Math.cos(a) * r0, Math.sin(a) * r0], [Math.cos(a) * r1, Math.sin(a) * r1]]); stroke(g, INK, 3); var tr = trim(g); tr.property("ADBE Vector Trim End").setValueAtTime(t + 0.4, 0); tr.property("ADBE Vector Trim End").setValueAtTime(t + 0.62, 100); tr.property("ADBE Vector Trim Start").setValueAtTime(t + 0.8, 0); tr.property("ADBE Vector Trim Start").setValueAtTime(t + 1.15, 100); }
        tab(ry, cx, cy, s, 1.03); vida(ry, t + 0.4, t + 1.2);
        var h1 = imp(G + "alfa/mano_senala.png", true);
        if (h1) { var L = c.layers.add(h1), e = 420 / h1.width * 100; S(L).setValue([e, e]); R(L).setValue(60); foto(L, 40); L.name = "mano entra"; L.motionBlur = true;
            P(L).expression = exprTab(s, 1.08, "[linear(time," + (t + 0.5) + "," + (t + 1.1) + ",-320,120), 1180]"); vida(L, t + 0.5, v[1]); }
        return { obra: ob, cx: cx, cy: cy, esc: k * 100, w: D0, h: D0, rot: 0, oval: true };
    }
    // pincelada que revela la obra: la pincelada crece como un barrido y en su borde parpadean barras blancas (referente 116-120 s)
    function pinceladaObra(s, q, t) {
        var v = viva(s), cx = 540, cy = 700, nm = "MATE pincelada " + s, pi = imp(G + "alfa/q_pincel_teal.png", true);
        var m = c.layers.add(pi), e = 1500 / pi.width * 100; m.name = nm; S(m).setValue([e, e * 2.6]); R(m).setValue(-6); tab(m, cx, cy, s, 1); m.enabled = false; vida(m, v[0], v[1]);
        var mw = fx(m, "ADBE Linear Wipe"); mw.property(2).setValue(270); mw.property(3).setValue(90); mw.property(1).setValueAtTime(t, 100); mw.property(1).setValueAtTime(t + 0.7, 0);
        var oi = imp(q.img, false), k = Math.max(1040 / oi.width, 1150 / oi.height), ob = c.layers.add(oi); ob.name = "obra " + s + " " + (++nObra);
        S(ob).setValue([k * 100, k * 100]); tab(ob, cx, cy, s, 1); ob.setTrackMatte(m, TrackMatteType.ALPHA); vida(ob, t, v[1]);
        S(ob).expression = "var b=Math.max(0,time-" + t + "); value*(1+0.012*b);";
        for (var i = 0; i < 3; i++) {
            var b = shp("barra borde"), g = grp(b, "b"); linea(g, [[-16, -260], [16, -260], [60, 260], [28, 260]], true); fill(g, "#FFFFFF");
            P(b).expression = exprTab(s, 1, "[linear(time," + t + "," + (t + 0.7) + ",-200," + (W + 100) + ")+" + i * 52 + "," + cy + "]"); O(b).expression = "posterizeTime(10); seedRandom(" + (s * 3 + i) + ",true); random()>0.3?90:0;"; vida(b, t, t + 0.85);
        }
        return { obra: ob, cx: cx, cy: cy, esc: k * 100, w: 1040, h: 1150, rot: -6, oval: false };
    }
    // silueta del artista que se llena (la mujer del referente 4-12 s): eco fantasma, bloques de color, sus obras en Multiply, piezas que se
    // amontonan de abajo arriba y el retrato en B/N encima; todo dentro de su silueta
    function siluetaArtista(s, q) {
        var v = viva(s), t = q.ini, rp = D.retrato, ri = imp(rp, true); if (!ri) return;
        var ancho = Math.min(860, 1150 * ri.width / ri.height), e = ancho / ri.width * 100, cx = 540, cy = 760;
        var eco = c.layers.add(ri); S(eco).setValue([e * 1.6, e * 1.6]); tab(eco, cx + 60, cy - 40, s, 0.9); fx(eco, "ADBE Fill").property("Color").setValue(rgb(TEAL)); mult(eco, 18); vida(eco, t, v[1]);
        O(eco).setValueAtTime(t, 0); O(eco).setValueAtTime(t + 0.3, 18);
        var m = c.layers.add(ri); m.name = "MATE silueta " + s; S(m).setValue([e, e]); tab(m, cx, cy, s, 1); m.enabled = false; vida(m, v[0], v[1]);
        var dentro = function (L) { L.setTrackMatte(m, TrackMatteType.ALPHA); return L; };
        var mg = shp("magenta silueta"), mgg = grp(mg, "m"); rect(mgg, ancho * 0.9, 420, 0); fill(mgg, MAG); R(mg).setValue(-6); tab(mg, cx - 60, cy + 380, s, 1); mult(mg, 85); dentro(mg); vida(mg, t + 0.25, v[1]); caer(mg, t + 0.25, 0.3);
        // v8: sin obras dentro (no se intervienen): papel, un bloque teal, semitono y las herramientas del pintor que se amontonan
        var pa = c.layers.add(imp("imagenes/texturas/Paper002_2k.jpg", false)); S(pa).setValue([70, 70]); tab(pa, cx, cy + 200, s, 1); mult(pa, 70); dentro(pa); vida(pa, t + 0.3, v[1]);
        var tl = shp("teal silueta"), tlg = grp(tl, "t"); rect(tlg, ancho * 0.8, 360, 0); fill(tlg, TEAL); R(tl).setValue(5); tab(tl, cx + 80, cy + 250, s, 1); mult(tl, 80); dentro(tl); vida(tl, t + 0.45, v[1]); caer(tl, t + 0.45, 0.3);
        var se = imp("componentes_ae/mates_png/semitono_parejo_4K_alfa.png", true); if (se) { var hs = c.layers.add(se); S(hs).setValue([32, 32]); tab(hs, cx, cy + 300, s, 1); mult(hs, 55); dentro(hs); vida(hs, t + 0.5, v[1]); }
        var herr = ["tubo_1", "pincel_1", "tubo_2", "frasco", "carboncillos", "tubo_3", "pincel_2", "espatula", "paleta", "compas", "regla", "bote_pinceles"];
        for (var i = 0; i < 18; i++) {   // se amontonan de abajo arriba
            var pi = imp(G + "alfa3/" + herr[i % herr.length] + ".png", true); if (!pi) continue; var Lp = c.layers.add(pi), kp = (110 + (i * 23) % 70) / Math.max(pi.width, pi.height) * 100; S(Lp).setValue([kp, kp]); R(Lp).setValue((i * 47) % 70 - 35); foto(Lp, 30); mult(Lp, 92);
            var x = cx - ancho * 0.42 + (i * 131) % Math.round(ancho * 0.84), y = cy + 520 - Math.floor(i / 6) * 85 - (i * 31) % 36, t0 = t + 0.6 + i * 0.05;
            P(Lp).expression = exprTab(s, 1, "[" + x + "," + y + "-Math.max(0,1-(time-" + t0 + ")/0.22)*300]"); dentro(Lp); vida(Lp, t0, v[1]);
        }
        var bw = c.layers.add(ri); bw.name = "retrato en Multiply"; S(bw).setValue([e, e]); tab(bw, cx, cy, s, 1); foto(bw, 70); mult(bw, 88); dentro(bw); vida(bw, t, v[1]);
    }
    // silueta de papel blanca sobre bloque oscuro, llena de la obra que sube (la mano del referente 81-85 s)
    function manoPapel(s, q, x, y, ancho) {
        var v = viva(s), mi = imp(G + "alfa3/mano_yeso.png", true); if (!mi) return;
        // del tamano justo del cuadro y sin parallax: mas grande, sobresalia en la seccion vecina y desaparecia de golpe
        var bk = shp("bloque oscuro"), bg = grp(bk, "b"); rect(bg, 1200, 2040, 0); fill(bg, "#1B1F1F"); tab(bk, 540, 960, s, 1); vida(bk, v[0], v[1]);
        var tx = c.layers.add(imp("imagenes/texturas/concrete_floor_worn_001_2k.jpg", false)); S(tx).setValue([100, 100]); tab(tx, 540, 960, s, 1); tx.blendingMode = BlendingMode.SCREEN; O(tx).setValue(24); vida(tx, v[0], v[1]);
        var e = ancho / mi.width * 100, m = c.layers.add(mi); m.name = "MATE mano " + s; S(m).setValue([e, e]); R(m).setValue(-8); tab(m, x, y, s, 1.02); m.enabled = false; vida(m, v[0], v[1]);
        var pa = c.layers.add(imp("imagenes/texturas/Paper001_2k.jpg", false)); S(pa).setValue([90, 90]); tab(pa, x, y, s, 1.02); fx(pa, "ADBE Brightness & Contrast 2").property(1).setValue(60); pa.setTrackMatte(m, TrackMatteType.ALPHA); vida(pa, v[0], v[1]);
        // v8: sin obra dentro: papel blanco, una franja teal que sube y semitono (las obras no se intervienen)
        var tl = shp("teal mano"), tlg = grp(tl, "t"); rect(tlg, ancho * 1.2, 260, 0); fill(tlg, TEAL); R(tl).setValue(-10); tab(tl, x, y, s, 1.02); mult(tl, 75); tl.setTrackMatte(m, TrackMatteType.ALPHA); vida(tl, v[0], v[1]);
        P(tl).expression = exprTab(s, 1.02, "[" + x + "," + (y + 360) + "-(time-" + q.ini + ")*150]");
        var se = imp("componentes_ae/mates_png/semitono_parejo_4K_alfa.png", true); if (se) { var hs = c.layers.add(se); S(hs).setValue([30, 30]); tab(hs, x, y + 150, s, 1.02); mult(hs, 50); hs.setTrackMatte(m, TrackMatteType.ALPHA); vida(hs, v[0], v[1]); }
    }

    // ---------- piezas v7
    // fondo de la cabeza: la obra a sangre en duotono (identidad de collage) y la palabra clave gigante que se desliza detras
    function fondoCabeza(s, q) {
        var v = viva(s), img = (q.obras.length ? q.obras[0].img : D.obrasArtista[0]), oi = imp(img, false);
        var bg = c.layers.addSolid(rgb(FONDOS[s % FONDOS.length]), "color fondo", W, H, 1, DUR); tab(bg, 540, 960, s, 1); vida(bg, v[0], q.corte ? q.corte + 0.02 : v[1]);   // v10: el fondo se corta con la presentadora (con +0.4 tapaba la obra ~5 cuadros: verde vacio)
        // v8: sin la obra en duotono detras: las obras no se intervienen
        var pal = [], pt = [];
        var fc = q.corte || v[1];   // las palabras gigantes solo mientras esta la cabeza; cada una con su propio tiempo
        for (var i = 0; i < q.etqs.length; i++) if (q.etqs[i].t < fc || q.etqs[i].cta) { pal.push(q.etqs[i].txt.toUpperCase()); pt.push(q.etqs[i].t); }
        if (!pal.length) { pal.push(D.artista.split(" ").pop().toUpperCase()); pt.push(q.ini + 0.1); }
        var np = Math.min(3, pal.length);
        for (i = 0; i < np; i++) {
            var t0 = pt[i], t1 = i + 1 < np ? pt[i + 1] : fc;
            for (var f = 0; f < 4; f++) {   // la palabra repetida en filas que se deslizan, como en el ejemplo
                var tx = texto(pal[i], "Impact", 230, f % 2 ? LIME : "#FFFFFF"); var r = centrar(tx); var e = Math.min(1.6, 1040 / r.width); S(tx).setValue([e * 100, e * 100]);
                O(tx).setValue(f === 1 ? 100 : 55); tx.name = "palabra fondo";
                var sg = ((s + f) % 2 ? 1 : -1), vy = [0, 18, -14, 10][s % 4];   // v8: cada seccion y cada fila en otra direccion
                P(tx).expression = exprTab(s, 0.97, "[540+" + sg + "*((time-" + t0 + ")*60%" + 160 + ")," + (250 + f * 230) + "+(time-" + t0 + ")*" + vy + "]"); R(tx).setValue([-4, 3, -2, 5][s % 4]);
                vida(tx, t0, t1); var sc = S(tx), vv = sc.value; sc.setValueAtTime(t0, [vv[0] * 0.8, vv[1] * 0.8]); sc.setValueAtTime(t0 + 0.2, vv);
            }
        }
    }
    // tarjeta de detalle: un recorte de la obra en una tarjeta con cinta, inclinada, a un lado (como la tarjeta del ejemplo)
    function tarjetaDetalle(s, o, x, y, ancho, rot, t, fin) {
        var oi = imp(o.img, false); if (!oi) return; var v = viva(s), alto = ancho * 1.25;
        var foco = (o.contornos && o.contornos.length) ? o.contornos[0].pts[Math.floor(o.contornos[0].pts.length / 2)] : [0.5, 0.45];
        var hoja = shp("tarjeta"), hg = grp(hoja, "h"); rect(hg, ancho + 36, alto + 36, 3); fill(hg, "#FBFBF6"); stroke(hg, INK, 2); R(hoja).setValue(rot); tab(hoja, x, y, s, 1.06);
        var k = Math.max(ancho / oi.width, alto / oi.height) * 2.2, ob = c.layers.add(oi); ob.name = "obra " + s + " " + (++nObra); S(ob).setValue([k * 100, k * 100]); R(ob).setValue(rot);
        T(ob).property("ADBE Anchor Point").setValue([foco[0] * oi.width, foco[1] * oi.height]); tab(ob, x, y, s, 1.06);
        mascara(ob, foco[0] * oi.width, foco[1] * oi.height, ancho / 2 / k, alto / 2 / k, false);
        var ci = pon(G + "alfa3/cinta.png", s, x, y - alto / 2 - 10, 140, 1.06, rot + 6); if (ci) mult(ci, 85);
        vida(hoja, t, fin); vida(ob, t, fin); if (ci) vida(ci, t + 0.06, fin); caer(hoja, t); caer(ob, t);
        D.tarjetas.push(hoja, ob); if (ci) D.tarjetas.push(ci);   // v10b: se suben encima de la presentadora al final del armado
    }
    // obra a sangre con recorrido lento: llena el cuadro y se desplaza entre dos puntos de su detalle
    function obraSangre(s, q, t) {
        var v = viva(s), oi = imp(q.img, false); if (!oi) return null;
        var k = Math.max(W / oi.width, H / oi.height) * 1.12, ob = c.layers.add(oi); ob.name = "obra " + s + " " + (++nObra); S(ob).setValue([k * 100, k * 100]);
        var holgX = Math.max(0, oi.width * k - W) / 2, holgY = Math.max(0, oi.height * k - H) / 2, dir = [1, -1, -1, 1][(s + nObra) % 4], diy = [1, 1, -1, -1][(s + nObra) % 4];   // v8: el recorrido cambia de direccion
        // v10b: recorrido lento (revision 2026-11-05: "saltos muy rapidos entre las obras"): como mucho 70 px/s en x y 50 px/s en y; antes cruzaba hasta 1100 px/s
        var du = Math.max(0.5, q.fin - q.ini), ax = Math.round(Math.min(holgX * 0.8, 35 * du)), ay = Math.round(Math.min(holgY * 0.6, 25 * du));
        tab(ob, 540, 960, s, 1); P(ob).expression = exprTab(s, 1, "var b=Math.max(0,time-" + t + ")/" + du + "; [540+" + dir + "*linear(b,0,1," + ax + ",-" + ax + ")," + "960+" + diy + "*linear(b,0,1," + ay + ",-" + ay + ")]");
        S(ob).expression = "var b=Math.max(0,time-" + t + "); value*(1+0.008*b);"; vida(ob, t, v[1]);
        // v10c: recortada a su cuadro (1080 x 1920 de su punto): al deslizar no se desborda sobre la obra vecina
        var cu = c.layers.addSolid([1, 1, 1], "MATE cuadro " + ob.name, W, H, 1, DUR); tab(cu, 540, 960, s, 1); cu.enabled = false; vida(cu, t, v[1]); ob.setTrackMatte(cu, TrackMatteType.ALPHA);
        return { obra: ob, cx: 540, cy: 960, esc: k * 100, w: W, h: H, rot: 0, oval: false };
    }

    // ---------- secciones
    function cabeza(s, q) {   // v8: la cabeza manda mientras habla; cuando nombra la obra, la obra entra a sangre y ella se va
        var gancho = q.tipo === "gancho", v = viva(s);
        fondoCabeza(s, q);
        if (q.inserto) {   // inserto: la obra a sangre mientras la nombra; la cabeza se oculta debajo y vuelve (tapado por franjas)
            var it0 = q.inserto.t0, it1 = q.inserto.t1, oiI = imp(q.inserto.img, false), subeI = oiI ? Math.max(W / oiI.width, H / oiI.height) : 1, insL;
            var fondoI = c.layers.addSolid(rgb(PAPEL), "papel inserto", W, H, 1, DUR); tab(fondoI, 540, 960, s, 1); vida(fondoI, it0, it1);
            if (subeI > 1.9) { var lmI = lamina(s, q.inserto.img, 540, 700, 1020, 1150, -1, 0.98, it0); if (lmI) { vida(lmI.obra, it0, it1); insL = lmI.obra; } }
            else { var obI = obraSangre(s, { img: q.inserto.img, ini: it0, fin: it1 }, it0); if (obI) { vida(obI.obra, it0, it1); insL = obI.obra; } }
            D.insertos.push([s, it0, it1]);
        }
        if (q.corte) {
            for (var i = 0; i < q.obras.length; i++) {
                // v10b: de una obra a la siguiente con un fundido lento de 0.9 s (antes un corte seco) y la siguiente debajo
                var o = q.obras[i], t0 = i === 0 ? q.corte : Math.max(o.t, q.corte + 0.8), tn = i + 1 < q.obras.length ? Math.max(q.obras[i + 1].t, q.corte + 0.8) : -1, t1 = tn > 0 ? tn + 0.9 : v[1];
                var oi0 = imp(o.img, false), sube = oi0 ? Math.max(W / oi0.width, H / oi0.height) : 1, Lo = null;
                if (sube > 1.9) { var lm = lamina(s, o.img, 540, 700, 940, 1150, i % 2 ? -1 : 1, 0.98, t0); if (lm) { vida(lm.obra, t0, t1); Lo = lm.obra; } }   // poca resolucion: en lamina
                else { var ob = obraSangre(s, { img: o.img, ini: t0, fin: t1 }, t0); if (ob) { vida(ob.obra, t0, t1); ob.obra.moveToEnd(); ob.obra.moveBefore(c.layer("papel")); Lo = ob.obra; } }
                if (Lo && tn > 0) { var op0 = O(Lo); op0.setValueAtTime(tn, 100); op0.setValueAtTime(tn + 0.9, 0); var ez = new KeyframeEase(0, 50); op0.setTemporalEaseAtKey(op0.numKeys - 1, [ez], [ez]); op0.setTemporalEaseAtKey(op0.numKeys, [ez], [ez]); }
            }
            var puestas = [];
            for (i = 0; i < q.etqs.length; i++) { var e = q.etqs[i]; if (e.t >= q.corte && !e.cta) {
                var ny = 0; for (var z = 0; z < puestas.length; z++) if (!puestas[z].fin || puestas[z].fin > e.t) ny++;   // v10b: la fila cuenta solo las que siguen a la vista
                etiqueta(s, 540, 260 + ny * 150, e.txt, e.t, e.rot, e.size, false, e.fin); puestas.push(e); } }
            for (i = 0; i < (q.cartelas || []).length; i++) { var ca = q.cartelas[i]; cartela(s, 250, 1120, ca.titulo, ca.fecha ? [ca.fecha] : [" "], ca.t, i % 2 ? 1.5 : -1.5); }   // centradas: a la izquierda las largas se salian
        } else {
            for (var j = 0; j < q.obras.length; j++) {   // la obra de la que habla entra como tarjeta de detalle a un lado, sin tapar la cara
                // v10b (revision 2026-11-05): cuando ella la senala, la tarjeta sale a su lado y ENCIMA de ella (antes quedaba detras);
                // la primera a la izquierda y la segunda a la derecha, por los lados del pelo y el hombro, nunca sobre la cara; se quedan las dos
                var oo = q.obras[j];
                tarjetaDetalle(s, oo, j % 2 ? 192 : 878, 1120, 290, j % 2 ? -6 : 6, Math.max(Math.min(oo.t, q.fin - 1.5), q.ini + 0.2), v[1]);   // al menos 1.5 s a la vista antes de que la camara se vaya
            }
        }
        registro(s);
    }
    function obra(s, q) {   // v7: la obra a sangre, con un solo acento; nada de relleno
        var oi0 = imp(q.img, false), sube = oi0 ? Math.max(W / oi0.width, H / oi0.height) : 1, ob;
        if (sube > 1.9) ob = lamina(s, q.img, 540, 700, 940, 1150, s % 2 ? -1 : 1, 0.98, Math.max(0, q.ini - 1.2));   // obra de poca resolucion: a sangre se ve borrosa
        else ob = obraSangre(s, q, Math.max(0, q.ini - 1.2));   // v10c: ya esta en su sitio cuando empieza el deslizamiento (antes aparecia al llegar: parecia un corte)
        // v8: la obra no se interviene: ni figuras que se mueven, ni lapiz, ni lupa encima
        cartela(s, 250, 1250, q.titulo, q.fecha ? [q.fecha] : [" "], q.ini + 0.3, s % 2 ? 1.5 : -1.5);
        for (var i = 0; i < q.etqs.length; i++) { var e = q.etqs[i]; etiqueta(s, e.x, e.y, e.txt, e.t, e.rot, e.size); }
        registro(s);
    }
    function ficha(s, q) {
        hoja(s, 540, 760, 940, 1100, "#BFCBC6", 30, -2, MG);
        etiqueta(s, 540, 215, "Artist file  No. " + D.numero, q.ini + 0.1, -3, 52);
        siluetaArtista(s, q);   // v6: el retrato del artista como silueta que se llena con sus obras y sus piezas
        // cartela grande: nombre en Impact a la medida, fechas en mono y lema en serif; nada tacha el texto
        var nul = nulo("ficha cartela"); tab(nul, 540, 1250, s, 1);   // v10c: un poco mas abajo (revision 2026-11-05)
        var v = viva(s); vida(nul, q.ini + 0.2, v[1]);
        var nm = texto(D.artista.toUpperCase(), "Impact", 100, INK), r = centrar(nm); if (r.width > 720) { var k = 720 / r.width * 100; S(nm).setValue([k, k]); }
        var fe = texto(D.fechas, "CourierNewPS-BoldMT", 44, INK); centrar(fe);
        var lema = D.lema, cut = lema.length > 26 ? lema.lastIndexOf(" ", Math.ceil(lema.length / 2) + 4) : -1; if (cut > 0) lema = lema.substr(0, cut) + "\r" + lema.substr(cut + 1);
        var le = texto(lema, "InstrumentSerif-Italic", 50, INK); var dl = le.property("ADBE Text Properties").property("ADBE Text Document").value; dl.autoLeading = false; dl.leading = 56; le.property("ADBE Text Properties").property("ADBE Text Document").setValue(dl); var rl = centrar(le);
        var hN = r.height * (r.width > 720 ? 720 / r.width : 1), hh = hN + 50 + rl.height + 90, ww = Math.min(800, Math.max(Math.min(r.width, 720), rl.width) + 70);
        var card = shp("hoja ficha"), cg = grp(card, "h"); rect(cg, ww, hh, 4); fill(cg, "#FBFBF6"); stroke(cg, INK, 2); card.parent = nul; P(card).setValue([0, 0]);
        nm.parent = nul; P(nm).setValue([0, -hh / 2 + 30 + hN / 2]); fe.parent = nul; P(fe).setValue([0, -hh / 2 + 30 + hN + 32]); le.parent = nul; P(le).setValue([0, -hh / 2 + 30 + hN + 60 + rl.height / 2 + 10]);
        // sin subrayado: cualquier trazo sobre el nombre lo tacha (revision 2026-11-04)
        vida(card, q.ini + 0.2, v[1]); vida(nm, q.ini + 0.2, v[1]); vida(fe, q.ini + 0.2, v[1]); vida(le, q.ini + 0.2, v[1]);
        // v10c: el nombre, las fechas y el lema entran con un fundido corto con la tarjeta (antes la tarjeta salia vacia 3 cuadros y el texto saltaba: "glitch")
        var ent = [[nm, 0.22], [fe, 0.42], [le, 0.62]];
        for (var z = 0; z < ent.length; z++) { var oz = O(ent[z][0]), tz = q.ini + ent[z][1]; oz.setValueAtTime(q.ini + 0.2, 0); oz.setValueAtTime(tz, 0); oz.setValueAtTime(tz + 0.25, 100); }
        nm.moveBefore(card); fe.moveBefore(card); le.moveBefore(card); R(nul).setValue(-1);
        S(nul).setValueAtTime(q.ini + 0.2, [92, 92]); S(nul).setValueAtTime(q.ini + 0.37, [100, 100]);
        medir("ficha cartela", s, q.ini + 0.2, 540, 1250, ww, hh, -1);
        registro(s);
    }
    function cita(s, q) {   // v10c (revision 2026-11-05: "la cita esta muy basica, deberia tener mas fuerza"): tipografia grande que entra palabra a palabra con la voz
        var v = viva(s), t0 = q.ini;
        var bk = shp("bloque oscuro"), bg = grp(bk, "b"); rect(bg, 1200, 2040, 0); fill(bg, "#151919"); tab(bk, 540, 960, s, 1); vida(bk, v[0], v[1]);
        var tx = c.layers.add(imp("imagenes/texturas/concrete_floor_worn_001_2k.jpg", false)); tab(tx, 540, 960, s, 1); tx.blendingMode = BlendingMode.SCREEN; O(tx).setValue(20); vida(tx, v[0], v[1]);
        // losa magenta en diagonal que cruza detras del texto
        var mg = shp("losa cita"), mgg = grp(mg, "m"); rect(mgg, 1500, 760, 0); fill(mgg, MAG); R(mg).setValue(-9); tab(mg, 540, 980, s, 0.97); O(mg).setValue(92); vida(mg, v[0], v[1]);
        var mp = P(mg).expression; P(mg).expression = "var e=ease(time," + (t0 - 0.05) + "," + (t0 + 0.45) + ",-1500,0); " + mp.replace("value-d", "value+[e,0]-d");
        // v10c (revision: "le faltaban detallitos del estilo base"): borde rasgado, semitono y papel dentro de la losa, cintas, mano de papel y lapiz
        aspero(mg, 14, 70, 6);
        var mm = shp("MATE losa cita"), mmg = grp(mm, "m"); rect(mmg, 1500, 760, 0); fill(mmg, "#FFFFFF"); R(mm).setValue(-9); tab(mm, 540, 980, s, 0.97); P(mm).expression = P(mg).expression; aspero(mm, 14, 70, 6); mm.enabled = false; vida(mm, v[0], v[1]);
        var se = imp("componentes_ae/mates_png/semitono_parejo_4K_alfa.png", true); if (se) { var hs = c.layers.add(se); S(hs).setValue([40, 40]); tab(hs, 760, 1060, s, 0.97); mult(hs, 40); hs.setTrackMatte(mm, TrackMatteType.ALPHA); vida(hs, t0, v[1]); }
        var pq = c.layers.add(imp("imagenes/texturas/Paper001_2k.jpg", false)); S(pq).setValue([80, 80]); tab(pq, 540, 980, s, 0.97); mult(pq, 45); pq.setTrackMatte(mm, TrackMatteType.ALPHA); vida(pq, t0, v[1]);
        var cin = [[120, 690, -32], [985, 1230, 28]];
        for (var ci = 0; ci < cin.length; ci++) { var cl = pon(G + "alfa3/cinta.png", s, cin[ci][0], cin[ci][1], 190, 0.97, cin[ci][2]); if (cl) { mult(cl, 90); vida(cl, t0 + 0.45 + ci * 0.08, v[1]); caer(cl, t0 + 0.45 + ci * 0.08); } }
        var mi = imp(G + "alfa3/mano_yeso.png", true);
        if (mi) { var ea = 380 / mi.width * 100, mh = c.layers.add(mi); mh.name = "MATE mano cita"; S(mh).setValue([ea, ea]); R(mh).setValue(-14); tab(mh, 905, 1770, s, 1.03); mh.enabled = false; vida(mh, v[0], v[1]);
            var pa = c.layers.add(imp("imagenes/texturas/Paper001_2k.jpg", false)); S(pa).setValue([60, 60]); tab(pa, 905, 1770, s, 1.03); fx(pa, "ADBE Brightness & Contrast 2").property(1).setValue(60); pa.setTrackMatte(mh, TrackMatteType.ALPHA); vida(pa, t0 + 0.2, v[1]);
            var tl = shp("teal mano cita"), tlg = grp(tl, "t"); rect(tlg, 600, 150, 0); fill(tlg, TEAL); R(tl).setValue(-10); tab(tl, 905, 1830, s, 1.03); mult(tl, 80); tl.setTrackMatte(mh, TrackMatteType.ALPHA); vida(tl, t0 + 0.2, v[1]);
            caer(pa, t0 + 0.2); }
        var pg = c.layers.add(imp("imagenes/texturas/Paper002_2k.jpg", false)); S(pg).setValue([H * 1.05 / pg.source.height * 100, H * 1.05 / pg.source.height * 100]); tab(pg, 540, 960, s, 1); pg.blendingMode = BlendingMode.SCREEN; O(pg).setValue(10); vida(pg, v[0], v[1]);
        // palabras con su tiempo (las de la voz si coinciden; si no, repartidas)
        var lineas = [], todas = [];
        todas = q.cita.join(" ").replace(/[\u201C\u201D"]/g, "").replace(/^\s+|\s+$/g, "").toUpperCase().split(/\s+/);
        var cur = "", j;   // lineas cortas (12 letras como mucho): la letra puede ser mucho mas grande
        for (var i = 0; i < todas.length; i++) { if (cur && (cur + " " + todas[i]).length > 12) { lineas.push(cur); cur = todas[i]; } else cur = cur ? cur + " " + todas[i] : todas[i]; }
        if (cur) lineas.push(cur);
        var TW = [], pw = q.palabras || [];
        for (i = 0; i < todas.length; i++) TW.push(pw.length === todas.length ? pw[i][1] : t0 + 0.25 + i * Math.max(0.15, (q.fin - t0 - 1.6) / todas.length));
        var clave = (q.clave || "").toUpperCase();
        var nul = nulo("cita"); tab(nul, 540, 960, s, 1); vida(nul, v[0], v[1]);
        S(nul).expression = "var b=Math.max(0,time-" + t0 + "); value*(1+0.012*b);";   // empuje lento hacia dentro
        // tamano comun: la linea mas ancha mide 940 px
        var SIZE = 150, capas = [], anch = 0;
        for (i = 0; i < lineas.length; i++) { var L = texto(lineas[i], "Impact", SIZE, "#FFFFFF", ParagraphJustification.LEFT_JUSTIFY); var r = L.sourceRectAtTime(0, false); anch = Math.max(anch, r.width); capas.push(L); }
        var k = Math.min(850 / anch, 1150 / (SIZE * 1.04 * lineas.length)), lh = SIZE * 1.04 * k, y0 = 1000 - lh * lineas.length / 2, n = 0;
        var kl = -1, kw = 0;
        for (i = 0; i < capas.length; i++) {
            var L = capas[i], r = L.sourceRectAtTime(0, false); L.name = "cita linea " + (i + 1); S(L).setValue([k * 100, k * 100]);
            T(L).property("ADBE Anchor Point").setValue([r.left, r.top]); L.parent = nul; P(L).setValue([70 - 540, y0 + i * lh - 960]); vida(L, t0, v[1]);
            try { L.property("ADBE Text Properties").property("ADBE Text More Options").property("ADBE Text Anchor Point Grouping").setValue(2); } catch (e) {}
            var ws = lineas[i].split(/\s+/), St = [], K = -1;
            for (j = 0; j < ws.length; j++) { St.push(TW[n + j].toFixed(3)); if (clave && ws[j].replace(/[^A-Z]/g, "") === clave) { K = j; kl = i; kw = r.width * k; var kt = TW[n + j]; } }
            n += ws.length;
            var A = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"), ap = A.property("ADBE Text Animator Properties");
            ap.addProperty("ADBE Text Opacity").setValue(0); ap.addProperty("ADBE Text Scale 3D").setValue([175, 175, 100]); ap.addProperty("ADBE Text Position 3D").setValue([0, 40, 0]);
            var sl = A.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sl.property("ADBE Text Range Type2").setValue(3);
            sl.property("ADBE Text Expressible Amount").expression = "var S=[" + St.join(",") + "]; var t=time-S[textIndex-1]; t<0?100:100*(1-ease(t,0,0.22,0,1));";
            if (K >= 0) {   // la palabra clave en lima y un poco mas grande
                var B = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"), bp = B.property("ADBE Text Animator Properties");
                bp.addProperty("ADBE Text Fill Color").setValue(rgb(LIME)); bp.addProperty("ADBE Text Scale 3D").setValue([112, 112, 100]);
                var sb = B.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sb.property("ADBE Text Range Type2").setValue(3);
                sb.property("ADBE Text Expressible Amount").expression = "(textIndex-1)==" + K + "?100:0;";
            }
        }
        if (kl >= 0) {   // lapiz que rodea la linea de la palabra clave cuando ella la dice
            var el = shp("lapiz clave"), eg = grp(el, "e"); ell(eg, kw + 110, lh * 1.15); stroke(eg, "#FFFFFF", 6); var etr = trim(eg);
            etr.property("ADBE Vector Trim End").expression = "posterizeTime(12); Math.min(100,Math.max(0,(time-" + (kt + 0.15) + ")*200));";
            el.parent = nul; P(el).setValue([70 + kw / 2 - 540, y0 + kl * lh + lh * 0.45 - 960]); R(el).setValue(-4); aspero(el, 1.5, 40, 8); vida(el, kt + 0.15, v[1]);
        }
        // comilla gigante en lima que cae arriba a la izquierda
        var cm = texto("\u201C", "Impact", 640, LIME, ParagraphJustification.LEFT_JUSTIFY); cm.name = "comilla"; var rc = cm.sourceRectAtTime(0, false);
        T(cm).property("ADBE Anchor Point").setValue([rc.left + rc.width / 2, rc.top + rc.height / 2]); cm.parent = nul; P(cm).setValue([200 - 540, y0 - 150 - 960]); R(cm).setValue(-8); vida(cm, t0 - 0.05, v[1]); caer(cm, t0 - 0.05);
        // autor que se teclea al final, con una linea lima que se dibuja
        var tf = TW[TW.length - 1] + 0.2, au = texto(q.autor.replace(/^[\u2014\-\s]+/, "").toUpperCase(), "CourierNewPS-BoldMT", 40, "#FFFFFF", ParagraphJustification.LEFT_JUSTIFY); au.name = "cita autor";
        var ra = au.sourceRectAtTime(0, false); if (ra.width > 900) S(au).setValue([900 / ra.width * 100, 900 / ra.width * 100]);
        T(au).property("ADBE Anchor Point").setValue([ra.left, ra.top]); au.parent = nul; P(au).setValue([74 - 540, y0 + lh * lineas.length + 70 - 960]); vida(au, tf, v[1]);
        var AA = au.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator"); AA.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(0);
        var sa = AA.property("ADBE Text Selectors").addProperty("ADBE Text Selector"); sa.property("ADBE Text Percent Start").expression = "linear(time," + tf + "," + (tf + 0.45) + ",0,100);";
        var ul = shp("raya autor"), ug = grp(ul, "u"); linea(ug, [[0, 0], [Math.min(900, ra.width), 0]]); stroke(ug, LIME, 8); var tr = trim(ug);
        tr.property("ADBE Vector Trim End").expression = "ease(time," + tf + "," + (tf + 0.6) + ",0,100);"; ul.parent = nul; P(ul).setValue([74 - 540, y0 + lh * lineas.length + 70 + ra.height + 22 - 960]); vida(ul, tf, v[1]);
        medir("cita", s, t0, 540, 1000, 1000, lh * lineas.length + 260, 0);
        registro(s);
    }
    function trazoBajo(s) {   // franja de botones de Shorts: sin texto, con trazo de carbon y algo de papel
        var tc = pon(G + "alfa3/trazo_carbon.png", s, [300, 760, 420][s % 3], [1640, 1720, 1660][s % 3], 520, 0.95, [6, -8, 4][s % 3]); if (tc) mult(tc, 38);
    }

    // ---------- armado
    function build(datos) {
        D = datos; D.medidas = []; D.insertos = []; D.tarjetas = []; DUR = D.total; ROOT = G = D.kit;
        var tk = (D.estilo && D.estilo.tokens) || {};   // los colores del estilo de la marca (library/styles o brands/<marca>/styles)
        INK = tk.tinta || INK; PAPEL = tk.papel || PAPEL; MAG = tk.rojo || tk.magenta || MAG; LIME = tk.mascara || tk.lima || LIME; TEAL = tk.estatica || tk.teal || TEAL; MINT = tk.fosforo || tk.menta || MINT;
        if (tk.fondos_presentadora) FONDOS = tk.fondos_presentadora;
        for (var i = app.project.numItems; i >= 1; i--) { var it0 = app.project.item(i); if ((it0 instanceof CompItem && it0.name.indexOf(D.comp) === 0) || (it0 instanceof FolderItem && it0.name === D.comp + " media") || (it0 instanceof FootageItem && it0.file && it0.file.fsName.indexOf(D.comp) >= 0 && it0.file.fsName.indexOf("_mdna_sound") >= 0)) it0.remove(); }   // el wav de sonido importado queda bloqueado en Windows si no se quita
        fold = app.project.items.addFolder(D.comp + " media"); cache = {};
        c = app.project.items.addComp(D.comp, W, H, 1, DUR, FPS); c.motionBlur = true; c.shutterAngle = 90;   // v10c: menos estela en el deslizamiento
         c.shutterPhase = -90;
        // camara: en cada seccion deriva (12, 9 px/s) y salta en 6 cuadros justo antes de que empiece la siguiente
        var cam = c.layers.addNull(DUR); cam.name = "CAM"; cam.enabled = false; var cp = P(cam), S0 = D.secciones;
        cp.setValueAtTime(0, [W / 2 + S0[0].spot[0], H / 2 + S0[0].spot[1]]);
        for (i = 1; i < S0.length; i++) {
            var a = S0[i - 1], b = S0[i], esC = function (x) { return x.tipo === "cabeza" || x.tipo === "gancho"; }, pas = (esC(a) && !a.corte) !== esC(b) ? 0.55 : 1.2,   // v10c: deslizamiento de 1.2 s que se ve (con 0.8 parecia un corte)
                t1 = Math.max(b.ini - pas, a.ini + 0.05), dur = Math.min(5, t1 - Math.max(a.ini, 0)), dv = DERIVA[(i - 1) % 4];
            cp.setValueAtTime(t1, [W / 2 + a.spot[0] + dv[0] * dur, H / 2 + a.spot[1] + dv[1] * dur]);   // v10b: paso de 0.8 s entre obras; 0.55 donde las franjas lo tapan (de la presentadora a una obra: si empezara antes se comeria su final)
            cp.setValueAtTime(b.ini, [W / 2 + b.spot[0], H / 2 + b.spot[1]]);
        }
        var ul = S0[S0.length - 1], du = DERIVA[(S0.length - 1) % 4], dl = Math.min(5, DUR - ul.ini); cp.setValueAtTime(DUR, [W / 2 + ul.spot[0] + du[0] * dl, H / 2 + ul.spot[1] + du[1] * dl]);   // v10b: deriva acotada (en una seccion larga movia la lamina ~120 px y la cortaba)
        var lent = new KeyframeEase(0, 33), sale = new KeyframeEase(0, 55), llega = new KeyframeEase(0, 60);   // v8: curva mas suave
        for (i = 1; i <= cp.numKeys; i++) { var par = (i % 2 === 0); cp.setTemporalEaseAtKey(i, [par ? lent : llega], [par ? sale : lent]); cp.setSpatialAutoBezierAtKey(i, false); cp.setSpatialContinuousAtKey(i, false); cp.setSpatialTangentsAtKey(i, [0, 0, 0], [0, 0, 0]); }   // v10b: trayectoria recta (la curva automatica se adelantaba ~100 px antes del paso y arrastraba la obra)
        // mates de erosion compartidos (en pantalla)
        var cq = imp(G + "texturas3/craquelado.png", false); MC = c.layers.add(cq); MC.name = "MATE craquelado"; S(MC).setValue([W * 1.6 / cq.width * 100, W * 1.6 / cq.width * 100]); P(MC).setValue([W / 2, H / 2]); fx(MC, "ADBE Threshold2").property(1).setValue(0.46); MC.enabled = false;
        var gr = imp("imagenes/texturas/concrete_layers_02_2k.jpg", false); MG = c.layers.add(gr); MG.name = "MATE erosion"; S(MG).setValue([115, 115]); P(MG).setValue([W / 2, H / 2]); fx(MG, "ADBE Threshold2").property(1).setValue(0.445); MG.enabled = false;
        // fondo
        var base = c.layers.addSolid(rgb(tk.fondo || PAPEL), "papel", W, H, 1, DUR); base.moveToEnd();   // fondo del estilo (Cult Pixel: casi negro)
        var pp = c.layers.add(imp("imagenes/texturas/Paper001_2k.jpg", false)); S(pp).setValue([H * 1.05 / pp.source.height * 100, H * 1.05 / pp.source.height * 100]); P(pp).setValue([W / 2, H / 2]); mult(pp, 22);
        var li = imp(G + "texturas3/lienzo.png", false); if (li) { var ll = c.layers.add(li); S(ll).setValue([W * 1.9 / li.width * 100, W * 1.9 / li.width * 100]); P(ll).setValue([W / 2, H / 2]); mult(ll, 14); }
        // secciones
        for (i = 0; i < S0.length; i++) {
            var q = S0[i];
            if (q.tipo === "cabeza" || q.tipo === "gancho") cabeza(i, q); else if (q.tipo === "obra") obra(i, q); else if (q.tipo === "ficha") ficha(i, q); else if (q.tipo === "cita") cita(i, q);
        }
        var ds = c.layers.addSolid([0, 0, 0], "menos color tablero", W, H, 1, DUR); ds.adjustmentLayer = true; sat(ds, D.desaturar);
        // cabezas: grande en las lineas A (su toma), pequena a 6 fps en las obras
        var cabs = [];
        for (i = 0; i < S0.length; i++) {
            var s = S0[i]; if (s.tipo !== "cabeza" && s.tipo !== "gancho") continue;   // v5: la cabeza solo cuando habla
            var mt = imp(s.mate, true), v = viva(i), hd = s.head;
            if (true) {
                var fin = s.corte ? s.corte + 0.02 : v[1];   // llega al final de su linea; con corte, se corta bajo las franjas
                var cs = c.layers.add(mt); cs.name = "copia menta " + s.id; S(cs).setValue([hd.s, hd.s]); tab(cs, hd.x + 24, hd.y + 20, i, 1.02); fx(cs, "ADBE Fill").property("Color").setValue(rgb(MINT)); mult(cs, 62); cs.startTime = s.t0base; vida(cs, v[0], fin);
                var cb = c.layers.add(mt); cb.name = "CABEZA " + s.id; S(cb).setValue([hd.s, hd.s]); tab(cb, hd.x, hd.y, i, 1.05); cb.startTime = s.t0base; if (s.sin_boca) { vaiven(cb); vaiven(cs); } else { congelar(cb); congelar(cs); } vida(cb, v[0], fin); vida(cs, v[0], fin); cabs.push(cb);
                // v9: sin fundido (se veia raro): la cabeza se corta debajo de las franjas
                if (s.inserto) { var qs = [cb, cs]; for (var z = 0; z < 2; z++) { var op = O(qs[z]), o0 = op.value; op.setValueAtTime(s.inserto.t0 + 0.12, o0); op.setValueAtTime(s.inserto.t0 + 0.13, 0); op.setValueAtTime(s.inserto.t1 + 0.1, 0); op.setValueAtTime(s.inserto.t1 + 0.11, o0);
                    for (var kk = 1; kk <= op.numKeys; kk++) op.setInterpolationTypeAtKey(kk, KeyframeInterpolationType.HOLD); } }
            } else {
                var pe = c.layers.add(mt); pe.name = "cabeza 6 fps " + i; pe.timeRemapEnabled = true; pe.property("ADBE Time Remapping").expression = "posterizeTime(6); time%(source.duration-0.1);";
                S(pe).setValue([hd.s, hd.s]); tab(pe, hd.x, hd.y, i, 1.1); vida(pe, s.ini + 0.2, v[1]); caer(pe, s.ini + 0.2); cabs.push(pe);
            }
        }
        // glitch de 3 cuadros en cada latigo, debajo de las cabezas
        var mp = app.project.items.addComp(D.comp + " mapa glitch", W, H, 1, DUR, FPS); mp.parentFolder = fold;
        var ns = mp.layers.addSolid([0.5, 0.5, 0.5], "ruido", W, H, 1, DUR), fn = fx(ns, "ADBE Fractal Noise");
        fn.property("Contrast").setValue(280); fn.property("Uniform Scaling").setValue(0); fn.property("Scale Width").setValue(1400); fn.property("Scale Height").setValue(60); fn.property("Evolution").expression = "posterizeTime(15); time*720;";
        var mgl = c.layers.add(mp); mgl.name = "MAPA glitch"; mgl.enabled = false;
        var ga = c.layers.addSolid([0, 0, 0], "glitch", W, H, 1, DUR); ga.adjustmentLayer = true; var dm = fx(ga, "ADBE Displacement Map"); dm.property(1).setValue(mgl.index); dm.property(2).setValue(1); dm.property(4).setValue(1); dm.property(5).setValue(0);
        var gl = []; for (i = 1; i < S0.length; i++) gl.push("(time>" + (S0[i].ini - 0.14).toFixed(3) + "&&time<" + (S0[i].ini - 0.03).toFixed(3) + ")");
        dm.property(3).expression = "0;";   // v8: sin glitch en los saltos (transiciones suaves)
        if (D.estilo && D.estilo.glitch) {   // estilo con glitches (cult_pixel_vhs): desplazamiento + destello de estatica en cada cambio y corte
            var tg = []; for (i = 1; i < S0.length; i++) tg.push(S0[i].ini); for (i = 0; i < S0.length; i++) if (S0[i].corte) tg.push(S0[i].corte + 0.12);
            for (i = 0; i < D.insertos.length; i++) { tg.push(D.insertos[i][1] + 0.12); tg.push(D.insertos[i][2] + 0.1); }
            dm.property(3).expression = "var T=[" + tg.map(function (x) { return x.toFixed(3); }).join(",") + "]; var g=0; for (var i=0;i<T.length;i++) if (time>T[i]-0.18 && time<T[i]+0.06) g=1; posterizeTime(15); g? 60+random(120):0;";
            var est = D.estatica ? imp(D.estatica, false) : null;
            for (i = 0; i < tg.length; i++) {
                var sl = est ? c.layers.add(est) : c.layers.addSolid([0.6, 0.6, 0.6], "estatica", W, H, 1, DUR); sl.name = "estatica cambio";
                if (est) { S(sl).setValue([W / est.width * 100 * 1.05, H / est.height * 100 * 1.05]); P(sl).setValue([W / 2, H / 2]); } else fx(sl, "ADBE Noise").property(1).setValue(100);
                sl.blendingMode = BlendingMode.SCREEN; O(sl).expression = "posterizeTime(12); 35+random(50);"; vida(sl, tg[i] - 0.12, tg[i] + 0.02);
            }
        }
        for (i = 0; i < cabs.length; i++) cabs[i].moveToBeginning();
        for (i = 0; i < D.tarjetas.length; i++) D.tarjetas[i].moveToBeginning();   // v10b: tarjetas de detalle sobre la presentadora
        if (D.autodestruccion && cabs.length) autodestruir(cabs[cabs.length - 1], D.autodestruccion);
        // barrido magenta a la entrada de la ficha
        var sw = shp("barrido magenta"), g = grp(sw, "m"); linea(g, [[-700, -1100], [320, -1100], [90, 1100], [-930, 1100]], true); fill(g, MAG);
        P(sw).setValueAtTime(D.barrido - 0.25, [W + 1100, H / 2]); P(sw).setValueAtTime(D.barrido + 0.2, [-1100, H / 2]); vida(sw, D.barrido - 0.25, D.barrido + 0.25);
        for (i = 1; i < S0.length; i++) { var g0 = (S0[i - 1].tipo === "cabeza" || S0[i - 1].tipo === "gancho") && !S0[i - 1].corte, g1 = (S0[i].tipo === "cabeza" || S0[i].tipo === "gancho"); if (g0 !== g1) franjas(S0[i].ini); }
        for (i = 0; i < S0.length; i++) if (S0[i].corte) franjas(S0[i].corte + 0.12);
        for (i = 0; i < D.insertos.length; i++) { franjas(D.insertos[i][1] + 0.12); franjas(D.insertos[i][2] + 0.1); }   // entrada y salida del inserto   // v9: el corte de la cabeza a la obra, tapado por franjas
        subtitulos();
        var tp = c.layers.add(imp("imagenes/texturas/Paper002_2k.jpg", false)); S(tp).setValue([H * 1.05 / tp.source.height * 100, H * 1.05 / tp.source.height * 100]); P(tp).setValue([W / 2, H / 2]); mult(tp, 8);
        if (D.estilo && D.estilo.vhs) vhs();
        var gn = c.layers.addSolid([0, 0, 0], "grano", W, H, 1, DUR); gn.adjustmentLayer = true; fx(gn, "ADBE Noise").property(1).setValue(6);
        for (i = 0; i < D.voces.length; i++) { var V = c.layers.add(imp(D.voces[i].wav, false)); V.name = D.voces[i].id + " voz"; V.startTime = D.voces[i].start; }
        if (D.musica) { var mu = c.layers.add(imp(D.musica, false)); mu.name = "Musica"; mu.outPoint = DUR; var nv = D.musica.indexOf("elegida") >= 0 ? 0 : -13.2, al = mu.property("Audio").property("Audio Levels"); al.setValueAtTime(0, [nv, nv]); al.setValueAtTime(Math.max(0, DUR - 1.8), [nv, nv]); al.setValueAtTime(DUR, [-48, -48]); }   // v10c: musica propia ya normalizada; se apaga al final
        return "ok " + c.numLayers + " capas\n" + D.medidas.join("\n");
    }
    // la firma del final: el narrador se autodestruye de una forma ligada a la historia (1.6 s antes del final)
    function autodestruir(L, tipo) {
        var t0 = DUR - 1.7, t1 = DUR - 0.25, op = O(L);
        for (var i = c.numLayers; i >= 1; i--) if (c.layer(i).name.indexOf("copia menta") === 0 && c.layer(i).outPoint > t0) c.layer(i).outPoint = t0;
        try {
            if (tipo === "static_dissolve" || tipo === "glitch_out") {
                var td = fx(L, "ADBE Turbulent Displace"); td.property("Amount").setValueAtTime(t0, 0); td.property("Amount").setValueAtTime(t1, 260); td.property("Size").setValue(18);
                td.property("Evolution").expression = "time*900;";
                var nz = fx(L, "ADBE Noise"); nz.property(1).setValueAtTime(t0, 0); nz.property(1).setValueAtTime(t1, 100);
                op.expression = "time<" + t0 + "?value: (posterizeTime(15), Math.max(0, 1-(time-" + t0 + ")/" + (t1 - t0) + ")*(random()>0.25?100:15));";
            } else if (tipo === "melt") {
                var sc = S(L), v = sc.value; sc.setValueAtTime(t0, v); sc.setValueAtTime(t1, [v[0] * 1.06, v[1] * 1.35]);
                var tm = fx(L, "ADBE Turbulent Displace"); tm.property("Amount").setValueAtTime(t0, 0); tm.property("Amount").setValueAtTime(t1, 180); tm.property("Size").setValue(60);
                op.setValueAtTime(t1 - 0.4, op.value); op.setValueAtTime(t1, 0);
            } else if (tipo === "burn") {
                var bf = fx(L, "CC Burn Film"); bf.property("Evolution").setValueAtTime(t0, 0); bf.property("Evolution").setValueAtTime(t1, 110);
            } else if (tipo === "sparks") {
                var pw = fx(L, "CC Particle World"); pw.property("Birth Rate").setValueAtTime(t0, 0); pw.property("Birth Rate").setValueAtTime(t0 + 0.2, 8); pw.property("Birth Rate").setValueAtTime(t1, 0);
                op.expression = "time<" + t0 + "?value: (posterizeTime(20), Math.max(0, 1-(time-" + t0 + ")/" + (t1 - t0) + ")*(random()>0.4?100:0));";
            } else if (tipo === "smoke") {
                var fb = fx(L, "ADBE Fast Box Blur"); fb.property(1).setValueAtTime(t0, 0); fb.property(1).setValueAtTime(t1, 40);
                var ts = fx(L, "ADBE Turbulent Displace"); ts.property("Amount").setValueAtTime(t0, 0); ts.property("Amount").setValueAtTime(t1, 140); ts.property("Size").setValue(120);
                op.setValueAtTime(t0, op.value); op.setValueAtTime(t1, 0);
            }
        } catch (e) { op.setValueAtTime(t0, op.value); op.setValueAtTime(t1, 0); }   // efecto no disponible: al menos se apaga
        if (D.estatica && (tipo === "static_dissolve" || tipo === "glitch_out")) {
            var st = c.layers.add(imp(D.estatica, false)); st.name = "estatica final"; S(st).setValue([W / st.source.width * 105, H / st.source.height * 105]); P(st).setValue([W / 2, H / 2]);
            st.blendingMode = BlendingMode.SCREEN; O(st).setValueAtTime(t0 + 0.4, 0); O(st).setValueAtTime(t1, 85); O(st).setValueAtTime(DUR, 100); vida(st, t0 + 0.4, DUR);
        }
    }
    // look VHS (estilo con "vhs": true): sangrado de color, lineas de escaneo, banda de tracking, PLAY + contador, vineta, color lavado
    function vhs() {
        var v = D.estilo.vhs === true ? {} : D.estilo.vhs, tc = v.texto || "PLAY \u25B6";
        var cb = c.layers.addSolid([0, 0, 0], "VHS color", W, H, 1, DUR); cb.adjustmentLayer = true;
        try { var ch = fx(cb, "ADBE Channel Blur"); ch.property(1).setValue(7); ch.property(3).setValue(5); ch.property(5).setValue(2); } catch (e) {}   // rojo y azul sangran (eje horizontal)
        sat(cb, -18);
        try { fx(cb, "ADBE Fast Box Blur").property(1).setValue(0.8); } catch (e) {}
        var ex = fx(cb, "ADBE Brightness & Contrast 2"); ex.property(1).setValue(-6); ex.property(2).setValue(12);
        // lineas de escaneo: un patron de franjas finas en Multiply
        var sl = shp("VHS scanlines"); for (var i = 0; i < 64; i++) { var g = grp(sl, "l" + i); rect(g, W, 2, 0); fill(g, "#000000"); vec(g).property(2); g.property("ADBE Vector Transform Group").property("ADBE Vector Position").setValue([0, -H / 2 + i * 30 + 15]); }
        P(sl).setValue([W / 2, H / 2]); P(sl).expression = "value+[0, (time*90)%30];"; O(sl).setValue(16); sl.blendingMode = BlendingMode.MULTIPLY;
        // banda de tracking: una franja de ruido que baja cada pocos segundos
        var tb = c.layers.addSolid([0.5, 0.5, 0.5], "VHS tracking", W, 70, 1, DUR); var fn = fx(tb, "ADBE Fractal Noise");
        fn.property("Contrast").setValue(260); fn.property("Uniform Scaling").setValue(0); fn.property("Scale Width").setValue(900); fn.property("Scale Height").setValue(12); fn.property("Evolution").expression = "time*1400;";
        tb.blendingMode = BlendingMode.SCREEN; P(tb).expression = "var p=(time%7.3)/1.6; [540, p<1? -60+p*(1920+120) : -200];"; O(tb).expression = "posterizeTime(12); 22+random(18);";
        // vineta
        var vg = c.layers.addSolid([0, 0, 0], "VHS vineta", W, H, 1, DUR); var mk = vg.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"), sh = new Shape(), K = 0.5523, hw = W * 0.62, hh = H * 0.6;
        sh.vertices = [[540, 960 - hh], [540 + hw, 960], [540, 960 + hh], [540 - hw, 960]]; sh.inTangents = [[-hw * K, 0], [0, -hh * K], [hw * K, 0], [0, hh * K]]; sh.outTangents = [[hw * K, 0], [0, hh * K], [-hw * K, 0], [0, -hh * K]]; sh.closed = true;
        mk.property("ADBE Mask Shape").setValue(sh); mk.inverted = true; mk.property("ADBE Mask Feather").setValue([380, 380]); O(vg).setValue(55);
        // PLAY + contador (Courier), arriba a la izquierda, dentro de la zona segura
        var t1 = texto(tc, "CourierNewPS-BoldMT", 28, "#F7F8F4", ParagraphJustification.LEFT_JUSTIFY); t1.name = "VHS play"; P(t1).setValue([60, 118]);   // arriba de las etiquetas (decorativo) O(t1).expression = "posterizeTime(2); time%2<1.6?85:0;";
        var t2 = texto("SP 0:00:00", "CourierNewPS-BoldMT", 26, "#F7F8F4", ParagraphJustification.LEFT_JUSTIFY); t2.name = "VHS contador"; P(t2).setValue([60, 150]); O(t2).setValue(80);
        t2.property("ADBE Text Properties").property("ADBE Text Document").expression = "var s=Math.floor(time); 'SP 0:'+('0'+Math.floor(s/60)).slice(-2)+':'+('0'+(s%60)).slice(-2);";
        var e1 = fx(t1, "ADBE Glo2"); try { e1.property(3).setValue(0.4); } catch (e) {}
    }
    function subtitulos() {
        var L = D.subs, Y = D.yBarra;
        for (var i = 0; i < L.length; i++) {
            var sb = L[i], txt = [], S0 = [];
            for (var j = 0; j < sb.words.length; j++) { txt.push(sb.words[j].w); S0.push(sb.words[j].s); }
            var tl = texto(txt.join(" "), "Impact", 74, "#FFFFFF"); tl.name = "SUB " + (i + 1) + " " + txt.join(" ").substr(0, 30);
            var r = centrar(tl); P(tl).setValue([W / 2, Y]); R(tl).setValue(-1); vida(tl, sb.ini, sb.fin);
            var A = tl.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            A.property("ADBE Text Animator Properties").addProperty("ADBE Text Fill Color").setValue(rgb(LIME));
            var sel = A.property("ADBE Text Selectors").addProperty("ADBE Text Expressible Selector"); sel.property("ADBE Text Range Type2").setValue(3);
            sel.property("ADBE Text Expressible Amount").expression = "var S=[" + S0.join(",") + "], cur=-1; for (var q=0;q<S.length;q++) if (time>=S[q]) cur=q; (textIndex-1)===cur?100:0;";
            var br = shp("barra " + (i + 1)), bg = grp(br, "b"); rect(bg, r.width + 90, 112, 0); fill(bg, INK); P(br).setValue([W / 2, Y]); R(br).setValue(-1);
            aspero(br, 6, 34, 6); vida(br, sb.ini, sb.fin); br.moveAfter(tl);
        }
    }
    return { build: build };
})();
