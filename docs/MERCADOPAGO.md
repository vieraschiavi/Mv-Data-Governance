# 💳 MercadoPago — cobro real conectado

La web ya tiene el cobro **real** de MercadoPago conectado del lado del
servidor (Checkout Pro), con verificación del pago y emisión de licencia
automáticas. No hay que tocar código ni pegar links a mano: solo cargar
credenciales como variables de entorno en Vercel.

## Cómo funciona (resumen técnico)

1. El visitante hace clic en "Comprar con MercadoPago" en `landing/index.html`.
2. El navegador llama a la función serverless `api/checkout.js` (`POST /api/checkout`
   con `{plan: "licencia"}`), que crea una **preferencia** de pago contra la
   API de MercadoPago (`POST /checkout/preferences`) usando tu Access Token,
   y devuelve la URL de checkout (`init_point`).
3. El navegador redirige a esa URL (MercadoPago procesa el pago en su propia
   infraestructura — el sitio nunca toca datos de tarjeta).
4. MercadoPago devuelve al comprador a `landing/pago.html`, que llama a
   `api/verify-payment.js` (`GET /api/verify-payment?payment_id=...`). Esta
   función **verifica el pago contra la API de MercadoPago del lado del
   servidor** (nunca confía en los parámetros de la URL solos) y, si está
   `approved`, emite una **licencia firmada** (HMAC-SHA256, `MVDG1.…`) y la
   muestra junto con el botón de descarga.

Sin `MP_ACCESS_TOKEN` configurado, `api/checkout.js` cae a un link de pago
fijo por producto (`MP_LINK_*`, opcional) o devuelve un error claro en vez de
mostrar un checkout falso.

### La demo se pide: no se baja (sin MercadoPago)

Antes había un trial que se emitía solo (`POST /api/trial`: dejabas un email y
recibías una licencia Professional de 14 días) y una página de descargas
abierta. Las dos se sacaron, y no por seguridad abstracta: el ZIP público
traía los **105 archivos del programa** — `app/app.py` y el motor `mvdg/`
enteros. Cualquiera se llevaba el código fuente sin dar un nombre.

Hoy el circuito es:

1. El visitante completa **nombre, empresa, país y email** en
   `landing/descargas.html` → `POST /api/acceso`.
2. `api/acceso.js` te manda un mail con esos datos (por Resend, ver abajo).
   **No emite ninguna licencia**: si emitiera algo volvería a ser una descarga
   automática con un formulario adelante.
3. Hacés la demo 1 a 1 y, al terminar, le emitís su licencia de prueba desde
   **Actions → "Emitir licencia"** (plan `trial`, 14 días).
4. Con esa licencia baja el instalador: `/api/descargar` **exige** una licencia
   `MVDG2` válida y sin vencer (`?k=<licencia>`). Sin ella responde 403.

El que **paga** no hace nada de esto: `landing/pago.html` recibe su licencia al
verificarse el pago y ya arma el link de descarga con ella adentro.

> El gate vive en `api/descargar.js`, no en el HTML. Sacar el botón de la
> página y dejar el endpoint abierto sería decoración: la URL ya está
> publicada y quien la tenga seguiría bajando.

### Que te llegue el mail: Resend

`api/acceso.js` manda el aviso con [Resend](https://resend.com) (plan gratis,
no hace falta servidor SMTP). Pasos, una sola vez:

1. Creá la cuenta en <https://resend.com> con **el mismo mail** al que querés
   que lleguen los pedidos.
2. **API Keys → Create API Key**, permiso *Sending access*. Copiá la clave
   (empieza con `re_`); solo se muestra una vez.
3. Cargala en Vercel como `RESEND_API_KEY` (tabla de abajo) y hacé Redeploy.

Sin dominio propio no hay nada más que hacer: el remitente por defecto es
`onboarding@resend.dev`, que Resend habilita sin verificar nada — con el
límite de que **solo puede escribirle a la casilla dueña de la cuenta**, que es
justo lo que se necesita acá. Si más adelante verificás un dominio propio
(Resend → Domains), poné esa dirección en `MVDG_MAIL_FROM` y vas a poder
además acusarle recibo al que pidió la demo.

Si la clave no está cargada, el formulario **no dice "gracias"**: responde 503
y la página muestra el mailto de respaldo. Un formulario que agradece y tira
el pedido a la basura es peor que no tener formulario.

## 1. Variables de entorno a configurar en Vercel

Andá a tu proyecto en Vercel → **Settings → Environment Variables** y cargá:

