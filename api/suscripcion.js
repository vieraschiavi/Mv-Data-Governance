// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
//
// ────────────────────────────────────────────────────────────────────────────
// La licencia de una SUSCRIPCIÓN, mientras la suscripción esté paga
// ────────────────────────────────────────────────────────────────────────────
// El problema que cierra: "Professional" se vendía como US$390 POR MES y el
// token salía sin vencimiento. El cliente pagaba un mes y se quedaba con el
// plan para siempre. No era un bug de código — era plata que no entraba.
//
// La solución obvia (ponerle 31 días de vencimiento) rompía a los clientes que
// SÍ pagan: al mes 2 se quedaban afuera, porque no había forma de renovar. Por
// eso la versión anterior las dejó perpetuas a propósito. Arreglar el cobro sin
// arreglar la renovación es cambiar un problema por uno peor.
//
// Acá está la renovación. Y no necesita base de datos:
//
//   MERCADOPAGO YA SABE SI LA SUSCRIPCIÓN ESTÁ PAGA.
//
// Cada licencia de suscripción lleva adentro su propio `sub` (el id del
// preapproval). El programa lee ese id de su PROPIA licencia, pregunta acá, y
// si MercadoPago dice "authorized" recibe una licencia nueva por 35 días más.
// Si el cliente da de baja, MP deja de decir authorized, no hay licencia
// nueva, y a los 35 días el programa vuelve solo a demo.
//
// 35 y no 31: si el cobro de MP se atrasa un par de días — cosa que pasa — un
// vencimiento de 31 dejaría al cliente afuera por culpa de la pasarela. Cuatro
// días de colchón cuestan nada y evitan un ticket de soporte por cada atraso.
//
// Este endpoint es de solo lectura contra MP y no cobra nada. Se puede llamar
// las veces que sea: siempre contesta lo mismo mientras el estado no cambie.

const { signEd25519, diasDeSku, planDeSku } = require("./_license");
const { rateLimited, clientIp } = require("./_rate_limit");

// El programa consulta al abrir, así que el límite tiene que tolerar varias
// aperturas seguidas sin habilitar un barrido de ids ajenos.
const LIMITE = { max: 20, windowMs: 60_000 };

// El plazo y el plan salen de la tabla SKU, no de constantes propias: si acá
// dijera 35 y allá 31, la licencia venceria antes de que el programa pidiera
// la siguiente y el cliente quedaría afuera unos días todos los meses.
const SKU = "pro";
const DIAS = diasDeSku(SKU);
const PLAN = planDeSku(SKU);

module.exports = async (req, res) => {
  if (rateLimited(clientIp(req), LIMITE)) {
    res.status(429).json({ activa: false, error: "rate_limit" });
    return;
  }

  const id = String((req.query && req.query.id) || "").trim();
  // Los ids de preapproval son alfanuméricos. Filtrar acá evita que un id
  // raro se convierta en una URL torcida contra la API de MercadoPago.
  if (!id || !/^[A-Za-z0-9]{8,64}$/.test(id)) {
    res.status(400).json({ activa: false, error: "id_invalido" });
    return;
  }

  const token = process.env.MP_ACCESS_TOKEN;
  if (!token) {
    res.status(500).json({ activa: false, error: "no_token" });
    return;
  }

  let datos;
  try {
    const r = await fetch("https://api.mercadopago.com/preapproval/" + id, {
      headers: { Authorization: "Bearer " + token },
    });
    if (r.status === 404) {
      res.status(404).json({ activa: false, motivo: "no_existe" });
      return;
    }
    if (!r.ok) {
      res.status(502).json({ activa: false, error: "mp_error" });
      return;
    }
    datos = await r.json();
  } catch (e) {
    res.status(502).json({ activa: false, error: "mp_inaccesible" });
    return;
  }

  // "authorized" = está al día. Cualquier otro estado (pending, paused,
  // cancelled) no renueva. Se responde 200 igual: que la suscripción esté
  // dada de baja no es un error del programa, es una respuesta.
  if (datos.status !== "authorized") {
    res.status(200).json({ activa: false, estado: datos.status || null,
                           motivo: "no_autorizada" });
    return;
  }

  const privKey = process.env.LICENSE_PRIVATE_KEY;
  if (!privKey) {
    res.status(200).json({ activa: true, estado: datos.status,
                           license_key: null, motivo: "emisor_no_configurado" });
    return;
  }

  const iat = Math.floor(Date.now() / 1000);
  const payload = {
    plan: PLAN,
    email: datos.payer_email || null,
    // `sub` es lo que hace posible la renovación automática: el programa lo
    // lee de su propia licencia y vuelve a preguntar acá cuando se acerca el
    // vencimiento. Sin esto haría falta que el cliente guarde el id a mano.
    sub: id,
    iat: iat,
    exp: iat + DIAS * 86400,
  };

  let license = null;
  try {
    license = signEd25519(payload, privKey);
  } catch (e) {
    res.status(200).json({ activa: true, estado: datos.status,
                           license_key: null, motivo: "error_de_firma" });
    return;
  }

  res.status(200).json({
    activa: true,
    estado: datos.status,
    plan: PLAN,
    dias: DIAS,
    license_key: license,
  });
};

module.exports.DIAS = DIAS;
