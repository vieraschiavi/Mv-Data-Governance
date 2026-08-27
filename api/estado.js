// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
//
// ────────────────────────────────────────────────────────────────────────────
// Diagnóstico de configuración: qué falta para cobrar y entregar
// ────────────────────────────────────────────────────────────────────────────
// El problema que cierra: hasta acá, saber si producción estaba bien
// configurada era adivinar. Las variables se cargan en Vercel, no en el
// repo, así que el código no puede "traerlas" — y si falta una, el síntoma
// aparece recién cuando un cliente real aprieta Comprar y algo no sale. Ese
// es el peor momento posible para enterarse.
//
// Esto lo convierte en una URL: /api/estado dice, sin ambigüedad, qué está
// puesto, qué falta, y QUÉ SE ROMPE por cada cosa que falta.
//
// ────────────────────────────────────────────────────────────────────────────
// NUNCA devuelve un valor, ni enmascarado
// ────────────────────────────────────────────────────────────────────────────
// Solo booleanos. Nada de primeros/últimos caracteres, nada de longitudes:
// un prefijo de un Access Token o de la clave que firma las licencias reduce
// el espacio de búsqueda de quien quiera adivinarla, y no ayuda en nada a
// diagnosticar. "Está" o "no está" es toda la información que hace falta.
//
// ────────────────────────────────────────────────────────────────────────────
// Se puede cerrar con llave
// ────────────────────────────────────────────────────────────────────────────
// Saber qué NO está configurado le dice algo a un atacante (por ejemplo, que
// el registro de pagos usados está apagado). Por eso: si existe la variable
// MVDG_ESTADO_TOKEN, este endpoint la EXIGE (?t=...). Si no existe, contesta
// igual — porque el momento en que más se necesita este diagnóstico es antes
// de haber configurado nada, y ahí no hay todavía nada que proteger. La
// respuesta avisa cuál de los dos casos es.

const { rateLimited, clientIp } = require("./_rate_limit");

// Cada fila: qué variable, qué pasa si falta, y si es imprescindible para
// que el circuito comercial (cobrar -> emitir licencia -> descargar) exista.
// `critica: true` es lo que se cuenta para decir "listo para vender".
const VARIABLES = [
  // --- cobro ---
  { env: "MP_ACCESS_TOKEN", grupo: "cobro", critica: true,
    rompe: "No se puede cobrar de verdad: el checkout cae al link fijo de respaldo (MP_LINK_*) o responde 503. Nunca muestra un checkout falso." },
  { env: "MP_CURRENCY", grupo: "cobro", critica: false,
    rompe: "Sin efecto: usa USD, que es lo que muestran los precios de la landing." },

  // --- licencias ---
  { env: "LICENSE_PRIVATE_KEY", grupo: "licencias", critica: true,
    rompe: "El cliente paga y NO recibe licencia utilizable. Falla cerrado (nunca entrega una rota), pero la venta queda a medias hasta que la emitas a mano." },
  { env: "LICENSE_SECRET", grupo: "licencias", critica: false,
    rompe: "No se emite la licencia MVDG1 (HMAC, formato viejo). La MVDG2 —la que el programa valida— sale igual." },
  { env: "LICENSE_PUBLIC_KEY", grupo: "licencias", critica: false,
    rompe: "Sin efecto: usa la clave pública embebida en mvdg/licensing.py, que es la misma que lleva el programa instalado." },

  // --- idempotencia ---
  { env: "KV_REST_API_URL", grupo: "idempotencia", critica: false,
    rompe: "No se registran los pagos ya usados: dentro de la ventana de 30 min un payment_id filtrado puede reusarse. Se degrada, no se rompe." },
  { env: "KV_REST_API_TOKEN", grupo: "idempotencia", critica: false,
    rompe: "Ídem KV_REST_API_URL: las dos van juntas o el registro queda apagado." },

  // --- entrega ---
  { env: "MVDG_INSTALLER_URL", grupo: "entrega", critica: true,
    rompe: "Nadie puede bajar el instalador: /api/descargar responde 503 diciendo qué falta, en vez de servir algo viejo." },
  { env: "MVDG_INSTALLER_URL_OWNER", grupo: "entrega", critica: false,
    rompe: "No se puede bajar el instalador de la edición owner (la tuya). No afecta a los clientes." },
  { env: "MVDG_SITE_HOST", grupo: "entrega", critica: false,
    rompe: "Sin efecto mientras uses el dominio de Vercel: el comprador vuelve al dominio canónico. Se define al poner dominio propio." },

  // --- mails ---
  { env: "RESEND_API_KEY", grupo: "mails", critica: true,
    rompe: "No llegan los pedidos de demo (el formulario responde 503 y muestra el mailto de respaldo) ni los avisos de 'alguien apretó Comprar'. La compra en sí sigue funcionando." },
  { env: "MVDG_MAIL_TO", grupo: "mails", critica: false,
    rompe: "Sin efecto: usa la casilla por defecto del proyecto." },
  { env: "MVDG_MAIL_FROM", grupo: "mails", critica: false,
    rompe: "Usa onboarding@resend.dev, que solo puede escribirle a la casilla dueña de la cuenta de Resend: no podés acusarle recibo al que pidió la demo." },
];

