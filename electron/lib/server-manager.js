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

// Nombre del archivo que marca un paquete como "para la VM del cliente".
// Tiene que decir EXACTAMENTE lo mismo que mvdg/install_mode.py:MARCADOR;
// hay un test que compara los dos valores, porque si se separan el shell y
// el motor quedan en modos distintos y nadie lo nota hasta la VM del cliente.
const MARCADOR_VM = "MODO_VM_CLIENTE.txt";

/**
 * En que modo esta instalado esto: "normal" o "vm_cliente".
 *
 * El ZIP portable trae el marcador en la raiz de la carpeta; el instalador
 * NSIS no. Asi el paquete que se bajo ES el modo, sin que nadie tenga que
 * configurar nada — que es justo lo que no se puede pedir en la VM de un
 * cliente, donde el consultor entra con lo puesto.
 *
 * Se busca al lado del .exe de la ventana (execPath) y arriba de resources/,
 * porque electron-builder deja el ejecutable en la raiz de la carpeta y los
 * recursos un nivel adentro.
 */
function modoInstalacion(execPath, resourcesPath) {
  const carpetas = [
    execPath ? path.dirname(execPath) : null,
    resourcesPath ? path.dirname(resourcesPath) : null,
    resourcesPath || null,
  ].filter(Boolean);
  for (const c of carpetas) {
    try {
      if (fs.existsSync(path.join(c, MARCADOR_VM))) return { modo: "vm_cliente", raiz: c };
    } catch { /* carpeta ilegible: se prueba la siguiente */ }
  }
  return { modo: "normal", raiz: null };
}

/**
 * Variables que hacen que el motor Python vea el MISMO modo que el shell.
 *
 * Se pasan explicitas en vez de dejar que install_mode.py vuelva a sondear
 * el disco: en el empaquetado el motor vive en resources/server/mvdg, o sea
 * tres niveles por debajo del marcador, y depender de que la busqueda hacia
 * arriba acierte en cada layout futuro es fragil. El shell ya sabe la
 * respuesta; se la dice.
 */
function envDelModo(execPath, resourcesPath) {
  const { modo, raiz } = modoInstalacion(execPath, resourcesPath);
  if (modo !== "vm_cliente") return {};
  return {
    MVDG_MODO_INSTALACION: "vm_cliente",
    MVDG_DATA_DIR: path.join(raiz, "Datos"),
  };
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
  modoInstalacion, envDelModo, MARCADOR_VM,
};
