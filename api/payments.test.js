/*
 * Test de comportamiento REAL de las funciones serverless de pago/licencia.
 * Antes estos 3 archivos (checkout.js, verify-payment.js, _license.js)
 * tenían 0% de cobertura de ejecución: los únicos tests existentes hacían
 * grep sobre el texto fuente, nunca llamaban a los handlers. Esto SÍ los
 * ejecuta, con mocks de req/res y de fetch (nunca toca la red real ni
 * MercadoPago). Node puro, sin dependencias — mismo patrón que
 * electron/lib/server-manager.test.js. Corré con:
 *   node api/payments.test.js
 */
const assert = require("node:assert");
const crypto = require("node:crypto");

const license = require("./_license");
const rateLimit = require("./_rate_limit");

let checks = 0;
async function check(desc, fn) {
  // await explícito: si no se espera fn(), los checks async corren en
  // paralelo y se pisan entre sí el estado compartido (rate limiter,
  // process.env) — eso rompió esta misma suite en la primera corrida.
  await fn();
  checks++;
  console.log(`✓ ${desc}`);
}

function mockRes() {
  const res = {
    _status: null, _body: null, _headers: {}, _ended: false,
    status(code) { this._status = code; return this; },
    json(obj) { this._body = obj; return this; },
    // Un redirect no responde con json(): setea Location y termina. Sin esto
    // el test de descargar.js explotaría por método inexistente.
    setHeader(k, v) { this._headers[k.toLowerCase()] = v; return this; },
    end() { this._ended = true; return this; },
  };
  return res;
}

async function withMockFetch(impl, fn) {
  const real = global.fetch;
  global.fetch = impl;
  try { await fn(); } finally { global.fetch = real; }
}

