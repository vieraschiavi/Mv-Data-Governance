// Proxy de IA pago con créditos.
//
// El programa de escritorio ya sabe llamar a Claude/ChatGPT/Gemini con la API
// key DEL USUARIO (mvdg/ai_provider.py), y esa vía sigue siendo la
// recomendada: el cliente paga precio de costo, sin intermediario. Este
// endpoint es la alternativa para quien no quiere gestionar una API key:
// compra créditos y las llamadas salen por acá, con las keys del dueño del
// producto.
//
// ────────────────────────────────────────────────────────────────────────────
// Acá se gasta plata real, así que todo falla CERRADO
// ────────────────────────────────────────────────────────────────────────────
// En el resto del backend, ante una caída del KV se prefiere dejar pasar
// (bloquear una compra es peor que el riesgo que se cubre). Acá es al revés:
// si no se puede confirmar que hay saldo, NO se llama al modelo. Una caída
// que "deja pasar" se traduce en una factura de Anthropic que paga el dueño.
//
// ────────────────────────────────────────────────────────────────────────────
// Se cobra ANTES de llamar, y se devuelve si falla
// ────────────────────────────────────────────────────────────────────────────
// Cobrar después dejaría la ventana obvia: mil pedidos simultáneos con saldo
// 1 se cobran una vez y se atienden mil veces. Cobrar antes cierra eso. Y si
// el modelo falla, se devuelve el crédito: nadie paga por una respuesta que
// no recibió.
const { rateLimited, clientIp } = require("./_rate_limit");
const cred = require("./_creditos");

// Techos de costo. Sin esto, un prompt gigante cuesta muchas veces más que
// el crédito que se cobró — el precio dejaría de tener relación con el gasto.
const MAX_PROMPT = 6000;      // caracteres
const MAX_SALIDA = 700;       // tokens de respuesta

// Las keys son del DUEÑO del producto, no del cliente. Se elige el primer
// proveedor configurado: quién atiende es una decisión de costo, no del
// cliente, y exponerla dejaría elegir el modelo más caro.
const PROVEEDORES = [
  {
    env: "MVDG_IA_ANTHROPIC", nombre: "claude",
    url: "https://api.anthropic.com/v1/messages",
    headers: (k) => ({ "x-api-key": k, "anthropic-version": "2023-06-01",
                       "content-type": "application/json" }),
    body: (p) => ({ model: "claude-sonnet-4-5", max_tokens: MAX_SALIDA,
                    messages: [{ role: "user", content: p }] }),
    texto: (d) => d && d.content && d.content[0] && d.content[0].text,
  },
  {
    env: "MVDG_IA_OPENAI", nombre: "openai",
    url: "https://api.openai.com/v1/chat/completions",
    headers: (k) => ({ Authorization: `Bearer ${k}`, "content-type": "application/json" }),
    body: (p) => ({ model: "gpt-4o-mini", max_tokens: MAX_SALIDA,
                    messages: [{ role: "user", content: p }] }),
    texto: (d) => d && d.choices && d.choices[0] && d.choices[0].message &&
                  d.choices[0].message.content,
  },
];

function elegirProveedor() {
  for (const p of PROVEEDORES) {
    const k = (process.env[p.env] || "").trim();
    if (k) return { ...p, key: k };
  }
  return null;
}

module.exports = async (req, res) => {
  if (rateLimited(clientIp(req), { max: 30, windowMs: 60_000 })) {
    res.status(429).json({ error: "rate_limit" });
    return;
  }
  if (req.method !== "POST") { res.status(405).json({ error: "method" }); return; }

  const body = typeof req.body === "string" ? safeJson(req.body) : (req.body || {});
  const clave = String(body.clave || "").trim();
  const operacion = String(body.operacion || "").trim();
  const prompt = String(body.prompt || "");

  if (!cred.claveValida(clave)) {
    res.status(400).json({ error: "clave_invalida" });
    return;
  }
  const costo = cred.COSTOS[operacion];
  if (!costo) { res.status(400).json({ error: "operacion_invalida" }); return; }
  if (!prompt || prompt.length > MAX_PROMPT) {
    res.status(400).json({ error: "prompt_invalido", max: MAX_PROMPT });
    return;
  }
  if (!cred.configurado()) {
    // Sin KV no hay libro mayor, y sin libro mayor no se puede cobrar. Se
    // dice claro en vez de atender gratis.
    res.status(503).json({ error: "creditos_no_disponibles" });
    return;
  }
  const prov = elegirProveedor();
  if (!prov) { res.status(503).json({ error: "ia_no_configurada" }); return; }

  // Se cobra primero. -1 = no alcanza; null = no se pudo confirmar, y eso NO
  // se trata como que alcanza.
  const restante = await cred.consumir(clave, costo);
  if (restante === null) { res.status(503).json({ error: "saldo_no_verificable" }); return; }
  if (restante < 0) {
    res.status(402).json({ error: "sin_creditos", costo: costo });
    return;
  }

  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 45_000);
    let datos;
    try {
      const r = await fetch(prov.url, {
        method: "POST",
        headers: prov.headers(prov.key),
        body: JSON.stringify(prov.body(prompt)),
        signal: ctrl.signal,
      });
      if (!r.ok) throw new Error("proveedor " + r.status);
      datos = await r.json();
    } finally {
      clearTimeout(timer);
    }
    const texto = prov.texto(datos);
    if (!texto) throw new Error("respuesta vacia");
    res.status(200).json({ texto: texto, saldo: restante, proveedor: prov.nombre });
  } catch (e) {
    // Falló el modelo: se devuelve lo cobrado. El cliente no paga por una
    // respuesta que no recibió. Nunca se filtra el detalle del error, que
    // puede traer la key o datos del proveedor.
    await cred.devolver(clave, costo);
    res.status(502).json({ error: "proveedor_no_responde" });
  }
};

function safeJson(s) { try { return JSON.parse(s); } catch (e) { return {}; } }
