/*
 * MV Data Governance · Configuración de pagos (MercadoPago).
 *
 * COMO CONECTAR TU MERCADOPAGO (una sola vez):
 *   1. Entrá a tu cuenta de MercadoPago → "Cobrar" → "Link de pago"
 *      (o "Botón de pago"). Creá un link por cada producto con su precio.
 *   2. En "Configuración avanzada" del link, poné la URL de retorno
 *      (back_url / "A dónde vuelve el cliente al pagar") apuntando a:
 *         https://mv-data-governance.vercel.app/pago.html
 *      Así, al pagar, el cliente vuelve a la página de descarga.
 *   3. Pegá cada URL de link de pago abajo, entre las comillas.
 *
 * Mientras un link esté vacío (""), el botón deriva al contacto por mail
 * (no se muestra ningún checkout falso).
 */
window.MVDG_PAY = {
  // Email de contacto para el fallback (mientras no haya link de MP)
  contactEmail: "vieraschiavi@gmail.com",

  // Tasa USD -> UYU para mostrar el precio en pesos al lado (ajustala a la
  // cotizacion del dia; poné 0 para ocultar el precio en UYU).
  uyuRate: 40,

  // --- Links de pago de MercadoPago (pegá los tuyos) ---
  links: {
    licencia:  "",   // Licencia PC (pago único)
    pro:       "",   // Professional (suscripción mensual)
    cred100:   "",   // Pack 100 créditos
    cred550:   "",   // Pack 550 créditos
    cred2500:  ""    // Pack 2500 créditos
  },

  // --- Precios mostrados en la web (en USD; ajustá si cobrás en $ local) ---
  prices: {
    licencia:  { amount: 149, unit: "" },        // pago único
    pro:       { amount: 390, unit: "/mes" },     // mensual
    cred100:   { amount: 9,   credits: 100 },
    cred550:   { amount: 39,  credits: 550 },
    cred2500:  { amount: 149, credits: 2500 }
  }
};
