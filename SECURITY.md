# Seguridad — MV Data Governance

## Reportar una vulnerabilidad

Escribí a **vieraschiavi@gmail.com** con el asunto `[SECURITY] MV Data Governance`.
No abras un issue público para vulnerabilidades sin parchear.

## Dependencias de terceros — estado y CVEs conocidos

El repo no vendoriza librerías de terceros (no hay carpetas `vendor/` ni
copias de código ajeno pegadas a mano — `electron/lib/` es código propio, no
vendorizado, ver su cabecera). Todas las dependencias son gestionadas por
`pip` (`requirements.txt`/`requirements-dev.txt`) o `npm`
(`electron/package.json`), con versión declarada — nada instalado "a ojo"
sin quedar registrado en un archivo de lockfile/requirements.

La landing (`landing/*.html`) no carga **ninguna** librería JS de terceros
(sin jQuery, sin Leaflet, sin librerías de gráficos): es HTML/CSS/JS propio,
sin `<script src="https://cdn...">` de ningún framework — el único recurso
externo es el video de respaldo servido desde jsDelivr (contenido estático,
no código).

### Auditoría de `electron/` (`npm audit`, revisada a mano)

| Paquete | Uso | Estado |
|---|---|---|
| `electron-builder` | empaquetado del `.exe`/AppImage (`npm run dist-win`/`dist-linux`) — **nunca corre en la app instalada**, solo en la máquina de quien compila | Actualizado `^25.0.0` → `^26.15.3`: sacaba la cadena crítica de `node-tar` (varios GHSA, arbitrary file overwrite vía hardlink/symlink). Verificado: `npm audit` da 0 en esta cadena tras el bump, y `npm run build-launcher` + el test existente (`node lib/server-manager.test.js`) siguen pasando. |
| `esbuild` | empaqueta el launcher React (`scripts/build-launcher.mjs`), modo **build** de una sola pasada, nunca modo `serve` | Actualizado `^0.24.0` → `^0.28.1`: sacaba un CVE moderado (el dev-server de esbuild acepta requests de cualquier origen) que de todos modos no aplicaba a este uso (no se usa el dev-server). Verificado con un build real tras el bump. |
| `electron` | runtime de la app de escritorio — **este sí corre en la máquina del usuario final** | **`^33.0.0`, sin actualizar.** `npm audit` reporta **2 vulnerabilidades altas**: las de `electron` (ASAR integrity bypass, spoof de respuestas IPC de service worker, origen incorrecto en el permission handler de iframes, y varias de DevTools) y una de `extract-zip` (path traversal por symlink). El fix disponible es `electron@43.x`: un salto de **10 versiones mayores** con cambios de API, que no es seguro aplicar a ciegas sin poder probar la app empaquetada de punta a punta (Electron necesita entorno gráfico; este repo se audita headless). Dentro de `^33` ya se está en la última (`33.4.11`), así que **no hay parche que aplicar sin el salto mayor**. **Queda declarado acá a propósito, no escondido**: la próxima vez que se toque `electron/`, evaluar el bump en una máquina con GUI. |
| `extract-zip` | **NO viaja en la app instalada.** Entra como dependencia del paquete npm `electron`, que solo se usa para bajar el binario al compilar. Verificado: `npm ls extract-zip` lo muestra colgando de `electron` (devDependency), y el `files` de electron-builder empaqueta únicamente `main.js`, `preload.js`, `launcher/dist`, `ui/dist` y `lib/` — ningún `node_modules`. El riesgo es para quien compila, no para quien instala. |

Reproducir la auditoría: `cd electron && npm install && npm audit`.

### Motor Python (`requirements.txt`)

Sin drivers de base de datos vendorizados: cada motor (`psycopg2-binary`,
`pymysql`, `pyodbc`, `oracledb`) es opcional y lo instala quien lo necesita,
declarado en `requirements.txt` con el comentario correspondiente. `mcp`
está fijado por debajo de `2.0` a propósito — ver el comentario en
`requirements.txt` y `tests/test_core.py::test_mcp_pinneado_por_debajo_de_2`.
