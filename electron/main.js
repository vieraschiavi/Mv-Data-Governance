// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · shell de escritorio (Electron).
 *
 * Qué hace: muestra el launcher (React) mientras levanta la API de gobierno
 * (FastAPI) en un puerto libre de 127.0.0.1, y cuando responde carga la
 * INTERFAZ REACT que ese mismo servidor publica en /app. Al cerrar la
 * ventana, apaga el servidor. Todo corre en la máquina del usuario: el shell
 * no hace ninguna llamada a internet (misma promesa que el resto).
 *
 * SIN STREAMLIT. Esta es la versión .exe: la interfaz es React consumiendo
 * la API REST del motor. La versión portable (.bat) sigue usando Streamlit —
 * son dos formas de ver EL MISMO motor, para clientes distintos (los que
 * pueden instalar un .exe, y los que solo pueden correr un .bat).
 *
 * La UI se carga desde http://127.0.0.1:<puerto>/app y no desde file://
 * a propósito: mismo origen que la API, así no hace falta CORS ni relajar
 * webSecurity — las dos formas habituales de que un empaquetado de
 * escritorio termine con un agujero.
 *
 * De dónde saca el servidor Python (en este orden):
 *   1. MVDG_SERVER_CMD (variable de entorno, para armados a medida)
 *   2. resources/server/ dentro de la app instalada (electron-builder)
 *      usando el Python del sistema
 *   3. la raíz del repositorio (modo desarrollo) con .venv/bin/python si
 *      existe, o python3/python del sistema
 *
 * La lógica de arranque (puerto libre, detectar Python, polling del
 * servidor) vive en lib/server-manager.js, sin depender de Electron, para
 * poder testearla con Node puro — ver lib/server-manager.test.js.
 */
const { app, BrowserWindow, ipcMain, shell } = require("electron");
const path = require("node:path");
const fs = require("node:fs");
const sm = require("./lib/server-manager");
const nav = require("./lib/navegacion");

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

  // El modo (mi equipo / VM del cliente) se resuelve ACA y se le pasa al
  // motor: es lo unico que cambia entre las dos formas de instalar, y decide
  // donde queda guardado lo que el usuario hace.
  const envModo = sm.envDelModo(process.execPath, process.resourcesPath);

  if (process.env.MVDG_SERVER_CMD) {
    const { spawn } = require("node:child_process");
    const cmd = process.env.MVDG_SERVER_CMD.replaceAll("{port}", String(serverPort));
    sendStatus("starting", cmd);
    serverProc = spawn(cmd, { shell: true, cwd: root, env: { ...process.env, ...envModo } });
  } else {
    sendStatus("searching_python");
    const bin = sm.pythonCandidates(root).find((b) => sm.pythonWorks(b, root));
    if (!bin) {
      sendStatus("no_python");
      return false;
    }
    sendStatus("starting", `${bin} · puerto ${serverPort}`);
    serverProc = sm.spawnApi(bin, root, serverPort, uiDir(), envModo);
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
/**
 * Carpeta del bundle React ya construido (ui/dist).
 *
 * En la app instalada, electron-builder deja los recursos en
 * process.resourcesPath; en desarrollo, al lado de este archivo. Se le pasa
 * EXPLICITA al servidor: la heurística relativa de bi_api encuentra la
 * carpeta en el repo pero no en el .exe instalado, y el síntoma sería un
 * 404 en /app justo después de instalar.
 */
function uiDir() {
  const candidatas = [
    path.join(__dirname, "ui", "dist"),
    process.resourcesPath ? path.join(process.resourcesPath, "ui") : null,
  ].filter(Boolean);
  return candidatas.find((c) => fs.existsSync(path.join(c, "index.html"))) || "";
}

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
  // /app = la interfaz React que sirve el propio servidor de la API.
  await win.loadURL(`http://127.0.0.1:${serverPort}/app/`);
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
  // La ventana solo puede mostrar NUESTRA interfaz. La decision de que es
  // "nuestro" vive en lib/navegacion.js para poder testearla sin Electron
  // (ver el comentario de ese archivo).
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (nav.alAbrirVentana(url) === "externo") shell.openExternal(url);
    return { action: "deny" };     // nunca una ventana de Electron
  });
  win.webContents.on("will-navigate", (ev, url) => {
    if (nav.alNavegar(url) === "bloquear") ev.preventDefault();
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
