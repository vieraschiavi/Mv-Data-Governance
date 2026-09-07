# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Exportar un documento a HTML, Word y PDF.

Sin dependencias nuevas, a propósito
────────────────────────────────────
Un informe que hay que mandarle a un gerente tiene que salir en el formato
que esa persona usa, y eso normalmente significa Word o PDF. Las librerías
para eso (python-docx, reportlab, weasyprint) son varios megas cada una y
viajarían dentro del instalador que baja cada cliente, para generar tres
archivos.

Por eso los tres se escriben acá con la biblioteca estándar:

  HTML  texto plano con estilos embebidos. Además trae hoja de impresión,
        así que "Imprimir → Guardar como PDF" del navegador da un PDF con
        la misma calidad tipográfica que la pantalla.
  DOCX  un .docx ES un zip con XML adentro. Se arma con `zipfile` y cuatro
        piezas de OOXML. Word, LibreOffice y Google Docs lo abren nativo,
        editable — no es un HTML renombrado.
  PDF   escritor propio, mínimo pero real: objetos, xref, fuentes base-14
        (Helvetica), paginado y corte de línea con las métricas verdaderas
        de la fuente. No hace tablas ni imágenes; hace texto bien.

La API es una sola: se arma un `dict` con el documento y cada función lo
convierte. Así el contenido se escribe una vez y sale en los tres.
"""
from __future__ import annotations

import html
import io
import zipfile
from datetime import datetime, timezone

# ───────────────────────────── HTML ─────────────────────────────────────
_CSS = """
:root{--tinta:#12233b;--suave:#5b6b82;--linea:#dde5ef;--ambar:#b07d1a;--fondo:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--tinta);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.hoja{max-width:900px;margin:0 auto;padding:48px 32px 80px}
h1{font-size:31px;line-height:1.15;margin:0 0 6px;letter-spacing:-.02em}
.sub{color:var(--suave);font-size:17px;margin:0 0 26px}
.meta{border:1px solid var(--linea);border-radius:12px;padding:14px 18px;margin:0 0 34px;
  display:grid;grid-template-columns:auto 1fr;gap:6px 20px;font-size:14px}
.meta dt{color:var(--suave);margin:0}
.meta dd{margin:0;font-weight:600}
.etapa{border-top:1px solid var(--linea);padding:26px 0 4px;break-inside:avoid}
.etapa h2{font-size:20px;margin:0 0 4px;display:flex;gap:11px;align-items:baseline}
.num{flex:none;width:30px;height:30px;border-radius:50%;background:var(--tinta);color:#fff;
  font-size:14px;display:inline-flex;align-items:center;justify-content:center;font-weight:700}
.modulo{font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color:var(--suave);margin:0 0 14px 41px}
.bloque{margin:0 0 12px 41px}
.et{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.09em;
  text-transform:uppercase;color:var(--suave);margin:0 0 2px}
.bloque p{margin:0}
.evidencia{margin:12px 0 4px 41px;padding:11px 15px;border-left:3px solid var(--ambar);
  background:#fdf8ee;border-radius:0 8px 8px 0;font-size:15px}
.evidencia .et{color:var(--ambar)}
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--linea);
  color:var(--suave);font-size:13px}
