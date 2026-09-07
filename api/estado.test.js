// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
//
// Tests del diagnóstico de configuración (api/estado.js).
//
// Lo que se cuida acá, en orden de importancia:
//   1. Que NUNCA devuelva el valor de una variable. Un endpoint de
//      diagnóstico que filtra el Access Token o la clave que firma las
//      licencias es peor que no tenerlo.
//   2. Que "listo_para_vender" signifique de verdad que se puede cobrar,
//      emitir la licencia y descargar — no que el sitio cargue.
//   3. Que el candado opcional (MVDG_ESTADO_TOKEN) cierre cuando está puesto.
//
// Sin dependencias: solo módulos nativos de Node, igual que el resto.
const assert = require("assert");

const RUTA = require.resolve("./estado.js");

// Reset del módulo entre casos: `estado.js` lee process.env en cada request,
// pero el limitador de tasa guarda estado en memoria y contaría los hits de
// un caso en el siguiente.
function cargarLimpio() {
  delete require.cache[RUTA];
  delete require.cache[require.resolve("./_rate_limit.js")];
  return require(RUTA);
}

function llamar(env, query = {}, method = "GET") {
  const previo = {};
  // Se aísla el entorno: se guarda lo que había, se pone lo del caso, y se
  // restaura al final. Si no, un caso deja variables puestas para el próximo.
  const claves = new Set([
    ...Object.keys(env),
    "MP_ACCESS_TOKEN", "LICENSE_PRIVATE_KEY", "MVDG_INSTALLER_URL",
    "RESEND_API_KEY", "MVDG_ESTADO_TOKEN", "LICENSE_SECRET",
    "KV_REST_API_URL", "KV_REST_API_TOKEN", "MP_CURRENCY",
    "LICENSE_PUBLIC_KEY", "MVDG_INSTALLER_URL_OWNER", "MVDG_SITE_HOST",
    "MVDG_MAIL_TO", "MVDG_MAIL_FROM",
  ]);
  for (const k of claves) { previo[k] = process.env[k]; delete process.env[k]; }
  for (const [k, v] of Object.entries(env)) process.env[k] = v;

  const estado = cargarLimpio();
  let status = null, body = null;
  const res = {
    status(c) { status = c; return this; },
    json(b) { body = b; return this; },
  };
  estado({ method, query, headers: {}, socket: {} }, res);

  for (const k of claves) {
    if (previo[k] === undefined) delete process.env[k];
    else process.env[k] = previo[k];
  }
  return { status, body };
}

// Todo lo imprescindible puesto.
const COMPLETO = {
  MP_ACCESS_TOKEN: "APP_USR-token-de-prueba",
  LICENSE_PRIVATE_KEY: "clave-privada-de-prueba",
  MVDG_INSTALLER_URL: "https://ejemplo.invalid/MVDataGovernance_Setup.exe",
  RESEND_API_KEY: "re_clave_de_prueba",
};

let n = 0;
function ok(msg) { n++; console.log("✓ " + msg); }

// ───────────────────────────────────────────────────────── 1. no filtra nada
{
  const { body } = llamar(COMPLETO);
  const texto = JSON.stringify(body);
  for (const valor of Object.values(COMPLETO)) {
    assert.ok(!texto.includes(valor),
      `el diagnóstico devolvió el VALOR de una variable: ${valor}`);
  }
  // Ni siquiera un prefijo: 6 caracteres del Access Token ya reducen el
  // espacio de búsqueda de quien quiera adivinarlo.
  for (const valor of Object.values(COMPLETO)) {
    assert.ok(!texto.includes(valor.slice(0, 6)),
      `el diagnóstico filtró un prefijo del valor: ${valor.slice(0, 6)}`);
  }
  ok("nunca devuelve el valor de una variable, ni un prefijo");
}

// ────────────────────────────────────────── 2. listo_para_vender es honesto
{
  const { status, body } = llamar(COMPLETO);
  assert.strictEqual(status, 200);
  assert.strictEqual(body.listo_para_vender, true);
  assert.deepStrictEqual(body.faltan_criticas, []);
  ok("con todo lo imprescindible puesto: listo_para_vender = true");
}

