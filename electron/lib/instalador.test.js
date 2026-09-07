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

// ------------------------------ las DOS formas de instalar, bien separadas
//
// Instalacion normal (mi laptop, o la de la consultora que me contrata) y
// paquete portable para la VM del cliente. La segunda no puede salir de un
// instalador: en una VM corporativa no hay permisos de administrador y el
// perfil de usuario se puede resetear al cerrar sesion. Son dos targets
// distintos del MISMO build — mismo binario, misma auditoria.
// El paquete portable NO es otro target de electron-builder: se rearma desde
// `dist_electron/win-unpacked` en el workflow, agregandole el marcador. Un
// target `zip` daria un segundo ZIP de ~400 MB sin el marcador adentro — o
// sea, el paquete equivocado, pesando el doble. Que el workflow lo arme
// bien lo verifica un test de Python sobre el YAML.
check("NSIS: instalacion por USUARIO, sin pedir administrador", () => {
  // perMachine true exige elevacion. En la laptop de una consultora eso ya
  // es incomodo; en la VM de un cliente, directamente no se puede.
  assert.strictEqual(nsis.perMachine, false,
    "perMachine tiene que ser false: instalar por maquina pide admin y en " +
    "un equipo corporativo el consultor no lo tiene");
});

check("el shell y el motor llaman igual al marcador del modo VM", () => {
  const fs = require("node:fs");
  const sm = require("./server-manager");
  const py = fs.readFileSync(
    path.join(__dirname, "..", "..", "mvdg", "install_mode.py"), "utf8");
  const m = py.match(/^MARCADOR\s*=\s*"([^"]+)"/m);
  assert.ok(m, "no se encontro MARCADOR en mvdg/install_mode.py");
  assert.strictEqual(sm.MARCADOR_VM, m[1],
    `el shell busca "${sm.MARCADOR_VM}" y el motor "${m[1]}": con nombres ` +
    `distintos quedan en modos distintos y el usuario ve una sola mitad`);
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

// -------------------------------------- el script NSIS que propone el disco
//
// Tres formas distintas de que esto no haga NADA sin que nadie se entere, y
// las tres son silenciosas: que el archivo no exista, que no llegue al repo
// (estaba en electron/build/, y "build/" esta en .gitignore — el .exe habria
// fallado por octava vez), o que el macro se llame distinto de "preInit", que
// es el unico nombre que electron-builder invoca.
{
  const fs = require("node:fs");
  const { execFileSync } = require("node:child_process");
  const incluido = nsis.include;

  check("NSIS: hay script propio para proponer la carpeta", () => {
    assert.ok(incluido, "falta nsis.include");
  });

  const ruta = path.join(__dirname, "..", incluido);

  check("NSIS: el script incluido existe en disco", () => {
    assert.ok(fs.existsSync(ruta), `no existe ${incluido}`);
  });

  check("NSIS: el script NO esta ignorado por git", () => {
    // git check-ignore sale 0 si el archivo ESTA ignorado.
    let ignorado = false;
    try {
      execFileSync("git", ["check-ignore", "-q", ruta], { stdio: "ignore" });
      ignorado = true;
    } catch { ignorado = false; }
    assert.strictEqual(ignorado, false,
      `${incluido} esta en .gitignore: no llega al runner y el build falla`);
  });

  const nsh = fs.readFileSync(ruta, "utf8");

  check("NSIS: define el macro preInit (el unico que electron-builder llama)",
    () => {
      assert.match(nsh, /!macro\s+preInit\b/,
        "sin un macro llamado exactamente preInit, el script se compila y no hace nada");
    });

  // Se miran solo las lineas de CODIGO. Buscar sobre el archivo crudo daba
  // verde con las lecturas comentadas: el texto "ReadRegStr" seguia estando
  // adentro del comentario. Verificado — el test pasaba sobre el bug.
  const codigo = nsh
    .split("\n")
    .map((l) => l.replace(/^\s*[;#].*$/, ""))
    .join("\n");

  check("NSIS: no pisa la carpeta de una instalacion que ya existe", () => {
    // En una actualizacion, reescribir InstallLocation mandaria la version
    // nueva a otro disco y dejaria la vieja colgada. Tiene que LEER primero.
    const iLee = codigo.indexOf("ReadRegStr");
    const iEscribe = codigo.indexOf("WriteRegExpandStr");
    assert.ok(iLee !== -1, "no lee InstallLocation antes de escribir");
    assert.ok(iEscribe !== -1, "no escribe InstallLocation en ningun lado");
    assert.ok(iLee < iEscribe,
      "escribe InstallLocation antes de leer si ya habia una instalacion");
  });

  // Compilar de verdad, si hay makensis. Un error de sintaxis en el .nsh
  // rompe el build del instalador entero, y eso solo se ve en el runner.
  let makensis = true;
  try { execFileSync("makensis", ["-VERSION"], { stdio: "ignore" }); }
  catch { makensis = false; }

  if (makensis) {
    check("NSIS: el script COMPILA (makensis)", () => {
      const os = require("node:os");
      const tmp = path.join(os.tmpdir(), "mvdg_nsis_check.nsi");
      // Arnes minimo con lo que el .nsh espera del entorno de electron-builder.
      fs.writeFileSync(tmp, [
        `!define INSTALL_REGISTRY_KEY "Software\\mvdg-check"`,
        `OutFile "${path.join(os.tmpdir(), "mvdg_nsis_check.exe")}"`,
        `InstallDir "$LOCALAPPDATA\\Programs\\MV Data Governance"`,
        `!include "${ruta}"`,
        `Function .onInit`,
        `  !insertmacro preInit`,
        `FunctionEnd`,
        `Section "x"`,
        `SectionEnd`,
      ].join("\n"));
      execFileSync("makensis", [tmp], { stdio: "pipe" });
    });
  } else {
    console.log("· makensis no esta instalado: no se compila el .nsh (PARCIAL)");
  }
}

console.log(`\nTodos los checks del instalador pasaron (${checks}).`);
