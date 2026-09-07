# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Compilación del motor a binario (Cython).

Por qué existe
--------------
En el bundle de PyInstaller, ``mvdg/`` viaja como **carpeta de datos con los
``.py`` en texto plano** (no como paquete importado): Streamlit ejecuta
``app.py`` como script, así que el análisis estático de PyInstaller no puede
rastrear el motor y lo copia tal cual. Resultado: el que instala el programa
tiene el motor completo — reglas de calidad, catálogo, linaje, MDM, perfilado —
legible con el Bloc de notas, sin necesidad de crackear nada.

Este script compila esos módulos a extensiones nativas (``.pyd`` en Windows,
``.so`` en Linux/macOS) con Cython, y deja ``app.py`` como capa fina de interfaz
que importa el motor ya compilado. Eso NO vuelve el programa inviolable — un
binario nativo se puede reversear con Ghidra/IDA, y de hecho nadie necesita leer
el código para copiar el comportamiento observando la demo. Lo que hace es subir
el costo de copiar el CÓDIGO de "abrir el .py en un editor" a "reversear un
binario", que es un oficio aparte.

Uso
---
    python packaging/build_compiled.py

Genera ``build/mvdg_compiled/mvdg/`` y ``packaging/mvdg.spec`` la usa
automáticamente si existe (si no, cae al ``mvdg/`` de siempre en texto plano,
así el build nunca se rompe por no tener Cython instalado).

Requiere Cython y un compilador de C (en Windows: Build Tools de Visual Studio).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "mvdg")
STAGING = os.path.join(ROOT, "build", "mvdg_compiled")
OUT_PKG = os.path.join(STAGING, "mvdg")

# Módulos que NO se compilan, con el motivo técnico de cada uno. No es una lista
# de conveniencia: cada exclusión se verificó rompiendo algo real al compilarla.
NO_COMPILAR = {
    # `python -m <módulo>` NO funciona sobre una extensión nativa: el
    # intérprete corta con "No code object available for mvdg.X" porque runpy
    # necesita código fuente o bytecode, no un .so/.pyd. Estos tres son
    # entrypoints reales (el .bat del servidor, el botón "Probar servidor MCP"
    # de la app y el selfcheck lanzan subprocesos así), por lo tanto tienen que
    # seguir siendo .py.
    "mcp_server.py": "entrypoint: se lanza con python -m mvdg.mcp_server",
    "selfcheck.py": "entrypoint: se lanza con python -m mvdg.selfcheck",
    "server.py": "entrypoint: se lanza con python -m mvdg.server",

    # El selfcheck abre el CÓDIGO FUENTE de enforcement.py y afirma que no
    # contiene "sqlalchemy" ni ".execute(" — es la garantía auditable de que el
    # módulo genera DDL como texto y no ejecuta nada contra la base. Compilarlo
    # deja esa garantía sin poder verificarse (y encima es una garantía que
    # conviene que el cliente pueda auditar por su cuenta).
    "enforcement.py": "el selfcheck audita su código fuente como garantía de seguridad",

    # Sin valor como secreto: es la versión y la paleta de marca, y
    # packaging/mvdg.spec lo importa para leer __version__.
    "__init__.py": "lo importa mvdg.spec para la versión; sin lógica de negocio",

    # ~1700 líneas de traducciones visibles en pantalla: no hay nada que
    # proteger y conviene que sea legible/parcheable.
    "i18n.py": "solo textos de interfaz ES/EN/PT; cero lógica de negocio",
}


def _limpiar() -> None:
    if os.path.isdir(STAGING):
        shutil.rmtree(STAGING)
    os.makedirs(OUT_PKG, exist_ok=True)


def _copiar_fuentes() -> list[str]:
    """Copia mvdg/ al staging. Devuelve los .py que hay que compilar."""
    a_compilar = []
    for nombre in sorted(os.listdir(SRC)):
        origen = os.path.join(SRC, nombre)
        if os.path.isdir(origen):
            if nombre == "__pycache__":
                continue
            shutil.copytree(origen, os.path.join(OUT_PKG, nombre))
            continue
        if nombre.endswith((".pyc", ".pyo")):
            continue
        shutil.copy2(origen, os.path.join(OUT_PKG, nombre))
        if nombre.endswith(".py") and nombre not in NO_COMPILAR:
            a_compilar.append(nombre)
    return a_compilar


