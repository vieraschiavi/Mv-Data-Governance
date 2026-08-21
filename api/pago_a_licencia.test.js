// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
//
// El circuito de un cliente que PAGA, de punta a punta.
//
// Simula lo unico que no se puede tener aca: la respuesta de MercadoPago. Todo
// lo demas es el codigo de produccion — verify-payment.js firmando con la
// LICENSE_PRIVATE_KEY de verdad, y despues Python verificando ese token con la
// PUBLIC_KEY_B64 que lleva embebida el programa del cliente.
//
// Si este archivo pasa, un pago aprobado termina en un programa desbloqueado.
const assert = require("node:assert");
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const crypto = require("node:crypto");

const RAIZ = path.resolve(__dirname, "..");

// Par de claves EFIMERO, generado en cada corrida. Asi este test no necesita
// ningun secreto y puede correr en CI — y de paso no queda atado a la clave
// de produccion, que puede rotarse sin romperlo.
const { privateKey, publicKey } = crypto.generateKeyPairSync("ed25519");
const b64u = (b) => Buffer.from(b).toString("base64")
  .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
// Los 32 bytes crudos: el DER de una publica Ed25519 son 12 de cabecera + 32.
const PUBLICA = b64u(publicKey.export({ type: "spki", format: "der" }).subarray(12));
// Y de la privada, los ultimos 32 del PKCS#8.
const PRIVADA = b64u(privateKey.export({ type: "pkcs8", format: "der" }).subarray(16));

function mockRes() {
  return {
    _status: null, _body: null,
    status(c) { this._status = c; return this; },
    json(o) { this._body = o; return this; },
    setHeader() { return this; }, end() { return this; },
  };
}

// Lo que devolveria la API de MercadoPago para un pago recien aprobado.
function pagoMP(sku, { estado = "approved", hace_min = 1 } = {}) {
  const fecha = new Date(Date.now() - hace_min * 60_000).toISOString();
  return {
    ok: true,
    json: async () => ({
      status: estado, date_approved: fecha, date_created: fecha,
      metadata: { plan: sku },
      payer: { email: "comprador@empresa.com" },
    }),
  };
}

// Verifica el token con el MOTOR PYTHON, que es lo que corre en la PC del
// cliente. Cruzar de Node a Python es el punto: que las dos mitades del
// sistema coincidan de verdad, no que cada una se apruebe a si misma.
function verificarEnElPrograma(token) {
  const codigo = `
import json, sys
sys.path.insert(0, ${JSON.stringify(RAIZ)})
from mvdg import licensing
licensing.PUBLIC_KEY_B64 = sys.argv[2]
p = licensing.verify(sys.argv[1], check_machine=False)
if p is None:
    print(json.dumps({"valida": False})); raise SystemExit(0)
# .Que habilita ese plan? Se pregunta al motor, no se asume.
funcs = {}
_plan_real = licensing.plan
licensing.plan = lambda: p["plan"]
try:
    for f in sorted(licensing.FUNCIONES_PAGAS):
        funcs[f] = licensing.has_feature(f)
finally:
    licensing.plan = _plan_real
print(json.dumps({"valida": True, "plan": p["plan"],
                  "email": p.get("email"), "exp": p.get("exp"),
                  "funciones": funcs}))
`;
  const salida = execFileSync("python3", ["-c", codigo, token, PUBLICA],
                              { encoding: "utf8", cwd: RAIZ });
  return JSON.parse(salida.trim());
}

let ok = 0;
const fallos = [];
function check(desc, fn) {
  try { fn(); ok++; console.log(`  [OK ] ${desc}`); }
  catch (e) { fallos.push(desc); console.log(`  [FALLA] ${desc}\n         ${e.message}`); }
}

