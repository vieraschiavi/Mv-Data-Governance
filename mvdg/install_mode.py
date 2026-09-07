# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Cómo está instalado: en mi equipo o en el del cliente.

El caso real que resuelve
─────────────────────────
Un consultor de una empresa (digamos Practia) entra a trabajar a un cliente
(digamos Conaprole). Hay DOS equipos y no son intercambiables:

  · **Mi equipo.** La laptop de la consultora. Instalo normal: instalador,
    acceso directo en el escritorio, entrada en Agregar o quitar programas.
    Mis datos viven en mi perfil de usuario y ahí se quedan entre proyectos.

  · **El equipo del cliente.** Una VM corporativa, casi siempre con: sin
    permisos de administrador, sin internet, perfil de usuario que se
    resetea al cerrar sesión (VDI no persistente), y una política que dice
    que nada del cliente sale de esa máquina. Ahí un instalador es un
    problema, y guardar en el perfil del usuario es perder el trabajo.

Antes esto no estaba discriminado: había una sola forma de instalar, pensada
para el primer caso, y en el segundo el usuario tenía que adivinar. Y el
modo importa aunque el programa sea el mismo, porque cambia **dónde queda lo
que uno hace**: la curaduría, las conexiones guardadas, las fichas, la
licencia activada.

Qué cambia y qué NO
───────────────────
Cambia UNA sola cosa: dónde vive lo persistente (ver ``mvdg.paths``).

  normal      → el perfil del usuario (``~/.mv_data_governance``), o la
                carpeta de instalación si se puede escribir ahí.
  vm_cliente  → ``Datos/`` DENTRO de la carpeta del programa, siempre.
                Borrás la carpeta y no queda nada en la VM: ni en el perfil,
                ni en el registro, ni en Archivos de programa.

NO cambia nada más. Mismas pestañas, mismo motor, mismas reglas, misma
licencia. "Funciona igual" no es una promesa de folleto: hay un test que
compara las funciones habilitadas en los dos modos y falla si difieren. Un
modo recortado sería una segunda versión del producto disfrazada de opción
de instalación, y la que se probaría menos es justo la que corre en la
máquina del cliente.

Cómo se decide el modo
──────────────────────
1. ``MVDG_MODO_INSTALACION`` (``normal`` o ``vm_cliente``): manda siempre.
   Es lo que exporta el shell de Electron y lo que usan los tests.
2. Un archivo marcador ``MODO_VM_CLIENTE.txt`` en la carpeta del programa.
   Es lo que trae adentro el ZIP portable y no trae el instalador: así el
   paquete que bajaste ES el modo, sin que nadie tenga que configurarlo.
3. Si no hay ninguno de los dos: ``normal``.

