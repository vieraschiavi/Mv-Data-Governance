// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
// Empaqueta la interfaz de escritorio (React) -> ui/dist/.
//
// Autocontenido: React queda DENTRO del bundle, nada se baja de internet.
// Eso no es una preferencia de estilo — el programa promete funcionar sin
// conexión, y un <script src="https://…"> lo rompería en la primera PC sin
// internet, que es justo el caso de muchos clientes corporativos.
import { build } from "esbuild";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const aqui = dirname(fileURLToPath(import.meta.url));
const salida = join(aqui, "..", "ui", "dist");
mkdirSync(salida, { recursive: true });

await build({
  entryPoints: [join(aqui, "..", "ui", "src", "index.jsx")],
  bundle: true,
  minify: true,
  outfile: join(salida, "ui.js"),
  loader: { ".jsx": "jsx" },
  jsx: "automatic",
  target: ["chrome120"],
  define: { "process.env.NODE_ENV": '"production"' },
});

const css = readFileSync(join(aqui, "..", "ui", "src", "styles.css"), "utf8");

// La MARCA, embebida como data URI desde el PNG de assets/brand.
//
// Se lee el archivo en tiempo de build a proposito: asi el .png sigue siendo
// la unica fuente de verdad. Si se cambia el logo, cambia en la web y en el
// programa sin tocar codigo — que es lo contrario a pegar un base64 a mano y
// que quede desactualizado sin que nadie lo note.
//
// Y va embebido y no como archivo suelto porque el navegador pide
// /favicon.ico SIEMPRE: sin esto quedaba un 404 en la consola en cada
// arranque, y en un programa que se vende un error en consola es una
// pregunta incomoda esperando a que alguien abra las herramientas.
//
// Antes habia acá un escudo ambar dibujado en SVG: no era el logo de la
// marca. El de la landing y el del .exe tienen que ser el MISMO.
const LOGO = "data:image/png;base64," + readFileSync(
  join(aqui, "..", "..", "assets", "brand", "mv_icon_64.png")).toString("base64");

// CSP estricta: sin 'unsafe-eval' y sin orígenes externos. connect-src queda
// en 'self' porque la UI la sirve el MISMO servidor que la API — si algún día
// se abriera desde otro origen habría que ampliarlo a mano, y que haya que
// hacerlo a mano es la idea.
writeFileSync(join(salida, "index.html"), `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; connect-src 'self'; style-src 'unsafe-inline'; script-src 'self'; img-src 'self' data:">
<link rel="icon" href="${LOGO}">
<title>MV Data Governance</title>
<style>:root{--mv-logo:url("${LOGO}")}\n${css}</style>
</head>
<body><div id="root"></div><script src="ui.js"></script></body>
</html>
`);
console.log("ui/dist listo (React empaquetado, sin CDN)");
