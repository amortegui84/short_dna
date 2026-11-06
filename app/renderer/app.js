// shorts-factory app (renderer). Views = the paths: a Short from a topic, a style from a reference video, a brand kit from a
// URL, characters, assets, platform plans, projects and the library. Claude works in the side panel; every tool it wants to
// use that is not read-only waits for the user's approval; anything paid shows its estimated cost first.
const $ = (s, el = document) => el.querySelector(s);
const h = (t, a = {}, ...kids) => { const e = document.createElement(t); for (const [k, v] of Object.entries(a)) k.startsWith("on") ? e.addEventListener(k.slice(2), v) : k === "html" ? (e.innerHTML = v) : e.setAttribute(k, v); for (const c of kids.flat()) e.append(c instanceof Node ? c : document.createTextNode(c ?? "")); return e; };
const fileUrl = (p) => "file:///" + p.replace(/\\/g, "/");
let LIB = null, STATUS = [], CFGDIR = "", BRAND = "_general";
const BDIR = () => CFGDIR + "/" + BRAND;
const PAID_MCP = /krea|flora|generate_(image|video|audio|3d)|create_generations|run_canvas|upscale/i;

// ---------- side panel: Claude + log
document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => {
  document.querySelectorAll(".tabs button").forEach((x) => x.classList.toggle("on", x === b));
  $("#chat").classList.toggle("hidden", b.dataset.side !== "chat"); $("#log").classList.toggle("hidden", b.dataset.side !== "log");
});
const msg = (cls, text) => { const m = h("div", { class: "m " + cls }, text); $("#msgs").append(m); $("#msgs").scrollTop = 1e9; };
function askClaude(prompt, fresh = false) {
  msg("me", prompt.length > 400 ? prompt.slice(0, 400) + " …" : prompt);
  document.querySelector('[data-side="chat"]').click();
  return window.api.claude(prompt, fresh || $("#fresh").checked, $("#allconn").checked);
}
$("#ask").onsubmit = (e) => { e.preventDefault(); const q = $("#q").value.trim(); if (!q) return; $("#q").value = ""; askClaude(q); };
$("#stop").onclick = () => window.api.stop();
window.api.on("claude:text", (t) => msg("", t));
window.api.on("claude:tool", (t) => msg("tool", "→ " + t.name + " " + JSON.stringify(t.input).slice(0, 160)));
window.api.on("claude:init", (d) => {
  msg("sys", "Claude ready (" + (d.model || "") + "). MCP: " + (d.mcp || []).map((s) => s.name + (s.status === "connected" ? " ✓" : " ✗")).join(", "));
  const fig = (d.mcp || []).find((s) => /figma/i.test(s.name)); const st = STATUS.find((s) => s.id === "figma");
  if (st) { st.ok = fig ? fig.status === "connected" : false; st.detail = fig ? "Figma MCP " + fig.status : "no Figma connector in this Claude account"; paintMini(); }
});
window.api.on("claude:done", (d) => msg("sys", d.error ? "Error: " + d.error : `Done (${d.turns} turns${d.cost ? ", $" + d.cost.toFixed(3) : ""}).`));
window.api.on("claude:permission", (p) => {
  const paid = PAID_MCP.test(p.toolName);
  const box = h("div", { class: "ask" }, h("b", {}, (paid ? "PAID TOOL — check the cost Claude quoted. " : "") + "Claude wants to use " + p.toolName),
    h("pre", {}, JSON.stringify(p.input, null, 1).slice(0, 1500)),
    h("div", { class: "row" }, h("button", { onclick: () => { window.api.answer(p.id, true); box.remove(); } }, "Allow"),
      h("button", { class: "ghost", onclick: () => { window.api.answer(p.id, false); box.remove(); } }, "Deny")));
  $("#perm").append(box);
});
window.api.on("log", (d) => { $("#log").textContent += d.text; $("#log").scrollTop = 1e9; });

