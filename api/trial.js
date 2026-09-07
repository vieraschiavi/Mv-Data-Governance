// Prueba gratuita de 14 días del plan Professional (USD 390/mes) — SIN
// tarjeta de crédito ni paso por MercadoPago. Emite la misma licencia Ed25519
// (MVDG2) que recibiría alguien que pagó, pero con `exp` a 14 días: el
// programa la revalida en cada lectura (ver mvdg/licensing.py::verify) y
// vuelve solo a plan demo al vencer — no hace falta ningún código de
// "downgrade", el mismo chequeo de vencimiento que ya cubren los tests.
//
// Limite honesto: sin base de datos (Vercel serverless es sin estado), no
// hay forma de impedir que la misma persona pida varios trials con emails
// distintos. El rate limit por IP frena un script en loop, no a alguien
// decidido a probarlo dos veces — es la misma clase de límite que ya declara
// _rate_limit.js para el resto de estas funciones, no un agujero nuevo.

const { signEd25519 } = require("./_license");
const { rateLimited, clientIp } = require("./_rate_limit");

const DIAS_TRIAL = 14;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

module.exports = async (req, res) => {
  // 10/min por IP: un trial no es algo que se pida en loop; el límite bajo
  // es a propósito, más estricto que checkout (20/min) porque acá no hay
  // ningún paso de pago real que ya frene el abuso por costo.
  if (rateLimited(clientIp(req), { max: 10, windowMs: 60_000 })) {
    res.status(429).json({ error: "rate_limit" });
    return;
  }
  if (req.method !== "POST") { res.status(405).json({ error: "method" }); return; }

  const body = typeof req.body === "string" ? safeJson(req.body) : (req.body || {});
  const email = String(body.email || "").trim().toLowerCase();
  if (!email || email.length > 254 || !EMAIL_RE.test(email)) {
    res.status(400).json({ error: "email_invalido" });
    return;
  }

  const privKey = process.env.LICENSE_PRIVATE_KEY;
  if (!privKey) {
    // Mismo criterio que verify-payment.js: nunca se entrega una licencia
    // rota como si fuera buena. Sin la clave configurada, no hay trial.
    res.status(503).json({ error: "emisor_no_configurado" });
    return;
  }

  const iat = Math.floor(Date.now() / 1000);
  const payload = { plan: "trial", email: email, iat: iat, exp: iat + DIAS_TRIAL * 86400 };

  try {
    const licenseKey = signEd25519(payload, privKey);
    res.status(200).json({
      license_key: licenseKey, plan: "trial", email: email,
      dias: DIAS_TRIAL, vence: payload.exp,
    });
  } catch (e) {
    res.status(500).json({ error: "exception" });
  }
};

function safeJson(s) { try { return JSON.parse(s); } catch (e) { return {}; } }
