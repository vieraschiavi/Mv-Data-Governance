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

function pythonCandidates(repoRoot) {
  const names = process.platform === "win32"
    ? ["python.exe", "python3.exe", "py.exe"]
    : ["python3", "python"];
  const venvs = process.platform === "win32"
    ? [path.join(repoRoot, ".venv", "Scripts", "python.exe")]
    : [path.join(repoRoot, ".venv", "bin", "python")];
  return [...venvs.filter((p) => fs.existsSync(p)), ...names];
}

function pythonWorks(bin, cwd) {
  try {
    const r = spawnSync(bin, ["-c", "import streamlit"], { cwd, timeout: 20000 });
    return r.status === 0;
  } catch {
    return false;
  }
}

function serverRoot(resourcesPath, repoRoot) {
  const installed = resourcesPath ? path.join(resourcesPath, "server") : null;
  if (installed && fs.existsSync(path.join(installed, "app", "app.py"))) {
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
  spawnStreamlit, waitForServer, stopProcess,
};
