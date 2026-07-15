# 🖥️ MV Data Governance · shell de escritorio (Electron + React)

Envuelve el programa (Streamlit) en una ventana de escritorio nativa, con
un launcher React mientras arranca. **No reemplaza** a la Opción A
(instalador PyInstaller) ni a la Opción B (portable `.bat`) — es una
**tercera forma de empaquetar el mismo programa** para clientes que
prefieren un instalador `.exe` de aspecto más "app de escritorio" (ícono en
el menú inicio, ventana propia sin barra de navegador) en vez de un `.exe`
generado por PyInstaller o un `.bat` que abre el navegador.

**Cómo funciona:** al abrir la app, Electron busca un puerto libre en
`127.0.0.1`, levanta `streamlit run app/app.py` con Python (del sistema o
de un `.venv` empaquetado), muestra un launcher (React) mientras el
servidor arranca, y cuando responde carga el programa en la misma ventana.
Al cerrar la ventana, mata el proceso de Streamlit. **Nada sale a
internet** — mismo principio que el resto del producto.

```
electron/
├── main.js                    ← proceso principal de Electron
├── preload.js                 ← puente aislado (solo estado + reintentar)
├── lib/
│   ├── server-manager.js      ← arranque del servidor (SIN depender de Electron)
│   └── server-manager.test.js ← test end-to-end con Node puro (ver abajo)
├── launcher/
│   ├── src/App.jsx            ← launcher React (ES/EN/PT)
│   └── fallback.html          ← se usa si no se corrió build-launcher
├── scripts/build-launcher.mjs ← empaqueta React con esbuild (sin CDN)
└── package.json                ← electron-builder (NSIS Windows + AppImage Linux)
```

## Qué se verificó en este entorno de desarrollo (Linux, sin GUI)

Este entorno no tiene pantalla ni permite bajar el binario de Electron
(~200 MB, requiere red sin restricciones), así que **la ventana de
Electron en sí no se abrió acá**. Lo que SÍ se separó y verificó de forma
real:

- **`lib/server-manager.js`** — toda la lógica de arranque (elegir puerto
  libre, encontrar un Python que tenga Streamlit, lanzar
  `streamlit run`, hacer polling hasta que responda, matar el proceso) se
  escribió **sin importar `electron`**, específicamente para poder
  testearla con Node puro.
- **`lib/server-manager.test.js`** corre con `node lib/server-manager.test.js`
  (sin Electron) y hace un end-to-end real: levanta un Streamlit de
  verdad contra `app/app.py` de este repo, confirma que `waitForServer()`
  lo detecta arriba, lo mata, y confirma que un puerto sin nadie
  escuchando da timeout correctamente. **Se corrió y pasó** en este
  entorno.
- El launcher React se compiló de verdad con `npm run build-launcher`
  (esbuild) → `launcher/dist/index.html` + `launcher.js` autocontenido,
  sin CDN.
- `node --check` confirma que `main.js`, `preload.js` y el resto de los
  scripts no tienen errores de sintaxis.

## Qué NO se verificó (requiere Windows / una GUI)

- Abrir la ventana de Electron de verdad (`npm start`) — no probado acá.
- Construir el instalador `.exe` (`npm run dist-win`, vía
  `electron-builder` con NSIS) — requiere Windows o Wine; no se construyó
  en este entorno.
- El ícono, el título de ventana y el comportamiento de "instancia única"
  en Windows real.

**Antes de entregar este empaquetado a un cliente**, un desarrollador con
Windows debe correr `npm install && npm start` para confirmar la ventana,
y `npm run dist-win` para generar y probar el instalador.

## Uso

```bash
cd electron
npm install
npm run build-launcher   # empaqueta el launcher React (solo hace falta 1 vez, o tras editar App.jsx)
npm start                 # abre la ventana (requiere Python + streamlit instalado o un .venv)
npm run dist-win           # genera el instalador .exe (NSIS) — requiere Windows
npm run dist-linux         # genera un AppImage — Linux
npm test                   # corre el test end-to-end de server-manager.js (sin Electron)
```

## Variables de entorno

| Variable | Para qué |
|---|---|
| `MVDG_SERVER_CMD` | Comando alternativo para levantar el servidor (reemplaza `{port}` por el puerto elegido). Útil si empaquetás un Python embebido con otro layout. |

## Diseño: por qué `server-manager.js` está separado de `main.js`

`main.js` solo puede importarse dentro de un proceso Electron (usa
`require("electron")` en el primer renglón), lo que hace imposible
testearlo con Node puro fuera de ese runtime. Toda la lógica que SÍ se
puede probar sin Electron —elegir puerto, encontrar Python, lanzar
Streamlit, hacer polling— vive en `lib/server-manager.js`, que no importa
`electron` en ningún lado. `main.js` es una capa fina que conecta esa
lógica con las APIs de ventana de Electron (`BrowserWindow`, `ipcMain`).
