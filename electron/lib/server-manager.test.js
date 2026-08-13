// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Test end-to-end de server-manager.js con Node puro (sin Electron): arranca
 * un Streamlit REAL contra app/app.py de este repo y confirma que
 * waitForServer() lo detecta arriba. Corré con: node lib/server-manager.test.js
 */
const assert = require("node:assert");
const http = require("node:http");
const path = require("node:path");
const sm = require("./server-manager");

const REPO_ROOT = path.resolve(__dirname, "..", "..");

async function main() {
  // 1. freePort() da un puerto usable
  const port = await sm.freePort();
  assert.ok(port > 0 && port < 65536, "freePort debe devolver un puerto válido");
  console.log(`✓ freePort() -> ${port}`);

  // 2. serverRoot() cae al repo cuando no hay resourcesPath (modo dev)
  const root = sm.serverRoot(undefined, REPO_ROOT);
  assert.strictEqual(root, REPO_ROOT);
  console.log("✓ serverRoot() en modo desarrollo -> raíz del repo");

  // 3. pythonCandidates() encuentra un intérprete que puede importar streamlit
  const candidates = sm.pythonCandidates(root);
  const bin = candidates.find((b) => sm.pythonWorks(b, root));
  assert.ok(bin, `ninguno de los candidatos [${candidates}] tiene fastapi+uvicorn`);
  console.log(`✓ pythonWorks() encontró un intérprete real: ${bin}`);

  // 4. EL CAMINO DE LA VERSION .EXE: spawnApi levanta la API real y esa
  //    misma API sirve la interfaz React en /app. Es el recorrido completo
  //    del programa de escritorio, sin Streamlit por ningún lado.
  const uiDir = path.join(__dirname, "..", "ui", "dist");
  const proc = sm.spawnApi(bin, root, port, uiDir);
  try {
    const up = await sm.waitForServer(port, 60000, 500);
    assert.strictEqual(up, true, "waitForServer no detectó la API real a tiempo");
    console.log(`✓ spawnApi() levantó la API real en :${port}`);

    const traer = (ruta) => new Promise((resolve) => {
      http.get(`http://127.0.0.1:${port}${ruta}`, (res) => {
        let cuerpo = "";
        res.on("data", (d) => { cuerpo += d; });
        res.on("end", () => resolve({ status: res.statusCode, cuerpo }));
      }).on("error", () => resolve({ status: 0, cuerpo: "" }));
    });

    const app = await traer("/app/");
    assert.strictEqual(app.status, 200, "la interfaz React no se sirve en /app");
    assert.ok(app.cuerpo.includes('id="root"'), "/app no devolvió la app React");
    assert.ok(!/streamlit/i.test(app.cuerpo), "la interfaz menciona Streamlit");
    console.log("✓ /app sirve la interfaz React (y no contiene Streamlit)");

    const js = await traer("/app/ui.js");
    assert.strictEqual(js.status, 200, "el bundle React no se sirve");
    console.log("✓ /app/ui.js se sirve desde el mismo origen (sin CORS)");

    const kpis = await traer("/api/kpis?lang=es");
    assert.strictEqual(kpis.status, 200, "la API de gobierno no responde");
    assert.ok(JSON.parse(kpis.cuerpo).data.length > 0, "la API devolvió 0 KPIs");
    console.log("✓ la misma API sirve los datos de gobierno");
  } finally {
    sm.stopProcess(proc);
  }

  // 5. tras matar el proceso, un puerto que nunca se levanta hace timeout rápido
  const deadPort = await sm.freePort();
  const upDead = await sm.waitForServer(deadPort, 2000, 300);
  assert.strictEqual(upDead, false, "waitForServer debería dar timeout en un puerto muerto");
  console.log("✓ waitForServer() da timeout correctamente si nadie escucha");

  console.log("\nTodos los checks de server-manager.js pasaron.");
}

main().catch((err) => {
  console.error("✗ FALLÓ:", err);
  process.exit(1);
});