async function main() {
  delete require.cache[require.resolve(path.join(RAIZ, "api/verify-payment.js"))];
  delete require.cache[require.resolve(path.join(RAIZ, "api/_rate_limit.js"))];
  const verify = require(path.join(RAIZ, "api/verify-payment.js"));
  const rl = require(path.join(RAIZ, "api/_rate_limit.js"));

  process.env.MP_ACCESS_TOKEN = "APP_USR-de-prueba";
  process.env.LICENSE_PRIVATE_KEY = PRIVADA;

  const real = global.fetch;
  let pid = 1000;

  async function comprar(sku, opciones) {
    rl.resetForTests();
    global.fetch = async () => pagoMP(sku, opciones);
    const res = mockRes();
    await verify({ query: { payment_id: String(++pid) }, headers: {} }, res);
    global.fetch = real;
    return res._body;
  }

  console.log("\n== Un cliente compra y el programa se desbloquea ==\n");

  for (const [sku, planEsperado] of [["licencia", "licencia"],
                                     ["pro", "professional"]]) {
    const r = await comprar(sku);
    check(`SKU "${sku}": el pago aprobado devuelve una licencia`, () => {
      assert.strictEqual(r.approved, true, "MP dijo aprobado y la API no");
      assert.ok(r.license_key, `no emitio licencia (motivo: ${r.motivo})`);
      assert.strictEqual(r.plan, sku, "la pagina muestra el SKU comprado");
      assert.strictEqual(r.tier, planEsperado, "el tier no es el esperado");
    });

    const v = verificarEnElPrograma(r.license_key);
    check(`SKU "${sku}": el PROGRAMA acepta esa licencia (plan ${planEsperado})`, () => {
      assert.strictEqual(v.valida, true, "el motor rechazo la licencia emitida");
      assert.strictEqual(v.plan, planEsperado);
      assert.strictEqual(v.email, "comprador@empresa.com");
    });
    check(`SKU "${sku}": habilita las 3 funciones pagas`, () => {
      const apagadas = Object.entries(v.funciones)
        .filter(([, on]) => !on).map(([f]) => f);
      assert.deepStrictEqual(apagadas, [],
        `pago y NO tiene: ${apagadas.join(", ")}`);
    });
  }

  console.log("\n== Lo que NO tiene que entregar licencia ==\n");

  const rechazo = await comprar("pro", { estado: "pending" });
  check("pago PENDIENTE: no emite licencia", () => {
    assert.strictEqual(rechazo.approved, false);
    assert.strictEqual(rechazo.license_key, null);
  });

  const viejo = await comprar("pro", { hace_min: 120 });
  check("pago aprobado hace 2 horas: fuera de ventana, no emite", () => {
    assert.strictEqual(viejo.license_key, null);
    assert.strictEqual(viejo.motivo, "fuera_de_ventana");
  });

  const skuRaro = await comprar("cred100");
  check("SKU que no otorga licencia: no emite y lo dice", () => {
    assert.strictEqual(skuRaro.license_key, null);
    assert.strictEqual(skuRaro.motivo, "sku_sin_licencia");
  });

  // sin emisor configurado — el caso que ESTABA pasando en produccion
  const guardada = process.env.LICENSE_PRIVATE_KEY;
  delete process.env.LICENSE_PRIVATE_KEY;
  const sinEmisor = await comprar("pro");
  process.env.LICENSE_PRIVATE_KEY = guardada;
  check("sin LICENSE_PRIVATE_KEY: no emite, y el motivo lo explica", () => {
    assert.strictEqual(sinEmisor.license_key, null);
    assert.strictEqual(sinEmisor.motivo, "emisor_no_configurado");
  });

  console.log("\n== La demo ==\n");
  const demo = verificarEnElPrograma("no-hay-licencia");
  check("sin licencia: el programa queda en demo y no habilita nada pagado",
    () => { assert.strictEqual(demo.valida, false); });

  if (fallos.length) {
    console.error(`\nFALLÓ: ${fallos.join("; ")}`);
    process.exit(1);
  }
  console.log(`\nTodos los checks de pago -> licencia pasaron (${ok}).`);
}

main();
