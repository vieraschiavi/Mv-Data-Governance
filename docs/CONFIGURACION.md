# Configuración de producción — MV Data Governance

**Este archivo NO contiene ningún secreto.** Solo los *nombres* de las
variables, de dónde sale el valor de cada una, y qué se rompe si falta.

Para saber en cualquier momento qué está configurado y qué falta, sin exponer
ningún valor:

```
https://<tu-dominio>/api/estado
```

---

## Por qué los valores no viven en el repositorio

Este repositorio es **público**. Un valor real commiteado queda publicado en
ese momento y en el historial de git para siempre, aunque después se borre.

| Si se filtra | Consecuencia |
|---|---|
| `MP_ACCESS_TOKEN` | Cualquiera cobra en tu cuenta de MercadoPago. |
| `LICENSE_PRIVATE_KEY` | Cualquiera se emite licencias infinitas del producto. Las que ya vendiste dejan de significar algo: no hay forma de revocarlas sin rotar el par y romperle la licencia a cada cliente que pagó. |
| `licencia_owner.txt` | Se publica la versión full desbloqueada para cualquiera que clone. |

Por eso `.gitignore` bloquea `.env`, `*.pem`, `*.key`, `licencia_owner.txt` y
`clave_privada_licencias.txt`. **Eso no es prolijidad: es lo único que separa
un producto que se vende de uno que se regala.**

Los valores reales van solo en estos tres lugares:

| Dónde | Qué va | Cómo |
|---|---|---|
| **Vercel** | Todo lo del circuito de cobro y entrega | Project → Settings → Environment Variables, alcance *Production*. **Redesplegar** después. |
| **GitHub** | Lo que usan los workflows | Settings → Secrets and variables → Actions |
| **Tu PC** | Para correr local | Un archivo `.env` (ya ignorado por git) |

> Si algún valor ya se commiteó alguna vez: **rotarlo**, no solo borrarlo del
> archivo. Sigue en el historial.

---

## 1. Vercel — lo imprescindible para vender

Sin estas cuatro, el circuito comercial no está completo. `/api/estado` las
marca como críticas y responde `listo_para_vender: false` mientras falte una.

| Variable | De dónde sale | Si falta |
|---|---|---|
| `MP_ACCESS_TOKEN` | MercadoPago → Tus integraciones → **Credenciales de producción** → Access Token | No se cobra de verdad: el checkout cae al link fijo de respaldo o responde 503. Nunca muestra un checkout falso. |
| `LICENSE_PRIVATE_KEY` | `python packaging/licencias.py keygen` | El cliente paga y **no recibe licencia utilizable**. Falla cerrado (nunca entrega una rota), pero la venta queda a medias. |
| `MVDG_INSTALLER_URL` | URL `https://` donde alojes el instalador del cliente | Nadie puede bajar el instalador: `/api/descargar` responde 503 diciendo qué falta. |
| `RESEND_API_KEY` | resend.com/api-keys → Create API Key (*Sending access*) | No llegan los pedidos de demo ni los avisos de "alguien apretó Comprar". La compra en sí sigue funcionando. |

### Recomendadas

