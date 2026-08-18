// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Invariantes del instalador de Windows, verificables con Node puro.
 *     node lib/instalador.test.js
 *
 * Por qué existe
 * -------------
 * El instalador se compila en un runner Windows: ni NSIS ni la ventana de
 * Electron se pueden ejecutar en Linux ni en CI de Linux. Eso dejaba dos
 * clases de error que solo aparecían DESPUÉS de bajar el .exe y probarlo a
 * mano — y las dos pasaron de verdad:
 *
 *   1. El build fallo 7 veces seguidas con "No module named 'mvdg'". El
 *      Python embebido se armaba en "build/pyembed" (dos niveles bajo la
 *      raiz) pero su ._pth agrega "..", que se resuelve contra la carpeta
 *      del ._pth. Dos niveles abajo, ".." daba "<repo>/build", que no tiene
 *      el motor. Nunca hubo instalador de Electron.
 *
 *   2. "No me deja elegir el directorio." electron-builder IGNORA
 *      allowToChangeInstallationDirectory cuando oneClick es true, y no
 *      avisa: sale un instalador de un solo clic que va derecho a C:.
 *
 * Las dos son configuracion, no codigo — asi que se pueden verificar sin
 * Windows. Es lo unico de la cadena del instalador que este entorno puede
 * probar, y es justo donde estaban los errores.
 */
const assert = require("node:assert");
const path = require("node:path");
const pkg = require("../package.json");

let checks = 0;
function check(desc, fn) { fn(); checks++; console.log("✓ " + desc); }

const build = pkg.build || {};
const nsis = build.nsis || {};
const recursos = build.extraResources || [];

// ------------------------------------------------- elegir carpeta y disco
check("NSIS: oneClick es false — sin esto NO hay pantalla de carpeta", () => {
  // Es la condicion previa: con oneClick true, electron-builder ignora
  // allowToChangeInstallationDirectory sin emitir ninguna advertencia.
  assert.strictEqual(nsis.oneClick, false,
    "oneClick tiene que ser false o el instalador va derecho a C: sin preguntar");
});

check("NSIS: se puede cambiar la carpeta de instalacion", () => {
  assert.strictEqual(nsis.allowToChangeInstallationDirectory, true);
});

check("NSIS: deja desinstalador con nombre propio", () => {
  assert.ok(nsis.uninstallDisplayName,
    "sin uninstallDisplayName la entrada de 'Agregar o quitar programas' queda con el nombre interno");
});

check("NSIS: accesos directos en escritorio y menu Inicio", () => {
  assert.strictEqual(nsis.createDesktopShortcut, true);
  assert.strictEqual(nsis.createStartMenuShortcut, true);
});

// --------------------------------------- el motor, UN nivel sobre python
//
// El ._pth del Python embebido lleva ".." y eso se resuelve contra la
// carpeta del ._pth. O sea: el motor tiene que quedar exactamente un nivel
// arriba del python.exe, en el build Y ya instalado. Si alguien mueve
// cualquiera de los dos, el sintoma es un ModuleNotFoundError en el runner
// —o peor, un .exe que instala bien y no abre.
function destino(sufijo) {
  const e = recursos.find((r) => r.to && r.to.replace(/\\/g, "/").endsWith(sufijo));
  assert.ok(e, `falta el extraResources que copia a .../${sufijo}`);
  return e;
}

check("layout: el motor y el python embebido caen en la misma carpeta", () => {
  const py = destino("python");
  const motor = destino("mvdg");
  const api = destino("bi_api");
  const dir = (r) => path.posix.dirname(r.to.replace(/\\/g, "/"));
  assert.strictEqual(dir(py), dir(motor),
    `python va a ${py.to} y mvdg a ${motor.to}: '..' no daria con el motor`);
  assert.strictEqual(dir(py), dir(api));
});

check("layout: en el BUILD el python queda al lado del motor, no mas abajo",
  () => {
    // "../pyembed" -> el padre del python es la raiz del repo, que tiene el
    // motor. "../build/pyembed" -> el padre es <repo>/build, que no lo tiene:
    // ese fue el bug que rompio el build 7 veces.
    const py = destino("python");
    const desde = py.from.replace(/\\/g, "/");
    assert.match(desde, /^\.\.\/[^/]+$/,
      `extraResources.from = "${desde}": tiene que ser "../<carpeta>" (un solo ` +
      `nivel bajo la raiz) para que el ".." del ._pth de con el motor`);
  });

console.log(`\nTodos los checks del instalador pasaron (${checks}).`);