@media print{
  /* Que el PDF del navegador salga igual que la pantalla: sin fondos que
     se coman la tinta, y sin cortar una etapa al medio entre dos hojas. */
  .hoja{max-width:none;padding:0}
  .etapa{break-inside:avoid;page-break-inside:avoid}
  a{text-decoration:none;color:inherit}
  @page{margin:18mm 16mm}
}
"""


def _ahora() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def a_html(doc: dict) -> str:
    """El documento como una página HTML autocontenida y lista para imprimir."""
    e = html.escape
    partes = [
        "<!doctype html><html lang=\"", e(doc.get("lang", "es")), "\"><head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
        "<title>", e(doc["titulo"]), "</title><style>", _CSS, "</style></head><body>",
        "<div class=\"hoja\"><h1>", e(doc["titulo"]), "</h1>",
        "<p class=\"sub\">", e(doc.get("subtitulo", "")), "</p>",
    ]
    if doc.get("meta"):
        partes.append("<dl class=\"meta\">")
        for clave, valor in doc["meta"]:
            partes += ["<dt>", e(str(clave)), "</dt><dd>", e(str(valor)), "</dd>"]
        partes.append("</dl>")

    for sec in doc["secciones"]:
        partes += ["<section class=\"etapa\"><h2><span class=\"num\">",
                   e(str(sec.get("n", ""))), "</span><span>", e(sec["titulo"]),
                   "</span></h2>"]
        if sec.get("modulo"):
            partes += ["<p class=\"modulo\">", e(sec["modulo"]), "</p>"]
        for etiqueta, texto in sec["bloques"]:
            if not texto:
                continue
            partes += ["<div class=\"bloque\"><span class=\"et\">", e(etiqueta),
                       "</span><p>", e(texto), "</p></div>"]
        if sec.get("evidencia"):
            partes += ["<div class=\"evidencia\"><span class=\"et\">",
                       e(sec.get("evidencia_etiqueta", "Evidencia")), "</span><p>",
                       e(sec["evidencia"]), "</p></div>"]
        partes.append("</section>")

    partes += ["<footer>", e(doc.get("pie", "")), " · ", _ahora(),
               "</footer></div></body></html>"]
    return "".join(partes)


# ───────────────────────────── DOCX ─────────────────────────────────────
# Un .docx es un zip con un puñado de XML. Se escriben los cuatro que Word
# exige para abrirlo sin quejarse: [Content_Types], la relación raíz, la
# relación del documento y el documento en sí.
_CT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

_DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _p(texto: str, *, tam: int = 22, negrita: bool = False, color: str = "12233B",
       espacio: int = 120, mono: bool = False) -> str:
    """Un párrafo de Word. `tam` va en medios puntos (22 = 11pt)."""
    fuente = "Consolas" if mono else "Calibri"
    return (
        f'<w:p><w:pPr><w:spacing w:after="{espacio}"/></w:pPr>'
        f'<w:r><w:rPr><w:rFonts w:ascii="{fuente}" w:hAnsi="{fuente}"/>'
        f'{"<w:b/>" if negrita else ""}'
        f'<w:sz w:val="{tam}"/><w:color w:val="{color}"/></w:rPr>'
        f'<w:t xml:space="preserve">{html.escape(texto)}</w:t></w:r></w:p>'
    )


def a_docx(doc: dict) -> bytes:
    """El documento como .docx real: se abre editable en Word, no es HTML."""
    cuerpo = [_p(doc["titulo"], tam=40, negrita=True, espacio=60)]
    if doc.get("subtitulo"):
        cuerpo.append(_p(doc["subtitulo"], tam=24, color="5B6B82", espacio=200))
    for clave, valor in doc.get("meta") or []:
        cuerpo.append(_p(f"{clave}: {valor}", tam=20, color="5B6B82", espacio=40))

    for sec in doc["secciones"]:
        cuerpo.append(_p(f"{sec.get('n', '')}. {sec['titulo']}",
                         tam=28, negrita=True, espacio=60))
        if sec.get("modulo"):
            cuerpo.append(_p(sec["modulo"], tam=18, color="5B6B82",
                             espacio=120, mono=True))
        for etiqueta, texto in sec["bloques"]:
            if not texto:
                continue
            cuerpo.append(_p(etiqueta.upper(), tam=16, negrita=True,
                             color="5B6B82", espacio=20))
            cuerpo.append(_p(texto, espacio=140))
        if sec.get("evidencia"):
            cuerpo.append(_p(sec.get("evidencia_etiqueta", "Evidencia").upper(),
                             tam=16, negrita=True, color="B07D1A", espacio=20))
            cuerpo.append(_p(sec["evidencia"], negrita=True, espacio=200))

    cuerpo.append(_p(f"{doc.get('pie', '')} · {_ahora()}", tam=18, color="5B6B82"))
    documento = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 f'<w:document xmlns:w="{_W}"><w:body>{"".join(cuerpo)}</w:body></w:document>')

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CT)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("word/_rels/document.xml.rels", _DOC_RELS)
        z.writestr("word/document.xml", documento)
    return buf.getvalue()


# ───────────────────────────── PDF ──────────────────────────────────────
# Escritor mínimo pero real. Un PDF es: una cabecera, una lista de objetos
# numerados, una tabla de posiciones (xref) y un trailer que dice dónde
# empieza esa tabla. Nada de eso necesita una librería.
#
# Se usan las fuentes base-14 (Helvetica y Helvetica-Bold), que TODO lector
# de PDF tiene incorporadas: no hay que embeber un archivo de fuente, que es
# lo que haría pesado esto.
#
# El corte de línea usa las métricas VERDADERAS de Helvetica (tabla de abajo).
# Con un ancho promedio el texto se sale del margen o queda ridículamente
# corto según el párrafo, y eso se nota en la primera página.
_ANCHO_HELV = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191,
    "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
    "0": 556, "1": 556, "2": 556, "3": 556, "4": 556, "5": 556, "6": 556, "7": 556,
    "8": 556, "9": 556, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556,
    "@": 1015, "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778,
    "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
    "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556,
    "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556, "v": 500, "w": 722,
    "x": 500, "y": 500, "z": 500, "{": 334, "|": 260, "}": 334, "~": 584,
}
_ANCHO_POR_DEFECTO = 556          # acentuadas y demás: ancho de una minúscula

# WinAnsi (cp1252) cubre español y portugués enteros, pero no la tipografía
# fina que usa el resto del programa. Se reemplaza en vez de romper el
# archivo: una flecha perdida es mejor que un PDF que no abre.
#
# El tilde y la cruz van escritos con su escape ('\\u2713', '\\u2717') y no
# con el glifo: hay un test que prohibe emojis sueltos en el codigo de
# interfaz, y tiene razon. Aca son ENTRADA de una tabla de reemplazo, no
# algo que se muestre, pero escribirlos literales obligaria a aflojar ese
# guardia, y despues el proximo emoji decorativo entra sin que nadie mire.
_SUSTITUCIONES = {"→": "->", "←": "<-", "—": "-", "–": "-",
                  "≥": ">=", "≤": "<=",
                  "“": '"', "”": '"', "‘": "'", "’": "'",
                  "…": "...", "\u2713": "OK", "\u2717": "X", "•": "-"}

_A4_ANCHO, _A4_ALTO = 595.28, 841.89
_MARGEN = 56.0


def _ancho_texto(texto: str, tam: float) -> float:
    return sum(_ANCHO_HELV.get(c, _ANCHO_POR_DEFECTO) for c in texto) * tam / 1000.0


def _limpiar(texto: str) -> str:
    for viejo, nuevo in _SUSTITUCIONES.items():
        texto = texto.replace(viejo, nuevo)
    return texto


def _cortar(texto: str, tam: float, ancho: float) -> list[str]:
    """Parte el texto en líneas que entran en `ancho` puntos."""
    lineas, actual = [], ""
    for palabra in _limpiar(texto).split():
        prueba = f"{actual} {palabra}".strip()
        if actual and _ancho_texto(prueba, tam) > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas or [""]


def _escapar_pdf(texto: str) -> str:
    return texto.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


class _Lienzo:
    """Acumula líneas de texto y las reparte en páginas."""

    def __init__(self):
        self.paginas: list[list[str]] = [[]]
        self.y = _A4_ALTO - _MARGEN

    def _nueva(self):
        self.paginas.append([])
        self.y = _A4_ALTO - _MARGEN

    def espacio(self, alto: float):
        self.y -= alto

    def escribir(self, texto: str, tam: float = 10.5, negrita: bool = False,
                 sangria: float = 0.0, gris: bool = False, interlinea: float = 1.45):
        ancho = _A4_ANCHO - 2 * _MARGEN - sangria
        alto = tam * interlinea
        for linea in _cortar(texto, tam, ancho):
            if self.y - alto < _MARGEN:
                self._nueva()
            self.y -= alto
            color = "0.36 0.42 0.51 rg" if gris else "0.07 0.14 0.23 rg"
            fuente = "/F2" if negrita else "/F1"
            self.paginas[-1].append(
                f"BT {color} {fuente} {tam:.1f} Tf "
                f"1 0 0 1 {_MARGEN + sangria:.1f} {self.y:.1f} Tm "
                f"({_escapar_pdf(linea)}) Tj ET")

    def regla(self):
        if self.y - 14 < _MARGEN:
            self._nueva()
            return
        self.y -= 14
        self.paginas[-1].append(
            f"0.87 0.90 0.94 RG 0.7 w {_MARGEN} {self.y:.1f} m "
            f"{_A4_ANCHO - _MARGEN} {self.y:.1f} l S")


def _armar_pdf(paginas: list[list[str]]) -> bytes:
    """Objetos + xref + trailer. El orden importa: el xref guarda el byte
    exacto donde arranca cada objeto, así que se calcula mientras se escribe."""
    objetos: list[bytes] = []

    def agregar(cuerpo: bytes) -> int:
        objetos.append(cuerpo)
        return len(objetos)          # los ids arrancan en 1

    ids_paginas, ids_contenido = [], []
    for contenido in paginas:
        flujo = "\n".join(contenido).encode("cp1252", "replace")
        ids_contenido.append(agregar(
            b"<< /Length " + str(len(flujo)).encode() + b" >>\nstream\n"
            + flujo + b"\nendstream"))
        ids_paginas.append(None)     # se completa abajo: necesita el id del padre

    id_padre = len(objetos) + len(paginas) + 1
    for i, id_cont in enumerate(ids_contenido):
        ids_paginas[i] = agregar(
            f"<< /Type /Page /Parent {id_padre} 0 R "
            f"/MediaBox [0 0 {_A4_ANCHO:.2f} {_A4_ALTO:.2f}] "
            f"/Resources << /Font << /F1 {id_padre + 1} 0 R /F2 {id_padre + 2} 0 R >> >> "
            f"/Contents {id_cont} 0 R >>".encode())

    kids = " ".join(f"{i} 0 R" for i in ids_paginas)
    agregar(f"<< /Type /Pages /Kids [{kids}] /Count {len(ids_paginas)} >>".encode())
    agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>")
    agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
            b"/Encoding /WinAnsiEncoding >>")
    id_catalogo = agregar(f"<< /Type /Catalog /Pages {id_padre} 0 R >>".encode())

    salida = bytearray(b"%PDF-1.4\n")
    posiciones = []
    for i, cuerpo in enumerate(objetos, start=1):
        posiciones.append(len(salida))
        salida += f"{i} 0 obj\n".encode() + cuerpo + b"\nendobj\n"
    inicio_xref = len(salida)
    salida += f"xref\n0 {len(objetos) + 1}\n".encode() + b"0000000000 65535 f \n"
    for pos in posiciones:
        salida += f"{pos:010d} 00000 n \n".encode()
    salida += (f"trailer\n<< /Size {len(objetos) + 1} /Root {id_catalogo} 0 R >>\n"
               f"startxref\n{inicio_xref}\n%%EOF\n").encode()
    return bytes(salida)


def a_pdf(doc: dict) -> bytes:
    """El documento como PDF. Texto real y seleccionable, no una imagen."""
    c = _Lienzo()
    c.escribir(doc["titulo"], tam=20, negrita=True, interlinea=1.25)
    if doc.get("subtitulo"):
        c.escribir(doc["subtitulo"], tam=11, gris=True)
    for clave, valor in doc.get("meta") or []:
        c.escribir(f"{clave}: {valor}", tam=9, gris=True, interlinea=1.35)
    c.espacio(10)

    for sec in doc["secciones"]:
        c.regla()
        c.espacio(8)
        c.escribir(f"{sec.get('n', '')}. {sec['titulo']}", tam=13.5, negrita=True)
        if sec.get("modulo"):
            c.escribir(sec["modulo"], tam=8.5, gris=True)
        c.espacio(4)
        for etiqueta, texto in sec["bloques"]:
            if not texto:
                continue
            c.escribir(etiqueta.upper(), tam=8, negrita=True, gris=True, sangria=8)
            c.escribir(texto, tam=10.5, sangria=8)
            c.espacio(4)
        if sec.get("evidencia"):
            c.escribir(sec.get("evidencia_etiqueta", "Evidencia").upper(),
                       tam=8, negrita=True, gris=True, sangria=8)
            c.escribir(sec["evidencia"], tam=10.5, negrita=True, sangria=8)
        c.espacio(8)

    c.regla()
    c.espacio(6)
    c.escribir(f"{doc.get('pie', '')} · {_ahora()}", tam=8.5, gris=True)
    return _armar_pdf(c.paginas)
