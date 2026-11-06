// shorts-factory desktop app (Electron main process).
// - Talks to Claude through the Claude Agent SDK (the Claude Code CLI logged in on this machine): the repo's skill,
//   CLAUDE.md and docs are loaded (settingSources), and the app hands Claude the MCP servers in config "mcp"
//   (Motion DNA for After Effects, Motion DNA Blender); claude.ai connectors (Figma, Krea, Flora...) come from the account.
// - Runs the factory and the engine scripts (python) and streams their output.
// - Checks every connection (Claude, After Effects + Motion DNA bridge, Blender, ComfyUI, Qwen, keys).
const { app, BrowserWindow, ipcMain, shell, dialog } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn, execFile } = require("child_process");
const http = require("http");

const REPO = path.resolve(__dirname, "..");
const cfgFile = fs.existsSync(path.join(REPO, "config/local.json")) ? "config/local.json" : "config/local.example.json";
const CFG = JSON.parse(fs.readFileSync(path.join(REPO, cfgFile), "utf8"));
const PY = CFG.python_tools || "python";
const BRANDS = CFG.brands_dir || path.join(REPO, "brands");
let win, session = null, abort = null;
const pending = new Map();   // permission requests waiting for the user

function send(ch, data) { if (win && !win.isDestroyed()) win.webContents.send(ch, data); }
const readJSON = (p, d = null) => { try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { return d; } };
const listDirs = (p) => (fs.existsSync(p) ? fs.readdirSync(p, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name) : []);

function envKeys() {
  const out = {};
  try {
    for (const l of fs.readFileSync(CFG.env_file, "utf8").split(/\r?\n/)) {
      const m = l.match(/^([A-Z0-9_]+)=(.*)$/); if (m) out[m[1]] = !!m[2].trim();
    }
  } catch (e) {}
  return out;   // only presence, never the values
}

function ping(url) {
  return new Promise((res) => {
    const r = http.get(url, { timeout: 2500 }, (x) => { x.resume(); res(x.statusCode < 500); });
    r.on("error", () => res(false)); r.on("timeout", () => { r.destroy(); res(false); });
  });
}
function procs() {
  return new Promise((res) => execFile("tasklist", ["/fo", "csv", "/nh"], { windowsHide: true }, (e, out) => res((out || "").toLowerCase())));
}

ipcMain.handle("status", async () => {
  const p = await procs(), k = envKeys(), md = CFG.motion_dna;
  const bridge = fs.existsSync(path.join(md, "bridge/outbox/_bridge_started.txt"));
  const claudeV = await new Promise((r) => execFile("claude", ["--version"], { shell: true, windowsHide: true }, (e, o) => r(e ? null : o.trim())));
  const s = [
    { id: "claude", name: "Claude (Agent SDK)", ok: !!claudeV, detail: claudeV || "install Claude Code and log in: npm i -g @anthropic-ai/claude-code" },
    { id: "ae", name: "After Effects", ok: p.includes("afterfx.exe"), detail: p.includes("afterfx.exe") ? "running" : "not running" },
    { id: "mdna", name: "Motion DNA bridge", ok: bridge && p.includes("afterfx.exe"), detail: bridge ? "bridge started (panel docked)" : "open AE with the Motion DNA panel" },
    { id: "blender", name: "Blender", ok: p.includes("blender.exe"), detail: p.includes("blender.exe") ? "running (Motion DNA add-on)" : (fs.existsSync(CFG.blender || "") ? "installed, not running" : "not found") },
    { id: "figma", name: "Figma", ok: null, detail: "through the Claude account's connectors (checked when Claude starts)" },
    { id: "h3", name: "ComfyUI H3 / ACE", ok: await ping(CFG.comfy_h3.url + "/system_stats"), detail: CFG.comfy_h3.url },
    { id: "klein", name: "ComfyUI Klein", ok: await ping(CFG.comfy_klein.url + "/system_stats"), detail: CFG.comfy_klein.url },
    { id: "qwen", name: "QwenStudio", ok: CFG.qwen ? await ping(CFG.qwen.url) : false, detail: CFG.qwen ? CFG.qwen.url : "not configured" },
  ];
  for (const [id, name] of [["ELEVENLABS_API_KEY", "ElevenLabs"], ["GEMINI_API_KEY", "Nano Banana (Gemini)"], ["SEEDANCE_API_KEY", "Seedance"], ["SUNO_API_KEY", "Suno"], ["ASSETS_API_KEY", "Generic asset API"], ["POSTWIRE_API_KEY", "PostWire (TikTok)"]])
    s.push({ id, name, ok: !!k[id], detail: k[id] ? "key present" : "no key in " + CFG.env_file });
  return s;
});

