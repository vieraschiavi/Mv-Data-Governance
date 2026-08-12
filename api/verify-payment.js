// Verifica un pago de MercadoPago contra la API real (server-side) antes de
// habilitar la descarga. Evita que alguien arme la URL de /pago.html a mano
// sin haber pagado. Si el pago está aprobado, emite automáticamente la
// licencia MV Data Governance (firmada).

const { sign, signEd25519, planDeSku, diasDeSku } = require("./_license");
const { rateLimited, clientIp } = require("./_rate_limit");
const { registrar } = require("./_usados");

module.exports = async (req, res) => {
  // 30/min por IP: la página solo llama esto una vez al cargar /pago.html,
  // pero frena un intento de enumerar payment_id contra la API de MP.
  if (rateLimited(clientIp(req), { max: 30, windowMs: 60_000 })) {
    res.status(429).json({ approved: false, error: "rate_limit" });
    return;
  }
  const paymentId = String((req.query && req.query.payment_id) || "").trim();
  if (!paymentId || !/^[0-9]+$/.test(paymentId)) {
    res.status(400).json({ approved: false, error: "payment_id inválido" });
    return;
  }
  const token = process.env.MP_ACCESS_TOKEN;
  if (!token) { res.status(500).json({ approved: false, error: "no_token" }); return; }

  try {
    const r = await fetch("https://api.mercadopago.com/v1/payments/" + paymentId, {
      headers: { Authorization: "Bearer " + token },
    });
    const data = await r.json();
    if (!r.ok) { res.status(502).json({ approved: false, error: "mp_error" }); return; }

    const approved = data.status === "approved";
    // El SKU es lo que se cobro; el plan es el tier que el programa entiende.
    // Traducir es obligatorio: meter el SKU crudo en el token hacia que
    // licensing.verify() lo rechazara por plan desconocido.
    const sku = (data.metadata && data.metadata.plan) || null;
    const plan = planDeSku(sku);

    // --- La licencia se emite solo en una ventana corta tras el pago -------
    //
    // El payment_id NO es un secreto: MercadoPago lo agrega a la URL de
    // retorno, asi que queda en la barra del navegador del comprador, en su
    // historial y en cualquier captura que comparta. Y este endpoint no ata
    // quien llama con quien pago: cualquiera con ese id pedia una licencia, y
    // las veces que quisiera. Con licencias perpetuas y sin atar a la maquina,
    // un solo id compartido alcanzaba para licencias ilimitadas.
    //
    // Sin base de datos no se puede llevar registro de ids ya usados (Vercel
    // es sin estado), pero si acotar CUANDO sirven. El comprador legitimo cae
    // en /pago.html segundos despues de pagar; un id filtrado se reusa mucho
    // mas tarde. La ventana no elimina el problema — lo reduce de "para
    // siempre" a "media hora".
    const VENTANA_MIN = 30;
    const aprobadoEn = Date.parse(data.date_approved || data.date_created || "");
    // Sin fecha utilizable no se puede afirmar que el pago sea reciente, asi
    // que no se afirma: falla CERRADO. Es el mismo criterio que descargar.js
    // ("fallar ruidoso es mejor que entregar algo equivocado") — si MP cambia
    // el formato, las ventas se cortan de golpe y se arregla, en vez de dejar
    // la ventana abierta en silencio.
    const fresco = Number.isFinite(aprobadoEn) &&
      (Date.now() - aprobadoEn) <= VENTANA_MIN * 60_000 &&
      (aprobadoEn - Date.now()) <= 5 * 60_000;   // tolera reloj adelantado

    const iat = Math.floor(Date.now() / 1000);
    const payload = {
      plan: plan,
      pid: paymentId,
      email: (data.payer && data.payer.email) || null,
      iat: iat,
    };
    // El vencimiento sale de lo que se VENDIO (DIAS_POR_SKU), no de una
    // constante suelta: si un SKU pasa a ser temporal, el token caduca sin
    // tocar este archivo. 0 = perpetua, y entonces NO se agrega `exp` —
    // verify() solo rechaza cuando `exp` existe y ya paso.
    const dias = diasDeSku(sku);
    if (dias > 0) payload.exp = iat + dias * 86400;

    // MVDG1 (HMAC): se mantiene por compatibilidad con lo ya emitido.
    let license = null;
    const secret = process.env.LICENSE_SECRET;
    // Se aplica la MISMA ventana a la HMAC. Hoy nadie la muestra, pero
    // dejarla saliendo cuando la Ed25519 se retiene seria una mina: basta
    // que alguien cablee esa via mas adelante para reabrir el agujero.
    // La HMAC se decide junto con la Ed25519 mas abajo (necesita `emitible`,
    // que sale del registro). Se calcula despues para no emitir una si se
    // retiene la otra.
    const puedeHmac = approved && secret && fresco;

    // MVDG2 (Ed25519): ESTA es la que el programa de escritorio sabe validar
    // (ver mvdg/licensing.py). Si falta LICENSE_PRIVATE_KEY o la firma falla,
    // se devuelve null y el cliente ve "no se pudo emitir la licencia" — nunca
    // se entrega una licencia rota como si fuera buena.
    // Se exige `plan`: un SKU sin tier (los packs de creditos) NO recibe
    // licencia. Antes se le firmaba una igual, y el cliente se llevaba una
    // license_key que el programa rechaza — peor que no darle ninguna, porque
    // parece que compro algo que no funciona.
    // Registro de pagos ya usados: cierra lo que la ventana solo achicaba.
    // Se consulta SOLO si todo lo demas ya dio verde, para no marcar como
    // usado un pago al que igual no le ibamos a emitir licencia — eso
    // quemaria el id del comprador legitimo.
    const privKey = process.env.LICENSE_PRIVATE_KEY;
    let usado = "sin_registro";
    if (approved && privKey && plan && fresco) {
      usado = await registrar(paymentId);
    }
    const emitible = usado !== "repetido";

    if (puedeHmac && emitible) license = sign(payload, secret);

    let licenseKey = null;
    if (approved && privKey && plan && fresco && emitible) {
      try {
        licenseKey = signEd25519(payload, privKey);
      } catch (e) {
        licenseKey = null;
      }
    }

    res.status(200).json({
      // `plan` sigue siendo el SKU: es lo que la pagina de pago muestra y su
      // tabla PLAN_NAMES esta indexada asi. `tier` es el plan de licencia,
      // util para soporte cuando hay que entender que recibio el cliente.
      approved: approved, status: data.status, plan: sku, tier: plan,
      license: license, license_key: licenseKey,
      // Por que no hay licencia, cuando el pago si esta aprobado. La pagina
      // ya muestra 'escribinos y te la mandamos'; esto es para soporte.
      motivo: (approved && !licenseKey)
        ? (!plan ? "sku_sin_licencia" : !privKey ? "emisor_no_configurado"
                 : !fresco ? "fuera_de_ventana"
                 : usado === "repetido" ? "ya_emitida" : "error_de_firma")
        : undefined,
    });
  } catch (e) {
    res.status(500).json({ approved: false, error: "exception" });
  }
};
