// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Invariantes de la navegación de la interfaz de escritorio (React).
 *     node ui/vistas.test.js
 *
 * Por qué existe
 * --------------
 * Agregar una vista son TRES lugares: la lista `VISTAS` (el botón), el mapa
 * `RENDER` (el componente) y la clave de i18n (el texto del botón). Olvidarse
 * de cualquiera de los tres no rompe el build ni tira un error:
 *
 *   · sin entrada en RENDER  -> se aprieta el botón y la pantalla queda en
 *     blanco, porque `RENDER[vista]` es undefined y React no renderiza nada;
 *   · sin clave de i18n      -> el botón muestra el identificador interno
 *     ("relevamiento") en vez del nombre, en los tres idiomas.
 *
 * Los dos síntomas se ven recién abriendo el .exe, que es el ciclo más lento
 * que tiene este proyecto. Acá se ven en un segundo, con Node puro.
 */
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

let checks = 0;
function check(desc, fn) { fn(); checks++; console.log("✓ " + desc); }

const src = (nombre) =>
  fs.readFileSync(path.join(__dirname, "src", nombre), "utf8");

const app = src("App.jsx");
const i18n = src("i18n.js");

// VISTAS = ["panorama", "catalogo", ...]
const bloqueVistas = app.match(/const VISTAS = \[([\s\S]*?)\];/);
assert.ok(bloqueVistas, "no se encontró la lista VISTAS en App.jsx");
const vistas = [...bloqueVistas[1].matchAll(/"([^"]+)"/g)].map((m) => m[1]);

// RENDER = { panorama: Panorama, ... }
const bloqueRender = app.match(/const RENDER = \{([\s\S]*?)\};/);
assert.ok(bloqueRender, "no se encontró el mapa RENDER en App.jsx");
const render = [...bloqueRender[1].matchAll(/(\w+)\s*:/g)].map((m) => m[1]);

check("hay vistas declaradas", () => {
  assert.ok(vistas.length >= 10, `solo ${vistas.length} vistas`);
});

check("cada vista tiene su componente en RENDER", () => {
  const faltan = vistas.filter((v) => !render.includes(v));
  assert.deepStrictEqual(faltan, [],
    `estas vistas tienen boton y no tienen componente: ${faltan.join(", ")}. ` +
    `El sintoma es una pantalla en blanco al apretar el boton, sin ningun error.`);
});

check("no hay componentes en RENDER sin su boton", () => {
  const sobran = render.filter((r) => !vistas.includes(r));
  assert.deepStrictEqual(sobran, [],
    `estos componentes no se pueden alcanzar: ${sobran.join(", ")}`);
});

check("cada vista tiene su nombre en los TRES idiomas", () => {
  const sinClave = [];
  const sinIdioma = [];
  for (const v of vistas) {
    // La clave del boton es el nombre de la vista: t(v, lang).
    const entrada = i18n.match(
      new RegExp(`\\b${v}:\\s*\\{([^}]*)\\}`));
    if (!entrada) { sinClave.push(v); continue; }
    for (const lg of ["es", "en", "pt"]) {
      if (!new RegExp(`\\b${lg}:`).test(entrada[1])) sinIdioma.push(`${v}.${lg}`);
    }
  }
  assert.deepStrictEqual(sinClave, [],
    `estas vistas no tienen texto en i18n.js y el boton muestra el ` +
    `identificador interno: ${sinClave.join(", ")}`);
  assert.deepStrictEqual(sinIdioma, [],
    `faltan idiomas: ${sinIdioma.join(", ")}`);
});

// --------------------------------------------------- las dos vistas nuevas
//
// El motor del relevamiento y el de las reuniones viven en Python. Si alguien
// los reimplementa en JavaScript "para que ande sin el servidor", quedan dos
// motores: el banco de preguntas del .exe y el del panel se separan en el
// primer cambio, y el que corre en la maquina del cliente es el que menos se
// prueba. Esto lo fija.
check("las vistas de consultoria NO traen logica propia", () => {
  const vista = src("consultoria.jsx");
  const sospechas = [
    [/\bconst\s+PREGUNTAS\b/, "un banco de preguntas propio"],
    [/WEBVTT|-->\s*\$\{|\bparseTranscript\b/, "un parser de transcripciones propio"],
    [/\bdecision|compromiso\b.*=\s*\[/, "una lista de marcadores propia"],
  ];
  const halladas = sospechas.filter(([re]) => re.test(vista)).map(([, q]) => q);
  assert.deepStrictEqual(halladas, [],
    `la vista tiene ${halladas.join(" y ")}: eso ya lo hace el motor en ` +
    `Python y duplicarlo da dos versiones que se separan`);
});

check("las dos vistas nuevas estan enchufadas", () => {
  for (const v of ["relevamiento", "reuniones"]) {
    assert.ok(vistas.includes(v), `falta la vista ${v}`);
  }
  assert.match(app, /from "\.\/consultoria"/,
    "App.jsx no importa las vistas de consultoria");
});

console.log(`\nTodos los checks de las vistas pasaron (${checks}).`);
