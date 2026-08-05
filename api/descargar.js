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

const { rateLimited, clientIp } = require("./_rate_limit");

// Variable de entorno con la URL del instalador. Sin esto configurado la
// función NO inventa una URL ni sirve un archivo viejo: responde 503 con un
// mensaje que dice exactamente qué falta. Fallar ruidoso es mejor que dejar
// un botón que baja algo equivocado.
const VAR_URL = "MVDG_INSTALLER_URL";

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

  const destino = (process.env[VAR_URL] || "").trim();
  if (!destino) {
    res.status(503).json({
      error: "sin_configurar",
      es: `Falta la variable de entorno ${VAR_URL} con la URL del instalador.`,
      en: `Missing ${VAR_URL} environment variable with the installer URL.`,
      pt: `Falta a variável de ambiente ${VAR_URL} com a URL do instalador.`,
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