| Variable | De dónde sale | Si falta |
|---|---|---|
| `KV_REST_API_URL` + `KV_REST_API_TOKEN` | Vercel → Storage → KV (o Upstash) | No se registran los pagos ya usados: dentro de la ventana de 30 min un `payment_id` filtrado puede reusarse. Se degrada, no se rompe. |
| `LICENSE_SECRET` | `openssl rand -hex 32` | No se emite la licencia MVDG1 (formato viejo). La MVDG2 —la que el programa valida— sale igual. |
| `MVDG_ESTADO_TOKEN` | Lo inventás vos: cadena larga | `/api/estado` queda **abierto al público**. Con esta variable, exige `?t=<token>`. |
| `MVDG_INSTALLER_URL_OWNER` | Ídem `MVDG_INSTALLER_URL`, edición owner | No se puede bajar el instalador owner. No afecta a clientes. |
| `MVDG_SITE_HOST` | Tu dominio propio | Sin efecto con el dominio de Vercel: el comprador vuelve al canónico. |
| `MVDG_MAIL_TO` / `MVDG_MAIL_FROM` | Tu casilla / dominio verificado en Resend | Usa los valores por defecto. Con el `from` por defecto (`onboarding@resend.dev`) **no** podés acusarle recibo al que pidió la demo. |
| `MP_CURRENCY` | — | Usa `USD`, que es lo que muestran los precios de la landing. |
| `MP_LINK_LICENCIA`, `MP_LINK_PRO` | Links de pago fijos de MercadoPago | Solo se usan si **no** hay `MP_ACCESS_TOKEN`. |

---

## 2. GitHub Actions — secrets

| Secret | Para qué | Si falta |
|---|---|---|
| `LICENSE_PRIVATE_KEY` | La misma de Vercel. La usa el workflow **Emitir licencia** para firmar licencias de prueba y de venta desde la pestaña Actions. | No podés emitir licencias a mano. |
| `MVDG_OWNER_TOKEN` | El token MVDG2 plan `owner` **atado a tu máquina**, que hace que el instalador owner abra ya desbloqueado. Se genera con `python packaging/owner_setup.py`. | El instalador owner no se construye, y el workflow avisa por qué (no falla en silencio). |
| `MP_ACCESS_TOKEN` | La misma de Vercel. La usa el workflow **Monitor** para reportar cuánto entró. | El monitor no reporta ventas. |

---

## 3. El programa en la PC del cliente — todo opcional

Nada de esto hace falta para vender: el programa anda sin configurar nada.

| Variable | Por defecto |
|---|---|
| `MVDG_API_PORT` / `MVDG_API_HOST` | `8600` / `127.0.0.1` |
| `MVDG_API_TOKEN` | Vacío. **Obligatoria si publicás la API fuera de `127.0.0.1`**: sin ella el arranque se corta (falla cerrado) en vez de exponer el catálogo sin login. |
| `MVDG_API_CORS_ORIGINS` | Solo la app local |
| `MVDG_API_RATE_LIMIT` | `240` req/min por IP (`0` = desactivado) |
| `MVDG_DATA_DIR` | `~/.mv_data_governance` |
| `MVDG_MAX_UPLOAD_MB` | `2048` MB por archivo en `/api/perfilar`. **`0` = sin tope**, y ahí el único límite es la RAM de la máquina. Conviene bajarlo si publicás la API fuera de `127.0.0.1`: sin tope, una sola petición basta para voltear el proceso. |
| `MVDG_MAX_UPLOAD_DE_MB` | `4096` MB para el conjunto de archivos de Ingeniería de datos (entran varios a la vez). `0` = sin tope. |
| `MVDG_MAX_FILAS` | `0` = leer el archivo entero. Con un número, se leen las primeras N filas **y la respuesta lo avisa** (`truncado: true`). Antes esto valía 200.000 fijo y truncaba en silencio. |
| `STREAMLIT_SERVER_MAX_UPLOAD_SIZE` | `5000` MB (definido en `.streamlit/config.toml`). Es el tope del dashboard; el corte es del servidor, así que el archivo se sube entero antes de rechazarse. |
| `MVDG_SERVER_PASSWORD` | Vacío. Si se define, exige login antes del dashboard. |
| `MVDG_LICENCIAS_URL` | El emisor embebido en `mvdg/licensing.py` |
| `MVDG_AI_PROVIDER` / `MVDG_AI_BASE_URL` | IA externa apagada. **La API key de IA no es una variable de entorno**: se guarda en el keyring del sistema operativo desde la pestaña Ayuda, con la cuenta del propio cliente. |

---

## 4. Conectores empresariales — apagados por defecto, a propósito

