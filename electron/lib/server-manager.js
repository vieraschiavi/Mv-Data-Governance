// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · lógica de arranque del servidor local — separada de
 * main.js a propósito para poder testearla con Node puro (sin el runtime de
 * Electron, que no siempre está disponible para bajar en todos los
 * entornos). main.js importa estas mismas funciones.
 */
const { spawn, spawnSync } = require("node:child_process");
const http = require("node:http");
const net = require("node:net");
const path = require("node:path");
const fs = require("node:fs");

function freePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.listen(0, "127.0.0.1", () => {
      const port = srv.address().port;
      srv.close(() => resolve(port));
    });
    srv.on("error", reject);
  });
}

/**
 * Interpretes a probar, EN ORDEN de preferencia:
 *   1. el Python EMBEBIDO que viaja dentro del instalador (server/python).
 *      Es el que hace que el .exe ande en una PC recien formateada, sin
 *      pedirle a nadie que instale Python.
 *   2. el .venv del repo (modo desarrollo).
 *   3. el Python del sistema, como ultimo recurso.
 *
 * El embebido va primero a proposito: si el cliente TIENE Python instalado
 * pero sin fastapi, elegir el suyo haria fallar el arranque teniendo al
 * lado uno que funciona.
 */
function pythonCandidates(repoRoot) {
  const win = process.platform === "win32";
  const names = win ? ["python.exe", "python3.exe", "py.exe"] : ["python3", "python"];
  const propios = win
    ? [path.join(repoRoot, "python", "python.exe"),
       path.join(repoRoot, ".venv", "Scripts", "python.exe")]
    : [path.join(repoRoot, "python", "bin", "python3"),
       path.join(repoRoot, ".venv", "bin", "python")];
  return [...propios.filter((p) => fs.existsSync(p)), ...names];
}

// Que importe fastapi + uvicorn y NO streamlit: la version de escritorio
// sirve la UI React desde bi_api. Pedir streamlit acá haría fallar el
// arranque en un empaquetado que, correctamente, no lo incluye.
function pythonWorks(bin, cwd) {
  try {
    const r = spawnSync(bin, ["-c", "import fastapi, uvicorn"], { cwd, timeout: 20000 });
    return r.status === 0;
  } catch {
    return false;
  }
}

function serverRoot(resourcesPath, repoRoot) {
  const installed = resourcesPath ? path.join(resourcesPath, "server") : null;
  if (installed && fs.existsSync(path.join(installed, "bi_api", "main.py"))) {
    return installed;
  }
  return repoRoot;
}

function spawnStreamlit(bin, root, port, extraEnv) {
  const appPy = path.join(root, "app", "app.py");
  const args = ["-m", "streamlit", "run", appPy,
    "--server.headless", "true",
    "--server.address", "127.0.0.1",
    "--server.port", String(port),
    "--browser.gatherUsageStats", "false"];
  return spawn(bin, args, {
    cwd: root,
    env: { ...process.env, PYTHONUNBUFFERED: "1", ...extraEnv },
  });
}

/**
 * Levanta la API de gobierno (FastAPI), que ademas sirve la UI React en
 * /app. Reemplaza a spawnStreamlit en la version de escritorio.
 *
 * MVDG_UI_DIR se pasa explicito porque en el empaquetado de
 * electron-builder la carpeta del bundle NO queda al lado de bi_api/ — la
 * heuristica relativa de bi_api serviria para el repo pero no para el .exe
 * instalado, y el sintoma seria un 404 en /app despues de instalar.
 */
function spawnApi(bin, root, port, uiDir, extraEnv) {
  return spawn(bin, ["-m", "bi_api.main"], {
    cwd: root,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: "1",
      MVDG_API_HOST: "127.0.0.1",
      MVDG_API_PORT: String(port),
      ...(uiDir ? { MVDG_UI_DIR: uiDir } : {}),
      ...extraEnv,
    },
  });
}

function waitForServer(port, timeoutMs = 180000, pollMs = 700) {
  const url = `http://127.0.0.1:${port}/`;
  const started = Date.now();
  return new Promise((resolve) => {
    const tick = () => {
      if (Date.now() - started > timeoutMs) return resolve(false);
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode < 500) return resolve(true);
        setTimeout(tick, pollMs);
      });
      req.on("error", () => setTimeout(tick, pollMs));
      req.setTimeout(3000, () => { req.destroy(); setTimeout(tick, pollMs); });
    };
    tick();
  });
}

function stopProcess(proc) {
  if (!proc) return;
  try {
    if (process.platform === "win32") {
      spawnSync("taskkill", ["/pid", String(proc.pid), "/T", "/F"]);
    } else {
      proc.kill("SIGTERM");
    }
  } catch { /* ya muerto */ }
}

module.exports = {
  freePort, pythonCandidates, pythonWorks, serverRoot,
  spawnStreamlit, spawnApi, waitForServer, stopProcess,
};
