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
  for (const [id, name] of [["ELEVENLABS_API_KEY", "ElevenLabs"], ["GEMINI_API_KEY", "Nano Banana (Gemini)"], ["SEEDANCE_API_KEY", "Seedance"], ["SUNO_API_KEY", "Suno"], ["ASSETS_API_KEY", "Generic asset API"]])
    s.push({ id, name, ok: !!k[id], detail: k[id] ? "key present" : "no key in " + CFG.env_file });
  return s;
});

ipcMain.handle("library", () => {
  const L = path.join(REPO, "library");
  const chars = listDirs(path.join(L, "characters")).map((c) => {
    const j = readJSON(path.join(L, "characters", c, "character.json"), {});
    const d = path.join(L, "characters", c);
    return { slug: c, nombre: j.nombre, descripcion: j.descripcion, maestro: path.join(d, j.maestro || ""),
      looks: Object.entries(j.looks || {}).map(([k, v]) => ({ key: k, imagen: path.join(d, v.imagen), ropa: v.ropa })) };
  });
  const styles = fs.readdirSync(path.join(L, "styles")).filter((f) => f.endsWith(".json")).map((f) => readJSON(path.join(L, "styles", f)));
  const templates = listDirs(path.join(L, "templates")).map((t) => readJSON(path.join(L, "templates", t, "template.json")));
  const pdir = path.join(L, "platforms");
  const platforms = fs.existsSync(pdir) ? fs.readdirSync(pdir).filter((f) => f.endsWith(".json")).map((f) => readJSON(path.join(pdir, f))) : [];
  return { chars, styles, templates, platforms, hooks: readJSON(path.join(L, "hooks.json"), []), techniques: readJSON(path.join(L, "techniques/techniques.json"), []) };
});

ipcMain.handle("projects", () => {
  const W = CFG.work_dir;
  return listDirs(W).filter((d) => fs.existsSync(path.join(W, d, "proyecto.json"))).map((d) => {
    const pj = readJSON(path.join(W, d, "proyecto.json"), {});
    const done = fs.readdirSync(path.join(W, d)).filter((f) => f.startsWith(".done_")).map((f) => f.slice(6));
    const mp4 = path.join(W, d, `${pj.slug}.mp4`);
    return { slug: d, tema: pj.tema || pj.artista, personaje: pj.personaje, look: pj.look, estilo: pj.estilo, plataformas: pj.plataformas || [], done, video: fs.existsSync(mp4) ? mp4 : null, dir: path.join(W, d) };
  });
});

ipcMain.handle("folders", () => {
  const out = {};
  for (const k of ["referencias", "marcas", "assets"]) {
    const p = path.join(CFG.work_dir, k);
    out[k] = listDirs(p).map((d) => ({ slug: d, dir: path.join(p, d), files: fs.readdirSync(path.join(p, d)) }));
  }
  return out;
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

ipcMain.handle("workdir", () => CFG.work_dir.split("\\").join("/"));
ipcMain.handle("open", (e, p) => shell.openPath(p));
ipcMain.handle("pickFile", async (e, filters) => (await dialog.showOpenDialog(win, { properties: ["openFile"], filters })).filePaths[0] || null);
ipcMain.handle("readFile", (e, p) => { try { return fs.readFileSync(p, "utf8"); } catch (x) { return null; } });

// ---------- Claude
const AUTO = new Set(["Read", "Glob", "Grep", "WebSearch", "WebFetch", "TodoWrite", "Skill", "ToolSearch"]);
function mcpServers() {
  const out = {};
  for (const [k, v] of Object.entries(CFG.mcp || {}))
    out[k] = v.type === "http" ? { type: "http", url: v.url } : { type: "stdio", command: v.command, args: (v.args || []).map((a) => a.replace("{motion_dna}", CFG.motion_dna)) };
  return out;
}
const APP_CONTEXT = `You are running inside the shorts-factory desktop app (repo: ${REPO}). Follow .claude/skills/shorts-factory/SKILL.md
and CLAUDE.md. Projects live in ${CFG.work_dir}. The user sees your text in a chat panel and approves tool calls in the app.
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
      for (const v of ["home", "short", "reference", "brand", "character", "assets", "platforms", "projects", "library"]) {
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
