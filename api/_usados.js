// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Registro de pagos ya usados para emitir licencia — el cierre del agujero
// que la ventana de tiempo solo achicaba.
//
// ────────────────────────────────────────────────────────────────────────────
// Que problema cierra
// ────────────────────────────────────────────────────────────────────────────
// verify-payment no puede atar quien llama con quien pago: el payment_id
// viaja en la URL de retorno de MercadoPago, o sea que esta en el historial
// del comprador y en cualquier captura que comparta. La ventana de 30 minutos
// bajo el riesgo de "para siempre" a "media hora", pero adentro de esa media
// hora el id seguia sirviendo infinitas veces.
//
// Con un registro de ids ya emitidos, cada pago emite UNA vez. Eso necesita
// estado, y Vercel es sin estado — de ahi que hasta ahora no existiera.
//
// ────────────────────────────────────────────────────────────────────────────
// Por que Redis por REST y no una libreria
// ────────────────────────────────────────────────────────────────────────────
// El repo tiene CERO dependencias npm, a proposito. La API REST de Upstash
// (la que provisiona Vercel KV) se habla con `fetch` y nada mas, asi que el
// registro no cuesta ni una dependencia. Si algun dia se cambia de proveedor,
// lo unico que se toca es este archivo.
//
// ────────────────────────────────────────────────────────────────────────────
// Las dos decisiones que importan
// ────────────────────────────────────────────────────────────────────────────
// 1. SIN CONFIGURAR, NO ROMPE. Si no estan las variables de entorno, devuelve
//    "sin_registro" y verify-payment sigue con la ventana de tiempo sola —
//    exactamente el comportamiento de antes. Asi esto se puede mergear hoy y
//    activarse el dia que se provisione el KV, sin un despliegue roto en el
//    medio.
//
// 2. SI EL KV FALLA, SE FALLA ABIERTO. Un timeout o un 500 devuelven
//    "sin_registro", no "repetido". Es la unica decision defendible: fallar
//    cerrado significaria que una caida de Upstash le impide comprar a TODOS
//    los clientes. Y no se queda desprotegido — la ventana de 30 minutos
//    sigue aplicando. Se degrada a lo de antes, no a nada.
//
// 3. EL F5 DEL COMPRADOR TIENE QUE ANDAR. Si el registro fuera de un solo uso
//    estricto, recargar /pago.html dejaria al que pago sin ver su licencia, y
//    eso es un ticket de soporte garantizado. Por eso se guarda CUANDO se uso
//    por primera vez y se permite reemitir durante unos minutos: es el mismo
//    comprador con la misma pestana. Pasada esa gracia, ese id no sirve mas,
//    ni dentro ni fuera de la ventana.
const GRACIA_MS = 15 * 60_000;      // recargas del comprador
const TTL_S = 400 * 24 * 3600;      // el registro no crece para siempre
const TIMEOUT_MS = 2_500;           // el pago no puede quedarse esperando al KV

function config() {
  const url = (process.env.KV_REST_API_URL || "").trim().replace(/\/+$/, "");
  const token = (process.env.KV_REST_API_TOKEN || "").trim();
  return url && token ? { url, token } : null;
}

/**
 * Marca un pago como usado.
 *
 * Devuelve:
 *   "nuevo"        — primera vez: se puede emitir la licencia
 *   "repetido"     — ya se emitio hace rato: NO emitir
 *   "recarga"      — ya se emitio recien: es el comprador recargando, emitir
 *   "sin_registro" — no hay KV configurado, o fallo: decide la ventana sola
 */
async function registrar(paymentId) {
  const cfg = config();
  if (!cfg) return "sin_registro";

  const clave = `mvdg:pago:${paymentId}`;
  const ahora = Date.now();

  // Una sola ida y vuelta: SET NX (marca si no estaba) y GET (trae el valor
  // que quedo, sea el nuevo o el que ya habia). Hacerlo en dos requests
  // abriria una carrera entre dos pedidos simultaneos del mismo id.
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  let datos;
  try {
    const r = await fetch(`${cfg.url}/pipeline`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cfg.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify([
        ["SET", clave, String(ahora), "NX", "EX", String(TTL_S)],
        ["GET", clave],
      ]),
      signal: ctrl.signal,
    });
    if (!r.ok) return "sin_registro";
    datos = await r.json();
  } catch {
    return "sin_registro";        // timeout, DNS, KV caido: se degrada
  } finally {
    clearTimeout(timer);
  }

  if (!Array.isArray(datos) || datos.length < 2) return "sin_registro";
  const seteo = datos[0] && datos[0].result;
  if (seteo === "OK") return "nuevo";

  // Ya existia. Si se uso hace muy poco es el mismo comprador recargando.
  const previo = Number(datos[1] && datos[1].result);
  if (Number.isFinite(previo) && ahora - previo <= GRACIA_MS) return "recarga";
  return "repetido";
}

module.exports = { registrar, GRACIA_MS, TTL_S };