// ---------- cost gate: every paid action shows its estimate and waits for a yes
function confirmCost(est, title) {
  return new Promise((res) => {
    const paid = (est.filas || [est]).filter((f) => (f.usd ?? f.total_usd) > 0);
    if (!paid.length) return res(true);
    const rows = paid.map((f) => h("tr", {}, h("td", {}, f.etapa || f.proveedor), h("td", {}, f.proveedor), h("td", {}, `${f.cantidad} ${f.unidad}`),
      h("td", {}, "$" + (f.usd ?? f.total_usd).toFixed(2)), h("td", {}, f.verificado ? "verified " + f.verificado : "price not verified")));
    const d = h("dialog", {}, h("h2", {}, "Estimated cost: " + title), h("table", {}, h("tr", {}, ...["Stage", "Provider", "Quantity", "USD", "Price"].map((x) => h("th", {}, x))), rows),
      h("p", { class: "lead" }, `Total ~ $${(est.total_usd ?? 0).toFixed(2)}. Prices from library/costs.json (edit them there); real cost depends on plan and retries.`),
      h("div", { class: "row" }, h("button", { onclick: () => { d.close(); d.remove(); res(true); } }, "Accept and run"), h("button", { class: "ghost", onclick: () => { d.close(); d.remove(); res(false); } }, "Cancel")));
    d.style.cssText = "background:#191d1d;color:#f7f8f4;border:1px solid #e6128f;border-radius:10px;max-width:760px"; document.body.append(d); d.showModal();
  });
}
async function estimate(args) { const r = await window.api.run("costo", args, "cost"); try { return JSON.parse(r.out.trim().split("\n").pop()); } catch (e) { return { total_usd: 0, filas: [] }; } }
async function runFactory(slug, extra = []) {
  const est = await estimate(["proyecto", BDIR() + "/proyectos/" + slug]);
  if (!(await confirmCost(est, slug))) return;
  document.querySelector('[data-side="log"]').click();
  await window.api.run("factory", ["run", BRAND + "/" + slug, ...extra, "--yes"], slug);
}

// ---------- connections
function paintMini() { $("#conn-mini").replaceChildren(...STATUS.map((s) => h("span", { class: "dot " + (s.ok === null ? "unk" : s.ok ? "ok" : "bad"), title: s.name + ": " + s.detail }))); }
async function refreshStatus() { STATUS = await window.api.status(); paintMini(); return STATUS; }

// ---------- views
const V = {};
V.home = async () => {
  const st = await refreshStatus();
  const go = (v) => () => show(v);
  return [h("h1", {}, "What do you want to make?"), h("p", { class: "lead" }, "Pick a path. Claude researches, writes and drives Motion DNA in After Effects, Blender and Figma; you approve at checkpoints and see the cost before anything paid runs."),
    h("div", { class: "cards" },
      h("div", { class: "card", onclick: go("short") }, h("div", { class: "k" }, "Topic → Short"), h("p", {}, "Research a topic, write the script with platform hooks, generate and build the video.")),
      h("div", { class: "card", onclick: go("reference") }, h("div", { class: "k" }, "Reference → Style"), h("p", {}, "A link or a video file: measure it, describe its style, match it to Motion DNA, make a style.")),
      h("div", { class: "card", onclick: go("brand") }, h("div", { class: "k" }, "Brand → Kit"), h("p", {}, "A website: logo, colours and fonts, a Motion DNA brand and its components.")),
      h("div", { class: "card", onclick: go("character") }, h("div", { class: "k" }, "Character"), h("p", {}, "Pick one, describe a new one, or let Claude propose one for your idea.")),
      h("div", { class: "card", onclick: go("assets") }, h("div", { class: "k" }, "Assets"), h("p", {}, "Images, props and backgrounds with local models or paid APIs (cost first).")),
      h("div", { class: "card", onclick: go("platforms") }, h("div", { class: "k" }, "Platforms"), h("p", {}, "Strategy, hooks and a series plan for TikTok, Reels, Shorts and more."))),
    h("h2", {}, "Connections"),
    h("table", { class: "status" }, st.map((s) => h("tr", {}, h("td", {}, h("span", { class: "dot " + (s.ok === null ? "unk" : s.ok ? "ok" : "bad") })), h("td", {}, s.name), h("td", {}, s.detail)))),
    h("div", { class: "row" }, h("button", { class: "ghost", onclick: () => show("home") }, "Refresh"), h("button", { class: "ghost", onclick: () => askClaude("Check the connections: call ae_status (Motion DNA), blender_status (Motion DNA Blender) and tell me which MCP servers and claude.ai connectors (Figma, Krea, Flora) are available in this session.") }, "Ask Claude to test MCP"))];
};

