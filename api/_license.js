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

// La clave PUBLICA. Es la misma que lleva embebida el programa
// (mvdg/licensing.py PUBLIC_KEY_B64) y es inofensiva: solo sirve para
// verificar firmas, nunca para hacerlas. Va acá y no en una variable de
// entorno porque una publica que se puede "olvidar de configurar" es un
// chequeo que se apaga solo — y este chequeo es el que decide quien baja el
// programa. LICENSE_PUBLIC_KEY la pisa, para poder rotar el par sin deploy.
const PUBLIC_KEY_B64 = "P00Ez9Ow4kUDYsyMAMvs-3kiJ9pJAlD0LNoW2VGsN28";

function clavePublica() {
  const b = (process.env.LICENSE_PUBLIC_KEY || PUBLIC_KEY_B64).trim();
  const raw = Buffer.from(b.replace(/-/g, "+").replace(/_/g, "/"), "base64");
  if (raw.length !== 32) throw new Error("clave publica Ed25519 invalida");
  return crypto.createPublicKey({
    key: Buffer.concat([Buffer.from("302a300506032b6570032100", "hex"), raw]),
    format: "der", type: "spki",
  });
}

// Devuelve el payload si la licencia es autentica y no vencio; null si no.
// Es el mismo criterio que mvdg/licensing.verify() del lado Python: firma
// valida, formato MVDG2, y `exp` en el futuro si existe. NO mira la maquina —
// del lado del servidor no hay forma de saber en que PC se va a instalar.
//
// Nunca tira: cualquier basura que llegue por la URL termina en null. Un
// throw acá seria un 500 en la cara de alguien que pego mal una clave.
function verifyEd25519(licencia, ahoraSeg) {
  if (typeof licencia !== "string") return null;
  const partes = licencia.split(".");
  if (partes.length !== 3 || partes[0] !== "MVDG2") return null;
  let payload;
  try {
    const sig = Buffer.from(partes[2].replace(/-/g, "+").replace(/_/g, "/"), "base64");
    if (!crypto.verify(null, Buffer.from(partes[1], "ascii"), clavePublica(), sig)) {
      return null;
    }
    payload = JSON.parse(Buffer.from(
      partes[1].replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8"));
  } catch (e) { return null; }
  if (!payload || typeof payload !== "object") return null;
  const ahora = Number.isFinite(ahoraSeg) ? ahoraSeg : Math.floor(Date.now() / 1000);
  if (typeof payload.exp === "number" && payload.exp <= ahora) return null;
  return payload;
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
//   Professional para siempre. El mecanismo ya andaba (las licencias de
//   prueba llevan exp a 14 dias y caducan solas): era el camino de pago el
//   que lo omitia.
//
// `recurrente` — si MercadoPago lo cobra TODOS LOS MESES (preapproval) o una
//   sola vez (preferencia de checkout). Esto es lo que faltaba y por lo que la
//   version anterior dejo "pro" perpetuo a proposito: ponerle vencimiento sin
//   una via de renovacion es peor que dejarlo perpetuo, porque al mes 2 se
//   queda afuera el que SI paga. Con el preapproval hecho (api/checkout.js) y
//   la renovacion contra MercadoPago (api/suscripcion.js), "pro" ya puede
//   vencer: cada 35 dias el programa pide una licencia nueva y la recibe
//   mientras la suscripcion siga paga.
//
//   35 y no 31: si el cobro de MP se atrasa un par de dias, un vencimiento de
//   31 dejaria al cliente afuera por culpa de la pasarela.
//
// Esta tabla es la UNICA fuente de las tres cosas. checkout.js decide si crea
// una suscripcion o una preferencia leyendo `recurrente` de aca — antes tenia
// su propia bandera adentro de PLANS, o sea el mismo hecho escrito dos veces,
// que es como empezo este bug: la condicion de venta vivia en el HTML y el
// vencimiento en el JS, sin nada que los atara.
//
// UNA tabla y no un mapa por atributo: con dos mapas separados se podia
// registrar MEDIO SKU — declararle el plan y olvidar el plazo — y como el
// plazo ausente vale 0, ese SKU salia perpetuo sin que nada lo notara.
// Verificado: pasaba los tests de Python Y los de Node. Es el mismo bug que
// este archivo vino a arreglar, un nivel mas arriba. Con una sola entrada, la
// estructura lo impide y no hay que acordarse de escribir el test.
// --------------------------------------------------------------------------
const SKU = {
  licencia: { plan: "licencia", dias: 0, recurrente: false },
  pro: { plan: "professional", dias: 35, recurrente: true },
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

// Un SKU desconocido NO es recurrente: en la duda se cobra una sola vez, que
// es el error barato. Al reves (cobrarle todos los meses a alguien que compro
// una vez) es un cargo indebido.
function esRecurrente(sku) {
  const e = sku && Object.prototype.hasOwnProperty.call(SKU, sku) ? SKU[sku] : null;
  return Boolean(e && e.recurrente);
}

module.exports = { sign, verify, signEd25519, verifyEd25519, PUBLIC_KEY_B64,
                   SKU, PLAN_POR_SKU, planDeSku,
                   DIAS_POR_SKU, diasDeSku, esRecurrente };
