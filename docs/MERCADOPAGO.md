# 💳 Conectar MercadoPago (venta y descarga)

La web ya trae el flujo de venta armado. Solo falta pegar **tus** links de
pago de MercadoPago — se hace una vez, sin programar.

## 1. Crear los links de pago

En tu cuenta de MercadoPago:

1. Entrá a **Cobrar → Link de pago** (o "Botón de pago").
2. Creá un link por producto, con su precio:
   - **Licencia PC** — US$ 149 (pago único)
   - **Professional** — US$ 390 / mes (suscripción)
   - **100 créditos** — US$ 9
   - **550 créditos** — US$ 39
   - **2.500 créditos** — US$ 149
3. En **Configuración avanzada** de cada link, poné la **URL de retorno**
   (a dónde vuelve el cliente al pagar):
   ```
   https://mv-data-governance.vercel.app/pago.html
   ```
   Así, al confirmarse el pago, el cliente llega a la página de descarga.

## 2. Pegar los links en el proyecto

Editá **`landing/payments-config.js`** y pegá cada URL entre las comillas:

```js
links: {
  licencia:  "https://mpago.la/XXXX",   // Licencia PC
  pro:       "https://mpago.la/XXXX",   // Professional mensual
  cred100:   "https://mpago.la/XXXX",
  cred550:   "https://mpago.la/XXXX",
  cred2500:  "https://mpago.la/XXXX"
}
```

Guardá, hacé commit a `main` y **Redeploy** en Vercel. Listo: los botones
"Comprar con MercadoPago" ya llevan al checkout real.

> **Mientras un link esté vacío**, el botón deriva a tu correo (no se muestra
> ningún checkout falso). Podés publicar la web ya y agregar los links después.

## 3. Entregar la descarga tras el pago

`pago.html` (la URL de retorno) ofrece la descarga automáticamente. Para mayor
control, MercadoPago te avisa cada pago por email y en su panel; podés además
mandarle al comprador el enlace y una clave de licencia por correo.

## Notas

- **Suscripción mensual (Professional):** en MercadoPago se crea como
  "Suscripción" en vez de link de pago único; pegás igual su URL en `pro`.
- **Precios en pesos:** si preferís cobrar en UYU/ARS, poné el monto en el
  link de MercadoPago y ajustá los números en `payments-config.js` (`prices`).
- Todo el cobro ocurre en la infraestructura de MercadoPago; el sitio es
  estático y no maneja datos de tarjetas.
