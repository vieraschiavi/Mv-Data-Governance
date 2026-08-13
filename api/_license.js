// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Firma y verificación de licencias MV Data Governance (HMAC-SHA256, sin
// dependencias externas). Prefijo "_" para que Vercel NO la trate como
// endpoint — es un módulo interno, no una función pública.

const crypto = require("crypto");

function b64u(buf) {
  return Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64uJson(obj) { return b64u(JSON.stringify(obj)); }

function sign(payload, secret) {
  const body = b64uJson(payload);
  const sig = b64u(crypto.createHmac("sha256", secret).update(body).digest());
  return "MVDG1." + body + "." + sig;
}

function verify(license, secret) {
  if (typeof license !== "string") return null;
  const parts = license.split(".");
  if (parts.length !== 3 || parts[0] !== "MVDG1") return null;
  const body = parts[1], sig = parts[2];
  const expected = b64u(crypto.createHmac("sha256", secret).update(body).digest());
  const a = Buffer.from(sig), b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const json = Buffer.from(body.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8");
    return JSON.parse(json);
  } catch (e) { return null; }
}

// --------------------------------------------------------------------------
// Formato MVDG2 — firma Ed25519 (clave publica/privada).
//
// El MVDG1 de arriba (HMAC) sigue sirviendo entre funciones del backend, donde
// los dos extremos son de confianza. Pero NO sirve para que el programa de
// escritorio valide una licencia: verificar un HMAC exige el mismo secreto que
// lo firma, asi que habria que embeber LICENSE_SECRET en el .exe que se
// distribuye — y cualquiera que lo extraiga puede emitir licencias infinitas,
// ademas de quedarse con el secreto del backend de pagos.
//
// Con Ed25519 el backend firma con la privada (LICENSE_PRIVATE_KEY, que nunca
// sale del servidor) y el programa verifica con la publica embebida, que es
// inofensiva aunque se lea del binario. Node trae Ed25519 nativo: sin deps.
// El par se genera con packaging/licencias.py keygen.
// --------------------------------------------------------------------------

function ed25519PrivateKey(rawB64u) {
  // La clave viaja como los 32 bytes crudos en base64url; Node necesita un
  // KeyObject, y la via sin dependencias es envolverla en el DER de PKCS#8.
  const raw = Buffer.from(rawB64u.replace(/-/g, "+").replace(/_/g, "/"), "base64");
  if (raw.length !== 32) throw new Error("LICENSE_PRIVATE_KEY debe ser Ed25519 de 32 bytes");
  const der = Buffer.concat([
    Buffer.from("302e020100300506032b657004220420", "hex"),
    raw,
  ]);
  return crypto.createPrivateKey({ key: der, format: "der", type: "pkcs8" });
}

function signEd25519(payload, privateKeyB64u) {
  const body = b64uJson(payload);
  const sig = crypto.sign(null, Buffer.from(body, "ascii"),
                          ed25519PrivateKey(privateKeyB64u));
  return "MVDG2." + body + "." + b64u(sig);
}

// --------------------------------------------------------------------------
// QUE SE VENDE: por cada SKU del checkout, que licencia otorga y por cuanto.
//
// `plan` — el SKU y el plan son cosas distintas, y confundirlos costo caro. El
//   SKU es lo que se cobra ("pro"); el plan es el tier que el programa
//   entiende ("professional", ver PLANES en mvdg/licensing.py). Se metia el
//   SKU crudo en el token, licensing.verify() lo rechazaba por plan
//   desconocido, y el que pagaba US$390/mes caia a demo sin ningun error.
//   `null` = ese SKU no otorga licencia. Los packs de creditos son consumo, no
//   un tier: firmarles un token con plan "cred100" daba una license_key que el
//   programa rechaza — una clave rota entregada como si fuera buena.
//
// `dias` — cuanto dura. 0 = perpetua, o sea sin `exp` en el token. Se vendia
//   "pro" como MENSUAL y el token salia sin `exp`; como verify() solo rechaza
//   cuando `exp` existe y ya paso, el cliente pagaba un mes y se quedaba con
//   Professional para siempre. El mecanismo ya andaba (api/trial.js emite exp
//   a 14 dias y el trial caduca solo): era el camino de pago el que lo omitia.
//
//   Hoy las dos son perpetuas, que es lo unico que esta infraestructura puede
//   cumplir: sin base de datos (Vercel es sin estado) ni reentrega automatica,
//   poner 31 dias sin via de renovacion dejaria afuera al mes siguiente a todo
//   el que pago. Para pasar "pro" a mensual de verdad hacen falta ademas
//   suscripciones de MercadoPago (preapproval), webhook de cobro recurrente y
//   entrega de la clave nueva cada mes; hasta entonces la landing tampoco
//   puede anunciarlo por mes, y hay un test que lo verifica.
//
// UNA tabla y no un mapa por atributo: con dos mapas separados se podia
// registrar MEDIO SKU — declararle el plan y olvidar el plazo — y como el
// plazo ausente vale 0, ese SKU salia perpetuo sin que nada lo notara.
// Verificado: pasaba los tests de Python Y los de Node. Es el mismo bug que
// este archivo vino a arreglar, un nivel mas arriba. Con una sola entrada, la
// estructura lo impide y no hay que acordarse de escribir el test.
// --------------------------------------------------------------------------
const SKU = {
  licencia: { plan: "licencia", dias: 0 },
  pro: { plan: "professional", dias: 0 },
};

// Derivados, para quien solo necesita una de las dos caras.
const PLAN_POR_SKU = Object.fromEntries(
  Object.entries(SKU).map(([k, v]) => [k, v.plan]));

const DIAS_POR_SKU = Object.fromEntries(
  Object.entries(SKU).map(([k, v]) => [k, v.dias]));

// Un SKU que no esta en la tabla no recibe licencia (plan null), asi que el
// plazo no llega a usarse: no hay token que pueda salir perpetuo por omision.
function diasDeSku(sku) {
  const e = sku && Object.prototype.hasOwnProperty.call(SKU, sku) ? SKU[sku] : null;
  return e ? e.dias : 0;
}

function planDeSku(sku) {
  const e = sku && Object.prototype.hasOwnProperty.call(SKU, sku) ? SKU[sku] : null;
  return e ? e.plan : null;
}

module.exports = { sign, verify, signEd25519, SKU, PLAN_POR_SKU, planDeSku,
                   DIAS_POR_SKU, diasDeSku };
