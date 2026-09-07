// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
//
// ────────────────────────────────────────────────────────────────────────────
// Pedido de acceso a la demo
// ────────────────────────────────────────────────────────────────────────────
// Reemplaza a la descarga abierta y al trial que se emitía solo. El visitante
// deja nombre, empresa, país y email; el pedido llega por mail y la licencia
// la emite una persona después de la demo 1:1.
//
// Por qué el cambio: un demo abierto regalaba el artefacto de ingeniería —
// cualquiera se bajaba el producto entero sin dar un nombre. Pedirlo cambia
// tres cosas: no se regala el programa (solo se muestra), se separa al
// prospecto del competidor curioso, y la demo agendada se usa para vender
// mientras se muestra, en vez de que miren solos y se vayan.
//
// ESTE ENDPOINT NO EMITE NINGUNA LICENCIA. Es a propósito: si emitiera algo,
// volvería a ser una descarga automática con un formulario adelante, que es
// exactamente lo que se quiso sacar. Lo único que hace es avisar.
//
// ────────────────────────────────────────────────────────────────────────────
// Cómo llega el mail
// ────────────────────────────────────────────────────────────────────────────
// Por Resend (https://resend.com), que tiene plan gratis y no pide servidor
// SMTP. Hace falta UNA variable de entorno en Vercel:
//
//   RESEND_API_KEY   -> la clave que da Resend (empieza con "re_")
//
// Opcionales:
//   MVDG_MAIL_TO     -> a dónde llega el aviso (por defecto, el del dueño)
//   MVDG_MAIL_FROM   -> el remitente. Por defecto "onboarding@resend.dev",
//                       que Resend habilita sin verificar dominio pero SOLO
//                       puede escribirle a la casilla dueña de la cuenta. Con
//                       un dominio propio verificado se pone acá y se le puede
//                       escribir a cualquiera (por ejemplo, acusar recibo al
//                       que pidió la demo).
//
// Si falta la clave, el pedido NO se pierde en silencio: responde 503 y la
// página muestra el mailto de respaldo. Un formulario que dice "gracias" y
// tira el pedido a la basura es peor que no tener formulario.

const { rateLimited, clientIp } = require("./_rate_limit");

const DESTINO = (process.env.MVDG_MAIL_TO || "vieraschiavi@gmail.com").trim();
const REMITENTE = (process.env.MVDG_MAIL_FROM || "onboarding@resend.dev").trim();

// Topes de largo: cortan un cuerpo de 2 MB pegado en el campo "empresa" antes
// de que se convierta en un mail de 2 MB. Generosos para que ningún nombre
// real quede afuera.
const LARGO = { nombre: 120, empresa: 120, pais: 60, email: 254, mensaje: 2000 };

// 5/min por IP. Pedir una demo es algo que se hace una vez; esto frena que
// alguien use el formulario como generador de mails.
const LIMITE = { max: 5, windowMs: 60_000 };

function texto(v, max) {
  return String(v == null ? "" : v).replace(/\s+/g, " ").trim().slice(0, max);
}

module.exports = async (req, res) => {
  if (rateLimited(clientIp(req), LIMITE)) {
    res.status(429).json({ ok: false, error: "rate_limit" });
    return;
  }
  if (req.method !== "POST") { res.status(405).json({ ok: false, error: "method" }); return; }

  const body = typeof req.body === "string" ? safeJson(req.body) : (req.body || {});
  const datos = {
    nombre: texto(body.nombre, LARGO.nombre),
    empresa: texto(body.empresa, LARGO.empresa),
    pais: texto(body.pais, LARGO.pais),
    email: texto(body.email, LARGO.email),
    mensaje: texto(body.mensaje, LARGO.mensaje),
  };

  // Los cuatro que hacen que el pedido sirva para algo. El mensaje (cuándo le
  // viene bien la demo) es opcional: pedirlo obligatorio agrega fricción justo
  // en el paso donde la gente abandona.
  const faltan = ["nombre", "empresa", "pais", "email"].filter((c) => !datos[c]);
  if (faltan.length) {
    res.status(400).json({ ok: false, error: "faltan_datos", campos: faltan });
    return;
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(datos.email)) {
    res.status(400).json({ ok: false, error: "email_invalido" });
    return;
  }

  const apiKey = (process.env.RESEND_API_KEY || "").trim();
  if (!apiKey) {
    // 503 y no 200: que el visitante vea el mailto de respaldo en vez de
    // creer que el pedido llegó.
    res.status(503).json({ ok: false, error: "mail_no_configurado" });
    return;
  }

  // Todo el pedido va en TEXTO PLANO, no en HTML. Es contenido que escribió un
  // desconocido: mandarlo como HTML sería inyectarle marcado a la casilla que
  // lo lee. En texto plano no hay nada que escapar ni nada que renderice.
  const cuerpo = [
    "Pedido de acceso a la demo — MV Data Governance",
    "",
    `Nombre:  ${datos.nombre}`,
    `Empresa: ${datos.empresa}`,
    `País:    ${datos.pais}`,
    `Email:   ${datos.email}`,
    "",
    datos.mensaje ? `Mensaje:\n${datos.mensaje}` : "(sin mensaje)",
    "",
    "───",
    "Para darle acceso: Actions -> \"Emitir licencia\" -> plan trial, 14 dias.",
  ].join("\n");

  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer " + apiKey,
                 "Content-Type": "application/json" },
      body: JSON.stringify({
        from: REMITENTE,
        to: [DESTINO],
        // El asunto lleva empresa y nombre: la bandeja se ordena sola y se ve
        // de quién es el pedido sin abrirlo.
        subject: `Demo MV Data Governance — ${datos.empresa} (${datos.nombre})`,
        text: cuerpo,
        // Responder al mail contesta al que pidió la demo, no a Resend.
        reply_to: datos.email,
      }),
    });
    if (!r.ok) {
      res.status(502).json({ ok: false, error: "mail_no_enviado" });
      return;
    }
  } catch (e) {
    res.status(502).json({ ok: false, error: "mail_inaccesible" });
    return;
  }

  res.status(200).json({ ok: true });
};

function safeJson(s) { try { return JSON.parse(s); } catch (e) { return {}; } }

module.exports.DESTINO = DESTINO;
module.exports.LARGO = LARGO;
