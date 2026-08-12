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
// SKU comercial -> plan de licencia.
//
// Son dos cosas distintas y confundirlas costo caro: el SKU es lo que se cobra
// en el checkout ("pro"), el plan es el tier que el programa entiende
// ("professional", ver PLANES en mvdg/licensing.py). Estaban usandose como si
// fueran lo mismo — el plan del SKU se metia crudo en el token — y el
// resultado era que el cliente que pagaba US$390/mes recibia un token con
// plan "pro", que licensing.verify() RECHAZA por plan desconocido. Caia a
// demo. Sin ningun error: pagaba y no recibia nada.
//
// null = ese SKU no otorga licencia. Los packs de creditos son consumo, no un
// tier; firmarles un token con plan "cred100" producia una license_key que el
// programa rechaza, o sea una clave rota entregada como si fuera buena.
//
// Cualquier SKU nuevo del checkout tiene que aparecer aca o los tests fallan.
const PLAN_POR_SKU = {
  licencia: "licencia",
  pro: "professional",
  cred100: null,
  cred550: null,
  cred2500: null,
};

// --------------------------------------------------------------------------
// Cuanto DURA lo que se vendio, en dias. 0 = perpetua (sin `exp` en el token).
//
// Esto existe porque el checkout vendia "pro" como MENSUAL y el token salia
// sin `exp`: licensing.verify() solo rechaza si hay un `exp` vencido, asi que
// el cliente pagaba un mes y se quedaba con Professional para siempre. El
// mecanismo de vencimiento ya funcionaba (api/trial.js lo usa y el trial
// caduca solo) — el camino de pago simplemente lo omitia.
//
// Hoy las dos son PERPETUAS, que es lo unico que esta infraestructura puede
// cumplir: sin base de datos (Vercel es sin estado) y sin reentrega
// automatica, poner exp=31 sin una via de renovacion dejaria afuera al mes
// siguiente a todo el que pago. Un cliente con algo de mas es un problema; un
// cliente que pago y quedo bloqueado es otro mucho peor.
//
// Para pasar "pro" a mensual de verdad hace falta, ademas de cambiar el 0 por
// 31 aca: suscripciones de MercadoPago (preapproval), webhook de cobro
// recurrente, y una forma de hacerle llegar la clave nueva cada mes. Mientras
// eso no exista, la landing tampoco puede anunciarlo como mensual — y hay un
// test que lo verifica.
const DIAS_POR_SKU = {
  licencia: 0,
  pro: 0,
  cred100: 0,
  cred550: 0,
  cred2500: 0,
};

function diasDeSku(sku) {
  if (!sku) return 0;
  return Object.prototype.hasOwnProperty.call(DIAS_POR_SKU, sku)
    ? DIAS_POR_SKU[sku]
    : 0;
}

function planDeSku(sku) {
  if (!sku) return null;
  return Object.prototype.hasOwnProperty.call(PLAN_POR_SKU, sku)
    ? PLAN_POR_SKU[sku]
    : null;
}

module.exports = { sign, verify, signEd25519, PLAN_POR_SKU, planDeSku, DIAS_POR_SKU, diasDeSku };
