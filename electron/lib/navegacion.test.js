// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Test de la política de navegación de la ventana de escritorio, con Node
 * puro (sin Electron, sin pantalla). Corré con:
 *     node lib/navegacion.test.js
 *
 * Por qué importa que este test exista: main.js no se puede ejecutar en CI
 * (Electron necesita display), así que sin esto la regla de seguridad se
 * escribía una vez y nadie la volvía a verificar nunca.
 */
const assert = require("node:assert");
const nav = require("./navegacion");

let checks = 0;
function check(desc, fn) {
  fn();
  checks++;
  console.log("✓ " + desc);
}

// --------------------------------------------------------------- navegar
check("navegar: la interfaz propia (API local) se permite", () => {
  assert.strictEqual(nav.alNavegar("http://127.0.0.1:8600/app/"), "permitir");
  assert.strictEqual(nav.alNavegar("http://localhost:51234/app/index.html"), "permitir");
  assert.strictEqual(nav.alNavegar("http://127.0.0.1:8600/api/glosario"), "permitir");
});

check("navegar: el launcher empaquetado (file://) se permite", () => {
  assert.strictEqual(nav.alNavegar("file:///C:/Program%20Files/MV/launcher.html"),
                     "permitir");
});

check("navegar: un sitio externo se BLOQUEA", () => {
  for (const u of ["https://evil.com/phishing",
                   "http://evil.com",
                   "https://mv-data-governance.vercel.app"]) {
    assert.strictEqual(nav.alNavegar(u), "bloquear", u);
  }
});

check("navegar: un host que solo CONTIENE localhost no alcanza", () => {
  // el clasico: localhost.evil.com resuelve a lo que quiera el atacante
  assert.strictEqual(nav.alNavegar("http://localhost.evil.com/x"), "bloquear");
  assert.strictEqual(nav.alNavegar("http://127.0.0.1.evil.com/x"), "bloquear");
  // y el usuario:contrasena@ que hace que la URL PAREZCA local
  assert.strictEqual(nav.alNavegar("http://127.0.0.1@evil.com/x"), "bloquear");
});

check("navegar: un esquema peligroso se bloquea", () => {
  for (const u of ["javascript:alert(1)", "data:text/html,<script>x</script>",
                   "vbscript:x", "no-es-una-url"]) {
    assert.strictEqual(nav.alNavegar(u), "bloquear", u);
  }
});

// ---------------------------------------------------------- abrir ventana
check("ventana: nunca se abre una ventana de Electron", () => {
  // el handler siempre devuelve deny en main.js; aca se verifica la decision
  // de QUE hacer con la URL, que es la parte con logica
  assert.strictEqual(nav.alAbrirVentana("https://learn.microsoft.com/power-bi"),
                     "externo");
  assert.strictEqual(nav.alAbrirVentana("http://127.0.0.1:8600/app/"), "externo");
});

check("ventana: un esquema que no es http/https no abre nada", () => {
  for (const u of ["file:///etc/passwd", "javascript:alert(1)",
                   "ms-msdt:/id", "", null, undefined]) {
    assert.strictEqual(nav.alAbrirVentana(u), "descartar", String(u));
  }
});

console.log(`\nTodos los checks de navegacion pasaron (${checks}).`);
