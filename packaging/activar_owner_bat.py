# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Genera el .bat que pasa una instalación a versión owner.

Para qué
--------
El instalador del owner (el que sale del workflow con el secreto
``MVDG_OWNER_TOKEN``) ya viene desbloqueado. Pero si lo que hay instalado es
el .exe de CLIENTE — porque se bajó de la landing, o porque el build del
owner todavía no corrió — hace falta algo que lo pase a owner sin pegar
ninguna clave a mano.

Eso es el .bat que genera este script: se copia a la carpeta del programa,
doble clic, y la instalación queda desbloqueada.

Dónde escribe, y por qué en CUATRO lugares
------------------------------------------
No hay un único lugar correcto: depende de qué versión esté instalada y de
si la carpeta es escribible. ``licensing.current()`` busca en este orden:

1. ``data_dir()/licencia.json``      <- gana siempre, y es escribible sin admin
2. ``licencia_owner.txt`` empaquetada <- al lado del exe (frozen) o del motor

Y ``data_dir()`` a su vez cambia: es ``Data`` al lado del .exe cuando el
programa está congelado con PyInstaller **y** esa carpeta se puede escribir;
si no, ``~/.mv_data_governance``. La versión Electron no está congelada, así
que siempre usa el perfil del usuario, y su motor vive en
``resources/server/`` — dentro de Archivos de programa, donde un usuario sin
admin NO puede escribir.

Escribir en los cuatro cubre todas las combinaciones. No es redundancia
defensiva: cada destino corresponde a un caso real distinto, y ninguno es
peligroso porque **el token se vuelve a verificar por firma en cada lectura**
(``current()`` llama a ``verify()``). Un archivo de más en un lugar que no se
usa no desbloquea nada por sí solo.

El .bat lleva el token adentro
------------------------------
Es lo que lo hace "sin trabas": no pregunta nada. Por eso el .bat generado
**no se commitea** — el repo es público y ese token abre el programa
completo. Está en .gitignore y hay un test que falla si aparece trackeado.

Uso
---
    python packaging/activar_owner_bat.py                  # lee MVDG_OWNER_TOKEN
    python packaging/activar_owner_bat.py --token MVDG2... --salida MV_Owner.bat
"""
from __future__ import annotations

import argparse
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

NOMBRE_POR_DEFECTO = "MV_Activar_Owner.bat"

# El .bat corre en cmd.exe, que usa cp850/cp1252: cualquier acento se ve como
# basura. Se escribe sin acentos a propósito, no por descuido.
PLANTILLA = r"""@echo off
REM ===================================================================
REM  MV Data Governance - Activar version OWNER
REM ===================================================================
REM  Copia este archivo a la carpeta donde esta instalado el programa
REM  y hace doble clic. No pide nada.
REM
REM  ESTE ARCHIVO CONTIENE TU LICENCIA: no lo compartas ni lo subas a
REM  ningun lado. Cualquiera que lo tenga desbloquea el programa.
REM ===================================================================
setlocal

set "TOKEN=__TOKEN__"
set "AQUI=%~dp0"
set "HECHOS=0"

echo.
echo   =============================================
echo    MV Data Governance - Activacion OWNER
echo   =============================================
echo.

REM --- 1. Perfil del usuario. Es el que usa la version Electron, y el
REM        unico que SIEMPRE se puede escribir sin permisos de admin.
set "D1=%USERPROFILE%\.mv_data_governance"
if not exist "%D1%" mkdir "%D1%" >nul 2>&1
>"%D1%\licencia.json" echo {"token":"%TOKEN%"}
if exist "%D1%\licencia.json" (
  echo   [OK] %D1%\licencia.json
  set /a HECHOS+=1
) else (
  echo   [--] no se pudo escribir en %D1%
)

REM --- 2. Data al lado del exe: lo que usa el .exe de PyInstaller cuando
REM        esta instalado en una carpeta escribible (D:\, un pendrive).
set "D2=%AQUI%Data"
if not exist "%D2%" mkdir "%D2%" >nul 2>&1
>"%D2%\licencia.json" echo {"token":"%TOKEN%"}
if exist "%D2%\licencia.json" (
  echo   [OK] %D2%\licencia.json
  set /a HECHOS+=1
) else (
  echo   [--] %D2% no se puede escribir ^(hace falta admin^) - se ignora
)

