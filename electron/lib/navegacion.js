// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · política de navegación de la ventana de escritorio.
 *
 * Por qué vive acá y no dentro de main.js
 * ---------------------------------------
 * main.js necesita Electron para correr, y Electron necesita una pantalla:
 * en un servidor de CI (o en este entorno Linux headless) no se puede
 * ejecutar. Una regla de seguridad que no se puede correr en los tests es
 * una regla que nadie verifica — se escribe una vez, alguien la toca seis
 * meses después y nadie se entera. Extraída acá es Node puro y se prueba
 * como cualquier otra función.
 *
 * Es el mismo criterio que ya se usó con server-manager.js.
 *
 * Qué decide
 * ----------
 * contextIsolation y nodeIntegration protegen el puente entre la página y
 * Node, pero no impiden que la ventana NAVEGUE a otro sitio. Sin esto, un
 * window.open o un enlace externo se abre dentro de la app: con el chrome de
 * la aplicación y sin barra de direcciones, o sea sin que el usuario pueda
 * ver dónde está parado. Es un punto explícito del checklist de seguridad de
 * Electron.
 *
 * La interfaz propia se sirve desde http://127.0.0.1:<puerto>/app (la API) y
 * el launcher desde file://. Todo lo demás es ajeno.
 */

/** ¿Esta URL es la interfaz propia (API local o launcher empaquetado)? */
function esPropia(url) {
  let u;
  try {
    u = new URL(String(url));
  } catch {
    return false;
  }
  // El launcher se carga con loadFile() -> file://. Electron no dispara
  // will-navigate para loadFile/loadURL, pero si algún día lo hiciera (o si
  // el launcher navegara internamente), no se puede romper el arranque.
  if (u.protocol === "file:") return true;
  if (u.protocol !== "http:" && u.protocol !== "https:") return false;
  return u.hostname === "127.0.0.1" || u.hostname === "localhost";
}

/**
 * Qué hacer cuando la página intenta NAVEGAR a `url`.
 * "permitir" | "bloquear"
 */
function alNavegar(url) {
  return esPropia(url) ? "permitir" : "bloquear";
}

/**
 * Qué hacer cuando la página intenta ABRIR UNA VENTANA a `url`.
 *
 * Nunca se abre una ventana de Electron: o va al navegador del sistema (donde
 * el usuario ve la URL y tiene sus propias defensas) o no va a ningún lado.
 * Un esquema que no sea http/https (file://, javascript:, un handler raro del
 * sistema) se descarta sin abrir nada.
 *
 * "externo" = abrir en el navegador del sistema y denegar la ventana.
 * "descartar" = denegar y no abrir nada.
 */
function alAbrirVentana(url) {
  return /^https?:\/\//i.test(String(url)) ? "externo" : "descartar";
}

module.exports = { esPropia, alNavegar, alAbrirVentana };
