// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Descarga del instalador .exe de Windows.
//
// ────────────────────────────────────────────────────────────────────────────
// Por qué un redirect y no el archivo servido desde acá
// ────────────────────────────────────────────────────────────────────────────
// El instalador pesa cientos de MB. No puede vivir en el repositorio (GitHub
// rechaza archivos de más de 100 MB) ni en el deploy de Vercel (mismo orden de
// límite, y cada deploy lo re-subiría). Así que el .exe se aloja aparte y esta
// función redirige ahí.
//
// La ventaja de que sea un endpoint y no un <a href> directo al hosting: la
// URL real vive en una variable de entorno. Cambiar de hosting (una release
// pública, S3, R2, Blob) es cambiar una variable en Vercel — no hay que tocar
// el HTML de las 4 páginas que enlazan la descarga, ni volver a deployar.
//
// ────────────────────────────────────────────────────────────────────────────
// Demo y full son EL MISMO archivo
// ────────────────────────────────────────────────────────────────────────────
// No hay dos instaladores. Hay uno, y la licencia decide qué habilita:
//
//   sin licencia          -> plan demo (catálogo, calidad, linaje, glosario,
//                            perfilado, MDM, export a BI, datos propios)
//   con licencia pagada   -> se suman migración a Purview/Collibra y escaneo
//                            de tenant BI (ver mvdg/licensing.py)
//
// Por eso quien paga NO baja otro programa: baja el mismo y pega su clave en
// la pestaña Ayuda. Mantenerlo así es deliberado — un único binario es el que
// se audita, se testea y se firma; dos builds paralelos serían dos superficies
// donde uno puede quedar atrás del otro sin que nadie se entere.
//
// El parámetro ?plan= solo sirve para medir desde dónde se descargó; no cambia
// el archivo que se entrega, y no se usa para autorizar nada.
//
// ────────────────────────────────────────────────────────────────────────────
// LA DESCARGA NO ES PÚBLICA: hay que traer una licencia (?k=)
// ────────────────────────────────────────────────────────────────────────────
// Antes esta URL entregaba el instalador a cualquiera que la escribiera. La
// página de descargas era pública, así que "público" era el diseño — pero el
// artefacto de ingeniería quedaba regalado: cualquier competidor se bajaba el
// producto entero sin dejar rastro, sin dar un nombre y sin hablar con nadie.
//
// El criterio nuevo es que la demo se pide. Y el gate tiene que estar ACÁ, no
// en el HTML: sacar el botón de la página y dejar el endpoint abierto es
// decoración — la URL ya está publicada y quien la tenga sigue bajando.
//
// Qué habilita la descarga: una licencia MVDG2 válida y sin vencer.
//   · el que paga         -> la recibe al pagar (pago.html la agrega al link)
//   · el que pide la demo -> se le emite una licencia `trial` DESPUÉS de la
//                            demo 1:1, con Actions -> "Emitir licencia"
// Sin base de datos y sin cuentas: la firma Ed25519 ya es la credencial, y es
// la misma que el programa valida después. Un solo mecanismo, no dos.
//
// Lo que esto NO es: una protección contra que alguien reparta su propio
// instalador una vez bajado. Eso no existe para software que se instala.
// Lo que sí hace es que nadie se lo lleve ANÓNIMAMENTE: para bajarlo hay que
// haber pasado por una compra o por una demo agendada, y las dos dejan quién.

const { rateLimited, clientIp } = require("./_rate_limit");
const { verifyEd25519 } = require("./_license");

