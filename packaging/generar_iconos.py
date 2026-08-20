# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Genera todos los íconos del producto desde el logo.

Por qué existe
--------------
El logo de la marca es UN vector (assets/brand/mv_logo.svg). De ahí salen el
.ico de Windows, los PNG de cada tamaño y la copia que usa la landing. Tenerlo
como script y no como "una vez los generé a mano" es lo que hace que cambiar
el logo sea una operación de un comando, en vez de una cacería de archivos
sueltos que quedan desincronizados: el favicon nuevo y el ícono del escritorio
viejo, y nadie se entera hasta que un cliente lo ve.

El SVG es la fuente de verdad porque escala sin perder nada: el mismo archivo
da el ícono de 16 px de la barra de tareas y el de 1024 de la tienda.

Uso
---
    python packaging/generar_iconos.py            # regenera todo
    python packaging/generar_iconos.py --revisar  # falla si algo quedó viejo

`--revisar` es para el CI: no escribe nada, solo confirma que los PNG del
repo son los que salen del SVG actual.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARCA = os.path.join(RAIZ, "assets", "brand")
SVG = os.path.join(MARCA, "mv_logo.svg")

# Los PNG sueltos que consume el producto.
#   1024 -> mv_icon.png, el maestro (y la copia de la landing)
#   256  -> ícono de Linux para electron-builder (exige 256 como mínimo)
#   128  -> el launcher del .exe
#   64   -> el encabezado de la interfaz y su favicon
#   32   -> usos chicos
TAMANIOS = {"mv_icon.png": 1024, "mv_icon_256.png": 256,
            "mv_icon_128.png": 128, "mv_icon_64.png": 64,
            "mv_icon_32.png": 32}

# Windows elige de acá según el contexto: 16 en la barra de título, 32 en la
# barra de tareas, 48 en el escritorio, 256 en vista de iconos grandes. Si
# falta uno, Windows escala otro y se ve borroso justo donde más se mira.
ICO = [16, 32, 48, 64, 128, 256]

# La landing tiene que mostrar EXACTAMENTE el mismo archivo que el producto.
COPIAS = [os.path.join(RAIZ, "landing", "mv_icon.png")]


def _png(tam: int) -> bytes:
    import cairosvg
    return cairosvg.svg2png(url=SVG, output_width=tam, output_height=tam)


def _sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def generar(revisar: bool = False) -> int:
    if not os.path.exists(SVG):
        sys.stderr.write(f"\n  Falta el logo vectorial: {SVG}\n\n")
        return 2
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "\n  Falta cairosvg (solo para regenerar los iconos):\n"
            "      pip install cairosvg\n\n")
        return 2

    from PIL import Image

    desactualizados = []
    maestro = None

    for nombre, tam in TAMANIOS.items():
        datos = _png(tam)
        if nombre == "mv_icon.png":
            maestro = datos
        ruta = os.path.join(MARCA, nombre)
        viejo = open(ruta, "rb").read() if os.path.exists(ruta) else b""
        # El PNG no es byte-a-byte reproducible entre versiones de la
        # libreria, asi que se compara el CONTENIDO de la imagen, no el
        # archivo: si no, "--revisar" fallaria siempre y dejaria de servir.
        igual = False
        if viejo:
            try:
                igual = (Image.open(io.BytesIO(viejo)).convert("RGBA").tobytes()
                         == Image.open(io.BytesIO(datos)).convert("RGBA").tobytes())
            except Exception:      # noqa: BLE001 — archivo ilegible = distinto
                igual = False
        if igual:
            continue
        desactualizados.append(nombre)
        if not revisar:
            with open(ruta, "wb") as fh:
                fh.write(datos)
            print(f"  {nombre:<18} {tam}x{tam}")

    # El .ico, con todos los tamaños adentro.
    ruta_ico = os.path.join(MARCA, "mv.ico")
    if not revisar:
        base = Image.open(io.BytesIO(_png(256))).convert("RGBA")
        base.save(ruta_ico, format="ICO",
                  sizes=[(t, t) for t in ICO])
        print(f"  {'mv.ico':<18} {ICO}")
    else:
        try:
            with Image.open(ruta_ico) as im:
                tiene = sorted({t[0] for t in im.ico.sizes()})
            if tiene != sorted(ICO):
                desactualizados.append(f"mv.ico (tiene {tiene})")
        except Exception:          # noqa: BLE001
            desactualizados.append("mv.ico (ilegible)")

    # Las copias (la landing).
    for destino in COPIAS:
        actual = open(destino, "rb").read() if os.path.exists(destino) else b""
        if maestro is not None and _sha(actual) != _sha(maestro):
            desactualizados.append(os.path.relpath(destino, RAIZ))
            if not revisar:
                with open(destino, "wb") as fh:
                    fh.write(maestro)
                print(f"  {os.path.relpath(destino, RAIZ)}")

    if revisar and desactualizados:
        sys.stderr.write(
            "\n  Estos iconos NO salen del logo actual:\n    - "
            + "\n    - ".join(desactualizados)
            + "\n\n  Regeneralos con: python packaging/generar_iconos.py\n\n")
        return 1
    if revisar:
        print("  Todos los iconos estan al dia con assets/brand/mv_logo.svg")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Genera los iconos del producto desde el logo vectorial")
    p.add_argument("--revisar", action="store_true",
                   help="no escribe: falla si algo quedo viejo")
    args = p.parse_args(argv)
    return generar(revisar=args.revisar)


if __name__ == "__main__":
    raise SystemExit(main())
