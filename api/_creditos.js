// Saldo de créditos IA — el libro mayor del proxy.
//
// ────────────────────────────────────────────────────────────────────────────
// Por qué el saldo NO puede vivir en el programa del cliente
// ────────────────────────────────────────────────────────────────────────────
// El resto de la licencia se verifica del lado del cliente y eso se asume
// (mvdg/licensing.py lo declara). Con los créditos no alcanza: acá cada
// crédito gastado le cuesta plata REAL al dueño del producto, porque las
// llamadas al modelo van con SUS API keys. Un saldo guardado en el disco del
// usuario se resetea borrando un archivo, y eso no seria "una licencia
// pirateada" — seria una factura de Anthropic que paga otro.
//
// Por eso el saldo vive en el KV y solo el servidor lo toca.
//
// ────────────────────────────────────────────────────────────────────────────
// Identidad sin cuentas
// ────────────────────────────────────────────────────────────────────────────
// El programa es de escritorio y no tiene usuarios ni contraseñas, y montar
// eso solo para esto seria desproporcionado. En su lugar, al pagar se emite
// una CLAVE DE CRÉDITOS al azar: quien la tiene, gasta ese saldo. Es el mismo
// modelo de confianza que una API key, y el cliente ya entiende ese objeto.
//
// ────────────────────────────────────────────────────────────────────────────
// Consumo atómico, y por qué con Lua
// ────────────────────────────────────────────────────────────────────────────
// "leer saldo, comparar, restar" en tres viajes tiene una carrera obvia: dos
// pedidos simultáneos leen 1 crédito, los dos ven que alcanza, y los dos
// gastan. Con saldo bajo eso regala llamadas; con concurrencia alta, muchas.
// El script de Lua corre entero dentro de Redis, así que compara y resta sin
// que nadie se meta en el medio.
const crypto = require("crypto");

const PREFIJO_CLAVE = "mvdgc_";
const TTL_S = 0;                    // los créditos no vencen (así se anuncia)

// Lo que cuesta cada operación, en créditos. Son los números que la landing
// le promete al cliente: si cambian acá, hay que cambiarlos allá (y hay un
// test que lo exige).
const COSTOS = {
  sugerencia: 1,
  glosario: 2,
};

function config() {
  const url = (process.env.KV_REST_API_URL || "").trim().replace(/\/+$/, "");
  const token = (process.env.KV_REST_API_TOKEN || "").trim();
  return url && token ? { url, token } : null;
}

function nuevaClave() {
  return PREFIJO_CLAVE + crypto.randomBytes(24).toString("base64url");
}

function claveValida(clave) {
  return typeof clave === "string" &&
    /^mvdgc_[A-Za-z0-9_-]{32}$/.test(clave);
}

function _k(clave) { return `mvdg:cred:${clave}`; }

async function _redis(comandos) {
  const cfg = config();
  if (!cfg) return null;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 3_000);
  try {
    const r = await fetch(`${cfg.url}/pipeline`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cfg.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(comandos),
      signal: ctrl.signal,
    });
    if (!r.ok) return null;
    const datos = await r.json();
    return Array.isArray(datos) ? datos : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/** Suma créditos (una compra). Devuelve el saldo nuevo, o null si fallo. */
async function acreditar(clave, cantidad) {
  if (!claveValida(clave) || !Number.isInteger(cantidad) || cantidad <= 0) {
    return null;
  }
  const cmds = [["INCRBY", _k(clave), String(cantidad)]];
  if (TTL_S > 0) cmds.push(["EXPIRE", _k(clave), String(TTL_S)]);
  const r = await _redis(cmds);
  return r && r[0] ? Number(r[0].result) : null;
}

/** Saldo actual. null si no se pudo consultar (NO se asume cero). */
async function saldo(clave) {
  if (!claveValida(clave)) return null;
  const r = await _redis([["GET", _k(clave)]]);
  if (!r || !r[0]) return null;
  const v = r[0].result;
  return v === null || v === undefined ? 0 : Number(v);
}

/**
 * Descuenta de forma ATÓMICA. Devuelve el saldo restante, o -1 si no alcanza,
 * o null si el KV no está disponible.
 *
 * null y -1 son cosas distintas a propósito: "no alcanza" es una respuesta
 * legítima que el cliente tiene que ver; "no se pudo consultar" NO puede
 * tratarse como si alcanzara, o una caída del KV regalaría llamadas pagas.
 */
async function consumir(clave, cantidad) {
  if (!claveValida(clave) || !Number.isInteger(cantidad) || cantidad <= 0) {
    return -1;
  }
  const lua = [
    "local s = tonumber(redis.call('GET', KEYS[1]) or '0')",
    "local c = tonumber(ARGV[1])",
    "if s < c then return -1 end",
    "return redis.call('DECRBY', KEYS[1], c)",
  ].join("\n");
  const r = await _redis([["EVAL", lua, "1", _k(clave), String(cantidad)]]);
  if (!r || !r[0]) return null;
  const v = Number(r[0].result);
  return Number.isFinite(v) ? v : null;
}

/**
 * Devuelve créditos ya descontados. Se usa cuando el modelo falla DESPUÉS de
 * cobrar: el cliente no puede pagar por una respuesta que nunca recibió.
 */
async function devolver(clave, cantidad) {
  return acreditar(clave, cantidad);
}

module.exports = {
  nuevaClave, claveValida, acreditar, saldo, consumir, devolver,
  COSTOS, PREFIJO_CLAVE, configurado: () => config() !== null,
};