def _compilar(a_compilar: list[str]) -> None:
    """Compila los módulos con Cython, desde el staging como cwd.

    El cwd importa: cythonize deriva el nombre del módulo del path relativo,
    así que compilando "mvdg/quality.py" desde STAGING el módulo queda como
    ``mvdg.quality`` y los imports relativos internos (``from .clients import
    data_dir``) siguen resolviendo igual que en el paquete original.
    """
    setup_py = os.path.join(STAGING, "_setup_cython.py")
    objetivos = [f"mvdg/{n}" for n in a_compilar]
    with open(setup_py, "w", encoding="utf-8") as fh:
        fh.write(
            "from setuptools import setup\n"
            "from Cython.Build import cythonize\n"
            "from Cython.Compiler import Options\n"
            "# Los docstrings del motor explican la lógica de negocio en detalle\n"
            "# (causa raíz de cada regla, umbrales, decisiones de diseño). Si\n"
            "# quedan embebidos en el binario, se leen con `strings` y buena\n"
            "# parte del esfuerzo de compilar no sirve para nada.\n"
            "# Ojo: es una opción GLOBAL de Cython, no un compiler_directive\n"
            "# (pasarla como directive falla con 'unknown compiler directive').\n"
            "Options.docstrings = False\n"
            f"OBJETIVOS = {objetivos!r}\n"
            "# annotation_typing=False es CRÍTICO acá, no una optimización:\n"
            "# las anotaciones del motor se escribieron como documentación para\n"
            "# humanos y type-checkers, no como hints de Cython. Con el default\n"
            "# (True), Cython las APLICA en runtime, así que una anotación\n"
            "# imprecisa —que Python ignora sin consecuencias— revienta con\n"
            "# TypeError SOLO en el build compilado. Eso es lo peor posible:\n"
            "# un bug que no existe en el .bat portable y sí en el .exe que se\n"
            "# le entrega al cliente. Compilamos para ofuscar, no para tipar:\n"
            "# el binario tiene que comportarse igual que el intérprete.\n"
            "setup(ext_modules=cythonize(OBJETIVOS, language_level=3, quiet=True,\n"
            "                            compiler_directives={'annotation_typing': False}),\n"
            "      script_args=['build_ext', '--inplace'])\n")
    subprocess.run([sys.executable, "_setup_cython.py"], cwd=STAGING, check=True)


def _borrar_fuentes_compiladas(a_compilar: list[str]) -> tuple[int, int]:
    """Saca del staging los .py que ya quedaron compilados (si no, Python
    importaría el .py y todo el trabajo no serviría de nada), más los .c
    intermedios que genera Cython — que son código C legible y equivalente al
    fuente: dejarlos sería anular el propósito del ejercicio.
    """
    borrados = 0
    for nombre in a_compilar:
        py = os.path.join(OUT_PKG, nombre)
        base = nombre[:-3]
        compilado = [f for f in os.listdir(OUT_PKG)
                     if f.startswith(base + ".") and f.endswith((".pyd", ".so"))]
        if not compilado:
            raise SystemExit(
                f"  ERROR: {nombre} no generó .pyd/.so — se aborta para no "
                f"entregar un bundle a medias (mitad compilado, mitad fuente).")
        if os.path.exists(py):
            os.remove(py)
            borrados += 1
    intermedios = 0
    for f in list(os.listdir(OUT_PKG)):
        if f.endswith(".c"):
            os.remove(os.path.join(OUT_PKG, f))
            intermedios += 1
    for extra in ("_setup_cython.py", "build"):
        ruta = os.path.join(STAGING, extra)
        if os.path.isdir(ruta):
            shutil.rmtree(ruta)
        elif os.path.exists(ruta):
            os.remove(ruta)
    cache = os.path.join(OUT_PKG, "__pycache__")
    if os.path.isdir(cache):
        shutil.rmtree(cache)
    return borrados, intermedios


def main() -> int:
    try:
        import Cython  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "\n  Cython no está instalado — no se compila el motor.\n"
            "  Instalalo con:  pip install cython\n"
            "  (en Windows también hacen falta los Build Tools de Visual Studio)\n"
            "  El build sigue funcionando sin esto, pero el motor viaja como\n"
            "  código fuente legible.\n\n")
        return 1

    print("  [1/3] Copiando mvdg/ al staging...")
    _limpiar()
    a_compilar = _copiar_fuentes()
    print(f"        {len(a_compilar)} módulos a compilar · "
          f"{len(NO_COMPILAR)} excluidos a propósito")

    print("  [2/3] Compilando con Cython (esto tarda)...")
    _compilar(a_compilar)

    print("  [3/3] Borrando fuentes .py compiladas y .c intermedios...")
    borrados, intermedios = _borrar_fuentes_compiladas(a_compilar)

    quedan = sorted(f for f in os.listdir(OUT_PKG) if f.endswith(".py"))
    print(f"\n  OK: {OUT_PKG}")
    print(f"      {borrados} .py compilados y removidos · {intermedios} .c intermedios borrados")
    print(f"      quedan como fuente (a propósito): {', '.join(quedan)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