// Cada variable crítica, sacada de a una, tiene que tumbar el veredicto.
for (const critica of ["MP_ACCESS_TOKEN", "LICENSE_PRIVATE_KEY",
                       "MVDG_INSTALLER_URL", "RESEND_API_KEY"]) {
  const env = { ...COMPLETO };
  delete env[critica];
  const { body } = llamar(env);
  assert.strictEqual(body.listo_para_vender, false,
    `sin ${critica} el endpoint igual dijo que estaba listo para vender`);
  assert.ok(body.faltan_criticas.includes(critica),
    `sin ${critica} no apareció en faltan_criticas`);
  // Y tiene que decir QUÉ se rompe, no solo que falta.
  const fila = body.detalle.find((f) => f.variable === critica);
  assert.ok(fila && typeof fila.rompe === "string" && fila.rompe.length > 20,
    `${critica} no explica qué se rompe cuando falta`);
  ok(`sin ${critica}: no está listo para vender, y dice por qué`);
}

// Una opcional que falta NO puede bloquear la venta.
{
  const { body } = llamar({ ...COMPLETO });   // KV y LICENSE_SECRET ausentes
  assert.strictEqual(body.listo_para_vender, true);
  assert.ok(body.faltan_opcionales.includes("KV_REST_API_URL"));
  assert.ok(body.faltan_opcionales.includes("LICENSE_SECRET"));
  ok("las variables opcionales que faltan no bloquean la venta");
}

// ──────────────────────────────────────────────────── 3. candado opcional
{
  const { status, body } = llamar({ ...COMPLETO, MVDG_ESTADO_TOKEN: "s3cr3to" });
  assert.strictEqual(status, 401, "con MVDG_ESTADO_TOKEN puesto, no exigió token");
  assert.strictEqual(body.error, "no_autorizado");
  ok("con MVDG_ESTADO_TOKEN definido, sin ?t= responde 401");
}
{
  const { status, body } = llamar(
    { ...COMPLETO, MVDG_ESTADO_TOKEN: "s3cr3to" }, { t: "s3cr3to" });
  assert.strictEqual(status, 200);
  assert.strictEqual(body.protegido, true);
  ok("con el token correcto responde 200 y se declara protegido");
}
{
  const { status } = llamar(
    { ...COMPLETO, MVDG_ESTADO_TOKEN: "s3cr3to" }, { t: "otro-token" });
  assert.strictEqual(status, 401, "aceptó un token equivocado");
  ok("un token equivocado no entra");
}
{
  // Sin candado configurado contesta igual — es cuando más se necesita —,
  // pero tiene que DECIR que está abierto en vez de fingir que está cerrado.
  const { status, body } = llamar(COMPLETO);
  assert.strictEqual(status, 200);
  assert.strictEqual(body.protegido, false);
  assert.ok(/MVDG_ESTADO_TOKEN/.test(body.aviso_proteccion || ""),
    "no avisa que el diagnóstico está abierto");
  ok("sin candado: contesta, pero avisa que está abierto");
}

// ─────────────────────────────────────────────────────────── 4. método
{
  const { status } = llamar(COMPLETO, {}, "POST");
  assert.strictEqual(status, 405);
  ok("solo GET");
}

// ──────────────────────────── 5. la tabla cubre lo que el código realmente lee
{
  const fs = require("fs");
  const path = require("path");
  const estado = cargarLimpio();
  const declaradas = new Set(estado.VARIABLES.map((v) => v.env));

  // Variables que las funciones serverless leen de verdad. Si alguien agrega
  // una nueva y no la declara acá, este diagnóstico mentiría por omisión:
  // diría "listo para vender" sin haber mirado algo que sí hace falta.
  const dir = path.join(__dirname);
  const leidas = new Set();
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith(".js") || f.endsWith(".test.js")) continue;
    const src = fs.readFileSync(path.join(dir, f), "utf8");
    for (const m of src.matchAll(/process\.env\.([A-Z][A-Z0-9_]*)/g)) {
      leidas.add(m[1]);
    }
  }
  // Estas se leen pero no son configuración del circuito comercial.
  const exentas = new Set([
    "MVDG_ESTADO_TOKEN",   // es el candado de este mismo endpoint
    "MP_LINK_LICENCIA",    // respaldo, se arma dinámicamente MP_LINK_<PLAN>
  ]);
  const sinDeclarar = [...leidas].filter(
    (v) => !declaradas.has(v) && !exentas.has(v));
  assert.deepStrictEqual(sinDeclarar, [],
    "api/*.js lee variables que el diagnóstico no mira: " + sinDeclarar.join(", "));
  ok("el diagnóstico cubre todas las variables que api/*.js lee de verdad");
}

console.log(`\nTodos los checks del diagnóstico de configuración pasaron (${n}).`);