const GRUPOS = {
  cobro: "Cobro (MercadoPago)",
  licencias: "Emisión de licencias",
  idempotencia: "Registro de pagos usados",
  entrega: "Descarga del instalador",
  mails: "Mails (demos y avisos)",
};

function puesta(env) {
  return Boolean(String(process.env[env] || "").trim());
}

module.exports = (req, res) => {
  if (rateLimited(clientIp(req), { max: 30, windowMs: 60_000 })) {
    res.status(429).json({ error: "rate_limit" });
    return;
  }
  if (req.method !== "GET") { res.status(405).json({ error: "method" }); return; }

  // Candado opcional — ver el encabezado del archivo.
  const llave = String(process.env.MVDG_ESTADO_TOKEN || "").trim();
  if (llave) {
    const enviada = String((req.query && req.query.t) || "").trim();
    // Comparación de largo fijo: no filtra la llave carácter a carácter.
    const crypto = require("crypto");
    const a = crypto.createHash("sha256").update(enviada).digest();
    const b = crypto.createHash("sha256").update(llave).digest();
    if (!crypto.timingSafeEqual(a, b)) {
      res.status(401).json({ error: "no_autorizado",
        detalle: "Este diagnóstico está protegido. Pasá ?t=<MVDG_ESTADO_TOKEN>." });
      return;
    }
  }

  const filas = VARIABLES.map((v) => ({
    variable: v.env,
    grupo: GRUPOS[v.grupo] || v.grupo,
    critica: v.critica,
    configurada: puesta(v.env),
    // El "qué se rompe" solo tiene sentido cuando falta. Devolverlo siempre
    // haría ruido en el caso bueno, que es el que se mira más seguido.
    rompe: puesta(v.env) ? undefined : v.rompe,
  }));

  const faltanCriticas = filas.filter((f) => f.critica && !f.configurada);
  const faltanOpcionales = filas.filter((f) => !f.critica && !f.configurada);

  // El circuito comercial completo: cobrar -> emitir -> entregar. Si algo de
  // esto falta, no está listo para vender, por más que el sitio cargue.
  const listoParaVender = faltanCriticas.length === 0;

  res.status(200).json({
    listo_para_vender: listoParaVender,
    resumen: listoParaVender
      ? "Todo lo imprescindible está configurado: se puede cobrar, emitir la licencia y descargar el instalador."
      : `Faltan ${faltanCriticas.length} variable(s) imprescindible(s): ` +
        faltanCriticas.map((f) => f.variable).join(", "),
    faltan_criticas: faltanCriticas.map((f) => f.variable),
    faltan_opcionales: faltanOpcionales.map((f) => f.variable),
    // Que quede claro si este diagnóstico está abierto al público o no.
    protegido: Boolean(llave),
    aviso_proteccion: llave ? undefined
      : "Este endpoint está abierto. Definí MVDG_ESTADO_TOKEN en Vercel para exigir ?t=<token>.",
    detalle: filas,
    // Nunca hay valores acá. Se dice explícitamente para que nadie lo espere.
    nota: "Solo booleanos: este endpoint jamás devuelve el valor de una variable, ni enmascarado.",
  });
};

module.exports.VARIABLES = VARIABLES;