REM --- 3. Licencia empaquetada al lado del exe congelado.
>"%AQUI%licencia_owner.txt" echo %TOKEN%
if exist "%AQUI%licencia_owner.txt" (
  echo   [OK] %AQUI%licencia_owner.txt
  set /a HECHOS+=1
) else (
  echo   [--] %AQUI% no se puede escribir ^(hace falta admin^) - se ignora
)

REM --- 4. Licencia empaquetada al lado del motor de la version Electron.
REM        Suele estar en Archivos de programa: si falla, no importa, el
REM        punto 1 ya alcanza.
set "D4=%AQUI%resources\server"
if exist "%D4%\mvdg\licensing.py" (
  >"%D4%\licencia_owner.txt" echo %TOKEN%
  if exist "%D4%\licencia_owner.txt" (
    echo   [OK] %D4%\licencia_owner.txt
    set /a HECHOS+=1
  ) else (
    echo   [--] %D4% no se puede escribir ^(hace falta admin^) - se ignora
  )
)

echo.
if "%HECHOS%"=="0" (
  echo   ERROR: no se pudo escribir en ningun lado.
  echo   Proba hacer clic derecho ^> "Ejecutar como administrador".
  echo.
  pause
  exit /b 1
)

REM Una variable de entorno MVDG_DATA_DIR mandaria sobre todo lo anterior:
REM si esta puesta, el programa leeria de ahi y no de donde escribimos.
if defined MVDG_DATA_DIR (
  echo   AVISO: tenes MVDG_DATA_DIR=%MVDG_DATA_DIR%
  echo   El programa lee la licencia de ahi. Copia el licencia.json
  echo   generado a esa carpeta si no se activa.
  echo.
)

echo   Listo. Abri MV Data Governance: entra como OWNER, sin clave.
echo   ^(si ya estaba abierto, cerralo y volve a abrirlo^)
echo.
pause
endlocal
"""


def generar(token: str) -> str:
    """El texto del .bat, con el token adentro."""
    token = token.strip()
    if not token.startswith("MVDG2."):
        raise SystemExit(
            f"  El token no parece una licencia MVDG2: empieza con "
            f"'{token[:12]}...'")
    # Un token es base64url + puntos. Si trajera un metacaracter de cmd
    # (&, |, >, <, ^, %) el .bat se rompería de formas raras en vez de
    # fallar claro, así que se corta acá.
    permitido = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz0123456789-_.")
    malos = sorted(set(token) - permitido)
    if malos:
        raise SystemExit(f"  El token tiene caracteres que cmd.exe "
                         f"interpretaria: {malos}")
    return PLANTILLA.replace("__TOKEN__", token)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Genera el .bat que activa la version owner")
    p.add_argument("--token", help="si no, se lee MVDG_OWNER_TOKEN")
    p.add_argument("--salida", default=NOMBRE_POR_DEFECTO)
    args = p.parse_args(argv)

    token = (args.token or os.environ.get("MVDG_OWNER_TOKEN") or "").strip()
    if not token:
        sys.stderr.write(
            "\n  Falta el token: pasalo con --token o defini "
            "MVDG_OWNER_TOKEN.\n"
            "  Se emite con:  python packaging/licencias.py firmar "
            "--plan owner --email <tu-email>\n\n")
        return 2

    # Se verifica ANTES de generar nada: un .bat con un token que no valida
    # se ve exactamente igual que uno bueno, y el sintoma aparece recien
    # cuando el programa sigue abriendo en demo sin decir por que.
    from mvdg import licensing
    payload = licensing.verify(token, check_machine=False)
    if payload is None:
        sys.stderr.write("\n  El token NO verifica contra la clave publica "
                         "de mvdg/licensing.py.\n  No se genera nada.\n\n")
        return 1
    if payload.get("plan") != licensing.PLAN_OWNER:
        sys.stderr.write(f"\n  El token es plan '{payload.get('plan')}', "
                         f"se esperaba 'owner'.\n\n")
        return 1

    with open(args.salida, "w", encoding="ascii", newline="\r\n") as fh:
        fh.write(generar(token))

    print(f"\n  Generado: {args.salida}")
    print(f"  plan={payload['plan']} email={payload.get('email')}")
    if payload.get("mid"):
        print(f"  atado a la maquina {payload['mid']}")
    else:
        print("  SIN atar a una maquina: sirve en cualquier PC. No lo "
              "compartas.")
    print("\n  Copialo a la carpeta del programa y hace doble clic.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
