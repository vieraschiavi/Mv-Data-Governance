// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
//
// ────────────────────────────────────────────────────────────────────────────
// Avisar por mail, sin que el aviso pueda romper lo que estaba pasando
// ────────────────────────────────────────────────────────────────────────────
// Lo usan dos cosas distintas:
//
//   · api/acceso.js    — alguien pidió acceso a la demo
//   · api/checkout.js  — alguien APRETÓ COMPRAR
//
// El segundo es el que importa para decidir cuándo pagar hosting: te dice el
// momento exacto en que hubo intención de compra, en vez de tener que
// suponerlo. Ojo con lo que NO significa: apretar Comprar no es haber pagado.
// El pago se confirma en /api/verify-payment y ahí es donde el dinero existe.
//
// ────────────────────────────────────────────────────────────────────────────
// LA REGLA DE ORO DE ESTE ARCHIVO
// ────────────────────────────────────────────────────────────────────────────
// UN AVISO QUE FALLA NUNCA PUEDE ROMPER LA COMPRA.
//
// Si Resend está caído, o la clave venció, o la red del borde tiene un mal
// minuto, el comprador TIENE que seguir yendo a MercadoPago igual. Perder un
// mail es una molestia; perder una venta por un mail es absurdo.
//
// Por eso `avisar()` no lanza NUNCA: devuelve true/false y quien lo llama
// puede ignorar el resultado sin envolver nada en try/catch.
//
// Y se espera (await) en vez de dejar la promesa suelta: en serverless, la
// función se congela apenas responde, así que una promesa sin await queda a
// medio camino y el mail no sale. Cuesta ~200 ms sobre el clic de Comprar y
// es la diferencia entre un aviso que llega y uno que llega a veces.

const DESTINO = (process.env.MVDG_MAIL_TO || "vieraschiavi@gmail.com").trim();
const REMITENTE = (process.env.MVDG_MAIL_FROM || "onboarding@resend.dev").trim();

// Si Resend tarda más que esto, no vale la pena seguir esperando: el
// comprador está mirando un botón que dice "…" mientras tanto.
const TIMEOUT_MS = 4000;

/**
 * Manda un aviso. NUNCA lanza.
 *
 * @returns {Promise<boolean>} true si Resend lo aceptó.
 */
async function avisar(asunto, cuerpo, opciones = {}) {
  const apiKey = (process.env.RESEND_API_KEY || "").trim();
  if (!apiKey) return false;

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const payload = {
      from: REMITENTE,
      to: [DESTINO],
      subject: String(asunto).slice(0, 200),
      // Texto plano SIEMPRE: parte de esto lo escribió un desconocido
      // (el email que puso en el formulario). En texto plano no hay nada que
      // escapar ni nada que el cliente de correo vaya a renderizar.
      text: String(cuerpo).slice(0, 20_000),
    };
    if (opciones.responderA) payload.reply_to = opciones.responderA;

    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer " + apiKey,
                 "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    });
    return r.ok;
  } catch (e) {
    // Se traga TODO a propósito: ver la regla de oro de arriba.
    return false;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Aviso de "alguien apretó Comprar".
 *
 * Se arma acá y no en checkout.js para que el texto sea uno solo: el día que
 * haya que agregarle un dato, se agrega en un lugar.
 */
async function avisarIntentoDeCompra({ plan, titulo, precio, moneda,
                                       email, suscripcion, host }) {
  const cuando = new Date().toISOString().replace("T", " ").slice(0, 16);
  const cuerpo = [
    "Alguien acaba de apretar COMPRAR en MV Data Governance.",
    "",
    `Plan:    ${titulo || plan}`,
    `Precio:  ${precio} ${moneda}${suscripcion ? " POR MES (suscripcion)" : " (pago unico)"}`,
    `Email:   ${email || "(no lo pide este plan)"}`,
    `Sitio:   ${host || "-"}`,
    `Cuando:  ${cuando} UTC`,
    "",
    "───",
    "OJO: esto es INTENCION de compra, no una venta.",
    "Todavia tiene que pagar en MercadoPago. La venta confirmada te llega",
    "cuando el pago se aprueba y se emite la licencia.",
  ].join("\n");
  return avisar(
    `Clic en Comprar — ${titulo || plan} (${precio} ${moneda})`,
    cuerpo,
    { responderA: email || undefined });
}

module.exports = { avisar, avisarIntentoDeCompra, DESTINO, REMITENTE };