// ────────────────────────────────────────────────────────────────────────────
// CADA UNO BAJA EL BUILD DE SU PLAN
// ────────────────────────────────────────────────────────────────────────────
// Antes había UNA sola variable para todos, así que el owner —con su licencia
// owner en la mano— bajaba el mismo instalador que un cliente: el build sin
// desbloquear. La versión owner existía en Actions y no llegaba por ningún
// lado. Ahora la elige el plan que trae la licencia FIRMADA, que es un dato
// que el que descarga no puede falsear.
//
// Sigue habiendo UN SOLO PROGRAMA. Lo que cambia entre los dos artefactos no
// es el código: el build owner lleva `licencia_owner.txt` adentro (atada a la
// máquina) para abrir desbloqueado sin pegar nada. Todo lo demás —qué habilita
// cada plan pago— lo decide la licencia en tiempo de ejecución
// (mvdg/licensing.py), no el instalador. Hacer un .exe por plan sería tener
// cuatro superficies que se desincronizan sin que nadie se entere, que es
// justo lo que este proyecto viene evitando a propósito.
//
// Sin la variable del build owner configurada, el owner recibe 503 diciendo
// cuál falta — NO se le entrega el build del cliente. Servir "algo parecido"
// en silencio es cómo se termina probando el producto equivocado y creyendo
// que se probó el bueno.
const VAR_URL = "MVDG_INSTALLER_URL";
const VAR_URL_OWNER = "MVDG_INSTALLER_URL_OWNER";

function variableDelPlan(plan) {
  return plan === "owner" ? VAR_URL_OWNER : VAR_URL;
}

module.exports = async (req, res) => {
  // 30/min por IP: bajar un instalador es algo que se hace una vez, pero un
  // reintento tras un corte de red es normal. El límite frena un script en
  // loop, no a una persona.
  if (rateLimited(clientIp(req), { max: 30, windowMs: 60_000 })) {
    res.status(429).json({ error: "rate_limit" });
    return;
  }
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.status(405).json({ error: "method" });
    return;
  }

  // La licencia primero: si no autoriza, no hay por qué mirar la URL del
  // instalador ni revelar si está configurada.
  const clave = String((req.query && (req.query.k || req.query.licencia)) || "").trim();
  const licencia = verifyEd25519(clave);
  if (!licencia) {
    res.status(403).json({
      error: clave ? "licencia_invalida" : "licencia_requerida",
      es: "La demo no es de descarga libre. Pedí acceso en /descargas.html: "
          + "coordinamos una demo 1:1 y te enviamos tu licencia.",
      en: "The demo is not a free download. Request access at /descargas.html: "
          + "we set up a 1:1 demo and send you your license.",
      pt: "A demo não é de download livre. Peça acesso em /descargas.html: "
          + "marcamos uma demo 1:1 e enviamos sua licença.",
    });
    return;
  }

  // El plan sale de la licencia verificada, nunca de la query: `?plan=` lo
  // pone quien descarga y solo sirve para medir de dónde vino el clic.
  const variable = variableDelPlan(licencia.plan);
  const destino = (process.env[variable] || "").trim();
  if (!destino) {
    res.status(503).json({
      error: "sin_configurar",
      variable: variable,
      es: `Falta la variable de entorno ${variable} con la URL del instalador.`,
      en: `Missing ${variable} environment variable with the installer URL.`,
      pt: `Falta a variável de ambiente ${variable} com a URL do instalador.`,
    });
    return;
  }

  // Solo https. Un http:// permitiría degradar la descarga de un ejecutable a
  // texto plano interceptable — para un .exe que el usuario va a correr con
  // permisos, eso es exactamente lo que no se quiere.
  let url;
  try {
    url = new URL(destino);
  } catch {
    res.status(500).json({ error: "url_invalida" });
    return;
  }
  if (url.protocol !== "https:") {
    res.status(500).json({ error: "url_insegura" });
    return;
  }

  // 302 y no 301: un permanente lo cachea el navegador para siempre, y el día
  // que cambie el hosting los que ya entraron seguirían yendo al viejo.
  res.setHeader("Location", url.toString());
  res.setHeader("Cache-Control", "no-store");
  res.status(302).end();
};

module.exports.VAR_URL = VAR_URL;
module.exports.VAR_URL_OWNER = VAR_URL_OWNER;
module.exports.variableDelPlan = variableDelPlan;
