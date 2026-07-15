/*
 * MV Data Governance · shell de escritorio (Electron).
 *
 * Qué hace: muestra el launcher (React) mientras levanta el servidor local
 * de Streamlit en un puerto libre de 127.0.0.1, y cuando el puerto responde
 * carga el programa en la misma ventana. Al cerrar la ventana, apaga el
 * servidor. Todo corre en la máquina del usuario: el shell no hace ninguna
 * llamada a internet (misma promesa que el resto del producto).
 *
 * De dónde saca el servidor Python (en este orden):
 *   1. MVDG_SERVER_CMD (variable de entorno, para armados a medida)
 *   2. resources/server/ dentro de la app instalada (electron-builder)
 *      usando el Python del sistema
 *   3. la raíz del repositorio (modo desarrollo: ../app/app.py) con
 *      .venv/bin/python si existe, o python3/python del sistema
 *
 * La lógica de arranque (puerto libre, detectar Python, polling del
 * servidor) vive en lib/server-manager.js, sin depender de Electron, para
 * poder testearla con Node puro — ver lib/server-manager.test.js.
 */
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("node:path");
const fs = require("node:fs");
const sm = require("./lib/server-manager");

let win = null;
let serverProc = null;
let serverPort = null;

function sendStatus(key, detail) {
  if (win && !win.isDestroyed()) win.webContents.send("mvdg:status", { key, detail: detail || "" });
}

const REPO_ROOT = path.resolve(__dirname, "..");

// --------------------------------------------------------------- servidor
async function startServer() {
  serverPort = await sm.freePort();
  const root = sm.serverRoot(process.resourcesPath, REPO_ROOT);

  if (process.env.MVDG_SERVER_CMD) {
    const { spawn } = require("node:child_process");
    const cmd = process.env.MVDG_SERVER_CMD.replaceAll("{port}", String(serverPort));
    sendStatus("starting", cmd);
    serverProc = spawn(cmd, { shell: true, cwd: root });
  } else {
    sendStatus("searching_python");
    const bin = sm.pythonCandidates(root).find((b) => sm.pythonWorks(b, root));
    if (!bin) {
      sendStatus("no_python");
      return false;
    }
    sendStatus("starting", `${bin} · puerto ${serverPort}`);
    serverProc = sm.spawnStreamlit(bin, root, serverPort);
  }

  serverProc.on("exit", (code) => {
    if (code !== 0 && code !== null) sendStatus("server_died", `exit ${code}`);
    serverProc = null;
  });
  serverProc.stderr?.on("data", (d) => {
    const line = String(d).trim();
    if (line) sendStatus("log", line.slice(0, 300));
  });
  return true;
}

function stopServer() {
  sm.stopProcess(serverProc);
  serverProc = null;
}

// ---------------------------------------------------------------- ventana
function launcherFile() {
  const built = path.join(__dirname, "launcher", "dist", "index.html");
  if (fs.existsSync(built)) return built;
  return path.join(__dirname, "launcher", "fallback.html");
}

async function bootAndLoad() {
  const ok = await startServer();
  if (!ok) return;
  sendStatus("waiting");
  const up = await sm.waitForServer(serverPort);
  if (!up) {
    sendStatus("timeout");
    return;
  }
  sendStatus("ready");
  await win.loadURL(`http://127.0.0.1:${serverPort}/`);
}

async function createWindow() {
  win = new BrowserWindow({
    width: 1440,
    height: 900,
    show: false,
    backgroundColor: "#0e1a2b",
    title: "MV Data Governance",
    icon: process.platform === "win32"
      ? path.resolve(REPO_ROOT, "assets", "brand", "mv.ico")
      : path.resolve(REPO_ROOT, "assets", "brand", "mv_icon_256.png"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.setMenuBarVisibility(false);
  win.once("ready-to-show", () => win.show());
  await win.loadFile(launcherFile());
  await bootAndLoad();
}

ipcMain.handle("mvdg:retry", async () => {
  stopServer();
  await win.loadFile(launcherFile());
  await bootAndLoad();
  return true;
});

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (win) { if (win.isMinimized()) win.restore(); win.focus(); }
  });
  app.whenReady().then(createWindow);
}

app.on("window-all-closed", () => {
  stopServer();
  app.quit();
});
app.on("before-quit", stopServer);