function lookPicker(state) {
  const box = h("div", { class: "looks" });
  const paint = () => {
    const c = LIB.chars.find((x) => x.slug === state.character); box.replaceChildren();
    if (!c) return;
    for (const l of c.looks) box.append(h("div", { class: "look" + (state.look === l.key ? " on" : ""), onclick: () => { state.look = l.key; paint(); } }, h("img", { src: fileUrl(l.imagen) }), h("span", {}, l.key)));
  };
  paint(); return { box, paint };
}
const sel = (opts, val, on) => { const s = h("select", { onchange: (e) => on(e.target.value) }, opts.map(([v, t]) => { const o = h("option", { value: v }, t); if (v === val) o.selected = true; return o; })); return s; };

V.short = async () => {
  // the brand's own defaults (brand.json: plantilla, personaje, estilo_por_defecto) win over the first item of each list
  const B = (await window.api.brands()).find((x) => x.slug === BRAND) || {};
  const has = (list, v) => v && list.some((x) => x.slug === v) ? v : null;
  const st = { topic: "", platforms: B.plataformas?.length ? [...B.plataformas] : ["youtube_shorts"], template: has(LIB.templates, B.plantilla) || LIB.templates[0]?.slug,
    character: has(LIB.chars, B.personaje) || LIB.chars[0]?.slug, look: "", style: has(LIB.styles, B.estilo_por_defecto) || has(LIB.styles, B.estilo) || LIB.styles[0]?.slug,
    length: 60, lang: B.idioma || "English", notes: "" };
  const lp = lookPicker(st);
  const plats = h("div", { class: "chips" }, (LIB.platforms.length ? LIB.platforms : [{ slug: "youtube_shorts", nombre: "YouTube Shorts" }, { slug: "tiktok", nombre: "TikTok" }, { slug: "instagram_reels", nombre: "Instagram Reels" }])
    .map((p) => { const c = h("span", { class: st.platforms.includes(p.slug) ? "on" : "" }, p.nombre || p.slug); c.onclick = () => { st.platforms = st.platforms.includes(p.slug) ? st.platforms.filter((x) => x !== p.slug) : [...st.platforms, p.slug]; c.classList.toggle("on"); }; return c; }));
  const slug = h("input", { placeholder: "06_vermeer" });
  return [h("h1", {}, "Topic → Short"), h("p", { class: "lead" }, "Claude researches with sources, picks a hook for each platform and writes the script. Nothing is generated until you approve it."),
    h("div", { class: "grid2" },
      h("div", {}, h("label", {}, "Topic"), h("input", { placeholder: "Johannes Vermeer and the camera obscura", oninput: (e) => st.topic = e.target.value }),
        h("label", {}, "Project id"), slug,
        h("label", {}, "Platforms"), plats,
        h("label", {}, "Template"), sel(LIB.templates.map((t) => [t.slug, t.nombre]), st.template, (v) => st.template = v),
        h("label", {}, "Style"), sel(LIB.styles.map((s) => [s.slug, s.nombre]), st.style, (v) => st.style = v),
        h("div", { class: "grid2" }, h("div", {}, h("label", {}, "Length (s)"), h("input", { type: "number", value: 60, oninput: (e) => st.length = +e.target.value })),
          h("div", {}, h("label", {}, "Language"), h("input", { value: st.lang, oninput: (e) => st.lang = e.target.value }))),
        h("label", {}, "Notes for Claude"), h("textarea", { rows: 3, oninput: (e) => st.notes = e.target.value })),
      h("div", {}, h("label", {}, "Character"), sel(LIB.chars.map((c) => [c.slug, c.nombre || c.slug]), st.character, (v) => { st.character = v; st.look = ""; lp.paint(); }),
        h("label", {}, "Look"), lp.box)),
    h("div", { class: "row" }, h("button", { onclick: async () => {
      if (!st.topic || !slug.value) return alert("Topic and project id");
      const args = ["new", slug.value, "--brand", BRAND, "--topic", st.topic, "--template", st.template, "--character", st.character, "--style", st.style]; if (st.look) args.push("--look", st.look);
      const r = await window.api.run("factory", args, "new");
      if (r.code) return alert(r.out);
      askClaude(PROMPTS.short({ ...st, brand: BRAND, slug: slug.value, dir: BDIR() + "/proyectos/" + slug.value }), true);
    } }, "Create project and ask Claude for research + script"))];
};

