// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Test de regresión de seguridad: ejecuta las funciones de escape REALES
 * (esc()/rvEsc()) tal como viven hoy en el HTML de producción — no una
 * reimplementación en el test — contra una batería de payloads de XSS, y
 * verifica que el resultado no puede formar HTML/atributos/eventos.
 *
 * Por qué esto y no solo un grep: un grep de "¿existe la función esc()?"
 * puede pasar aunque alguien la vacíe, la comente, o cambie su regex para
 * que deje pasar un carácter. Esto la CORRE de verdad con entradas
 * adversariales y falla si el resultado deja de ser inerte. Si mañana
 * alguien borra el escapado, o solo escapa "<" y no "&", este test lo
 * detecta — no hace falta que alguien recuerde revisarlo a mano.
 *
 * Node puro, sin dependencias (extrae la función real del archivo con un
 * escáner de llaves balanceadas, no con regex frágil, y la corre con
 * `new Function`). Mismo patrón que electron/lib/server-manager.test.js y
 * api/payments.test.js. Corré con:
 *   node landing/security.test.js
 */
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const DIR = __dirname;

/** Extrae el código fuente de `function <name>(...) {...}` contando llaves,
 * no con regex — el cuerpo real tiene objetos literales y funciones
 * anidadas, así que un regex ingenuo corta en la primera "}" que encuentra. */
function extractFunctionSource(html, name) {
  const marker = `function ${name}(`;
  const start = html.indexOf(marker);
  if (start === -1) throw new Error(`no se encontró "${marker}" en el archivo`);
  const braceOpen = html.indexOf("{", start);
  if (braceOpen === -1) throw new Error(`sin "{" tras ${marker}`);
  let depth = 0, i = braceOpen;
  for (; i < html.length; i++) {
    if (html[i] === "{") depth++;
    else if (html[i] === "}") { depth--; if (depth === 0) break; }
  }
  if (depth !== 0) throw new Error(`llaves desbalanceadas extrayendo ${name}`);
  return html.slice(start, i + 1);
}

/** Carga la función REAL desde el archivo de producción y la devuelve
 * ejecutable — con `new Function`, no con `eval` de una cadena construida a
 * mano, y el código viene siempre del propio repo (primera parte, ya
 * revisada), nunca de un payload externo. */
function loadRealFunction(relPath, name) {
  const html = fs.readFileSync(path.join(DIR, relPath), "utf8");
  const src = extractFunctionSource(html, name);
  return new Function(`${src}; return ${name};`)();
}

let checks = 0;
function check(desc, fn) {
  fn();
  checks++;
  console.log(`✓ ${desc}`);
}

// Payloads adversariales: intento de tag, intento de handler de evento sin
// tag, intento de fuga de atributo, intento de cerrar un bloque y abrir
// script nuevo, y comilla simple + doble mezcladas.
const PAYLOADS = [
  "<script>window.__xss=1</script>",
  "<img src=x onerror=window.__xss=1>",
  "\"><svg onload=window.__xss=1>",
  "'-window.__xss=1-'",
  "</div><script>window.__xss=1</script>",
  "<a href=\"javascript:window.__xss=1\">click</a>",
  "&lt;ya-escapado&gt;",             // que un valor YA escapado no se rompa doble
  "normal sin nada raro",             // caso feliz: no debe alterarse el contenido legible
];

/** Verifica que el string de salida no puede formar un tag, atributo ni
 * manejador de evento: cero '<', '>', comillas simples o dobles crudas. */
