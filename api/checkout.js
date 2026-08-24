// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Checkout de MercadoPago — función serverless (Vercel, CommonJS).
// El Access Token de MercadoPago vive SOLO como variable de entorno del
// servidor (MP_ACCESS_TOKEN). Nunca se expone al navegador ni se guarda en
// el repo. Alternativa sin token: configurar links de pago por producto
// (MP_LINK_LICENCIA, MP_LINK_PRO, MP_LINK_CRED100, MP_LINK_CRED550,
// MP_LINK_CRED2500) — ver docs/MERCADOPAGO.md.
//
// Sin verificación BotID: la tuvimos y BLOQUEABA A TODOS LOS COMPRADORES
// REALES — checkBotId clasifica como bot cualquier pedido que no traiga la
// firma del cliente de BotID, y esta landing (HTML estático) nunca integró
// ese cliente, así que el 100% de los clics reales en "Comprar" recibían
// 403 {"error":"bot"}. Si algún día se reincorpora, tiene que ser junto
// con la instrumentación del lado del navegador, nunca solo del lado del
// servidor. El riesgo sin ella es bajo: esto solo crea una preferencia de
// pago (nadie cobra nada sin pagar de verdad en MercadoPago).

const { rateLimited, clientIp } = require("./_rate_limit");
const { esRecurrente } = require("./_license");
const { avisarIntentoDeCompra } = require("./_aviso");

// Solo lo que es propio del cobro: como se llama y cuanto sale. SI se cobra
// todos los meses o una sola vez NO se decide aca — sale de la tabla SKU de
// _license.js, que es la misma de la que sale el vencimiento del token. Que
// vivan juntos no es prolijidad: "se vende mensual" y "la licencia vence" son
// el mismo hecho, y tenerlos en dos archivos distintos fue exactamente el
// bug — la landing cobraba US$390/mes y el token salia sin vencimiento.
const PLANS = {
  licencia: { title: "MV Data Governance · Licencia PC (pago único)", price: 149.0 },
  pro:      { title: "MV Data Governance · Professional (mensual)",   price: 390.0 },
};
const CURRENCY = process.env.MP_CURRENCY || "USD";  // coincide con los precios mostrados en la landing (US$)