V.reference = async () => {
  let src = ""; const slug = h("input", { placeholder: "calm-editorial-ref" }); const link = h("input", { placeholder: "https://www.youtube.com/shorts/… or TikTok / Instagram / Vimeo link", oninput: (e) => src = e.target.value });
  const out = h("div", {});
  const f = await window.api.folders();
  return [h("h1", {}, "Reference → Style"), h("p", { class: "lead" }, "Give a video whose style you want. The app measures it (cuts, pacing, motion energy, palette, one frame per shot); Claude describes it, matches it to Motion DNA and proposes a style. Only use videos you are allowed to study; they stay out of git."),
    h("div", { class: "grid2" }, h("div", {}, h("label", {}, "Link"), link, h("div", { class: "row" }, h("button", { class: "ghost", onclick: async () => { const p = await window.api.pickFile([{ name: "Video", extensions: ["mp4", "mov", "webm", "mkv"] }]); if (p) { src = p; link.value = p; } } }, "…or pick a file")),
      h("label", {}, "Name"), slug)),
    h("div", { class: "row" }, h("button", { onclick: async () => {
      if (!src || !slug.value) return alert("Link or file, and a name");
      document.querySelector('[data-side="log"]').click();
      const r = await window.api.run("referencia", [src, slug.value, BRAND], "reference");
      if (r.code) return;
      const dir = BDIR() + "/references/" + slug.value;
      out.replaceChildren(h("img", { class: "sheet", src: fileUrl(dir + "/hoja.jpg") }), h("pre", {}, r.out.trim().split("\n").pop()));
      askClaude(PROMPTS.reference({ src, dir, slug: slug.value, motion_dna: "the Motion DNA repo" }), true);
    } }, "Analyse and ask Claude")), out,
    h("h2", {}, "Analysed references"), h("div", { class: "cards" }, f.references.map((r) => h("div", { class: "card", onclick: () => window.api.open(r.dir) }, h("h3", {}, r.slug), r.files.includes("hoja.jpg") ? h("img", { class: "sheet", src: fileUrl(r.dir + "/hoja.jpg") }) : "")))];
};

