// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Throttle de renovación de suscripción — cierra el hallazgo de la
// auditoría sobre api/suscripcion.js: un preapproval_id filtrado se podía
// canjear por una licencia Professional infinitas veces.
//
// ────────────────────────────────────────────────────────────────────────────
// Por qué esto NO es el mismo problema que _usados.js
// ────────────────────────────────────────────────────────────────────────────
// _usados.js cierra un pago de una sola vez: un payment_id sirve UNA vez y
// listo. suscripcion.js es al revés a propósito — el programa del cliente
// pagante tiene que poder volver a pedir la licencia cada tantos días,
// indefinidamente, mientras la suscripción siga "authorized" en MercadoPago
// (así es como se implementó la renovación mensual, ver el comentario en
// suscripcion.js). Un registro de "una sola vez" rompería exactamente el
// flujo que se necesita.
//
// Lo que hace falta no es bloquear la reutilización, es ACOTARLA: el
// preapproval_id viaja en la URL de retorno del comprador (no es secreto,
// mismo problema documentado para payment_id) y CUALQUIERA que lo obtenga
// puede pedir una licencia propia mientras la suscripción del titular real
// siga paga — sin haber pagado nada él. Poniendo un piso de tiempo entre
// una renovación y la siguiente para el MISMO preapproval_id, un atacante
// queda limitado a, como mucho, una licencia por cooldown — no infinitas —
// sin afectar al cliente real, que solo necesita renovar cada tantos días.
//
// Mismas dos decisiones de _usados.js, por la misma razón:
// 1. SIN CONFIGURAR, NO ROMPE — sin KV, "sin_registro" y se emite igual
//    (el rate limit por IP sigue aplicando).
// 2. SI EL KV FALLA, SE FALLA ABIERTO — un timeout no le corta la
//    renovación a un cliente que pagó.
const TIMEOUT_MS = 2_500;

function config() {
  const url = (process.env.KV_REST_API_URL || "").trim().replace(/\/+$/, "");
  const token = (process.env.KV_REST_API_TOKEN || "").trim();
  return url && token ? { url, token } : null;
}

async function _kvFetch(cfg, comandos) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
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
    return await r.json();
  } catch {
    return null;               // timeout, DNS, KV caído: se degrada
  } finally {
    clearTimeout(timer);
  }
}

/**
 * ¿Se puede emitir una licencia nueva para este preapproval_id ahora mismo?
 *
 * Devuelve:
 *   "permitida"    — primera vez, o ya pasó el cooldown: emitir
 *   "muy_reciente" — se emitió hace menos de `cooldownMs`: NO emitir
 *   "sin_registro" — sin KV configurado, o KV caído: no se bloquea nada
 *
 * Si devuelve "permitida", YA DEJÓ registrado el momento — no hace falta
 * (ni hay que) llamar a nada más después de emitir.
 */
async function permitirRenovacion(subId, cooldownMs) {
  const cfg = config();
  if (!cfg) return "sin_registro";

  const clave = `mvdg:sub:${subId}`;
  const ahora = Date.now();

  const previo = await _kvFetch(cfg, [["GET", clave]]);
  if (!Array.isArray(previo) || !previo.length) return "sin_registro";
  const ts = Number(previo[0] && previo[0].result);
  if (Number.isFinite(ts) && ahora - ts < cooldownMs) return "muy_reciente";

  // Se registra AHORA como último momento de emisión. Una carrera acá (dos
  // pedidos casi simultáneos del mismo id) deja pasar como mucho una
  // renovación de más — no es una falla de seguridad, es el mismo margen
  // que _usados.js acepta para el F5 del comprador.
  const ttlS = Math.max(60, Math.ceil((cooldownMs / 1000) * 3));
  await _kvFetch(cfg, [["SET", clave, String(ahora), "EX", String(ttlS)]]);
  return "permitida";
}

module.exports = { permitirRenovacion };