Estas credenciales son **del cliente**, no tuyas: se cargan en la instalación
de cada empresa, nunca en este repo ni en Vercel. Sin ellas los conectores
quedan en modo previsualización (se ve exactamente qué se enviaría, no se
envía nada), que es el comportamiento correcto.

| Conector | Variables |
|---|---|
| Power BI / Fabric | `POWERBI_CLIENT_ID`, `POWERBI_CLIENT_SECRET`, `POWERBI_TENANT_ID` |
| Tableau | `TABLEAU_SERVER_URL`, `TABLEAU_SITE`, `TABLEAU_TOKEN_NAME`, `TABLEAU_TOKEN_SECRET` |
| Microsoft Purview | `PURVIEW_TENANT_ID`, `PURVIEW_CLIENT_ID`, `PURVIEW_CLIENT_SECRET`, `PURVIEW_ACCOUNT_NAME` |
| Collibra | `COLLIBRA_BASE_URL`, `COLLIBRA_USERNAME`, `COLLIBRA_PASSWORD`, `COLLIBRA_DOMAIN_ID`, `COLLIBRA_TABLE_TYPE_ID`, `COLLIBRA_COLUMN_TYPE_ID`, `COLLIBRA_TERM_TYPE_ID`, `COLLIBRA_COLUMN_TABLE_RELATION_TYPE_ID`, `COLLIBRA_CANDIDATE_STATUS_ID`, `COLLIBRA_ACCEPTED_STATUS_ID` |
| Azure Resource Graph | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SUBSCRIPTION_ID` |
| Etiquetas MIP | `MIP_TENANT_ID`, `MIP_CLIENT_ID`, `MIP_CLIENT_SECRET` |

---

## 5. Orden de puesta en marcha

1. **Generar el par de licencias** (una sola vez):
   ```bash
   python packaging/licencias.py keygen
   ```
   Pegá la **pública** en `PUBLIC_KEY_B64` de `mvdg/licensing.py` y guardá la
   **privada** como `LICENSE_PRIVATE_KEY` en Vercel **y** en GitHub Actions.
   Sin este paso ninguna licencia valida — ni la de un cliente ni la tuya.
   Falla cerrado, a propósito.

2. **Cargar las 4 críticas en Vercel** (tabla de arriba) y **redesplegar**.

3. **Verificar** que quedó bien, sin adivinar:
   ```
   https://<tu-dominio>/api/estado
   ```
   Tiene que responder `"listo_para_vender": true`. Si no, la respuesta dice
   exactamente qué variable falta y qué se rompe por eso.

4. **Cerrar el diagnóstico**: definí `MVDG_ESTADO_TOKEN` y volvé a
   desplegar. A partir de ahí `/api/estado` exige `?t=<token>`.

5. **Alojar el instalador** y poner su URL en `MVDG_INSTALLER_URL`.

6. **Probar el circuito completo** con una compra real de prueba: comprar →
   `/pago.html` verifica el pago contra MercadoPago del lado del servidor →
   emite la licencia firmada → aparece el botón de descarga.

---

## 6. Los errores que salen más caro

1. **Cargar las variables y no redesplegar.** Vercel toma las variables en el
   build: hasta que no redesplegás, producción sigue con las viejas.
2. **Usar credenciales de prueba de MercadoPago en producción.** Cobra en la
   cuenta de test y el dinero no existe.
3. **Perder `LICENSE_PRIVATE_KEY`.** No se puede regenerar: hay que crear un
   par nuevo, y eso invalida todas las licencias ya vendidas.
4. **Commitear un valor real "por un momento".** Queda en el historial de git
   para siempre. Rotarlo, no borrarlo.
5. **Cambiar los precios en un solo lado.** La fuente de verdad es `PLANS` en
   `api/checkout.js`; lo que se muestra está en `landing/payments-config.js`.
   Si no coinciden, la landing anuncia un precio y el checkout cobra otro.