ipcMain.handle("library", (e, brand) => {
  const L = path.join(REPO, "library"), B = brand ? path.join(BRANDS, brand) : null;
  const both = (sub) => [...(B ? listDirs(path.join(B, sub)).map((n) => [path.join(B, sub), n, true]) : []), ...listDirs(path.join(L, sub)).map((n) => [path.join(L, sub), n, false])];
  const jsonFiles = (sub) => [...(B && fs.existsSync(path.join(B, sub)) ? fs.readdirSync(path.join(B, sub)).filter((f) => f.endsWith(".json")).map((f) => path.join(B, sub, f)) : []),
    ...fs.readdirSync(path.join(L, sub)).filter((f) => f.endsWith(".json")).map((f) => path.join(L, sub, f))];
  const chars = both("characters").filter(([b, c]) => fs.existsSync(path.join(b, c, "character.json"))).map(([b, c, own]) => {
    const j = readJSON(path.join(b, c, "character.json"), {});
    const d = path.join(b, c);
    return { slug: c, own, nombre: j.nombre, descripcion: j.descripcion, maestro: path.join(d, j.maestro || ""),
      looks: Object.entries(j.looks || {}).map(([k, v]) => ({ key: k, imagen: path.join(d, v.imagen), ropa: v.ropa })) };
  });
  const styles = jsonFiles("styles").map((f) => readJSON(f)).filter(Boolean);
  const templates = both("templates").map(([b, t]) => readJSON(path.join(b, t, "template.json"))).filter(Boolean);
  const pdir = path.join(L, "platforms");
  const platforms = fs.existsSync(pdir) ? fs.readdirSync(pdir).filter((f) => f.endsWith(".json")).map((f) => readJSON(path.join(pdir, f))) : [];
  // finished videos of every brand, so the library can play an example of each style and template
  const examples = [];
  for (const b of listDirs(BRANDS)) {
    const W = path.join(BRANDS, b, "proyectos");
    for (const d of listDirs(W)) {
      const pj = readJSON(path.join(W, d, "proyecto.json"), null); if (!pj) continue;
      const base = pj.slug || d;
      const video = [`${base}_AE.mp4`, `${base}.mp4`].map((f) => path.join(W, d, f)).find((f) => fs.existsSync(f));
      if (video) examples.push({ brand: b, slug: d, tema: pj.tema || pj.artista, estilo: pj.estilo, plantilla: pj.plantilla, video });
    }
  }
  // a style may also point to older example folders with a contact sheet (no video)
  for (const s of styles) s.hojas = (s.ejemplos || []).map((e) => path.join(REPO, e, "contact_sheet.jpg")).filter((f) => fs.existsSync(f));
  return { chars, styles, templates, platforms, examples, hooks: readJSON(path.join(L, "hooks.json"), []), techniques: readJSON(path.join(L, "techniques/techniques.json"), []) };
});

ipcMain.handle("projects", (e, brand) => {
  const W = path.join(BRANDS, brand || "_general", "proyectos");
  return listDirs(W).filter((d) => fs.existsSync(path.join(W, d, "proyecto.json"))).map((d) => {
    const pj = readJSON(path.join(W, d, "proyecto.json"), {});
    const done = fs.readdirSync(path.join(W, d)).filter((f) => f.startsWith(".done_")).map((f) => f.slice(6));
    // the finished cut is the After Effects render; the plain mp4 is the draft before it
    const base = pj.slug || d;
    const cut = [`${base}_AE.mp4`, `${base}.mp4`].map((f) => path.join(W, d, f)).find((f) => fs.existsSync(f)) || null;
    const st = cut ? fs.statSync(cut) : fs.statSync(path.join(W, d, "proyecto.json"));
    return { slug: d, tema: pj.tema || pj.artista, personaje: pj.personaje, look: pj.look, estilo: pj.estilo, plataformas: pj.plataformas || [], done,
      video: cut, final: !!cut && cut.endsWith("_AE.mp4"), mb: cut ? +(st.size / 1048576).toFixed(1) : 0, when: st.mtimeMs, dir: path.join(W, d),
      // publishing (docs/PUBLISHING.md): the light copy and where it went
      pub: fs.existsSync(path.join(W, d, `${base}_pub.mp4`)) ? path.join(W, d, `${base}_pub.mp4`) : null,
      publicado: readJSON(path.join(W, d, "publicado.json"), null), qc: readJSON(path.join(W, d, "qc.json"), null) };
  }).sort((a, b) => b.when - a.when);
});

