; © 2026 Martín Viera. Todos los derechos reservados.
; Software propietario. Ver LICENSE — prohibida su redistribución.
;
; ---------------------------------------------------------------------------
; MV Data Governance · dónde propone instalarse
; ---------------------------------------------------------------------------
;
; El problema
; -----------
; NSIS propone siempre el disco del sistema (C:). En equipos donde C: es un SSD
; chico y los datos viven en D:, eso obliga a corregir la ruta a mano en cada
; instalación — y el que no se da cuenta llena el disco de arranque.
;
; Qué hace esto
; -------------
; Antes de mostrar nada, busca una unidad FIJA que no sea la del sistema y que
; tenga espacio de sobra, y propone esa. Si no hay ninguna, no toca nada y
; queda el comportamiento normal de siempre.
;
; Es solo la PROPUESTA: la pantalla de carpeta sigue estando
; (allowToChangeInstallationDirectory) y el usuario elige lo que quiera. Esto
; cambia el default, no la libertad de elegir.
;
; Lo que NO hace, a propósito
; ---------------------------
; Si ya hay una instalación registrada, no la toca. Pisar esa ruta en una
; actualización mandaría la versión nueva a otro disco y dejaría la vieja
; colgada, ocupando lugar y con accesos directos apuntando a cualquier lado.
; Por eso primero se lee, y solo se escribe si está vacío.
;
; Unidades de red y extraíbles quedan afuera: instalar el programa en un pendrive
; o en un recurso de red que mañana no está da un programa que "dejó de andar"
; sin explicación. GetDrives con "HDD" ya filtra solo discos fijos.

!include "FileFunc.nsh"
!include "LogicLib.nsh"

Var MVDG_DESTINO       ; la unidad elegida, ej "D:" — vacío = usar el default
Var MVDG_SISTEMA       ; la unidad de Windows, ej "C:"
Var MVDG_LIBRE         ; espacio libre en MB de la unidad que se está mirando

; Mínimo razonable: el programa con el Python embebido ronda los 400 MB, y
; dejar el disco al límite es peor que instalar en C:. 3 GB da margen para la
; instalación, una actualización y los datos del usuario.
!define MVDG_MIN_MB 3000

; Callback de ${GetDrives}: se llama una vez por unidad fija.
;   $9 = raíz de la unidad, con barra ("D:\")
Function MVDG_MirarUnidad
  ; Ya hay una elegida: no se sigue buscando (gana la primera, orden alfabético).
  ${If} $MVDG_DESTINO != ""
    Push "StopGetDrives"
    Return
  ${EndIf}

  StrCpy $R8 $9 2                       ; "D:\" -> "D:"
  ${If} $R8 != $MVDG_SISTEMA
    ${DriveSpace} "$9" "/D=F /S=M" $MVDG_LIBRE
    ${If} $MVDG_LIBRE > ${MVDG_MIN_MB}
      StrCpy $MVDG_DESTINO $R8
      Push "StopGetDrives"
      Return
    ${EndIf}
  ${EndIf}

  Push ""                               ; seguir con la siguiente unidad
FunctionEnd

Function MVDG_ElegirDestino
  StrCpy $MVDG_DESTINO ""
  StrCpy $MVDG_SISTEMA $WINDIR 2        ; "C:\Windows" -> "C:"
  ${GetDrives} "HDD" MVDG_MirarUnidad
FunctionEnd

; preInit lo llama electron-builder al principio de .onInit, antes de decidir
; el directorio por defecto. Es el único punto donde esto se puede cambiar.
!macro preInit
  ; ¿Ya hay una instalación? Entonces manda la que eligió el usuario.
  SetRegView 64
  ReadRegStr $R7 HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation
  ${If} $R7 == ""
    ReadRegStr $R7 HKLM "${INSTALL_REGISTRY_KEY}" InstallLocation
  ${EndIf}

  ${If} $R7 == ""
    Call MVDG_ElegirDestino
    ${If} $MVDG_DESTINO != ""
      SetRegView 64
      WriteRegExpandStr HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation \
        "$MVDG_DESTINO\MV Data Governance"
      SetRegView 32
      WriteRegExpandStr HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation \
        "$MVDG_DESTINO\MV Data Governance"
      SetRegView 64
    ${EndIf}
  ${EndIf}
!macroend
