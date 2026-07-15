/*
 * Test end-to-end de server-manager.js con Node puro (sin Electron): arranca
 * un Streamlit REAL contra app/app.py de este repo y confirma que
 * waitForServer() lo detecta arriba. Corré con: node lib/server-manager.test.js
 */
const assert = require("node:assert");
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
  assert.ok(bin, `ninguno de los candidatos [${candidates}] tiene streamlit`);
  console.log(`✓ pythonWorks() encontró un intérprete real: ${bin}`);

  // 4. levantamos un Streamlit REAL y confirmamos que waitForServer() lo detecta
  const proc = sm.spawnStreamlit(bin, root, port);
  try {
    const up = await sm.waitForServer(port, 60000, 500);
    assert.strictEqual(up, true, "waitForServer no detectó el servidor real a tiempo");
    console.log(`✓ waitForServer() detectó Streamlit real en :${port}`);
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