ipcMain.handle("brands", () => listDirs(BRANDS).filter((b) => fs.existsSync(path.join(BRANDS, b, "brand.json"))).map((b) => ({ ...readJSON(path.join(BRANDS, b, "brand.json"), {}), dir: path.join(BRANDS, b) })));
ipcMain.handle("saveBrand", (e, b) => { fs.writeFileSync(path.join(BRANDS, b.slug, "brand.json"), JSON.stringify(b, null, 1)); return true; });
ipcMain.handle("folders", (e, brand) => {
  const out = {};
  for (const k of ["references", "assets", "kit", "music", "research"]) {
    const p = path.join(BRANDS, brand || "_general", k);
    out[k] = listDirs(p).map((d) => ({ slug: d, dir: path.join(p, d), files: fs.readdirSync(path.join(p, d)) }));
  }
  return out;
});

// every asset of a brand (kit, assets, references, music) and of each episode (artworks and reconstructions, start frames,
// the self-destruct, music takes, sound), grouped by folder; folders starting with "_" (layers, discarded) are skipped
const MEDIA = { image: /\.(png|jpe?g|webp|gif)$/i, video: /\.(mp4|mov|webm)$/i, audio: /\.(wav|mp3|m4a|ogg)$/i };
const kindOf = (f) => Object.keys(MEDIA).find((k) => MEDIA[k].test(f));
function mediaGroups(dir, label, depth = 2) {
  const out = [];
  const walk = (d, name, lvl) => {
    if (!fs.existsSync(d)) return;
    const ents = fs.readdirSync(d, { withFileTypes: true });
    const files = ents.filter((e) => e.isFile() && kindOf(e.name)).map((e) => ({ path: path.join(d, e.name), name: e.name, kind: kindOf(e.name) }));
    if (files.length) out.push({ group: name, dir: d, files });
    if (lvl < depth) for (const e of ents) if (e.isDirectory() && !e.name.startsWith("_")) walk(path.join(d, e.name), name + " / " + e.name, lvl + 1);
  };
  walk(dir, label, 1);
  return out;
}
ipcMain.handle("assetsOf", (e, brand) => {
  const B = path.join(BRANDS, brand || "_general");
  const groups = [...mediaGroups(path.join(B, "kit"), "Kit"), ...mediaGroups(path.join(B, "assets"), "Assets"),
    ...mediaGroups(path.join(B, "references"), "References", 1), ...mediaGroups(path.join(B, "music"), "Music and voice", 2)];
  const W = path.join(B, "proyectos");
  const episodes = listDirs(W).filter((d) => fs.existsSync(path.join(W, d, "proyecto.json"))).map((d) => {
    const P = path.join(W, d), pj = readJSON(path.join(P, "proyecto.json"), {});
    return { slug: d, tema: pj.tema || pj.artista, dir: P, creditos: readJSON(path.join(P, "obras", "CREDITOS.json"), null),
      groups: [...mediaGroups(path.join(P, "obras"), "Artworks and reconstructions", 1), ...mediaGroups(path.join(P, "inicios"), "Start frames", 1),
        ...mediaGroups(path.join(P, "final"), "Self-destruct ending", 1), ...mediaGroups(path.join(P, "musica"), "Music takes", 1),
        ...mediaGroups(path.join(P, "ae", "sound"), "Sound design", 1)] };
  });
  return { dir: B, groups, episodes };
});

// python: factory.py or engine/<script>.py, output streamed to the log
ipcMain.handle("run", (e, { script, args, tag }) => new Promise((resolve) => {
  const file = script === "factory" ? path.join(REPO, "factory.py") : path.join(REPO, "engine", script + ".py");
  const p = spawn(PY, ["-u", file, ...args], { cwd: REPO, env: { ...process.env, PYTHONIOENCODING: "utf-8" }, windowsHide: true });
  let out = "";
  const on = (d) => { const t = d.toString(); out += t; send("log", { tag, text: t }); };
  p.stdout.on("data", on); p.stderr.on("data", on);
  p.on("close", (code) => { send("log", { tag, text: `\n[${tag}] exit ${code}\n` }); resolve({ code, out }); });
}));

