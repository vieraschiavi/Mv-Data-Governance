// Empaqueta el launcher React (esbuild) -> launcher/dist/ (autocontenido,
// sin CDN: React queda adentro del bundle — nada se baja de internet).
import { build } from "esbuild";
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, "..", "launcher", "dist");
mkdirSync(out, { recursive: true });

await build({
  entryPoints: [join(here, "..", "launcher", "src", "index.jsx")],
  bundle: true,
  minify: true,
  outfile: join(out, "launcher.js"),
  loader: { ".jsx": "jsx" },
  jsx: "automatic",
  target: ["chrome120"],
});

const css = readFileSync(join(here, "..", "launcher", "src", "styles.css"), "utf8");
writeFileSync(join(out, "index.html"), `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'unsafe-inline'; script-src 'self'">
<title>MV Data Governance</title>
<style>${css}</style>
</head>
<body><div id="root"></div><script src="launcher.js"></script></body>
</html>
`);
console.log("launcher/dist listo (React empaquetado, sin CDN)");
