# Material comercial — MV Data Governance

Piezas para presentar el producto a **gerentes de financieras/PYMEs** (cliente) y a **inversores**.
Trilingüe: Español (ES), Inglés (EN), Portugués (PT), más una variante **Inversor** (ES) reencuadrada
al pedido de capital.

## Contenido

| Carpeta | Variante | Archivos |
|---|---|---|
| `es/` | Español · cliente-financiera | Pitch deck (PPTX + PDF) · One-pager (PDF A4 + PPTX apaisado) |
| `en/` | English · lender/manager | idem |
| `pt/` | Português (pt-BR) · financeira | idem |
| `inversor/` | Español · inversor | idem, con portada y cierre en pedido de capital / uso de fondos |
| `emails/` | — | `Emails-Presentacion.md`: 4 emails de presentación listos para copiar |
| `src/` | — | Generadores reproducibles (ver abajo) |

Nomenclatura por archivo:
- `*-Pitch.pptx` — deck editable (12 slides, 16:9).
- `*-Deck.pdf` — el deck en PDF (para enviar por mail / leer).
- `*-OnePager.pdf` — resumen ejecutivo, 1 página A4.
- `*-OnePager-PPTX.pptx` — el one-pager editable como slide apaisada 16:9.

## Cifras

Todas las cifras (neto 18m US$86–146k, recurrente US$2,9–5,0k/m, escenarios, etc.) salen del modelo
financiero `src/model.py` y están verificadas contra su salida. Los precios (Licencia US$149,
Professional US$390/mes, créditos IA US$9/39/149) son los reales del repositorio. Las cifras de
mercado/ads están marcadas verificado vs. estimado en las propias piezas.

## Regenerar

Los entregables se generan desde un motor **data-driven** (un solo contenido por idioma/variante +
plantillas compartidas), así ES/EN/PT/Inversor no divergen por edición manual.

```bash
cd docs/comercial/src
npm install pptxgenjs            # dependencia del generador de PPTX
node gen.js                      # -> 4 deck PPTX + 8 HTML (deck y one-pager) por variante
node build_op_pptx.js            # -> 4 one-pager PPTX (slide apaisada)
# PDFs: renderizar los HTML con Chromium (--print-to-pdf). Ver notas abajo.
python3 model.py                 # imprime la tabla de escenarios (fuente de verdad de las cifras)
```

- `content.js` — contenido ES + constantes de los gráficos.
- `content_i18n.js` — EN, PT y la variante Inversor (derivada de ES).
- `gen.js` — plantillas HTML (deck + one-pager) y generador de deck PPTX.
- `build_op_pptx.js` — generador del one-pager PPTX apaisado.
- `model.py` — modelo financiero (3 escenarios × con/sin ads × horizontes).

Los PDF se producen renderizando los HTML generados (`deck_*.html`, `onepager_*.html`) con Chromium
headless (`--headless --print-to-pdf`), no con LibreOffice.

## Notas

- Los datos de demo son **100% sintéticos**. Ninguna pieza contiene datos reales de personas.
- Para el PDF del deck generado por el propio PowerPoint: abrir el `.pptx` y "Guardar como PDF".