| Variable | Obligatoria | Qué es |
|---|---|---|
| `MP_ACCESS_TOKEN` | Sí (para cobro real) | Access Token **privado** de tu cuenta de MercadoPago (Panel → Tus integraciones → Credenciales de producción). **Nunca lo compartas ni lo pegues en el chat conmigo ni en el repo** — solo va como variable de entorno en Vercel. |
| `LICENSE_SECRET` | Recomendada | Clave secreta propia para firmar las licencias. Cualquier string largo y aleatorio (ej: generalo vos con `openssl rand -hex 32`). Sin esto, el pago se verifica igual pero no se emite licencia automática. |
| `LICENSE_PRIVATE_KEY` | Recomendada | Clave privada Ed25519 (par generado con `python packaging/licencias.py keygen` — ver `distribucion/owner/LEEME.md`) que firma las licencias `MVDG2`, las que **el programa de escritorio sabe validar** (`mvdg/licensing.py`). Sin esto, ni una compra real ni la licencia de prueba post-demo salen utilizables — falla cerrado, nunca se entrega una licencia rota. |
| `RESEND_API_KEY` | Sí (para recibir los pedidos de demo) | Clave de [Resend](https://resend.com) (empieza con `re_`) con la que `api/acceso.js` te manda el mail de cada pedido de acceso. Sin esto el formulario responde 503 y muestra el mailto de respaldo — nunca finge que el pedido llegó. |
| `MVDG_INSTALLER_URL` | Sí (para que se pueda bajar el .exe) | URL `https://` donde está alojado el instalador. `api/descargar.js` redirige ahí **después** de validar la licencia. Sin esto responde 503 diciendo exactamente qué falta, en vez de servir algo viejo. |
| `MVDG_MAIL_TO` | No | A dónde llegan los pedidos de demo. Por defecto, tu casilla. |
| `MVDG_MAIL_FROM` | No | Remitente de esos mails. Por defecto `onboarding@resend.dev` (sirve sin verificar dominio, pero solo puede escribirle a la casilla dueña de la cuenta de Resend). |
| `LICENSE_PUBLIC_KEY` | No | Clave pública Ed25519 con la que `api/descargar.js` valida las licencias. Por defecto usa la que está embebida en el código, la misma que lleva el programa. Solo se toca para rotar el par. |
| `MP_CURRENCY` | No | Moneda de cobro en MercadoPago. Por defecto `USD` (coincide con los precios mostrados en la web). |
| `MP_LINK_LICENCIA`, `MP_LINK_PRO`, `MP_LINK_CRED100`, `MP_LINK_CRED550`, `MP_LINK_CRED2500` | No | Links de pago fijos de respaldo, solo se usan si **no** hay `MP_ACCESS_TOKEN` cargado. |

Después de cargarlas, hacé **Redeploy** en Vercel para que tomen efecto.

> Yo (Claude) no puedo crear tu Access Token ni acceder a tu cuenta de
> MercadoPago — es un paso que hacés vos directamente en el panel de
> MercadoPago y en el de Vercel. El código ya está listo del lado del
> proyecto para usarlo apenas lo cargues.

## 2. Cómo conseguir el Access Token

1. Entrá a tu cuenta de MercadoPago → **Tu negocio → Configuración → Credenciales**
   (o `https://www.mercadopago.com.uy/developers/panel/app`).
2. Creá una aplicación (o usá la que ya tengas) y copiá el **Access Token de
   producción** (no el de prueba/sandbox, salvo que quieras testear primero).
3. Pegalo como `MP_ACCESS_TOKEN` en Vercel (paso 1).

## 3. Precios y planes

Los planes y precios que cobra `api/checkout.js` están en el objeto `PLANS`
de ese archivo (fuente de verdad del cobro real):

- **Licencia PC** — US$ 149 (pago único)
- **Professional** — US$ 390 / mes
- **100 créditos** — US$ 9
- **550 créditos** — US$ 39
- **2.500 créditos** — US$ 149

Los precios que se **muestran** en la web (incluyendo el equivalente en UYU)
están en `landing/payments-config.js` — deben coincidir con `PLANS` si los
cambiás.

## 4. Verificar que funciona

1. Con `MP_ACCESS_TOKEN` y `LICENSE_SECRET` cargados y redeployado, entrá a
   la web y hacé clic en cualquier botón "Comprar con MercadoPago" / "Comprar".
2. Debería abrir el checkout real de MercadoPago con el precio correcto.
3. Al completar un pago (o probar con credenciales de test de MercadoPago),
   volvés a `pago.html`, que muestra "✅ Pago confirmado", el botón de
   descarga y tu licencia.
4. Podés revisar cada pago en el panel de MercadoPago (**Actividad**) y, si
   configuraste `LICENSE_SECRET`, la licencia queda asociada al `payment_id`.

## Notas de seguridad

- El pago **nunca** se da por bueno solo por volver a `pago.html` con
  parámetros en la URL: `api/verify-payment.js` siempre re-consulta el
  estado real del pago contra la API de MercadoPago con tu Access Token
  antes de mostrar la descarga o emitir licencia.
- El Access Token y `LICENSE_SECRET` viven **solo** como variables de
  entorno del servidor en Vercel — nunca se envían al navegador, nunca se
  commitean al repo.
- Las licencias se firman con HMAC-SHA256 y se validan con comparación de
  tiempo constante (`crypto.timingSafeEqual`) para evitar timing attacks.
