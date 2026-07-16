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

const PLANS = {
  licencia: { title: "MV Data Governance · Licencia PC (pago único)", price: 149.0 },
  pro:      { title: "MV Data Governance · Professional (mensual)",   price: 390.0 },
  cred100:  { title: "MV Data Governance · 100 créditos",             price: 9.0 },
  cred550:  { title: "MV Data Governance · 550 créditos",             price: 39.0 },
  cred2500: { title: "MV Data Governance · 2.500 créditos",           price: 149.0 },
};
const CURRENCY = process.env.MP_CURRENCY || "USD";  // coincide con los precios mostrados en la landing (US$)

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ error: "method" }); return; }

  const body = typeof req.body === "string" ? safeJson(req.body) : (req.body || {});
  const plan = String(body.plan || "").toLowerCase();
  const p = PLANS[plan];
  if (!p) { res.status(400).json({ error: "plan_invalido" }); return; }

  const base = "https://" + (req.headers.host || "mv-data-governance.vercel.app");
  const token = process.env.MP_ACCESS_TOKEN;
  const link = process.env["MP_LINK_" + plan.toUpperCase()];

  // Sin Access Token: si hay link de pago configurado, devuelvo ese.
  if (!token) {
    if (link) { res.status(200).json({ url: link }); return; }
    res.status(503).json({ error: "medio_pago_no_configurado" });
    return;
  }

  try {
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
    res.status(200).json({ url: data.init_point });
  } catch (e) {
    res.status(500).json({ error: "exception" });
  }
};

function safeJson(s) { try { return JSON.parse(s); } catch (e) { return {}; } }

module.exports.PLANS = PLANS;