async function main() {
  // ----------------------------------------------------- api/_license.js
  {
    const secret = "s3creto-de-test";
    const payload = { plan: "professional", email: "c@empresa.com" };
    const token = license.sign(payload, secret);
    await check("_license: sign()+verify() HMAC roundtrip", () => {
      const out = license.verify(token, secret);
      assert.deepStrictEqual(out, payload);
    });
    await check("_license: verify() rechaza secreto equivocado", () => {
      assert.strictEqual(license.verify(token, "otro-secreto"), null);
    });
    await check("_license: verify() rechaza firma manipulada", () => {
      const partes = token.split(".");
      const roto = partes[0] + "." + partes[1] + "." + partes[2].slice(0, -2) + "xx";
      assert.strictEqual(license.verify(roto, secret), null);
    });
    await check("_license: verify() rechaza formato inválido", () => {
      assert.strictEqual(license.verify("no-es-un-token", secret), null);
      assert.strictEqual(license.verify(null, secret), null);
      assert.strictEqual(license.verify(123, secret), null);
    });
  }
  {
    // Ed25519: par de prueba generado con la misma codificación que
    // packaging/licencias.py keygen (32 bytes crudos en base64url).
    const raw = crypto.randomBytes(32);
    const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const privB64u = b64u(raw);
    const der = Buffer.concat([Buffer.from("302e020100300506032b657004220420", "hex"), raw]);
    const privKeyObj = crypto.createPrivateKey({ key: der, format: "der", type: "pkcs8" });
    const pubKeyObj = crypto.createPublicKey(privKeyObj);
    const pubRaw = pubKeyObj.export({ format: "der", type: "spki" }).subarray(-32);

    const payload = { plan: "owner", email: "owner@test.com" };
    const token = license.signEd25519(payload, privB64u);
    await check("_license: signEd25519() produce MVDG2.<payload>.<firma>", () => {
      const partes = token.split(".");
      assert.strictEqual(partes.length, 3);
      assert.strictEqual(partes[0], "MVDG2");
    });
    await check("_license: la firma Ed25519 verifica con la clave pública correspondiente", () => {
      const partes = token.split(".");
      const sig = Buffer.from(partes[2].replace(/-/g, "+").replace(/_/g, "/"), "base64");
      const pubKey = crypto.createPublicKey({
        key: Buffer.concat([Buffer.from("302a300506032b6570032100", "hex"), pubRaw]),
        format: "der", type: "spki",
      });
      const ok = crypto.verify(null, Buffer.from(partes[1], "ascii"), pubKey, sig);
      assert.strictEqual(ok, true);
    });
    await check("_license: signEd25519() rechaza una clave privada de largo incorrecto", () => {
      assert.throws(() => license.signEd25519(payload, b64u(Buffer.alloc(16))));
    });
  }

  // --------------------------------------------------- api/_rate_limit.js
  {
    rateLimit.resetForTests();
    await check("_rate_limit: deja pasar hasta el máximo y corta después", () => {
      const opts = { max: 3, windowMs: 60_000 };
      assert.strictEqual(rateLimit.rateLimited("1.2.3.4", opts), false);
      assert.strictEqual(rateLimit.rateLimited("1.2.3.4", opts), false);
      assert.strictEqual(rateLimit.rateLimited("1.2.3.4", opts), false);
      assert.strictEqual(rateLimit.rateLimited("1.2.3.4", opts), true);
    });
    await check("_rate_limit: cada IP tiene su propio contador", () => {
      const opts = { max: 1, windowMs: 60_000 };
      assert.strictEqual(rateLimit.rateLimited("5.5.5.5", opts), false);
      assert.strictEqual(rateLimit.rateLimited("6.6.6.6", opts), false);
    });
    await check("_rate_limit: clientIp() usa x-forwarded-for y cae a remoteAddress", () => {
      assert.strictEqual(rateLimit.clientIp({ headers: { "x-forwarded-for": "9.9.9.9, 1.1.1.1" } }), "9.9.9.9");
      assert.strictEqual(rateLimit.clientIp({ headers: {}, socket: { remoteAddress: "127.0.0.1" } }), "127.0.0.1");
    });
  }

  // ----------------------------------------------------- api/checkout.js
  {
    delete require.cache[require.resolve("./checkout")];
    rateLimit.resetForTests();
    const checkout = require("./checkout");

    await check("checkout: rechaza método distinto de POST", async () => {
      const res = mockRes();
      await checkout({ method: "GET", headers: {} }, res);
      assert.strictEqual(res._status, 405);
    });
    await check("checkout: plan inválido -> 400 (sin tocar red)", async () => {
      const res = mockRes();
      await checkout({ method: "POST", headers: {}, body: { plan: "no-existe" } }, res);
      assert.strictEqual(res._status, 400);
      assert.strictEqual(res._body.error, "plan_invalido");
    });
    await check("checkout: plan válido con payload como string se parsea", async () => {
      const res = mockRes();
      const envAntes = process.env.MP_ACCESS_TOKEN;
      delete process.env.MP_ACCESS_TOKEN;
      try {
        await checkout({ method: "POST", headers: {}, body: '{"plan":"licencia"}' }, res);
        assert.strictEqual(res._status, 503); // sin token ni link: 503 medio_pago_no_configurado
      } finally {
        if (envAntes !== undefined) process.env.MP_ACCESS_TOKEN = envAntes;
      }
    });
    await check("checkout: sin token pero con link configurado -> devuelve el link", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envLink = process.env.MP_LINK_LICENCIA;
      delete process.env.MP_ACCESS_TOKEN;
      process.env.MP_LINK_LICENCIA = "https://link.mercadopago.com/xyz";
      try {
        await checkout({ method: "POST", headers: {}, body: { plan: "licencia" } }, res);
        assert.strictEqual(res._status, 200);
        assert.strictEqual(res._body.url, "https://link.mercadopago.com/xyz");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken;
        if (envLink !== undefined) process.env.MP_LINK_LICENCIA = envLink; else delete process.env.MP_LINK_LICENCIA;
      }
    });
    await check("checkout: con token, MercadoPago responde OK -> 200 con la URL real", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({ init_point: "https://mp.test/pay/abc" }) }),
          async () => {
            await checkout({ method: "POST", headers: {}, body: { plan: "pro" } }, res);
          }
        );
        assert.strictEqual(res._status, 200);
        assert.strictEqual(res._body.url, "https://mp.test/pay/abc");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("checkout: MercadoPago responde error -> 502, nunca 200", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      try {
        await withMockFetch(
          async () => ({ ok: false, json: async () => ({}) }),
          async () => {
            await checkout({ method: "POST", headers: {}, body: { plan: "pro" } }, res);
          }
        );
        assert.strictEqual(res._status, 502);
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("checkout: fetch tira una excepción -> 500, no revienta el proceso", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      try {
        await withMockFetch(
          async () => { throw new Error("red caída"); },
          async () => {
            await checkout({ method: "POST", headers: {}, body: { plan: "pro" } }, res);
          }
        );
        assert.strictEqual(res._status, 500);
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("checkout: rate limit corta después de 20 requests de la misma IP", async () => {
      rateLimit.resetForTests();
      const req = { method: "GET", headers: { "x-forwarded-for": "8.8.8.8" } };
      let ultimo;
      for (let i = 0; i < 21; i++) {
        const res = mockRes();
        await checkout(req, res);
        ultimo = res;
      }
      assert.strictEqual(ultimo._status, 429);
      assert.strictEqual(ultimo._body.error, "rate_limit");
      rateLimit.resetForTests();
    });
  }

  // ----------------------------------------------- api/verify-payment.js
  {
    delete require.cache[require.resolve("./verify-payment")];
    rateLimit.resetForTests();
    const verifyPayment = require("./verify-payment");

    await check("verify-payment: payment_id vacío -> 400", async () => {
      const res = mockRes();
      await verifyPayment({ query: {}, headers: {} }, res);
      assert.strictEqual(res._status, 400);
    });
    await check("verify-payment: rechaza payment_id con caracteres no numéricos (intento de inyección)", async () => {
      const res = mockRes();
      for (const payload of ["1; DROP TABLE pagos;--", "<script>alert(1)</script>", "../../etc/passwd", "1 OR 1=1"]) {
        const r = mockRes();
        await verifyPayment({ query: { payment_id: payload }, headers: {} }, r);
        assert.strictEqual(r._status, 400, `payload no bloqueado: ${payload}`);
      }
      res.status(400); // silenciar "unused" del linter mental
    });
    await check("verify-payment: sin MP_ACCESS_TOKEN -> 500 no_token", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      delete process.env.MP_ACCESS_TOKEN;
      try {
        await verifyPayment({ query: { payment_id: "12345" }, headers: {} }, res);
        assert.strictEqual(res._status, 500);
        assert.strictEqual(res._body.error, "no_token");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken;
      }
    });
    await check("verify-payment: pago aprobado -> approved=true y emite licencia Ed25519", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envPriv = process.env.LICENSE_PRIVATE_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const raw = crypto.randomBytes(32);
      const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(raw);
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({
            status: "approved", date_approved: new Date().toISOString(),
            // "pro" es el SKU REAL que manda el checkout. Este test decia
            // "professional", que es el PLAN — un valor que MercadoPago nunca
            // envia. Por eso el test estaba verde mientras el circuito real
            // estaba roto: verificaba un escenario que no puede ocurrir.
            metadata: { plan: "pro" },
            payer: { email: "c@empresa.com" },
          }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "999" }, headers: {} }, res);
          }
        );
        assert.strictEqual(res._body.approved, true);
        assert.strictEqual(res._body.plan, "pro");            // SKU, lo que muestra la pagina
        assert.strictEqual(res._body.tier, "professional");   // plan que entiende el programa
        assert.ok(res._body.license_key && res._body.license_key.startsWith("MVDG2."));
        // y el token tiene que llevar el PLAN, no el SKU: con "pro" adentro,
        // licensing.verify() lo rechaza por plan desconocido y el cliente que
        // pago US$390/mes queda en demo.
        const cuerpo = JSON.parse(Buffer.from(
          res._body.license_key.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"),
          "base64").toString("utf8"));
        assert.strictEqual(cuerpo.plan, "professional");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envPriv !== undefined) process.env.LICENSE_PRIVATE_KEY = envPriv; else delete process.env.LICENSE_PRIVATE_KEY;
      }
    });
    await check("verify-payment: un SKU temporal emite el token CON vencimiento", async () => {
      // El bug real: "pro" se vendia mensual y el token salia sin `exp`, asi
      // que la suscripcion era perpetua. Este test atraviesa el handler de
      // verdad — no reimplementa la regla — subiendo pro a 31 dias.
      // Se muta SKU y no DIAS_POR_SKU: ese ultimo es una copia derivada, y
      // tocarlo no cambiaria nada. Que el test se rompa al mover la fuente de
      // verdad es correcto — significa que esta atado a ella y no a un espejo.
      const lic = require("./_license");
      const original = lic.SKU.pro.dias;
      lic.SKU.pro.dias = 31;
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envPriv = process.env.LICENSE_PRIVATE_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(crypto.randomBytes(32));
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({
            status: "approved", date_approved: new Date().toISOString(), metadata: { plan: "pro" },
            payer: { email: "c@empresa.com" },
          }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "1001" }, headers: {} }, res);
          }
        );
        const cuerpo = JSON.parse(Buffer.from(
          res._body.license_key.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"),
          "base64").toString("utf8"));
        assert.ok(cuerpo.exp, "un SKU de 31 dias tiene que emitir `exp`");
        assert.strictEqual(cuerpo.exp - cuerpo.iat, 31 * 86400);
      } finally {
        lic.SKU.pro.dias = original;
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envPriv !== undefined) process.env.LICENSE_PRIVATE_KEY = envPriv; else delete process.env.LICENSE_PRIVATE_KEY;
      }
    });
    await check("verify-payment: un SKU perpetuo NO lleva vencimiento", async () => {
      // El otro lado: con 0 dias el token no puede llevar `exp`, o el cliente
      // que compro una licencia de pago unico se quedaria sin ella.
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envPriv = process.env.LICENSE_PRIVATE_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(crypto.randomBytes(32));
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({
            status: "approved", date_approved: new Date().toISOString(), metadata: { plan: "licencia" },
            payer: { email: "c@empresa.com" },
          }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "1002" }, headers: {} }, res);
          }
        );
        const cuerpo = JSON.parse(Buffer.from(
          res._body.license_key.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"),
          "base64").toString("utf8"));
        assert.strictEqual(cuerpo.exp, undefined);
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envPriv !== undefined) process.env.LICENSE_PRIVATE_KEY = envPriv; else delete process.env.LICENSE_PRIVATE_KEY;
      }
    });
    // --- la ventana de emision -------------------------------------------
    // El payment_id viaja en la URL de retorno del comprador, y este endpoint
    // no ata quien llama con quien pago. Sin ventana, un id compartido emitia
    // licencias perpetuas ilimitadas.
    const conPago = async (mp) => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envPriv = process.env.LICENSE_PRIVATE_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const b64u = (b) => Buffer.from(b).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(crypto.randomBytes(32));
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => mp }),
          async () => {
            await verifyPayment({ query: { payment_id: "2000" }, headers: {} }, res);
          }
        );
        return res._body;
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envPriv !== undefined) process.env.LICENSE_PRIVATE_KEY = envPriv; else delete process.env.LICENSE_PRIVATE_KEY;
      }
    };
    const base = { status: "approved", metadata: { plan: "licencia" }, payer: { email: "c@x.com" } };

    await check("verify-payment: un pago VIEJO no emite licencia", async () => {
      const hace2h = new Date(Date.now() - 2 * 3600 * 1000).toISOString();
      const b = await conPago({ ...base, date_approved: hace2h });
      assert.strictEqual(b.approved, true);   // el pago sigue siendo real
      assert.strictEqual(b.license_key, null);
      assert.strictEqual(b.license, null);    // tampoco la HMAC
      assert.strictEqual(b.motivo, "fuera_de_ventana");
    });
    await check("verify-payment: un pago SIN fecha falla cerrado", async () => {
      // No se puede afirmar que sea reciente, asi que no se afirma. Si MP
      // cambiara el formato, las ventas se cortan de golpe y se arregla — en
      // vez de dejar la ventana abierta sin que nadie se entere.
      const b = await conPago({ ...base });
      assert.strictEqual(b.license_key, null);
      assert.strictEqual(b.motivo, "fuera_de_ventana");
    });
    await check("verify-payment: un pago RECIENTE si emite licencia", async () => {
      const b = await conPago({ ...base, date_approved: new Date().toISOString() });
      assert.ok(b.license_key && b.license_key.startsWith("MVDG2."));
      assert.strictEqual(b.motivo, undefined);
    });
    await check("verify-payment: date_created sirve si no hay date_approved", async () => {
      const b = await conPago({ ...base, date_created: new Date().toISOString() });
      assert.ok(b.license_key && b.license_key.startsWith("MVDG2."));
    });

    // --- el registro de pagos ya usados ----------------------------------
    // Cierra lo que la ventana solo achicaba: adentro de esos 30 minutos el
    // id servia infinitas veces. Se simula el KV en memoria con la misma
    // semantica de Upstash (SET NX devuelve "OK" o null).
    const kvFalso = () => {
      const store = new Map();
      return {
        store,
        fetch: async (url, opts) => {
          const cmds = JSON.parse(opts.body);
          return { ok: true, json: async () => cmds.map(([op, k, v]) => {
            if (op === "SET") {
              if (store.has(k)) return { result: null };   // NX: ya estaba
              store.set(k, v); return { result: "OK" };
            }
            return { result: store.has(k) ? store.get(k) : null };
          }) };
        },
      };
    };
    const conKV = async (kv, mpBody, paymentId) => {
      const res = mockRes();
      const env = {
        MP_ACCESS_TOKEN: process.env.MP_ACCESS_TOKEN,
        LICENSE_PRIVATE_KEY: process.env.LICENSE_PRIVATE_KEY,
        KV_REST_API_URL: process.env.KV_REST_API_URL,
        KV_REST_API_TOKEN: process.env.KV_REST_API_TOKEN,
      };
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const b64u = (b) => Buffer.from(b).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(crypto.randomBytes(32));
      process.env.KV_REST_API_URL = "https://kv.de.test";
      process.env.KV_REST_API_TOKEN = "tok";
      try {
        await withMockFetch(
          async (url, opts) => (String(url).includes("kv.de.test")
            ? kv.fetch(url, opts)
            : { ok: true, json: async () => mpBody }),
          async () => {
            await verifyPayment({ query: { payment_id: paymentId }, headers: {} }, res);
          }
        );
        return res._body;
      } finally {
        for (const [k, v] of Object.entries(env)) {
          if (v !== undefined) process.env[k] = v; else delete process.env[k];
        }
      }
    };
    const pagoFresco = () => ({
      status: "approved", date_approved: new Date().toISOString(),
      metadata: { plan: "licencia" }, payer: { email: "c@x.com" },
    });

    await check("registro: el MISMO payment_id no emite una segunda licencia", async () => {
      const kv = kvFalso();
      const a = await conKV(kv, pagoFresco(), "3001");
      assert.ok(a.license_key, "la primera vez si tiene que emitir");
      // Se envejece la marca mas alla de la gracia: ya no es una recarga.
      const clave = "mvdg:pago:3001";
      kv.store.set(clave, String(Date.now() - 60 * 60_000));
      const b = await conKV(kv, pagoFresco(), "3001");
      assert.strictEqual(b.license_key, null);
      assert.strictEqual(b.license, null);       // tampoco la HMAC
      assert.strictEqual(b.motivo, "ya_emitida");
    });
    await check("registro: recargar la pagina SI vuelve a mostrar la licencia", async () => {
      // Un solo uso estricto dejaria sin licencia al que aprieta F5. Eso es
      // un ticket de soporte garantizado, asi que hay una gracia corta.
      const kv = kvFalso();
      const a = await conKV(kv, pagoFresco(), "3002");
      const b = await conKV(kv, pagoFresco(), "3002");
      assert.ok(a.license_key && b.license_key);
      assert.strictEqual(b.motivo, undefined);
    });
    await check("registro: si el KV se cae, la venta NO se corta", async () => {
      // Fallar cerrado significaria que una caida de Upstash impide comprar a
      // TODOS. Se degrada a la ventana de tiempo, que es lo de antes.
      const kv = { fetch: async () => { throw new Error("KV caido"); } };
      const b = await conKV(kv, pagoFresco(), "3003");
      assert.ok(b.license_key, "una caida del KV no puede bloquear una compra");
    });
    await check("registro: sin KV configurado se comporta como antes", async () => {
      const { registrar } = require("./_usados");
      const env = { u: process.env.KV_REST_API_URL, t: process.env.KV_REST_API_TOKEN };
      delete process.env.KV_REST_API_URL; delete process.env.KV_REST_API_TOKEN;
      try {
        assert.strictEqual(await registrar("9999"), "sin_registro");
      } finally {
        if (env.u !== undefined) process.env.KV_REST_API_URL = env.u;
        if (env.t !== undefined) process.env.KV_REST_API_TOKEN = env.t;
      }
    });

    await check("verify-payment: pago NO aprobado -> approved=false, license siempre null", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({ status: "rejected", metadata: {} }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "999" }, headers: {} }, res);
          }
        );
        assert.strictEqual(res._body.approved, false);
        assert.strictEqual(res._body.license, null);
        assert.strictEqual(res._body.license_key, null);
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("verify-payment: metadata.plan con HTML (dato de una API externa) nunca se ejecuta, solo viaja como string", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({
            status: "approved", date_approved: new Date().toISOString(), metadata: { plan: "<img src=x onerror=alert(1)>" }, payer: {},
          }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "1" }, headers: {} }, res);
          }
        );
        // El handler no sanitiza (no es su trabajo: nunca lo inyecta en HTML,
        // solo lo devuelve como JSON). Lo que importa es que viaje intacto
        // como STRING de datos y no como código: si esto fuera a un innerHTML
        // sin escapar en el frontend, ESE es el punto que cubre
        // landing/security.test.js con la misma carga útil.
        assert.strictEqual(typeof res._body.plan, "string");
        assert.strictEqual(res._body.plan, "<img src=x onerror=alert(1)>");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("verify-payment: MercadoPago responde error -> 502", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      try {
        await withMockFetch(
          async () => ({ ok: false, json: async () => ({}) }),
          async () => {
            await verifyPayment({ query: { payment_id: "1" }, headers: {} }, res);
          }
        );
        assert.strictEqual(res._status, 502);
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("verify-payment: rate limit corta después de 30 requests de la misma IP", async () => {
      rateLimit.resetForTests();
      const req = { query: { payment_id: "1" }, headers: { "x-forwarded-for": "7.7.7.7" } };
      let ultimo;
      for (let i = 0; i < 31; i++) {
        const res = mockRes();
        await verifyPayment(req, res);
        ultimo = res;
      }
      assert.strictEqual(ultimo._status, 429);
      rateLimit.resetForTests();
    });
  }

  // ------------------------------------------------------------ api/trial.js
  // Trial de 14 días del plan Professional (USD 390/mes), SIN tarjeta: nunca
  // pasa por MercadoPago ni pide datos de pago — solo email. Antes de esto no
  // existía ningún flujo de trial real, solo un botón "pedir demo".
  {
    delete require.cache[require.resolve("./trial")];
    rateLimit.resetForTests();
    const trial = require("./trial");

    const b64u = (buf) => Buffer.from(buf).toString("base64")
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const b64uDecode = (s) => Buffer.from(
      s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - s.length % 4) % 4), "base64");

    function conClavePrivada(fn) {
      const antes = process.env.LICENSE_PRIVATE_KEY;
      const raw = crypto.randomBytes(32);
      process.env.LICENSE_PRIVATE_KEY = b64u(raw);
      return Promise.resolve().then(fn).finally(() => {
        if (antes !== undefined) process.env.LICENSE_PRIVATE_KEY = antes;
        else delete process.env.LICENSE_PRIVATE_KEY;
      });
    }

    await check("trial: sin email -> 400, no emite nada", async () => {
      await conClavePrivada(async () => {
        const res = mockRes();
        await trial({ method: "POST", body: {} }, res);
        assert.strictEqual(res._status, 400);
      });
    });

    await check("trial: email inválido -> 400", async () => {
      await conClavePrivada(async () => {
        for (const malo of ["no-es-email", "a@b", "@sin-usuario.com", "  "]) {
          const res = mockRes();
          await trial({ method: "POST", body: { email: malo } }, res);
          assert.strictEqual(res._status, 400, `debería rechazar: ${malo}`);
        }
      });
    });

    await check("trial: método distinto de POST -> 405", async () => {
      await conClavePrivada(async () => {
        const res = mockRes();
        await trial({ method: "GET", body: {} }, res);
        assert.strictEqual(res._status, 405);
      });
    });

    await check("trial: sin LICENSE_PRIVATE_KEY configurada -> 503, nunca una licencia rota", async () => {
      const antes = process.env.LICENSE_PRIVATE_KEY;
      delete process.env.LICENSE_PRIVATE_KEY;
      try {
        const res = mockRes();
        await trial({ method: "POST", body: { email: "consultor@empresa.com" } }, res);
        assert.strictEqual(res._status, 503);
        assert.strictEqual(res._body.license_key, undefined);
      } finally {
        if (antes !== undefined) process.env.LICENSE_PRIVATE_KEY = antes;
      }
    });

    await check("trial: email válido -> 200, emite MVDG2 sin pedir NINGÚN dato de pago", async () => {
      await conClavePrivada(async () => {
        const res = mockRes();
        const antes = Date.now();
        await trial({ method: "POST", body: { email: "Consultor@Empresa.com" } }, res);
        assert.strictEqual(res._status, 200);
        assert.strictEqual(res._body.plan, "trial");
        assert.strictEqual(res._body.email, "consultor@empresa.com"); // normalizado a minúsculas
        assert.ok(res._body.license_key.startsWith("MVDG2."));

        // El payload firmado es el único lugar donde viaja informacion: no
        // tiene payment_id, tarjeta, ni ningun campo de pago — es literalmente
        // imposible que el flujo pida una tarjeta si el payload nunca la tiene.
        const partes = res._body.license_key.split(".");
        const payload = JSON.parse(b64uDecode(partes[1]).toString("utf8"));
        assert.deepStrictEqual(Object.keys(payload).sort(), ["email", "exp", "iat", "plan"]);
        assert.strictEqual(payload.plan, "trial");

        // 14 dias exactos entre emision y vencimiento.
        assert.strictEqual(payload.exp - payload.iat, 14 * 86400);
        assert.ok(payload.iat * 1000 >= antes - 2000);
      });
    });

    await check("trial: la firma verifica de forma independiente con la clave pública (crypto.verify puro)", async () => {
      const rawPriv = crypto.randomBytes(32);
      const der = Buffer.concat([
        Buffer.from("302e020100300506032b657004220420", "hex"), rawPriv,
      ]);
      const privKeyObj = crypto.createPrivateKey({ key: der, format: "der", type: "pkcs8" });
      const pubKeyObj = crypto.createPublicKey(privKeyObj);
      const pubRaw = pubKeyObj.export({ type: "spki", format: "der" }).subarray(-32);

      const antes = process.env.LICENSE_PRIVATE_KEY;
      process.env.LICENSE_PRIVATE_KEY = b64u(rawPriv);
      try {
        delete require.cache[require.resolve("./trial")];
        const trial2 = require("./trial");
        const res = mockRes();
        await trial2({ method: "POST", body: { email: "otra@empresa.com" } }, res);
        const [, body, sig] = res._body.license_key.split(".");
        const ok = crypto.verify(null, Buffer.from(body, "ascii"), pubKeyObj, b64uDecode(sig));
        assert.strictEqual(ok, true);
        // con la clave publica INCORRECTA, no verifica
        const otraPub = crypto.generateKeyPairSync("ed25519").publicKey;
        const falso = crypto.verify(null, Buffer.from(body, "ascii"), otraPub, b64uDecode(sig));
        assert.strictEqual(falso, false);
      } finally {
        if (antes !== undefined) process.env.LICENSE_PRIVATE_KEY = antes; else delete process.env.LICENSE_PRIVATE_KEY;
      }
    });

    await check("trial: rate limit corta después de 10 requests de la misma IP", async () => {
      await conClavePrivada(async () => {
        rateLimit.resetForTests();
        const req = { method: "POST", body: { email: "loop@empresa.com" } };
        let ultimo;
        for (let i = 0; i < 11; i++) {
          const res = mockRes();
          await trial(req, res);
          ultimo = res;
        }
        assert.strictEqual(ultimo._status, 429);
        rateLimit.resetForTests();
      });
    });
  }

  {
    // ---------------------------------------------------------------- descargas
    // El .exe no vive en el repo ni en el deploy (pesa cientos de MB): la
    // landing pega a /api/descargar y este redirige a donde este alojado.
    const descargar = require("./descargar");
    const ANTES = process.env.MVDG_INSTALLER_URL;
    const conUrl = async (valor, fn) => {
      if (valor === null) delete process.env.MVDG_INSTALLER_URL;
      else process.env.MVDG_INSTALLER_URL = valor;
      try { await fn(); } finally {
        if (ANTES !== undefined) process.env.MVDG_INSTALLER_URL = ANTES;
        else delete process.env.MVDG_INSTALLER_URL;
      }
    };

    await check("descargar: redirige 302 a la URL configurada", async () => {
      await conUrl("https://ejemplo.com/MVDataGovernance_Setup.exe", async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET", url: "/api/descargar" }, res);
        assert.strictEqual(res._status, 302);
        assert.strictEqual(res._headers.location,
          "https://ejemplo.com/MVDataGovernance_Setup.exe");
        // no-store: si el hosting cambia, nadie queda pegado al viejo
        assert.strictEqual(res._headers["cache-control"], "no-store");
        assert.ok(res._ended);
      });
    });

    await check("descargar: sin configurar responde 503 y NO inventa una URL", async () => {
      await conUrl(null, async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET" }, res);
        assert.strictEqual(res._status, 503);
        assert.strictEqual(res._body.error, "sin_configurar");
        // el mensaje dice QUE falta, en los 3 idiomas
        for (const k of ["es", "en", "pt"]) {
          assert.ok(res._body[k].includes("MVDG_INSTALLER_URL"));
        }
        assert.ok(!res._headers.location, "no debe redirigir a ningun lado");
      });
    });

    await check("descargar: rechaza http:// (un .exe se descarga por https o nada)", async () => {
      await conUrl("http://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET" }, res);
        assert.strictEqual(res._status, 500);
        assert.strictEqual(res._body.error, "url_insegura");
        assert.ok(!res._headers.location);
      });
    });

    await check("descargar: URL mal formada no explota, responde 500", async () => {
      await conUrl("no-es-una-url", async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET" }, res);
        assert.strictEqual(res._status, 500);
        assert.strictEqual(res._body.error, "url_invalida");
      });
    });

    await check("descargar: el plan NO cambia el archivo (demo y full son el mismo .exe)", async () => {
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        const destinos = [];
        for (const plan of ["demo", "full", undefined, "inventado"]) {
          rateLimit.resetForTests();
          const res = mockRes();
          await descargar({ method: "GET", query: { plan } }, res);
          destinos.push(res._headers.location);
        }
        assert.strictEqual(new Set(destinos).size, 1,
          "el parametro plan no debe elegir un archivo distinto");
      });
    });

    await check("descargar: POST no sirve para bajar (405)", async () => {
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "POST" }, res);
        assert.strictEqual(res._status, 405);
      });
    });

    await check("descargar: rate limit corta a los 30 de la misma IP", async () => {
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        let ultimo;
        for (let i = 0; i < 31; i++) {
          ultimo = mockRes();
          await descargar({ method: "GET" }, ultimo);
        }
        assert.strictEqual(ultimo._status, 429);
        rateLimit.resetForTests();
      });
    });
  }

  console.log(`\nTodos los checks de pago/licencia pasaron (${checks}).`);
}

main().catch((e) => { console.error("FALLÓ:", e); process.exit(1); });
