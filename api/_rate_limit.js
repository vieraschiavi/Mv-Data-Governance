// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Rate limiting en memoria para las funciones serverless de pago/licencia.
// Prefijo "_" para que Vercel NO la trate como endpoint — es un módulo
// interno, igual que _license.js.
//
// Mismo criterio que bi_api/main.py: ventana deslizante en memoria del
// proceso. En Vercel cada instancia lambda puede ser efímera, así que esto
// NO es un límite global perfecto entre instancias — pero sí frena en seco
// un loop o un script contra la MISMA instancia (que es lo que Vercel
// reutiliza en ráfagas cortas desde la misma IP), y es estrictamente mejor
// que no tener nada. Sin dependencia nueva: Map + Date.now().

const HITS = new Map();

function clientIp(req) {
  const xf = req.headers && req.headers["x-forwarded-for"];
  if (xf) return String(xf).split(",")[0].trim();
  return (req.socket && req.socket.remoteAddress) || "desconocido";
}

// Devuelve true si YA se paso el limite (y no cuenta este intento). Pensado
// para checkear una vez al principio del handler.
function rateLimited(key, { max, windowMs }) {
  const now = Date.now();
  let hits = HITS.get(key);
  if (!hits) { hits = []; HITS.set(key, hits); }
  while (hits.length && now - hits[0] > windowMs) hits.shift();
  if (hits.length >= max) return true;
  hits.push(now);
  // Higiene: no acumular IPs muertas para siempre.
  //
  // La version anterior barria borrando solo las entradas con array VACIO, y
  // los arrays se podan unicamente cuando esa misma clave se vuelve a
  // consultar (el `while` de arriba). O sea que una IP que entra una vez y no
  // vuelve deja su timestamp para siempre, su array nunca queda vacio, y el
  // barrido no borraba NADA. Medido: 3000 IPs con la ventana ya vencida
  // dejaban las 3000 entradas en el Map.
  //
  // Ahora se mira la ULTIMA marca de cada clave: si ya quedo fuera de la
  // ventana, esa clave no puede limitar a nadie y se va. Peor caso si otro
  // endpoint usa una ventana mas larga: alguien recupera su cupo antes de
  // tiempo — muy preferible a que el proceso crezca sin techo.
  if (HITS.size > 2048) {
    for (const [k, v] of HITS) {
      if (!v.length || now - v[v.length - 1] > windowMs) HITS.delete(k);
    }
  }
  return false;
}

function resetForTests() { HITS.clear(); }

module.exports = { rateLimited, clientIp, resetForTests };