V.brand = async () => {
  const bs = await window.api.brands(); const b = bs.find((x) => x.slug === BRAND);
  if (!b) return [h("h1", {}, "Brand"), h("p", { class: "lead" }, "Pick a brand in the selector or create one (+ New brand). Every brand has its own folder: profile, characters, styles, kit, music, references, research, projects and collects.")];
  const url = h("input", { placeholder: "https://brand.com (optional: read logo, colours and fonts from the site)" }); const out = h("div", {});
  const field = (k, label, rows) => { const el = rows ? h("textarea", { rows }) : h("input", {}); el.value = typeof b[k] === "string" ? b[k] : JSON.stringify(b[k] || ""); el.oninput = () => { try { b[k] = typeof b[k] === "string" || rows ? el.value : JSON.parse(el.value); } catch (x) { b[k] = el.value; } }; return [h("label", {}, label), el]; };
  const showKit = async (dir) => {
    const k = JSON.parse(await window.api.readFile(dir + "/marca.json") || "{}");
    out.replaceChildren(h("div", {}, [...Object.values(k.colores_var || {}), ...(k.colores || [])].slice(0, 12).map((c) => h("span", { class: "sw", title: c, style: "background:" + c }))),
      h("p", { class: "lead" }, "Fonts: " + (k.fuentes || []).join(", ")), h("div", { class: "looks" }, (k.logos || []).map((l) => h("div", { class: "look" }, h("img", { src: fileUrl(dir + "/" + l), style: "object-fit:contain;background:#fff" }), h("span", {}, l)))));
  };
  return [h("h1", {}, b.nombre), h("p", { class: "lead" }, b.dir),
    h("div", { class: "grid2" }, h("div", {}, ...field("handle", "Handle"), ...field("audiencia", "Audience", 2), ...field("tono", "Tone of voice", 2), ...field("mensaje", "Underlying message", 2),
      ...field("plataformas", "Platforms (JSON list)")),
      h("div", {}, ...field("colores", "Colours (JSON)"), ...field("fuentes", "Fonts (JSON)"), ...field("personaje", "Character"), ...field("estilo", "Style"), ...field("plantilla", "Template"), ...field("figma", "Figma (JSON: url, file_key)"))),
    h("div", { class: "row" }, h("button", { onclick: async () => { await window.api.saveBrand(b); alert("Saved"); } }, "Save profile"), h("button", { class: "ghost", onclick: () => window.api.open(b.dir) }, "Open folder"),
      h("button", { class: "mag", onclick: () => askClaude(PROMPTS.brandBuild({ brand: b.slug, dir: b.dir }), true) }, "Build the brand with Claude")),
    h("h2", {}, "Read a website (optional)"), url,
    h("div", { class: "row" }, h("button", { class: "ghost", onclick: async () => {
      if (!url.value) return; const r = await window.api.run("marca", [url.value, BRAND], "brand"); if (r.code) return;
      const dir = BDIR() + "/references/web"; await showKit(dir); askClaude(PROMPTS.brand({ url: url.value, dir }), true);
    } }, "Read it and ask Claude")), out];
};

V.character = async () => {
  const st = { character: LIB.chars[0]?.slug, look: "" }; const lp = lookPicker(st);
  const desc = h("textarea", { rows: 3, placeholder: "A calm 60-year-old museum restorer with silver hair and round glasses, in a workshop full of canvases…" });
  const idea = h("textarea", { rows: 3, placeholder: "A channel about forgotten women inventors for teenagers on TikTok" });
  const prov = sel([["comfy_klein", "Flux Klein (local, free)"], ["zimage", "Z-Image (local, free)"], ["nano_banana", "Nano Banana (paid)"], ["krea", "Krea MCP (paid)"], ["flora", "Flora MCP (paid)"]], "comfy_klein", () => {});
  const outfit = h("input", { placeholder: "a camel trench coat over a black turtleneck" }); const pose = h("input", { placeholder: "head tilted toward the viewer's right, one hand on the desk" });
  return [h("h1", {}, "Characters"), h("p", { class: "lead" }, "Your presenter: launch an existing one, describe a new one, or let Claude propose one for an idea. Generated people only, or real people with their consent."),
    h("h2", {}, "Library"), sel(LIB.chars.map((c) => [c.slug, c.nombre || c.slug]), st.character, (v) => { st.character = v; lp.paint(); }),
    h("p", { class: "lead" }, LIB.chars.find((c) => c.slug === st.character)?.descripcion || ""), lp.box,
    h("h2", {}, "New look for this character"), h("div", { class: "grid2" }, h("div", {}, h("label", {}, "Outfit"), outfit), h("div", {}, h("label", {}, "Pose and head angle"), pose)),
    h("div", { class: "row" }, h("button", { class: "ghost", onclick: () => askClaude(PROMPTS.look({ character: st.character, outfit: outfit.value, pose: pose.value })) }, "Make look candidates (Klein, local)")),
    h("h2", {}, "Describe a new character"), desc, h("label", {}, "Image provider"), prov,
    h("div", { class: "row" }, h("button", { onclick: () => askClaude(PROMPTS.characterDescribe({ desc: desc.value, provider: prov.value }), true) }, "Create it with Claude")),
    h("h2", {}, "Let Claude propose one"), idea,
    h("div", { class: "row" }, h("button", { class: "mag", onclick: () => askClaude(PROMPTS.characterPropose({ idea: idea.value, platforms: [] }), true) }, "Propose 3 characters"))];
};

