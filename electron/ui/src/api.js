// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Cliente de la API de gobierno (bi_api/main.py).
 *
 * La UI se sirve DESDE el mismo servidor (FastAPI la monta en /app), así que
 * las llamadas son de mismo origen: sin CORS, sin file://, sin puerto
 * hardcodeado. Si algún día la UI se abriera desde otro lado, MVDG_API_BASE
 * permite apuntarla a mano — pero el camino normal no necesita configurar
 * nada, que es justamente lo que hace que el .exe "ande y ya".
 */

// Mismo origen por defecto. `location.origin` da http://127.0.0.1:<puerto>
// real, sea cual sea el puerto libre que eligió el lanzador.
const BASE = (typeof window !== "undefined" && window.MVDG_API_BASE) || "";

export class ApiError extends Error {
  constructor(mensaje, detalle) {
    super(mensaje);
    this.detalle = detalle || "";
  }
}

async function pedir(ruta) {
  let r;
  try {
    r = await fetch(`${BASE}${ruta}`);
  } catch (e) {
    // fetch solo rechaza por red: el servidor todavía no levantó, o murió.
    throw new ApiError("sin_conexion", `${ruta} · ${e.message}`);
  }
  if (!r.ok) {
    let detalle = `HTTP ${r.status}`;
    try {
      const cuerpo = await r.json();
      if (cuerpo && cuerpo.detail) detalle += ` · ${cuerpo.detail}`;
    } catch {
      /* el cuerpo puede no ser JSON; el status ya dice bastante */
    }
    throw new ApiError("respuesta_invalida", `${ruta} · ${detalle}`);
  }
  return r.json();
}

/** Índice del servidor: versión, idiomas y tablas disponibles. */
export function meta() {
  return pedir("/");
}

/** Una tabla de gobierno, ya traducida por el motor. */
export async function tabla(nombre, lang) {
  const r = await pedir(`/api/${encodeURIComponent(nombre)}?lang=${lang}`);
  return Array.isArray(r.data) ? r.data : [];
}

/**
 * Todas las tablas que la interfaz necesita, en paralelo.
 *
 * En paralelo y no en serie porque son 6 llamadas y el motor recalcula
 * calidad en cada una: en serie, el primer render tardaba lo que tardan
 * todas sumadas.
 */
export async function todo(lang) {
  const nombres = ["kpis", "catalog", "dictionary", "quality_results",
                   "quality_by_dimension", "quality_by_dataset",
                   "lineage", "glossary", "policies"];
  const partes = await Promise.all(nombres.map((n) => tabla(n, lang)));
  return Object.fromEntries(nombres.map((n, i) => [n, partes[i]]));
}

/* ------------------------------------------------------------- licencia
 * El .exe no tenia forma de activar una compra: sus vistas son todas
 * gratuitas y no habia donde pegar la clave, asi que demo, paga y owner se
 * veian igual. Estas tres llamadas cierran eso contra /api/licencia.
 */
export async function licencia() {
  return pedir("/api/licencia");
}

export async function activarLicencia(token) {
  let r;
  try {
    r = await fetch(`${BASE}/api/licencia`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ token }),
    });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  const cuerpo = await r.json().catch(() => ({}));
  if (!r.ok) {
    // El detalle lo escribe la API y ya viene explicado; se pasa tal cual
    // para no inventar un mensaje distinto del que dice el motor.
    throw new ApiError("clave_invalida", cuerpo.detail || `HTTP ${r.status}`);
  }
  return cuerpo;
}

export async function desactivarLicencia() {
  let r;
  try {
    r = await fetch(`${BASE}/api/licencia`, { method: "DELETE" });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  if (!r.ok) throw new ApiError("respuesta_invalida", `HTTP ${r.status}`);
  return r.json();
}
export async function renovarLicencia() {
  let r;
  try {
    r = await fetch(`${BASE}/api/licencia/renovar`, { method: "POST" });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  const cuerpo = await r.json().catch(() => ({}));
  if (!r.ok) throw new ApiError("respuesta_invalida", `HTTP ${r.status}`);
  return cuerpo;
}
