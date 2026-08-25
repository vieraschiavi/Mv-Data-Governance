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
    // `code` es el mismo valor que `message`, con nombre de lo que realmente
    // es: todos los que construyen esto pasan un identificador
    // ("sin_conexion", "requiere_licencia"), no un texto para mostrarle a
    // nadie. Sin este campo, `e.code` daba undefined y TODOS los errores
    // caian en el mensaje generico — el que pagaba y no tenia licencia veia
    // "el sistema remoto no respondio" en vez de "esto necesita licencia".
    // Lo encontro una prueba en Chromium contra la API real; compilaba y el
    // endpoint estaba bien, asi que ningun test de unidad lo hubiera visto.
    this.code = mensaje;
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

/* --- Las tres funciones que se cobran -------------------------------------
   Estaban en la API y no habia forma de llamarlas desde el programa: el que
   pagaba veia la lista de funciones desbloqueadas y ningun boton. --- */

export async function conectores() {
  return pedir("/api/conectores");
}

// `aplicar` es lo que separa la vista previa (gratis) del push REAL contra el
// sistema de la empresa (licenciado). Va explicito en cada llamada: un default
// que aplique de verdad seria un push a produccion por olvidarse un parametro.
export async function migrar(destino, aplicar, lang) {
  return enviar(`/api/migracion/${destino}?lang=${encodeURIComponent(lang)}`,
                { aplicar: Boolean(aplicar) });
}

export async function escanearTenant(maxWorkspaces, lang) {
  return enviar(`/api/bi/escanear-tenant?lang=${encodeURIComponent(lang)}`,
                { max_workspaces: maxWorkspaces });
}

// POST comun a los tres. El 402 se distingue del resto porque no es un error
// del programa: es "esto se paga", y la interfaz tiene que mostrarlo como el
// aviso de licencia y no como una falla.
async function enviar(ruta, cuerpo) {
  let r;
  try {
    r = await fetch(`${BASE}${ruta}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  const datos = await r.json().catch(() => ({}));
  if (r.status === 402) throw new ApiError("requiere_licencia", datos.detail);
  if (r.status === 409) throw new ApiError("sin_credenciales", datos.detail);
  if (!r.ok) throw new ApiError("respuesta_invalida", datos.detail || `HTTP ${r.status}`);
  return datos;
}

/* --- Perfilar tus propios datos ------------------------------------------
   La landing lo anuncia como la primera funcion del producto y el .exe no la
   tenia. El archivo NO sale de la maquina: la API escucha en 127.0.0.1, se lee
   en memoria y se descarta. --- */
export async function perfilar(archivo, lang) {
  const cuerpo = new FormData();
  cuerpo.append("archivo", archivo);
  let r;
  try {
    // Sin content-type a mano: el navegador tiene que poner el boundary del
    // multipart. Escribirlo rompe la subida de una forma que solo se ve con
    // un archivo real.
    r = await fetch(`${BASE}/api/perfilar?lang=${encodeURIComponent(lang)}`,
                    { method: "POST", body: cuerpo });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  const datos = await r.json().catch(() => ({}));
  if (r.status === 413) throw new ApiError("archivo_muy_grande", datos.detail);
  if (!r.ok) throw new ApiError("archivo_invalido", datos.detail);
  return datos;
}

/* --- Ingeniería de datos: perfil avanzado + calidad 6D + claves/joins +
   tiempo + fuga (leakage) + features + DDL, sobre archivo o base de datos.
   Gratis, igual que perfilar(): no requiere licencia — "sin cobrarlo aparte"
   fue el pedido.

   El texto de contenido (issues, roles, riesgos de join…) ya viene TRADUCIDO
   desde bi_api (mismo motor de idioma que el resto de la API); acá no se
   arma ninguna oración, solo se transportan los datos. --- */

// `detail` puede ser un string (validaciones simples) o el objeto trilingüe
// {error, es, en, pt} que arma bi_api._de_error — de ahí sale el texto.
function detalleDe(datos) {
  const d = datos && datos.detail;
  if (!d) return "";
  if (typeof d === "string") return d;
  return d.es || d.en || d.pt || d.detalle || JSON.stringify(d);
}

async function enviarJson(ruta, cuerpo) {
  let r;
  try {
    r = await fetch(`${BASE}${ruta}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(cuerpo || {}),
    });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) throw new ApiError("respuesta_invalida", detalleDe(datos));
  return datos;
}

export async function ingenieriaArchivo(archivos, { target = "", columnaTiempo = "", lang = "es" } = {}) {
  const cuerpo = new FormData();
  for (const a of archivos) cuerpo.append("archivos", a);
  const qs = new URLSearchParams({ lang, target, columna_tiempo: columnaTiempo });
  let r;
  try {
    r = await fetch(`${BASE}/api/ingenieria/archivo?${qs}`, { method: "POST", body: cuerpo });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  const datos = await r.json().catch(() => ({}));
  if (r.status === 413) throw new ApiError("archivo_muy_grande", detalleDe(datos));
  if (!r.ok) throw new ApiError("archivo_invalido", detalleDe(datos));
  return datos;
}

export function ingenieriaSqlProbar(perfil) {
  return enviarJson("/api/ingenieria/sql/probar", perfil);
}

export function ingenieriaSqlTablas(perfil) {
  return enviarJson("/api/ingenieria/sql/tablas", perfil);
}

export function ingenieriaSqlAnalizar(cuerpo, lang) {
  return enviarJson(`/api/ingenieria/sql/analizar?lang=${encodeURIComponent(lang)}`, cuerpo);
}

export function ingenieriaSqlGuardarConexion(perfil) {
  return enviarJson("/api/ingenieria/sql/conexiones", perfil);
}

export async function ingenieriaSqlConexiones() {
  return pedir("/api/ingenieria/sql/conexiones");
}

export async function ingenieriaSqlBorrarConexion(connId) {
  let r;
  try {
    r = await fetch(`${BASE}/api/ingenieria/sql/conexiones/${encodeURIComponent(connId)}`,
                    { method: "DELETE" });
  } catch (e) {
    throw new ApiError("sin_conexion", e.message);
  }
  if (!r.ok) throw new ApiError("respuesta_invalida", `HTTP ${r.status}`);
  return r.json();
}