ipcMain.handle("workdir", () => BRANDS.split("\\").join("/"));
ipcMain.handle("open", (e, p) => shell.openPath(p));
ipcMain.handle("openUrl", (e, u) => (/^https:\/\//.test(u) ? shell.openExternal(u) : false));
ipcMain.handle("pickFile", async (e, filters) => (await dialog.showOpenDialog(win, { properties: ["openFile"], filters })).filePaths[0] || null);
ipcMain.handle("readFile", (e, p) => { try { return fs.readFileSync(p, "utf8"); } catch (x) { return null; } });

// ---------- Claude
const AUTO = new Set(["Read", "Glob", "Grep", "WebSearch", "WebFetch", "TodoWrite", "Skill", "ToolSearch"]);
// values of the named keys from the .env, handed only to the MCP server that asks for them (config mcp.<name>.env_keys)
function envValues(names) {
  const out = {};
  try {
    for (const l of fs.readFileSync(CFG.env_file, "utf8").split(/\r?\n/)) {
      const m = l.match(/^([A-Z0-9_]+)=(.*)$/); if (m && names.includes(m[1]) && m[2].trim()) out[m[1]] = m[2].trim();
    }
  } catch (e) {}
  return out;
}
function mcpServers() {
  const out = {};
  for (const [k, v] of Object.entries(CFG.mcp || {}))
    out[k] = v.type === "http" ? { type: "http", url: v.url } : { type: "stdio", command: v.command, args: (v.args || []).map((a) => a.replace("{motion_dna}", CFG.motion_dna)),
      ...(v.env_keys ? { env: { ...process.env, ...envValues(v.env_keys) } } : {}) };
  return out;
}
const APP_CONTEXT = `You are running inside the shorts-factory desktop app (repo: ${REPO}). Follow .claude/skills/shorts-factory/SKILL.md
and CLAUDE.md. Brands live in ${BRANDS}/<brand>/ (brand.json, characters, styles, kit, music, references, research, proyectos, collects); a project is ${BRANDS}/<brand>/proyectos/<slug>. Work inside the brand the user picked. The user sees your text in a chat panel and approves tool calls in the app.
Speak the user's language in chat; write repo files in English. Quote USD before any paid generation.`;

ipcMain.handle("claude:send", async (e, { prompt, fresh, all }) => {
  const todos = all ?? CFG.claude_todos_los_conectores;   // strict = only config "mcp" (cheaper); all = every connector of the account
  const { query } = await import("@anthropic-ai/claude-agent-sdk");
  if (fresh) session = null;
  abort = new AbortController();
  const canUseTool = (toolName, input) => {
    if (AUTO.has(toolName) || /^mcp__.*__(list_|get_|ae_status|blender_status|check_layout|render_frame|read_)/.test(toolName))
      return Promise.resolve({ behavior: "allow", updatedInput: input });
    const id = Math.random().toString(36).slice(2);
    send("claude:permission", { id, toolName, input });
    return new Promise((res) => pending.set(id, (ok) => res(ok ? { behavior: "allow", updatedInput: input } : { behavior: "deny", message: "The user declined this in the app." })));
  };
  try {
    for await (const m of query({ prompt, options: { cwd: REPO, resume: session || undefined, settingSources: todos ? ["user", "project", "local"] : ["project", "local"],
      mcpServers: mcpServers(), strictMcpConfig: !todos, canUseTool, abortController: abort, systemPrompt: { type: "preset", preset: "claude_code", append: APP_CONTEXT } } })) {
      if (m.type === "system" && m.subtype === "init") { session = m.session_id; send("claude:init", { mcp: m.mcp_servers, model: m.model }); }
      else if (m.type === "assistant") for (const b of m.message.content) {
        if (b.type === "text") send("claude:text", b.text);
        else if (b.type === "tool_use") send("claude:tool", { name: b.name, input: b.input });
      } else if (m.type === "result") send("claude:done", { cost: m.total_cost_usd, turns: m.num_turns, error: m.is_error ? m.result : null });
    }
  } catch (x) { send("claude:done", { error: String(x) }); }
});
ipcMain.handle("claude:answer", (e, { id, ok }) => { const f = pending.get(id); if (f) { pending.delete(id); f(ok); } });
ipcMain.handle("claude:stop", () => { if (abort) abort.abort(); });

app.whenReady().then(() => {
  win = new BrowserWindow({ width: 1440, height: 920, backgroundColor: "#111414", title: "shorts-factory",
    webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, nodeIntegration: false } });
  win.loadFile(path.join(__dirname, "renderer/index.html"));
  // self-test: SF_SNAPSHOT=<folder> opens every view, saves a screenshot of each and the console errors, then quits
  if (process.env.SF_SNAPSHOT) {
    const dir = process.env.SF_SNAPSHOT, errs = [];
    fs.mkdirSync(dir, { recursive: true });
    win.webContents.on("console-message", (e, level, message) => { if (level >= 2) errs.push(message); });
    win.webContents.once("did-finish-load", async () => {
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      await wait(3500);
      for (const v of ["home", "short", "reference", "brand", "character", "assets", "platforms", "projects", "publish", "library"]) {
        await win.webContents.executeJavaScript(`document.querySelector('[data-view="${v}"]').click()`);
        await wait(1800);
        fs.writeFileSync(path.join(dir, v + ".png"), (await win.webContents.capturePage()).toPNG());
      }
      fs.writeFileSync(path.join(dir, "errors.txt"), errs.join("\n") || "no console errors");
      app.quit();
    });
  }
});
app.on("window-all-closed", () => app.quit());