V.assets = async () => {
  const st = { provider: "comfy_klein", size: "768x1344", cutout: false, n: 1 }; const prompt = h("textarea", { rows: 3, placeholder: "an antique brass magnifying glass on paper, studio light, isolated" });
  const name = h("input", { placeholder: "lupa_laton" }); const refs = []; const out = h("div", { class: "looks" });
  const f = await window.api.folders();
  const viaMcp = (p) => p === "krea" || p === "flora";
  return [h("h1", {}, "Assets"), h("p", { class: "lead" }, "Props, backgrounds, stickers, textures. Local models cost nothing; paid APIs show the estimate first. Krea and Flora run through Claude's MCP connectors."),
    h("div", { class: "grid2" }, h("div", {}, h("label", {}, "Prompt"), prompt, h("label", {}, "File name"), name,
      h("div", { class: "row" }, h("button", { class: "ghost", onclick: async () => { const p = await window.api.pickFile([{ name: "Image", extensions: ["png", "jpg", "jpeg", "webp"] }]); if (p) { refs.push(p); out.append(h("div", { class: "look" }, h("img", { src: fileUrl(p) }), h("span", {}, "reference"))); } } }, "Add reference image"))),
      h("div", {}, h("label", {}, "Provider"), sel([["qwen_layered", "Qwen-Image-Layered · local, alpha"], ["comfy_klein", "Flux Klein · local"], ["zimage", "Z-Image · local"], ["qwen_style", "Qwen style transfer · local (ref 1 = photo, ref 2 = style)"], ["nano_banana", "Nano Banana · paid"], ["generic_http", "Generic API · paid"], ["krea", "Krea · MCP, paid"], ["flora", "Flora · MCP, paid"]], st.provider, (v) => st.provider = v),
        h("label", {}, "Size"), sel([["768x1344", "9:16"], ["1344x768", "16:9"], ["1024x1024", "1:1"], ["1080x1350", "4:5"]], st.size, (v) => st.size = v),
        h("label", {}, "How many"), h("input", { type: "number", value: 1, min: 1, max: 8, oninput: (e) => st.n = +e.target.value }),
        h("label", { class: "small" }, h("input", { type: "checkbox", onchange: (e) => st.cutout = e.target.checked }), "cut out the background"))),
    h("div", { class: "row" }, h("button", { onclick: async () => {
      if (!prompt.value || !name.value) return alert("Prompt and file name");
      const dest = BDIR() + "/assets/" + name.value;
      const est = await estimate(["asset", st.provider, "--n", String(st.n)]);
      if (!(await confirmCost({ ...est, filas: [{ ...est, etapa: "asset", usd: est.total_usd }] }, name.value))) return;
      if (viaMcp(st.provider)) return askClaude(PROMPTS.assetClaude({ prompt: prompt.value, size: st.size, cutout: st.cutout, provider: st.provider, out: dest, target: "the asset library" }));
      document.querySelector('[data-side="log"]').click();
      for (let i = 0; i < st.n; i++) {
        const r = await window.api.run("assets", ["--provider", st.provider, "--prompt", prompt.value, "--out", `${dest}/${name.value}_${i + 1}.png`, "--size", st.size, "--seed", String(7 + i), ...(refs.length ? ["--refs", ...refs] : []), ...(st.cutout ? ["--cutout"] : [])], "asset");
        const p = r.out.trim().split("\n").pop(); if (!r.code) out.append(h("div", { class: "look" }, h("img", { src: fileUrl(p) }), h("span", {}, p.split(/[\\/]/).pop())));
      }
    } }, "Generate")), out,
    h("h2", {}, "Asset folders"), h("div", { class: "cards" }, f.assets.map((a) => h("div", { class: "card", onclick: () => window.api.open(a.dir) }, h("h3", {}, a.slug), h("p", {}, a.files.length + " files"))))];
};