Solo stdlib acá adentro, igual que ``mvdg.paths``: esto se consulta en el
arranque, antes de que exista nada.
"""
from __future__ import annotations

import os
import sys

MODO_NORMAL = "normal"
MODO_VM_CLIENTE = "vm_cliente"
MODOS = (MODO_NORMAL, MODO_VM_CLIENTE)

#: Nombre del archivo que marca un paquete como "para la VM del cliente".
#: Va en mayúsculas y con extensión .txt a propósito: alguien que abre la
#: carpeta tiene que poder leerlo y entender qué significa sin documentación.
MARCADOR = "MODO_VM_CLIENTE.txt"

VARIABLE = "MVDG_MODO_INSTALACION"

# Cuántos niveles se sube buscando el marcador. En el empaquetado de Electron
# el motor queda en `<instalación>/resources/server/mvdg`, o sea tres arriba;
# se prueba uno más por si el layout cambia. Más que eso sería salirse de la
# carpeta del programa y encontrar un marcador ajeno.
_NIVELES = 4

# El sondeo del disco se cachea por carpeta: `modo()` lo llama `data_dir()`,
# que se llama seguido, y no tiene sentido hacer stat en cada consulta.
_MARCADOR_ENCONTRADO: dict[str, str] = {}


def _candidatas() -> list[str]:
    """Carpetas donde puede estar el marcador, de la más específica a la menos.

    Se mira desde el módulo y desde el ejecutable porque no son la misma
    carpeta en todos los empaquetados: con PyInstaller el motor viaja adentro
    del .exe, y con Electron el .exe de la ventana está varios niveles arriba
    del Python que corre el motor.
    """
    bases = [os.path.dirname(os.path.abspath(__file__))]
    try:
        bases.append(os.path.dirname(os.path.abspath(sys.executable)))
    except Exception:
        pass

    vistas: list[str] = []
    for base in bases:
        actual = base
        for _ in range(_NIVELES + 1):
            if actual not in vistas:
                vistas.append(actual)
            padre = os.path.dirname(actual)
            if padre == actual:
                break
            actual = padre
    return vistas


def _marcador_en_disco() -> str:
    """Carpeta del programa si hay marcador, o "" si no lo hay."""
    clave = os.path.dirname(os.path.abspath(__file__))
    if clave in _MARCADOR_ENCONTRADO:
        return _MARCADOR_ENCONTRADO[clave]
    hallada = ""
    for carpeta in _candidatas():
        try:
            if os.path.isfile(os.path.join(carpeta, MARCADOR)):
                hallada = carpeta
                break
        except OSError:
            continue
    _MARCADOR_ENCONTRADO[clave] = hallada
    return hallada


def _olvidar_cache() -> None:
    """Vacía el cache del sondeo. Solo para los tests."""
    _MARCADOR_ENCONTRADO.clear()


def modo() -> str:
    """``"normal"`` o ``"vm_cliente"``. Nunca lanza."""
    declarado = (os.environ.get(VARIABLE) or "").strip().lower()
    if declarado in MODOS:
        return declarado
    return MODO_VM_CLIENTE if _marcador_en_disco() else MODO_NORMAL


def es_vm_cliente() -> bool:
    return modo() == MODO_VM_CLIENTE


def raiz_portable() -> str | None:
    """Carpeta del programa cuando corre en modo VM del cliente.

    Es donde va a colgar ``Datos/``. Sale del marcador si lo hay; si el modo
    se forzó por variable de entorno (sin marcador), se usa la carpeta del
    ejecutable, que es lo más cercano a "la carpeta del programa" cuando no
    hay una declarada.
    """
    if not es_vm_cliente():
        return None
    hallada = _marcador_en_disco()
    if hallada:
        return hallada
    try:
        return os.path.dirname(os.path.abspath(sys.executable))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Para mostrarlo en pantalla
# ---------------------------------------------------------------------------
# El texto va acá y no en `mvdg/i18n.py` por la misma razón que el de
# `dmbok.py` o `pipeline_doc.py`: son párrafos largos atados a este módulo,
# no etiquetas de botones. La regla de los tres idiomas se cumple igual.

_TEXTOS = {
    MODO_NORMAL: {
        "titulo": {
            "es": "Instalación normal (tu equipo)",
            "en": "Normal install (your machine)",
            "pt": "Instalação normal (seu equipamento)",
        },
        "detalle": {
            "es": "Instalado con el instalador de Windows: acceso directo en el "
                  "escritorio, entrada en el menú Inicio y desinstalación desde "
                  "«Agregar o quitar programas». Lo que hacés queda guardado en "
                  "tu perfil de usuario y sigue ahí entre proyectos.",
            "en": "Installed with the Windows installer: desktop shortcut, Start "
                  "Menu entry and uninstall from \"Add or remove programs\". Your "
                  "work is stored in your user profile and stays there between "
                  "projects.",
            "pt": "Instalado com o instalador do Windows: atalho na área de "
                  "trabalho, entrada no menu Iniciar e desinstalação em "
                  "«Aplicativos». O que você faz fica salvo no seu perfil de "
                  "usuário e permanece entre projetos.",
        },
    },
    MODO_VM_CLIENTE: {
        "titulo": {
            "es": "Equipo o VM del cliente (portable)",
            "en": "Client machine or VM (portable)",
            "pt": "Equipamento ou VM do cliente (portátil)",
        },
        "detalle": {
            "es": "Descomprimido en una carpeta, sin instalador y sin permisos de "
                  "administrador. No escribe en el registro ni en el perfil del "
                  "usuario: todo lo que hacés queda en la carpeta «Datos» de acá "
                  "al lado. Borrás la carpeta del programa y no queda rastro en "
                  "la máquina del cliente.",
            "en": "Unzipped into a folder, with no installer and no administrator "
                  "rights. It writes nothing to the registry or the user profile: "
                  "everything you do stays in the \"Datos\" folder next to it. "
                  "Delete the program folder and nothing is left on the client's "
                  "machine.",
            "pt": "Descompactado em uma pasta, sem instalador e sem permissões de "
                  "administrador. Não escreve no registro nem no perfil do "
                  "usuário: tudo o que você faz fica na pasta «Datos» ao lado. "
                  "Apague a pasta do programa e não sobra rastro na máquina do "
                  "cliente.",
        },
    },
}


def descripcion(lang: str = "es") -> dict:
    """Modo actual listo para mostrar: ``modo``, ``titulo``, ``detalle``, ``datos``.

    ``datos`` es la carpeta REAL donde se está guardando, sondeada, no la que
    debería ser. En una VM con la carpeta del programa de solo lectura, el
    programa igual arranca guardando en el perfil — y entonces conviene que
    la pantalla lo diga, porque es justo el caso en el que el trabajo se
    pierde al cerrar sesión.
    """
    from . import paths  # acá adentro: paths importa este módulo

    actual = modo()
    textos = _TEXTOS[actual]
    carpeta = paths.data_dir()
    esperada = raiz_portable()
    return {
        "modo": actual,
        "titulo": textos["titulo"].get(lang, textos["titulo"]["es"]),
        "detalle": textos["detalle"].get(lang, textos["detalle"]["es"]),
        "datos": carpeta,
        # True cuando se pidió modo VM pero la carpeta del programa no admite
        # escritura y hubo que caer al perfil del usuario.
        "datos_fuera_de_la_carpeta": bool(
            esperada and not carpeta.startswith(os.path.join(esperada, ""))),
    }
