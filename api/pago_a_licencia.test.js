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
                  "sub": p.get("sub"), "funciones": funcs}))
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

  // Solo los SKU de PAGO UNICO: este endpoint es el del pago de una sola vez.
  // "pro" se cobra por suscripcion y su licencia sale de /api/suscripcion —
  // esta mas abajo, con su propio circuito completo hasta Python.
  for (const [sku, planEsperado] of [["licencia", "licencia"]]) {
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

  const rechazo = await comprar("licencia", { estado: "pending" });
  check("pago PENDIENTE: no emite licencia", () => {
    assert.strictEqual(rechazo.approved, false);
    assert.strictEqual(rechazo.license_key, null);
  });

  const viejo = await comprar("licencia", { hace_min: 120 });
  check("pago aprobado hace 2 horas: fuera de ventana, no emite", () => {
    assert.strictEqual(viejo.license_key, null);
    assert.strictEqual(viejo.motivo, "fuera_de_ventana");
  });

  const skuRaro = await comprar("cred100");
  check("SKU que no otorga licencia: no emite y lo dice", () => {
    assert.strictEqual(skuRaro.license_key, null);
    assert.strictEqual(skuRaro.motivo, "sku_sin_licencia");
  });

  // Un pago suelto de un SKU mensual NO se licencia por aca. La licencia que
  // saldria de este endpoint no lleva `sub` adentro, asi que el programa no
  // sabria contra que suscripcion renovar: se apagaria sola a los 35 dias y
  // el cliente no tendria forma de recuperarla. Es peor que no darle nada,
  // porque parece que funciono.
  const mensual = await comprar("pro");
  check("SKU mensual por la via de pago unico: no emite, va por /api/suscripcion", () => {
    assert.strictEqual(mensual.approved, true);
    assert.strictEqual(mensual.license_key, null);
    assert.strictEqual(mensual.motivo, "sku_por_suscripcion");
  });

  // sin emisor configurado — el caso que ESTABA pasando en produccion
  const guardada = process.env.LICENSE_PRIVATE_KEY;
  delete process.env.LICENSE_PRIVATE_KEY;
  const sinEmisor = await comprar("licencia");
  process.env.LICENSE_PRIVATE_KEY = guardada;
  check("sin LICENSE_PRIVATE_KEY: no emite, y el motivo lo explica", () => {
    assert.strictEqual(sinEmisor.license_key, null);
    assert.strictEqual(sinEmisor.motivo, "emisor_no_configurado");
  });

  console.log("\n== Suscripcion Professional (el cobro mensual de verdad) ==\n");
  {
    delete require.cache[require.resolve(path.join(RAIZ, "api/suscripcion.js"))];
    const suscripcion = require(path.join(RAIZ, "api/suscripcion.js"));

    async function consultar(id, estado, email) {
      rl.resetForTests();
      global.fetch = async () => ({
        ok: true, status: 200,
        json: async () => ({ status: estado, payer_email: email || null }),
      });
      const res = mockRes();
      await suscripcion({ query: { id }, headers: {} }, res);
      global.fetch = real;
      return res._body;
    }

    const activa = await consultar("2c93808493", "authorized", "sus@empresa.com");
    check("suscripcion al dia: emite licencia CON vencimiento", () => {
      assert.strictEqual(activa.activa, true);
      assert.ok(activa.license_key, `no emitio (motivo: ${activa.motivo})`);
    });

    const v = verificarEnElPrograma(activa.license_key);
    check("el PROGRAMA la acepta como professional y habilita las 3", () => {
      assert.strictEqual(v.valida, true);
      assert.strictEqual(v.plan, "professional");
      assert.deepStrictEqual(
        Object.entries(v.funciones).filter(([, on]) => !on).map(([f]) => f), []);
    });

    check("la licencia VENCE (esto es lo que se estaba perdiendo)", () => {
      assert.ok(v.exp, "salio SIN vencimiento: el cliente paga un mes y se " +
                       "queda con el plan para siempre");
      const dias = Math.round((v.exp - Date.now() / 1000) / 86400);
      assert.ok(dias > 30 && dias <= 36,
        `vence en ${dias} dias; se esperaban ~35`);
    });

    // Y lo que hace que vencer no rompa al que paga: la licencia se puede
    // renovar sola porque lleva su propio id de suscripcion adentro.
    check("lleva el id de la suscripcion, para poder renovarse sola", () => {
      const cuerpo = JSON.parse(Buffer.from(
        activa.license_key.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"),
        "base64").toString());
      assert.strictEqual(cuerpo.sub, "2c93808493",
        "sin `sub` el programa no sabe por cual suscripcion preguntar");
    });

    for (const estado of ["pending", "paused", "cancelled"]) {
      const r = await consultar("2c93808493", estado);
      check(`suscripcion "${estado}": NO renueva`, () => {
        assert.strictEqual(r.activa, false);
        assert.ok(!r.license_key);
      });
    }

    check("un id con formato invalido se rechaza sin llamar a MercadoPago",
      () => {
        rl.resetForTests();
      });
    for (const malo of ["", "../otro", "a", "x".repeat(80)]) {
      rl.resetForTests();
      const res = mockRes();
      await suscripcion({ query: { id: malo }, headers: {} }, res);
      check(`id invalido ${JSON.stringify(malo.slice(0, 12))} -> 400`, () => {
        assert.strictEqual(res._status, 400);
      });
    }
  }

  console.log("\n== La descarga: la misma licencia abre las dos puertas ==\n");
  {
    // La demo dejo de ser de descarga libre: /api/descargar exige una
    // licencia. Si el servidor y el programa no coincidieran en QUE licencia
    // es valida, el cliente que paga podria quedar de un lado y no del otro —
    // con la clave puesta en el programa y un 403 al querer bajarlo, o al
    // reves. Esto verifica que el MISMO token pase los dos chequeos.
    delete require.cache[require.resolve(path.join(RAIZ, "api/descargar.js"))];
    const antesPub = process.env.LICENSE_PUBLIC_KEY;
    process.env.LICENSE_PUBLIC_KEY = PUBLICA;
    process.env.MVDG_INSTALLER_URL = "https://ejemplo.com/setup.exe";
    const descargar = require(path.join(RAIZ, "api/descargar.js"));

    async function bajar(k) {
      rl.resetForTests();
      const res = mockRes();
      await descargar({ method: "GET", query: k === null ? {} : { k }, headers: {} }, res);
      return res;
    }

    const compra = await comprar("licencia");
    const conLicencia = await bajar(compra.license_key);
    check("el que compro puede bajar el instalador con su licencia", () => {
      assert.strictEqual(conLicencia._status, 302,
        `no lo dejo bajar (motivo: ${JSON.stringify(conLicencia._body)})`);
    });
    check("y el programa acepta esa MISMA licencia", () => {
      assert.strictEqual(verificarEnElPrograma(compra.license_key).valida, true);
    });

    const sinNada = await bajar(null);
    check("sin licencia NO se baja el instalador", () => {
      assert.strictEqual(sinNada._status, 403);
    });

    // Una licencia vencida: rechazada por los dos lados, no por uno solo.
    const iat = Math.floor(Date.now() / 1000) - 100 * 86400;
    const vencida = require(path.join(RAIZ, "api/_license.js"))
      .signEd25519({ plan: "trial", iat: iat, exp: iat + 86400 }, PRIVADA);
    const conVencida = await bajar(vencida);
    check("una licencia vencida no baja el instalador NI abre el programa", () => {
      assert.strictEqual(conVencida._status, 403, "el servidor la dejo pasar");
      assert.strictEqual(verificarEnElPrograma(vencida).valida, false,
                         "el programa la dejo pasar");
    });

    delete process.env.MVDG_INSTALLER_URL;
    if (antesPub !== undefined) process.env.LICENSE_PUBLIC_KEY = antesPub;
    else delete process.env.LICENSE_PUBLIC_KEY;
  }

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