V.platforms = async () => {
  const st = { platforms: [], topic: "" }; const topic = h("input", { placeholder: "art history mysteries" });
  const P = LIB.platforms;
  return [h("h1", {}, "Platforms"), h("p", { class: "lead" }, "Each network has its own specs, length, hooks, CTA and AI-disclosure rule (library/platforms, sources in docs/PLATFORMS.md). Plan a series and repurpose one master per platform."),
    P.length ? h("table", {}, h("tr", {}, ...["Platform", "Ideal length", "Safe area", "Rewards", "AI disclosure"].map((x) => h("th", {}, x))),
      P.map((p) => h("tr", {}, h("td", {}, p.nombre || p.slug), h("td", {}, (p.specs?.ideal_s || []).join("-") + " s"), h("td", {}, JSON.stringify(p.specs?.safe_area || {})),
        h("td", {}, (p.algoritmo || []).slice(0, 3).join("; ")), h("td", {}, typeof p.ia_disclosure === "string" ? p.ia_disclosure : JSON.stringify(p.ia_disclosure || ""))))) : h("p", { class: "lead" }, "Platform strategies are being researched (library/platforms/)."),
    h("h2", {}, "Hooks"), h("div", { class: "chips" }, (LIB.hooks.hooks || LIB.hooks || []).map?.((k) => h("span", { title: k.definicion }, k.nombre || k.id)) || ""),
    h("h2", {}, "Plan a series"), h("label", {}, "Channel topic"), topic,
    h("div", { class: "chips" }, P.map((p) => { const c = h("span", {}, p.nombre || p.slug); c.onclick = () => { st.platforms = st.platforms.includes(p.slug) ? st.platforms.filter((x) => x !== p.slug) : [...st.platforms, p.slug]; c.classList.toggle("on"); }; return c; })),
    h("div", { class: "row" }, h("button", { onclick: () => askClaude(PROMPTS.platformPlan({ platforms: st.platforms.length ? st.platforms : ["youtube_shorts", "tiktok", "instagram_reels"], topic: topic.value, character: LIB.chars[0]?.slug, style: LIB.styles[0]?.slug, out: BDIR() + "/research/plan_" + (topic.value || "plan").replace(/\W+/g, "_") + ".md" }), true) }, "Plan with Claude"))];
};

V.projects = async () => {
  const ps = await window.api.projects(BRAND);
  const names = ["research", "script", "design", "obras", "retrato", "look", "inicios", "voz", "clips", "sts", "montaje", "mates", "musica", "ae", "render", "qc", "collect"];
  const url = (p) => "file:///" + encodeURI(p.split("\\").join("/"));
  const day = (ms) => new Date(ms).toLocaleDateString(undefined, { day: "numeric", month: "short" });
  const card = (p) => {
    const n = names.filter((x) => p.done.includes(x)).length;
    const thumb = p.video
      ? h("video", { src: url(p.video) + "#t=3", preload: "metadata", playsinline: "", onmouseenter: (e) => { e.target.muted = true; e.target.play(); }, onmouseleave: (e) => e.target.pause(), onclick: () => window.api.open(p.video) })
      : h("div", { class: "empty" }, "No video yet");
    return h("div", { class: "vid" }, thumb,
      h("div", { class: "meta" }, h("b", {}, p.slug), h("span", { class: "tag" + (p.final ? " on" : "") }, p.video ? (p.final ? "Final" : "Draft") : `${n}/${names.length} stages`)),
      h("p", {}, p.tema || ""),
      h("p", { class: "sub" }, [p.estilo, p.video ? `${p.mb} MB` : "", day(p.when)].filter(Boolean).join(" · ")),
      h("details", {}, h("summary", {}, `Stages ${n}/${names.length}`), h("div", { class: "chips" }, names.map((x) => h("span", { class: p.done.includes(x) ? "on" : "" }, x)))),
      h("div", { class: "row" }, p.video ? h("button", { onclick: () => window.api.open(p.video) }, "Play") : h("button", { onclick: () => runFactory(p.slug) }, "Run next"),
        h("button", { class: "ghost", onclick: () => window.api.open(p.dir) }, "Folder"),
        h("button", { class: "ghost", onclick: () => askClaude(PROMPTS.run({ slug: p.slug })) }, "With Claude")));
  };
  return [h("h1", {}, "Projects"), h("p", { class: "lead" }, "Every video of this brand, newest first. Hover to preview, click to play the finished cut; each one is a folder in work_dir with everything that made it."),
    ps.length ? h("div", { class: "gallery" }, ps.map(card)) : h("p", { class: "lead" }, "No projects yet: start with Topic → Short.")];
};

