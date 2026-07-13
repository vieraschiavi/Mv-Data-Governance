/*
 * MV Data Governance · Configuración de precios mostrados en la web.
 *
 * El COBRO REAL con MercadoPago ya está conectado del lado del servidor
 * (funciones serverless api/checkout.js y api/verify-payment.js) — no hay
 * nada que pegar acá. Para activarlo, configurá en Vercel (Project Settings
 * → Environment Variables) las variables MP_ACCESS_TOKEN y LICENSE_SECRET
 * (o, sin token, los links MP_LINK_LICENCIA / MP_LINK_PRO / MP_LINK_CRED100
 * / MP_LINK_CRED550 / MP_LINK_CRED2500). Guía completa: docs/MERCADOPAGO.md
 *
 * Este archivo solo controla los PRECIOS que se muestran en pantalla — no
 * contiene ningún dato sensible.
 */
window.MVDG_PAY = {
  // Tasa USD -> UYU para mostrar el precio en pesos al lado (ajustala a la
  // cotizacion del dia; poné 0 para ocultar el precio en UYU).
  uyuRate: 40,

  // --- Precios mostrados en la web (en USD; deben coincidir con PLANS en api/checkout.js) ---
  prices: {
    licencia:  { amount: 149, unit: "" },        // pago único
    pro:       { amount: 390, unit: "/mes" },     // mensual
    cred100:   { amount: 9,   credits: 100 },
    cred550:   { amount: 39,  credits: 550 },
    cred2500:  { amount: 149, credits: 2500 }
  }
};
