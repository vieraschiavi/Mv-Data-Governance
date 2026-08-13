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

// Favicon embebido como data URI y no como archivo: el navegador pide
// /favicon.ico SIEMPRE, y sin esto quedaba un 404 en la consola en cada
// arranque. En un programa que se vende, un error en la consola es una
// pregunta incómoda esperando a que alguien abra las herramientas de
// desarrollo. Escudo en ámbar sobre el navy de la marca.
const FAVICON =
  "data:image/svg+xml," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' +
    '<rect width="32" height="32" rx="7" fill="#081527"/>' +
    '<path d="M16 5l9 3.4v6.9c0 5.6-3.8 10.3-9 11.7-5.2-1.4-9-6.1-9-11.7V8.4L16 5z" ' +
    'fill="none" stroke="#f2b441" stroke-width="2.2" stroke-linejoin="round"/>' +
    '<path d="M11.5 16.2l3.2 3.2 6-6.4" fill="none" stroke="#f2b441" ' +
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>');

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
<link rel="icon" href="${FAVICON}">
<title>MV Data Governance</title>
<style>${css}</style>
</head>
<body><div id="root"></div><script src="ui.js"></script></body>
</html>
`);
console.log("ui/dist listo (React empaquetado, sin CDN)");