V.library = async () => [h("h1", {}, "Library"), h("p", { class: "lead" }, "What the system knows: styles, techniques and templates (library/), model notes (docs/models/), every lesson (docs/LEARNINGS.md)."),
  h("h2", {}, "Styles"), h("table", {}, LIB.styles.map((s) => h("tr", {}, h("td", {}, h("b", {}, s.nombre)), h("td", {}, h("div", {}, Object.values(s.tokens || {}).filter((v) => typeof v === "string").map((c) => h("span", { class: "sw", style: "background:" + c }))), (s.reglas || []).slice(0, 4).join(" · "))))),
  h("h2", {}, "Techniques"), h("table", {}, LIB.techniques.map((t) => h("tr", {}, h("td", {}, h("b", {}, t.nombre)), h("td", {}, t.uso), h("td", {}, t.como)))),
  h("h2", {}, "Templates"), h("table", {}, LIB.templates.map((t) => h("tr", {}, h("td", {}, h("b", {}, t.nombre)), h("td", {}, (t.estructura || []).map((s) => s.seccion).join(" → ")))))];

async function show(v) {
  document.querySelectorAll("#nav button[data-view]").forEach((b) => b.classList.toggle("on", b.dataset.view === v));
  LIB = await window.api.library(BRAND);
  $("#view").replaceChildren(h("p", { class: "lead" }, "…"));
  $("#view").replaceChildren(...(await V[v]()));
}
document.querySelectorAll("#nav button[data-view]").forEach((b) => b.onclick = () => show(b.dataset.view));
// ---------- brand selector: every view works inside the chosen brand (brands/<brand>/...)
async function paintBrands() {
  const bs = await window.api.brands();
  const s = h("select", { id: "brand-sel", onchange: (e) => { if (e.target.value === "+") return newBrand(); BRAND = e.target.value; try { localStorage.setItem("brand", BRAND); } catch (x) {} show(document.querySelector("#nav button.on")?.dataset.view || "home"); } },
    [["_general", "General"], ...bs.map((b) => [b.slug, b.nombre || b.slug]), ["+", "+ New brand"]].map(([v, t]) => { const o = h("option", { value: v }, t); if (v === BRAND) o.selected = true; return o; }));
  $("#brand-box").replaceChildren(h("label", {}, "Brand"), s);
}
function newBrand() {
  const name = h("input", { placeholder: "Cult Pixel" }), slug = h("input", { placeholder: "cult_pixel" }), handle = h("input", { placeholder: "@cult_pixel" });
  const plats = h("input", { value: "instagram_reels,tiktok,youtube_shorts" }), lang = h("input", { value: "English" });
  const d = h("dialog", {}, h("h2", {}, "New brand"), h("label", {}, "Name"), name, h("label", {}, "Id (folder)"), slug, h("label", {}, "Handle"), handle,
    h("label", {}, "Platforms"), plats, h("label", {}, "Language"), lang,
    h("div", { class: "row" }, h("button", { onclick: async () => {
      if (!slug.value || !name.value) return;
      const r = await window.api.run("factory", ["brand-new", slug.value, "--name", name.value, "--handle", handle.value, "--platforms", plats.value, "--lang", lang.value], "brand");
      d.close(); d.remove(); if (!r.code) { BRAND = slug.value; await paintBrands(); show("brand"); }
    } }, "Create"), h("button", { class: "ghost", onclick: () => { d.close(); d.remove(); paintBrands(); } }, "Cancel")));
  d.style.cssText = "background:#191d1d;color:#f7f8f4;border:1px solid #c1f157;border-radius:10px;width:420px"; document.body.append(d); d.showModal();
}
(async () => { CFGDIR = await window.api.workdir(); try { BRAND = localStorage.getItem("brand") || "_general"; } catch (x) {} await paintBrands(); show("home"); })();