module.exports = async (req, res) => {
  // 20/min por IP: de sobra para un click de "Comprar" con algún reintento,
  // corta un script creando preferencias de pago en loop.
  if (rateLimited(clientIp(req), { max: 20, windowMs: 60_000 })) {
    res.status(429).json({ error: "rate_limit" });
    return;
  }
  if (req.method !== "POST") { res.status(405).json({ error: "method" }); return; }

  const body = typeof req.body === "string" ? safeJson(req.body) : (req.body || {});
  const plan = String(body.plan || "").toLowerCase();
  const p = PLANS[plan];
  if (!p) { res.status(400).json({ error: "plan_invalido" }); return; }

  const base = "https://" + sitioDeConfianza(req.headers && req.headers.host);
  const token = process.env.MP_ACCESS_TOKEN;
  const link = process.env["MP_LINK_" + plan.toUpperCase()];

  // Sin Access Token: si hay link de pago configurado, devuelvo ese.
  if (!token) {
    if (link) {
      await avisarIntentoDeCompra({
        plan, titulo: p.title, precio: p.price, moneda: CURRENCY,
        suscripcion: esRecurrente(plan), host: base, ip: clientIp(req),
      });
      res.status(200).json({ url: link });
      return;
    }
    res.status(503).json({ error: "medio_pago_no_configurado" });
    return;
  }

  try {
    if (esRecurrente(plan)) {
      // ----------------------------------------------------------------
      // Suscripcion (preapproval): MercadoPago cobra solo cada mes.
      // ----------------------------------------------------------------
      // payer_email es obligatorio para crear un preapproval, asi que el
      // boton de la landing lo pide antes de mandar acá. Sin email no se
      // puede crear la suscripcion — se corta con un mensaje claro en vez
      // de mandarle a MercadoPago un cuerpo que va a rechazar.
      const email = String(body.email || "").trim();
      if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        res.status(400).json({ error: "email_requerido" });
        return;
      }
      const sus = {
        reason: p.title,
        // El comprador vuelve acá con ?preapproval_id=... y con eso la
        // pagina pide su primera licencia a /api/suscripcion.
        back_url: base + "/pago.html?sus=1",
        payer_email: email,
        auto_recurring: {
          frequency: 1,
          frequency_type: "months",
          transaction_amount: p.price,
          currency_id: CURRENCY,
        },
        status: "pending",
      };
      const r = await fetch("https://api.mercadopago.com/preapproval", {
        method: "POST",
        headers: { Authorization: "Bearer " + token,
                   "Content-Type": "application/json" },
        body: JSON.stringify(sus),
      });
      const data = await r.json();
      if (!r.ok || !data.init_point) {
        res.status(502).json({ error: "mercadopago" });
        return;
      }
      // El aviso va ANTES de responder: en serverless la funcion se congela
      // apenas responde, asi que una promesa suelta no llega a mandarse.
      // avisar() no lanza nunca — si el mail falla, la compra sigue igual.
      await avisarIntentoDeCompra({
        plan, titulo: p.title, precio: p.price, moneda: CURRENCY,
        email, suscripcion: true, host: base, ip: clientIp(req),
      });
      res.status(200).json({ url: data.init_point, suscripcion: true });
      return;
    }

    const pref = {
      items: [{ title: p.title, quantity: 1, unit_price: p.price, currency_id: CURRENCY }],
      back_urls: {
        success: base + "/pago.html?status=approved&plan=" + plan,
        pending: base + "/pago.html?status=pending",
        failure: base + "/index.html#precios",
      },
      auto_return: "approved",
      metadata: { plan: plan },
    };
    const r = await fetch("https://api.mercadopago.com/checkout/preferences", {
      method: "POST",
      headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" },
      body: JSON.stringify(pref),
    });
    const data = await r.json();
    if (!r.ok || !data.init_point) {
      res.status(502).json({ error: "mercadopago" });
      return;
    }
    await avisarIntentoDeCompra({
      plan, titulo: p.title, precio: p.price, moneda: CURRENCY,
      suscripcion: false, host: base, ip: clientIp(req),
    });
    res.status(200).json({ url: data.init_point });
  } catch (e) {
    res.status(500).json({ error: "exception" });
  }
};

function safeJson(s) { try { return JSON.parse(s); } catch (e) { return {}; } }

// El dominio al que MercadoPago devuelve al comprador DESPUES de pagar.
//
// Antes salia directo de `req.headers.host`, que lo pone quien hace el pedido.
// Hoy Vercel solo enruta hosts que son del proyecto, asi que no era explotable
// — pero el dia que eso cambie, o si esto se mueve a otro hosting, un Host
// falseado mandaria al comprador (con su payment_id en la URL) a un sitio
// ajeno, y ese sitio podria pedir la licencia con ese id. Es barato no
// depender de que el borde nos proteja.
//
// Se acepta: el dominio propio, cualquier *.vercel.app (los previews de cada
// PR, que tienen que seguir funcionando) y lo que se declare en MVDG_SITE_HOST.
// Si mañana se pone un dominio propio, se agrega ahi; mientras tanto el
// comprador vuelve al dominio canonico — feo pero funcional, nunca a un
// tercero.
const HOST_CANONICO = "mv-data-governance.vercel.app";

function sitioDeConfianza(host) {
  const h = String(host || "").trim().toLowerCase();
  // Un host valido es solo letras, digitos, puntos, guiones y un puerto.
  // Cualquier otra cosa (barras, arrobas, espacios) es un intento de
  // torcer la URL, no un dominio.
  if (!/^[a-z0-9.-]+(:[0-9]{1,5})?$/.test(h)) return HOST_CANONICO;
  const propio = (process.env.MVDG_SITE_HOST || "").trim().toLowerCase();
  if (propio && h === propio) return h;
  if (h === HOST_CANONICO) return h;
  if (/^[a-z0-9-]+(\.[a-z0-9-]+)*\.vercel\.app$/.test(h)) return h;
  return HOST_CANONICO;
}

module.exports.PLANS = PLANS;
module.exports.sitioDeConfianza = sitioDeConfianza;
