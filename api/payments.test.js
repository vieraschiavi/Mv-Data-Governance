// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
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
            await checkout({ method: "POST", headers: {}, body: { plan: "licencia" } }, res);
          }
        );
        assert.strictEqual(res._status, 200);
        assert.strictEqual(res._body.url, "https://mp.test/pay/abc");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    // --- suscripción: el plan mensual NO se cobra con una preferencia ------
    // Una preferencia cobra UNA VEZ. Que "pro" saliera por ahí era el bug:
    // US$390 anunciados por mes, cobrados una sola vez, licencia sin
    // vencimiento. Estos tres checks fijan el camino nuevo.
    await check("checkout: el plan mensual va a /preapproval, no a /preferences", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      let urlLlamada = null, cuerpo = null;
      try {
        await withMockFetch(
          async (url, opts) => {
            urlLlamada = url; cuerpo = JSON.parse(opts.body);
            return { ok: true, json: async () => ({ init_point: "https://mp.test/sub/abc" }) };
          },
          async () => {
            await checkout({ method: "POST", headers: {},
                             body: { plan: "pro", email: "cliente@empresa.com" } }, res);
          }
        );
        assert.ok(/\/preapproval$/.test(urlLlamada),
                  `se llamo a ${urlLlamada}: una preferencia cobra una sola vez`);
        assert.strictEqual(cuerpo.auto_recurring.frequency_type, "months");
        assert.strictEqual(cuerpo.auto_recurring.frequency, 1);
        assert.strictEqual(cuerpo.payer_email, "cliente@empresa.com");
        assert.strictEqual(res._status, 200);
        assert.strictEqual(res._body.url, "https://mp.test/sub/abc");
        assert.strictEqual(res._body.suscripcion, true);
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("checkout: suscripción sin email -> 400, sin tocar MercadoPago", async () => {
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      let toco = false;
      try {
        await withMockFetch(
          async () => { toco = true; return { ok: true, json: async () => ({}) }; },
          async () => {
            await checkout({ method: "POST", headers: {}, body: { plan: "pro" } }, res);
          }
        );
        assert.strictEqual(res._status, 400);
        assert.strictEqual(res._body.error, "email_requerido");
        assert.strictEqual(toco, false, "mando a MercadoPago un cuerpo que iba a rechazar");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
      }
    });
    await check("checkout: lo recurrente sale de la tabla SKU, no de checkout.js", async () => {
      // Si alguien saca `recurrente` de la tabla, el plan mensual vuelve a
      // cobrarse una sola vez y nada mas se entera. Esto lo ata.
      const { esRecurrente } = require("./_license");
      for (const sku of Object.keys(checkout.PLANS)) {
        const res = mockRes();
        const envToken = process.env.MP_ACCESS_TOKEN;
        process.env.MP_ACCESS_TOKEN = "token-de-test";
        let urlLlamada = null;
        try {
          await withMockFetch(
            async (url) => {
              urlLlamada = url;
              return { ok: true, json: async () => ({ init_point: "https://mp.test/x" }) };
            },
            async () => {
              await checkout({ method: "POST", headers: {},
                               body: { plan: sku, email: "c@e.com" } }, res);
            }
          );
        } finally {
          if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        }
        assert.strictEqual(/\/preapproval$/.test(urlLlamada), esRecurrente(sku),
          `'${sku}': esRecurrente=${esRecurrente(sku)} pero se llamo a ${urlLlamada}`);
      }
    });
    // ---- el aviso de "apreto Comprar" ---------------------------------
    await check("checkout: avisa por mail cuando alguien aprieta Comprar", async () => {
      // El reset limpia TAMBIEN el deduplicador de avisos, que comparte el
      // contador del limitador: sin esto, los clics de los checks anteriores
      // ya "gastaron" el aviso de este plan y no sale ninguno.
      rateLimit.resetForTests();
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envKey = process.env.RESEND_API_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      process.env.RESEND_API_KEY = "re_de_prueba";
      let aviso = null;
      try {
        await withMockFetch(
          async (url, opts) => {
            if (String(url).includes("resend.com")) {
              // La demora REAL es lo que hace util este test. Sin ella, una
              // promesa suelta (sin await) igual alcanzaba a resolverse antes
              // de la aserccion y el test quedaba VERDE con el await sacado —
              // verificado mutandolo. En Vercel no hay esa gracia: la funcion
              // se congela apenas responde y el mail no sale nunca. Con el
              // timer, "no esperaste" y "no llego" vuelven a ser lo mismo.
              await new Promise((r) => setTimeout(r, 25));
              aviso = JSON.parse(opts.body);
              return { ok: true, json: async () => ({ id: "x" }) };
            }
            return { ok: true, json: async () => ({ init_point: "https://mp.test/x" }) };
          },
          async () => {
            await checkout({ method: "POST", headers: {}, body: { plan: "licencia" } }, res);
          }
        );
        assert.strictEqual(res._status, 200);
        assert.ok(aviso, "no mando ningun aviso");
        assert.ok(/Comprar/i.test(aviso.subject), `asunto raro: ${aviso.subject}`);
        assert.ok(aviso.text.includes("149"), "el aviso no dice cuanto sale");
        // Texto plano, nunca html: parte del cuerpo lo escribio un desconocido.
        assert.strictEqual(aviso.html, undefined);
        // Y tiene que decir que NO es una venta: apretar Comprar no es pagar,
        // y confundir las dos cosas hace que uno crea que vendio y no vendio.
        assert.ok(/no es una venta|INTENCION/i.test(aviso.text),
                  "el aviso no aclara que todavia no pago");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envKey !== undefined) process.env.RESEND_API_KEY = envKey; else delete process.env.RESEND_API_KEY;
      }
    });

    await check("checkout: el que duda y toca cinco veces manda UN mail, no cinco", async () => {
      // Sin esto, a la tercera vez que pasa se dejan de leer los avisos — que
      // es peor que no tenerlos, porque el dia que llega uno de verdad ya esta
      // en la pila de los que se ignoran.
      rateLimit.resetForTests();
      const envToken = process.env.MP_ACCESS_TOKEN, envKey = process.env.RESEND_API_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      process.env.RESEND_API_KEY = "re_de_prueba";
      let mails = 0;
      const req = { method: "POST", headers: { "x-forwarded-for": "9.9.9.9" },
                    body: { plan: "licencia" } };
      try {
        await withMockFetch(
          async (url) => {
            if (String(url).includes("resend.com")) {
              mails++;
              return { ok: true, json: async () => ({ id: "x" }) };
            }
            return { ok: true, json: async () => ({ init_point: "https://mp.test/x" }) };
          },
          async () => {
            for (let i = 0; i < 5; i++) {
              const res = mockRes();
              await checkout(req, res);
              // Cada clic tiene que seguir llevandolo a MercadoPago: el
              // deduplicador silencia el MAIL, nunca la compra.
              assert.strictEqual(res._status, 200, `el clic ${i + 1} no pudo comprar`);
            }
          }
        );
        assert.strictEqual(mails, 1, `mando ${mails} mails por la misma persona`);

        // Otra persona (otra IP) SI tiene que avisar: si el deduplicador
        // silenciara a todos, el segundo cliente del dia pasaria inadvertido.
        await withMockFetch(
          async (url) => {
            if (String(url).includes("resend.com")) {
              mails++;
              return { ok: true, json: async () => ({ id: "x" }) };
            }
            return { ok: true, json: async () => ({ init_point: "https://mp.test/x" }) };
          },
          async () => {
            const res = mockRes();
            await checkout({ ...req, headers: { "x-forwarded-for": "8.8.4.4" } }, res);
            assert.strictEqual(res._status, 200);
          }
        );
        assert.strictEqual(mails, 2, "otra persona distinta no genero aviso");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envKey !== undefined) process.env.RESEND_API_KEY = envKey; else delete process.env.RESEND_API_KEY;
        rateLimit.resetForTests();
      }
    });

    await check("checkout: si el AVISO falla, la compra sigue igual", async () => {
      // La regla de oro: perder un mail es una molestia; perder una venta por
      // un mail es absurdo. Resend caido, clave vencida, red mala — el
      // comprador tiene que seguir yendo a MercadoPago.
      for (const comoFalla of [
        async () => { throw new Error("resend caido"); },
        async () => ({ ok: false, json: async () => ({ error: "clave vencida" }) }),
      ]) {
        // resetForTests limpia el deduplicador: sin esto el segundo caso
        // quedaria silenciado por el primero y no probaria nada.
        rateLimit.resetForTests();
        const res = mockRes();
        const envToken = process.env.MP_ACCESS_TOKEN, envKey = process.env.RESEND_API_KEY;
        process.env.MP_ACCESS_TOKEN = "token-de-test";
        process.env.RESEND_API_KEY = "re_de_prueba";
        try {
          await withMockFetch(
            async (url, opts) => {
              if (String(url).includes("resend.com")) return comoFalla(url, opts);
              return { ok: true, json: async () => ({ init_point: "https://mp.test/x" }) };
            },
            async () => {
              await checkout({ method: "POST", headers: {}, body: { plan: "licencia" } }, res);
            }
          );
          assert.strictEqual(res._status, 200,
            "el aviso caido se llevo puesta la compra");
          assert.strictEqual(res._body.url, "https://mp.test/x");
        } finally {
          if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
          if (envKey !== undefined) process.env.RESEND_API_KEY = envKey; else delete process.env.RESEND_API_KEY;
        }
      }
    });

    await check("checkout: sin RESEND_API_KEY no intenta avisar, y la compra anda", async () => {
      rateLimit.resetForTests();
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envKey = process.env.RESEND_API_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      delete process.env.RESEND_API_KEY;
      let tocoResend = false;
      try {
        await withMockFetch(
          async (url) => {
            if (String(url).includes("resend.com")) tocoResend = true;
            return { ok: true, json: async () => ({ init_point: "https://mp.test/x" }) };
          },
          async () => {
            await checkout({ method: "POST", headers: {}, body: { plan: "licencia" } }, res);
          }
        );
        assert.strictEqual(res._status, 200);
        assert.strictEqual(tocoResend, false, "llamo a Resend sin clave configurada");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envKey !== undefined) process.env.RESEND_API_KEY = envKey;
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
            await checkout({ method: "POST", headers: {},
                             body: { plan: "pro", email: "c@e.com" } }, res);
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
            await checkout({ method: "POST", headers: {},
                             body: { plan: "pro", email: "c@e.com" } }, res);
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
            // El SKU REAL que manda el checkout, no el PLAN — un valor que
            // MercadoPago nunca envia. El test decia "professional" y estaba
            // verde mientras el circuito real estaba roto: verificaba un
            // escenario que no puede ocurrir.
            //
            // Y es "licencia", el de pago unico: este endpoint es el del pago
            // de una sola vez. "pro" se cobra por suscripcion y su licencia
            // sale de /api/suscripcion (ver el check de mas abajo).
            metadata: { plan: "licencia" },
            payer: { email: "c@empresa.com" },
          }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "999" }, headers: {} }, res);
          }
        );
        assert.strictEqual(res._body.approved, true);
        assert.strictEqual(res._body.plan, "licencia");    // SKU, lo que muestra la pagina
        assert.strictEqual(res._body.tier, "licencia");    // plan que entiende el programa
        assert.ok(res._body.license_key && res._body.license_key.startsWith("MVDG2."));
        // y el token tiene que llevar el PLAN, no el SKU: con "pro" adentro,
        // licensing.verify() lo rechaza por plan desconocido y el cliente que
        // pago US$390/mes queda en demo.
        const cuerpo = JSON.parse(Buffer.from(
          res._body.license_key.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"),
          "base64").toString("utf8"));
        assert.strictEqual(cuerpo.plan, "licencia");
      } finally {
        if (envToken !== undefined) process.env.MP_ACCESS_TOKEN = envToken; else delete process.env.MP_ACCESS_TOKEN;
        if (envPriv !== undefined) process.env.LICENSE_PRIVATE_KEY = envPriv; else delete process.env.LICENSE_PRIVATE_KEY;
      }
    });
    await check("verify-payment: un SKU temporal emite el token CON vencimiento", async () => {
      // El bug real: "pro" se vendia mensual y el token salia sin `exp`, asi
      // que la suscripcion era perpetua. Este test atraviesa el handler de
      // verdad — no reimplementa la regla — poniendole vencimiento a un SKU.
      // Se muta SKU y no DIAS_POR_SKU: ese ultimo es una copia derivada, y
      // tocarlo no cambiaria nada. Que el test se rompa al mover la fuente de
      // verdad es correcto — significa que esta atado a ella y no a un espejo.
      // Se muta "licencia" porque este endpoint solo licencia lo de pago
      // unico; lo recurrente lo atiende /api/suscripcion.
      const lic = require("./_license");
      const original = lic.SKU.licencia.dias;
      lic.SKU.licencia.dias = 31;
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envPriv = process.env.LICENSE_PRIVATE_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(crypto.randomBytes(32));
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({
            status: "approved", date_approved: new Date().toISOString(),
            metadata: { plan: "licencia" },
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
        lic.SKU.licencia.dias = original;
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
    await check("verify-payment: un SKU por suscripcion NO se licencia por aca", async () => {
      // Una licencia emitida por este endpoint no lleva `sub` adentro, y sin
      // ese id el programa no sabe contra que suscripcion renovar: se
      // apagaria sola a los 35 dias y el cliente no tendria como recuperarla.
      // Entregar eso es peor que no entregar nada, porque parece que funciono.
      const res = mockRes();
      const envToken = process.env.MP_ACCESS_TOKEN, envPriv = process.env.LICENSE_PRIVATE_KEY;
      process.env.MP_ACCESS_TOKEN = "token-de-test";
      const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      process.env.LICENSE_PRIVATE_KEY = b64u(crypto.randomBytes(32));
      try {
        await withMockFetch(
          async () => ({ ok: true, json: async () => ({
            status: "approved", date_approved: new Date().toISOString(),
            metadata: { plan: "pro" },
            payer: { email: "c@empresa.com" },
          }) }),
          async () => {
            await verifyPayment({ query: { payment_id: "1003" }, headers: {} }, res);
          }
        );
        assert.strictEqual(res._body.approved, true);
        assert.strictEqual(res._body.license_key, null);
        assert.strictEqual(res._body.motivo, "sku_por_suscripcion");
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

  // ----------------------------------------------------------- api/acceso.js
  // Reemplaza al trial que se emitia solo. Aquel firmaba una licencia
  // Professional de 14 dias a cualquiera que escribiera un email — y con esa
  // licencia se bajaba el programa, asi que era la descarga abierta con un
  // formulario adelante. Este NO emite nada: avisa por mail y ya.
  {
    delete require.cache[require.resolve("./acceso")];
    rateLimit.resetForTests();
    const acceso = require("./acceso");

    const COMPLETO = { nombre: "Ana Perez", empresa: "Datos SA",
                       pais: "Uruguay", email: "ana@datos.com" };

    async function conResend(impl, fn) {
      const antes = process.env.RESEND_API_KEY;
      process.env.RESEND_API_KEY = "re_de_prueba";
      try { await withMockFetch(impl, fn); } finally {
        if (antes !== undefined) process.env.RESEND_API_KEY = antes;
        else delete process.env.RESEND_API_KEY;
      }
    }

    await check("acceso: metodo distinto de POST -> 405", async () => {
      const res = mockRes();
      await acceso({ method: "GET", headers: {}, body: {} }, res);
      assert.strictEqual(res._status, 405);
    });

    await check("acceso: faltan datos -> 400 y dice cuales", async () => {
      await conResend(async () => { throw new Error("no tenia que llamar"); },
        async () => {
          const res = mockRes();
          await acceso({ method: "POST", headers: {},
                         body: { email: "a@b.com" } }, res);
          assert.strictEqual(res._status, 400);
          assert.strictEqual(res._body.error, "faltan_datos");
          assert.deepStrictEqual(res._body.campos.sort(),
                                 ["empresa", "nombre", "pais"]);
        });
    });

    await check("acceso: email invalido -> 400", async () => {
      for (const malo of ["no-es-email", "a@b", "@sin-usuario.com", " "]) {
        rateLimit.resetForTests();
        const res = mockRes();
        await acceso({ method: "POST", headers: {},
                       body: { ...COMPLETO, email: malo } }, res);
        assert.strictEqual(res._status, 400, `deberia rechazar: ${malo}`);
      }
    });

    await check("acceso: NUNCA emite una licencia, ni con todo correcto", async () => {
      // Es el punto entero del cambio. Si algun dia esto devuelve una clave,
      // volvimos a la descarga automatica con un formulario adelante.
      await conResend(async () => ({ ok: true, json: async () => ({ id: "x" }) }),
        async () => {
          rateLimit.resetForTests();
          const res = mockRes();
          await acceso({ method: "POST", headers: {}, body: COMPLETO }, res);
          assert.strictEqual(res._status, 200);
          assert.strictEqual(res._body.ok, true);
          const cuerpo = JSON.stringify(res._body);
          assert.ok(!/MVDG[12]\./.test(cuerpo), "devolvio una licencia");
          assert.strictEqual(res._body.license_key, undefined);
        });
    });

    await check("acceso: el mail va al dueno, en texto plano y con reply_to del que pidio", async () => {
      let enviado = null;
      await conResend(async (url, opts) => {
        enviado = { url, cuerpo: JSON.parse(opts.body),
                    auth: opts.headers.Authorization };
        return { ok: true, json: async () => ({ id: "x" }) };
      }, async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await acceso({ method: "POST", headers: {},
                       body: { ...COMPLETO, mensaje: "martes a las 10" } }, res);
        assert.strictEqual(res._status, 200);
      });
      assert.strictEqual(enviado.url, "https://api.resend.com/emails");
      assert.strictEqual(enviado.auth, "Bearer re_de_prueba");
      assert.deepStrictEqual(enviado.cuerpo.to, [acceso.DESTINO]);
      // reply_to y no replyTo: la API REST de Resend usa snake_case. Con el
      // nombre equivocado el campo se ignora y responder el aviso le contesta
      // a Resend, no al que pidio la demo.
      assert.strictEqual(enviado.cuerpo.reply_to, COMPLETO.email);
      // texto plano, nunca html: es contenido que escribio un desconocido
      assert.strictEqual(enviado.cuerpo.html, undefined);
      for (const dato of [COMPLETO.nombre, COMPLETO.empresa, COMPLETO.pais,
                          COMPLETO.email, "martes a las 10"]) {
        assert.ok(enviado.cuerpo.text.includes(dato), `falta en el mail: ${dato}`);
      }
      // el asunto ordena la bandeja sin abrir el mail
      assert.ok(enviado.cuerpo.subject.includes(COMPLETO.empresa));
    });

    await check("acceso: sin RESEND_API_KEY -> 503, no dice 'gracias' y pierde el pedido", async () => {
      const antes = process.env.RESEND_API_KEY;
      delete process.env.RESEND_API_KEY;
      try {
        rateLimit.resetForTests();
        const res = mockRes();
        await acceso({ method: "POST", headers: {}, body: COMPLETO }, res);
        assert.strictEqual(res._status, 503);
        assert.strictEqual(res._body.ok, false);
        assert.strictEqual(res._body.error, "mail_no_configurado");
      } finally {
        if (antes !== undefined) process.env.RESEND_API_KEY = antes;
      }
    });

    await check("acceso: si Resend falla -> 502, tampoco dice que llego", async () => {
      await conResend(async () => ({ ok: false, json: async () => ({}) }),
        async () => {
          rateLimit.resetForTests();
          const res = mockRes();
          await acceso({ method: "POST", headers: {}, body: COMPLETO }, res);
          assert.strictEqual(res._status, 502);
          assert.strictEqual(res._body.ok, false);
        });
    });

    await check("acceso: recorta campos larguisimos en vez de mandar un mail de 2 MB", async () => {
      let enviado = null;
      await conResend(async (url, opts) => {
        enviado = JSON.parse(opts.body); return { ok: true, json: async () => ({}) };
      }, async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await acceso({ method: "POST", headers: {},
                       body: { ...COMPLETO, empresa: "x".repeat(500_000) } }, res);
        assert.strictEqual(res._status, 200);
      });
      assert.ok(enviado.text.length < 5000, `mail de ${enviado.text.length} bytes`);
    });

    await check("acceso: rate limit corta a los 5 de la misma IP", async () => {
      await conResend(async () => ({ ok: true, json: async () => ({}) }),
        async () => {
          rateLimit.resetForTests();
          let ultimo;
          for (let i = 0; i < 6; i++) {
            ultimo = mockRes();
            await acceso({ method: "POST", headers: { "x-forwarded-for": "7.7.7.7" },
                           body: COMPLETO }, ultimo);
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

    // La descarga ya NO es publica: exige una licencia MVDG2 valida. Como
    // este test no tiene la clave privada de produccion, se genera un par
    // efimero y se le dice a _license.js que verifique con esa publica.
    const parRaw = crypto.randomBytes(32);
    const aB64u = (b) => Buffer.from(b).toString("base64")
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const privDemo = aB64u(parRaw);
    const pubDemo = aB64u(crypto.createPublicKey(crypto.createPrivateKey({
      key: Buffer.concat([Buffer.from("302e020100300506032b657004220420", "hex"), parRaw]),
      format: "der", type: "pkcs8",
    })).export({ format: "der", type: "spki" }).subarray(-32));
    process.env.LICENSE_PUBLIC_KEY = pubDemo;
    const ahora = Math.floor(Date.now() / 1000);
    // `k` valida para todos los casos que prueban OTRA cosa que no es el gate.
    const K = license.signEd25519({ plan: "licencia", iat: ahora }, privDemo);
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
        await descargar({ method: "GET", url: "/api/descargar", query: { k: K } }, res);
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
        await descargar({ method: "GET", query: { k: K } }, res);
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
        await descargar({ method: "GET", query: { k: K } }, res);
        assert.strictEqual(res._status, 500);
        assert.strictEqual(res._body.error, "url_insegura");
        assert.ok(!res._headers.location);
      });
    });

    await check("descargar: URL mal formada no explota, responde 500", async () => {
      await conUrl("no-es-una-url", async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET", query: { k: K } }, res);
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
          await descargar({ method: "GET", query: { plan, k: K } }, res);
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
        await descargar({ method: "POST", query: { k: K } }, res);
        assert.strictEqual(res._status, 405);
      });
    });

    // ---- el gate: la demo se pide, no se baja ---------------------------
    await check("descargar: SIN licencia no baja nada (403), aunque este todo configurado", async () => {
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET", query: {} }, res);
        assert.strictEqual(res._status, 403);
        assert.strictEqual(res._body.error, "licencia_requerida");
        assert.ok(!res._headers.location, "redirigio igual: el gate no sirve");
        // el mensaje dice como conseguirla, en los 3 idiomas
        for (const k of ["es", "en", "pt"]) {
          assert.ok(res._body[k] && res._body[k].includes("descargas.html"));
        }
      });
    });

    await check("descargar: una licencia inventada o manipulada no sirve", async () => {
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        const partes = K.split(".");
        const manipulada = partes[0] + "." + partes[1] + "." +
                           partes[2].slice(0, -2) + "xx";
        const otroPar = license.signEd25519({ plan: "owner", iat: ahora },
                                            aB64u(crypto.randomBytes(32)));
        for (const malo of ["MVDG2.x.y", "cualquier-cosa", manipulada,
                            otroPar, "MVDG1." + partes[1] + "." + partes[2]]) {
          rateLimit.resetForTests();
          const res = mockRes();
          await descargar({ method: "GET", query: { k: malo } }, res);
          assert.strictEqual(res._status, 403,
            `dejo pasar una licencia que no vale: ${malo.slice(0, 24)}`);
          assert.ok(!res._headers.location);
        }
      });
    });

    await check("descargar: una licencia VENCIDA no sirve", async () => {
      // El caso del que probo la demo hace tres meses. Sin esto, la licencia
      // de prueba seria una llave permanente a la descarga.
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        const vencida = license.signEd25519(
          { plan: "trial", iat: ahora - 100 * 86400, exp: ahora - 86400 }, privDemo);
        const res = mockRes();
        await descargar({ method: "GET", query: { k: vencida } }, res);
        assert.strictEqual(res._status, 403);
        assert.strictEqual(res._body.error, "licencia_invalida");
      });
    });

    await check("descargar: una licencia de prueba VIGENTE si sirve", async () => {
      // El que hizo la demo 1 a 1 tiene que poder instalarlo.
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        const trial = license.signEd25519(
          { plan: "trial", iat: ahora, exp: ahora + 14 * 86400 }, privDemo);
        const res = mockRes();
        await descargar({ method: "GET", query: { k: trial } }, res);
        assert.strictEqual(res._status, 302);
      });
    });

    await check("descargar: sin licencia NO revela si el instalador esta configurado", async () => {
      // Responder 503 "falta MVDG_INSTALLER_URL" a un desconocido le cuenta
      // como esta armado el backend. El 403 va primero, siempre.
      await conUrl(null, async () => {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET", query: {} }, res);
        assert.strictEqual(res._status, 403);
      });
    });

    // ---- cada plan baja SU build --------------------------------------
    await check("descargar: el OWNER baja el build owner, no el del cliente", async () => {
      // El bug que esto cierra: habia una sola variable, asi que el owner
      // —con su licencia owner— bajaba el mismo .exe sin desbloquear que un
      // cliente. La version owner existia en Actions y no llegaba por ningun
      // lado.
      const antesC = process.env.MVDG_INSTALLER_URL;
      const antesO = process.env.MVDG_INSTALLER_URL_OWNER;
      process.env.MVDG_INSTALLER_URL = "https://ejemplo.com/cliente.exe";
      process.env.MVDG_INSTALLER_URL_OWNER = "https://ejemplo.com/owner.exe";
      try {
        rateLimit.resetForTests();
        const kOwner = license.signEd25519({ plan: "owner", iat: ahora }, privDemo);
        const res = mockRes();
        await descargar({ method: "GET", query: { k: kOwner } }, res);
        assert.strictEqual(res._status, 302);
        assert.strictEqual(res._headers.location, "https://ejemplo.com/owner.exe");
      } finally {
        if (antesC !== undefined) process.env.MVDG_INSTALLER_URL = antesC; else delete process.env.MVDG_INSTALLER_URL;
        if (antesO !== undefined) process.env.MVDG_INSTALLER_URL_OWNER = antesO; else delete process.env.MVDG_INSTALLER_URL_OWNER;
      }
    });

    await check("descargar: NINGUN plan que no sea owner llega al build owner", async () => {
      // Lo inverso, que es lo que importa para que no se filtre: el build
      // owner viene desbloqueado, y aunque este atado a una maquina no tiene
      // por que salir a pasear.
      const antesC = process.env.MVDG_INSTALLER_URL;
      const antesO = process.env.MVDG_INSTALLER_URL_OWNER;
      process.env.MVDG_INSTALLER_URL = "https://ejemplo.com/cliente.exe";
      process.env.MVDG_INSTALLER_URL_OWNER = "https://ejemplo.com/owner.exe";
      try {
        for (const plan of ["licencia", "professional", "trial", "demo",
                            "enterprise", "OWNER", "owner ", "", null]) {
          rateLimit.resetForTests();
          const k = license.signEd25519({ plan, iat: ahora }, privDemo);
          const res = mockRes();
          await descargar({ method: "GET", query: { k } }, res);
          assert.strictEqual(res._headers.location, "https://ejemplo.com/cliente.exe",
            `el plan ${JSON.stringify(plan)} llego al build owner`);
        }
      } finally {
        if (antesC !== undefined) process.env.MVDG_INSTALLER_URL = antesC; else delete process.env.MVDG_INSTALLER_URL;
        if (antesO !== undefined) process.env.MVDG_INSTALLER_URL_OWNER = antesO; else delete process.env.MVDG_INSTALLER_URL_OWNER;
      }
    });

    await check("descargar: sin el build owner configurado, el owner NO recibe el del cliente", async () => {
      // Caer al build del cliente en silencio es como se termina probando el
      // producto equivocado creyendo que se probo el bueno. Falla ruidoso y
      // dice QUE variable falta.
      const antesC = process.env.MVDG_INSTALLER_URL;
      const antesO = process.env.MVDG_INSTALLER_URL_OWNER;
      process.env.MVDG_INSTALLER_URL = "https://ejemplo.com/cliente.exe";
      delete process.env.MVDG_INSTALLER_URL_OWNER;
      try {
        rateLimit.resetForTests();
        const kOwner = license.signEd25519({ plan: "owner", iat: ahora }, privDemo);
        const res = mockRes();
        await descargar({ method: "GET", query: { k: kOwner } }, res);
        assert.strictEqual(res._status, 503);
        assert.ok(!res._headers.location, "le dio el build del cliente al owner");
        assert.strictEqual(res._body.variable, "MVDG_INSTALLER_URL_OWNER");
        for (const idioma of ["es", "en", "pt"]) {
          assert.ok(res._body[idioma].includes("MVDG_INSTALLER_URL_OWNER"));
        }
      } finally {
        if (antesC !== undefined) process.env.MVDG_INSTALLER_URL = antesC; else delete process.env.MVDG_INSTALLER_URL;
        if (antesO !== undefined) process.env.MVDG_INSTALLER_URL_OWNER = antesO; else delete process.env.MVDG_INSTALLER_URL_OWNER;
      }
    });

    await check("descargar: el ?plan= de la URL NO puede pedir el build owner", async () => {
      // El plan sale de la licencia firmada. Si saliera de la query,
      // ?plan=owner seria la llave del build desbloqueado para cualquiera.
      const antesC = process.env.MVDG_INSTALLER_URL;
      const antesO = process.env.MVDG_INSTALLER_URL_OWNER;
      process.env.MVDG_INSTALLER_URL = "https://ejemplo.com/cliente.exe";
      process.env.MVDG_INSTALLER_URL_OWNER = "https://ejemplo.com/owner.exe";
      try {
        rateLimit.resetForTests();
        const res = mockRes();
        await descargar({ method: "GET", query: { k: K, plan: "owner" } }, res);
        assert.strictEqual(res._headers.location, "https://ejemplo.com/cliente.exe",
          "?plan=owner alcanzo para bajar el build desbloqueado");
      } finally {
        if (antesC !== undefined) process.env.MVDG_INSTALLER_URL = antesC; else delete process.env.MVDG_INSTALLER_URL;
        if (antesO !== undefined) process.env.MVDG_INSTALLER_URL_OWNER = antesO; else delete process.env.MVDG_INSTALLER_URL_OWNER;
      }
    });

    await check("descargar: rate limit corta a los 30 de la misma IP", async () => {
      await conUrl("https://ejemplo.com/setup.exe", async () => {
        rateLimit.resetForTests();
        let ultimo;
        for (let i = 0; i < 31; i++) {
          ultimo = mockRes();
          await descargar({ method: "GET", query: { k: K } }, ultimo);
        }
        assert.strictEqual(ultimo._status, 429);
        rateLimit.resetForTests();
      });
    });
    delete process.env.LICENSE_PUBLIC_KEY;
  }

  // ------------------------------------- coherencia de la cadena comercial
  //
  // Lo que se OFRECE, lo que se puede COBRAR y lo que se ENTREGA son tres
  // listas en tres archivos distintos, y nada las ataba. Hoy coinciden porque
  // se cuidaron a mano; alcanza con agregar un plan en la landing y olvidarse
  // del checkout para que el boton devuelva 400, o agregarlo al checkout y
  // olvidarse de la tabla SKU para cobrar algo que no entrega licencia.
  //
  // Es exactamente el bug que _license.js ya cerro un nivel mas abajo (un SKU
  // con plan y sin plazo). La leccion de aquella vez fue que un test que hay
  // que acordarse de escribir no sirve: lo que sirve es que la estructura lo
  // impida o que algo lo verifique solo. Aca no se pueden fusionar los tres
  // archivos (uno es HTML estatico), asi que se verifica.
  {
    const fs = require("node:fs");
    const path = require("node:path");
    const checkout = require("./checkout");
    const planesCheckout = Object.keys(checkout.PLANS).sort();
    const skus = Object.keys(license.SKU).sort();

    await check("comercial: todo plan cobrable tiene entrada en la tabla SKU",
      () => {
        const huerfanos = planesCheckout.filter((p) => !skus.includes(p));
        assert.deepStrictEqual(huerfanos, [],
          `estos planes se cobran pero no entregan licencia: ${huerfanos}`);
      });

    await check("comercial: todo SKU que entrega licencia se puede cobrar",
      () => {
        const invendibles = skus.filter((s) => !planesCheckout.includes(s));
        assert.deepStrictEqual(invendibles, [],
          `estos SKU otorgan licencia pero no hay forma de comprarlos: ${invendibles}`);
      });

    await check("comercial: cada boton de compra de la landing existe en el checkout",
      () => {
        const html = fs.readFileSync(
          path.join(__dirname, "..", "landing", "index.html"), "utf8");
        const botones = [...html.matchAll(/data-mp="([a-z0-9_]+)"/g)]
          .map((m) => m[1]);
        assert.ok(botones.length > 0, "no se encontro ningun boton data-mp");
        const rotos = botones.filter((b) => !planesCheckout.includes(b));
        assert.deepStrictEqual(rotos, [],
          `botones que responderian 400 plan_invalido: ${rotos}`);
      });
  }

  // ------------------------------------------ checkout: dominio de retorno
  {
    const { sitioDeConfianza } = require("./checkout");
    const CANON = "mv-data-governance.vercel.app";

    await check("checkout: un Host ajeno NO decide a donde vuelve el comprador",
      () => {
        assert.strictEqual(sitioDeConfianza("atacante.com"), CANON);
        assert.strictEqual(sitioDeConfianza("evil.com:443"), CANON);
        // formas de torcer la URL, no dominios
        assert.strictEqual(sitioDeConfianza("evil.com/x"), CANON);
        assert.strictEqual(sitioDeConfianza("a@evil.com"), CANON);
        assert.strictEqual(sitioDeConfianza(""), CANON);
        assert.strictEqual(sitioDeConfianza(undefined), CANON);
      });

    await check("checkout: los previews de Vercel siguen funcionando", () => {
      const preview = "mv-data-governance-git-rama-mv13.vercel.app";
      assert.strictEqual(sitioDeConfianza(preview), preview);
      assert.strictEqual(sitioDeConfianza(CANON), CANON);
      // ...pero no un dominio que solo TERMINA parecido
      assert.strictEqual(sitioDeConfianza("vercel.app.evil.com"), CANON);
    });

    await check("checkout: un dominio propio se habilita con MVDG_SITE_HOST",
      () => {
        const antes = process.env.MVDG_SITE_HOST;
        process.env.MVDG_SITE_HOST = "mvdatagovernance.com";
        try {
          assert.strictEqual(sitioDeConfianza("mvdatagovernance.com"),
                             "mvdatagovernance.com");
          assert.strictEqual(sitioDeConfianza("otro.com"), CANON);
        } finally {
          if (antes === undefined) delete process.env.MVDG_SITE_HOST;
          else process.env.MVDG_SITE_HOST = antes;
        }
      });
  }

  console.log(`\nTodos los checks de pago/licencia pasaron (${checks}).`);
}

main().catch((e) => { console.error("FALLÓ:", e); process.exit(1); });