function assertInert(desc, out) {
  assert.ok(!/[<>]/.test(out), `${desc}: quedó un '<' o '>' sin escapar -> ${out}`);
  assert.ok(!/["']/.test(out), `${desc}: quedó una comilla sin escapar -> ${out}`);
}

function main() {
  // ------------------------------------------------- landing/index.html
  const rvEsc = loadRealFunction("index.html", "rvEsc");
  for (const payload of PAYLOADS) {
    check(`index.html rvEsc(): inerte contra ${JSON.stringify(payload).slice(0, 40)}`, () => {
      assertInert("rvEsc", rvEsc(payload));
    });
  }
  check("index.html rvEsc(): el texto normal se conserva legible", () => {
    assert.strictEqual(rvEsc("Excelente producto, 5 estrellas"), "Excelente producto, 5 estrellas");
  });
  check("index.html rvEsc(): null/undefined no revientan, dan string vacío", () => {
    assert.strictEqual(rvEsc(null), "");
    assert.strictEqual(rvEsc(undefined), "");
  });

  // ----------------------------------------------- landing/reviews.html
  const esc1 = loadRealFunction("reviews.html", "esc");
  for (const payload of PAYLOADS) {
    check(`reviews.html esc(): inerte contra ${JSON.stringify(payload).slice(0, 40)}`, () => {
      assertInert("esc", esc1(payload));
    });
  }

  // --------------------------------------------------- landing/pago.html
  const esc2 = loadRealFunction("pago.html", "esc");
  for (const payload of PAYLOADS) {
    check(`pago.html esc(): inerte contra ${JSON.stringify(payload).slice(0, 40)}`, () => {
      assertInert("esc", esc2(payload));
    });
  }

  // ---------------------------------------- las 3 funciones dan el MISMO
  // criterio (regresión: que no se desalineen entre sí con el tiempo)
  check("las 3 funciones de escape coinciden en su criterio", () => {
    for (const payload of PAYLOADS) {
      const a = rvEsc(payload), b = esc1(payload), c = esc2(payload);
      assert.strictEqual(a, b, `rvEsc vs reviews.esc difieren en ${JSON.stringify(payload)}`);
      assert.strictEqual(a, c, `rvEsc vs pago.esc difieren en ${JSON.stringify(payload)}`);
    }
  });

  // ---------------------------------------------------- sitios de uso real
  // Confirma que TODO campo externo (reseñas, respuesta de la API de pago)
  // sigue pasando por una de estas funciones antes de insertarse. Si alguien
  // agrega un campo nuevo sin escaparlo, esto rompe.
  check("index.html: cada campo de reseña pasa por rvEsc() antes de insertarse", () => {
    const html = fs.readFileSync(path.join(DIR, "index.html"), "utf8");
    for (const campo of ["comment", "name", "role"]) {
      assert.ok(new RegExp(`rvEsc\\(r\\.${campo}\\)`).test(html), `r.${campo} sin rvEsc()`);
    }
  });
  check("reviews.html: cada campo de reseña pasa por esc() antes de insertarse", () => {
    const html = fs.readFileSync(path.join(DIR, "reviews.html"), "utf8");
    for (const campo of ["comment", "name", "role", "date"]) {
      assert.ok(new RegExp(`esc\\(r\\.${campo}\\)`).test(html), `r.${campo} sin esc()`);
    }
  });
  check("pago.html: los campos que vienen de la API de pago pasan por esc()", () => {
    const html = fs.readFileSync(path.join(DIR, "pago.html"), "utf8");
    for (const campo of ["planName", "STATE.license"]) {
      assert.ok(new RegExp(`esc\\(${campo.replace(".", "\\.")}\\)`).test(html), `${campo} sin esc()`);
    }
  });
  // El trial autoservicio (/api/trial) se elimino: emitia una licencia a
  // cualquiera que dejara un email, y con esa licencia se bajaba el programa.
  // Su chequeo de XSS se reemplaza por el del formulario que lo sustituye.
  check("index.html: ya no queda ningun uso de /api/trial", () => {
    const html = fs.readFileSync(path.join(DIR, "index.html"), "utf8");
    const sinComentarios = html.replace(/\/\*[\s\S]*?\*\/|<!--[\s\S]*?-->/g, "");
    assert.ok(!/fetch\(['"]\/api\/trial/.test(sinComentarios),
              "index.html sigue llamando a /api/trial, que ya no existe");
  });
  check("descargas.html: la respuesta del pedido de acceso NO va por innerHTML", () => {
    // Este formulario muestra mensajes de estado, no datos de nadie — pero la
    // regla de la casa es que nada que venga de una respuesta se inserte como
    // marcado. Con textContent no hay nada que escapar ni que se pueda olvidar.
    const html = fs.readFileSync(path.join(DIR, "descargas.html"), "utf8");
    assert.ok(/msg\.textContent\s*=/.test(html),
              "el mensaje del formulario no usa textContent");
    const js = html.slice(html.indexOf("accesoForm"));
    assert.ok(!/msg\.innerHTML/.test(js),
              "el formulario de acceso escribe innerHTML: usa textContent");
  });
  check("descargas.html: la pagina ya no ofrece ninguna descarga directa", () => {
    // El punto del cambio: la demo se pide, no se baja. Un <a> al .zip o al
    // endpoint de descarga en esta pagina anula todo lo demas.
    const html = fs.readFileSync(path.join(DIR, "descargas.html"), "utf8");
    assert.ok(!/href=["'][^"']*\.zip/.test(html), "sigue habiendo un link a un .zip");
    assert.ok(!/href=["'][^"']*\/api\/descargar/.test(html),
              "sigue habiendo un link directo al endpoint de descarga");
  });

  console.log(`\nTodos los checks de seguridad (XSS) pasaron (${checks}).`);
}

main();
