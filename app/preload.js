const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("api", {
  status: () => ipcRenderer.invoke("status"),
  library: () => ipcRenderer.invoke("library"),
  projects: () => ipcRenderer.invoke("projects"),
  folders: () => ipcRenderer.invoke("folders"),
  run: (script, args, tag) => ipcRenderer.invoke("run", { script, args, tag }),
  workdir: () => ipcRenderer.invoke("workdir"),
  open: (p) => ipcRenderer.invoke("open", p),
  pickFile: (filters) => ipcRenderer.invoke("pickFile", filters),
  readFile: (p) => ipcRenderer.invoke("readFile", p),
  claude: (prompt, fresh, all) => ipcRenderer.invoke("claude:send", { prompt, fresh, all }),
  answer: (id, ok) => ipcRenderer.invoke("claude:answer", { id, ok }),
  stop: () => ipcRenderer.invoke("claude:stop"),
  on: (ch, f) => ipcRenderer.on(ch, (e, d) => f(d)),
});
